from project_modules.common import PROJECT_DIRECTORY_PATH

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import koreanize_matplotlib

from project_modules.plot_style import (
    apply_plot_style
    )

from data_modules.data_io import (
    save_figure,
    read_data_file_into_dataframe
    )

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

MISSING_RATE_LIMIT = 0.2

DISPATCH_COLOR = "#9A3324"
TRANSPORT_COLOR = "#2E7D5B"
TEMPERATURE_COLOR = "#1F4E79"

def point_at_axis(axis, color: str, tail, head_x) -> None:
    """
    Draws an arrow from a point on a curve towards the axis it should be read
    against.

    tail: (x, y) of a real data point, in data coordinates.
    head_x: x the arrow points at, level with the tail.
    """
    axis.annotate("", xy=(head_x, tail[1]), xytext=tail,
                  xycoords="data", textcoords="data",
                  arrowprops={"arrowstyle": "->", "color": color,
                              "linewidth": 1.8, "shrinkA": 2, "shrinkB": 0})

def plot(base_table: pd.DataFrame) -> Figure:
    """
    Note: Close the figure after use.
    """
    if base_table.empty:
        return None

    df = base_table.copy()
    df["일시"] = pd.to_datetime(df["연월"], format="%Y%m")

    monthly = (
        df
        .groupby("일시", as_index=False)
        .agg(총출동수=("출동수", "sum"),
             총이송수=("이송수", "sum"),
             이송수결측률=("이송수", lambda counts: counts.isna().mean()),
             평균기온=("평균기온", "mean"))
        )

    monthly.loc[monthly["이송수결측률"] > MISSING_RATE_LIMIT, "총이송수"] = None

    apply_plot_style()

    figure, axis = plt.subplots(figsize=(11.5, 5))

    axis.plot(monthly["일시"], monthly["총출동수"],
              color=DISPATCH_COLOR, linewidth=1.8, label="월간 총 출동 수")
    axis.plot(monthly["일시"], monthly["총이송수"],
              color=TRANSPORT_COLOR, linewidth=1.5, linestyle="--",
              label="월간 총 이송 수")
    axis.set_xlabel("연도")
    axis.set_ylabel("6개 소방서 월간 총 건수")
    axis.set_ylim(bottom=0)

    first, last = monthly["일시"].iloc[0], monthly["일시"].iloc[-1]
    axis.set_xlim(first - pd.DateOffset(months=11),
                  last + pd.DateOffset(months=11))

    axis.grid(True, alpha=0.3)

    temperature_axis = axis.twinx()
    temperature_axis.plot(monthly["일시"], monthly["평균기온"],
                          color=TEMPERATURE_COLOR, linewidth=1.4, alpha=0.65,
                          label="평균 기온")
    temperature_axis.set_ylabel("평균 기온 / °C")

    temperature_axis.grid(False)

    point_at_axis(axis, DISPATCH_COLOR,
                  (first, monthly["총출동수"].iloc[0]),
                  first - pd.DateOffset(months=10))
    point_at_axis(axis, TRANSPORT_COLOR,
                  (first, monthly["총이송수"].iloc[0]),
                  first - pd.DateOffset(months=10))
    point_at_axis(temperature_axis, TEMPERATURE_COLOR,
                  (last, monthly["평균기온"].iloc[-1]),
                  last + pd.DateOffset(months=10))

    handles, labels = axis.get_legend_handles_labels()
    temperature_handles, temperature_labels = \
        temperature_axis.get_legend_handles_labels()

    temperature_axis.legend(
        handles + temperature_handles, labels + temperature_labels,
        loc="lower left", bbox_to_anchor=(0, 1.01), ncol=3, frameon=False)

    figure.tight_layout()

    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    figure = plot(base_table)
    save_figure(figure,
                       BASE_OUTPUT_PATH / "figure11_monthly_series.svg",
                       should_close=True)

if __name__ == "__main__":
    main()
