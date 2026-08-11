import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dataclasses import dataclass
from collections.abc import Iterable
from pathlib import Path
from matplotlib.figure import Figure

# Switch to the non-interactive AGG (Anti-Grain Geometry) backend
matplotlib.use("Agg")

IQR_MULTIPLIER = 1.5 # IQR = Interquartile Range

@dataclass
class NumericalColumnStatistics:
    min: float
    q1: float
    median: float
    mean: float
    q3: float
    max: float
    std: float

@dataclass
class InterquartileRangeAnalysis:
    lower: float
    upper: float
    outlier_count: int

@dataclass
class NumericalDomainAnalysis:
    lower: float | None
    upper: float | None
    outlier_count: int = 0

@dataclass
class NumericalColumnAnalysis:
    column: str
    count: int
    missing_count: int
    missing_ratio: float
    valid_count: int
    unique_count: int
    statistics: NumericalColumnStatistics | None = None
    iqr: InterquartileRangeAnalysis | None = None
    domain: NumericalDomainAnalysis | None = None
    outlier_count: int = 0
    outlier_ratio: float = 0.0

def classify_columns(dataframe: pd.DataFrame, columns_to_exclude=None)\
    -> tuple[list[str], list[str]]:
    """ 
    Returns:
        categorical and numerical column names.
    """

    if columns_to_exclude is None:
        columns_to_exclude = {"source_file"}
    else:
        columns_to_exclude = set(columns_to_exclude)

    dataframe = dataframe.drop(columns=columns_to_exclude, errors="ignore")
    # Note: Setting errors='ignore' suppresses KeyError exceptions
    # if any specified labels do not exist in the DataFrame.

    numerical_columns = dataframe.select_dtypes(
        include=np.number).columns.tolist()

    categorical_columns = dataframe.select_dtypes(
        include=["object", "category", "bool",]).columns.tolist()

    return categorical_columns, numerical_columns

def get_basic_information(dataframe: pd.DataFrame) -> dict[str, object]:
    """Return basic dataset information."""

    categorical_column_names, numerical_column_names =\
        classify_columns(dataframe)

    rows, columns = dataframe.shape

    return {
        "rows": rows,
        "columns": columns,
        "categorical_columns": categorical_column_names,
        "numerical_columns": numerical_column_names,
        "total_missing": int(dataframe.isna().sum().sum())
        }

def analyze_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    missing_count = dataframe.isna().sum()

    rows = len(dataframe)

    if rows == 0: # rows == 0
        missing_ratio = pd.Series(0.0, index=dataframe.columns)
    else:
        missing_ratio = missing_count / rows * 100.0

    result = pd.DataFrame({
        "column": dataframe.columns,
        "missing_count": missing_count.values,
        "missing_ratio": missing_ratio.values,
        "valid_count": rows - missing_count.values
        })

    sorted_result = (
        result
        .sort_values("missing_count", ascending=False)
        .reset_index(drop=True)
        )

    return sorted_result

def analyze_categorical_distribution(dataframe: pd.DataFrame, column: str)\
    -> pd.DataFrame:
    distribution = (
        dataframe[column]
        .value_counts(dropna=False)
        .rename_axis("value")
        .reset_index(name="count")
        )

    rows = len(dataframe)

    if rows == 0:
        distribution["ratio"] = 0.0
    else:
        distribution["ratio"] = distribution["count"] / rows * 100.0

    return distribution

def analyze_numerical_column(dataframe: pd.DataFrame, column: str,
                             lower: object | None = None,
                             upper: object | None = None) -> NumericalColumnAnalysis:
    """
    Analyzes one numerical column.
    lower and upper define domain boundaries.
    """

    series = dataframe[column]
    count = len(series)

    cleaned_series = series.dropna()
    valid_count = len(cleaned_series)

    missing_count = count - valid_count

    result = NumericalColumnAnalysis(
        column=column,
        count=count,
        missing_count=missing_count,
        missing_ratio=(missing_count / count * 100.0 if count else 0.0),
        valid_count=valid_count,
        unique_count=int(cleaned_series.nunique()),
        domain=NumericalDomainAnalysis(lower, upper)
        )

    if cleaned_series.empty:
        return result

    q1 = cleaned_series.quantile(0.25)
    median = cleaned_series.quantile(0.50)
    q3 = cleaned_series.quantile(0.75)
    iqr = q3 - q1

    iqr_lower = q1 - IQR_MULTIPLIER * iqr
    iqr_upper = q3 + IQR_MULTIPLIER * iqr

    iqr_mask = ((series < iqr_lower) | (series > iqr_upper)).fillna(False)

    domain_mask = pd.Series(None, index=series.index)

    if lower is not None:
        domain_mask |= series < lower

    if upper is not None:
        domain_mask |= series > upper

    domain_mask = domain_mask.fillna(False)

    result.statistics = NumericalColumnStatistics(
        min=cleaned_series.min(),
        q1=q1,
        median=median,
        mean=cleaned_series.mean(),
        q3=q3,
        max=cleaned_series.max(),
        std=cleaned_series.std()
        )

    result.iqr = InterquartileRangeAnalysis(
        lower=iqr_lower,
        upper=iqr_upper,
        outlier_count=int(iqr_mask.sum())
        )

    result.domain.outlier_count = int(domain_mask.sum())

    outlier_mask = (iqr_mask | domain_mask)
    outlier_count = int(outlier_mask.sum())
    result.outlier_count = outlier_count
    result.outlier_ratio = outlier_count / len(series) * 100.0

    return result

