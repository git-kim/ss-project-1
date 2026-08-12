from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    MODEL_FORMULA,
    REFERENCE_HOUR,
    REFERENCE_TEMPERATURE,
    REFERENCE_YEAR,
    STATIONS,
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

    # 평균 기온은 관측소의 시간별 기온을 연월, 시간대, 지역별로 평균한 값이다.
    # 따라서 하루 단위 폭염이나 한파는 이 값에 남지 않는다.

    apply_plot_style()

    figure, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True)

    # split so the confidence bands stop overlapping each other
    for axis, (panel_title, panel_stations) in zip(axes, PANELS.items()):
        for station in panel_stations:
            minimum, maximum = observed_range.loc[station]

            # each station is drawn only over the temperatures it actually saw
            temp_grid = np.linspace(minimum, maximum, GRID_SIZE)

            covariates = {
                "소방서": station,
                "시간대": REFERENCE_HOUR,
                "연도": REFERENCE_YEAR,
                }

            irr, lower, upper = get_irr_with_ci(
                result, covariates, temp_grid, REFERENCE_TEMPERATURE)

            style = get_station_style(station)

            axis.plot(temp_grid, irr, label=station, color=style["color"],
                      linestyle=style["linestyle"], linewidth=2.4)

            axis.fill_between(temp_grid, lower, upper, color=style["color"],
                              alpha=0.15)

        axis.axhline(1.0, color=REFERENCE_COLOR, linestyle="--",
                     label=f"기준선 ({REFERENCE_TEMPERATURE}°C = 1.0)")
        axis.set_title(panel_title)
        axis.set_xlabel("평균 기온 / °C")

        # same ticks on both panels so they can be compared at a glance
        axis.set_xlim(*AXIS_TEMPERATURE_RANGE)
        axis.set_xticks(range(AXIS_TEMPERATURE_RANGE[0],
                              AXIS_TEMPERATURE_RANGE[1] + 1, 5))
        axis.legend(loc="upper left")
        axis.grid(True, alpha=0.3)

    metric_name = target_column[:2]

    axes[0].set_ylabel(f"{metric_name} 발생률비")

    figure.suptitle(f"평균 기온별 {metric_name} 발생률비 (음이항 회귀, 연도 통제)")

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
