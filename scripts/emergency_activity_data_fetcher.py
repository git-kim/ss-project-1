from pathlib import Path
from project_modules.common import PROJECT_DIRECTORY_PATH, get_data_api_key
from project_modules.emergency_info_api import (
    EmergencyInfoApiClient,
    EmergencyInfoApiConfig
)

STATIONS = [
    "강남소방서",
    "강동소방서",
    "노원소방서",
    "수성소방서",
    "해운대소방서",
    "원주소방서"
]

MONTHS = [f"{year}{month:02d}"
          for year in range(2017, 2026)
          for month in range(1, 13)]

def main() -> None:
    api_key = get_data_api_key()

    if not api_key:
        raise RuntimeError("DATA_API_KEY is not set.")

    config = EmergencyInfoApiConfig(
        api_relative_url="getEmgencyActivityInfo",
        output_dir=Path(PROJECT_DIRECTORY_PATH / "data/raw/구급활동정보"),
        year_month_key="gutYm",
    )

    with EmergencyInfoApiClient(config) as client:
        client.fetch_all(api_key=api_key, stations=STATIONS, months=MONTHS)

if __name__ == "__main__":
    main()
