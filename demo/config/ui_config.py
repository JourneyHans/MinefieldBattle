# -*- coding: utf-8 -*-
"""
UI外观和布局配置（UI设计师）
"""
# 导入地图和窗口配置（用于布局计算）
from .map_config import MAP_WIDTH, MAP_HEIGHT
from .card_config import CARD_WIDTH as CARD_WIDTH_DEFAULT, CARD_HEIGHT as CARD_HEIGHT_DEFAULT, CARD_MARGIN as CARD_MARGIN_DEFAULT

# 颜色配置
COLOR_HIDDEN = (100, 100, 100)  # 隐藏格子 - 灰色
COLOR_REVEALED = (200, 200, 200)  # 已揭示格子 - 浅灰色
COLOR_NUMBER = (150, 200, 255)  # 数字格子 - 浅蓝色
COLOR_MONSTER = (255, 100, 100)  # 怪物格子 - 红色
COLOR_DEPLOYED = (100, 255, 100)  # 已部署兵种 - 绿色
COLOR_COUNTDOWN = (255, 200, 100)  # 倒计时中 - 橙色
COLOR_MONSTER_WON = (255, 50, 50)  # 怪物胜利 - 深红色
COLOR_MONSTER_LOST = (150, 150, 150)  # 怪物失败 - 灰色
COLOR_TEXT = (0, 0, 0)  # 文字颜色 - 黑色
COLOR_BACKGROUND = (240, 240, 240)  # 背景色 - 浅灰色
COLOR_UI_BG = (50, 50, 50)  # UI背景 - 深灰色
COLOR_UI_TEXT = (255, 255, 255)  # UI文字 - 白色

# 窗口配置 - 固定16:9分辨率
WINDOW_WIDTH = 640  # 窗口宽度
WINDOW_HEIGHT = 360  # 窗口高度

# 布局配置（将在calculate_layout()中动态计算）
# 这些变量将在布局计算后设置
CELL_SIZE = 50  # 默认值，会被动态计算覆盖
CELL_MARGIN = 2  # 默认值，会被动态计算覆盖
MAP_AREA_WIDTH = 0
MAP_AREA_HEIGHT = 0
MAP_START_X = 0
MAP_START_Y = 0
UI_PANEL_WIDTH = 0
UI_PANEL_X = 0
UI_PANEL_Y = 0
UI_PANEL_HEIGHT = 0
HAND_AREA_Y = 0
HAND_AREA_X = 0
HAND_AREA_WIDTH = 0
BUTTON_X = 0
BUTTON_Y = 0
BUTTON_WIDTH = 120  # 默认值，会被动态计算覆盖
BUTTON_HEIGHT = 40  # 默认值，会被动态计算覆盖
CARD_WIDTH = 80  # 默认值，会被动态计算覆盖
CARD_HEIGHT = 120  # 默认值，会被动态计算覆盖
CARD_MARGIN = 5  # 默认值，会被动态计算覆盖
LEFT_PANEL_WIDTH = 0
LEFT_PANEL_X = 0
LEFT_PANEL_Y = 0
LEFT_PANEL_HEIGHT = 0
RIGHT_PANEL_WIDTH = 0
RIGHT_PANEL_X = 0
RIGHT_PANEL_Y = 0
RIGHT_PANEL_HEIGHT = 0

# 按钮配置（BUTTON_WIDTH和BUTTON_HEIGHT在calculate_layout()中动态计算）
BUTTON_COLOR = (100, 150, 200)  # 按钮颜色
BUTTON_HOVER_COLOR = (120, 170, 220)  # 按钮悬停颜色
BUTTON_TEXT_COLOR = (255, 255, 255)  # 按钮文字颜色


