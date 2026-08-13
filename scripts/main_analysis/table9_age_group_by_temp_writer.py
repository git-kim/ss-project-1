from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    STATIONS,
    add_temperature_range_column
    )

import pandas as pd

from project_modules.area_name_mapper import AREA_OBSERVATORY_CODE_MAP

from data_modules.data_io import (
    load_specific_data_files_into_single_dataframe as load_data_files,
    save_dataframe_as_csv
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/interim"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

AGE_GROUP_LABELS = {
    -1: "미상",
    0: "9세 이하",
    10: "10대",
    20: "20대",
    30: "30대",
    40: "40대",
    50: "50대",
    60: "60대",
    70: "70대",
    80: "80세 이상"
}

SOURCE_FILE_PREFIX_MAP = {
    "출동수": "구급활동정보",
    "이송수": "구급환자이송정보"
}

def load_data() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    frames = {}

    for metric, file_prefix in SOURCE_FILE_PREFIX_MAP.items():
        file_paths = [BASE_INPUT_PATH / f"{file_prefix}_{station}.csv"
                      for station in STATIONS]
        frames[metric], _ = load_data_files(file_paths, encoding="utf-8")

    weather_file_paths = [BASE_INPUT_PATH / f"기상-{area_name}.csv"
                          for area_name in AREA_OBSERVATORY_CODE_MAP.values()]
    weather_df, _ = load_data_files(weather_file_paths, encoding="utf-8")

    return frames, weather_df

def get_age_group_table(frames: dict[str, pd.DataFrame],
                        weather_df: pd.DataFrame) -> pd.DataFrame:
    key_columns = ["연월", "시간대", "지역"]
    group_columns = ["지표", "소방서", "기온구간"]

    results = []

    for metric, frame in frames.items():
        merged = pd.merge(frame.dropna(subset="시간대"),
                          weather_df[[*key_columns, "평균기온"]],
                          on=key_columns, how="left")

        merged = add_temperature_range_column(merged)
        merged["연령대"] = merged["연령대"].map(AGE_GROUP_LABELS)
        merged["지표"] = metric

        counts = (
            merged
            .groupby([*group_columns, "연령대"], as_index=False, observed=True)
            .size()
            .rename(columns={"size": "건수"})
            )

        cell_counts = (
            merged[[*group_columns, *key_columns]]
            .drop_duplicates()
            .groupby(group_columns, as_index=False, observed=True)
            .size()
            .rename(columns={"size": "관측N"})
            )

        result = pd.merge(counts, cell_counts, on=group_columns, how="left")

        result["연월시간대당평균건수"] = result["건수"] / result["관측N"]
        result["구성비"] = (
            result["건수"]
            / result.groupby(group_columns, observed=True)["건수"]
                    .transform("sum")
            * 100
            )

        results.append(result)

    return (pd.concat(results, ignore_index=True)
            .sort_values([*group_columns, "연령대"], ignore_index=True))

def main() -> None:
    frames, weather_df = load_data()
    age_group_table = get_age_group_table(frames, weather_df)
    save_dataframe_as_csv(age_group_table,
                          BASE_OUTPUT_PATH / "table9_age_group_by_temp.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
