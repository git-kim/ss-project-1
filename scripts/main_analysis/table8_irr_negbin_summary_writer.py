from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    MODEL_FORMULA,
    REFERENCE_HOUR,
    REFERENCE_TEMPERATURE,
    REFERENCE_YEAR,
    STATIONS,
    add_year_column
    )

from data_modules.count_model import (
    fit_negative_binomial,
    get_irr_with_ci
    )

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from data_modules.data_io import (
    save_dataframe_as_csv,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

OUT_OF_RANGE_TEXT = "관측범위 밖"

def get_irr_comparison_table(base_table: pd.DataFrame,
                             target_temps: list[float] | None = None)\
    -> pd.DataFrame:
    if base_table.empty:
        return pd.DataFrame()

    if target_temps is None:
        target_temps = [-5.0, 0.0, 25.0, 30.0, 33.0]

    df_clean = add_year_column(base_table.dropna(subset=["이송수", "출동수"]))

    observed_range = df_clean.groupby("소방서")["평균기온"].agg(["min", "max"])

    results = {}

    for target_column in ["출동수", "이송수"]:
        formula = MODEL_FORMULA.format(target=target_column)

        # same formula, two families: only the dispersion assumption differs
        poisson_result = smf.glm(formula, data=df_clean,
                                 family=sm.families.Poisson()).fit()
        negative_binomial_result, _ = fit_negative_binomial(formula, df_clean)

        for station in STATIONS:
            covariates = {
                "소방서": station,
                "시간대": REFERENCE_HOUR,
                "연도": REFERENCE_YEAR,
                }

            _, poisson_lower, poisson_upper = get_irr_with_ci(
                poisson_result, covariates, target_temps,
                REFERENCE_TEMPERATURE)

            irr, lower, upper = get_irr_with_ci(
                negative_binomial_result, covariates, target_temps,
                REFERENCE_TEMPERATURE)

            results[(target_column, station)] = (
                irr, lower, upper, poisson_lower, poisson_upper)

    rows = []

    for station in STATIONS:
        minimum, maximum = observed_range.loc[station]

        for index, temperature in enumerate(target_temps):
            row = {"소방서": station, "평균기온": temperature}

            for target_column in ["출동수", "이송수"]:
                irr, lower, upper, poisson_lower, poisson_upper = \
                    results[(target_column, station)]

                if not minimum <= temperature <= maximum:
                    row[f"{target_column} IRR"] = OUT_OF_RANGE_TEXT
                    row[f"{target_column} 증감률"] = OUT_OF_RANGE_TEXT
                    row[f"{target_column} 95% CI (포아송)"] = OUT_OF_RANGE_TEXT
                    row[f"{target_column} 95% CI (음이항)"] = OUT_OF_RANGE_TEXT
                    continue

                row[f"{target_column} IRR"] = f"{irr[index]:.3f}"
                row[f"{target_column} 증감률"] = f"{(irr[index] - 1) * 100:+.1f}%"
                row[f"{target_column} 95% CI (포아송)"] = (
                    f"{poisson_lower[index]:.3f} - {poisson_upper[index]:.3f}")
                row[f"{target_column} 95% CI (음이항)"] = (
                    f"{lower[index]:.3f} - {upper[index]:.3f}")

            rows.append(row)

    return pd.DataFrame(rows)

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    comparison_table = get_irr_comparison_table(base_table)
    save_dataframe_as_csv(comparison_table,
                          BASE_OUTPUT_PATH / "table8_irr_negbin_summary.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
