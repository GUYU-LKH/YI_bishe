# -*- coding: utf-8 -*-
"""
单学生快速跑通UPKST（不需要profiles），用于确认算法可运行。
"""
from __future__ import annotations
import os
import sys

# 确保可以 import upkst
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from upkst.types import StudentState, UPKSTParams
from upkst.datasets.paper_table3_3 import make_points_from_table
from upkst.datasets.prereq_default import apply_prereqs
from upkst.runner import run_upkst


def main():
    student = StudentState(A=1.0)
    masteries = {
        "一元函数导数及其应用": 0.3,
        "平面解析几何": 0.4,
        "三角函数": 0.55,
    }
    points = make_points_from_table(masteries=masteries, base_unit=6.0)
    name_to_id = {kp.name: kid for kid, kp in points.items()}
    points = apply_prereqs(points, name_to_id)

    params = UPKSTParams(
        k=0.35, T=120.0, t_min=3.0,
        alpha=1.0, beta=2.0, beta_jump=0.8,
        rho=0.15, n_ants=50, n_iters=120, seed=7
    )

    best = run_upkst(points, student, params)
    print("\n===== BEST SOLUTION =====")
    print("Path (name):", [points[i].name for i in best.path])
    print("lambda:", best.lam)
    print(f"U={best.U:.6f}  L={best.L:.6f}  Q={best.Q:.6f}")
    print("Time allocation sum:", sum(best.t_map.values()))
    for i in best.path:
        kp = points[i]
        print(f"  {kp.name:<12}  t={best.t_map[i]:.2f}  w={kp.w}  d={kp.d}  m={kp.mastery}")


if __name__ == "__main__":
    main()
