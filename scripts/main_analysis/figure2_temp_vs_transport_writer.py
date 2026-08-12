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

    # 평균 기온은 관측소의 시간별 기온을 연월, 시간대, 지역별로 평균한 값이다.
    # 따라서 하루 단위 폭염이나 한파는 이 값에 남지 않는다.

    apply_plot_style()

    figure, axis = plt.subplots(figsize=(11, 7))

    stations = list(AREA_FIRE_STATION_NAME_MAP.keys())

    legend_handles = []

    for station in stations:
        style = get_station_style(station)
        color = style["color"]
        station_data = (
            base_table[base_table["소방서"] == station][["평균기온", "이송수"]]
            .dropna()
            )

        sns.scatterplot(
            data=station_data,
            x="평균기온",
            y="이송수",
            color=color,
            marker=style["marker"],
            alpha=0.3,
            s=26,
            ax=axis
        )

        sns.regplot(
            data=station_data,
            x="평균기온",
            y="이송수",
            scatter=False,
            color=color,
            line_kws={"linewidth": 2.4, "linestyle": style["linestyle"]},
            ax=axis
        )

        x = station_data["평균기온"]
        y = station_data["이송수"]

        correlation = x.corr(y)

        if pd.notna(correlation):
            r_squared = correlation ** 2

            slope, intercept = np.polyfit(x, y, 1)

            x_position = x.quantile(0.75)
            y_position = slope * x_position + intercept

            axis.text(
                x_position,
                y_position,
                f"R² = {r_squared:.3f}",
                color="black",
                fontsize=12,
                fontweight="bold",
                ha="left",
                va="bottom"
            )

        legend_handles.extend([
            Line2D(
                [0],
                [0],
                marker=style["marker"],
                linestyle="None",
                markerfacecolor=color,
                markeredgecolor=color,
                markersize=7,
                alpha=0.6,
                label=f"{station}"
            ),
            Line2D(
                [0],
                [0],
                color=color,
                linewidth=2.4,
                linestyle=style["linestyle"],
                label=f"{station} 회귀선"
            )
        ])

    axis.set_title("평균 기온과 이송 수의 관계")
    axis.set_xlabel("평균 기온 / ℃")
    axis.set_ylabel("이송 수")
    axis.set_xlim(left=-10,right=35)
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
        handles=legend_handles,
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
                BASE_OUTPUT_PATH / "figure2_temp_vs_transport.svg",
                should_close=True)

if __name__ == "__main__":
    main()
