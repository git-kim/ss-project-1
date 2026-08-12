import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import seaborn as sns
import koreanize_matplotlib

from project_modules.area_name_mapper import AREA_FIRE_STATION_NAME_MAP

from data_modules.data_io import (
    save_figure,
    read_data_file_into_dataframe
    )

from project_modules.common import PROJECT_DIRECTORY_PATH

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

def plot(base_table: pd.DataFrame) -> Figure:
    """
    Note: Close the figure after use.
    """
    if base_table.empty:
        return None

    bins = [-15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
    labels = [
        "-15 ~ -10",
        "-10 ~ -5",
        "-5 ~ 0",
        "0 ~ 5",
        "5 ~ 10",
        "10 ~ 15",
        "15 ~ 20",
        "20 ~ 25",
        "25 ~ 30",
        "30 ~ 35",
        "35 ~ 40"
        ]

    base_table["기온구간"] = pd.cut(base_table["평균기온"], bins=bins, labels=labels)

    station_data  = base_table.groupby(["소방서", "기온구간"], observed=True).agg(
        평균이송수=("이송수", "mean")
        ).reset_index()

    overall_data  = base_table.groupby("기온구간", observed=True).agg(
        전체평균이송수=("이송수", "mean")
        ).reset_index()

    figure, axis = plt.subplots(figsize=(9, 6))

    stations = list(AREA_FIRE_STATION_NAME_MAP.keys())
    colors = sns.color_palette("tab10", n_colors=len(stations))

    temperature_order = list(base_table["기온구간"].cat.categories)

    station_data = (
        base_table
        .groupby(["기온구간", "소방서"], observed=True)
        .agg(평균이송수=("이송수", "mean"))
        .reset_index()
        )

    overall_data = (
        base_table
        .groupby("기온구간", observed=True)
        .agg(전체평균이송수=("이송수", "mean"))
        .reindex(temperature_order)
        .reset_index()
    )

    n_stations = len(stations)

    n_bars = n_stations + 1
    group_width = 0.8
    bar_width = group_width / n_bars

    x = np.arange(len(temperature_order))

    for i, (station, color) in enumerate(zip(stations, colors)):
        values = (
            station_data[station_data["소방서"] == station]
            .set_index("기온구간")
            .reindex(temperature_order)["평균이송수"]
            .to_numpy()
            )

        positions = x - group_width / 2 + bar_width / 2 + i * bar_width

        axis.bar(positions, values, width=bar_width, color=color, label=station)

    overall_values = overall_data["전체평균이송수"].to_numpy()

    overall_positions = x - group_width / 2 + bar_width / 2 + n_stations * bar_width

    axis.bar(overall_positions, overall_values, width=bar_width,
             color="lightgray", edgecolor="black", label="전체 평균")


    axis.set_xticks(x)
    axis.set_xticklabels(temperature_order)

    half_group_width = group_width / 2

    axis.set_xlim(
        x[0] - half_group_width,
        x[-1] + half_group_width
    )

    axis.set_title("평균 기온 구간별 평균 이송 수")
    axis.set_xlabel("평균 기온 구간 / ℃")
    axis.set_ylabel("평균 이송 수")

    axis.set_ylim(bottom=0)

    axis.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True,
        length=5,
        width=1
    )

    legend = axis.legend(
        title=None,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True
    )

    legend.get_frame().set_edgecolor("black")
    legend.get_frame().set_linewidth(1.0)

    figure.tight_layout()
    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    figure = plot(base_table)
    save_figure(figure,
                BASE_OUTPUT_PATH / "figure4_temp_range_vs_transport.svg",
                should_close=True)

if __name__ == "__main__":
    main()
