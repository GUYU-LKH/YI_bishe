# -*- coding: utf-8 -*-
"""
启发信息 η 的构造：式(2-7)
η_j = w_j (1-m_{s,j}) / (t_base,j * d_j)
"""
from __future__ import annotations
from typing import Dict
from .types import KnowledgePoint


def build_eta(points: Dict[int, KnowledgePoint], eps: float) -> Dict[int, float]:
    eta: Dict[int, float] = {}
    for kid, p in points.items():
        denom = p.t_base * p.d
        denom = denom if denom > eps else eps
        eta[kid] = (p.w * (1.0 - p.mastery)) / denom
    return eta
