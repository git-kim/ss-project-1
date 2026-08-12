from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    STATIONS,
    add_year_column
    )

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import koreanize_matplotlib

from project_modules.plot_style import (
    apply_plot_style,
    get_station_style,
    REFERENCE_COLOR
    )

from data_modules.data_io import (
    save_figure,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

TARGET_COLUMNS = ["출동수", "이송수"]


def plot(base_table: pd.DataFrame) -> Figure:
    """
    Note: Close the figure after use.
    """
    if base_table.empty:
        return None

    df = add_year_column(base_table)

    yearly_temperature = df.groupby("연도")["평균기온"].mean()

    # 평균 기온은 연월, 시간대별 평균 기온을 그 해의 전 시간대와 6개 소방서에
    # 걸쳐 다시 평균한 값이다. 원자료의 단순 연평균이 아니다.

    apply_plot_style()

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharex=True)

    for axis, target_column in zip(axes, TARGET_COLUMNS):
        station_totals = (
            df
            .pivot_table(index="연도", columns="소방서", values=target_column,
                         aggfunc="sum")
            )

        for station in STATIONS:
            style = get_station_style(station)

            axis.plot(station_totals.index, station_totals[station],
                      label=station, color=style["color"],
                      marker=style["marker"], linestyle=style["linestyle"],
                      linewidth=2.2, markersize=7)

        axis.set_xlabel("연도")
        axis.set_title(f"연간 총 {target_column[:2]} 수")
        axis.set_ylim(bottom=0)
        axis.grid(True, alpha=0.3)

        temperature_axis = axis.twinx()
        temperature_axis.plot(yearly_temperature.index, yearly_temperature,
                              color=REFERENCE_COLOR, linestyle="--",
                              linewidth=1.8, marker="s", markersize=4,
                              label="평균 기온")

        # fixed range so the nearly flat yearly temperature is not read as a
        # large swing next to the count lines
        temperature_axis.set_ylim(0, 30)
        temperature_axis.grid(False)

        if axis is axes[-1]:
            temperature_axis.set_ylabel("평균 기온 / °C")

    axes[0].set_ylabel("연간 총 건수")

    handles, labels = axes[0].get_legend_handles_labels()
    temperature_handles, temperature_labels = \
        temperature_axis.get_legend_handles_labels()

    legend = figure.legend(handles + temperature_handles,
                           labels + temperature_labels,
                           loc="lower center", ncol=7, frameon=False,
                           bbox_to_anchor=(0.5, -0.06))

    figure.suptitle("소방서별 연간 총 건수와 연평균 기온")

    figure.tight_layout()

    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    figure = plot(base_table)
    save_figure(figure,
                       BASE_OUTPUT_PATH / "figure10_yearly_trend.svg",
                       should_close=True)

if __name__ == "__main__":
    main()
