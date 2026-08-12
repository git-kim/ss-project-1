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
    bins = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
    labels = [
        "-20 ~ -15",
        "-15 ~ -10",
        "-10 ~ -5",
        "-5 ~ 0",
        "0 ~ 5",
        "5 ~ 10",
        "10 ~ 15",
        "15 ~ 20",
        "20 ~ 25",
        "25 ~ 30",
        "30 ~ 35",
        "35 ~ 40"
        ]

    base_table["기온구간"] = pd.cut(base_table["평균기온"], bins=bins, labels=labels)

    result = (
        base_table.groupby(["소방서", "기온구간"], observed=False, as_index=False)
        .agg(
            관측N=("평균기온", "count"),
            총출동수=("출동수", lambda x: int(x.sum())),
            평균출동수=("출동수", "mean"),
            총이송수=("이송수", lambda x: int(x.sum())),
            평균이송수=("이송수", "mean"),
            평균평균기온=("평균기온", "mean")
            )
            )
    return result

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    result = get_statistics(base_table)
    save_dataframe_as_csv(result,
                          BASE_OUTPUT_PATH / "table3_station_temp_range.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
