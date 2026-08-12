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
    save_dataframe_as_csv,
    read_data_file_into_dataframe
    )

from project_modules.common import PROJECT_DIRECTORY_PATH

BASE_INPUT_PATH = PROJECT_DIRECTORY_PATH / "data/processed"
BASE_OUTPUT_PATH = PROJECT_DIRECTORY_PATH / "outputs/main"

def get_irr_summary_table(base_table: pd.DataFrame,
                          target_temps: list[float] | None = None,
                          ref_temp: float = 14.0) -> pd.DataFrame:
    if base_table.empty:
        return pd.DataFrame()

    if target_temps is None:
        target_temps = [-5.0, 0.0, 18.0, 25.0, 30.0, 33.0]

    df_clean = base_table.dropna(subset=["이송수", "출동수"]).copy()

    # 1. 포아송 회귀 모형 적합 (이송수 및 출동수)
    model_transfer = smf.glm(
        formula="이송수 ~ bs(평균기온, df=3) * C(소방서) + C(시간대)",
        data=df_clean,
        family=sm.families.Poisson(),
    ).fit()

    model_dispatch = smf.glm(
        formula="출동수 ~ bs(평균기온, df=3) * C(소방서) + C(시간대)",
        data=df_clean,
        family=sm.families.Poisson(),
    ).fit()

    # 2. 기준 기온(ref_temp) 포함 예측용 데이터프레임 생성
    eval_temps = list(dict.fromkeys(list(target_temps) + [ref_temp]))
    eval_df = pd.DataFrame(
        {
            "평균기온": eval_temps,
            "소방서": df_clean["소방서"].mode()[0],  # 최빈값 소방서 기준
            "시간대": 14.0,  # 대표 시간대
        }
    )

    # 3. 예측값 및 95% 신뢰구간 산출
    pred_t = model_transfer.get_prediction(eval_df).summary_frame()
    pred_d = model_dispatch.get_prediction(eval_df).summary_frame()

    # 4. 기준 기온 인덱스 추출
    ref_idx = eval_temps.index(ref_temp)

    # [이송수] 상대 발생률비(IRR) 및 CI 계산
    ref_log_t = np.log(pred_t["mean"].iloc[ref_idx])
    irr_t = np.exp(np.log(pred_t["mean"]) - ref_log_t)
    irr_lower_t = np.exp(np.log(pred_t["mean_ci_lower"]) - ref_log_t)
    irr_upper_t = np.exp(np.log(pred_t["mean_ci_upper"]) - ref_log_t)

    # [출동수] 상대 발생률비(IRR) 및 CI 계산
    ref_log_d = np.log(pred_d["mean"].iloc[ref_idx])
    irr_d = np.exp(np.log(pred_d["mean"]) - ref_log_d)
    irr_lower_d = np.exp(np.log(pred_d["mean_ci_lower"]) - ref_log_d)
    irr_upper_d = np.exp(np.log(pred_d["mean_ci_upper"]) - ref_log_d)

    # 5. 지정된 열 구조에 맞춰 결과 생성
    rows = []
    for t in target_temps:
        idx = eval_temps.index(t)

        row = {
            "평균기온": t,
            "이송수 IRR (95% CI)": (
                f"{irr_t.iloc[idx]:.3f} ({irr_lower_t.iloc[idx]:.3f} -"
                f" {irr_upper_t.iloc[idx]:.3f})"
            ),
            "이송수 증감률": f"{(irr_t.iloc[idx] - 1) * 100:+.1f}%",
            "출동수 IRR (95% CI)": (
                f"{irr_d.iloc[idx]:.3f} ({irr_lower_d.iloc[idx]:.3f} -"
                f" {irr_upper_d.iloc[idx]:.3f})"
            ),
            "출동수 증감률": f"{(irr_d.iloc[idx] - 1) * 100:+.1f}%",
        }
        rows.append(row)

    return pd.DataFrame(rows)

def main() -> None:
    base_table = read_data_file_into_dataframe(
        BASE_INPUT_PATH / "base_table.csv", encoding="utf-8")
    summary_table = get_irr_summary_table(base_table)
    save_dataframe_as_csv(summary_table,
                          BASE_OUTPUT_PATH / "table6_irr_summary.csv",
                          encoding="utf-8")

if __name__ == "__main__":
    main()
