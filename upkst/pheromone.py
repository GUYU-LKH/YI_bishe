"""
信息素更新：式(2-15)~(2-18)
- 挥发：τ ← (1-ρ) τ
- 增量：Δτ_ij = Q * g_i / (Σ g + eps)  (i,j)∈P
- 更新：τ ← τ + Δτ
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np

from .types import KnowledgePoint, UPKSTParams


def update_pheromone(points: Dict[int, KnowledgePoint],
                     tau: np.ndarray,
                     idx: Dict[int, int],
                     solutions: List[Tuple[List[int], Dict[int, float], float, float, Dict[int, float]]],
                     params: UPKSTParams) -> None:
    # 式(2-15)
    tau *= (1.0 - params.rho)

    delta = np.zeros_like(tau)
    for path, t_map, L, Q, g_map in solutions:
        sum_g = sum(g_map.values()) + params.eps
        for i, j in zip(path[:-1], path[1:]):
            delta[idx[i], idx[j]] += Q * g_map.get(i, 0.0) / sum_g

    # 式(2-18)
    tau += delta
    np.clip(tau, params.tau_min, params.tau_max, out=tau)
