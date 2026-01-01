UPKST 完整可运行包（含测试Excel）
==============================

目录结构（upkst 与 data/output 同级）：
  upkst/                 核心算法包
  scripts/               运行脚本
  data/students/students.xlsx   测试数据（合成）
  output/                默认输出目录（会自动生成子目录）

一键运行（推荐）：
  python scripts/run_all.py

分步运行：
  1) 生成学生画像（m 与 A）
     python scripts/build_profiles_from_excel.py
  2) 批量跑UPKST
     python scripts/run_batch_students.py

说明：
  - 默认读取 data/students/students.xlsx 的 raw_long sheet。
  - 生成的画像输出到 output/profiles/
  - 运行结果输出到 output/results/
