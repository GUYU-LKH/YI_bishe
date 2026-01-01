"""
kkt_time.py

给定路径 P 的最优学习时间分配（对应论文式(2-8)~(2-13)）：
  max_t  Σ_{i∈P} w_i * Δm_i(t_i)
  s.t.   Σ_{i∈P} t_i = T,   t_i ≥ t_min

学习曲线导数形式（与你论文一致）：
  f_i'(t) = w_i (1 - m_i) a_i exp(-a_i t)
  其中 a_i = k * A_s / d_i

KKT 得到闭式：
  t_i*(λ) = max{ t_min, (1/a_i) ln( w_i(1-m_i)a_i / λ ) }

λ 通过总时长等式 Σ t_i*(λ) = T 用二分法求解。

注意：
- 本实现假设 P 包含所有知识点，因此可行性必须满足：T ≥ |P| * t_min
- 若出现“所有点都被锁死在 t_min 但 T 更大”的退化情况（例如所有 c_i≈0），
  则目标对额外时间近似不敏感，本实现会把剩余时间均分出去以满足等式约束。
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import math

from .types import KnowledgePoint, StudentState, UPKSTParams


def allocate_time_kkt(
    points: Dict[int, KnowledgePoint],
    path: List[int],
    student: StudentState,
    params: UPKSTParams,
) -> Tuple[Dict[int, float], float]:
    """
    返回：
      t_map: Dict[kid, t_i]
      lam:   λ*
    """
    n = len(path)
    if n == 0:
        return {}, 0.0

    # 1) 可行性检查（P包含所有知识点时尤为关键）
    if params.T < n * params.t_min - 1e-12:
        raise ValueError(f"Infeasible time budget: T={params.T} < |P|*t_min={n*params.t_min}")

    # 2) 预计算 a_i 与 c_i（导数系数）
    #    f'_i(t) = c_i * exp(-a_i t),  其中 c_i = w_i(1-m_i)a_i
    a: Dict[int, float] = {}
    c: Dict[int, float] = {}
    for i in path:
        p = points[i]
        ai = params.k * float(student.A) / max(float(p.d), params.eps)
        ai = max(ai, params.eps)
        ci = float(p.w) * (1.0 - float(p.mastery)) * ai
        a[i] = ai
        c[i] = max(ci, 0.0)

    def t_of_lambda(lam: float) -> Dict[int, float]:
        """按闭式计算 t_i(λ)，并做下界截断：t_i>=t_min"""
        lam = max(lam, params.eps)
        out: Dict[int, float] = {}
        for i in path:
            ai = a[i]
            ci = c[i]

            # 无约束解： (1/ai) ln(ci/lam)
            # 若 ci=0，则 ln(0) -> -inf，最后会被 max 截断到 t_min
            ratio = ci / lam
            ratio = max(ratio, params.eps)  # 防止 log(0)
            t_un = (1.0 / ai) * math.log(ratio)

            # 下界：t_i >= t_min  →  max
            out[i] = max(params.t_min, t_un)
        return out

    def sum_t(lam: float) -> float:
        tm = t_of_lambda(lam)
        return sum(tm[i] for i in path)

    # 3) 构造二分区间
    # λ 越大 -> t 越小 -> Σt 越小（单调）
    lam_lo = 1e-12

    # 选一个足够大的 lam_hi，使所有点都压到 t_min：
    # 当 lam >= c_i * exp(-a_i*t_min) 时，无约束解 <= t_min
    lam_hi = max(c[i] * math.exp(-a[i] * params.t_min) for i in path) + 1e-12
    lam_hi = max(lam_hi, 1e-12)

    # 理论上：sum(lam_lo) >= T >= sum(lam_hi)=n*t_min
    # 这里做个稳健兜底（极端数值下可能需要扩大 lam_hi）
    if sum_t(lam_hi) > params.T + 1e-9:
        # 扩大到足够大，直到 Σt <= T
        for _ in range(50):
            lam_hi *= 10.0
            if sum_t(lam_hi) <= params.T + 1e-9:
                break

    # 4) 二分求 λ*
    for _ in range(80):
        lam_mid = 0.5 * (lam_lo + lam_hi)
        s_mid = sum_t(lam_mid)

        if abs(s_mid - params.T) <= 1e-9:
            lam_lo = lam_hi = lam_mid
            break

        if s_mid > params.T:
            # 时间太多：增大 λ 把时间压下来
            lam_lo = lam_mid
        else:
            # 时间太少：减小 λ 把时间放大
            lam_hi = lam_mid

    lam_star = 0.5 * (lam_lo + lam_hi)
    t_map = t_of_lambda(lam_star)

    # 5) 数值误差修正：把 gap 分配出去，确保严格 Σt=T
    s = sum(t_map[i] for i in path)
    gap = params.T - s

    if abs(gap) > 1e-8:
        # 优先分给未锁死点（t > t_min）
        free = [i for i in path if t_map[i] > params.t_min + 1e-12]

        if free:
            add = gap / len(free)
            for i in free:
                t_map[i] = max(params.t_min, t_map[i] + add)
        else:
            # 退化情况：全部锁死但仍有 gap（例如 c_i 全≈0）
            # 目标对额外时间不敏感，均分以满足等式约束
            add = gap / n
            for i in path:
                t_map[i] = max(params.t_min, t_map[i] + add)

    return t_map, lam_star
