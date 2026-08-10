from pathlib import Path
import pandas as pd
import numpy as np

def get_unique_values_recursively(root_directory: str, output_dict: dict[str, set[object]]) -> None:
    root_path = Path(root_directory)
    for file_path in root_path.rglob("*.json"):
        # current_folder_name = file_path.parent.name
        # print(f"Processing JSON in folder: '{current_folder_name}' {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                df = pd.read_json(f)

            if df.empty:
                print("The file is empty.")
                continue

            column_names = df.columns.to_list()

            for column_name in column_names:
                output_dict.setdefault(column_name, set())
            for column_name in column_names:
                has_nan = df[column_name].hasnans
                unique_values = df[column_name].dropna().unique()
                output_dict[column_name].update(unique_values)

                if has_nan:
                    output_dict[column_name].add(np.nan)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return output_dict
