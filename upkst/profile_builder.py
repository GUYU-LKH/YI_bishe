"""
从“学生×知识点成绩”构建：知识点掌握度 m_{s,i} 与整体学习能力 A_s。


默认输入格式（长表 raw_long）：
  student_id, exam_id, exam_date, exam_weight, kp_name, score, full_score, score_rate
"""
from __future__ import annotations
from typing import Tuple, Dict, Optional
import numpy as np
import pandas as pd
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileParams:
    gamma: float = 1.2          # sigmoid 拉伸系数 γ
    decay_lambda: float = 0.003 # 时间衰减 λ（按“天”计）: w = exp(-λ * Δdays)
    kappa: float = 0.3          # 能力映射尺度 κ：A_s = exp(κ * z_s)
    fill_mastery: float = 0.5   # 缺失知识点掌握度的回填值
    eps: float = 1e-9


def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -40, 40)  # 防止溢出
    return 1.0 / (1.0 + np.exp(-x))


def load_long_table(path: str, sheet: str = "raw_long") -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    else:
        df = pd.read_csv(path, encoding="utf-8-sig")
    return df


def compute_time_weight(exam_date: pd.Series, exam_weight: pd.Series, decay_lambda: float) -> np.ndarray:
    """
    w_e = exam_weight * exp(-lambda * Δdays)
    其中“当前时点”默认取数据中的最新 exam_date。
    """
    dates = pd.to_datetime(exam_date)
    now = dates.max()
    delta_days = (now - dates).dt.days.astype(float)
    return exam_weight.to_numpy(dtype=float) * np.exp(-decay_lambda * delta_days)


def build_mastery(df_long: pd.DataFrame, params: ProfileParams) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    输出：
      mastery_long: [student_id, kp_name, mastery]
      debug_exam_kp_stats: [exam_id, kp_name, mean, std, n]
    """
    df = df_long.copy()
    if "score_rate" not in df.columns:
        if "score" in df.columns and "full_score" in df.columns:
            df["score_rate"] = df["score"] / df["full_score"]
        else:
            raise ValueError("需要 score_rate 或 (score, full_score) 列")

    # 计算时间权重
    df["time_w"] = compute_time_weight(df["exam_date"], df["exam_weight"], params.decay_lambda)

    # 考试内、知识点内标准化
    grp = df.groupby(["exam_id", "kp_name"])
    stats = grp["score_rate"].agg(["mean", "std", "count"]).reset_index()
    stats["std"] = stats["std"].fillna(0.0)
    stats["std"] = stats["std"].where(stats["std"] > 1e-6, 1e-6)

    df = df.merge(stats, on=["exam_id", "kp_name"], how="left")
    z = (df["score_rate"] - df["mean"]) / (df["std"] + params.eps)
    df["m_hat"] = _sigmoid(params.gamma * z.to_numpy())

    # 聚合到 m_{s,i}
    # m_{s,i} = Σ w * m_hat / Σ w
    agg = df.groupby(["student_id", "kp_name"]).apply(
        lambda g: pd.Series({
            "mastery": float(np.sum(g["time_w"] * g["m_hat"]) / (np.sum(g["time_w"]) + params.eps)),
            "n_obs": int(len(g)),
        })
    ).reset_index()

    mastery_long = agg[["student_id", "kp_name", "mastery", "n_obs"]].copy()

    debug_stats = stats.rename(columns={"count": "n"})
    return mastery_long, debug_stats


def build_ability(df_long: pd.DataFrame, params: ProfileParams) -> pd.DataFrame:
    """
    用“每次考试的总体表现”构建 A_s。
    1) 对每个 (student, exam) 聚合一个 overall_rate（平均得分率）
    2) 在每次考试内对 overall_rate 做 z 标准化（跨卷可比）
    3) 时间衰减加权得到 z_s
    4) A_s = exp(kappa * z_s)
    """
    df = df_long.copy()
    if "score_rate" not in df.columns:
        if "score" in df.columns and "full_score" in df.columns:
            df["score_rate"] = df["score"] / df["full_score"]
        else:
            raise ValueError("需要 score_rate 或 (score, full_score) 列")

    # 考试内总体表现
    overall = df.groupby(["student_id", "exam_id", "exam_date", "exam_weight"])["score_rate"].mean().reset_index()
    overall = overall.rename(columns={"score_rate": "overall_rate"})
    overall["time_w"] = compute_time_weight(overall["exam_date"], overall["exam_weight"], params.decay_lambda)

    # 考试内标准化
    st = overall.groupby("exam_id")["overall_rate"].agg(["mean", "std"]).reset_index()
    st["std"] = st["std"].fillna(0.0)
    st["std"] = st["std"].where(st["std"] > 1e-6, 1e-6)
    overall = overall.merge(st, on="exam_id", how="left")
    overall["z"] = (overall["overall_rate"] - overall["mean"]) / (overall["std"] + params.eps)

    # 时间加权聚合
    zs = overall.groupby("student_id").apply(
        lambda g: float(np.sum(g["time_w"] * g["z"]) / (np.sum(g["time_w"]) + params.eps))
    ).reset_index(name="z_s")

    zs["A_s"] = np.exp(params.kappa * zs["z_s"].to_numpy(dtype=float))
    return zs[["student_id", "z_s", "A_s"]]
