#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块
集中管理所有游戏配置
"""

# ==================== 窗口配置 ====================
# 分辨率配置
RESOLUTIONS = {
    '1440x810': {'width': 1440, 'height': 810},
    '1280x720': {'width': 1280, 'height': 720},
    '1024x768': {'width': 1024, 'height': 768}
}

# 默认分辨率
DEFAULT_RESOLUTION_KEY = '1440x810'
WINDOW_TITLE = "魔法军团"
FPS = 60  # 游戏帧率

# ==================== 颜色配置 ====================
# 背景颜色
BACKGROUND_COLOR = (0, 0, 0)  # 黑色 #000

# UI颜色
UI_TEXT_COLOR = (187, 187, 187)  # #bbb
UI_BG_COLOR = (42, 42, 42)  # #2a2a2a
UI_BG_HOVER_COLOR = (58, 58, 58)  # #3a3a3a
UI_BORDER_COLOR = (255, 255, 255)  # 白色
UI_BORDER_FOCUS_COLOR = (74, 158, 255)  # #4a9eff

# 棋盘颜色
GRID_BG_COLOR = (26, 26, 26)  # #1a1a1a 棋盘背景色（深灰色）
LAND_COLOR = (34, 34, 34)  # #222 土地地块颜色（比背景稍亮）
GRID_LINE_COLOR = (20, 20, 20)  # #141414 网格线颜色（加深，形成更明显的区分）
GRID_BORDER_COLOR = (102, 102, 102)  # #666 棋盘边框颜色

# 迷雾和标记颜色
FOG_COLOR = (58, 58, 58)  # #3a3a3a 迷雾方块颜色
MARK_COLOR = (204, 204, 204)  # #cccccc 标记颜色（浅灰色X）

# ==================== 棋盘配置 ====================
# 注意：这些值会在游戏初始化时根据难度自动设置
GRID_ROWS = 9  # 默认9×9棋盘（简单难度）
GRID_COLS = 9
BASE_CELL_SIZE = 36  # 基础格子大小（像素）
CELL_SIZE = 46  # 每个格子大小（像素），根据难度动态调整（9×9地图放大30%为46，其他为36）

GRID_BORDER_OFFSET = 8  # 边框向外扩展的像素（间距缩小50%，从12像素减少到8像素）
GRID_BORDER_WIDTH = 4  # 边框宽度（保持粗细不变）
GRID_LINE_WIDTH = 2  # 网格线宽度（加粗格子间距）
FOG_BLOCK_PADDING = 2  # 迷雾方块边距

# ==================== 字体配置 ====================
# 中文字体列表（按优先级）
CHINESE_FONT_NAMES = [
    'Microsoft YaHei',  # 微软雅黑（Windows常用）
    'SimHei',           # 黑体
    'SimSun',           # 宋体
    'KaiTi',            # 楷体
    'Arial Unicode MS', # Arial Unicode（如果存在）
    'arial',            # 备用：Arial
]

# 字体大小
FONT_SIZE_SMALL = 14
FONT_SIZE_MEDIUM = 18
FONT_SIZE_LARGE = 20

# ==================== 难度配置 ====================
# 难度选项（地图大小）
DIFFICULTIES = {
    'easy': {'rows': 9, 'cols': 9, 'display': '9×9'},
    'normal': {'rows': 16, 'cols': 16, 'display': '16×16'},
    'hard': {'rows': 16, 'cols': 30, 'display': '16×30'}
}

# 默认难度
DEFAULT_DIFFICULTY = 'easy'  # 默认9×9地图

# 根据难度获取格子大小（9×9地图放大30%）
def get_cell_size(difficulty):
    """根据难度获取格子大小"""
    if difficulty == 'easy':
        return int(BASE_CELL_SIZE * 1.3)  # 9×9地图放大30%
    return BASE_CELL_SIZE  # 其他难度保持原大小

# 根据难度获取棋子地块数量
def get_piece_land_block_counts(difficulty):
    """根据难度获取棋子地块数量"""
    counts = {
        'easy': {'danger': 9, 'safe': 1, 'endpoint': 1},  # 简单难度：危险9，安全1，终点1
        'normal': {'danger': 36, 'safe': 4, 'endpoint': 1},  # 普通难度：危险36，安全4，终点1
        'hard': {'danger': 89, 'safe': 10, 'endpoint': 1}  # 困难难度：危险89，安全10，终点1
    }
    return counts.get(difficulty, counts['normal'])

# ==================== UI配置 ====================
# 分辨率选择器位置
RESOLUTION_SELECTOR_X = 15
RESOLUTION_SELECTOR_Y = 15
RESOLUTION_BUTTON_WIDTH = 120
RESOLUTION_BUTTON_HEIGHT = 28
RESOLUTION_OPTION_HEIGHT = 28

# 难度选择器位置（右上角）
DIFFICULTY_SELECTOR_X = -1  # -1表示需要动态计算（右上角）
DIFFICULTY_SELECTOR_Y = 15
DIFFICULTY_BUTTON_WIDTH = 100
DIFFICULTY_BUTTON_HEIGHT = 28
DIFFICULTY_OPTION_HEIGHT = 28

# ==================== 生命值配置 ====================
MAX_HP = 5  # 最大生命值
HEALTH_BAR_HEIGHT = 35  # 血条高度（像素）
HEALTH_BAR_WIDTH = 200  # 血条固定宽度（像素）
HEALTH_BAR_Y = 20  # 血条距离画面上方（像素）
HEALTH_BAR_LABEL_X = 350  # 标签距离画面左侧（像素）
HEALTH_BAR_LABEL_SPACING = 15  # 标签和血条之间的间距（像素）
HEALTH_BAR_BG_COLOR = (51, 51, 51)  # #333 血条背景颜色（深灰色）
HEALTH_BAR_BORDER_COLOR = (85, 85, 85)  # #555 血条边框颜色
HEALTH_BAR_FILL_COLOR = (85, 221, 85)  # #55dd55 血量条颜色（绿色）
HEALTH_BAR_SHADOW_COLOR = (85, 221, 85)  # #55dd55 外发光颜色
HEALTH_BAR_TEXT_COLOR = (187, 187, 187)  # #bbb 标签文字颜色
HEALTH_BAR_VALUE_COLOR = (26, 26, 26)  # #1a1a1a 数值文字颜色（深灰色）
HEALTH_BAR_BORDER_WIDTH = 3  # 血条边框宽度（像素）
HEALTH_BAR_PADDING = 3  # 血条内边距（像素）

# ==================== 灵火配置 ====================
MAX_SPIRIT_FIRE = 5  # 最大灵火值
SPIRIT_FIRE_BAR_HEIGHT = 35  # 灵火条高度（像素）
SPIRIT_FIRE_BAR_WIDTH = 200  # 灵火条固定宽度（像素）
SPIRIT_FIRE_BAR_Y = 20  # 灵火条距离画面上方（像素）
SPIRIT_FIRE_BAR_SPACING = 15  # 灵火条和生命条之间的间距（像素）
SPIRIT_FIRE_BAR_BG_COLOR = (51, 51, 51)  # #333 灵火条背景颜色（深灰色）
SPIRIT_FIRE_BAR_BORDER_COLOR = (85, 85, 85)  # #555 灵火条边框颜色
SPIRIT_FIRE_BAR_FILL_COLOR = (85, 170, 221)  # #55aadd 灵火条颜色（蓝色）
SPIRIT_FIRE_BAR_SHADOW_COLOR = (85, 170, 221)  # #55aadd 外发光颜色（蓝色）
SPIRIT_FIRE_BAR_TEXT_COLOR = (187, 187, 187)  # #bbb 标签文字颜色
SPIRIT_FIRE_BAR_VALUE_COLOR = (26, 26, 26)  # #1a1a1a 数值文字颜色（深灰色）
SPIRIT_FIRE_BAR_BORDER_WIDTH = 3  # 灵火条边框宽度（像素）
SPIRIT_FIRE_BAR_PADDING = 3  # 灵火条内边距（像素）

# ==================== 重置按钮配置 ====================
RESET_BUTTON_X = -1  # -1表示需要动态计算（画面右侧）
RESET_BUTTON_Y = 20  # 重置按钮距离画面上方（像素），与血条对齐
RESET_BUTTON_WIDTH = 80  # 重置按钮宽度（像素）
RESET_BUTTON_HEIGHT = 35  # 重置按钮高度（像素），与血条高度一致
RESET_BUTTON_TEXT = "重置"  # 重置按钮文本
RESET_BUTTON_BG_COLOR = (42, 42, 42)  # #2a2a2a 按钮背景颜色
RESET_BUTTON_BG_HOVER_COLOR = (58, 58, 58)  # #3a3a3a 按钮悬停背景颜色
RESET_BUTTON_BG_ACTIVE_COLOR = (26, 26, 26)  # #1a1a1a 按钮按下背景颜色
RESET_BUTTON_BORDER_COLOR = (85, 85, 85)  # #555 按钮边框颜色
RESET_BUTTON_BORDER_HOVER_COLOR = (102, 102, 102)  # #666 按钮悬停边框颜色
RESET_BUTTON_TEXT_COLOR = (187, 187, 187)  # #bbb 按钮文字颜色
RESET_BUTTON_BORDER_WIDTH = 2  # 按钮边框宽度（像素）
RESET_BUTTON_PADDING = (8, 18)  # 按钮内边距（垂直，水平）（像素）

# ==================== 勇士列表配置 ====================
WARRIOR_LIST_X = -1  # -1表示需要动态计算（画面右侧）
WARRIOR_LIST_Y = 70  # 勇士列表距离画面上方（像素）
WARRIOR_LIST_WIDTH = 240  # 勇士列表宽度（像素，已放大3倍：80*3）
WARRIOR_LIST_SLOT_SIZE = 108  # 勇士槽位大小（像素，已放大3倍：36*3）
WARRIOR_LIST_SLOT_GAP = 8  # 勇士槽位间距（像素，缩短）
WARRIOR_LIST_PADDING = 12  # 勇士列表内边距（像素，缩短）
WARRIOR_LIST_BG_COLOR = (26, 26, 26)  # #1a1a1a 勇士列表背景颜色
WARRIOR_LIST_BORDER_COLOR = (85, 85, 85)  # #555 勇士列表边框颜色
WARRIOR_LIST_TITLE_COLOR = (187, 187, 187)  # #bbb 勇士列表标题颜色
WARRIOR_LIST_SLOT_BG_COLOR = (26, 26, 26)  # #1a1a1a 勇士槽位背景颜色
WARRIOR_LIST_SLOT_BORDER_COLOR = (85, 85, 85)  # #555 勇士槽位边框颜色
WARRIOR_LIST_SLOT_TEXT_COLOR = (187, 187, 187)  # #bbb 勇士槽位文字颜色
WARRIOR_LIST_SLOT_HOVER_COLOR = (74, 158, 255)  # #4a9eff 勇士槽位悬停发光颜色
WARRIOR_LIST_BORDER_WIDTH = 1  # 勇士列表边框宽度（像素）
WARRIOR_SLOT_BORDER_WIDTH = 1  # 勇士槽位边框宽度（像素）
WARRIOR_LETTERS = ['1', '2', '3', '4', '5']  # 勇士数字列表

