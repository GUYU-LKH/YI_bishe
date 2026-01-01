"""
论文第3章的“课标知识点 + 云数据分析”整理的知识点元数据。
综合得分、总权重%、综合难度(星级)、重要程度(星级)、考频。
这里默认：
  w_i <- 总权重(%)
  d_i <- 综合难度(星级)
  t_base <- base_unit * d_i
"""
from __future__ import annotations
from typing import Dict, Optional
from dataclasses import replace

from ..types import KnowledgePoint


TABLE3_3 = [
    ("一元函数导数及其应用", 92, 13.5, 4.5, 5, "必"),
    ("平面解析几何",         89, 17.0, 4.5, 5, "必"),
    ("三角函数",             85, 14.5, 3.5, 5, "必"),
    ("数列",                 82,  9.5, 4.0, 4, "必"),
    ("空间向量与立体几何",   78,  8.5, 3.5, 4, "必"),
    ("函数概念与性质",       75,  7.0, 3.5, 4, "必"),
    ("概率",                 70,  7.5, 3.0, 4, "高"),
    ("统计",                 68,  6.0, 3.0, 4, "高"),
    ("平面向量及其应用",     65,  3.0, 2.5, 3, "高"),
    ("指数函数",             60,  4.0, 2.5, 3, "中"),
    ("对数函数",             60,  4.0, 3.0, 3, "中"),
    ("立体几何初步",         58,  6.5, 2.5, 3, "中"),
    ("幂函数",               55,  3.0, 2.0, 2, "中"),
    ("函数应用",             52,  2.0, 2.5, 3, "中"),
    ("计数原理",             50,  2.0, 2.5, 2, "中"),
    ("复数",                 45,  3.0, 1.0, 2, "必"),
    ("集合与逻辑",           45,  3.0, 1.0, 2, "必"),
]


def make_points_from_table(masteries: Optional[Dict[str, float]] = None,
                           base_unit: float = 6.0,
                           normalize_weights: bool = False) -> Dict[int, KnowledgePoint]:
    """
    masteries: 可选，name->m 的初始掌握度；未给的默认 0.5
    base_unit: t_base 的基准系数（你可按“分钟/单位”等自己定）
    normalize_weights: 是否把 w 归一化到 sum(w)=1（可选）
    """
    masteries = masteries or {}
    points: Dict[int, KnowledgePoint] = {}

    weights = [float(w_pct) for (_, _, w_pct, *_rest) in TABLE3_3]
    w_scale = 1.0
    if normalize_weights:
        s = sum(weights)
        if s > 0:
            w_scale = 1.0 / s

    for i, (name, score, w_pct, diff_star, imp_star, freq) in enumerate(TABLE3_3, start=1):
        m = float(masteries.get(name, 0.5))
        kp = KnowledgePoint(
            kid=i,
            name=name,
            w=float(w_pct) * w_scale,
            d=float(diff_star),
            t_base=float(base_unit) * float(diff_star),
            mastery=m,
            prereqs=(),  # 先修关系在 prereq_default.py 里统一覆盖
        )
        points[i] = kp

    return points


def override_masteries(points_by_id: Dict[int, KnowledgePoint], masteries_by_name: Dict[str, float]) -> Dict[int, KnowledgePoint]:
    """把某个学生的 masteries(name->m) 写回 points[kid].mastery。"""
    out = {}
    for kid, kp in points_by_id.items():
        m = masteries_by_name.get(kp.name, kp.mastery)
        out[kid] = replace(kp, mastery=float(m))
    return out
