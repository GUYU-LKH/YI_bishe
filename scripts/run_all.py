# -*- coding: utf-8 -*-
"""
一键跑完整流程：
1) 从 data/students/students.xlsx 生成画像到 output/profiles/
2) 批量跑UPKST输出到 output/results/

用法：
  python scripts/run_all.py
"""
from __future__ import annotations
import os
import sys
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable

def run(cmd):
    print("\n>>", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    run([PY, os.path.join(ROOT, "scripts", "build_profiles_from_excel.py")])
    # 先用较小参数快速验证，可自行在 run_batch_students.py 里改默认或传参
    run([PY, os.path.join(ROOT, "scripts", "run_batch_students.py")])

if __name__ == "__main__":
    main()
