from pathlib import Path
import pandas as pd
import numpy as np

def locate_files_using_values_in_column(root_directory: str,
                                        target_column_name: str,
                                        values: list[object],
                                        output_column_names: list[str]) -> None:
    root_path = Path(root_directory)
    for file_path in root_path.rglob("*.json"):
        current_folder_name = file_path.parent.name
        # print(f"Processing JSON in folder: '{current_folder_name}' {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                df = pd.read_json(f)

            if df.empty:
                print("The file is empty.")
                continue

            column_names = df.columns.to_list()

            if target_column_name not in column_names:
                print("No columns found.")
                return

            result_df = df[df[target_column_name].isin(values)][output_column_names]
            if result_df.empty:
                return

            print(f"{current_folder_name} {file_path.name}: {result_df}")

        except Exception as e:
            print(type(e))
            print(f"Error reading {file_path}: {e}")
