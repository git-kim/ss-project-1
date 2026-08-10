from modules.unique_value_finder import get_unique_values_recursively as get_uniques
from pathlib import Path
from pprint import pprint

output_dict = {}

project_directory = Path(__file__).resolve().parent.parent

raw_data_root_directory = project_directory / "data/raw/구급활동정보"

from modules.value_file_locator import locate_files_using_values_in_column
locate_files_using_values_in_column(raw_data_root_directory, "cptcSeCdNm", ["센터"], ["cptcSeCdNm", "egrcSiggCdNm", "sptMvmnDtc"])

data_to_save = get_uniques(raw_data_root_directory, output_dict)

unique_values_path = project_directory / "data/interim/구급활동정보_unique_values.json"

with open(unique_values_path, "w", encoding="utf-8") as f:
    pprint(data_to_save, indent=4, stream=f)

