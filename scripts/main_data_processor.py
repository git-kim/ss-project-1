import pandas as pd
from project_modules.area_name_mapper import AREA_OBSERVATORY_CODE_MAP
from project_modules.common import PROJECT_DIRECTORY_PATH
from data_modules.data_io import (
    load_specific_data_files_into_single_dataframe as load_data_files,
    save_dataframe_as_csv
    )

STATIONS = [
    "강남소방서",
    "강동소방서",
    "노원소방서",
    "수성소방서",
    "해운대소방서",
    "원주소방서"
]

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/interim"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    transport_data_file_paths = [BASE_INPUT_PATH / f"구급환자이송정보_{station}.csv"
                                for station in STATIONS]
    transport_df, _ = load_data_files(transport_data_file_paths, encoding="utf-8")
    # print(transport_df.head(10))

    dispatch_data_file_paths = [BASE_INPUT_PATH / f"구급활동정보_{station}.csv"
                                for station in STATIONS]
    dispatch_df, _ = load_data_files(dispatch_data_file_paths, encoding="utf-8")
    # print(dispatch_df.head(10))

    weather_file_paths = [BASE_INPUT_PATH / f"기상-{area_name}.csv"
                          for area_name in AREA_OBSERVATORY_CODE_MAP.values()]
    weather_df, _ = load_data_files(weather_file_paths, encoding="utf-8")
    # print(weather_df.head(10))

    return transport_df, dispatch_df, weather_df

def create_base_table(transport_df: pd.DataFrame, dispatch_df: pd.DataFrame,
                      weather_df: pd.DataFrame) -> None:
    key_columns = ["연월", "시간대", "지역"]
    station_group_columns = ["소방서", *key_columns]

    transport_counts = (
        transport_df
        .dropna(subset="시간대")
        .groupby(station_group_columns, as_index=False, sort=False)
        .size()
        .rename(columns={"size": "이송수"})
        )
    
    dispatch_counts = (
        dispatch_df
        .dropna(subset="시간대")
        .groupby(station_group_columns, as_index=False, sort=False)
        .size()
        .rename(columns={"size": "출동수"})
        )

    merged = pd.merge(transport_counts, dispatch_counts,
                      on=station_group_columns, how="outer")

    merged = pd.merge(merged, weather_df[[*key_columns, "평균기온"]],
                      on=key_columns,
                      how="left")

    print(f"출동수 missing count: {merged["출동수"].isna().sum()}")
    print(f"이송수 missing count: {merged["이송수"].isna().sum()}")
    print(f"평균기온 missing count: {merged["평균기온"].isna().sum()}")
    return merged

def main() -> None:
    transport_df, dispatch_df, area_weather_map = load_data()
    base_table = create_base_table(transport_df, dispatch_df, area_weather_map)
    save_dataframe_as_csv(base_table, BASE_OUTPUT_PATH / "base_table.csv", encoding="utf-8")

if __name__ == "__main__":
    main()
