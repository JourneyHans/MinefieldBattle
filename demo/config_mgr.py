# -*- coding: utf-8 -*-
"""
配置管理器 - 统一入口
导入所有子配置模块，保持向后兼容
"""
# 导入所有子配置模块
from config import map_config
from config import game_config
from config import ui_config
from config import card_config
from config import task_config
from config import difficulty_config

# 从各个子配置模块导入所有配置项，重新导出以保持向后兼容

# 地图配置
MAP_WIDTH = map_config.MAP_WIDTH
MAP_HEIGHT = map_config.MAP_HEIGHT
CELL_SIZE = ui_config.CELL_SIZE  # 从ui_config导入（会被calculate_layout更新）
CELL_MARGIN = ui_config.CELL_MARGIN  # 从ui_config导入（会被calculate_layout更新）

# 游戏数值配置
INITIAL_HEALTH = game_config.INITIAL_HEALTH
INITIAL_ROUNDS = game_config.INITIAL_ROUNDS
COUNTDOWN_ROUNDS = game_config.COUNTDOWN_ROUNDS
MONSTER_COUNT_MIN = game_config.MONSTER_COUNT_MIN
MONSTER_COUNT_MAX = game_config.MONSTER_COUNT_MAX
MONSTER_BASE_POWER = game_config.MONSTER_BASE_POWER
MONSTER_POWER_DIVISOR = game_config.MONSTER_POWER_DIVISOR

# UI配置 - 颜色
COLOR_HIDDEN = ui_config.COLOR_HIDDEN
COLOR_REVEALED = ui_config.COLOR_REVEALED
COLOR_NUMBER = ui_config.COLOR_NUMBER
COLOR_MONSTER = ui_config.COLOR_MONSTER
COLOR_DEPLOYED = ui_config.COLOR_DEPLOYED
COLOR_COUNTDOWN = ui_config.COLOR_COUNTDOWN
COLOR_MONSTER_WON = ui_config.COLOR_MONSTER_WON
COLOR_MONSTER_LOST = ui_config.COLOR_MONSTER_LOST
COLOR_TEXT = ui_config.COLOR_TEXT
COLOR_BACKGROUND = ui_config.COLOR_BACKGROUND
COLOR_UI_BG = ui_config.COLOR_UI_BG
COLOR_UI_TEXT = ui_config.COLOR_UI_TEXT

# UI配置 - 窗口
WINDOW_WIDTH = ui_config.WINDOW_WIDTH
WINDOW_HEIGHT = ui_config.WINDOW_HEIGHT

# UI配置 - 布局变量
MAP_AREA_WIDTH = ui_config.MAP_AREA_WIDTH
MAP_AREA_HEIGHT = ui_config.MAP_AREA_HEIGHT
MAP_START_X = ui_config.MAP_START_X
MAP_START_Y = ui_config.MAP_START_Y
UI_PANEL_WIDTH = ui_config.UI_PANEL_WIDTH
UI_PANEL_X = ui_config.UI_PANEL_X
UI_PANEL_Y = ui_config.UI_PANEL_Y
UI_PANEL_HEIGHT = ui_config.UI_PANEL_HEIGHT
HAND_AREA_Y = ui_config.HAND_AREA_Y
HAND_AREA_X = ui_config.HAND_AREA_X
HAND_AREA_WIDTH = ui_config.HAND_AREA_WIDTH
BUTTON_X = ui_config.BUTTON_X
BUTTON_Y = ui_config.BUTTON_Y
BUTTON_WIDTH = ui_config.BUTTON_WIDTH
BUTTON_HEIGHT = ui_config.BUTTON_HEIGHT
LEFT_PANEL_WIDTH = ui_config.LEFT_PANEL_WIDTH
LEFT_PANEL_X = ui_config.LEFT_PANEL_X
LEFT_PANEL_Y = ui_config.LEFT_PANEL_Y
LEFT_PANEL_HEIGHT = ui_config.LEFT_PANEL_HEIGHT
RIGHT_PANEL_WIDTH = ui_config.RIGHT_PANEL_WIDTH
RIGHT_PANEL_X = ui_config.RIGHT_PANEL_X
RIGHT_PANEL_Y = ui_config.RIGHT_PANEL_Y
RIGHT_PANEL_HEIGHT = ui_config.RIGHT_PANEL_HEIGHT

# UI配置 - 按钮
BUTTON_COLOR = ui_config.BUTTON_COLOR
BUTTON_HOVER_COLOR = ui_config.BUTTON_HOVER_COLOR
BUTTON_TEXT_COLOR = ui_config.BUTTON_TEXT_COLOR

# UI配置 - 设置按钮
SETTINGS_BUTTON_X = ui_config.SETTINGS_BUTTON_X
SETTINGS_BUTTON_Y = ui_config.SETTINGS_BUTTON_Y
SETTINGS_BUTTON_SIZE_SCALED = ui_config.SETTINGS_BUTTON_SIZE_SCALED
SETTINGS_BUTTON_COLOR = ui_config.SETTINGS_BUTTON_COLOR
SETTINGS_BUTTON_HOVER_COLOR = ui_config.SETTINGS_BUTTON_HOVER_COLOR
SETTINGS_PANEL_COLOR = ui_config.SETTINGS_PANEL_COLOR
SETTINGS_PANEL_ALPHA = ui_config.SETTINGS_PANEL_ALPHA

# UI配置 - 窗口基础尺寸
BASE_WIDTH = ui_config.BASE_WIDTH
BASE_HEIGHT = ui_config.BASE_HEIGHT

# 卡牌配置
CARD_WIDTH = ui_config.CARD_WIDTH  # 从ui_config导入（会被calculate_layout更新）
CARD_HEIGHT = ui_config.CARD_HEIGHT  # 从ui_config导入（会被calculate_layout更新）
CARD_MARGIN = ui_config.CARD_MARGIN  # 从ui_config导入（会被calculate_layout更新）
CARDS_PER_TURN = card_config.CARDS_PER_TURN
MAX_HAND_SIZE = card_config.MAX_HAND_SIZE
UNIT_NAMES = card_config.UNIT_NAMES  # 保留用于向后兼容（已废弃）

# 兵种类型配置
UnitCategory = card_config.UnitCategory
BASE_UNITS = card_config.BASE_UNITS
CARD_DEAL_WEIGHTS = card_config.CARD_DEAL_WEIGHTS

# 任务配置
TaskType = task_config.TaskType
TASK_COUNT = task_config.TASK_COUNT
TASK_TYPE_NAMES = task_config.TASK_TYPE_NAMES
TASK_TYPE_DESCRIPTIONS = task_config.TASK_TYPE_DESCRIPTIONS

# UI配置 - 任务颜色
COLOR_TASK = ui_config.COLOR_TASK
COLOR_TASK_COMPLETED = ui_config.COLOR_TASK_COMPLETED
COLOR_TASK_CLAIMED = ui_config.COLOR_TASK_CLAIMED

# 难度配置
Difficulty = difficulty_config.Difficulty
DIFFICULTY_CONFIGS = difficulty_config.DIFFICULTY_CONFIGS
DEFAULT_DIFFICULTY = difficulty_config.DEFAULT_DIFFICULTY

# 当前难度状态（默认初级）
current_difficulty = DEFAULT_DIFFICULTY

# 导出布局计算函数
calculate_layout = ui_config.calculate_layout

