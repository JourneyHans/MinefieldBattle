# -*- coding: utf-8 -*-
"""
游戏数值配置（数值策划）
"""
from .difficulty_config import DEFAULT_DIFFICULTY, DIFFICULTY_CONFIGS

# 游戏配置
INITIAL_HEALTH = 4  # 初始生命值
INITIAL_ROUNDS = 50  # 初始回合数
COUNTDOWN_ROUNDS = 3  # 倒计时回合数

# 怪物数量配置（从难度配置动态获取）
def get_monster_count():
    """从当前难度配置获取地雷数量"""
    from config_mgr import current_difficulty
    config = DIFFICULTY_CONFIGS.get(current_difficulty, DIFFICULTY_CONFIGS[DEFAULT_DIFFICULTY])
    return config["mines"]

# 默认值（向后兼容）
MONSTER_COUNT_MIN = 10  # 最少怪物数量（已废弃，使用get_monster_count()）
MONSTER_COUNT_MAX = 15  # 最多怪物数量（已废弃，使用get_monster_count()）

# 怪物战力计算配置
MONSTER_BASE_POWER = 2  # 怪物基础战力（确保最低战力）
MONSTER_POWER_DIVISOR = 3  # 怪物战力计算除数（相邻数字和除以该值）

