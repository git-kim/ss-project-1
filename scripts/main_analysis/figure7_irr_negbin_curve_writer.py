from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    MODEL_FORMULA,
    REFERENCE_HOUR,
    REFERENCE_TEMPERATURE,
    REFERENCE_YEAR,
    add_year_column
    )

from data_modules.count_model import (
    fit_negative_binomial,
    get_irr_with_ci
    )

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
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

GRID_SIZE = 80
AXIS_TEMPERATURE_RANGE = (-10, 35)

ERROR_BAR_TEMPERATURES = [-5, 0, 5, 10, 15, 20, 25, 30]
ERROR_BAR_OFFSETS = (-0.6, 0.0, 0.6) # to prevent error bars from overlapping

PANELS = {
    "서울 3개소": ["강남소방서", "강동소방서", "노원소방서"],
    "대구 · 부산 · 강원": ["수성소방서", "해운대소방서", "원주소방서"]
}

TARGET_COLUMNS = {"dispatch": "출동수", "transport": "이송수"}

def plot(base_table: pd.DataFrame, target_column: str) -> Figure:
    """
    Note: Close the figure after use.
    """
    if base_table.empty:
        return None

    df_clean = add_year_column(base_table.dropna(subset=target_column))

    formula = MODEL_FORMULA.format(target=target_column)
    result, _ = fit_negative_binomial(formula, df_clean)

    observed_range = df_clean.groupby("소방서")["평균기온"].agg(["min", "max"])

    apply_plot_style()

    figure, axes_array = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True)

    for axes, (panel_title, panel_stations) in zip(axes_array, PANELS.items()):
        axes: Axes
        for station, offset in zip(panel_stations, ERROR_BAR_OFFSETS):
            minimum, maximum = observed_range.loc[station]

            temp_grid = np.linspace(minimum, maximum, GRID_SIZE)

            covariates = {
                "소방서": station,
                "시간대": REFERENCE_HOUR,
                "연도": REFERENCE_YEAR,
                }

            irr, lower, upper = get_irr_with_ci(
                result, covariates, temp_grid, REFERENCE_TEMPERATURE)

            style = get_station_style(station)

            axes.plot(temp_grid, irr, label=station, color=style["color"],
                      linestyle=style["linestyle"], linewidth=2.4)

            bar_temperatures = np.array(
                [temperature for temperature in ERROR_BAR_TEMPERATURES
                 if minimum <= temperature <= maximum])

            if bar_temperatures.size:
                bar_irr, bar_lower, bar_upper = get_irr_with_ci(
                    result, covariates, bar_temperatures,
                    REFERENCE_TEMPERATURE)

                axes.errorbar(
                    bar_temperatures + offset, bar_irr,
                    yerr=[bar_irr - bar_lower, bar_upper - bar_irr],
                    fmt=style["marker"], markersize=5, color=style["color"],
                    linestyle="none", capsize=3, elinewidth=1.4)

        axes.axhline(1.0, color=REFERENCE_COLOR, linestyle="--",
                     label=f"기준선 ({REFERENCE_TEMPERATURE}°C = 1.0)")
        axes.set_title(panel_title)
        axes.set_xlabel("평균 기온 / °C")

        axes.set_xlim(*AXIS_TEMPERATURE_RANGE)
        axes.set_xticks(range(AXIS_TEMPERATURE_RANGE[0],
                              AXIS_TEMPERATURE_RANGE[1] + 1, 5))

        handles, labels = axes.get_legend_handles_labels()
        interval_handle = Line2D([], [], color=REFERENCE_COLOR, marker="|",
                                 linestyle="none", markersize=11,
                                 markeredgewidth=1.6)

        axes.legend([*handles, interval_handle],
                    [*labels, "세로 막대 = 95% 신뢰 구간"],
                    loc="upper left", fontsize=13)

        axes.grid(True, alpha=0.3)

    metric_name = target_column[:2]

    axes[0].set_ylabel(f"{metric_name} 발생률비")

    figure.suptitle(
        f"평균 기온별 {metric_name} 발생률비 (음이항 회귀, 시간대 · 연도 통제)")

    figure.tight_layout()
    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")

    for suffix, target_column in TARGET_COLUMNS.items():
        figure = plot(base_table, target_column)
        save_figure(
            figure,
            BASE_OUTPUT_PATH / f"figure7_irr_negbin_curve_{suffix}.svg",
            should_close=True)

if __name__ == "__main__":
    main()
