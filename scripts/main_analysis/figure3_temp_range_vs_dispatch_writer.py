import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import seaborn as sns
import koreanize_matplotlib

from project_modules.plot_style import (
    apply_plot_style,
    get_station_style,
    set_bin_edge_ticks,
    OVERALL_COLOR,
    REFERENCE_COLOR
    )

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
        평균출동수=("출동수", "mean")
        ).reset_index()

    overall_data  = base_table.groupby("기온구간", observed=True).agg(
        전체평균출동수=("출동수", "mean")
        ).reset_index()

    # 평균 기온은 관측소의 시간별 기온을 연월, 시간대, 지역별로 평균한 값이다.
    # 따라서 하루 단위 폭염이나 한파는 이 값에 남지 않는다.

    apply_plot_style()

    figure, axis = plt.subplots(figsize=(10, 6))

    stations = list(AREA_FIRE_STATION_NAME_MAP.keys())

    temperature_order = list(base_table["기온구간"].cat.categories)

    station_data = (
        base_table
        .groupby(["기온구간", "소방서"], observed=True)
        .agg(평균출동수=("출동수", "mean"))
        .reset_index()
        )

    overall_data = (
        base_table
        .groupby("기온구간", observed=True)
        .agg(전체평균출동수=("출동수", "mean"))
        .reindex(temperature_order)
        .reset_index()
    )

    x = np.arange(len(temperature_order))

    for station in stations:
        style = get_station_style(station)

        values = (
            station_data[station_data["소방서"] == station]
            .set_index("기온구간")
            .reindex(temperature_order)["평균출동수"]
            .to_numpy()
            )

        axis.plot(x, values, label=station, color=style["color"],
                  marker=style["marker"], linestyle=style["linestyle"],
                  linewidth=2, markersize=7)

    overall_values = overall_data["전체평균출동수"].to_numpy()

    axis.plot(x, overall_values, label="전체 평균", color=OVERALL_COLOR,
              marker="o", linewidth=4, markersize=9, alpha=0.9, zorder=1)

    set_bin_edge_ticks(axis, bins, first_edge_position=-0.5)

    axis.set_title("평균 기온 구간별 평균 출동 수")
    axis.set_xlabel("평균 기온 / ℃")
    axis.set_ylabel("평균 출동 수")

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
                BASE_OUTPUT_PATH / "figure3_temp_range_vs_dispatch.svg",
                should_close=True)

if __name__ == "__main__":
    main()
