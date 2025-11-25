# -*- coding: utf-8 -*-
"""
任务系统配置
"""
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    EXPLORE_ADJACENT = "explore_adjacent"  # 探查相邻8格
    BATTLE_ALL_MONSTERS = "battle_all_monsters"  # 与所有怪物交战
    FIND_TASK = "find_task"  # 找到任务格子


# 任务配置
TASK_COUNT = 1  # 每局游戏的任务格子数量（目前只实现通关任务）
TASK_TYPE_NAMES = {
    TaskType.EXPLORE_ADJACENT: "探查周边",
    TaskType.BATTLE_ALL_MONSTERS: "击败所有怪物",
    TaskType.FIND_TASK: "找到任务"
}

TASK_TYPE_DESCRIPTIONS = {
    TaskType.EXPLORE_ADJACENT: "探查任务格子相邻8格",
    TaskType.BATTLE_ALL_MONSTERS: "与所有怪物交战",
    TaskType.FIND_TASK: "找到任务格子"
}

