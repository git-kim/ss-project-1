from project_modules.common import PROJECT_DIRECTORY_PATH

from project_modules.analysis_common import (
    TEMPERATURE_BINS,
    TEMPERATURE_LABELS
    )

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

REFERENCE_LABEL = "10 ~ 15"

# nine lines were unreadable, so decades are merged into bands; age is
# ordinal, so the bands take one hue that darkens with age.
#
# 9세 이하 and 미상 are both left out. The source data reclassified one into
# the other partway through: 9세 이하 is 1,977 records in 2020, 14 in 2021
# (five of the six stations report none all year), then 41,158 in 2022. Pooled
# over years that inversion flips the sign of the curve — 30~35℃ comes out at
# -37.7% against +44% when each year is computed on its own — so the line
# would point the wrong way rather than merely being noisy.
# 10대 is kept out of the 20~39세 band. Merging it there is what the decade
# figures say not to do: at 30~35℃ 10대 is +79% against +25/+23 for 20·30대,
# so the band average (+34%) hid the single steepest group. Every other merge
# holds up — 60대 +40 with 70대 +44, 40대 +26 with 50대 +35.
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

# the four adult bands keep one hue darkening with age. 10대 sits at the young
# end but behaves like the old end, so it gets a hue of its own rather than
# the lightest step of a ramp it does not belong to
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

    # 평균 기온은 관측소의 시간별 기온을 연월, 시간대, 지역별로 평균한 값이다.
    # 따라서 하루 단위 폭염이나 한파는 이 값에 남지 않는다.

    apply_plot_style()

    metrics = ["출동수", "이송수"]

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.8), sharey=True)

    for axis, metric in zip(axes, metrics):
        metric_rows = df[df["지표"] == metric]

        # 관측N is repeated on every age row of a station-range group, so
        # summing it straight would count a station's cells once per decade
        # folded into the band (three times over for 10~39세). Take each
        # station's value once; the denominator never depended on age anyway.
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

        # pooled over stations: total events divided by total observed
        # (연월, 시간대, 지역) combinations. which stations reach a given range
        # differs by range, so the ends of the axis carry some station-mix
        # difference alongside the temperature effect
        rates = counts.div(cells, axis=0)
        rates = rates.reindex(TEMPERATURE_LABELS).dropna(how="all")
        rates = rates[list(AGE_BAND_STYLES)]

        # each age band is scaled by its own mild-weather level, so the lines
        # compare shapes rather than volumes
        relative = rates / rates.loc[REFERENCE_LABEL]

        for age_group, (color, marker, width, style) in AGE_BAND_STYLES.items():
            axis.plot(relative.index, relative[age_group], label=age_group,
                      color=color, marker=marker, markersize=6,
                      linewidth=width, linestyle=style)

        axis.axhline(1.0, color=REFERENCE_COLOR, linestyle=":", linewidth=1.4,
                     label=f"기준선 ({REFERENCE_LABEL}°C = 1.0)")
        axis.set_xlabel("평균 기온 / °C")

        # 지표 is a column value ("출동수"), which is not how it is spelled in
        # running text
        axis.set_title(f"{metric[:2]} 수")
        set_bin_edge_ticks(axis, TEMPERATURE_BINS, first_edge_position=-0.5)
        axis.grid(True, alpha=0.3)

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
