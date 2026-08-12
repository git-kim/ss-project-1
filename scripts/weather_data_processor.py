from pathlib import Path
import pandas as pd

from data_modules.data_io import (
    load_data_files_into_single_dataframe as load_data_files,
    save_dataframe_as_csv
    )

from project_modules.area_name_mapper import (
    get_area_name_from_observatory_code
    )

from project_modules.common import PROJECT_DIRECTORY_PATH

def transform1(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe[
        [
            "지점",
            "일시",
            "기온(°C)",
            "습도(%)",
            "풍속(m/s)"
        ]
    ].copy()

    result["일시"] = pd.to_datetime(result["일시"])
    result["지역"] = result["지점"].map(get_area_name_from_observatory_code)
    result["연월"] = result["일시"].dt.strftime("%Y%m").astype(int)
    result["시간대"] = result["일시"].dt.strftime("%H").astype(int)

    result = result.groupby(["연월", "시간대", "지역"], as_index=False, sort=False)\
                   .agg(평균기온=("기온(°C)", "mean"),
                        중앙기온=("기온(°C)", "median"),
                        최저기온=("기온(°C)", "min"),
                        최고기온=("기온(°C)", "max"),
                        기온표준편차=("기온(°C)", "std"),
                        평균습도=("습도(%)", "mean"),
                        중앙습도=("습도(%)", "median"),
                        최저습도=("습도(%)", "min"),
                        최고습도=("습도(%)", "max"),
                        습도표준편차=("습도(%)", "std"),
                        평균풍속=("풍속(m/s)", "mean"),
                        중앙풍속=("풍속(m/s)", "median"),
                        최저풍속=("풍속(m/s)", "min"),
                        최고풍속=("풍속(m/s)", "max"),
                        풍속표준편차=("풍속(m/s)", "std"))
    return result

def transform2(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe[
        [
            "지점",
            "일시",
            "기온(°C)",
            "습도(%)",
            "풍속(m/s)"
        ]
    ].copy()

    result["일시"] = pd.to_datetime(result["일시"])
    result["지역"] = result["지점"].map(get_area_name_from_observatory_code)
    result["연도"] = result["일시"].dt.year

    result = result.groupby(["연도", "지역"], as_index=False, sort=False)\
                   .agg(평균기온=("기온(°C)", "mean"),
                        중앙기온=("기온(°C)", "median"),
                        최저기온=("기온(°C)", "min"),
                        최고기온=("기온(°C)", "max"),
                        기온표준편차=("기온(°C)", "std"),
                        평균습도=("습도(%)", "mean"),
                        중앙습도=("습도(%)", "median"),
                        최저습도=("습도(%)", "min"),
                        최고습도=("습도(%)", "max"),
                        습도표준편차=("습도(%)", "std"),
                        평균풍속=("풍속(m/s)", "mean"),
                        중앙풍속=("풍속(m/s)", "median"),
                        최저풍속=("풍속(m/s)", "min"),
                        최고풍속=("풍속(m/s)", "max"),
                        풍속표준편차=("풍속(m/s)", "std"))
    return result

def process(input_path: str | Path, output_path: str | Path, output_name: str) -> None:
    input_root = Path(input_path)
    output_root = Path(output_path)

    df, _ = load_data_files(input_root, is_recursive=False, encoding="cp949")

    df1 = transform1(df)
    output_path = output_root / f"{output_name}.csv"
    save_dataframe_as_csv(df1, output_path, encoding="utf-8")

    df2 = transform2(df)
    output_path = output_root / f"연간{output_name}.csv"
    save_dataframe_as_csv(df2, output_path, encoding="utf-8")

def main() -> None:   
    project_directory_path = PROJECT_DIRECTORY_PATH

    folder_names = ["기상-대구", "기상-부산", "기상-서울", "기상-원주"]

    for folder_name in folder_names:
        input_path = project_directory_path / f"data/raw/{folder_name}"
        output_path = project_directory_path / "data/interim"
        process(input_path, output_path, f"{folder_name}")

if __name__ == "__main__":
    main()
