# -*- coding: utf-8 -*-
"""
objective.py

定义：
- 效用 U(P,t;s)
- 损失 L(P,t;s) = -U + β * 难度跃迁惩罚
- 质量 Q(L) 用于信息素增量（蚁群算法）

你已确认：没有时间惩罚项，因此 L 只包含 -U 与难度跃迁惩罚。

重要：由于 L = -U + penalty 可能为负数，
若使用 Q = 1/(max(L,0)+eps) 会在 L<0 时导致 Q≈1/eps 恒大（如 1e9），信息素更新失真。
因此采用稳定单调映射：
    Q = max(0, -L) + eps
"""

from __future__ import annotations

from typing import Dict, List

from .types import KnowledgePoint, StudentState
from .learning_curve import delta_mastery


def utility(
    points: Dict[int, KnowledgePoint],
    path: List[int],
    t_map: Dict[int, float],
    student: StudentState,
    k: float,
) -> float:
    """式(2-3): U(P,t;s) = Σ w_i * Δm_i(t_i)"""
    s = 0.0
    for i in path:
        p = points[i]
        s += float(p.w) * delta_mastery(float(p.mastery), float(student.A), float(p.d), float(t_map[i]), k)
    return s


def difficulty_jump_penalty(points: Dict[int, KnowledgePoint], path: List[int]) -> float:
    """式(2-4): Σ max(0, d_{p_{j+1}} - d_{p_j})"""
    jump = 0.0
    for a, b in zip(path[:-1], path[1:]):
        jump += max(0.0, float(points[b].d) - float(points[a].d))
    return jump


def loss(
    points: Dict[int, KnowledgePoint],
    path: List[int],
    t_map: Dict[int, float],
    student: StudentState,
    k: float,
    beta_jump: float,
) -> float:
    """
    式(2-4): L(P,t;s) = -U(P,t;s) + beta_jump * Σ max(0, d_next - d_curr)
    """
    U = utility(points, path, t_map, student, k)
    return -U + float(beta_jump) * difficulty_jump_penalty(points, path)


def quality_from_loss(L: float, eps: float) -> float:
    """
    信息素质量（用于增量 Δτ）：
      Q = max(0, -L) + eps
    L 越小（越负）代表解越好，因此 -L 越大，Q 越大；L>=0 时 Q≈eps（很小但不为0）。
    """
    return max(0.0, -float(L)) + float(eps)


def contribution(
    points: Dict[int, KnowledgePoint],
    i: int,
    t_i: float,
    student: StudentState,
    k: float,
) -> float:
    """式(2-16): g_i = w_i * Δm_i(t_i)"""
    p = points[i]
    return float(p.w) * delta_mastery(float(p.mastery), float(student.A), float(p.d), float(t_i), k)
