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


def calculate_layout():
    """
    根据窗口大小动态计算所有布局参数
    支持任意16:9分辨率
    """
    global CELL_SIZE, CELL_MARGIN, MAP_AREA_WIDTH, MAP_AREA_HEIGHT
    global MAP_START_X, MAP_START_Y
    global UI_PANEL_WIDTH, UI_PANEL_X, UI_PANEL_Y, UI_PANEL_HEIGHT
    global HAND_AREA_Y, HAND_AREA_X, HAND_AREA_WIDTH
    global BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
    global CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN
    
    # 基础边距（按窗口大小比例缩放）
    base_margin = max(5, min(WINDOW_WIDTH, WINDOW_HEIGHT) // 20)
    margin = base_margin
    
    # UI面板最小宽度（按窗口宽度比例）
    ui_panel_min_width = max(150, WINDOW_WIDTH // 5)
    ui_panel_max_width = WINDOW_WIDTH // 3
    
    # 手牌区域预留高度（按窗口高度比例）
    hand_area_reserved_height = max(80, WINDOW_HEIGHT // 6)
    
    # 计算地图可用空间
    # 方案：地图在左，UI在右，手牌在底部
    available_width_for_map = WINDOW_WIDTH - margin * 2 - ui_panel_min_width - margin
    available_height_for_map = WINDOW_HEIGHT - margin * 2 - hand_area_reserved_height - margin
    
    # 计算格子大小（确保地图完整显示）
    # 地图需要：MAP_WIDTH个格子 + (MAP_WIDTH-1)个间距 + 2个边距
    cell_size_by_width = (available_width_for_map - margin * 2) // (MAP_WIDTH + 1)
    cell_size_by_height = (available_height_for_map - margin * 2) // (MAP_HEIGHT + 1)
    
    # 取较小值，确保地图完整显示
    CELL_SIZE = max(15, min(cell_size_by_width, cell_size_by_height))  # 最小15像素
    CELL_MARGIN = max(1, CELL_SIZE // 25)  # 间距按比例缩放
    
    # 计算地图区域实际大小
    MAP_AREA_WIDTH = MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
    MAP_AREA_HEIGHT = MAP_HEIGHT * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
    
    # 地图起始位置（居中或靠左）
    MAP_START_X = margin
    MAP_START_Y = margin
    
    # UI面板位置和大小
    UI_PANEL_X = MAP_START_X + MAP_AREA_WIDTH + margin
    UI_PANEL_Y = MAP_START_Y
    # UI面板宽度：使用剩余空间，但限制在合理范围内
    remaining_width = WINDOW_WIDTH - UI_PANEL_X - margin
    UI_PANEL_WIDTH = max(ui_panel_min_width, min(ui_panel_max_width, remaining_width))
    # UI面板高度：从地图顶部到窗口底部（留出底部边距）
    UI_PANEL_HEIGHT = WINDOW_HEIGHT - UI_PANEL_Y - margin
    
    # 手牌区域位置和大小
    HAND_AREA_X = MAP_START_X
    HAND_AREA_Y = MAP_START_Y + MAP_AREA_HEIGHT + margin
    HAND_AREA_WIDTH = MAP_AREA_WIDTH
    
    # 卡牌大小（根据格子大小按比例计算）
    # 原始比例：CELL_SIZE=50时，CARD_WIDTH=80, CARD_HEIGHT=120
    card_scale = CELL_SIZE / 50.0
    CARD_WIDTH = max(40, int(80 * card_scale))
    CARD_HEIGHT = max(60, int(120 * card_scale))
    CARD_MARGIN = max(2, int(5 * card_scale))
    
    # 结束回合按钮位置和大小
    BUTTON_X = HAND_AREA_X + HAND_AREA_WIDTH + margin
    BUTTON_Y = HAND_AREA_Y + margin // 2
    # 按钮大小按比例缩放
    button_scale = CELL_SIZE / 50.0
    BUTTON_WIDTH = max(60, int(120 * button_scale))
    BUTTON_HEIGHT = max(25, int(40 * button_scale))


# 初始化布局
calculate_layout()

# 按钮配置（BUTTON_WIDTH和BUTTON_HEIGHT在calculate_layout()中动态计算）
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

