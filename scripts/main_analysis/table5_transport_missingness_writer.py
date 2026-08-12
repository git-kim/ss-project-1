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

    result = (
        base_table.groupby("소방서", observed=False, as_index=False)
        .agg(
            N=("이송수", "size"),
            이송수존재N=("이송수", "count"),
            이송수결측N=("이송수", lambda x: x.isna().sum()),
            결측률=("이송수", lambda x: x.isna().sum() / len(x) * 100.0),
            )
            )

    return result

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    result = get_statistics(base_table)
    save_dataframe_as_csv(result,
                          BASE_OUTPUT_PATH / "table5_transport_missingness.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
