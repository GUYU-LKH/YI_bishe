# -*- coding: utf-8 -*-
"""
批量运行UPKST：读取 build_profiles_from_excel.py 的输出（mastery_long + ability），
对每个学生生成最优路径 P 与时间分配 t，并导出结果。

默认输入：output/profiles/
默认输出：output/results/
"""
from __future__ import annotations
import argparse
import os
import sys
import pandas as pd

# 允许直接 python scripts/*.py 运行：把项目根目录加入 sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from upkst.types import StudentState, UPKSTParams
from upkst.runner import run_upkst
from upkst.datasets.paper_table3_3 import make_points_from_table, override_masteries
from upkst.datasets.prereq_default import apply_prereqs


DEFAULT_PROFILES_DIR = os.path.join(ROOT, "output", "profiles")
DEFAULT_OUT_DIR = os.path.join(ROOT, "output", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles_dir", default=DEFAULT_PROFILES_DIR, help="profiles目录（含 mastery_long.csv, ability.csv）")
    ap.add_argument("--out_dir", default=DEFAULT_OUT_DIR, help="输出目录")
    ap.add_argument("--T", type=float, default=90.0, help="3个月，90天")
    ap.add_argument("--t_min", type=float, default=2.0, help="复习的最小天数")
    ap.add_argument("--n_ants", type=int, default=30)
    ap.add_argument("--n_iters", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    mastery_long = pd.read_csv(os.path.join(args.profiles_dir, "mastery_long.csv"), encoding="utf-8-sig")
    ability = pd.read_csv(os.path.join(args.profiles_dir, "ability.csv"), encoding="utf-8-sig")

    base_points = make_points_from_table(masteries={}, base_unit=6.0, normalize_weights=False)
    name_to_id = {kp.name: kid for kid, kp in base_points.items()}
    base_points = apply_prereqs(base_points, name_to_id)

    by_student = mastery_long.groupby("student_id")

    summary_rows = []
    time_rows = []
    edge_rows = []

    for _, row in ability.iterrows():
        sid = row["student_id"]
        A_s = float(row["A_s"])

        if sid in by_student.groups:
            sub = by_student.get_group(sid)
            m_map = {r["kp_name"]: float(r["mastery"]) for _, r in sub.iterrows()}
        else:
            m_map = {}

        points = override_masteries(base_points, m_map)
        student = StudentState(A=A_s)

        params = UPKSTParams(
            k=0.35,
            T=args.T,
            t_min=args.t_min,
            alpha=1.0,
            beta=2.0,
            beta_jump=0.8,
            rho=0.15,
            n_ants=args.n_ants,
            n_iters=args.n_iters,
            seed=args.seed,
        )

        best = run_upkst(points, student, params)

        path_names = [points[i].name for i in best.path]
        summary_rows.append({
            "student_id": sid,
            "A_s": A_s,
            "U": best.U,
            "L": best.L,
            "Q": best.Q,
            "lambda": best.lam,
            "path_kids": "->".join(map(str, best.path)),
            "path_names": "->".join(path_names),
        })

        for i in best.path:
            kp = points[i]
            time_rows.append({
                "student_id": sid,
                "kid": i,
                "kp_name": kp.name,
                "t": best.t_map[i],
                "w": kp.w,
                "d": kp.d,
                "mastery": kp.mastery,
            })

        for a, b in zip(best.path[:-1], best.path[1:]):
            edge_rows.append({
                "student_id": sid,
                "from_kid": a,
                "to_kid": b,
                "from_name": points[a].name,
                "to_name": points[b].name,
            })

    summary_df = pd.DataFrame(summary_rows)
    time_df = pd.DataFrame(time_rows)
    edge_df = pd.DataFrame(edge_rows)

    summary_df.to_csv(os.path.join(args.out_dir, "best_plan_summary.csv"), index=False, encoding="utf-8-sig")
    time_df.to_csv(os.path.join(args.out_dir, "best_time_long.csv"), index=False, encoding="utf-8-sig")
    edge_df.to_csv(os.path.join(args.out_dir, "best_path_edges.csv"), index=False, encoding="utf-8-sig")

    print("OK. Results written to:", os.path.abspath(args.out_dir))


if __name__ == "__main__":
    main()
