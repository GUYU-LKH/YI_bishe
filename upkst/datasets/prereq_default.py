# 默认先修关系

from __future__ import annotations
from typing import Dict, Tuple


PREREQS_BY_NAME: Dict[str, Tuple[str, ...]] = {
    "集合与逻辑": (),

    # 函数体系
    "函数概念与性质": ("集合与逻辑",),
    "幂函数": ("函数概念与性质",),
    "指数函数": ("函数概念与性质",),
    "对数函数": ("函数概念与性质",),
    "函数应用": ("函数概念与性质",),

    # 三角与向量/几何
    "三角函数": ("函数概念与性质",),
    "平面向量及其应用": ("三角函数",),
    "平面解析几何": ("平面向量及其应用", "函数概念与性质"),

    # 立体
    "立体几何初步": ("集合与逻辑",),
    "空间向量与立体几何": ("平面向量及其应用", "立体几何初步"),

    # 代数/其他
    "数列": ("函数概念与性质",),

    # 导数（一般依赖函数）
    "一元函数导数及其应用": ("函数概念与性质",),

    # 概率统计与计数
    "计数原理": ("集合与逻辑",),
    "概率": ("计数原理",),
    "统计": ("集合与逻辑",),

    # 复数
    "复数": ("集合与逻辑",),
}


def apply_prereqs(points_by_id, name_to_id):
    """把 PREREQS_BY_NAME 写回 points[kid].prereqs（按ID）。"""
    from dataclasses import replace

    for kid, kp in list(points_by_id.items()):
        prereq_names = PREREQS_BY_NAME.get(kp.name, ())
        prereq_ids = tuple(name_to_id[n] for n in prereq_names if n in name_to_id)
        points_by_id[kid] = replace(kp, prereqs=prereq_ids)
    return points_by_id
