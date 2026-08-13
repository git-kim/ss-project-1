from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    TEMPERATURE_BINS,
    TEMPERATURE_LABELS
    )

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import koreanize_matplotlib

from project_modules.plot_style import (
    apply_plot_style,
    REFERENCE_COLOR,
    set_bin_edge_ticks
    )

from data_modules.data_io import (
    save_figure,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

REFERENCE_LABEL = "10 ~ 15"

# Decades are merged into bands, but 9세 이하 and 미상 are both left out.
# 9세 이하 is 1,977 records in 2020, 14 in 2021
# (five of the six stations report none all year), then 41,158 in 2022.
#
# 10대 is kept out of the 20~39세 band.
# Merging it there is what the decade figures say not to do.
AGE_BAND_MAP = {
    "10대": "10대",
    "20대": "20~39세",
    "30대": "20~39세",
    "40대": "40~59세",
    "50대": "40~59세",
    "60대": "60~79세",
    "70대": "60~79세",
    "80세 이상": "80세 이상",
}

AGE_BAND_STYLES = {
    "10대": ("#2E6F8E", "o", 2.6, "--"),
    "20~39세": ("#E8B48D", "s", 2.2, "-"),
    "40~59세": ("#D08A52", "^", 2.4, "-"),
    "60~79세": ("#A85A2B", "D", 2.8, "-"),
    "80세 이상": ("#7A2418", "P", 3.2, "-"),
}

def plot(age_group_table: pd.DataFrame) -> Figure:
    """
    Note: Close the figure after use.
    """
    if age_group_table.empty:
        return None

    df = age_group_table[age_group_table["연령대"].isin(AGE_BAND_MAP)].copy()
    df["연령대"] = df["연령대"].map(AGE_BAND_MAP)

    apply_plot_style()

    metrics = ["출동수", "이송수"]

    figure, axes_array = plt.subplots(1, 2, figsize=(13, 5.8), sharey=True)

    for axes, metric in zip(axes_array, metrics):
        axes: Axes
        metric_rows = df[df["지표"] == metric]

        cells = (
            metric_rows
            .drop_duplicates(["소방서", "기온구간"])
            .groupby("기온구간", observed=True)["관측N"]
            .sum()
            )

        counts = (
            metric_rows
            .groupby(["기온구간", "연령대"], observed=True)["건수"]
            .sum()
            .unstack("연령대")
            )

        rates = counts.div(cells, axis=0)
        rates = rates.reindex(TEMPERATURE_LABELS).dropna(how="all")
        rates = rates[list(AGE_BAND_STYLES)]

        relative = rates / rates.loc[REFERENCE_LABEL]

        for age_group, (color, marker, width, style) in AGE_BAND_STYLES.items():
            axes.plot(relative.index, relative[age_group], label=age_group,
                      color=color, marker=marker, markersize=6,
                      linewidth=width, linestyle=style)

        axes.axhline(1.0, color=REFERENCE_COLOR, linestyle=":", linewidth=1.4,
                     label=f"기준선 ({REFERENCE_LABEL}°C = 1.0)")
        axes.set_xlabel("평균 기온 / °C")

        axes.set_title(f"{metric[:2]} 수")
        set_bin_edge_ticks(axes, TEMPERATURE_BINS, first_edge_position=-0.5)
        axes.grid(True, alpha=0.3)

    axes[0].set_ylabel(f"상대 건수 ({REFERENCE_LABEL}°C 구간 = 1.0)")

    legend = axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left",
                            frameon=True)
    legend.get_frame().set_edgecolor("black")
    legend.get_frame().set_linewidth(1.0)

    figure.suptitle("연령대별 기온 구간에 따른 상대 건수 (6개 소방서 합계)")

    figure.tight_layout()

    return figure

def main() -> None:
    age_group_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "table9_age_group_by_temp.csv", encoding="utf-8")
    figure = plot(age_group_table)
    save_figure(figure,
                       BASE_OUTPUT_PATH / "figure8_age_group_by_temp.svg",
                       should_close=True)

if __name__ == "__main__":
    main()
