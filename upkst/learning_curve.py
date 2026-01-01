"""
学习曲线与掌握提升：式(2-1)(2-2)
"""
from __future__ import annotations
import math
import numpy as np


def delta_mastery(mastery: float, A: float, d: float, t: float, k: float) -> float:
    """
    式(2-1): Δm_{s,i}(t_i) = (1 - m_{s,i}) (1 - exp(-k * A_s / d_i * t_i))
    """
    mastery = float(np.clip(mastery, 0.0, 1.0))
    a = k * A / max(d, 1e-12)
    return (1.0 - mastery) * (1.0 - math.exp(-a * t))


def mastery_after(mastery: float, dm: float) -> float:
    """
    式(2-2): m' = min(1, m + Δm)
    """
    return min(1.0, mastery + dm)
