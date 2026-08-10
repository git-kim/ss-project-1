from modules.numeric_value_analyzer import describe_numeric_values_recursively as describe
from pathlib import Path

project_directory = Path(__file__).resolve().parent.parent

columns = ["기온(°C)", "풍속(m/s)", "습도(%)"]

raw_data_root_directory = project_directory / "data/raw/기상-대구"
describe(raw_data_root_directory, "cp949", columns)

raw_data_root_directory = project_directory / "data/raw/기상-부산"
describe(raw_data_root_directory, "cp949", columns)

raw_data_root_directory = project_directory / "data/raw/기상-서울"
describe(raw_data_root_directory, "cp949", columns)

raw_data_root_directory = project_directory / "data/raw/기상-원주"
describe(raw_data_root_directory, "cp949", columns)
