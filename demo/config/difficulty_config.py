# -*- coding: utf-8 -*-
"""
难度配置（关卡策划）
定义三种扫雷难度级别
"""
from enum import Enum


class Difficulty(Enum):
    """难度级别"""
    BEGINNER = "beginner"      # 初级
    INTERMEDIATE = "intermediate"  # 中级
    EXPERT = "expert"          # 高级


# 难度配置字典
DIFFICULTY_CONFIGS = {
    Difficulty.BEGINNER: {
        "width": 9,
        "height": 9,
        "mines": 10,
        "name": "初级"
    },
    Difficulty.INTERMEDIATE: {
        "width": 16,
        "height": 16,
        "mines": 40,
        "name": "中级"
    },
    Difficulty.EXPERT: {
        "width": 16,
        "height": 30,
        "mines": 99,
        "name": "高级"
    }
}

# 默认难度
DEFAULT_DIFFICULTY = Difficulty.BEGINNER

