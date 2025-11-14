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
COLOR_TEXT = (0, 0, 0)  # 文字颜色 - 黑色
COLOR_BACKGROUND = (240, 240, 240)  # 背景色 - 浅灰色
COLOR_UI_BG = (50, 50, 50)  # UI背景 - 深灰色
COLOR_UI_TEXT = (255, 255, 255)  # UI文字 - 白色

# 窗口配置
WINDOW_WIDTH = MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN + 200  # 地图宽度 + UI区域
WINDOW_HEIGHT = MAP_HEIGHT * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN + 100  # 地图高度 + 底部信息
UI_PANEL_WIDTH = 200  # UI面板宽度

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

