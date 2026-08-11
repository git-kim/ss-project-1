AREA_FIRE_STATION_NAME_MAP = {
    "강남소방서": "서울",
    "강동소방서": "서울",
    "노원소방서": "서울",
    "수성소방서": "대구",
    "원주소방서": "원주",
    "해운대소방서": "부산"
    }

AREA_OBSERVATORY_CODE_MAP = {
    143: "대구",
    159: "부산",
    108: "서울",
    114: "원주"
}

def get_area_name_from_fire_station_name(fire_station_name: str) -> str | None:
    return AREA_FIRE_STATION_NAME_MAP.get(fire_station_name, None)

def get_area_name_from_observatory_code(observatory_code: int) -> str | None:
    return AREA_OBSERVATORY_CODE_MAP.get(observatory_code, None)