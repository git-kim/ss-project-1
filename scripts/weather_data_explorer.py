import matplotlib.pyplot as plt
import koreanize_matplotlib
from project_modules.common import PROJECT_DIRECTORY_PATH, sanitize_filename

from data_modules.data_io import (
    load_data_files_into_single_dataframe as load_data_files,
    save_text,
    save_figure
    )

from data_modules.data_analysis import (
    analyze_categorical_distribution,
    analyze_missing_values,
    analyze_numerical_column,
    classify_columns,
    # plot_categorical_distribution,
    plot_missing_values,
    plot_numerical_distribution
    )

RAW_DATA_ENCODING = "cp949"
DESIRED_ENCODING = "utf-8"

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/raw"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/eda/weather"

NUMERIC_CONFIG = {
    "기온(°C)": (-50., 60.),
    "습도(%)": (0., 100.),
    "풍속(m/s)": (0., None),
}

FOLDER_NAMES = ["기상-대구", "기상-부산", "기상-서울", "기상-원주"]

def explore_folder(folder_name: str) -> None:
    output_path = BASE_OUTPUT_PATH / folder_name
    dataframe, file_info = load_data_files(BASE_INPUT_PATH / folder_name,
                                        is_recursive=True,
                                        encoding=RAW_DATA_ENCODING)
    save_text(
        "\n".join(
            f"{item['file']}\t"
            f"{item['rows']} rows\t"
            f"{item['columns']} columns\t"
            f"{item['status']}"
            for item in file_info
        ),
        output_path / "files.txt",
        encoding=DESIRED_ENCODING
    )

    missing_values = analyze_missing_values(dataframe)

    save_text(missing_values.to_string(index=False),
              output_path / "missing_values.txt", encoding=DESIRED_ENCODING)

    figure = plot_missing_values(missing_values)

    if figure is not None:
        save_figure(figure, output_path / "missing_values", should_close=True)

    categorical_columns, numerical_columns = classify_columns(dataframe)

    for column in categorical_columns:
        distribution = analyze_categorical_distribution(dataframe, column)

        save_text(
            distribution.to_string(index=False),
            output_path / sanitize_filename(f"categorical_{column}.txt"),
            encoding=DESIRED_ENCODING
        )

        # figure = plot_categorical_distribution(distribution, column)

        # if figure is not None:
        #     save_figure(figure,
        #                 output_path / sanitize_filename(f"categorical_{column}"),
        #                 should_close=True)

    for column in numerical_columns:
        lower, upper = NUMERIC_CONFIG.get(column, (None, None))

        analysis = analyze_numerical_column(dataframe, column, lower, upper)

        save_text(repr(analysis),
                  output_path / sanitize_filename(f"numerical_{column}.txt"),
                  encoding=DESIRED_ENCODING)

        figure = plot_numerical_distribution(dataframe, column, analysis)

        if figure is not None:
            save_figure(figure,
                        output_path / sanitize_filename(f"numerical_{column}"),
                        should_close=True)

def main() -> None:
    for folder_name in FOLDER_NAMES:
        explore_folder(folder_name)

if __name__ == "__main__":
    main()
