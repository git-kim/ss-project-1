import pandas as pd
from data_modules.data_io import (
    read_data_file_into_dataframe,
    save_dataframe_as_csv
    )
from project_modules.common import PROJECT_DIRECTORY_PATH

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

def get_statistics(base_table: pd.DataFrame)\
    -> pd.DataFrame:
    base_table["월"] = base_table["연월"] % 100

    result = (
        base_table.groupby("월", observed=False, as_index=False)
        .agg(
            관측N=("소방서", "count"),
            평균기온=("평균기온", "mean"),
            총출동수=("출동수", lambda x: int(x.sum())),
            평균출동수=("출동수", "mean"),
            총이송수=("이송수", lambda x: int(x.sum())),
            평균이송수=("이송수", "mean")
            )
            )

    return result

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    result = get_statistics(base_table)
    save_dataframe_as_csv(result,
                          BASE_OUTPUT_PATH / "table4_monthly.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