def get_numerical_outlier_mask(dataframe: pd.DataFrame,
                               analysis: NumericalColumnAnalysis) -> pd.Series:
    series = dataframe[analysis["column"]]

    mask = pd.Series(None, index=series.index)

    iqr = analysis.iqr

    mask |= ((series < iqr["lower"]) | (series > iqr["upper"]))

    domain = analysis.domain

    if domain["lower"] is not None:
        mask |= series < domain["lower"]

    if domain["upper"] is not None:
        mask |= series > domain["upper"]

    return mask.fillna(False)

def find_value_missing_rows(dataframe: pd.DataFrame,
                            columns: list[str] | None = None) -> pd.DataFrame:
    if columns is None:
        columns = dataframe.columns.tolist()

    if not columns:
        return dataframe.head(0).copy()

    mask = dataframe[columns].isna().any(axis=1)

    return dataframe.loc[mask].copy()

def find_value_rows(dataframe: pd.DataFrame, values: dict[str, list[object]])\
    -> pd.DataFrame:
    """
    Find rows containing any specified values.
    The values can be specified as {"column_name": ["value1", "value2"]}.
    """

    mask = pd.Series(False, index=dataframe.index)

    for column, target_values in values.items():
        mask |= dataframe[column].isin(target_values)

    return dataframe.loc[mask].copy()

def find_numerical_outlier_rows(dataframe: pd.DataFrame,
                                analyses: Iterable[NumericalColumnAnalysis])\
                                    -> pd.DataFrame:
    mask = pd.Series(False, index=dataframe.index)

    for analysis in analyses:
        mask |= get_numerical_outlier_mask(dataframe, analysis)

    return dataframe.loc[mask].copy()

def find_rows(dataframe: pd.DataFrame,
              missing_columns: list[str] | None = None,
              outlier_analyses: Iterable[NumericalColumnAnalysis] | None = None,
              values: dict[str, list[object]] | None = None) -> pd.DataFrame:
    """
    Find rows satisfying any specified condition.
    The values can be specified as {"column_name": ["value1", "value2"]}.
    """

    mask = pd.Series(False, index=dataframe.index)

    if missing_columns:
        mask |= dataframe[missing_columns].isna().any(axis=1)

    if outlier_analyses:
        for analysis in outlier_analyses:
            mask |= get_numerical_outlier_mask(dataframe, analysis)

    if values:
        for column, target_values in values.items():
            mask |= dataframe[column].isin(target_values)

    return dataframe.loc[mask].copy()

def get_row_reasons(row: pd.Series,
              missing_columns: list[str] | None = None,
              outlier_analyses: Iterable[NumericalColumnAnalysis] | None = None,
              values: dict[str, list[object]] | None = None) -> list[str]:
    reasons = []

    if missing_columns:
        for column in missing_columns:
            if pd.isna(row[column]):
                reasons.append(f"{column}=NaN")

    if outlier_analyses:
        for analysis in outlier_analyses:
            column = analysis["column"]
            value = row[column]

            if pd.isna(value):
                continue

            iqr = analysis["iqr"]

            if value < iqr["lower"] or value > iqr["upper"]:
                reasons.append(f"{column}=outlier")
                continue

            domain = analysis["domain"]

            if domain["lower"] is not None and value < domain["lower"]:
                reasons.append(f"{column}=out_of_range")

            if domain["upper"] is not None and value > domain["upper"]:
                reasons.append(f"{column}=out_of_range")

    if values:
        for column, target_values in values.items():
            if row[column] in target_values:
                reasons.append(f"{column}={row[column]!r}") # !r means repr().

    return reasons

