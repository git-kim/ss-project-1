from pathlib import Path
import pandas as pd
from modules.area_name_mapper import get_area_name_from_fire_station_name

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

                df_new = df[["rsacGutFsttOgidNm", "gutYm", "gutHh", "ptntSdtSeCdNm", "ptntAge"]]

                df_new = df_new.rename(columns={
                    "rsacGutFsttOgidNm": "소방서",
                    "gutYm": "연월",
                    "gutHh": "시간대",
                    "ptntSdtSeCdNm": "성별"
                })

                df_new["지역"] = get_area_name_from_fire_station_name(directory_name)

                age_replacement = {"9세 이하": 0, "10~19세": 10, "20~29세": 20,
                                   "30~39세": 30, "40~49세": 40, "50~59세": 50,
                                   "60~69세": 60, "70~79세": 70, "80세 이상": 80,
                                   "기타": -1}

                df_new["연령대"] = df_new["ptntAge"].replace(age_replacement)

                if data is None:
                    data = df_new.copy()
                else:
                    data = pd.concat([data, df_new], ignore_index=True)

        print(data.head())

        with output_file.open("w", encoding="utf-8") as f:
            data.to_csv(f, index=False, encoding="utf-8")

project_directory = Path(__file__).resolve().parent.parent

raw_data_root_directory = project_directory / "data/raw/구급활동정보"
interim_data_root_directory = project_directory / "data/interim"

data_to_save = process(raw_data_root_directory, interim_data_root_directory, "구급활동정보")
