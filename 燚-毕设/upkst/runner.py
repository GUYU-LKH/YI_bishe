# -*- coding: utf-8 -*-
"""
UPKST 主流程：
- ACO 构造路径 P
- KKT 求 t
- 计算 U/L/Q
- 信息素更新
"""
from __future__ import annotations
from typing import Dict
import random
import numpy as np

from .types import KnowledgePoint, StudentState, UPKSTParams, Solution
from .heuristics import build_eta
from .aco import construct_path
from .kkt_time import allocate_time_kkt
from .objective import utility, loss, quality_from_loss, contribution
from .pheromone import update_pheromone


def run_upkst(points: Dict[int, KnowledgePoint], student: StudentState, params: UPKSTParams) -> Solution:
    rng = random.Random(params.seed)

    kids = sorted(points.keys())
    idx = {kid: i for i, kid in enumerate(kids)}
    n = len(kids)

    # tau[from_row, to_col], from_row in [0..n] (n 是 START), to_col in [0..n-1]
    tau = np.full((n + 1, n), params.tau0, dtype=float)

    eta = build_eta(points, params.eps)

    best = None

    for it in range(1, params.n_iters + 1):
        sols_for_update = []

        for _ in range(params.n_ants):
            P = construct_path(points, tau, idx, eta, params, rng)
            t_map, lam = allocate_time_kkt(points, P, student, params)

            U = utility(points, P, t_map, student, params.k)
            L = loss(points, P, t_map, student, params.k, params.beta_jump)
            Q = quality_from_loss(L, params.eps)
            g_map = {i: contribution(points, i, t_map[i], student, params.k) for i in P}

            sols_for_update.append((P, t_map, L, Q, g_map))

            cand = Solution(path=P, t_map=t_map, U=U, L=L, Q=Q, lam=lam)
            if best is None or cand.L < best.L:
                best = cand

        update_pheromone(points, tau, idx, sols_for_update, params)

        if it % max(1, params.n_iters // 10) == 0 and best is not None:
            print(f"[Iter {it:>3}/{params.n_iters}] best L={best.L:.6f}  U={best.U:.6f}  Q={best.Q:.6f}  lambda={best.lam:.6g}")

    assert best is not None
    return best