def write_row_summary(dataframe: pd.DataFrame,
                      output_path: str | Path,
                      missing_columns: list[str] | None = None,
                      outlier_analyses: Iterable[NumericalColumnAnalysis] | None = None,
                      values: dict[str, list[object]] | None = None,
                      columns: list[str] | None = None
                      ) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if columns is None:
        columns = [column for column in dataframe.columns
                   if column != "source_file"]

    lines = [f"Rows: {len(dataframe)}", ""]

    for index, row in dataframe.iterrows():
        source_file = row.get("source_file", "<unknown>")

        reasons = get_row_reasons(row, missing_columns, outlier_analyses, values)

        lines.append(f"[{index}] {source_file}")

        if reasons:
            lines.append(f"  reason: {'; '.join(reasons)}")

        lines.append("  data: " + " | ".join(f"{column}={row[column]!r}"
                                             for column in columns))

    path.write_text("\n".join(lines), encoding="utf-8")

def calculate_statistics(dataframe: pd.DataFrame,
                         columns: list[str] | None = None) -> pd.DataFrame:
    if columns is None:
        columns = dataframe.select_dtypes(include="number").columns

    if len(columns) == 0:
        return pd.DataFrame()

    return dataframe[columns].describe().T

def calculate_group_statistics(dataframe: pd.DataFrame,
                               group_by: str, target: str) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame()

    return (
        dataframe.groupby(group_by)[target].agg([
            "count",
            "mean",
            "std",
            "min",
            "median",
            "max"
            ])
        .reset_index()
    )

def calculate_correlation(dataframe: pd.DataFrame,
                          columns: list[str] | None = None) -> pd.DataFrame:
    if columns is None:
        columns = dataframe.select_dtypes(include="number").columns

    if len(columns) == 0:
        return pd.DataFrame()

    return dataframe[columns].corr()

def calculate_value_counts(dataframe: pd.DataFrame, column: str):
    return dataframe[column].value_counts(dropna=False).rename_axis("value")\
        .reset_index(name="count")

def plot_missing_values(missing_summary: pd.DataFrame) -> Figure:
    """
    Note: Close the figure after use.
    """
    data = missing_summary[missing_summary["missing_count"] > 0]

    if data.empty:
        return None

    figure, axis = plt.subplots(figsize=(10, max(4, len(data) * 0.4)))

    sns.barplot(data=data, x="missing_count", y="column", ax=axis)
    axis.bar_label(axis.containers[0], padding=4)
    axis.margins(x=0.1)
    axis.set_title("Missing Values by Column")

    figure.tight_layout()
    return figure

def plot_categorical_distribution(distribution: pd.DataFrame,
                                  column: str) -> Figure:
    """
    Note: Close the figure after use.
    """
    def format_value(value):
        if pd.isna(value):
            return "NaN"

        if isinstance(value, str):
            parsed = pd.to_datetime(value, errors="coerce")

            if pd.notna(parsed):
                return parsed.strftime("%Y-%m-%d %H:%M")

        return str(value)

    if distribution.empty:
        return None

    data = distribution.copy()

    data["value"] = data["value"].map(format_value)

    figure, axis = plt.subplots(
        figsize=(10, max(4, min(40, len(data) * 0.35)))
    )

    print("Plotting categorical distribution....")

    sns.barplot(data=data, x="count", y="value", ax=axis)

    axis.set_title(f"{column} - Value Distribution")

    figure.tight_layout()

    print("Returning categorical distribution figure.")
    return figure

def plot_numerical_distribution(dataframe: pd.DataFrame, column: str,
                              analysis: NumericalColumnAnalysis):
    """
    Note: Close the figure after use.
    """
    if analysis.valid_count == 0:
        return None

    figure, axes = plt.subplots(
        2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]}
    )

    sns.histplot(data=dataframe, x=column, kde=True, ax=axes[0])

    axes[0].set_title(f"{column} - Distribution")

    iqr = analysis.iqr

    axes[0].axvline(iqr.lower, linestyle="--", label="IQR Lower")
    axes[0].axvline(iqr.upper, linestyle="--", label="IQR Upper")

    domain = analysis.domain

    if domain.lower is not None:
        axes[0].axvline(domain.lower, linestyle=":", label="Domain Lower")

    if domain.upper is not None:
        axes[0].axvline(domain.upper, linestyle=":", label="Domain Upper")

    axes[0].legend()

    sns.boxplot(data=dataframe, x=column, ax=axes[1])

    figure.tight_layout()
    return figure
