from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    STATIONS,
    TEMPERATURE_BINS,
    TEMPERATURE_LABELS,
    add_temperature_range_column
    )

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import koreanize_matplotlib

from project_modules.plot_style import (
    apply_plot_style,
    get_station_color,
    REFERENCE_COLOR,
    set_bin_edge_ticks
    )

from data_modules.data_io import (
    save_figure,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

TARGET_COLUMNS = {"dispatch": "출동수", "transport": "이송수"}

def plot(base_table: pd.DataFrame, target_column: str) -> Figure:
    """
    Note: Close the figure after use.
    """
    if base_table.empty:
        return None

    df = add_temperature_range_column(base_table.dropna(subset=target_column))
    df["시간대"] = df["시간대"].astype(int)

    # 평균 기온은 관측소의 시간별 기온을 연월, 시간대, 지역별로 평균한 값이다.
    # 따라서 하루 단위 폭염이나 한파는 이 값에 남지 않는다.

    apply_plot_style()

    figure, axes = plt.subplots(2, 3, figsize=(12, 7.3))

    # one shared color scale so the panels can be compared with each other
    highest = df.groupby(["소방서", "시간대", "기온구간"], observed=True)\
                [target_column].mean().max()

    hour_ticks = list(range(0, 24, 3))

    for index, (axis, station) in enumerate(zip(axes.flat, STATIONS)):
        grid = (
            df[df["소방서"] == station]
            .pivot_table(index="시간대", columns="기온구간", values=target_column,
                         aggfunc="mean", observed=True)
            .reindex(columns=TEMPERATURE_LABELS)
            )

        sns.heatmap(grid, ax=axis, cmap="YlOrRd", vmin=0, vmax=highest,
                    linewidths=0.3, linecolor="white", cbar=False)

        axis.set_title(station)
        axis.set_xlabel("")
        axis.set_ylabel("")
        axis.grid(False)

        # seaborn strips the frame, which leaves the inward ticks hanging in
        # empty space, so it goes back on with the shared line weight
        for spine in axis.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(mpl.rcParams["axes.linewidth"])
            spine.set_color(mpl.rcParams["axes.edgecolor"])

        axis.tick_params(top=False, right=False, length=3)

        axis.set_yticks([hour + 0.5 for hour in hour_ticks])
        axis.set_yticklabels(hour_ticks if index % 3 == 0 else [], rotation=0)

        set_bin_edge_ticks(axis, TEMPERATURE_BINS, first_edge_position=0)

        if index < 3:
            axis.set_xticklabels([])

    figure.supxlabel("평균 기온 / °C")
    figure.supylabel("시간대 / 시")

    mappable = axes.flat[0].collections[0]
    figure.colorbar(mappable, ax=axes, shrink=0.85,
                    label=f"한 시간대의 평균 {target_column[:2]} 수 / 건")


    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")

    for suffix, target_column in TARGET_COLUMNS.items():
        figure = plot(base_table, target_column)
        save_figure(
            figure,
            BASE_OUTPUT_PATH / f"figure9_hour_temp_heatmap_{suffix}.svg",
            should_close=True)

if __name__ == "__main__":
    main()
