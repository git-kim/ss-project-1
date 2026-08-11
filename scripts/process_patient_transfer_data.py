from pathlib import Path
import pandas as pd
from project_modules.area_name_mapper import get_area_name_from_fire_station_name
from project_modules.common import PROJECT_DIRECTORY_PATH

def process(root_directory: str, output_root_directory: str, prefix: str) -> None:
    root_path = Path(root_directory)

    for raw_data_directory in root_path.rglob("*"):
        if not raw_data_directory.is_dir():
            continue

        directory_name = raw_data_directory.name

        file_paths = list(raw_data_directory.glob("*.json"))

        if not file_paths:
            continue

        output_root_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_root_directory / f"{prefix}_{directory_name}.csv"

        data = None

        for file_path in file_paths:
            with file_path.open("r", encoding="utf-8") as f:
                df = pd.read_json(f)

                if df.empty:
                    continue

                df_new = df[["rsacGutFsttOgidNm", "stmtYm", "stmtHh", "ptntSdtSeCdNm", "ptntAge"]]

                df_new = df_new.rename(columns={
                    "rsacGutFsttOgidNm": "소방서",
                    "stmtYm": "연월",
                    "stmtHh": "시간대",
                    "ptntSdtSeCdNm": "성별"
                })

                df_new["지역"] = get_area_name_from_fire_station_name(directory_name)

                age_replacement = {9: 0, 19: 10, 29: 20, 39: 30, 49: 40, 59: 50,
                                   69: 60, 79: 70, 89: 80, 99: 80, 100: 80, 109: 80,
                                   110: 80, 120: 80, 259: -1}

                df_new["연령대"] = df_new["ptntAge"].replace(age_replacement)

                if data is None:
                    data = df_new.copy()
                else:
                    data = pd.concat([data, df_new], ignore_index=True)

        print(data.head())

        with output_file.open("w", encoding="utf-8") as f:
            data.to_csv(f, index=False, encoding="utf-8")

project_directory = PROJECT_DIRECTORY_PATH

raw_data_root_directory = project_directory / "data/raw/구급환자이송정보"
interim_data_root_directory = project_directory / "data/interim"

data_to_save = process(raw_data_root_directory, interim_data_root_directory, "구급환자이송정보")