def calculate_layout():
    """
    根据窗口大小动态计算所有布局参数
    布局方案：
    - 左边：操作说明（小面板，不显眼）
    - 中间：棋盘（大）+ 手牌（大）- 占据视觉主要位置
    - 右边：游戏状态（生命值、回合数等）+ 结束回合按钮
    """
    global CELL_SIZE, CELL_MARGIN, MAP_AREA_WIDTH, MAP_AREA_HEIGHT
    global MAP_START_X, MAP_START_Y
    global UI_PANEL_WIDTH, UI_PANEL_X, UI_PANEL_Y, UI_PANEL_HEIGHT
    global HAND_AREA_Y, HAND_AREA_X, HAND_AREA_WIDTH
    global BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
    global CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN
    global LEFT_PANEL_WIDTH, LEFT_PANEL_X, LEFT_PANEL_Y, LEFT_PANEL_HEIGHT
    global RIGHT_PANEL_WIDTH, RIGHT_PANEL_X, RIGHT_PANEL_Y, RIGHT_PANEL_HEIGHT
    
    # 基础边距
    margin = max(5, min(WINDOW_WIDTH, WINDOW_HEIGHT) // 40)
    
    # 左边面板（操作说明）- 不显眼，较小
    LEFT_PANEL_WIDTH = max(120, WINDOW_WIDTH // 8)
    LEFT_PANEL_X = margin
    LEFT_PANEL_Y = margin
    LEFT_PANEL_HEIGHT = WINDOW_HEIGHT - margin * 2
    
    # 右边面板（游戏状态）- 中等大小
    RIGHT_PANEL_WIDTH = max(150, WINDOW_WIDTH // 6)
    RIGHT_PANEL_X = WINDOW_WIDTH - RIGHT_PANEL_WIDTH - margin
    RIGHT_PANEL_Y = margin
    RIGHT_PANEL_HEIGHT = WINDOW_HEIGHT - margin * 2
    
    # 中间区域（棋盘和手牌）- 占据主要空间
    center_area_x = LEFT_PANEL_X + LEFT_PANEL_WIDTH + margin
    center_area_width = RIGHT_PANEL_X - center_area_x - margin
    center_area_height = WINDOW_HEIGHT - margin * 2
    
    # 手牌区域预留高度（按窗口高度比例，但不要太大）
    hand_area_reserved_height = max(60, center_area_height // 5)
    
    # 地图可用空间
    available_width_for_map = center_area_width - margin * 2
    available_height_for_map = center_area_height - hand_area_reserved_height - margin * 2
    
    # 计算格子大小（让棋盘尽可能大）
    cell_size_by_width = (available_width_for_map - margin) // (MAP_WIDTH + 1)
    cell_size_by_height = (available_height_for_map - margin) // (MAP_HEIGHT + 1)
    
    # 取较小值，确保地图完整显示
    CELL_SIZE = max(20, min(cell_size_by_width, cell_size_by_height))
    CELL_MARGIN = max(1, CELL_SIZE // 25)
    
    # 计算地图区域实际大小
    MAP_AREA_WIDTH = MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
    MAP_AREA_HEIGHT = MAP_HEIGHT * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
    
    # 地图在中间区域居中
    MAP_START_X = center_area_x + (center_area_width - MAP_AREA_WIDTH) // 2
    MAP_START_Y = margin + (available_height_for_map - MAP_AREA_HEIGHT) // 2
    
    # 手牌区域位置和大小（在棋盘下方，居中）
    HAND_AREA_X = center_area_x + (center_area_width - MAP_AREA_WIDTH) // 2
    HAND_AREA_Y = MAP_START_Y + MAP_AREA_HEIGHT + margin
    HAND_AREA_WIDTH = MAP_AREA_WIDTH
    
    # 卡牌大小（根据格子大小按比例计算，让卡牌更大）
    card_scale = CELL_SIZE / 50.0
    CARD_WIDTH = max(50, int(80 * card_scale))
    CARD_HEIGHT = max(75, int(120 * card_scale))
    CARD_MARGIN = max(3, int(5 * card_scale))
    
    # 右边面板（游戏状态）
    UI_PANEL_X = RIGHT_PANEL_X
    UI_PANEL_Y = RIGHT_PANEL_Y
    UI_PANEL_WIDTH = RIGHT_PANEL_WIDTH
    UI_PANEL_HEIGHT = RIGHT_PANEL_HEIGHT
    
    # 结束回合按钮位置（在右边面板底部）
    button_scale = CELL_SIZE / 50.0
    BUTTON_WIDTH = max(80, int(120 * button_scale))
    BUTTON_HEIGHT = max(30, int(40 * button_scale))
    BUTTON_X = UI_PANEL_X + (UI_PANEL_WIDTH - BUTTON_WIDTH) // 2  # 居中
    BUTTON_Y = UI_PANEL_Y + UI_PANEL_HEIGHT - BUTTON_HEIGHT - margin  # 底部


# 初始化布局
calculate_layout()

