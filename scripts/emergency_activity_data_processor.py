from pathlib import Path
import pandas as pd

from data_modules.data_io import (
    load_data_files_in_specific_directory,
    save_dataframe_as_csv
    )

from project_modules.area_name_mapper import (
    get_area_name_from_fire_station_name
    )

from project_modules.common import PROJECT_DIRECTORY_PATH


def transform(dataframe: pd.DataFrame, directory_name: str) -> pd.DataFrame:
    desired_column_names = {
        "rsacGutFsttOgidNm": "소방서",
        "gutYm": "연월", # 출동 기준
        "gutHh": "시간대", # 출동 기준
        "ptntSdtSeCdNm": "성별"
        }

    age_replacement = {
        "9세 이하": 0,
        "10~19세": 10,
        "20~29세": 20,
        "30~39세": 30,
        "40~49세": 40,
        "50~59세": 50,
        "60~69세": 60,
        "70~79세": 70,
        "80세 이상": 80,
        "기타": -1
        }

    result = dataframe[["rsacGutFsttOgidNm", "gutYm", "gutHh", "ptntSdtSeCdNm",
                        "ptntAge"]].dropna(subset="gutHh").copy()

    result = result.rename(columns=desired_column_names)

    result["지역"] = get_area_name_from_fire_station_name(directory_name)

    result["연령대"] = result["ptntAge"].replace(age_replacement)

    return result

def process(input_path: str | Path, output_path: str | Path, prefix: str) -> None:
    input_root = Path(input_path)
    output_root = Path(output_path)

    for directory in input_root.rglob("*"):
        if not directory.is_dir():
            continue

        df = load_data_files_in_specific_directory(
            directory,
            encoding="utf-8"
        )

        if df.empty:
            continue

        print(len(df))

        df = transform(df, directory.name)

        print(len(df))

        output_path = output_root / f"{prefix}_{directory.name}.csv"

        save_dataframe_as_csv(df, output_path, encoding="utf-8")

def main() -> None:
    project_directory_path = PROJECT_DIRECTORY_PATH

    input_path = project_directory_path / "data/raw/구급활동정보"
    output_path = project_directory_path / "data/interim"

    process(input_path, output_path, "구급활동정보")

if __name__ == "__main__":
    main()
