"""
蚁群构造路径：式(2-5)(2-6)
- C_r：满足先修约束的候选集合
- 转移概率 p_ij ∝ τ_ij^alpha * η_j^beta
"""
from __future__ import annotations
from typing import Dict, List, Set
import random
import numpy as np

from .types import KnowledgePoint, UPKSTParams


def feasible_candidates(points: Dict[int, KnowledgePoint], visited: Set[int]) -> List[int]:
    """式(2-5): C_r = { j ∈ (K\V_r) | Pre(j) ⊆ V_r }"""
    cand = []
    for kid, kp in points.items():
        if kid in visited:
            continue
        if all(pre in visited for pre in kp.prereqs):
            cand.append(kid)
    return cand


def roulette_choice(items: List[int], weights: List[float], rng: random.Random) -> int:
    s = sum(weights)
    if s <= 0:
        return rng.choice(items)
    r = rng.random() * s
    acc = 0.0
    for it, w in zip(items, weights):
        acc += w
        if acc >= r:
            return it
    return items[-1]


def construct_path(points: Dict[int, KnowledgePoint],
                   tau: np.ndarray,
                   idx: Dict[int, int],
                   eta: Dict[int, float],
                   params: UPKSTParams,
                   rng: random.Random) -> List[int]:
    """
    从 START 行开始构造一条完整拓扑序。
    tau[from_row, to_col], from_row: 0..n (n为START)，to_col: 0..n-1
    """
    n = len(points)
    start_row = n
    visited: Set[int] = set()
    path: List[int] = []
    current_row = start_row

    while len(path) < n:
        cand = feasible_candidates(points, visited)
        if not cand:
            raise ValueError("无可行候选：先修图可能有环，或数据缺失。")

        weights = []
        for j in cand:
            jcol = idx[j]
            weights.append((tau[current_row, jcol] ** params.alpha) * (eta[j] ** params.beta))

        nxt = roulette_choice(cand, weights, rng)
        path.append(nxt)
        visited.add(nxt)
        current_row = idx[nxt]

    return path
