from pathlib import Path
import pandas as pd

def describe_numeric_values_recursively(root_directory: str, encoding: str,
                                        column_names: list[str]) -> None:
    root_path = Path(root_directory)
    for file_path in root_path.rglob("*.csv"):
        # current_folder_name = file_path.parent.name
        # print(f"Processing CSV in folder: '{current_folder_name}' {file_path.name}")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                df = pd.read_csv(f)

            if df.empty:
                print("The file is empty.")
                continue

            for column_name in column_names:
                has_nan = df[column_name].isna().any()
                if has_nan:
                    print(f"{file_path.name} has NaN (column: {column_name}).")

            print(df.describe())
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
