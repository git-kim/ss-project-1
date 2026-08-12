import pandas as pd
from data_modules.data_io import (
    read_data_file_into_dataframe,
    save_dataframe_as_csv
    )
from project_modules.common import PROJECT_DIRECTORY_PATH

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

def get_base_table_description(base_table: pd.DataFrame) -> pd.DataFrame:
    target_columns = ["출동수", "이송수", "평균기온"]
    result = base_table[target_columns].describe().T
    result = result.reset_index(names="변수")
    result["sum"] = base_table[target_columns].sum().array

    result = result[["변수", "count", "sum", "mean", "std", "min", "50%", "max"]].rename(
        columns={
            "count": "N",
            "sum": "총계",
            "mean": "평균",
            "std": "표준편차",
            "50%": "중앙값",
            "min": "최솟값",
            "max": "최댓값"
            })

    return result

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    result = get_base_table_description(base_table)
    save_dataframe_as_csv(result,
                          BASE_OUTPUT_PATH / "table1_description.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
