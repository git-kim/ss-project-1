from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    MODEL_FORMULA,
    STATIONS,
    add_year_column
    )

from data_modules.count_model import (
    fit_negative_binomial
    )

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from data_modules.data_io import (
    save_dataframe_as_csv,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

OVERALL_LABEL = "전체"

def get_dispersion_table(base_table: pd.DataFrame) -> pd.DataFrame:
    if base_table.empty:
        return pd.DataFrame()

    df_clean = add_year_column(base_table.dropna(subset=["이송수", "출동수"]))

    rows = []

    for target_column in ["출동수", "이송수"]:
        formula = MODEL_FORMULA.format(target=target_column)

        poisson_result = smf.glm(formula, data=df_clean,
                                 family=sm.families.Poisson()).fit()

        negative_binomial_result, alpha = fit_negative_binomial(formula, df_clean)

        squared_pearson = pd.Series(poisson_result.resid_pearson ** 2,
                                    index=df_clean.index)

        for station in [OVERALL_LABEL, *STATIONS]:
            group = (df_clean if station == OVERALL_LABEL
                     else df_clean[df_clean["소방서"] == station])

            counts = group[target_column]

            rows.append({
                "변수": target_column,
                "소방서": station,
                "관측N": len(group),
                "표본평균": counts.mean(),
                "표본분산": counts.var(),
                "분산÷평균": counts.var() / counts.mean(),
                "포아송 평균제곱피어슨잔차":
                    squared_pearson.loc[group.index].mean(),
                "포아송 AIC":
                    poisson_result.aic if station == OVERALL_LABEL else np.nan,
                "음이항 AIC":
                    negative_binomial_result.aic
                    if station == OVERALL_LABEL else np.nan,
                "음이항 alpha":
                    alpha if station == OVERALL_LABEL else np.nan,
                })

    return pd.DataFrame(rows)

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    dispersion_table = get_dispersion_table(base_table)
    save_dataframe_as_csv(dispersion_table,
                          BASE_OUTPUT_PATH / "table7_dispersion_check.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
