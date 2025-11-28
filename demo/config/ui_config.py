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
COLOR_TASK = (200, 100, 255)  # 任务格子 - 紫色
COLOR_TASK_COMPLETED = (150, 255, 150)  # 任务已完成 - 浅绿色
COLOR_TASK_CLAIMED = (100, 255, 100)  # 任务已确认 - 绿色
COLOR_TEXT = (0, 0, 0)  # 文字颜色 - 黑色
COLOR_BACKGROUND = (240, 240, 240)  # 背景色 - 浅灰色
COLOR_UI_BG = (50, 50, 50)  # UI背景 - 深灰色
COLOR_UI_TEXT = (255, 255, 255)  # UI文字 - 白色

# 窗口配置 - 固定16:9分辨率
# 基础分辨率
BASE_WIDTH = 640
BASE_HEIGHT = 360

# 分辨率缩放（可以动态修改）
WINDOW_SCALE = 1.5  # 默认1.5倍
WINDOW_WIDTH = int(BASE_WIDTH * WINDOW_SCALE)  # 窗口宽度
WINDOW_HEIGHT = int(BASE_HEIGHT * WINDOW_SCALE)  # 窗口高度

# 设置按钮配置
SETTINGS_BUTTON_SIZE = 30  # 设置按钮大小（会根据分辨率缩放）
SETTINGS_BUTTON_MARGIN = 10  # 设置按钮边距

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

# 设置界面配置
SETTINGS_PANEL_COLOR = (60, 60, 80)  # 设置面板背景色
SETTINGS_PANEL_ALPHA = 240  # 设置面板透明度
SETTINGS_BUTTON_COLOR = (80, 120, 160)  # 设置界面按钮颜色
SETTINGS_BUTTON_HOVER_COLOR = (100, 140, 180)  # 设置界面按钮悬停颜色


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
    
    # 基础边距（确保是整数）
    margin = int(max(5, min(WINDOW_WIDTH, WINDOW_HEIGHT) // 40))
    
    # 生命条高度和位置（在顶部）
    health_bar_height = max(30, int(WINDOW_HEIGHT * 0.04))
    health_bar_y = max(5, int(WINDOW_HEIGHT * 0.01))
    health_bar_bottom = health_bar_y + health_bar_height
    
    # 棋盘和手牌区的起始位置（在生命条下方，留出更多空间）
    content_start_y = int(health_bar_bottom + margin * 2)  # 生命条下方留出更多空间
    
    # 左边面板（操作说明）- 不显眼，较小
    LEFT_PANEL_WIDTH = int(max(120, WINDOW_WIDTH // 8))
    LEFT_PANEL_X = int(margin)
    LEFT_PANEL_Y = int(content_start_y)
    LEFT_PANEL_HEIGHT = int(WINDOW_HEIGHT - content_start_y - margin)
    
    # 右边面板（游戏状态）- 中等大小
    RIGHT_PANEL_WIDTH = int(max(150, WINDOW_WIDTH // 6))
    RIGHT_PANEL_X = int(WINDOW_WIDTH - RIGHT_PANEL_WIDTH - margin)
    RIGHT_PANEL_Y = int(content_start_y)
    RIGHT_PANEL_HEIGHT = int(WINDOW_HEIGHT - content_start_y - margin)
    
    # 中间区域（棋盘和手牌）- 占据主要空间
    center_area_x = int(LEFT_PANEL_X + LEFT_PANEL_WIDTH + margin)
    center_area_width = int(RIGHT_PANEL_X - center_area_x - margin)
    center_area_height = int(WINDOW_HEIGHT - content_start_y - margin)
    
    # 手牌区域预留高度（按窗口高度比例，但不要太大）
    hand_area_reserved_height = int(max(60, center_area_height // 5))
    
    # 地图可用空间
    available_width_for_map = int(center_area_width - margin * 2)
    available_height_for_map = int(center_area_height - hand_area_reserved_height - margin * 2)
    
    # 计算格子大小（让棋盘尽可能大，但至少保证文本不超框）
    cell_size_by_width = int((available_width_for_map - margin) // (MAP_WIDTH + 1))
    cell_size_by_height = int((available_height_for_map - margin) // (MAP_HEIGHT + 1))
    
    # 取较小值，但设置最小值为40（确保文本不超框）
    CELL_SIZE = int(max(40, min(cell_size_by_width, cell_size_by_height)))
    CELL_MARGIN = int(max(1, CELL_SIZE // 25))
    
    # 计算地图区域实际大小
    MAP_AREA_WIDTH = int(MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN)
    MAP_AREA_HEIGHT = int(MAP_HEIGHT * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN)
    
    # 地图在中间区域居中（从content_start_y开始）
    MAP_START_X = int(center_area_x + (center_area_width - MAP_AREA_WIDTH) // 2)
    MAP_START_Y = int(content_start_y + (available_height_for_map - MAP_AREA_HEIGHT) // 2)
    
    # 手牌区域位置和大小（在棋盘下方，居中）
    HAND_AREA_X = int(center_area_x + (center_area_width - MAP_AREA_WIDTH) // 2)
    HAND_AREA_Y = int(MAP_START_Y + MAP_AREA_HEIGHT + margin)
    HAND_AREA_WIDTH = int(MAP_AREA_WIDTH)
    
    # 卡牌大小（根据格子大小按比例计算，让卡牌更大）
    card_scale = CELL_SIZE / 50.0
    CARD_WIDTH = int(max(50, int(80 * card_scale)))
    CARD_HEIGHT = int(max(75, int(120 * card_scale)))
    CARD_MARGIN = int(max(3, int(5 * card_scale)))
    
    # 右边面板（游戏状态）
    UI_PANEL_X = int(RIGHT_PANEL_X)
    UI_PANEL_Y = int(RIGHT_PANEL_Y)
    UI_PANEL_WIDTH = int(RIGHT_PANEL_WIDTH)
    UI_PANEL_HEIGHT = int(RIGHT_PANEL_HEIGHT)
    
    # 结束回合按钮位置（在右边面板底部）
    button_scale = CELL_SIZE / 50.0
    BUTTON_WIDTH = int(max(80, int(120 * button_scale)))
    BUTTON_HEIGHT = int(max(30, int(40 * button_scale)))
    BUTTON_X = int(UI_PANEL_X + (UI_PANEL_WIDTH - BUTTON_WIDTH) // 2)  # 居中
    BUTTON_Y = int(UI_PANEL_Y + UI_PANEL_HEIGHT - BUTTON_HEIGHT - margin)  # 底部
    
    # 设置按钮位置（右上角）
    global SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y, SETTINGS_BUTTON_SIZE_SCALED
    settings_button_size = int(SETTINGS_BUTTON_SIZE * WINDOW_SCALE)
    SETTINGS_BUTTON_X = int(WINDOW_WIDTH - settings_button_size - SETTINGS_BUTTON_MARGIN * WINDOW_SCALE)
    SETTINGS_BUTTON_Y = int(SETTINGS_BUTTON_MARGIN * WINDOW_SCALE)
    SETTINGS_BUTTON_SIZE_SCALED = settings_button_size


# 初始化布局
calculate_layout()

