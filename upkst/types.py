from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class KnowledgePoint:
    """
    单个知识点 i 的属性（对单个学生 s）。
    - kid: 知识点ID（int）
    - name: 知识点名称（用于展示）
    - w: 重要度/权重 w_i（第3章表3-3可得）
    - d: 难度 d_i（第3章表3-3可得）
    - t_base: 完成一次有效复习的基准时间 t_base,i（可自定义规则映射）
    - mastery: 初始掌握度 m_{s,i} ∈ [0,1]
    - prereqs: 先修集合 Pre(i)，必须构成DAG
    """
    kid: int
    name: str
    w: float
    d: float
    t_base: float
    mastery: float
    prereqs: Tuple[int, ...]


@dataclass(frozen=True)
class StudentState:
    """学生状态 s：整体学习能力 A_s"""
    A: float


@dataclass(frozen=True)
class UPKSTParams:
    # 学习曲线参数（式2-1）
    k: float = 0.25

    # 总时间约束与下界（式2-8）
    T: float = 90.0 # 3个月，90天
    t_min: float = 2.0

    # ACO 参数（式2-6）
    alpha: float = 1.0
    beta: float = 2.0

    # 难度跃迁惩罚系数（式2-4 里的 β；为避免与 ACO beta 冲突，这里命名 beta_jump）
    beta_jump: float = 1.0

    # 信息素挥发系数（式2-15/2-18）
    rho: float = 0.1

    # 迭代与蚂蚁数量
    n_ants: int = 30
    n_iters: int = 80

    # 其他
    eps: float = 1e-9
    seed: int = 42

    # 初始信息素
    tau0: float = 1.0

    # 信息素裁剪（防止数值爆炸/消失）
    tau_min: float = 1e-6
    tau_max: float = 1e6


@dataclass(frozen=True)
class Solution:
    """一次候选解：路径P + 时间分配t + 指标"""
    path: List[int]
    t_map: Dict[int, float]
    U: float
    L: float
    Q: float
    lam: float
