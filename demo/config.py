# -*- coding: utf-8 -*-
"""
游戏配置常量
"""

# 地图配置
MAP_WIDTH = 10
MAP_HEIGHT = 10
CELL_SIZE = 50  # 每个格子的像素大小
CELL_MARGIN = 2  # 格子之间的间距

# 游戏配置
INITIAL_HEALTH = 3  # 初始生命值
INITIAL_ROUNDS = 50  # 初始回合数
COUNTDOWN_DURATION = 5  # 倒计时时长（秒）
MONSTER_COUNT_MIN = 5  # 最少怪物数量
MONSTER_COUNT_MAX = 8  # 最多怪物数量

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

# 卡牌配置
CARD_WIDTH = 80  # 卡牌宽度
CARD_HEIGHT = 120  # 卡牌高度
CARD_MARGIN = 5  # 卡牌间距
CARDS_PER_TURN = 3  # 每回合发牌数量
MAX_HAND_SIZE = 10  # 手牌最大数量

# 窗口配置 - 固定16:9分辨率
WINDOW_WIDTH = 1920  # 窗口宽度
WINDOW_HEIGHT = 1080  # 窗口高度

# 布局配置
MAP_AREA_WIDTH = MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN  # 地图区域宽度
MAP_AREA_HEIGHT = MAP_HEIGHT * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN  # 地图区域高度
MAP_START_X = 50  # 地图起始X坐标（左侧边距）
MAP_START_Y = 50  # 地图起始Y坐标（顶部边距）

UI_PANEL_WIDTH = 300  # UI面板宽度
UI_PANEL_X = MAP_START_X + MAP_AREA_WIDTH + 30  # UI面板X坐标（地图右侧）
UI_PANEL_Y = MAP_START_Y  # UI面板Y坐标（与地图顶部对齐）
# UI面板高度：从地图顶部到窗口底部，留出底部边距
UI_PANEL_HEIGHT = WINDOW_HEIGHT - MAP_START_Y - 20  # UI面板高度（充分利用垂直空间）

HAND_AREA_Y = MAP_START_Y + MAP_AREA_HEIGHT + 30  # 手牌区域Y坐标（地图下方）
HAND_AREA_X = MAP_START_X  # 手牌区域X坐标（与地图左侧对齐）
HAND_AREA_WIDTH = MAP_AREA_WIDTH  # 手牌区域宽度（与地图宽度一致）

BUTTON_X = HAND_AREA_X + HAND_AREA_WIDTH + 30  # 结束回合按钮X坐标
BUTTON_Y = HAND_AREA_Y + 10  # 结束回合按钮Y坐标

# 按钮配置
BUTTON_HEIGHT = 40  # 按钮高度
BUTTON_WIDTH = 120  # 按钮宽度
BUTTON_COLOR = (100, 150, 200)  # 按钮颜色
BUTTON_HOVER_COLOR = (120, 170, 220)  # 按钮悬停颜色
BUTTON_TEXT_COLOR = (255, 255, 255)  # 按钮文字颜色

# 兵种职业名称
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

