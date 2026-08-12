from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    add_year_column
    )

import pandas as pd

from data_modules.data_io import (
    save_dataframe_as_csv,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

def get_yearly_trend_table(base_table: pd.DataFrame) -> pd.DataFrame:
    if base_table.empty:
        return pd.DataFrame()

    df = add_year_column(base_table)

    result = (
        df
        .groupby("연도", as_index=False)
        .agg(관측N=("출동수", "size"),
             총출동수=("출동수", "sum"),
             총이송수=("이송수", "sum"),
             이송수결측N=("이송수", lambda counts: counts.isna().sum()),
             평균기온=("평균기온", "mean"))
        )

    result["출동수 전년대비"] = result["총출동수"].pct_change() * 100
    result["이송수 전년대비"] = result["총이송수"].pct_change() * 100

    return result

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    yearly_trend_table = get_yearly_trend_table(base_table)
    save_dataframe_as_csv(yearly_trend_table,
                          BASE_OUTPUT_PATH / "table10_yearly_trend.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
