import pandas as pd

STATIONS = [
    "강남소방서",
    "강동소방서",
    "노원소방서",
    "수성소방서",
    "해운대소방서",
    "원주소방서"
]

TEMPERATURE_BINS = [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35]
TEMPERATURE_LABELS = [
    "-10 ~ -5",
    "-5 ~ 0",
    "0 ~ 5",
    "5 ~ 10",
    "10 ~ 15",
    "15 ~ 20",
    "20 ~ 25",
    "25 ~ 30",
    "30 ~ 35"
    ]

REFERENCE_TEMPERATURE = 14.0
REFERENCE_HOUR = 14.0
REFERENCE_YEAR = 2019

MODEL_FORMULA = "{target} ~ bs(평균기온, df=3) * C(소방서) + C(시간대) + C(연도)"

def add_year_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    result["연도"] = result["연월"] // 100
    return result

def add_temperature_range_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    result["기온구간"] = pd.cut(result["평균기온"], bins=TEMPERATURE_BINS,
                            labels=TEMPERATURE_LABELS)
    return result
