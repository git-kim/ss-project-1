from pathlib import Path
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

SUPPORTED_FILE_SUFFIXES = {".csv", ".json"}

def find_data_files(input_path: str | Path, is_recursive: bool) -> list[Path]:
    def get_sorting_key(file_path: Path) -> str:
        return str(file_path).lower()

    path = Path(input_path)

    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_FILE_SUFFIXES:
            raise ValueError(f"Unsupported file: {path}")
        return [path]

    if not path.is_dir():
        raise FileNotFoundError(path)

    pattern = "**/*" if is_recursive else "*"

    generator = (
        file_path
        for file_path in path.glob(pattern)
        if file_path.is_file() and file_path.suffix.lower()
        in SUPPORTED_FILE_SUFFIXES
        ) # generator expression

    return sorted(generator, key=get_sorting_key)

def read_data_file_into_dataframe(file_path: str | Path, encoding: str)\
    -> pd.DataFrame:
    path = Path(file_path)

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, encoding=encoding)

    if suffix == ".json":
        return pd.read_json(path, encoding=encoding)

    raise ValueError(f"Unsupported file: {path}")

def load_data_files_into_single_dataframe(input_path: str, is_recursive: bool,
                                          encoding: str)\
    -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """
    Returns:
        (dataframe, file_info)
    """

    file_paths = find_data_files(input_path, is_recursive=is_recursive)

    if not file_paths:
        raise FileNotFoundError(f"No data files found: {input_path}")

    dataframes = []
    file_info = []

    for file_path in file_paths:
        try:
            dataframe = read_data_file_into_dataframe(
                file_path,
                encoding=encoding,
            )

            file_info.append({
                "file": str(file_path),
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
                "status": (
                    "empty"
                    if dataframe.empty
                    else "loaded"
                ),
            })

            if dataframe.empty:
                continue

            dataframe = dataframe.copy()

            if "source_file" in dataframe.columns:
                dataframe = dataframe.rename(columns={"source_file": "_source_file"})

            dataframe.insert(0, "source_file", str(file_path))

            dataframes.append(dataframe)

        except Exception as error:
            file_info.append({
                "file": str(file_path),
                "rows": 0,
                "columns": 0,
                "status": f"error: {error}",
            })

    if not dataframes:
        return pd.DataFrame(), file_info

    dataframe = pd.concat(dataframes, ignore_index=True, sort=False)

    return dataframe, file_info

def save_dataframe_as_csv(dataframe: pd.DataFrame, output_path: str | Path,
                          encoding: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False, encoding=encoding)

def save_text(text: object, output_path: str, encoding: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(text), encoding=encoding)

def save_figure(figure: Figure, output_path: str | Path, should_close: bool) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        figure.savefig(path.with_suffix(".svg"), bbox_inches="tight")
        # figure.savefig(path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    finally:
        if should_close:
            plt.close(figure)
