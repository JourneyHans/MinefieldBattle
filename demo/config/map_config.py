# -*- coding: utf-8 -*-
"""
地图配置（关卡策划）
"""
from .difficulty_config import DEFAULT_DIFFICULTY, DIFFICULTY_CONFIGS

# 地图配置（从难度配置动态获取，保留默认值用于向后兼容）
def get_map_size():
    """从当前难度配置获取地图大小"""
    from config_mgr import current_difficulty
    config = DIFFICULTY_CONFIGS.get(current_difficulty, DIFFICULTY_CONFIGS[DEFAULT_DIFFICULTY])
    return config["width"], config["height"]

# 默认值（向后兼容）
MAP_WIDTH = 10
MAP_HEIGHT = 10
CELL_SIZE = 50  # 每个格子的像素大小（初始默认值，会被动态计算覆盖）
CELL_MARGIN = 2  # 格子之间的间距（初始默认值，会被动态计算覆盖）

