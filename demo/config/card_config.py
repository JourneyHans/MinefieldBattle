# -*- coding: utf-8 -*-
"""
卡牌配置（数值策划）
"""
from enum import Enum

# 卡牌配置
CARD_WIDTH = 80  # 卡牌宽度（初始默认值，会被动态计算覆盖）
CARD_HEIGHT = 120  # 卡牌高度（初始默认值，会被动态计算覆盖）
CARD_MARGIN = 5  # 卡牌间距（初始默认值，会被动态计算覆盖）
CARDS_PER_TURN = 5  # 每回合发牌数量
MAX_HAND_SIZE = 10  # 手牌最大数量

# 兵种类型枚举
class UnitCategory(Enum):
    """兵种类型"""
    STRENGTH = "strength"  # 力量
    AGILITY = "agility"   # 敏捷
    WISDOM = "wisdom"     # 智慧

# 基础兵种定义
BASE_UNITS = {
    "士兵": {
        "category": UnitCategory.STRENGTH,
        "name": "士兵",
        "color": (255, 100, 100),  # 红色
        "power": 1,
        "health": 1
    },
    "游侠": {
        "category": UnitCategory.AGILITY,
        "name": "游侠",
        "color": (100, 255, 100),  # 绿色
        "power": 1,
        "health": 1
    },
    "法师": {
        "category": UnitCategory.WISDOM,
        "name": "法师",
        "color": (100, 100, 255),  # 蓝色
        "power": 1,
        "health": 1
    }
}

# 发牌权重配置（用于加权随机）
# 格式：{兵种名称: 权重}
CARD_DEAL_WEIGHTS = {
    "士兵": 5,  # 力量类型权重
    "游侠": 5,  # 敏捷类型权重
    "法师": 5   # 智慧类型权重
}

# 兵种职业名称（保留用于向后兼容，已废弃）
UNIT_NAMES = {
    1: "战士",
    2: "弓箭手",
    3: "法师",
    4: "圣骑士",
    5: "盗贼",
    6: "德鲁伊",
    7: "龙骑士",
    8: "大法师"
}

