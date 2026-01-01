"""
从Excel/CSV构建学生画像：
- 知识点掌握度 m_{s,i}（0~1）
- 整体学习能力 A_s（>0）

默认输入：data/students/students.xlsx 的 raw_long sheet。

默认输出到：output/profiles/
  - mastery_long.csv
  - mastery_wide.csv
  - ability.csv
  - debug_exam_kp_stats.csv
  - profiles.xlsx
  - config_used.json
"""
from __future__ import annotations
import argparse
import os
import json
import sys

import pandas as pd

# 允许直接 python scripts/*.py 运行：把项目根目录加入 sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from upkst.profile_builder import load_long_table, build_mastery, build_ability, ProfileParams


DEFAULT_INPUT = os.path.join(ROOT, "data", "students", "students.xlsx")
DEFAULT_OUTDIR = os.path.join(ROOT, "output", "profiles")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=DEFAULT_INPUT, help="输入Excel/CSV路径")
    ap.add_argument("--sheet", default="raw_long", help="Excel中的sheet名（默认 raw_long）")
    ap.add_argument("--out_dir", default=DEFAULT_OUTDIR, help="输出目录")
    ap.add_argument("--gamma", type=float, default=1.2)
    ap.add_argument("--decay_lambda", type=float, default=0.003)
    ap.add_argument("--kappa", type=float, default=0.3)
    ap.add_argument("--fill_mastery", type=float, default=0.5)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    params = ProfileParams(gamma=args.gamma, decay_lambda=args.decay_lambda, kappa=args.kappa, fill_mastery=args.fill_mastery)

    df = load_long_table(args.input, sheet=args.sheet)

    mastery_long, debug_stats = build_mastery(df, params)
    ability = build_ability(df, params)

    mastery_wide = mastery_long.pivot_table(index="student_id", columns="kp_name", values="mastery", aggfunc="mean").reset_index()

    mastery_long.to_csv(os.path.join(args.out_dir, "mastery_long.csv"), index=False, encoding="utf-8-sig")
    mastery_wide.to_csv(os.path.join(args.out_dir, "mastery_wide.csv"), index=False, encoding="utf-8-sig")
    ability.to_csv(os.path.join(args.out_dir, "ability.csv"), index=False, encoding="utf-8-sig")
    debug_stats.to_csv(os.path.join(args.out_dir, "debug_exam_kp_stats.csv"), index=False, encoding="utf-8-sig")

    out_xlsx = os.path.join(args.out_dir, "profiles.xlsx")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        mastery_long.to_excel(w, index=False, sheet_name="mastery_long")
        mastery_wide.to_excel(w, index=False, sheet_name="mastery_wide")
        ability.to_excel(w, index=False, sheet_name="ability")
        debug_stats.to_excel(w, index=False, sheet_name="debug_exam_kp_stats")

    with open(os.path.join(args.out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "input": args.input,
            "sheet": args.sheet,
            "params": params.__dict__,
        }, f, ensure_ascii=False, indent=2)

    print("OK. Profiles written to:", os.path.abspath(args.out_dir))


if __name__ == "__main__":
    main()
