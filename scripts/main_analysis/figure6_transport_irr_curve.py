import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import statsmodels.api as sm
import statsmodels.formula.api as smf
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
    target_column = "이송수"
    df = base_table.dropna(subset=target_column)

    # 1. 기온과 소방서 간 상호작용(*)을 반영한 모형 적합
    model_inter = smf.glm(
        formula=f"{target_column} ~ bs(평균기온, df=3) * C(소방서) + C(시간대)",
        data=df,
        family=sm.families.Poisson()
    ).fit()

    # 2. 소방서별 IRR 곡선 추정
    temp_grid = np.linspace(df["평균기온"].min(), df["평균기온"].max(), 200)
    stations = list(AREA_FIRE_STATION_NAME_MAP.keys())
    ref_temp = 14.0
    ref_idx = (np.abs(temp_grid - ref_temp)).argmin()

    figure, axis = plt.subplots(figsize=(9, 6))

    for st in stations:
        pred_df = pd.DataFrame(
            {"평균기온": temp_grid, "소방서": st, "시간대": 14.0}
        )

        # get_prediction().summary_frame()을 통해 예측값과 95% 신뢰구간을 함께 가져옴
        pred_summary = model_inter.get_prediction(pred_df).summary_frame()

        # 기준 기온(14.0°C) 위치의 로그 예측값
        ref_log = np.log(pred_summary["mean"].iloc[ref_idx])

        # 로그 차이의 지수화를 통한 IRR 및 상/하한 신뢰구간 계산
        irr_st = np.exp(np.log(pred_summary["mean"]) - ref_log)
        irr_lower = np.exp(np.log(pred_summary["mean_ci_lower"]) - ref_log)
        irr_upper = np.exp(np.log(pred_summary["mean_ci_upper"]) - ref_log)

        # 추정선 매핑 및 선 색상 추출
        (line,) = axis.plot(temp_grid, irr_st, label=f"{st}", linewidth=2)

        # 동일한 색상으로 95% 신뢰구간 음영(fill_between) 추가
        axis.fill_between(
            temp_grid,
            irr_lower,
            irr_upper,
            color=line.get_color(),
            alpha=0.12,
        )

    axis.axhline(1.0, color='red', linestyle="--",
                 label=f"기준선 ({ref_temp}°C = 1.0)")
    axis.set_xlabel('평균 기온 / °C')
    axis.set_ylabel('이송 발생률비')
    axis.set_title('평균 기온별 이송 발생률비 (B-스플라인 포아송 회귀 기반)')
    axis.legend()
    axis.grid(True, alpha=0.3)

    figure.tight_layout()
    return figure

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    figure = plot(base_table)
    save_figure(figure,
                BASE_OUTPUT_PATH / "figure6_transport_irr_curve.svg",
                should_close=True)

if __name__ == "__main__":
    main()
