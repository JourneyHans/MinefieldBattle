#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
魔法军团 - Python版
游戏主程序
"""

import pygame
import sys
import math
import random
import config
from collections import deque
from game_window import GameWindow
from draw_system import DrawSystem
from font_manager import FontManager

# ==================== 核心框架初始化 ====================
# 游戏窗口初始化
window = GameWindow()

# 字体管理器初始化
font_manager = FontManager()

# 绘制系统初始化
drawer = DrawSystem(window.screen)

# 棋盘背景内边距（居中显示）
PADDING_X = 0
PADDING_Y = 0

# 屏幕震动状态
screen_shake_active = False
screen_shake_start_time = 0
screen_shake_duration = 0
screen_shake_magnitude = 0
shake_offset_x = 0
shake_offset_y = 0

# 震动默认参数
DEFAULT_SHAKE_DURATION = 280  # 毫秒
DEFAULT_SHAKE_MAGNITUDE = 6

# 迷雾方块：使用set存储有迷雾方块的格子坐标 "row,col"
blocks = set()

# 标记的迷雾方块：使用set存储被标记的迷雾方块位置 "row,col"
marked_blocks = set()

# 动画状态：用于跟踪正在进行的扩散动画
reveal_animation = None
reveal_animation_data = None  # 存储动画数据：{'blocks_to_reveal': [], 'current_level': 0, 'last_frame_time': 0}

# 鼠标悬停状态：用于跟踪当前悬停的格子
hovered_cell = None  # (row, col) 或 None
hovered_board_warrior = None  # 棋盘上悬停的勇士方块，格式：(warrior_letter, block_key, warrior_rect) 或 None

# 生命值状态
current_hp = config.MAX_HP  # 当前生命值
current_spirit_fire = config.MAX_SPIRIT_FIRE  # 当前灵火值
spirit_fire_zero_pending = False  # 灵火归零待处理标志，如果为True表示灵火归零但等待检查是否有外来补充

# 游戏状态
is_game_over = False  # 游戏是否失败
is_game_won = False  # 玩家是否获胜（还未实现）

# 棋子地块层：危险地块、安全地块（包含治疗草和终点）
danger_land_blocks = set()  # 危险地块集合，存储格子坐标 "row,col"
safe_land_blocks = set()  # 安全地块集合，存储格子坐标 "row,col"（包含治疗草和终点）
safe_land_block_types = {}  # 安全地块类型字典，key为"row,col"，value为'heal'（治疗草）或'endpoint'（终点）
used_safe_land_blocks = set()  # 已使用的安全地块集合，存储格子坐标 "row,col"

# 暴露状态的危险地块（满足暴露条件但仍被迷雾覆盖）
exposed_danger_blocks = set()  # 暴露状态的危险地块集合，存储格子坐标 "row,col"
# 暴露状态的安全地块（满足暴露条件但仍被迷雾覆盖）
exposed_safe_blocks = set()  # 暴露状态的安全地块集合，存储格子坐标 "row,col"

# 怪物当前战力：存储每个怪物的当前战力，key为"row,col"，value为当前战力（整数）
monster_current_power = {}  # 怪物当前战力字典，如果怪物不在字典中，则使用初始战力

# 被发现提示：根据"被发现条件"自动标记的格子
discovered_hint_blocks = set()  # 被发现提示集合，存储格子坐标 "row,col"

# 勇士方块状态：使用字典存储勇士方块的位置，key为勇士字母(a-e)，value为格子坐标 "row,col"
warrior_blocks = []  # 勇士方块列表，存储(warrior_letter, block_key)元组，支持同名勇士方块

# 勇士方块牌库：存放所有可用的勇士方块
warrior_deck = []  # 勇士方块牌库，存储所有勇士方块的标识（如'1', '2', '3', '4', '5'）

# 起始区域（6个相连格子）
start_area = []

# 勇士拖拽目标高亮
warrior_drop_target = None

# 可用牌组按钮的全局引用（用于访问弃牌堆）
available_deck_button_global = None

# 常用字体（优先支持中文）
CJK_FONT_PREFERENCES = [
    'Microsoft YaHei',
    'SimHei',
    'PingFang SC',
    'Noto Sans CJK SC',
    'Source Han Sans SC',
    'Microsoft JhengHei',
    '微软雅黑',
    '黑体',
    'Arial Unicode MS',
    'Courier New',
    'Courier',
    'monospace',
]


def get_font_with_fallback(size, bold=False):
    """尝试加载支持中文的字体"""
    for font_name in CJK_FONT_PREFERENCES:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            test_surface = font.render('测试Aa123', True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except (OSError, pygame.error, AttributeError):
            # 字体加载失败或不可用
            continue
    return pygame.font.Font(None, size)

# 统计信息
total_piece_count = 0
total_danger_count = 0
total_safe_count = 0


def start_screen_shake(magnitude=DEFAULT_SHAKE_MAGNITUDE, duration=DEFAULT_SHAKE_DURATION):
    """启动屏幕震动效果"""
    global screen_shake_active, screen_shake_start_time, screen_shake_duration, screen_shake_magnitude
    screen_shake_active = True
    screen_shake_start_time = pygame.time.get_ticks()
    screen_shake_duration = duration
    screen_shake_magnitude = magnitude


def stop_screen_shake():
    """立即停止屏幕震动"""
    global screen_shake_active, shake_offset_x, shake_offset_y
    screen_shake_active = False
    shake_offset_x = 0
    shake_offset_y = 0


def update_screen_shake():
    """根据时间更新震动偏移"""
    global shake_offset_x, shake_offset_y
    if not screen_shake_active:
        shake_offset_x = 0
        shake_offset_y = 0
        return

    current_time = pygame.time.get_ticks()
    elapsed = current_time - screen_shake_start_time

    if elapsed >= screen_shake_duration:
        stop_screen_shake()
        return

    decay = 1 - (elapsed / screen_shake_duration)
    magnitude = screen_shake_magnitude * decay
    shake_offset_x = random.uniform(-1, 1) * magnitude
    shake_offset_y = random.uniform(-1, 1) * magnitude


def get_padding_values():
    """返回包含震动偏移的浮点内边距"""
    return PADDING_X + shake_offset_x, PADDING_Y + shake_offset_y


def get_padding_int():
    """返回包含震动偏移的整数内边距"""
    px, py = get_padding_values()
    return int(px), int(py)


def select_start_area():
    """随机选择6个相连格子的起始区域"""
    shapes = [
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],  # 2x3矩形
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],  # 3x2矩形
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0)],  # L形
        [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (2, 2)],  # L形镜像
        [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1), (3, 1)],  # T形
        [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2), (1, 3)],  # T形旋转
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],  # 水平直线
        [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],  # 垂直直线
        [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 3)],  # 阶梯
        [(0, 2), (0, 3), (1, 1), (1, 2), (2, 0), (2, 1)],  # 阶梯镜像
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (3, 0)],  # 小L
        [(0, 1), (0, 2), (1, 1), (1, 2), (2, 2), (3, 2)],  # 小L镜像
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (3, 1)],  # 十字
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],  # 方块+延伸
        [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (1, 2)]   # 方块+延伸（横向）
    ]

    shape = random.choice(shapes)

    # 随机水平翻转
    if random.random() < 0.5:
        max_col = max(c for _, c in shape)
        shape = [(r, max_col - c) for r, c in shape]

    # 随机垂直翻转
    if random.random() < 0.5:
        max_row = max(r for r, _ in shape)
        shape = [(max_row - r, c) for r, c in shape]

    # 如果形状超过棋盘，回退为简单矩形
    shape_rows = max(r for r, _ in shape) + 1
    shape_cols = max(c for _, c in shape) + 1
    if shape_rows > config.GRID_ROWS or shape_cols > config.GRID_COLS:
        shape = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        shape_rows = 2
        shape_cols = 3

    max_row = max(0, config.GRID_ROWS - shape_rows)
    max_col = max(0, config.GRID_COLS - shape_cols)
    start_row = random.randint(0, max_row) if max_row > 0 else 0
    start_col = random.randint(0, max_col) if max_col > 0 else 0

    area = []
    for r, c in shape:
        absolute_row = start_row + r
        absolute_col = start_col + c
        if 0 <= absolute_row < config.GRID_ROWS and 0 <= absolute_col < config.GRID_COLS:
            area.append((absolute_row, absolute_col))
    return area


def open_start_area_blocks():
    """移除起始区域的迷雾方块"""
    for row, col in start_area:
        block_key = f"{row},{col}"
        blocks.discard(block_key)
        marked_blocks.discard(block_key)


def is_valid_warrior_drop(block_key):
    """判断勇士是否可以放置在指定格子"""
    if block_key in blocks:
        return False
    if block_key in danger_land_blocks:
        return False
    return True

class ResolutionSelector:
    """分辨率选择器UI组件"""
    def __init__(self, x, y, font):
        self.x = x
        self.y = y
        self.font = font  # 保存字体引用
        self.options = ['1440x810', '1280x720', '1024x768']
        self.current = 0
        self.open = False
        self.hover_index = -1
        
        # 计算尺寸
        self.label_text = "画面大小："
        self.label_surface = self.font.render(self.label_text, True, config.UI_TEXT_COLOR)
        self.label_rect = self.label_surface.get_rect(topleft=(x, y))
        
        # 按钮尺寸
        self.button_width = config.RESOLUTION_BUTTON_WIDTH
        self.button_height = config.RESOLUTION_BUTTON_HEIGHT
        self.button_x = x + self.label_rect.width + 10
        self.button_y = y
        
        # 选项框尺寸
        self.option_height = config.RESOLUTION_OPTION_HEIGHT
        self.options_box_width = self.button_width

    def get_bottom(self):
        """返回组件底部位置"""
        element_height = max(self.button_height, self.label_rect.height)
        return self.y + element_height

    def get_reserved_height(self):
        """返回为防止遮挡需要预留的高度"""
        element_height = max(self.button_height, self.label_rect.height)
        dropdown_height = self.option_height * len(self.options)
        return element_height + dropdown_height
    
    def get_current_text(self):
        """获取当前选项的显示文本"""
        res = config.RESOLUTIONS[self.options[self.current]]
        return f"{res['width']} x {res['height']}"
    
    def handle_event(self, event):
        """处理事件"""
        global PADDING_X, PADDING_Y
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 检查是否点击了按钮
                button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
                if button_rect.collidepoint(mouse_pos):
                    self.open = not self.open
                elif self.open:
                    # 检查是否点击了选项
                    for i, option_key in enumerate(self.options):
                        option_y = self.button_y + self.button_height + i * self.option_height
                        option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                        if option_rect.collidepoint(mouse_pos):
                            if i != self.current:
                                self.current = i
                                # 更新窗口大小
                                if window.resize(option_key):
                                    # 更新棋盘背景内边距
                                    update_padding()
                            self.open = False
                            return True
                    # 点击了外部，关闭下拉菜单
                    self.open = False
                else:
                    # 点击了外部，关闭下拉菜单
                    self.open = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.open:
                self.hover_index = -1
                for i in range(len(self.options)):
                    option_y = self.button_y + self.button_height + i * self.option_height
                    option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                    if option_rect.collidepoint(mouse_pos):
                        self.hover_index = i
                        break
        
        return False
    
    def draw(self, surface):
        """绘制组件"""
        global total_piece_count, total_danger_count, total_safe_count
        # 绘制标签
        surface.blit(self.label_surface, self.label_rect)
        
        # 绘制按钮
        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos) and not self.open
        
        # 按钮背景色
        bg_color = config.UI_BG_HOVER_COLOR if is_hover else config.UI_BG_COLOR
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # 按钮边框
        border_color = config.UI_BORDER_FOCUS_COLOR if self.open else config.UI_BORDER_COLOR
        pygame.draw.rect(surface, border_color, button_rect, 1)
        
        # 按钮文字
        button_text = self.get_current_text()
        text_surface = self.font.render(button_text, True, config.UI_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # 绘制下拉选项
        if self.open:
            for i, option_key in enumerate(self.options):
                option_y = self.button_y + self.button_height + i * self.option_height
                option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                
                # 选项背景色
                if i == self.hover_index:
                    option_bg_color = config.UI_BG_HOVER_COLOR
                else:
                    option_bg_color = config.UI_BG_COLOR
                
                pygame.draw.rect(surface, option_bg_color, option_rect)
                
                # 选项边框
                pygame.draw.rect(surface, config.UI_BORDER_COLOR, option_rect, 1)
                
                # 选项文字
                res = config.RESOLUTIONS[option_key]
                option_text = f"{res['width']} x {res['height']}"
                option_text_surface = self.font.render(option_text, True, config.UI_TEXT_COLOR)
                option_text_rect = option_text_surface.get_rect(center=option_rect.center)
                surface.blit(option_text_surface, option_text_rect)

class DifficultySelector:
    """地图大小选择器UI组件"""
    def __init__(self, font):
        self.font = font  # 保存字体引用
        self.options = ['easy', 'normal', 'hard']  # 难度选项
        self.current = 0  # 默认选择easy（9×9）
        self.open = False
        self.hover_index = -1
        
        # 标签文本
        self.label_text = "地图大小："
        self.label_surface = self.font.render(self.label_text, True, config.UI_TEXT_COLOR)
        
        # 按钮尺寸
        self.button_width = config.DIFFICULTY_BUTTON_WIDTH
        self.button_height = config.DIFFICULTY_BUTTON_HEIGHT
        self.option_height = config.DIFFICULTY_OPTION_HEIGHT
        self.options_box_width = self.button_width
        
        # 位置（右上角，需要动态计算）
        self.x = 0
        self.y = config.DIFFICULTY_SELECTOR_Y
        self.position_manual = False  # 标记位置是否被手动设置
        self.update_position()

    def set_position(self, x=None, y=None, manual=True):
        """外部设置位置（x为None时使用右上角对齐，y为None时保持当前位置）
        
        Args:
            x: x坐标，None时使用右上角对齐
            y: y坐标，None时保持当前位置
            manual: 是否为手动设置，True表示手动设置，False表示自动设置
        """
        self.position_manual = manual  # 标记位置设置方式
        if y is not None:
            self.y = y
        if x is not None:
            self.x = x
        elif x is None:
            # 如果没有提供x，使用右上角对齐
            window_width, _ = window.get_size()
            label_width = self.label_surface.get_width()
            total_width = label_width + 10 + self.button_width
            self.x = window_width - total_width - 15  # 距离右边15像素
        
        # 计算标签和按钮位置
        self.label_rect = self.label_surface.get_rect(topleft=(self.x, self.y))
        self.button_x = self.x + self.label_rect.width + 10
        self.button_y = self.y
    
    def set_top(self, y):
        """外部设置顶部位置"""
        self.set_position(y=y, manual=True)
    
    def update_position(self):
        """更新位置（右上角对齐，自动设置）"""
        self.set_position(manual=False)
    
    def get_current_text(self):
        """获取当前选项的显示文本"""
        return config.DIFFICULTIES[self.options[self.current]]['display']
    
    def handle_event(self, event):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 检查是否点击了按钮
                button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
                if button_rect.collidepoint(mouse_pos):
                    self.open = not self.open
                elif self.open:
                    # 检查是否点击了选项
                    for i, option_key in enumerate(self.options):
                        option_y = self.button_y + self.button_height + i * self.option_height
                        option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                        if option_rect.collidepoint(mouse_pos):
                            if i != self.current:
                                self.current = i
                                # 更新难度和网格大小
                                self.update_difficulty()
                            self.open = False
                            return True
                    # 点击了外部，关闭下拉菜单
                    self.open = False
                else:
                    # 点击了外部，关闭下拉菜单
                    self.open = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.open:
                self.hover_index = -1
                for i in range(len(self.options)):
                    option_y = self.button_y + self.button_height + i * self.option_height
                    option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                    if option_rect.collidepoint(mouse_pos):
                        self.hover_index = i
                        break
        
        return False
    
    def update_difficulty(self):
        """更新难度和网格大小"""
        global blocks, marked_blocks, safe_land_blocks, safe_land_block_types, used_safe_land_blocks, warrior_blocks, warrior_deck, start_area, discovered_hint_blocks, warrior_drop_target
        
        # 获取当前难度
        difficulty_key = self.options[self.current]
        difficulty_info = config.DIFFICULTIES[difficulty_key]
        
        # 更新网格大小
        config.GRID_ROWS = difficulty_info['rows']
        config.GRID_COLS = difficulty_info['cols']
        
        # 更新格子大小（9×9地图放大30%）
        config.CELL_SIZE = config.get_cell_size(difficulty_key)
        
        # 重新初始化迷雾方块（先初始化所有格子都有迷雾，包括危险格子和安全格子）
        initialize_blocks()
        marked_blocks.clear()
        discovered_hint_blocks.clear()
        
        # 清除已使用的安全地块
        used_safe_land_blocks.clear()
        
        # 清除安全地块（包含终点）
        safe_land_blocks.clear()
        safe_land_block_types.clear()
        
        # 清除勇士方块
        warrior_blocks.clear()
        warrior_drop_target = None
        
        # 初始化勇士方块牌库（将所有勇士方块放入牌库）
        global warrior_deck
        warrior_deck = list(config.WARRIOR_LETTERS.copy())  # 复制配置中的勇士列表到牌库
        
        # 重新初始化棋子地块（危险地块等）
        # 注意：这些地块部署在迷雾覆盖的格子上，不会被立即显示
        # 只有当玩家点击打开迷雾时，才会看到这些地块
        initialize_piece_land_blocks(difficulty_key)
        
        # 打开起始区域
        open_start_area_blocks()
        
        # 重置生命值
        global current_hp, current_spirit_fire, spirit_fire_zero_pending
        current_hp = config.MAX_HP
        current_spirit_fire = config.MAX_SPIRIT_FIRE
        spirit_fire_zero_pending = False
        
        # 更新棋盘背景内边距
        update_padding()
        
        # 不在这里更新位置，位置由GameLoop.draw()管理
        # 如果位置是手动设置的，保持它；否则会在draw()中自动更新
    
    def draw(self, surface):
        """绘制组件"""
        # 更新位置（如果窗口大小改变且位置未被手动设置）
        if not self.position_manual:
            window_width, window_height = window.get_size()
            label_width = self.label_surface.get_width()
            total_width = label_width + 10 + self.button_width
            if self.x != window_width - total_width - 15:
                self.update_position()
        else:
            # 如果位置被手动设置，只更新内部坐标（label_rect等）
            self.label_rect = self.label_surface.get_rect(topleft=(self.x, self.y))
            self.button_x = self.x + self.label_rect.width + 10
            self.button_y = self.y
        
        # 绘制标签
        surface.blit(self.label_surface, self.label_rect)
        
        # 绘制按钮
        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos) and not self.open
        
        # 按钮背景色
        bg_color = config.UI_BG_HOVER_COLOR if is_hover else config.UI_BG_COLOR
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # 按钮边框
        border_color = config.UI_BORDER_FOCUS_COLOR if self.open else config.UI_BORDER_COLOR
        pygame.draw.rect(surface, border_color, button_rect, 1)
        
        # 按钮文字
        button_text = self.get_current_text()
        text_surface = self.font.render(button_text, True, config.UI_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # 绘制下拉选项
        if self.open:
            for i, option_key in enumerate(self.options):
                option_y = self.button_y + self.button_height + i * self.option_height
                option_rect = pygame.Rect(self.button_x, option_y, self.options_box_width, self.option_height)
                
                # 选项背景色
                if i == self.hover_index:
                    option_bg_color = config.UI_BG_HOVER_COLOR
                else:
                    option_bg_color = config.UI_BG_COLOR
                
                pygame.draw.rect(surface, option_bg_color, option_rect)
                
                # 选项边框
                pygame.draw.rect(surface, config.UI_BORDER_COLOR, option_rect, 1)
                
                # 选项文字
                option_text = config.DIFFICULTIES[option_key]['display']
                option_text_surface = self.font.render(option_text, True, config.UI_TEXT_COLOR)
                option_text_rect = option_text_surface.get_rect(center=option_rect.center)
                surface.blit(option_text_surface, option_text_rect)

class ResetButton:
    """重置按钮UI组件"""
    def __init__(self, font, game_loop_ref=None):
        self.font = font
        self.title_font = font_manager.get_large()
        self.text = config.RESET_BUTTON_TEXT
        self.width = config.RESET_BUTTON_WIDTH
        self.height = config.RESET_BUTTON_HEIGHT
        self.x = config.RESET_BUTTON_X  # 初始值，会在draw时动态计算
        self.y = config.RESET_BUTTON_Y
        self.pressed = False
        self.game_loop_ref = game_loop_ref  # 引用GameLoop实例，用于获取当前难度
        
    def update_position(self, x, y):
        """更新按钮位置"""
        self.x = x
        self.y = y
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if button_rect.collidepoint(mouse_pos):
                    self.pressed = True
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                if self.pressed:
                    self.pressed = False
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    if button_rect.collidepoint(mouse_pos):
                        # 触发重置游戏（获取当前难度）
                        difficulty_key = None
                        if self.game_loop_ref:
                            difficulty_key = self.game_loop_ref.difficulty_selector.options[self.game_loop_ref.difficulty_selector.current]
                        reset_game(difficulty_key, self.game_loop_ref)
                        
                        return True
                    self.pressed = False
        
        return False
    
    def draw(self, surface):
        """绘制组件"""
        window_width, window_height = window.get_size()
        
        # 统计信息面板高度和宽度（与 draw_game_stats 中保持一致）
        stats_padding = 12
        stats_line_height = 18
        stats_lines = [
            '地块信息统计',
            f'棋子地块：{total_piece_count}',
            f'危险地块：{total_danger_count}',
            f'安全地块：{total_safe_count}'
        ]
        stats_box_height = stats_line_height * len(stats_lines) + stats_padding * 2
        
        # 计算统计信息框的宽度
        stats_font = get_font_with_fallback(14)
        stats_width = 0
        for line in stats_lines:
            text_surface = stats_font.render(line, True, (255, 255, 255))
            stats_width = max(stats_width, text_surface.get_width())
        stats_box_width = stats_width + stats_padding * 2
        
        # 统计信息的顶部位置和左侧位置
        stats_top = window_height - stats_box_height - 12
        stats_left = 12
        
        # 统计信息框的中心x坐标
        stats_center_x = stats_left + stats_box_width / 2
        
        # 重置按钮位置：与统计信息居中对齐，位于统计信息上方
        button_x = stats_center_x - self.width / 2  # 按钮中心对齐到统计信息框中心
        button_y = stats_top - self.height - 8  # 留8px 间距
        
        # 如果统计信息不显示（total_piece_count <= 0），则放在底部左侧
        if total_piece_count <= 0:
            button_x = 12
            button_y = window_height - self.height - 12
        
        # 更新位置
        self.update_position(button_x, button_y)
        
        # 按钮矩形
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)
        
        # 按钮背景色
        if self.pressed:
            bg_color = config.RESET_BUTTON_BG_ACTIVE_COLOR
        elif is_hover:
            bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
        else:
            bg_color = config.RESET_BUTTON_BG_COLOR
        
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # 按钮边框
        border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR if is_hover else config.RESET_BUTTON_BORDER_COLOR
        pygame.draw.rect(surface, border_color, button_rect, config.RESET_BUTTON_BORDER_WIDTH)
        
        # 按钮文字（居中显示）
        text_surface = self.font.render(self.text, True, config.RESET_BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)

class WarriorList:
    """勇士列表UI组件"""
    def __init__(self, font, available_deck_button=None):
        self.font = font
        self.title_font = font_manager.get_large()
        self.title_font = font  # 标题字体（恢复原大小）
        self.width = config.WARRIOR_LIST_WIDTH
        self.x = config.WARRIOR_LIST_X  # 初始值，会在draw时动态计算
        self.y = config.WARRIOR_LIST_Y
        self.slot_size = config.WARRIOR_LIST_SLOT_SIZE
        self.slot_gap = config.WARRIOR_LIST_SLOT_GAP
        self.padding = config.WARRIOR_LIST_PADDING
        # 勇士列表从牌库中获取可用的勇士方块（已放置的勇士方块不在列表中显示）
        # 注意：warrior_letters会在draw方法中动态更新，从牌库中获取未放置的勇士方块
        self.warrior_letters = []  # 初始为空，会在draw方法中动态更新
        self.available_deck_button = available_deck_button  # 可用牌组按钮的引用
        self.drawn_cards = []
        self.hovered_card = None  # 记录当前悬停的勇士卡牌（用于绘制提示框）  # 抽取的卡牌列表（存储在卡牌槽位中）
        
        # 计算列表高度（使用配置中的最大勇士数量，因为牌库大小可能变化）
        # 标题高度 + 间距 + 槽位数量 * (槽位大小 + 间距) - 最后一个间距 + 内边距
        title_height = self.title_font.get_height()
        max_warriors = len(config.WARRIOR_LETTERS)  # 使用配置中的最大数量
        self.height = self.padding * 2 + title_height + self.slot_gap + \
                     max_warriors * (self.slot_size + self.slot_gap) - self.slot_gap
        
        # 拖拽状态
        self.is_dragging = False  # 是否正在拖拽
        self.dragging_letter = None  # 正在拖拽的勇士字母
        self.dragging_start_pos = None  # 拖拽开始时的鼠标位置
        self.dragging_slot_pos = None  # 拖拽开始时的槽位位置
        self.dragging_card_index = None  # 正在拖拽的卡牌在drawn_cards中的索引
        
        # 抽取勇士按钮状态
        self.draw_button_hover = False  # 按钮是否悬停
        
        # 抽取勇士计数器
        self.draw_counter_value = "1"  # 默认值为1
        self.draw_counter_active = False  # 计数器输入框是否激活
        self.draw_counter_input_rect = None  # 输入框矩形
        self.draw_counter_left_rect = None  # 左减按钮矩形
        self.draw_counter_right_rect = None  # 右加按钮矩形
        
        # 卡牌槽位按钮状态
        self.slot_button_hover = False  # 按钮是否悬停
        
        # 卡牌槽位计数器
        self.slot_counter_value = "8"  # 默认值为8
        self.slot_counter_active = False  # 计数器输入框是否激活
        self.slot_counter_input_rect = None  # 输入框矩形
        self.slot_counter_left_rect = None  # 左减按钮矩形
        self.slot_counter_right_rect = None  # 右加按钮矩形
        
        # 撤回勇士按钮状态
        self.undo_button_hover = False  # 按钮是否悬停
        self.undo_button_enabled = False  # 按钮是否可用（点亮状态）
        self.last_placed_warrior = None  # 最后一次放置的勇士信息 (warrior_letter, block_key, card_name)，用于撤回功能
        
    def update_position(self, x, y):
        """更新列表位置"""
        self.x = x
        self.y = y
    
    def draw(self, surface):
        """绘制组件"""
        # 使用棋盘格子大小作为勇士方块大小
        slot_size = config.CELL_SIZE
        
        # 更新位置（如果窗口大小改变）
        window_width, window_height = window.get_size()
        
        # 计算勇士列表位置（画面右侧）
        list_x = window_width - self.width - 15  # 距离右边缘15像素
        list_y = self.y
        
        # 更新位置
        self.update_position(list_x, list_y)
        
        # 检查最后放置的勇士是否还在棋盘上，如果不在则禁用撤回按钮
        if self.undo_button_enabled and self.last_placed_warrior:
            warrior_letter, block_key, _ = self.last_placed_warrior
            # 检查这个特定位置的勇士是否还在棋盘上（战斗后会被移除，不能撤回）
            global warrior_blocks
            warrior_still_on_board = any(w == warrior_letter and p == block_key for w, p in warrior_blocks)
            if not warrior_still_on_board:
                # 勇士已不在棋盘上（可能因战斗被移除），禁用撤回按钮
                self.last_placed_warrior = None
                self.undo_button_enabled = False
        
        # 计算重置按钮的底部位置，使背景框延伸到同一水平位置
        # 统计信息面板参数（与 ResetButton.draw 和 draw_game_stats 中保持一致）
        global total_piece_count, total_danger_count, total_safe_count
        stats_padding = 12
        stats_line_height = 18
        stats_lines = [
            '地块信息统计',
            f'棋子地块：{total_piece_count}',
            f'危险地块：{total_danger_count}',
            f'安全地块：{total_safe_count}'
        ]
        stats_box_height = stats_line_height * len(stats_lines) + stats_padding * 2
        
        # 计算重置按钮底部位置（与 ResetButton.draw 中的逻辑一致）
        # stats_top = window_height - stats_box_height - 12
        # button_y = stats_top - self.height - 8
        # 重置按钮底部 = button_y + self.height = stats_top - 8 = window_height - stats_box_height - 12 - 8
        if total_piece_count > 0:
            reset_button_bottom = window_height - stats_box_height - 12 - 8
        else:
            # 如果统计信息不显示，重置按钮在底部
            # button_y = window_height - RESET_BUTTON_HEIGHT - 12
            # 重置按钮底部 = button_y + RESET_BUTTON_HEIGHT = window_height - 12
            reset_button_bottom = window_height - 12
        
        # 计算背景框高度：从勇士列表顶部延伸到重置按钮底部
        target_height = max(reset_button_bottom - self.y, 0)  # 确保不为负数
        
        # 确保高度不小于内容高度
        title_height = self.title_font.get_height()
        content_height = self.padding * 2 + title_height + self.slot_gap + \
                        len(self.warrior_letters) * (slot_size + self.slot_gap) - self.slot_gap
        calculated_height = max(target_height, content_height)
        
        # 如果高度超出画面，限制高度
        max_height = window_height - self.y - 15  # 距离底部15像素
        self.height = min(calculated_height, max_height)
        
        # 绘制列表背景
        list_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, config.WARRIOR_LIST_BG_COLOR, list_rect)
        pygame.draw.rect(surface, config.WARRIOR_LIST_BORDER_COLOR, list_rect, config.WARRIOR_LIST_BORDER_WIDTH)
        
        # 绘制标题"勇士列表"
        title_text = "勇士列表"
        title_surface = self.title_font.render(title_text, True, config.WARRIOR_LIST_TITLE_COLOR)
        title_rect = title_surface.get_rect()
        title_x = self.x + (self.width - title_rect.width) // 2  # 居中
        title_y = self.y + self.padding
        surface.blit(title_surface, (title_x, title_y))
        
        # 标题下方卡牌槽位（显示抽取的卡牌）
        sample_size = config.CELL_SIZE
        sample_color = tuple(max(0, c - 10) for c in config.WARRIOR_LIST_SLOT_BG_COLOR)
        available_width = self.width - self.padding * 2 - sample_size * 4
        sample_spacing = available_width / 3 if available_width > 0 else 8
        # 增加卡牌槽位与标题之间的间距
        card_slot_top_margin = 20  # 额外的顶部间距
        sample_start_y = title_y + title_rect.height + self.slot_gap + card_slot_top_margin
        
        # 在标题和卡牌槽位之间绘制装饰线（居中位置）
        title_bottom = title_y + title_rect.height
        gap_total = self.slot_gap + card_slot_top_margin
        decoration_line_y = title_bottom + gap_total / 2
        decoration_line_x_start = self.x + self.padding
        decoration_line_x_end = self.x + self.width - self.padding
        # 使用不太白的颜色（深灰色）
        decoration_line_color = (60, 60, 60)  # 比边框颜色稍暗
        pygame.draw.line(surface, decoration_line_color, 
                        (decoration_line_x_start, int(decoration_line_y)),
                        (decoration_line_x_end, int(decoration_line_y)), 1)
        row_spacing = 10
        mouse_pos = pygame.mouse.get_pos()
        
        # 初始化悬停状态（在检查之前先重置）
        self.hovered_card = None
        
        # 获取当前槽位数量（从计数器获取）
        try:
            max_slots = int(self.slot_counter_value or "8")
        except ValueError:
            max_slots = 8
        max_slots = max(0, max_slots)  # 确保不为负数
        
        # 限制drawn_cards数量不超过槽位数量（多余的卡牌会在减少槽位时放入弃牌堆）
        if len(self.drawn_cards) > max_slots:
            # 将多余的卡牌放入弃牌堆
            excess_cards = self.drawn_cards[max_slots:]
            if self.available_deck_button and excess_cards:
                for card in excess_cards:
                    self.available_deck_button.discard_cards.append(card)
            # 移除多余的卡牌
            self.drawn_cards = self.drawn_cards[:max_slots]
        
        # 计算需要多少行（每4个一行）
        cols_per_row = 4
        total_rows = (max_slots + cols_per_row - 1) // cols_per_row  # 向上取整
        
        # 绘制动态数量的卡牌槽位（从左往右，每四个换一行）
        for row in range(total_rows):
            sample_y = sample_start_y + row * (sample_size + row_spacing)
            for col in range(cols_per_row):
                slot_index = row * cols_per_row + col
                
                # 如果超过最大槽位数，停止绘制
                if slot_index >= max_slots:
                    break
                
                sample_x = self.x + self.padding + col * (sample_size + sample_spacing)
                sample_rect = pygame.Rect(int(sample_x), sample_y, sample_size, sample_size)
                
                # 如果有卡牌，显示卡牌；否则显示空槽位
                if slot_index < len(self.drawn_cards):
                    card_name = self.drawn_cards[slot_index]
                    # 从 "步兵_1" 中提取 "1"
                    if card_name.startswith("步兵_"):
                        warrior_id = card_name.replace("步兵_", "")
                    else:
                        warrior_id = card_name
                    
                    # 绘制卡牌背景
                    is_hover = sample_rect.collidepoint(mouse_pos)
                    if is_hover:
                        # 记录悬停的卡牌（使用 copy() 确保 rect 不会改变）
                        self.hovered_card = (sample_rect.copy(), warrior_id)
                    
                    pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BG_COLOR, sample_rect)
                    border_color = config.WARRIOR_LIST_SLOT_HOVER_COLOR if is_hover else config.WARRIOR_LIST_SLOT_BORDER_COLOR
                    pygame.draw.rect(surface, border_color, sample_rect, config.WARRIOR_SLOT_BORDER_WIDTH)
                    
                    # 绘制勇士数字
                    warrior_font = get_font_with_fallback(int(sample_size * 0.5))
                    letter_surface = warrior_font.render(warrior_id, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
                    letter_rect = letter_surface.get_rect(center=sample_rect.center)
                    surface.blit(letter_surface, letter_rect)
                else:
                    # 绘制空槽位
                    pygame.draw.rect(surface, sample_color, sample_rect)
        
        # 边框已移除，保留纯色示例方块
        
        # 勇士槽位已移除，保留框体和按钮
        
        # 按钮尺寸
        button_height = 35  # 与重置按钮高度一致
        button_width = self.width - self.padding * 2  # 按钮宽度（列表宽度减去左右内边距）
        button_x = self.x + self.padding
        button_spacing = 8  # 两个按钮之间的间距
        
        # 绘制"卡牌槽位"按钮（在最上方）
        # 三个按钮：卡牌槽位（上）、撤回勇士（中）、抽取勇士（下）
        # 计算"抽取勇士"按钮位置（最下方）
        draw_button_y = self.y + self.height - button_height - self.padding
        # "撤回勇士"按钮在"抽取勇士"按钮上方，间距为button_spacing
        undo_button_y = draw_button_y - button_height - button_spacing
        # "卡牌槽位"按钮在"撤回勇士"按钮上方，间距为button_spacing
        slot_button_y = undo_button_y - button_height - button_spacing
        
        # 检查按钮是否在列表范围内
        if slot_button_y >= self.y + self.padding:
            # 绘制按钮
            slot_button_rect = pygame.Rect(button_x, slot_button_y, button_width, button_height)
            
            # 检查鼠标悬停
            self.slot_button_hover = slot_button_rect.collidepoint(mouse_pos)
            
            # 绘制按钮背景
            if self.slot_button_hover:
                bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
                border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR
            else:
                bg_color = config.RESET_BUTTON_BG_COLOR
                border_color = config.RESET_BUTTON_BORDER_COLOR
            
            pygame.draw.rect(surface, bg_color, slot_button_rect)
            pygame.draw.rect(surface, border_color, slot_button_rect, config.RESET_BUTTON_BORDER_WIDTH)
            
            # 按钮内布局：左侧文字，右侧计数器
            button_padding = 8
            text_left_padding = 12
            
            # 绘制按钮文字（左侧）
            slot_button_text = "卡牌槽位"
            text_surface = self.font.render(slot_button_text, True, config.RESET_BUTTON_TEXT_COLOR)
            text_x = slot_button_rect.x + text_left_padding
            text_y = slot_button_rect.centery - text_surface.get_height() // 2
            surface.blit(text_surface, (text_x, text_y))
            
            # 绘制计数器（右侧）
            counter_width = 80  # 计数器区域宽度
            counter_height = 24  # 计数器高度
            counter_x = slot_button_rect.right - counter_width - button_padding
            counter_y = slot_button_rect.centery - counter_height // 2
            
            # 输入框
            input_width = 40
            input_height = counter_height
            input_x = counter_x + (counter_width - input_width) // 2
            input_y = counter_y
            input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
            self.slot_counter_input_rect = input_rect
            
            # 绘制输入框背景
            input_bg_color = config.WARRIOR_LIST_BG_COLOR if not self.slot_counter_active else (40, 40, 40)
            pygame.draw.rect(surface, input_bg_color, input_rect)
            pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, input_rect, 1)
            
            # 绘制计数器值
            display_value = self.slot_counter_value if self.slot_counter_value else "0"
            if display_value == "":
                display_value = "0"
            value_color = (90, 90, 90) if display_value == "0" else config.RESET_BUTTON_TEXT_COLOR
            counter_font = get_font_with_fallback(16)
            value_surface = counter_font.render(display_value, True, value_color)
            value_rect = value_surface.get_rect(center=input_rect.center)
            surface.blit(value_surface, value_rect)
            
            # 左右按钮
            button_size = 20
            button_spacing = 4
            left_rect = pygame.Rect(
                input_rect.x - button_size - button_spacing,
                input_rect.centery - button_size // 2,
                button_size,
                button_size
            )
            right_rect = pygame.Rect(
                input_rect.right + button_spacing,
                input_rect.centery - button_size // 2,
                button_size,
                button_size
            )
            self.slot_counter_left_rect = left_rect
            self.slot_counter_right_rect = right_rect
            
            # 绘制左减按钮
            left_bg = config.WARRIOR_LIST_SLOT_BG_COLOR
            if left_rect.collidepoint(mouse_pos):
                left_bg = (40, 40, 40)
            pygame.draw.rect(surface, left_bg, left_rect)
            pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, left_rect, 1)
            # 绘制减号
            minus_color = (90, 90, 90) if display_value == "0" else config.WARRIOR_LIST_SLOT_TEXT_COLOR
            pygame.draw.line(surface, minus_color, 
                           (left_rect.centerx - 5, left_rect.centery),
                           (left_rect.centerx + 5, left_rect.centery), 2)
            
            # 绘制右加按钮
            right_bg = config.WARRIOR_LIST_SLOT_BG_COLOR
            if right_rect.collidepoint(mouse_pos):
                right_bg = (40, 40, 40)
            pygame.draw.rect(surface, right_bg, right_rect)
            pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, right_rect, 1)
            # 绘制加号
            pygame.draw.line(surface, config.WARRIOR_LIST_SLOT_TEXT_COLOR,
                           (right_rect.centerx - 5, right_rect.centery),
                           (right_rect.centerx + 5, right_rect.centery), 2)
            pygame.draw.line(surface, config.WARRIOR_LIST_SLOT_TEXT_COLOR,
                           (right_rect.centerx, right_rect.centery - 5),
                           (right_rect.centerx, right_rect.centery + 5), 2)
        
        # 绘制"撤回勇士"按钮（在"卡牌槽位"和"抽取勇士"按钮之间）
        # undo_button_y已在上面计算
        
        # 检查按钮是否在列表范围内
        if undo_button_y >= self.y + self.padding:
            # 绘制按钮
            undo_button_rect = pygame.Rect(button_x, undo_button_y, button_width, button_height)
            
            # 检查鼠标悬停（只有在按钮可用时才响应悬停）
            if self.undo_button_enabled:
                self.undo_button_hover = undo_button_rect.collidepoint(mouse_pos)
            else:
                self.undo_button_hover = False
            
            # 绘制按钮背景（根据可用状态调整颜色）
            if self.undo_button_enabled:
                if self.undo_button_hover:
                    bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
                    border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR
                    text_color = config.RESET_BUTTON_TEXT_COLOR
                else:
                    bg_color = config.RESET_BUTTON_BG_COLOR
                    border_color = config.RESET_BUTTON_BORDER_COLOR
                    text_color = config.RESET_BUTTON_TEXT_COLOR
            else:
                # 按钮不可用时的暗色状态
                bg_color = tuple(max(0, c - 40) for c in config.RESET_BUTTON_BG_COLOR)
                border_color = tuple(max(0, c - 40) for c in config.RESET_BUTTON_BORDER_COLOR)
                text_color = tuple(max(0, c - 60) for c in config.RESET_BUTTON_TEXT_COLOR)
            
            pygame.draw.rect(surface, bg_color, undo_button_rect)
            pygame.draw.rect(surface, border_color, undo_button_rect, config.RESET_BUTTON_BORDER_WIDTH)
            
            # 绘制按钮文字（居中）
            undo_button_text = "撤回勇士"
            text_surface = self.font.render(undo_button_text, True, text_color)
            text_rect = text_surface.get_rect(center=undo_button_rect.center)
            surface.blit(text_surface, text_rect)
        
        # 绘制"抽取勇士"按钮（在"撤回勇士"按钮下方，靠近列表下边缘）
        # draw_button_y已在上面计算
        
        # 检查按钮是否在列表范围内
        if draw_button_y >= self.y + self.padding:
            # 绘制按钮
            button_rect = pygame.Rect(button_x, draw_button_y, button_width, button_height)
            
            # 检查鼠标悬停
            self.draw_button_hover = button_rect.collidepoint(mouse_pos)
            
            # 绘制按钮背景
            if self.draw_button_hover:
                bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
                border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR
            else:
                bg_color = config.RESET_BUTTON_BG_COLOR
                border_color = config.RESET_BUTTON_BORDER_COLOR
            
            pygame.draw.rect(surface, bg_color, button_rect)
            pygame.draw.rect(surface, border_color, button_rect, config.RESET_BUTTON_BORDER_WIDTH)
            
            # 检查是否需要显示"洗牌"按钮
            # 条件：牌堆为空且弃牌堆有卡牌
            should_show_shuffle = False
            if self.available_deck_button:
                deck_cards = self.available_deck_button.deck_cards
                discard_cards = self.available_deck_button.discard_cards
                should_show_shuffle = (not deck_cards or len(deck_cards) == 0) and \
                                     (discard_cards and len(discard_cards) > 0)
            
            if should_show_shuffle:
                # 显示"洗牌"按钮：只有文字，居中，没有计数器
                button_text = "洗牌"
                text_surface = self.font.render(button_text, True, config.RESET_BUTTON_TEXT_COLOR)
                text_rect = text_surface.get_rect(center=button_rect.center)
                surface.blit(text_surface, text_rect)
                # 洗牌模式下不绘制计数器相关的矩形
                self.draw_counter_input_rect = None
                self.draw_counter_left_rect = None
                self.draw_counter_right_rect = None
            else:
                # 显示"抽取勇士"按钮：左侧文字，右侧计数器
                # 按钮内布局：左侧文字，右侧计数器
                button_padding = 8
                text_left_padding = 12
                
                # 绘制按钮文字（左侧）
                button_text = "抽取勇士"
                text_surface = self.font.render(button_text, True, config.RESET_BUTTON_TEXT_COLOR)
                text_x = button_rect.x + text_left_padding
                text_y = button_rect.centery - text_surface.get_height() // 2
                surface.blit(text_surface, (text_x, text_y))
                
                # 绘制计数器（右侧）
                counter_width = 80  # 计数器区域宽度
                counter_height = 24  # 计数器高度
                counter_x = button_rect.right - counter_width - button_padding
                counter_y = button_rect.centery - counter_height // 2
                
                # 输入框
                input_width = 40
                input_height = counter_height
                input_x = counter_x + (counter_width - input_width) // 2
                input_y = counter_y
                input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
                self.draw_counter_input_rect = input_rect
                
                # 绘制输入框背景
                input_bg_color = config.WARRIOR_LIST_BG_COLOR if not self.draw_counter_active else (40, 40, 40)
                pygame.draw.rect(surface, input_bg_color, input_rect)
                pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, input_rect, 1)
                
                # 绘制计数器值
                display_value = self.draw_counter_value if self.draw_counter_value else "0"
                if display_value == "":
                    display_value = "0"
                value_color = (90, 90, 90) if display_value == "0" else config.RESET_BUTTON_TEXT_COLOR
                counter_font = get_font_with_fallback(16)
                value_surface = counter_font.render(display_value, True, value_color)
                value_rect = value_surface.get_rect(center=input_rect.center)
                surface.blit(value_surface, value_rect)
                
                # 左右按钮
                button_size = 20
                button_spacing = 4
                left_rect = pygame.Rect(
                    input_rect.x - button_size - button_spacing,
                    input_rect.centery - button_size // 2,
                    button_size,
                    button_size
                )
                right_rect = pygame.Rect(
                    input_rect.right + button_spacing,
                    input_rect.centery - button_size // 2,
                    button_size,
                    button_size
                )
                self.draw_counter_left_rect = left_rect
                self.draw_counter_right_rect = right_rect
                
                # 绘制左减按钮
                left_bg = config.WARRIOR_LIST_SLOT_BG_COLOR
                if left_rect.collidepoint(mouse_pos):
                    left_bg = (40, 40, 40)
                pygame.draw.rect(surface, left_bg, left_rect)
                pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, left_rect, 1)
                # 绘制减号
                minus_color = (90, 90, 90) if display_value == "0" else config.WARRIOR_LIST_SLOT_TEXT_COLOR
                pygame.draw.line(surface, minus_color, 
                               (left_rect.centerx - 5, left_rect.centery),
                               (left_rect.centerx + 5, left_rect.centery), 2)
                
                # 绘制右加按钮
                right_bg = config.WARRIOR_LIST_SLOT_BG_COLOR
                if right_rect.collidepoint(mouse_pos):
                    right_bg = (40, 40, 40)
                pygame.draw.rect(surface, right_bg, right_rect)
                pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BORDER_COLOR, right_rect, 1)
                # 绘制加号
                pygame.draw.line(surface, config.WARRIOR_LIST_SLOT_TEXT_COLOR,
                               (right_rect.centerx - 5, right_rect.centery),
                               (right_rect.centerx + 5, right_rect.centery), 2)
                pygame.draw.line(surface, config.WARRIOR_LIST_SLOT_TEXT_COLOR,
                               (right_rect.centerx, right_rect.centery - 5),
                               (right_rect.centerx, right_rect.centery + 5), 2)
    
    def handle_event(self, event):
        """处理拖拽事件（已移除勇士方块列表）"""
        global warrior_drop_target, warrior_blocks
        mouse_pos = pygame.mouse.get_pos()
        window_width, window_height = window.get_size()
        list_x = window_width - self.width - 15
        list_y = self.y
        self.update_position(list_x, list_y)
        
        # 计算卡牌槽位位置（用于检测点击）
        title_text = "勇士列表"
        title_surface = self.title_font.render(title_text, True, config.WARRIOR_LIST_TITLE_COLOR)
        title_rect = title_surface.get_rect()
        title_x = self.x + (self.width - title_rect.width) // 2
        title_y = self.y + self.padding
        
        sample_size = config.CELL_SIZE
        available_width = self.width - self.padding * 2 - sample_size * 4
        sample_spacing = available_width / 3 if available_width > 0 else 8
        # 增加卡牌槽位与标题之间的间距（与draw方法保持一致）
        card_slot_top_margin = 20  # 额外的顶部间距
        sample_start_y = title_y + title_rect.height + self.slot_gap + card_slot_top_margin
        row_spacing = 10
        
        # 获取当前槽位数量（从计数器获取）
        try:
            max_slots = int(self.slot_counter_value or "8")
        except ValueError:
            max_slots = 8
        max_slots = max(0, max_slots)  # 确保不为负数
        
        # 计算需要多少行（每4个一行）
        cols_per_row = 4
        total_rows = (max_slots + cols_per_row - 1) // cols_per_row  # 向上取整
        
        # 检查是否点击了卡牌槽位
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row in range(total_rows):
                sample_y = sample_start_y + row * (sample_size + row_spacing)
                for col in range(cols_per_row):
                    slot_index = row * cols_per_row + col
                    
                    # 如果超过最大槽位数，停止检查
                    if slot_index >= max_slots:
                        break
                    
                    if slot_index < len(self.drawn_cards):
                        sample_x = self.x + self.padding + col * (sample_size + sample_spacing)
                        sample_rect = pygame.Rect(int(sample_x), sample_y, sample_size, sample_size)
                        
                        if sample_rect.collidepoint(mouse_pos):
                            # 开始拖拽
                            card_name = self.drawn_cards[slot_index]
                            if card_name.startswith("步兵_"):
                                warrior_id = card_name.replace("步兵_", "")
                            else:
                                warrior_id = card_name
                            
                            self.is_dragging = True
                            self.dragging_letter = warrior_id
                            self.dragging_card_index = slot_index
                            self.dragging_start_pos = mouse_pos
                            self.dragging_slot_pos = (sample_x, sample_y)
                            warrior_drop_target = None
                            return True
        
        # 处理拖拽释放
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                mouse_x, mouse_y = mouse_pos
                grid_pos = get_grid_position(mouse_x, mouse_y)
                
                if grid_pos:
                    row, col = grid_pos
                    block_key = f"{row},{col}"
                    
                    # 检查是否是有效位置
                    if is_valid_warrior_drop(block_key):
                        # 检查该位置是否已有勇士方块
                        position_occupied = any(pos == block_key for _, pos in warrior_blocks)
                        
                        if not position_occupied:
                            # 位置为空，可以放置
                            warrior_blocks.append((self.dragging_letter, block_key))
                            
                            # 记录最后一次放置的勇士信息，用于撤回功能
                            if self.dragging_card_index is not None and self.dragging_card_index < len(self.drawn_cards):
                                card_name = self.drawn_cards[self.dragging_card_index]
                                self.last_placed_warrior = (self.dragging_letter, block_key, card_name)
                                # 激活撤回按钮
                                self.undo_button_enabled = True
                            
                            # 从卡牌槽位中移除已放置的卡牌
                            if self.dragging_card_index is not None and self.dragging_card_index < len(self.drawn_cards):
                                self.drawn_cards.pop(self.dragging_card_index)
                        else:
                            # 位置已被占用，不放置（卡牌保留在槽位中）
                            pass
                    else:
                        # 如果不在有效位置，不放置（卡牌保留在槽位中）
                        pass
                else:
                    # 鼠标不在棋盘上，不放置（卡牌保留在槽位中）
                    pass
                
                # 结束拖拽
                self.is_dragging = False
                self.dragging_letter = None
                self.dragging_card_index = None
                self.dragging_start_pos = None
                self.dragging_slot_pos = None
                warrior_drop_target = None
                return True
        
        button_height = 35
        button_width = self.width - self.padding * 2
        button_x = self.x + self.padding
        button_spacing = 8  # 两个按钮之间的间距
        
        # 处理"卡牌槽位"按钮（三个按钮：卡牌槽位（上）、撤回勇士（中）、抽取勇士（下））
        # 计算"抽取勇士"按钮位置（最下方）
        draw_button_y = self.y + self.height - button_height - self.padding
        # "撤回勇士"按钮在"抽取勇士"按钮上方，间距为button_spacing
        undo_button_y = draw_button_y - button_height - button_spacing
        # "卡牌槽位"按钮在"撤回勇士"按钮上方，间距为button_spacing
        slot_button_y = undo_button_y - button_height - button_spacing
        slot_button_rect = pygame.Rect(button_x, slot_button_y, button_width, button_height)
        
        # 计算"卡牌槽位"按钮的计数器区域（与draw方法中的计算一致）
        button_padding = 8
        counter_width = 80
        counter_height = 24
        slot_counter_x = slot_button_rect.right - counter_width - button_padding
        slot_counter_y = slot_button_rect.centery - counter_height // 2
        
        slot_input_width = 40
        slot_input_height = counter_height
        slot_input_x = slot_counter_x + (counter_width - slot_input_width) // 2
        slot_input_y = slot_counter_y
        slot_input_rect = pygame.Rect(slot_input_x, slot_input_y, slot_input_width, slot_input_height)
        
        button_size = 20
        slot_button_spacing = 4
        slot_left_rect = pygame.Rect(
            slot_input_rect.x - button_size - slot_button_spacing,
            slot_input_rect.centery - button_size // 2,
            button_size,
            button_size
        )
        slot_right_rect = pygame.Rect(
            slot_input_rect.right + slot_button_spacing,
            slot_input_rect.centery - button_size // 2,
            button_size,
            button_size
        )
        
        # 处理"卡牌槽位"按钮的计数器点击
        if slot_input_rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.slot_counter_active = True
                self.draw_counter_active = False  # 取消另一个计数器的激活状态
                return True
        
        if slot_left_rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    current_value = int(self.slot_counter_value or "0")
                except ValueError:
                    current_value = 0
                current_value = max(0, current_value - 1)
                self.slot_counter_value = str(current_value)
                self.slot_counter_active = True
                self.draw_counter_active = False  # 取消另一个计数器的激活状态
                # 如果槽位减少，将多余的卡牌放入弃牌堆
                if len(self.drawn_cards) > current_value:
                    excess_cards = self.drawn_cards[current_value:]
                    if self.available_deck_button and excess_cards:
                        for card in excess_cards:
                            self.available_deck_button.discard_cards.append(card)
                    self.drawn_cards = self.drawn_cards[:current_value]
                return True
        
        if slot_right_rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    current_value = int(self.slot_counter_value or "0")
                except ValueError:
                    current_value = 0
                current_value += 1
                self.slot_counter_value = str(current_value)
                self.slot_counter_active = True
                self.draw_counter_active = False  # 取消另一个计数器的激活状态
                return True
        
        # 处理"卡牌槽位"按钮的键盘输入
        if self.slot_counter_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.slot_counter_value = self.slot_counter_value[:-1]
                # 检查并限制卡牌数量，将多余的卡牌放入弃牌堆
                try:
                    current_value = int(self.slot_counter_value or "0")
                except ValueError:
                    current_value = 0
                if len(self.drawn_cards) > current_value:
                    excess_cards = self.drawn_cards[current_value:]
                    if self.available_deck_button and excess_cards:
                        for card in excess_cards:
                            self.available_deck_button.discard_cards.append(card)
                    self.drawn_cards = self.drawn_cards[:current_value]
                return True
            elif event.key == pygame.K_RETURN:
                # 确认输入时，检查并限制卡牌数量，将多余的卡牌放入弃牌堆
                try:
                    current_value = int(self.slot_counter_value or "0")
                except ValueError:
                    current_value = 0
                if len(self.drawn_cards) > current_value:
                    excess_cards = self.drawn_cards[current_value:]
                    if self.available_deck_button and excess_cards:
                        for card in excess_cards:
                            self.available_deck_button.discard_cards.append(card)
                    self.drawn_cards = self.drawn_cards[:current_value]
                self.slot_counter_active = False
                return True
            elif event.unicode.isdigit():
                if len(self.slot_counter_value) < 4:
                    new_value = self.slot_counter_value + event.unicode
                    # 检查新值并限制卡牌数量，将多余的卡牌放入弃牌堆
                    try:
                        new_int_value = int(new_value)
                        if len(self.drawn_cards) > new_int_value:
                            excess_cards = self.drawn_cards[new_int_value:]
                            if self.available_deck_button and excess_cards:
                                for card in excess_cards:
                                    self.available_deck_button.discard_cards.append(card)
                            self.drawn_cards = self.drawn_cards[:new_int_value]
                    except ValueError:
                        pass
                    self.slot_counter_value = new_value
                return True
        
        # 点击"卡牌槽位"按钮其他区域
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if slot_button_rect.collidepoint(mouse_pos):
                # 如果点击的不是计数器区域，可以在这里添加按钮点击逻辑
                if not slot_input_rect.collidepoint(mouse_pos) and \
                   not slot_left_rect.collidepoint(mouse_pos) and \
                   not slot_right_rect.collidepoint(mouse_pos):
                    self.slot_counter_active = False
                    # 可以在这里添加按钮点击后的逻辑
                return True
        
        # 处理"撤回勇士"按钮
        # undo_button_y已在上面计算
        undo_button_rect = pygame.Rect(button_x, undo_button_y, button_width, button_height)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if undo_button_rect.collidepoint(mouse_pos) and self.undo_button_enabled:
                # 撤回最近一次摆放的勇士
                if self.last_placed_warrior:
                    warrior_letter, block_key, card_name = self.last_placed_warrior
                    
                    # 从棋盘上移除勇士
                    warrior_blocks[:] = [(w, p) for w, p in warrior_blocks if not (w == warrior_letter and p == block_key)]
                    
                    # 将卡牌放回卡牌槽位（放回末尾）
                    # 如果槽位未满，放回末尾；如果已满，放回末尾并移除最后一张
                    try:
                        max_slots = int(self.slot_counter_value or "8")
                    except ValueError:
                        max_slots = 8
                    max_slots = max(0, max_slots)
                    
                    if len(self.drawn_cards) < max_slots:
                        self.drawn_cards.append(card_name)
                    else:
                        # 槽位已满，放回末尾，移除最后一张放入弃牌堆
                        if self.available_deck_button:
                            if len(self.drawn_cards) > 0:
                                self.available_deck_button.discard_cards.append(self.drawn_cards[-1])
                        self.drawn_cards[-1] = card_name
                    
                    # 清除记录并禁用按钮（使用一次后变不可用）
                    self.last_placed_warrior = None
                    self.undo_button_enabled = False
                    return True
        
        # 处理"抽取勇士"按钮
        # draw_button_y已在上面计算
        button_rect = pygame.Rect(button_x, draw_button_y, button_width, button_height)
        
        # 检查是否需要显示"洗牌"按钮（与draw方法中的逻辑一致）
        should_show_shuffle = False
        if self.available_deck_button:
            deck_cards = self.available_deck_button.deck_cards
            discard_cards = self.available_deck_button.discard_cards
            should_show_shuffle = (not deck_cards or len(deck_cards) == 0) and \
                                 (discard_cards and len(discard_cards) > 0)
        
        # 只有在非洗牌模式下才处理计数器相关逻辑
        if not should_show_shuffle:
            # 计算"抽取勇士"按钮的计数器区域（与draw方法中的计算一致）
            counter_x = button_rect.right - counter_width - button_padding
            counter_y = button_rect.centery - counter_height // 2
            
            input_width = 40
            input_height = counter_height
            input_x = counter_x + (counter_width - input_width) // 2
            input_y = counter_y
            input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
            
            left_rect = pygame.Rect(
                input_rect.x - button_size - slot_button_spacing,
                input_rect.centery - button_size // 2,
                button_size,
                button_size
            )
            right_rect = pygame.Rect(
                input_rect.right + slot_button_spacing,
                input_rect.centery - button_size // 2,
                button_size,
                button_size
            )
            
            # 处理"抽取勇士"按钮的计数器点击
            if input_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.draw_counter_active = True
                    self.slot_counter_active = False  # 取消另一个计数器的激活状态
                    return True
            
            if left_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    try:
                        current_value = int(self.draw_counter_value or "0")
                    except ValueError:
                        current_value = 0
                    current_value = max(0, current_value - 1)
                    self.draw_counter_value = str(current_value)
                    self.draw_counter_active = True
                    self.slot_counter_active = False  # 取消另一个计数器的激活状态
                    return True
            
            if right_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    try:
                        current_value = int(self.draw_counter_value or "0")
                    except ValueError:
                        current_value = 0
                    current_value += 1
                    self.draw_counter_value = str(current_value)
                    self.draw_counter_active = True
                    self.slot_counter_active = False  # 取消另一个计数器的激活状态
                    return True
            
            # 处理"抽取勇士"按钮的键盘输入
            if self.draw_counter_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.draw_counter_value = self.draw_counter_value[:-1]
                    return True
                elif event.key == pygame.K_RETURN:
                    self.draw_counter_active = False
                    return True
                elif event.unicode.isdigit():
                    if len(self.draw_counter_value) < 4:
                        self.draw_counter_value = self.draw_counter_value + event.unicode
                    return True
            
            # 点击"抽取勇士"按钮其他区域
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(mouse_pos):
                    # 如果点击的不是计数器区域，执行抽取逻辑
                    if not input_rect.collidepoint(mouse_pos) and \
                       not left_rect.collidepoint(mouse_pos) and \
                       not right_rect.collidepoint(mouse_pos):
                        self.draw_counter_active = False
                        # 执行抽取勇士逻辑
                        self.draw_warriors_from_deck()
                    return True
        else:
            # 洗牌模式：点击按钮执行洗牌
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(mouse_pos):
                    self.draw_counter_active = False
                    self.shuffle_deck()
                    return True
        
        # 点击按钮外部区域，取消激活状态
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not button_rect.collidepoint(mouse_pos) and not slot_button_rect.collidepoint(mouse_pos):
                self.draw_counter_active = False
                self.slot_counter_active = False
        
        return False
    
    def draw_warriors_from_deck(self):
        """从牌堆抽取勇士方块到卡牌槽位"""
        if not self.available_deck_button:
            return
        
        # 获取抽取数量
        try:
            draw_count = int(self.draw_counter_value or "0")
        except ValueError:
            draw_count = 0
        
        if draw_count <= 0:
            return
        
        # 检查牌堆是否有卡牌
        deck_cards = self.available_deck_button.deck_cards
        if not deck_cards or len(deck_cards) == 0:
            return
        
        # 计算可用的槽位数量（从"卡牌槽位"按钮的计数器获取）
        try:
            max_slots = int(self.slot_counter_value or "8")
        except ValueError:
            max_slots = 8
        max_slots = max(0, max_slots)  # 确保不为负数
        available_slots = max_slots - len(self.drawn_cards)
        
        # 实际抽取数量 = min(计数器值, 牌堆剩余数量, 可用槽位数量)
        actual_draw_count = min(draw_count, len(deck_cards), available_slots)
        
        if actual_draw_count <= 0:
            return
        
        # 从牌堆随机抽取卡牌
        drawn = random.sample(deck_cards, actual_draw_count)
        self.drawn_cards.extend(drawn)
        
        # 从牌堆中移除已抽取的卡牌
        # 统计每个被抽取的卡牌需要移除的数量
        drawn_count = {}
        for card in drawn:
            drawn_count[card] = drawn_count.get(card, 0) + 1
        
        # 从原列表中移除对应数量的卡牌
        new_deck_cards = []
        remaining_count = drawn_count.copy()
        for card in deck_cards:
            if card in remaining_count and remaining_count[card] > 0:
                # 这个卡牌需要被移除
                remaining_count[card] -= 1
            else:
                # 保留这个卡牌
                new_deck_cards.append(card)
        
        self.available_deck_button.deck_cards = new_deck_cards
        
        # 成功抽取后，消耗1点灵火值
        consume_spirit_fire()
        # 检查灵火归零待处理标志（抽取勇士不会补充灵火，所以需要检查）
        check_spirit_fire_zero()
    
    def shuffle_deck(self):
        """洗牌功能：将弃牌堆所有勇士方块再次进入牌堆"""
        if not self.available_deck_button:
            return
        
        # 获取弃牌堆
        discard_cards = self.available_deck_button.discard_cards
        if not discard_cards or len(discard_cards) == 0:
            return
        
        # 将弃牌堆的所有卡牌添加到牌堆
        deck_cards = self.available_deck_button.deck_cards or []
        deck_cards.extend(discard_cards)
        
        # 随机打乱牌堆
        random.shuffle(deck_cards)
        
        # 更新牌堆
        self.available_deck_button.deck_cards = deck_cards
        
        # 清空弃牌堆
        self.available_deck_button.discard_cards = []
    
    def draw_dragging(self, surface):
        """绘制拖拽中的勇士方块"""
        if not self.is_dragging or not self.dragging_letter:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        warrior_size = config.CELL_SIZE
        
        # 计算拖拽方块的位置（鼠标位置偏移，使方块中心在鼠标位置）
        drag_x = mouse_pos[0] - warrior_size // 2
        drag_y = mouse_pos[1] - warrior_size // 2
        drag_rect = pygame.Rect(drag_x, drag_y, warrior_size, warrior_size)
        
        # 绘制拖拽中的勇士方块（半透明效果）
        drag_surface = pygame.Surface((warrior_size, warrior_size), pygame.SRCALPHA)
        drag_surface.fill((*config.WARRIOR_LIST_SLOT_BG_COLOR, 200))  # 半透明背景
        surface.blit(drag_surface, drag_rect.topleft)
        
        # 绘制边框
        pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_HOVER_COLOR, drag_rect, config.WARRIOR_SLOT_BORDER_WIDTH)
        
        # 绘制勇士数字
        warrior_font = get_font_with_fallback(int(warrior_size * 0.5))
        letter_surface = warrior_font.render(self.dragging_letter, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
        letter_rect = letter_surface.get_rect(center=drag_rect.center)
        surface.blit(letter_surface, letter_rect)
    
    def draw_card_tooltip(self, surface, anchor_rect, warrior_id):
        """绘制勇士卡牌信息提示框"""
        try:
            # 确保 warrior_id 是字符串
            warrior_id_str = str(warrior_id)
            warrior_name = f"步兵_{warrior_id_str}"
            try:
                power_value = int(warrior_id_str)
            except (ValueError, TypeError):
                power_value = 0
            description = "最基础的战士，和战友站在一起能提升战力"
            
            lines = [
                warrior_name,
                f"战力：{power_value}",
                description
            ]
            
            font = get_font_with_fallback(16)
            padding = 10
            line_height = 20
            try:
                tooltip_width = max(font.render(line, True, (255, 255, 255)).get_width() for line in lines) + padding * 2
            except (AttributeError, pygame.error, TypeError):
                # 字体渲染失败，使用默认宽度
                tooltip_width = 200  # 默认宽度
            tooltip_height = len(lines) * line_height + padding * 2
            
            # 计算提示框位置（固定在画面正下方，水平居中）
            window_width, window_height = window.get_size()
            tooltip_x = (window_width - tooltip_width) // 2  # 水平居中
            tooltip_y = window_height - tooltip_height - 20  # 距离底部20像素
            
            tooltip_rect = pygame.Rect(int(tooltip_x), int(tooltip_y), tooltip_width, tooltip_height)
            pygame.draw.rect(surface, (0, 0, 0, 255), tooltip_rect)
            pygame.draw.rect(surface, (120, 120, 120), tooltip_rect, 2)
            
            for i, line in enumerate(lines):
                try:
                    text_surface = font.render(line, True, (230, 230, 230) if i == 0 else (200, 200, 200))
                    text_pos = (
                        tooltip_rect.x + padding,
                        tooltip_rect.y + padding + i * line_height
                    )
                    surface.blit(text_surface, text_pos)
                except (AttributeError, pygame.error, TypeError, ValueError) as e:
                    print(f"渲染提示框文本时出错: {e}")
        except (AttributeError, pygame.error, TypeError, ValueError) as e:
            print(f"绘制提示框时出错: {e}")
            import traceback
            traceback.print_exc()

class WarriorDeckButton:
    """勇士牌库按钮和菜单UI组件"""
    def __init__(self, font, label="勇士牌库", offset=0, available_deck_button=None, game_loop_ref=None):
        self.font = font
        self.text = label
        self.button_offset = offset
        self.width = 100  # 按钮宽度
        self.height = 35  # 按钮高度（与重置按钮一致）
        self.x = 0  # 初始值，会在draw时动态计算（右下角）
        self.y = 0
        self.open = False  # 窗口是否打开
        self.pressed = False  # 按钮是否按下
        self.available_deck_button = available_deck_button  # 可用牌组按钮的引用
        self.game_loop_ref = game_loop_ref  # 引用GameLoop实例，用于访问warrior_list等
        self.hovered_card = None  # 记录当前悬停的勇士方块（用于绘制提示框）
        
        # 窗口配置
        self.window_padding = 20  # 窗口内边距
        # 勇士方块大小与勇士列表中的一致（使用棋盘格子大小，在绘制时动态获取）
        self.window_item_gap = 40  # 勇士方块之间的间距（再加大）
        self.window_cols = 3  # 每行显示的勇士方块数量
        self.window_width = 0  # 窗口宽度（动态计算）
        self.window_height = 0  # 窗口高度（动态计算）
        
        # 窗口大小调整
        self.is_resizing = False  # 是否正在调整大小
        self.resize_start_pos = None  # 开始调整大小时的鼠标位置
        self.resize_start_size = None  # 开始调整大小时的窗口大小
        self.resize_handle_size = 15  # 调整大小控件的尺寸
        
        # 勇士方块默认外观数据（与勇士列表中的外观一致）
        # 背景色：WARRIOR_LIST_SLOT_BG_COLOR = (26, 26, 26)  # #1a1a1a
        # 边框色：WARRIOR_LIST_SLOT_BORDER_COLOR = (85, 85, 85)  # #555
        # 边框宽度：WARRIOR_SLOT_BORDER_WIDTH = 1
        # 文字颜色：WARRIOR_LIST_SLOT_TEXT_COLOR = (187, 187, 187)  # #bbb
        # 字体：使用 self.font（与勇士列表中的字体一致）
        
        # 卡牌计数器（使用配置的默认值）
        self.card_counter_values = {
            warrior_id: config.WARRIOR_CARD_COUNTER_INITIAL_VALUES.get(warrior_id, "0")
            for warrior_id in config.WARRIOR_LETTERS
        }
        self.card_counter_active_id = None
        self.card_counter_rects = {
            warrior_id: {'input': None, 'left': None, 'right': None}
            for warrior_id in config.WARRIOR_LETTERS
        }
        
        # Initialize these to None to prevent AttributeError on first access
        self.stats_panel_rect = None
        self.confirm_button_rect = None
        self.clear_button_rect = None
    
    def draw_card_tooltip(self, surface, anchor_rect, warrior_id):
        """绘制勇士卡牌信息提示框"""
        try:
            # 确保 warrior_id 是字符串
            warrior_id_str = str(warrior_id)
            warrior_name = f"步兵_{warrior_id_str}"
            try:
                power_value = int(warrior_id_str)
            except (ValueError, TypeError):
                power_value = 0
            description = "最基础的战士，和战友站在一起能提升战力"
            
            lines = [
                warrior_name,
                f"战力：{power_value}",
                description
            ]
            
            font = get_font_with_fallback(16)
            padding = 10
            line_height = 20
            try:
                tooltip_width = max(font.render(line, True, (255, 255, 255)).get_width() for line in lines) + padding * 2
            except (AttributeError, pygame.error, TypeError):
                # 字体渲染失败，使用默认宽度
                tooltip_width = 200  # 默认宽度
            tooltip_height = len(lines) * line_height + padding * 2
            
            # 计算提示框位置（固定在画面正下方，水平居中）
            window_width, window_height = window.get_size()
            tooltip_x = (window_width - tooltip_width) // 2  # 水平居中
            tooltip_y = window_height - tooltip_height - 20  # 距离底部20像素
            
            tooltip_rect = pygame.Rect(int(tooltip_x), int(tooltip_y), tooltip_width, tooltip_height)
            pygame.draw.rect(surface, (0, 0, 0, 255), tooltip_rect)
            pygame.draw.rect(surface, (120, 120, 120), tooltip_rect, 2)
            
            for i, line in enumerate(lines):
                try:
                    text_surface = font.render(line, True, (230, 230, 230) if i == 0 else (200, 200, 200))
                    text_pos = (
                        tooltip_rect.x + padding,
                        tooltip_rect.y + padding + i * line_height
                    )
                    surface.blit(text_surface, text_pos)
                except (AttributeError, pygame.error, TypeError, ValueError) as e:
                    print(f"渲染提示框文本时出错: {e}")
        except (AttributeError, pygame.error, TypeError, ValueError) as e:
            print(f"绘制提示框时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def reset_deck(self):
        """重置牌组：清除所有勇士方块，然后根据计数器重新添加牌组到可用牌组"""
        global warrior_blocks, warrior_deck, warrior_drop_target
        
        # 1. 清除棋盘上的所有勇士方块
        warrior_blocks.clear()
        warrior_drop_target = None
        
        # 2. 清除勇士列表
        if self.game_loop_ref and hasattr(self.game_loop_ref, 'warrior_list'):
            self.game_loop_ref.warrior_list.drawn_cards = []
            self.game_loop_ref.warrior_list.is_dragging = False
            self.game_loop_ref.warrior_list.dragging_letter = None
            self.game_loop_ref.warrior_list.dragging_card_index = None
            self.game_loop_ref.warrior_list.dragging_start_pos = None
            self.game_loop_ref.warrior_list.dragging_slot_pos = None
        
        # 3. 清除牌堆和弃牌堆
        if self.available_deck_button:
            self.available_deck_button.deck_cards = []
            self.available_deck_button.discard_cards = []
        
        # 4. 根据牌库计数器重新添加牌组到可用牌组
        if self.available_deck_button:
            deck_cards = []
            for warrior_id in config.WARRIOR_LETTERS:
                count = int(self.card_counter_values.get(warrior_id, "0") or "0")
                warrior_name = f"步兵_{warrior_id}"
                # 根据数量添加对应数量的卡牌
                for _ in range(count):
                    deck_cards.append(warrior_name)
            self.available_deck_button.deck_cards = deck_cards
        
    def update_position(self, x, y):
        """更新按钮位置"""
        self.x = x
        self.y = y
    
    def handle_card_counter_click(self, mouse_pos):
        for warrior_id, rects in self.card_counter_rects.items():
            input_rect = rects.get('input')
            left_rect = rects.get('left')
            right_rect = rects.get('right')
            
            if input_rect and input_rect.collidepoint(mouse_pos):
                self.card_counter_active_id = warrior_id
                return True
            if left_rect and left_rect.collidepoint(mouse_pos):
                self.card_counter_active_id = warrior_id
                try:
                    current_value = int(self.card_counter_values[warrior_id] or "0")
                except ValueError:
                    current_value = 0
                current_value = max(0, current_value - 1)
                self.card_counter_values[warrior_id] = str(current_value)
                return True
            if right_rect and right_rect.collidepoint(mouse_pos):
                self.card_counter_active_id = warrior_id
                try:
                    current_value = int(self.card_counter_values[warrior_id] or "0")
                except ValueError:
                    current_value = 0
                current_value += 1
                self.card_counter_values[warrior_id] = str(current_value)
                return True
        
        self.card_counter_active_id = None
        return False
    
    def handle_event(self, event):
        """处理事件"""
        global hovered_cell, warrior_drop_target
        # 如果窗口打开，优先处理窗口内的事件
        if self.open:
            mouse_pos = pygame.mouse.get_pos()
            window_rect = self.get_window_rect()
            stats_panel_rect = getattr(self, "stats_panel_rect", None)
            confirm_button_rect = getattr(self, "confirm_button_rect", None)
            clear_button_rect = getattr(self, "clear_button_rect", None)
            
            # 检查是否点击了调整大小控件
            resize_handle_rect = self.get_resize_handle_rect()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    if resize_handle_rect.collidepoint(mouse_pos):
                        # 开始调整大小
                        self.is_resizing = True
                        self.resize_start_pos = mouse_pos
                        self.resize_start_size = (self.window_width, self.window_height)
                        return True

                    # 统计面板区域的按钮（可能不在主窗口矩形内）
                    if confirm_button_rect and confirm_button_rect.collidepoint(mouse_pos):
                        # 重置牌组：调用重置牌组方法
                        self.reset_deck()
                        return True
                    if clear_button_rect and clear_button_rect.collidepoint(mouse_pos):
                        # 清空所有勇士方块数量
                        for warrior_id in self.card_counter_values:
                            self.card_counter_values[warrior_id] = "0"
                        self.card_counter_active_id = None
                        return True

                    if window_rect.collidepoint(mouse_pos):
                        # 检查是否点击了关闭按钮
                        close_button_rect = self.get_close_button_rect()
                        if close_button_rect.collidepoint(mouse_pos):
                            self.open = False
                            return True
                        if self.handle_card_counter_click(mouse_pos):
                            return True
                        # 点击在窗口内（但不是关闭按钮和调整大小控件），阻止事件传递
                        return True
                    elif stats_panel_rect and stats_panel_rect.collidepoint(mouse_pos):
                        return True
                    else:
                        # 鼠标在窗口外，检查是否点击了按钮
                        # 计算按钮位置（与draw方法中的计算一致）
                        window_width, window_height = window.get_size()
                        button_x = window_width - self.width - 15  # 距离右边缘15像素
                        button_y = window_height - self.height - 15  # 距离底部15像素
                        button_rect = pygame.Rect(button_x, button_y, self.width, self.height)
                        if button_rect.collidepoint(mouse_pos):
                            # 点击了按钮，关闭窗口（按钮在窗口外）
                            self.open = False
                            return True
                        # 鼠标在窗口外且不是按钮，如果点击则关闭窗口
                        self.open = False
                        return True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    if self.is_resizing:
                        # 结束调整大小（无论鼠标在哪里释放）
                        self.is_resizing = False
                        self.resize_start_pos = None
                        self.resize_start_size = None
                        return True
                    self.pressed = False
                    # 如果鼠标在窗口内，拦截事件
                    if window_rect.collidepoint(mouse_pos) or \
                       (stats_panel_rect and stats_panel_rect.collidepoint(mouse_pos)) or \
                       (confirm_button_rect and confirm_button_rect.collidepoint(mouse_pos)) or \
                       (clear_button_rect and clear_button_rect.collidepoint(mouse_pos)):
                        return True
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_resizing:
                    # 调整窗口大小（无论鼠标在哪里，只要正在调整大小就继续）
                    if self.resize_start_pos and self.resize_start_size:
                        # 直接使用当前鼠标位置计算，确保实时响应
                        dx = mouse_pos[0] - self.resize_start_pos[0]
                        dy = mouse_pos[1] - self.resize_start_pos[1]
                        new_width = max(300, self.resize_start_size[0] + dx)  # 最小宽度300
                        new_height = max(200, self.resize_start_size[1] + dy)  # 最小高度200
                        # 立即更新窗口大小，确保按钮位置实时更新
                        self.window_width = int(new_width)
                        self.window_height = int(new_height)
                        return True
                elif window_rect.collidepoint(mouse_pos) or \
                        resize_handle_rect.collidepoint(mouse_pos) or \
                        (stats_panel_rect and stats_panel_rect.collidepoint(mouse_pos)) or \
                        (confirm_button_rect and confirm_button_rect.collidepoint(mouse_pos)) or \
                        (clear_button_rect and clear_button_rect.collidepoint(mouse_pos)):
                    # 鼠标在窗口内或调整大小控件上，拦截事件
                    return True
            
            if event.type == pygame.KEYDOWN and self.card_counter_active_id:
                active_id = self.card_counter_active_id
                if event.key == pygame.K_BACKSPACE:
                    current_value = self.card_counter_values[active_id]
                    self.card_counter_values[active_id] = current_value[:-1]
                elif event.key == pygame.K_RETURN:
                    self.card_counter_active_id = None
                elif event.unicode.isdigit():
                    current_value = self.card_counter_values[active_id]
                    if len(current_value) < 4:
                        self.card_counter_values[active_id] = current_value + event.unicode
                return True
            
            # 如果鼠标在窗口内，拦截其他事件
            if window_rect.collidepoint(mouse_pos) or \
               (stats_panel_rect and stats_panel_rect.collidepoint(mouse_pos)) or \
               (confirm_button_rect and confirm_button_rect.collidepoint(mouse_pos)) or \
               (clear_button_rect and clear_button_rect.collidepoint(mouse_pos)):
                return True
        
        # 窗口未打开时，处理按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mouse_pos = pygame.mouse.get_pos()
                # 计算按钮位置（与draw方法中的计算一致）
                window_width, window_height = window.get_size()
                button_x = window_width - self.width - 15  # 距离右边缘15像素
                button_y = window_height - self.height - 15  # 距离底部15像素
                button_rect = pygame.Rect(button_x, button_y, self.width, self.height)
                
                if button_rect.collidepoint(mouse_pos):
                    # 点击按钮，打开窗口
                    self.open = True
                    self.pressed = True
                    hovered_cell = None
                    warrior_drop_target = None
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.pressed = False
        
        return False
    
    def get_window_rect(self):
        """获取窗口矩形"""
        global warrior_deck
        window_width, window_height = window.get_size()
        
        # 如果窗口大小未设置或为0，使用默认大小
        if self.window_width == 0 or self.window_height == 0:
            # 默认窗口大小：700 × 525
            self.window_width = 700
            self.window_height = 525
        else:
            # 确保窗口大小不小于最小值
            self.window_width = max(300, self.window_width)
            self.window_height = max(200, self.window_height)
        
        # 窗口居中
        window_x = (window_width - self.window_width) // 2
        window_y = (window_height - self.window_height) // 2
        
        return pygame.Rect(window_x, window_y, self.window_width, self.window_height)
    
    def get_close_button_rect(self):
        """获取关闭按钮矩形"""
        window_rect = self.get_window_rect()
        button_size = 25
        button_x = window_rect.right - button_size - 10
        button_y = window_rect.y + 10
        return pygame.Rect(button_x, button_y, button_size, button_size)
    
    def get_resize_handle_rect(self):
        """获取调整大小控件矩形（右下角三角形区域）"""
        # 直接使用当前窗口大小计算，不依赖get_window_rect（避免循环调用）
        window_width, window_height = window.get_size()
        
        # 如果窗口大小未设置，使用默认值
        if self.window_width == 0 or self.window_height == 0:
            self.window_width = 700
            self.window_height = 525
        else:
            # 确保窗口大小不小于最小值
            self.window_width = max(300, self.window_width)
            self.window_height = max(200, self.window_height)
        
        # 窗口居中位置
        window_x = (window_width - self.window_width) // 2
        window_y = (window_height - self.window_height) // 2
        
        handle_size = self.resize_handle_size
        handle_x = window_x + self.window_width - handle_size
        handle_y = window_y + self.window_height - handle_size
        return pygame.Rect(handle_x, handle_y, handle_size, handle_size)
    
    def draw(self, surface):
        """绘制组件"""
        window_width, window_height = window.get_size()
        
        # 计算按钮位置（默认右下角）
        button_x = window_width - self.width - 15
        button_y = window_height - self.height - 15  # 距离底部15像素
        
        # 更新位置
        if hasattr(self, "button_offset"):
            button_x += self.button_offset
        self.update_position(button_x, button_y)
        
        # 绘制按钮
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)
        
        # 按钮背景色
        if self.pressed:
            bg_color = config.RESET_BUTTON_BG_ACTIVE_COLOR
        elif is_hover:
            bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
        else:
            bg_color = config.RESET_BUTTON_BG_COLOR
        
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # 按钮边框
        border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR if is_hover else config.RESET_BUTTON_BORDER_COLOR
        pygame.draw.rect(surface, border_color, button_rect, config.RESET_BUTTON_BORDER_WIDTH)
        
        # 按钮文字（居中显示）
        text_surface = self.font.render(self.text, True, config.RESET_BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # 如果窗口打开，绘制窗口
        if self.open:
            self.draw_window(surface)
    
    def draw_window(self, surface):
        """绘制窗口"""
        global warrior_deck, warrior_blocks
        
        # 获取窗口矩形
        window_rect = self.get_window_rect()
        
        mouse_pos = pygame.mouse.get_pos()
        # 绘制窗口背景（半透明效果）
        # 创建一个带 alpha 通道的 Surface
        bg_surface = pygame.Surface((window_rect.width, window_rect.height), pygame.SRCALPHA)
        # 使用半透明背景色（alpha = 220，约86%不透明度，可以略微看到背后）
        bg_color = (*config.WARRIOR_LIST_BG_COLOR, 220)  # RGBA
        pygame.draw.rect(bg_surface, bg_color, (0, 0, window_rect.width, window_rect.height))
        # 将半透明背景 blit 到主 surface
        surface.blit(bg_surface, (window_rect.x, window_rect.y))
        
        # 绘制窗口边框（保持不透明）
        pygame.draw.rect(surface, config.WARRIOR_LIST_BORDER_COLOR, window_rect, 3)
        
        # 绘制窗口标题
        title_text = "勇士牌库"
        base_height = self.font.get_height()
        title_font_size = max(int(base_height * 1.5), base_height + 4)
        title_font = get_font_with_fallback(title_font_size)
        title_surface = title_font.render(title_text, True, config.WARRIOR_LIST_TITLE_COLOR)
        title_rect = title_surface.get_rect()
        title_rect.midtop = (window_rect.centerx, window_rect.y + self.window_padding)
        surface.blit(title_surface, title_rect)
        
        # 统计小窗口（与勇士牌库同属一体）
        stats_panel_width = 180
        stats_panel_min_height = 130
        panel_gap = 20
        stats_panel_x = max(self.window_padding, window_rect.x - stats_panel_width - panel_gap)
        stats_panel_y = window_rect.y + self.window_padding
        
        total_warriors = sum(
            int(self.card_counter_values.get(wid, "0") or 0)
            for wid in warrior_deck
        )
        stats_lines = [
            f"总数：{total_warriors}",
        ]
        stats_line_font = get_font_with_fallback(18)
        stats_title_font = self.font
        stats_title_surface = stats_title_font.render("勇士统计", True, config.WARRIOR_LIST_TITLE_COLOR)
        
        # 绘制关闭按钮
        close_button_rect = self.get_close_button_rect()
        is_close_hover = close_button_rect.collidepoint(mouse_pos)
        close_bg_color = config.RESET_BUTTON_BG_HOVER_COLOR if is_close_hover else config.RESET_BUTTON_BG_COLOR
        pygame.draw.rect(surface, close_bg_color, close_button_rect)
        pygame.draw.rect(surface, config.RESET_BUTTON_BORDER_COLOR, close_button_rect, 1)
        # 绘制关闭按钮的X
        close_font = pygame.font.Font(None, 20)
        close_text = close_font.render("×", True, config.RESET_BUTTON_TEXT_COLOR)
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        surface.blit(close_text, close_text_rect)
        
        # 绘制调整大小控件（右下角三角形）
        # 如果正在调整大小，按钮位置直接跟随鼠标（更紧地跟随）
        if self.is_resizing and self.resize_start_pos:
            # 计算按钮应该跟随到的位置（鼠标位置，但限制在窗口范围内）
            handle_size = self.resize_handle_size
            handle_x = window_rect.right - handle_size
            handle_y = window_rect.bottom - handle_size
            resize_handle_rect = pygame.Rect(handle_x, handle_y, handle_size, handle_size)
        else:
            resize_handle_rect = self.get_resize_handle_rect()
        
        is_resize_hover = resize_handle_rect.collidepoint(mouse_pos) or self.is_resizing
        
        # 绘制三角形（朝向右下角）
        triangle_color = (200, 200, 200) if is_resize_hover else (150, 150, 150)  # 灰白色
        triangle_points = [
            (resize_handle_rect.right, resize_handle_rect.top),  # 右上角
            (resize_handle_rect.right, resize_handle_rect.bottom),  # 右下角
            (resize_handle_rect.left, resize_handle_rect.bottom)  # 左下角
        ]
        pygame.draw.polygon(surface, triangle_color, triangle_points)
        
        # 在窗口右下角显示窗口尺寸（在调整按钮上方）
        size_text = f"{int(self.window_width)} × {int(self.window_height)}"
        size_font = pygame.font.Font(None, 12)
        size_surface = size_font.render(size_text, True, (150, 150, 150))
        # 计算尺寸文字位置（右下角，在调整按钮上方）
        size_x = window_rect.right - size_surface.get_width() - 5
        size_y = window_rect.bottom - self.resize_handle_size - size_surface.get_height() - 3
        surface.blit(size_surface, (size_x, size_y))
        
        # 绘制勇士方块列表
        # 勇士方块大小与勇士列表中的一致（使用棋盘格子大小）
        window_item_size = config.CELL_SIZE  # 动态获取当前格子大小
        horizontal_offset = 40  # 使方块远离左侧
        content_start_x = window_rect.x + self.window_padding + horizontal_offset
        normal_title_font = get_font_with_fallback(int(self.font.get_height() * 0.9))
        normal_title_surface = normal_title_font.render("普通战士", True, config.WARRIOR_LIST_TITLE_COLOR)
        normal_title_rect = normal_title_surface.get_rect()
        normal_title_rect.topleft = (content_start_x, title_rect.bottom + 30)
        surface.blit(normal_title_surface, normal_title_rect)
        content_start_y = normal_title_rect.bottom + 35
        normal_section_bottom = content_start_y
        
        self.hovered_card = None
        
        for i, warrior_id in enumerate(warrior_deck):
            # 特殊布局：1, 2, 3, 4, 5全部在第一行（4和5跟在3后面）
            row = 0
            col = i  # 所有步兵都在第一行，按顺序排列：0, 1, 2, 3, 4
            
            # 计算勇士方块位置
            warrior_x = content_start_x + col * (window_item_size + self.window_item_gap)
            warrior_y = content_start_y + row * (window_item_size + self.window_item_gap)
            
            warrior_rect = pygame.Rect(warrior_x, warrior_y, window_item_size, window_item_size)
            normal_section_bottom = max(normal_section_bottom, warrior_rect.bottom)
            
            # 允许同名勇士方块，不再检查是否已放置
            
            # 检查鼠标悬停（与勇士列表逻辑一致）
            is_hover = warrior_rect.collidepoint(mouse_pos)
            
            # 绘制勇士方块背景（使用默认外观：WARRIOR_LIST_SLOT_BG_COLOR）
            pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BG_COLOR, warrior_rect)
            
            # 绘制勇士方块边框（使用默认外观：悬停时边框颜色变化，与勇士列表一致）
            border_color = config.WARRIOR_LIST_SLOT_HOVER_COLOR if is_hover else config.WARRIOR_LIST_SLOT_BORDER_COLOR
            pygame.draw.rect(surface, border_color, warrior_rect, config.WARRIOR_SLOT_BORDER_WIDTH)
            
            # 绘制勇士数字（居中，使用默认外观：WARRIOR_LIST_SLOT_TEXT_COLOR 和 self.font）
            letter_surface = self.font.render(warrior_id, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
            letter_rect = letter_surface.get_rect(center=warrior_rect.center)
            surface.blit(letter_surface, letter_rect)
            
            # 绘制勇士名称（在方块上方）
            warrior_name = f"步兵_{warrior_id}"
            name_font_size = 14
            name_font = get_font_with_fallback(name_font_size)
            name_surface = name_font.render(warrior_name, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
            name_x = warrior_rect.centerx - name_surface.get_width() // 2
            name_y = warrior_rect.top - name_surface.get_height() - 10
            surface.blit(name_surface, (name_x, name_y))
            
            # 为步兵_1绘制输入框和按钮
            input_width = window_item_size
            input_height = 30
            input_y = warrior_rect.bottom + 5
            
            input_rect = pygame.Rect(warrior_rect.x, input_y, input_width, input_height)
            
            pygame.draw.rect(surface, config.WARRIOR_LIST_BG_COLOR, input_rect)
            subtle_border_color = (35, 35, 35)
            pygame.draw.rect(surface, subtle_border_color, input_rect, 2)
            
            display_value = self.card_counter_values.get(warrior_id, "0")
            if display_value == "":
                display_value = "0"
            value_color = (90, 90, 90) if display_value == "0" else config.WARRIOR_LIST_SLOT_TEXT_COLOR
            value_surface = self.font.render(display_value, True, value_color)
            value_rect = value_surface.get_rect(center=input_rect.center)
            surface.blit(value_surface, value_rect)
            
            button_size = 24
            button_spacing = 6
            left_rect = pygame.Rect(
                warrior_rect.x,
                input_rect.bottom + button_spacing,
                button_size,
                button_size
            )
            right_rect = pygame.Rect(
                warrior_rect.x + input_width - button_size,
                input_rect.bottom + button_spacing,
                button_size,
                button_size
            )
            
            left_triangle = [
                (left_rect.centerx - 5, left_rect.centery),
                (left_rect.centerx + 5, left_rect.centery - 6),
                (left_rect.centerx + 5, left_rect.centery + 6),
            ]
            left_triangle_color = (90, 90, 90) if display_value == "0" else config.WARRIOR_LIST_SLOT_TEXT_COLOR
            pygame.draw.polygon(surface, left_triangle_color, left_triangle)
            
            right_triangle = [
                (right_rect.centerx + 5, right_rect.centery),
                (right_rect.centerx - 5, right_rect.centery - 6),
                (right_rect.centerx - 5, right_rect.centery + 6),
            ]
            pygame.draw.polygon(surface, config.WARRIOR_LIST_SLOT_TEXT_COLOR, right_triangle)
            
            self.card_counter_rects[warrior_id] = {
                'input': input_rect,
                'left': left_rect,
                'right': right_rect
            }
            
            if is_hover:
                self.hovered_card = (warrior_rect.copy(), warrior_id)
        
        # 不在draw方法中绘制提示框，改为在最后统一绘制，避免被窗口遮挡

        # 精英战士分类标题（占位）
        elite_title_font = get_font_with_fallback(int(self.font.get_height() * 0.9))
        elite_title_surface = elite_title_font.render("精英战士", True, config.WARRIOR_LIST_TITLE_COLOR)
        elite_title_rect = elite_title_surface.get_rect()
        elite_title_rect.topleft = (content_start_x, normal_section_bottom + 140)
        surface.blit(elite_title_surface, elite_title_rect)
        
        # 根据精英战士标题位置调整统计窗口高度
        target_bottom = elite_title_rect.y
        button_height = 32
        button_spacing = 10
        bottom_margin = 12
        
        # 计算所需高度：统计内容 + 两个按钮 + 间距
        stats_title_rect_temp = stats_title_surface.get_rect(center=(stats_panel_x + stats_panel_width // 2, stats_panel_y + 18))
        line_y_start = stats_title_rect_temp.bottom + 20
        line_block_height = len(stats_lines) * (stats_line_font.get_height() + 6)
        line_block_bottom = line_y_start + line_block_height
        required_bottom = line_block_bottom + button_height * 2 + button_spacing + bottom_margin
        
        # 统计面板高度需要容纳内容+两个按钮
        stats_panel_height = max(stats_panel_min_height, required_bottom - stats_panel_y, target_bottom - stats_panel_y)
        stats_panel_rect = pygame.Rect(stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height)
        self.stats_panel_rect = stats_panel_rect
        
        stats_surface = pygame.Surface((stats_panel_width, stats_panel_height), pygame.SRCALPHA)
        stats_color = (*config.WARRIOR_LIST_BG_COLOR, 230)
        stats_surface.fill(stats_color)
        surface.blit(stats_surface, stats_panel_rect.topleft)
        pygame.draw.rect(surface, config.WARRIOR_LIST_BORDER_COLOR, stats_panel_rect, 2)
        
        stats_title_rect = stats_title_surface.get_rect(center=(stats_panel_rect.centerx, stats_panel_rect.y + 18))
        surface.blit(stats_title_surface, stats_title_rect)
        
        line_y = stats_title_rect.bottom + 20
        for line in stats_lines:
            line_surface = stats_line_font.render(line, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
            line_rect = line_surface.get_rect()
            line_rect.midleft = (stats_panel_rect.x + 12, line_y)
            surface.blit(line_surface, line_rect)
            line_y += line_surface.get_height() + 6
        
        # “确认牌组”和“清空牌组”按钮
        button_width = stats_panel_width - 24
        button_x = stats_panel_rect.x + 12
        
        # 确认牌组按钮（在上方）
        confirm_button_y = stats_panel_rect.bottom - bottom_margin - button_height * 2 - button_spacing
        confirm_button_rect = pygame.Rect(button_x, confirm_button_y, button_width, button_height)
        self.confirm_button_rect = confirm_button_rect
        
        is_confirm_hover = confirm_button_rect.collidepoint(mouse_pos)
        confirm_bg = config.RESET_BUTTON_BG_HOVER_COLOR if is_confirm_hover else config.RESET_BUTTON_BG_COLOR
        confirm_border = config.RESET_BUTTON_BORDER_HOVER_COLOR if is_confirm_hover else config.RESET_BUTTON_BORDER_COLOR
        pygame.draw.rect(surface, confirm_bg, confirm_button_rect)
        pygame.draw.rect(surface, confirm_border, confirm_button_rect, 1)
        
        confirm_text = self.font.render("重置牌组", True, config.RESET_BUTTON_TEXT_COLOR)
        surface.blit(confirm_text, confirm_text.get_rect(center=confirm_button_rect.center))
        
        # 清空牌组按钮（在下方）
        clear_button_y = stats_panel_rect.bottom - bottom_margin - button_height
        clear_button_rect = pygame.Rect(button_x, clear_button_y, button_width, button_height)
        self.clear_button_rect = clear_button_rect
        
        is_clear_hover = clear_button_rect.collidepoint(mouse_pos)
        clear_bg = config.RESET_BUTTON_BG_HOVER_COLOR if is_clear_hover else config.RESET_BUTTON_BG_COLOR
        clear_border = config.RESET_BUTTON_BORDER_HOVER_COLOR if is_clear_hover else config.RESET_BUTTON_BORDER_COLOR
        pygame.draw.rect(surface, clear_bg, clear_button_rect)
        pygame.draw.rect(surface, clear_border, clear_button_rect, 1)
        
        clear_text = self.font.render("清空牌组", True, config.RESET_BUTTON_TEXT_COLOR)
        surface.blit(clear_text, clear_text.get_rect(center=clear_button_rect.center))


class AvailableDeckWindowButton:
    """可用牌组按钮，与简易窗口"""

    def __init__(self, font, label="可用牌组", offset=0):
        self.font = font
        self.text = label
        self.button_offset = offset
        self.width = 100
        self.height = 35
        self.x = 0
        self.y = 0
        self.pressed = False
        self.open = False
        self.is_resizing = False
        self.window_width = 700
        self.window_height = 525
        self.window_padding = 20
        self.resize_handle_size = 15
        self.resize_start_pos = None
        self.resize_start_size = None
        self.deck_cards = []
        self.discard_cards = []
        self.stats_panel_rect = None
        self.confirm_button_rect = None
        self.hovered_warrior = None  # 记录当前悬停的勇士方块（用于绘制提示框）

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def get_window_rect(self):
        window_width, window_height = window.get_size()
        window_x = (window_width - self.window_width) // 2
        window_y = (window_height - self.window_height) // 2
        return pygame.Rect(window_x, window_y, self.window_width, self.window_height)

    def get_close_button_rect(self, window_rect):
        button_size = 25
        button_x = window_rect.right - button_size - 10
        button_y = window_rect.y + 10
        return pygame.Rect(button_x, button_y, button_size, button_size)

    def get_resize_handle_rect(self):
        window_rect = self.get_window_rect()
        handle_x = window_rect.right - self.resize_handle_size
        handle_y = window_rect.bottom - self.resize_handle_size
        return pygame.Rect(handle_x, handle_y, self.resize_handle_size, self.resize_handle_size)

    def handle_event(self, event):
        global hovered_cell, warrior_drop_target

        if self.open:
            mouse_pos = pygame.mouse.get_pos()
            window_rect = self.get_window_rect()
            close_rect = self.get_close_button_rect(window_rect)
            resize_rect = self.get_resize_handle_rect()
            stats_rect = getattr(self, "stats_panel_rect", None)
            confirm_rect = getattr(self, "confirm_button_rect", None)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if resize_rect.collidepoint(mouse_pos):
                        self.is_resizing = True
                        self.resize_start_pos = mouse_pos
                        self.resize_start_size = (self.window_width, self.window_height)
                        return True
                    if close_rect.collidepoint(mouse_pos):
                        self.open = False
                        return True
                    if window_rect.collidepoint(mouse_pos) or (stats_rect and stats_rect.collidepoint(mouse_pos)):
                        return True
                    else:
                        self.open = False
                        return True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.is_resizing:
                        self.is_resizing = False
                        self.resize_start_pos = None
                        self.resize_start_size = None
                        return True
                    self.pressed = False
                    if window_rect.collidepoint(mouse_pos):
                        return True

            elif event.type == pygame.MOUSEMOTION:
                if self.is_resizing and self.resize_start_pos and self.resize_start_size:
                    dx = mouse_pos[0] - self.resize_start_pos[0]
                    dy = mouse_pos[1] - self.resize_start_pos[1]
                    self.window_width = max(300, int(self.resize_start_size[0] + dx))
                    self.window_height = max(200, int(self.resize_start_size[1] + dy))
                    return True
                if window_rect.collidepoint(mouse_pos) or resize_rect.collidepoint(mouse_pos):
                    return True

            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if button_rect.collidepoint(mouse_pos):
                self.pressed = True
                self.open = True
                hovered_cell = None
                warrior_drop_target = None
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

        return False

    def draw(self, surface):
        window_width, window_height = window.get_size()
        button_x = window_width - self.width - 15 + self.button_offset
        button_y = window_height - self.height - 15
        self.update_position(button_x, button_y)

        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)

        if self.pressed:
            bg_color = config.RESET_BUTTON_BG_ACTIVE_COLOR
        elif is_hover:
            bg_color = config.RESET_BUTTON_BG_HOVER_COLOR
        else:
            bg_color = config.RESET_BUTTON_BG_COLOR

        pygame.draw.rect(surface, bg_color, button_rect)
        border_color = config.RESET_BUTTON_BORDER_HOVER_COLOR if is_hover else config.RESET_BUTTON_BORDER_COLOR
        pygame.draw.rect(surface, border_color, button_rect, config.RESET_BUTTON_BORDER_WIDTH)

        text_surface = self.font.render(self.text, True, config.RESET_BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)

        if self.open:
            self.draw_window(surface)

    def draw_window(self, surface):
        window_rect = self.get_window_rect()
        
        # 在绘制窗口开始时重置悬停状态
        self.hovered_warrior = None

        # 背景
        bg_surface = pygame.Surface((window_rect.width, window_rect.height), pygame.SRCALPHA)
        bg_color = (*config.WARRIOR_LIST_BG_COLOR, 220)
        pygame.draw.rect(bg_surface, bg_color, (0, 0, window_rect.width, window_rect.height))
        surface.blit(bg_surface, window_rect.topleft)

        pygame.draw.rect(surface, config.WARRIOR_LIST_BORDER_COLOR, window_rect, 3)

        # 标题
        title_font = get_font_with_fallback(max(int(self.font.get_height() * 1.5), self.font.get_height() + 4))
        title_surface = title_font.render("可用牌组", True, config.WARRIOR_LIST_TITLE_COLOR)
        title_rect = title_surface.get_rect(midtop=(window_rect.centerx, window_rect.y + self.window_padding))
        surface.blit(title_surface, title_rect)

        # 关闭按钮
        close_rect = self.get_close_button_rect(window_rect)
        mouse_pos = pygame.mouse.get_pos()
        is_close_hover = close_rect.collidepoint(mouse_pos)
        close_bg_color = config.RESET_BUTTON_BG_HOVER_COLOR if is_close_hover else config.RESET_BUTTON_BG_COLOR
        pygame.draw.rect(surface, close_bg_color, close_rect)
        pygame.draw.rect(surface, config.RESET_BUTTON_BORDER_COLOR, close_rect, 1)
        close_text = pygame.font.Font(None, 20).render("×", True, config.RESET_BUTTON_TEXT_COLOR)
        surface.blit(close_text, close_text.get_rect(center=close_rect.center))

        # 调整大小控件
        resize_rect = self.get_resize_handle_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_resize_hover = resize_rect.collidepoint(mouse_pos) or self.is_resizing
        triangle_color = (200, 200, 200) if is_resize_hover else (150, 150, 150)
        triangle_points = [
            (resize_rect.right, resize_rect.top),
            (resize_rect.right, resize_rect.bottom),
            (resize_rect.left, resize_rect.bottom)
        ]
        pygame.draw.polygon(surface, triangle_color, triangle_points)

        size_text = f"{int(self.window_width)} × {int(self.window_height)}"
        size_surface = pygame.font.Font(None, 12).render(size_text, True, (150, 150, 150))
        size_x = resize_rect.left - size_surface.get_width() - 4
        size_y = resize_rect.bottom - size_surface.get_height() - 4
        surface.blit(size_surface, (size_x, size_y))

        # 栏位布局（上下排列）
        content_top = title_rect.bottom + self.window_padding
        content_bottom = window_rect.bottom - self.window_padding
        available_height = max(0, content_bottom - content_top)
        section_gap = 20
        section_height = (available_height - section_gap) / 2 if available_height > section_gap else available_height / 2
        section_height = max(120, section_height)

        section_width = window_rect.width - self.window_padding * 2
        deck_rect = pygame.Rect(
            window_rect.x + self.window_padding,
            content_top,
            section_width,
            section_height
        )
        discard_rect = pygame.Rect(
            window_rect.x + self.window_padding,
            deck_rect.bottom + section_gap,
            section_width,
            section_height
        )

        self.draw_section(surface, deck_rect, "牌堆", self.deck_cards)
        self.draw_section(surface, discard_rect, "弃牌堆", self.discard_cards)
    
    def draw_card_tooltip(self, surface, anchor_rect, warrior_id):
        """绘制勇士卡牌信息提示框"""
        try:
            # 确保 warrior_id 是字符串
            warrior_id_str = str(warrior_id)
            warrior_name = f"步兵_{warrior_id_str}"
            try:
                power_value = int(warrior_id_str)
            except (ValueError, TypeError):
                power_value = 0
            description = "最基础的战士，和战友站在一起能提升战力"
            
            lines = [
                warrior_name,
                f"战力：{power_value}",
                description
            ]
            
            font = get_font_with_fallback(16)
            padding = 10
            line_height = 20
            try:
                tooltip_width = max(font.render(line, True, (255, 255, 255)).get_width() for line in lines) + padding * 2
            except (AttributeError, pygame.error, TypeError):
                # 字体渲染失败，使用默认宽度
                tooltip_width = 200  # 默认宽度
            tooltip_height = len(lines) * line_height + padding * 2
            
            # 计算提示框位置（固定在画面正下方，水平居中）
            window_width, window_height = window.get_size()
            tooltip_x = (window_width - tooltip_width) // 2  # 水平居中
            tooltip_y = window_height - tooltip_height - 20  # 距离底部20像素
            
            tooltip_rect = pygame.Rect(int(tooltip_x), int(tooltip_y), tooltip_width, tooltip_height)
            pygame.draw.rect(surface, (0, 0, 0, 255), tooltip_rect)
            pygame.draw.rect(surface, (120, 120, 120), tooltip_rect, 2)
            
            for i, line in enumerate(lines):
                try:
                    text_surface = font.render(line, True, (230, 230, 230) if i == 0 else (200, 200, 200))
                    text_pos = (
                        tooltip_rect.x + padding,
                        tooltip_rect.y + padding + i * line_height
                    )
                    surface.blit(text_surface, text_pos)
                except (AttributeError, pygame.error, TypeError, ValueError) as e:
                    print(f"渲染提示框文本时出错: {e}")
        except (AttributeError, pygame.error, TypeError, ValueError) as e:
            print(f"绘制提示框时出错: {e}")
            import traceback
            traceback.print_exc()

    def draw_section(self, surface, rect, title, cards):
        pygame.draw.rect(surface, (24, 24, 24), rect)
        pygame.draw.rect(surface, config.WARRIOR_LIST_BORDER_COLOR, rect, 2)

        header_font = get_font_with_fallback(int(self.font.get_height() * 1.1))

        header_surface = header_font.render(title, True, config.WARRIOR_LIST_TITLE_COLOR)
        header_rect = header_surface.get_rect(midtop=(rect.centerx, rect.top + 12))
        surface.blit(header_surface, header_rect)

        divider_y = header_rect.bottom + 8
        pygame.draw.line(surface, config.WARRIOR_LIST_BORDER_COLOR, (rect.x + 12, divider_y),
                         (rect.right - 12, divider_y), 1)

        # 内容区域
        content_top = divider_y + 14
        content_rect = pygame.Rect(rect.x + 12, content_top, rect.width - 24, rect.bottom - content_top - 12)

        if cards:
            # 绘制勇士方块
            warrior_size = config.CELL_SIZE  # 使用棋盘格子大小
            padding = 8  # 内边距
            spacing = 8  # 方块之间的间距
            
            # 计算每行可以放置多少个方块
            available_width = content_rect.width - padding * 2
            cols = max(1, int((available_width + spacing) / (warrior_size + spacing)))
            
            # 计算起始位置（左对齐）
            start_x = content_rect.x + padding
            start_y = content_rect.y + padding
            
            mouse_pos = pygame.mouse.get_pos()
            # 注意：不在draw_section中重置hovered_warrior，而是在draw_window开始时重置
            # 这样可以让多个section共享同一个hovered_warrior状态
            
            for idx, card_name in enumerate(cards):
                # 从 "步兵_1" 中提取 "1"
                if card_name.startswith("步兵_"):
                    warrior_id = card_name.replace("步兵_", "")
                else:
                    warrior_id = card_name  # 如果格式不对，直接使用
                
                # 计算位置
                row = idx // cols
                col = idx % cols
                warrior_x = start_x + col * (warrior_size + spacing)
                warrior_y = start_y + row * (warrior_size + spacing)
                
                # 检查是否超出显示区域
                if warrior_y + warrior_size > content_rect.bottom:
                    break  # 超出区域，停止绘制
                
                warrior_rect = pygame.Rect(warrior_x, warrior_y, warrior_size, warrior_size)
                
                # 检查鼠标悬停
                is_hover = warrior_rect.collidepoint(mouse_pos)
                if is_hover:
                    self.hovered_warrior = (warrior_rect, warrior_id)
                
                # 绘制勇士方块背景
                pygame.draw.rect(surface, config.WARRIOR_LIST_SLOT_BG_COLOR, warrior_rect)
                
                # 绘制勇士方块边框
                border_color = config.WARRIOR_LIST_SLOT_HOVER_COLOR if is_hover else config.WARRIOR_LIST_SLOT_BORDER_COLOR
                pygame.draw.rect(surface, border_color, warrior_rect, config.WARRIOR_SLOT_BORDER_WIDTH)
                
                # 绘制勇士数字（居中）
                warrior_font = get_font_with_fallback(int(warrior_size * 0.5))
                letter_surface = warrior_font.render(warrior_id, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
                letter_rect = letter_surface.get_rect(center=warrior_rect.center)
                surface.blit(letter_surface, letter_rect)
            
            # 不在draw方法中绘制提示框，改为在最后统一绘制，避免被窗口遮挡
        else:
            # 没有数据时显示占位文本
            placeholder_font = get_font_with_fallback(18)
            placeholder_surface = placeholder_font.render("暂无数据", True, (120, 120, 120))
            placeholder_rect = placeholder_surface.get_rect(center=(rect.centerx, rect.centery))
            surface.blit(placeholder_surface, placeholder_rect)

def reset_game(difficulty_key=None, game_loop_ref=None):
    """重置游戏"""
    global blocks, marked_blocks, current_hp, current_spirit_fire, spirit_fire_zero_pending, danger_land_blocks, safe_land_blocks, safe_land_block_types, used_safe_land_blocks, discovered_hint_blocks, reveal_animation, reveal_animation_data, warrior_blocks, warrior_deck, is_game_over, is_game_won, start_area, warrior_drop_target, monster_current_power
    
    # 取消正在进行的动画
    reveal_animation = None
    reveal_animation_data = None
    stop_screen_shake()
    
    # 获取当前难度（如果未提供，使用默认难度）
    if difficulty_key is None:
        difficulty_key = config.DEFAULT_DIFFICULTY
    
    # 重置迷雾方块（先初始化所有格子都有迷雾，包括危险格子和安全格子）
    initialize_blocks()
    
    # 清除标记
    marked_blocks.clear()
    
    # 清除被发现提示
    discovered_hint_blocks.clear()
    
    # 清除已使用的安全地块
    used_safe_land_blocks.clear()
    
    # 重新初始化棋子地块层（危险地块等）
    # 注意：这些地块部署在迷雾覆盖的格子上，不会被立即显示
    # 只有当玩家点击打开迷雾时，才会看到这些地块
    initialize_piece_land_blocks(difficulty_key)
    
    # 打开起始区域
    open_start_area_blocks()
    
    # 重置生命值和灵火值
    current_hp = config.MAX_HP
    current_spirit_fire = config.MAX_SPIRIT_FIRE
    spirit_fire_zero_pending = False
    
    # 重置游戏状态
    is_game_over = False
    is_game_won = False
    
    # 清除暴露状态
    global exposed_danger_blocks, exposed_safe_blocks
    exposed_danger_blocks.clear()
    exposed_safe_blocks.clear()
    
    # 清空怪物当前战力字典
    monster_current_power.clear()
    
    # 将已放置的勇士方块收回牌库（不影响牌库的其他状态）
    for warrior_letter, block_key in warrior_blocks:
        if warrior_letter not in warrior_deck:
            warrior_deck.append(warrior_letter)
    
    # 清除勇士方块
    warrior_blocks.clear()
    warrior_drop_target = None
    
    # 清空卡牌槽位中的勇士卡牌
    if game_loop_ref and hasattr(game_loop_ref, 'warrior_list'):
        game_loop_ref.warrior_list.drawn_cards = []
        game_loop_ref.warrior_list.is_dragging = False
        game_loop_ref.warrior_list.dragging_letter = None
        game_loop_ref.warrior_list.dragging_card_index = None
        game_loop_ref.warrior_list.dragging_start_pos = None
        game_loop_ref.warrior_list.dragging_slot_pos = None
    
    # 注意：不重置warrior_deck，保持牌库的当前状态

def parse_block_key(block_key):
    """安全解析 block_key 为 (row, col) 元组
    Args:
        block_key: 格子坐标字符串，格式为 "row,col"
    Returns:
        (row, col) 元组，如果解析失败返回 None
    """
    try:
        parts = block_key.split(',')
        if len(parts) != 2:
            return None
        row, col = int(parts[0]), int(parts[1])
        return (row, col)
    except (ValueError, AttributeError):
        return None

def count_opened_around(row, col):
    """计算指定格子周围8格中已经被打开的格子数量"""
    count = 0
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc
        if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
            block_key = f"{new_row},{new_col}"
            # "被打开"的格子：没有迷雾方块覆盖
            if block_key not in blocks:
                count += 1
    
    return count

def has_no_fog_around(row, col):
    """检查指定格子周围是否没有迷雾（用于终点的暴露条件）"""
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
                block_key = f"{new_row},{new_col}"
                if block_key in blocks:  # 有迷雾
                    return False
    return True

def should_expose_safe_block(block_key, opened_count, row, col):
    """判断安全地块是否应该暴露（根据各子项决定）"""
    if block_key not in safe_land_blocks:
        return False
    
    block_type = safe_land_block_types.get(block_key, 'heal')
    if block_type == 'heal':
        # 治疗草：周围8格中已有4个迷雾格子被打开
        return opened_count >= 4
    elif block_type == 'endpoint':
        # 终点：周围8格不再存在迷雾格子
        return has_no_fog_around(row, col)
    return False

def update_discovered_hints():
    """根据"被发现条件"更新自动提示标记"""
    global discovered_hint_blocks, exposed_danger_blocks, exposed_safe_blocks
    
    discovered_hint_blocks.clear()
    
    # 危险地块：周围8格中有3个迷雾格子被打开；暴露条件：4个空白格子
    for block_key in danger_land_blocks:
        # 仅对仍在迷雾中的地块进行提示
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，清除暴露状态
            exposed_danger_blocks.discard(block_key)
            continue
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        opened_count = count_opened_around(row, col)
        if opened_count >= 3:
            discovered_hint_blocks.add(block_key)
        if opened_count >= 4:
            exposed_danger_blocks.add(block_key)
            discovered_hint_blocks.discard(block_key)  # 暴露后不再使用被发现提示
        else:
            # 如果不再满足暴露条件，清除暴露状态
            exposed_danger_blocks.discard(block_key)
    
    # 安全地块（包含治疗草和终点）：根据各子项的被发现条件和暴露条件处理
    for block_key in safe_land_blocks:
        # 仅对仍在迷雾中的地块进行提示
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，清除暴露状态
            exposed_safe_blocks.discard(block_key)
            continue
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        opened_count = count_opened_around(row, col)
        block_type = safe_land_block_types.get(block_key, 'heal')
        
        # 根据类型判断被发现条件
        if block_type == 'heal':
            # 治疗草：周围8格中有3个相连的迷雾格子被打开
            if has_three_connected_opened(row, col):
                discovered_hint_blocks.add(block_key)
        elif block_type == 'endpoint':
            # 终点：周围8格中有3个迷雾格子被打开
            if opened_count >= 3:
                discovered_hint_blocks.add(block_key)
        
        # 判断暴露条件
        if should_expose_safe_block(block_key, opened_count, row, col):
            exposed_safe_blocks.add(block_key)
            discovered_hint_blocks.discard(block_key)  # 暴露后不再使用被发现提示
        else:
            # 如果不再满足暴露条件，清除暴露状态
            exposed_safe_blocks.discard(block_key)
    
    # 如果某个迷雾格子已成为自动提示格子或暴露格子，则撤销玩家手动标记
    all_auto_hints = discovered_hint_blocks | exposed_danger_blocks | exposed_safe_blocks
    for block_key in all_auto_hints:
        if block_key in marked_blocks:
            marked_blocks.remove(block_key)

def draw_red_exclamation_hint(surface, center_x, center_y, size, color):
    """绘制红色感叹号提示图标（极简风格）
    感叹号由两部分组成：
    1. 竖线：细长的矩形（完全对称）
    2. 圆点：底部的小圆点
    
    Args:
        surface: 绘制目标surface
        center_x: 中心点x坐标（浮点数）
        center_y: 中心点y坐标（浮点数）
        size: 感叹号的基础尺寸
        color: 颜色（RGBA元组或RGB元组）
    """
    # 转换为整数坐标，确保像素对齐
    cx = int(center_x)
    cy = int(center_y)
    
    # 计算感叹号各部分尺寸（极简风格：细竖线 + 小圆点）
    # 竖线：细长的矩形（固定宽度4像素，与圆点对齐）
    line_width = max(4, int(size * 0.2))     # 竖线宽度（至少4像素，与圆点直径对齐）
    line_height = int(size * 0.75)           # 竖线高度
    
    # 圆点（直径4像素，半径2像素）
    dot_radius = max(2, int(size * 0.12))    # 圆点半径（至少2像素，直径4像素）
    gap = int(size * 0.2)                     # 竖线和圆点之间的间距
    
    # 计算总高度，用于垂直居中
    total_height = line_height + gap + dot_radius * 2
    start_y = cy - total_height // 2
    
    # 竖线的位置
    line_top_y = start_y
    line_bottom_y = line_top_y + line_height
    
    # 圆点的位置
    dot_y = line_bottom_y + gap + dot_radius
    
    # 绘制竖线（矩形，宽度4像素，与圆点直径对齐）
    # 确保竖线和圆点都使用相同的中轴线（cx）
    if line_width % 2 == 0:  # 偶数宽度（4像素）
        half_width = line_width // 2  # 2
        line_left = cx - half_width   # cx - 2
        line_right = cx + half_width - 1  # cx + 1
    else:  # 奇数宽度，完全对称
        half_width = (line_width - 1) // 2
        line_left = cx - half_width
        line_right = cx + half_width
    
    # 绘制矩形竖线（确保宽度正确）
    line_rect_width = line_right - line_left + 1
    line_rect = pygame.Rect(line_left, line_top_y, line_rect_width, line_height)
    pygame.draw.rect(surface, color, line_rect)
    
    # 绘制圆点（底部的小圆点，水平居中，直径4像素）
    # 圆点中心在cx，半径2，从cx-2到cx+2，与竖线中轴线对齐
    pygame.draw.circle(surface, color, (cx, int(dot_y)), dot_radius)

def draw_discovered_hints(surface):
    """绘制被发现提示图标（红色发光感叹号）"""
    # 只绘制仍在迷雾中的地块
    for block_key in list(discovered_hint_blocks):
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，不再显示提示
            discovered_hint_blocks.discard(block_key)
            continue
        
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        # 计算格子中心位置
        padding_x_int, padding_y_int = get_padding_int()
        x = padding_x_int + col * config.CELL_SIZE
        y = padding_y_int + row * config.CELL_SIZE
        center_x = x + config.CELL_SIZE / 2
        center_y = y + config.CELL_SIZE / 2
        
        # 提示整体大小控制在格子内部的90%（缩小三分之一）
        max_size = config.CELL_SIZE * 0.9
        exclamation_size = max_size * 0.47  # 0.7 * 2/3 ≈ 0.47
        
        # 闪烁效果：透明度在0.7~1.0之间平滑变化，周期约3秒
        blink_speed = 3000  # 毫秒
        current_time = pygame.time.get_ticks()
        blink_phase = (current_time % blink_speed) / blink_speed
        alpha = 0.7 + 0.3 * (math.sin(blink_phase * math.pi * 2) * 0.5 + 0.5)
        
        # 红色感叹号颜色（带透明度）
        hint_color = (255, 0, 0, int(255 * alpha))  # rgba(255, 0, 0, alpha)
        
        # 创建临时surface用于绘制半透明感叹号
        hint_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        
        # 绘制感叹号（不包含外发光圆形）
        draw_red_exclamation_hint(hint_surface, config.CELL_SIZE / 2, config.CELL_SIZE / 2, 
                                  exclamation_size, hint_color)
        
        # 将半透明surface绘制到主surface上
        surface.blit(hint_surface, (x, y))

# ==================== 游戏逻辑函数 ====================
def initialize_blocks():
    """初始化所有格子都有迷雾方块"""
    global blocks
    blocks.clear()
    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            blocks.add(f"{row},{col}")

def get_grid_position(mouse_x, mouse_y):
    """获取鼠标点击的网格坐标"""
    padding_x, padding_y = get_padding_values()
    x = mouse_x - padding_x
    y = mouse_y - padding_y
    
    if x < 0 or y < 0 or x > config.GRID_COLS * config.CELL_SIZE or y > config.GRID_ROWS * config.CELL_SIZE:
        return None  # 点击在网格外
    
    col = int(x / config.CELL_SIZE)
    row = int(y / config.CELL_SIZE)
    
    if 0 <= col < config.GRID_COLS and 0 <= row < config.GRID_ROWS:
        return (row, col)
    
    return None

def update_padding():
    """更新棋盘背景内边距使网格居中"""
    global PADDING_X, PADDING_Y
    window_width, window_height = window.get_size()
    GRID_WIDTH = config.GRID_COLS * config.CELL_SIZE
    GRID_HEIGHT = config.GRID_ROWS * config.CELL_SIZE
    # 使用round()四舍五入居中，避免向左上角偏移
    PADDING_X = round((window_width - GRID_WIDTH) / 2)
    PADDING_Y = round((window_height - GRID_HEIGHT) / 2)

def is_piece_block(block_key):
    """检查一个格子是否是棋子地块（危险、安全地块（包含治疗草和终点））"""
    return (block_key in danger_land_blocks or
            block_key in safe_land_blocks)

def count_piece_land_blocks_around(row, col):
    """计算指定格子周围8格中棋子地块（危险、安全地块（包含治疗草和终点））的总数"""
    count = 0
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc
        if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
            block_key = f"{new_row},{new_col}"
            if is_piece_block(block_key):
                count += 1
    
    return count

def has_piece_land_blocks_around(row, col):
    """检查指定格子周围是否有棋子地块（危险、安全地块（包含治疗草和终点））"""
    return count_piece_land_blocks_around(row, col) > 0

def initialize_piece_land_blocks(difficulty_key):
    """初始化棋子地块层：随机部署危险地块、安全地块（包含治疗草和终点）
    
    注意：此函数在迷雾方块初始化之后调用。
    这些地块部署在迷雾覆盖的格子上，不会被立即显示。
    只有当玩家点击打开迷雾时，才会看到这些地块。
    终点作为安全地块的子项存储在safe_land_blocks中，通过safe_land_block_types区分类型。
    """
    global danger_land_blocks, safe_land_blocks, safe_land_block_types, start_area
    global total_piece_count, total_danger_count, total_safe_count
    
    # 清空现有的危险地块、安全地块
    danger_land_blocks.clear()
    safe_land_blocks.clear()
    safe_land_block_types.clear()
    
    # 选择起始区域
    start_area = select_start_area()
    
    # 获取难度对应的棋子地块数量
    counts = config.get_piece_land_block_counts(difficulty_key)
    endpoint_count = counts.get('endpoint', 0)
    
    # 生成所有可能的格子位置，排除起始区域
    excluded_cells = {f"{row},{col}" for row, col in start_area}
    all_positions = []
    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            key = f"{row},{col}"
            if key not in excluded_cells:
                all_positions.append(key)
    
    # 随机打乱位置数组
    random.shuffle(all_positions)
    available = len(all_positions)
    
    # 分配危险地块（这些格子仍然被迷雾覆盖）
    danger_slots = min(counts['danger'], available)
    for i in range(danger_slots):
        block_key = all_positions[i]
        danger_land_blocks.add(block_key)
        # 设置怪物的初始战力（普通怪物_N01，战力2~5随机）
        random_power = random.randint(2, 5)
        set_monster_initial_power(block_key, random_power)
    
    # 分配安全地块（治疗草）（这些格子仍然被迷雾覆盖）
    safe_slots = min(counts['safe'], max(0, available - danger_slots))
    for i in range(safe_slots):
        idx = danger_slots + i
        if idx < available:
            block_key = all_positions[idx]
            safe_land_blocks.add(block_key)
            safe_land_block_types[block_key] = 'heal'
    
    # 分配终点地块（作为安全地块的子项）（这些格子仍然被迷雾覆盖）
    endpoint_slots = min(endpoint_count, max(0, available - danger_slots - safe_slots))
    for i in range(endpoint_slots):
        idx = danger_slots + safe_slots + i
        if idx < available:
            block_key = all_positions[idx]
            safe_land_blocks.add(block_key)
            safe_land_block_types[block_key] = 'endpoint'

    # 更新统计信息
    total_danger_count = len(danger_land_blocks)
    total_safe_count = len(safe_land_blocks)
    total_piece_count = total_danger_count + total_safe_count

def _get_warrior_position_map():
    """获取勇士位置映射字典，提高查找效率
    Returns:
        dict: key为block_key，value为(warrior_letter, block_key)元组的列表
    """
    global warrior_blocks
    position_map = {}
    for warrior_letter, warrior_pos in warrior_blocks:
        if warrior_pos not in position_map:
            position_map[warrior_pos] = []
        position_map[warrior_pos].append((warrior_letter, warrior_pos))
    return position_map

def has_warriors_around(row, col):
    """检测指定格子周围8格是否有勇士方块"""
    # 构建位置映射以提高查找效率
    position_map = _get_warrior_position_map()
    
    # 检查周围8格
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            # 跳过中心格子
            if dr == 0 and dc == 0:
                continue
            
            new_row = row + dr
            new_col = col + dc
            
            # 检查是否在棋盘范围内
            if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
                block_key = f"{new_row},{new_col}"
                # 使用字典查找，O(1)复杂度
                if block_key in position_map:
                    return True
    
    return False

def get_warriors_around(row, col):
    """获取指定格子周围8格内的所有勇士方块，返回(warrior_letter, block_key)列表"""
    # 构建位置映射以提高查找效率
    position_map = _get_warrior_position_map()
    
    warriors = []
    found_positions = set()  # 用于避免重复添加同一个位置的勇士
    
    # 检查周围8格
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            # 跳过中心格子
            if dr == 0 and dc == 0:
                continue
            
            new_row = row + dr
            new_col = col + dc
            
            # 检查是否在棋盘范围内
            if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
                block_key = f"{new_row},{new_col}"
                # 避免重复添加同一个位置的勇士
                if block_key not in found_positions and block_key in position_map:
                    # 添加该位置的所有勇士
                    warriors.extend(position_map[block_key])
                    found_positions.add(block_key)
    
    return warriors

def get_monster_power(block_key):
    """获取怪物的当前战力
    如果怪物在monster_current_power字典中，返回当前战力
    否则返回初始战力（普通怪物_N01，战力2）
    注意：如果怪物已经被移除（不在danger_land_blocks中），返回0
    """
    global monster_current_power, danger_land_blocks
    
    # 检查怪物是否还存在
    if block_key not in danger_land_blocks:
        return 0
    
    # 如果怪物在字典中，返回当前战力
    if block_key in monster_current_power:
        return monster_current_power[block_key]
    
    # 否则生成随机初始战力（普通怪物_N01，战力2~5随机）并保存
    # 未来可以根据block_key或其他标识来区分不同怪物
    random_power = random.randint(2, 5)
    monster_current_power[block_key] = random_power
    return random_power

def get_monster_spirit_fire(block_key):
    """获取怪物的灵火值
    目前所有危险地块都是普通怪物_N01，灵火值2
    未来可以根据block_key或其他标识来区分不同怪物
    """
    # 检查怪物是否还存在
    global danger_land_blocks
    if block_key not in danger_land_blocks:
        return 0
    
    # 目前所有危险地块都是普通怪物_N01，灵火值2
    # 未来可以根据block_key或其他标识来区分不同怪物
    return 2

def add_spirit_fire(amount):
    """给玩家补充灵火值
    Args:
        amount: 要补充的灵火值
    """
    global current_spirit_fire, spirit_fire_zero_pending
    # 补充灵火值，不超过最大值
    current_spirit_fire = min(config.MAX_SPIRIT_FIRE, current_spirit_fire + amount)
    # 如果有外来补充，清除待处理标志（表示有外来补充，不需要扣血回灵火）
    if spirit_fire_zero_pending and current_spirit_fire > 0:
        spirit_fire_zero_pending = False

def set_monster_initial_power(block_key, power):
    """设置怪物的初始战力"""
    global monster_current_power
    monster_current_power[block_key] = power

def reduce_monster_power(block_key, reduction):
    """减少怪物的战力
    Args:
        block_key: 怪物的位置
        reduction: 要减少的战力值
    Returns:
        减少后的战力值，如果战力<=0则返回0
    """
    global monster_current_power
    
    # 获取当前战力
    current_power = get_monster_power(block_key)
    
    # 减少战力
    new_power = max(0, current_power - reduction)
    
    # 更新字典
    monster_current_power[block_key] = new_power
    
    # 如果战力为0，移除怪物，补充灵火值
    if new_power == 0:
        global danger_land_blocks
        # 在移除前获取怪物的灵火值
        monster_spirit_fire = get_monster_spirit_fire(block_key)
        danger_land_blocks.discard(block_key)
        monster_current_power.pop(block_key, None)
        # 补充怪物的灵火值给玩家
        if monster_spirit_fire > 0:
            add_spirit_fire(monster_spirit_fire)
    
    return new_power

def get_warrior_power(warrior_letter):
    """获取勇士的战力
    勇士的战力就是其字母对应的数字（'1'到'5'）
    """
    try:
        return int(warrior_letter)
    except ValueError:
        return 0

def calculate_total_warrior_power(warriors):
    """计算勇士总战力（简单相加，不考虑阵型）"""
    total = 0
    for warrior_letter, _ in warriors:
        total += get_warrior_power(warrior_letter)
    return total

def trigger_battle(block_key, warriors):
    """触发战斗流程
    Args:
        block_key: 怪物的位置
        warriors: 参与战斗的勇士列表，格式为[(warrior_letter, block_key), ...]
    """
    global current_hp, is_game_over, danger_land_blocks, warrior_blocks, available_deck_button_global
    
    # 获取怪物战力
    monster_power = get_monster_power(block_key)
    
    # 计算勇士总战力
    warrior_total_power = calculate_total_warrior_power(warriors)
    
    # 所有参与战斗的勇士进入弃牌堆（无论胜负）
    if available_deck_button_global:
        for warrior_letter, _ in warriors:
            available_deck_button_global.discard_cards.append(f"步兵_{warrior_letter}")
    
    # 从棋盘移除勇士（使用集合提高效率并避免重复移除）
    warriors_to_remove = set(warriors)
    warrior_blocks[:] = [w for w in warrior_blocks if w not in warriors_to_remove]
    
    # 战斗判定
    if warrior_total_power >= monster_power:
        # 勇士胜利：怪物被移除，补充灵火值
        monster_spirit_fire = get_monster_spirit_fire(block_key)
        danger_land_blocks.discard(block_key)
        # 补充怪物的灵火值给玩家
        if monster_spirit_fire > 0:
            add_spirit_fire(monster_spirit_fire)
    else:
        # 怪物胜利：怪物战力减少，玩家受到伤害
        remaining_power = reduce_monster_power(block_key, warrior_total_power)
        damage = remaining_power
        
        if damage > 0 and current_hp > 0:
            current_hp = max(0, current_hp - damage)
            start_screen_shake()
            
            # 检查游戏是否失败
            if current_hp == 0:
                is_game_over = True
    
    # 战斗结束后，检查灵火归零待处理标志（战斗可能会补充灵火）
    check_spirit_fire_zero()

def consume_spirit_fire():
    """消耗灵火值
    默认每次执行行动会消耗1点灵火值
    当灵火值归零时，设置待处理标志，等待检查是否有外来补充
    """
    global current_spirit_fire, spirit_fire_zero_pending
    
    if current_spirit_fire > 0:
        # 如果灵火值大于0，消耗1点
        current_spirit_fire = max(0, current_spirit_fire - 1)
        
        # 如果消耗后灵火值归零，设置待处理标志，等待检查是否有外来补充
        if current_spirit_fire == 0:
            spirit_fire_zero_pending = True
    else:
        # 如果灵火值已经是0，设置待处理标志
        spirit_fire_zero_pending = True

def check_spirit_fire_zero():
    """检查灵火归零待处理标志，如果没有外来补充则扣血回灵火
    应该在可能补充灵火的操作之后调用
    """
    global current_spirit_fire, current_hp, is_game_over, spirit_fire_zero_pending
    
    # 如果标志还在且灵火仍为0，说明没有外来补充，执行扣血回灵火
    if spirit_fire_zero_pending and current_spirit_fire == 0:
        if current_hp > 0:
            current_hp = max(0, current_hp - 1)
            start_screen_shake()
            
            # 检查游戏是否失败
            if current_hp == 0:
                is_game_over = True
        
        # 将灵火回满
        current_spirit_fire = config.MAX_SPIRIT_FIRE
        # 清除待处理标志
        spirit_fire_zero_pending = False

def trigger_danger_land_block_effect(block_key):
    """触发危险地块的特性（造成伤害或触发战斗）
    当怪物周围有勇士时，触发战斗
    当怪物周围没有勇士时，对玩家造成伤害
    """
    global current_hp, is_game_over
    
    # 检查是否是危险地块（怪物）
    if block_key not in danger_land_blocks:
        return
    
    # 安全解析坐标
    parsed = parse_block_key(block_key)
    if parsed is None:
        return
    row, col = parsed
    
    # 获取周围8格内的所有勇士
    warriors = get_warriors_around(row, col)
    
    # 调试：打印检测到的勇士信息
    # print(f"怪物位置: {block_key}, 检测到的勇士数量: {len(warriors)}, 勇士列表: {warriors}")
    
    if len(warriors) > 0:
        # 如果有勇士：触发战斗
        trigger_battle(block_key, warriors)
        # trigger_battle内部已经调用了check_spirit_fire_zero，这里不需要再调用
    else:
        # 如果没有勇士：对玩家造成伤害（目前所有危险地块都是普通怪物_N01，伤害1）
        if current_hp > 0:
            current_hp = max(0, current_hp - 1)
            start_screen_shake()
            
            # 检查游戏是否失败
            if current_hp == 0:
                is_game_over = True
        # 没有勇士时不会补充灵火，需要检查灵火归零待处理标志
        check_spirit_fire_zero()

def trigger_monster_reveal(block_key):
    """处理怪物现身触发：检测周围8格是否有勇士，没有则攻击玩家
    这是 trigger_danger_land_block_effect 的别名，保持向后兼容
    """
    trigger_danger_land_block_effect(block_key)

def has_three_connected_opened(row, col):
    """检查是否有3个相连的已打开格子（用于治疗草的发现条件）"""
    opened_positions = []
    
    # 收集周围8格中已打开的格子位置
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc
        if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
            block_key = f"{new_row},{new_col}"
            if block_key not in blocks:
                opened_positions.append((new_row, new_col))
    
    # 如果已打开的格子少于3个，直接返回False
    if len(opened_positions) < 3:
        return False
    
    # 检查是否有3个格子相连（使用BFS检查连通性）
    # 尝试从每个已打开的格子开始，看能否找到3个相连的格子
    for start_pos in opened_positions:
        visited = set()
        queue = deque([start_pos])
        visited.add(f"{start_pos[0]},{start_pos[1]}")
        
        # BFS搜索相连的已打开格子
        while queue and len(visited) < 3:
            r, c = queue.popleft()
            
            # 检查8个方向
            for dr, dc in directions:
                new_row = r + dr
                new_col = c + dc
                block_key = f"{new_row},{new_col}"
                
                # 检查是否在已打开的格子列表中且未访问过
                if (new_row, new_col) in opened_positions and block_key not in visited:
                    visited.add(block_key)
                    queue.append((new_row, new_col))
        
        # 如果找到了3个或更多相连的格子，返回True
        if len(visited) >= 3:
            return True
    
    return False

def trigger_safe_land_block_effect(block_key):
    """触发安全地块的特性（恢复生命）"""
    global current_hp, safe_land_blocks, used_safe_land_blocks
    
    # 一次性道具：如果已经使用过，则不再生效
    if block_key in used_safe_land_blocks:
        return
    
    # 标记为已使用
    used_safe_land_blocks.add(block_key)
    
    # 恢复1点生命值（不超过最大生命）
    if current_hp < config.MAX_HP:
        current_hp = min(config.MAX_HP, current_hp + 1)
    
    # 使用后从安全地块中移除，使该格子变成空格子
    safe_land_blocks.discard(block_key)

def are_all_monsters_defeated():
    """检查是否所有怪物都被消灭"""
    global danger_land_blocks
    return len(danger_land_blocks) == 0

def trigger_endpoint_land_block_effect(block_key):
    """触发终点地块的特性（胜利）"""
    global is_game_over, is_game_won, safe_land_blocks, safe_land_block_types
    if is_game_over or is_game_won:
        return
    # 只有在所有怪物都被消灭时才能触发胜利
    if not are_all_monsters_defeated():
        return
    is_game_won = True
    safe_land_blocks.discard(block_key)
    safe_land_block_types.pop(block_key, None)

def draw_safe_land_blocks(surface):
    """绘制安全地块（治疗草 - 绿色方块）"""
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 地块大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    # 绘制安全地块（治疗草 - 绿色方块）
    for block_key in safe_land_blocks:
        # 只绘制治疗草类型的地块
        if safe_land_block_types.get(block_key) != 'heal':
            continue
        # 只绘制没有被迷雾方块覆盖的地块
        if block_key not in blocks:
            parsed = parse_block_key(block_key)
            if parsed is None:
                continue
            row, col = parsed
            # 土地格子左上角位置（与draw_fog_blocks保持一致）
            land_x = padding_x_int + col * config.CELL_SIZE
            land_y = padding_y_int + row * config.CELL_SIZE
            
            if block_key in used_safe_land_blocks:
                # 已使用：绘制空心方块（变暗的绿色边框），大小与提示图案一致
                square_size = config.CELL_SIZE * 0.6 * 0.55  # 与提示图案大小一致：maxSize * 0.55
                center_x = padding_x_int + col * config.CELL_SIZE + config.CELL_SIZE / 2
                center_y = padding_y_int + row * config.CELL_SIZE + config.CELL_SIZE / 2
                
                # 绘制空心方块（变暗的绿色边框 #227722）
                rect = pygame.Rect(
                    int(center_x - square_size / 2),
                    int(center_y - square_size / 2),
                    int(square_size),
                    int(square_size)
                )
                pygame.draw.rect(surface, (34, 119, 34), rect, 2)  # #227722，线宽2
            else:
                # 未使用：亮绿色实心小方块（大小与提示图案一致）
                square_size = config.CELL_SIZE * 0.6 * 0.55  # 与提示图案大小一致：maxSize * 0.55
                center_x = padding_x_int + col * config.CELL_SIZE + config.CELL_SIZE / 2
                center_y = padding_y_int + row * config.CELL_SIZE + config.CELL_SIZE / 2
                
                # 绘制亮绿色实心方块（#44ff44）
                rect = pygame.Rect(
                    int(center_x - square_size / 2),
                    int(center_y - square_size / 2),
                    int(square_size),
                    int(square_size)
                )
                pygame.draw.rect(surface, (68, 255, 68), rect)  # #44ff44

def draw_endpoint_land_blocks(surface):
    """绘制终点地块（黄色圆圈）"""
    FOG_BLOCK_PADDING = 2
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2
    
    padding_x_int, padding_y_int = get_padding_int()
    
    # 检查是否所有怪物都被消灭
    all_monsters_defeated = are_all_monsters_defeated()
    
    # 绘制安全地块中的终点类型地块
    for block_key in safe_land_blocks:
        # 只绘制终点类型的地块
        if safe_land_block_types.get(block_key) != 'endpoint':
            continue
        if block_key not in blocks:
            parsed = parse_block_key(block_key)
            if parsed is None:
                continue
            row, col = parsed
            land_x = padding_x_int + col * config.CELL_SIZE
            land_y = padding_y_int + row * config.CELL_SIZE
            
            # 计算中心点（完全居中）
            center_x = land_x + config.CELL_SIZE / 2
            center_y = land_y + config.CELL_SIZE / 2
            radius = config.CELL_SIZE * 0.25 * 0.8
            
            # 根据任务完成状态选择颜色
            if all_monsters_defeated:
                # 任务完成：正常黄色圆圈
                pygame.draw.circle(surface, (255, 216, 75), (int(center_x), int(center_y)), int(radius), 2)
            else:
                # 任务未完成：灰暗外观（深灰色圆圈）
                pygame.draw.circle(surface, (100, 100, 100), (int(center_x), int(center_y)), int(radius), 2)

def draw_danger_land_blocks(surface):
    """绘制危险地块（怪物方块：深红色方块，中间有红色三角形）"""
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 地块大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    # 绘制危险地块（怪物方块）
    for block_key in danger_land_blocks:
        # 只绘制没有被迷雾方块覆盖的地块
        if block_key not in blocks:
            parsed = parse_block_key(block_key)
            if parsed is None:
                continue
            row, col = parsed
            # 土地格子左上角位置（与draw_fog_blocks保持一致）
            land_x = padding_x_int + col * config.CELL_SIZE
            land_y = padding_y_int + row * config.CELL_SIZE
            
            # 地块左上角位置（完全居中，每边2像素边距）
            offset = FOG_BLOCK_PADDING
            x = land_x + offset
            y = land_y + offset
            
            # 绘制怪物方块背景（深红色 #642828，参考勇士方块的蓝色）
            monster_rect = pygame.Rect(x, y, block_size, block_size)
            pygame.draw.rect(surface, (100, 40, 40), monster_rect)  # 深红色背景
            
            # 绘制红色三角形（在方块中间）
            # 三角形大小：地块大小的36%（参考网页版）
            triangle_size = block_size * 0.36
            # 计算中心点（转换为整数确保像素对齐）
            center_x = int(x + block_size / 2)
            center_y = int(y + block_size / 2)
            # 计算三角形尺寸（转换为整数确保对称）
            half_width = int(triangle_size / 2)
            height = int(triangle_size)
            
            # 三角形的三个顶点：顶点在上，底部两点在下（完全对称）
            top_y = center_y - height // 2
            bottom_y = center_y + height // 2
            
            # 绘制三角形（红色 #ff4444）
            triangle_points = [
                (center_x, top_y),  # 顶点（居中）
                (center_x - half_width, bottom_y),  # 左下角
                (center_x + half_width, bottom_y)  # 右下角
            ]
            pygame.draw.polygon(surface, (255, 68, 68), triangle_points)  # #ff4444

def draw_warrior_blocks(surface):
    """绘制勇士方块（蓝色方块和数字）"""
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 地块大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    global warrior_blocks, hovered_board_warrior, is_game_over, is_game_won
    # 初始化悬停状态
    hovered_board_warrior = None
    
    # 如果游戏失败或已获胜，不检测悬停
    if is_game_over or is_game_won:
        mouse_pos = None
    else:
        mouse_pos = pygame.mouse.get_pos()
    
    # 绘制勇士方块（蓝色方块）
    for warrior_letter, block_key in warrior_blocks:
        # 只绘制没有被迷雾方块覆盖的勇士方块
        if block_key not in blocks:
            parsed = parse_block_key(block_key)
            if parsed is None:
                continue
            row, col = parsed
            # 土地格子左上角位置（与draw_fog_blocks保持一致）
            land_x = padding_x_int + col * config.CELL_SIZE
            land_y = padding_y_int + row * config.CELL_SIZE
            
            # 地块左上角位置（完全居中，每边2像素边距）
            offset = FOG_BLOCK_PADDING
            x = land_x + offset
            y = land_y + offset
            
            # 绘制勇士方块背景（深蓝色）
            warrior_rect = pygame.Rect(x, y, block_size, block_size)
            
            # 检测鼠标悬停
            if mouse_pos is not None and warrior_rect.collidepoint(mouse_pos):
                hovered_board_warrior = (warrior_letter, block_key, warrior_rect.copy())
            
            pygame.draw.rect(surface, (30, 70, 140), warrior_rect)  # 深蓝色，提高与数字的对比度
            
            # 绘制勇士数字（与牌库中的勇士方块一致）
            # 创建字体（格子大小的50%），使用与牌库相同的字体获取方式
            font_size = int(config.CELL_SIZE * 0.5)
            warrior_font = get_font_with_fallback(font_size)
            # 使用与牌库相同的颜色配置
            letter_surface = warrior_font.render(warrior_letter, True, config.WARRIOR_LIST_SLOT_TEXT_COLOR)
            letter_rect = letter_surface.get_rect(center=(x + block_size / 2, y + block_size / 2))
            surface.blit(letter_surface, letter_rect)

def draw_number_hints(surface):
    """绘制数字提示层：显示每个已打开格子周围8格中棋子地块的总数"""
    # 只显示没有被迷雾方块覆盖的格子，且周围有棋子地块的格子
    # 数字颜色和样式：灰色 #3a3a3a，等宽字体，加粗，大小为格子大小的50%
    
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 地块大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    # 创建等宽字体（用于数字提示）
    # 字体大小：格子大小的50%，加粗
    font_size = int(config.CELL_SIZE * 0.5)
    number_font = None
    
    # 尝试使用Courier New（Windows/Mac）或Courier（Linux）
    font_names = ['Courier New', 'Courier', 'monospace']
    for font_name in font_names:
        try:
            number_font = pygame.font.SysFont(font_name, font_size, bold=True)
            # 测试字体是否可用
            test_surface = number_font.render('0', True, (255, 255, 255))
            if test_surface.get_width() > 0:
                break
        except (OSError, pygame.error, AttributeError):
            # 字体加载失败或不可用
            continue
    
    # 如果都失败，使用默认字体
    if number_font is None:
        try:
            number_font = pygame.font.Font(None, font_size)
        except (OSError, pygame.error):
            # 最后的备选方案
            try:
                number_font = pygame.font.Font(pygame.font.get_default_font(), font_size)
            except (OSError, pygame.error):
                # 如果所有方法都失败，创建一个最小字体
                number_font = pygame.font.Font(None, font_size)
    
    # 数字颜色：灰色（加深）#2d2d2d
    number_color = (45, 45, 45)  # #2d2d2d 加深后的数字颜色
    # 背景颜色：加深数字提示格子的背景颜色
    bg_color = (20, 20, 20)  # #141414 加深后的背景颜色
    
    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            block_key = f"{row},{col}"
            # 只显示已打开的格子（没有迷雾方块覆盖）
            if block_key not in blocks:
                # 如果该格子本身就是棋子地块，暴露后不再显示数字
                if is_piece_block(block_key):
                    continue
                
                # 计算周围棋子地块数量
                count = count_piece_land_blocks_around(row, col)
                if count > 0:
                    # 土地格子左上角位置（与draw_fog_blocks保持一致）
                    land_x = padding_x_int + col * config.CELL_SIZE
                    land_y = padding_y_int + row * config.CELL_SIZE
                    
                    # 地块左上角位置（完全居中，每边2像素边距）
                    offset = FOG_BLOCK_PADDING
                    x = land_x + offset
                    y = land_y + offset
                    
                    # 绘制背景矩形
                    bg_rect = pygame.Rect(x, y, block_size, block_size)
                    pygame.draw.rect(surface, bg_color, bg_rect)
                    
                    # 绘制数字（居中显示）
                    number_text = str(count)
                    number_surface = number_font.render(number_text, True, number_color)
                    number_rect = number_surface.get_rect(center=(x + block_size / 2, y + block_size / 2))
                    surface.blit(number_surface, number_rect)

def auto_reveal_blocks(start_row, start_col):
    """自动展开迷雾方块（以起点向四周扩散，带动画效果）"""
    global reveal_animation, reveal_animation_data
    
    # 如果已有动画在进行，先取消
    if reveal_animation_data is not None:
        reveal_animation_data = None
    
    # 使用队列进行广度优先搜索（BFS），收集需要打开的地块
    queue = deque([(start_row, start_col, 0)])  # (row, col, level)
    visited = set()
    blocks_to_reveal = []  # 按层级存储需要打开的地块
    
    # 8个方向的偏移量（上下左右和4个对角线）
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    # 收集所有需要打开的地块，按层级分组
    while queue:
        row, col, level = queue.popleft()
        block_key = f"{row},{col}"
        
        # 边界检查
        if row < 0 or row >= config.GRID_ROWS or col < 0 or col >= config.GRID_COLS:
            continue
        
        # 如果已经访问过，跳过
        if block_key in visited:
            continue
        
        # 如果该格子没有迷雾方块，跳过
        if block_key not in blocks:
            continue
        
        # 如果该格子被标记了，跳过（不自动翻开被标记的格子）
        if block_key in marked_blocks:
            continue
        
        # 如果该格子下有安全地块（包含治疗草和终点），不在扩散中自动翻开
        if block_key in safe_land_blocks:
            visited.add(block_key)
            continue
        
        # 标记为已访问
        visited.add(block_key)
        
        # 添加到待打开列表（按层级）
        while len(blocks_to_reveal) <= level:
            blocks_to_reveal.append([])
        blocks_to_reveal[level].append((row, col))
        
        # 检查当前格子周围是否有棋子地块，如果有则停止扩散
        has_piece_land_around = has_piece_land_blocks_around(row, col)
        
        # 如果当前格子周围有棋子地块，不继续扩散到周围格子
        if not has_piece_land_around:
            # 将周围8个格子加入队列继续扩散
            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc
                new_block_key = f"{new_row},{new_col}"
                
                # 检查边界和是否已访问，以及是否被标记
                if (0 <= new_row < config.GRID_ROWS and 
                    0 <= new_col < config.GRID_COLS and 
                    new_block_key not in visited and
                    new_block_key in blocks and
                    new_block_key not in marked_blocks):
                    queue.append((new_row, new_col, level + 1))
    
    # 如果没有需要打开的地块，直接返回
    if not blocks_to_reveal:
        return
    
    # 初始化动画数据
    reveal_animation_data = {
        'blocks_to_reveal': blocks_to_reveal,
        'current_level': 0,
        'last_frame_time': pygame.time.get_ticks(),
        'frame_delay': 30  # 每层之间的延迟（毫秒）
    }

# ==================== 绘制系统函数 ====================
def draw_board(surface):
    """绘制棋盘背景"""
    GRID_WIDTH = config.GRID_COLS * config.CELL_SIZE
    GRID_HEIGHT = config.GRID_ROWS * config.CELL_SIZE
    
    # 已删除棋盘背景绘制
    # 确保所有坐标计算基于整数，保持左右上下对称
    padding_x_int, padding_y_int = get_padding_int()
    
    # 绘制土地地块层（每个格子）
    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            # 使用统一的整数基准，确保像素对齐
            x = padding_x_int + col * config.CELL_SIZE
            y = padding_y_int + row * config.CELL_SIZE
            pygame.draw.rect(surface, config.LAND_COLOR, 
                           (x, y, config.CELL_SIZE, config.CELL_SIZE))
    
    # 已删除边框绘制
    
    # 绘制棋盘背景网格线
    # 绘制垂直线
    for i in range(config.GRID_COLS + 1):
        # 使用统一的整数基准，确保像素对齐
        x = padding_x_int + i * config.CELL_SIZE
        pygame.draw.line(surface, config.GRID_LINE_COLOR,
                        (x, padding_y_int),
                        (x, padding_y_int + config.GRID_ROWS * config.CELL_SIZE), 
                        config.GRID_LINE_WIDTH)
    
    # 绘制水平线
    for i in range(config.GRID_ROWS + 1):
        # 使用统一的整数基准，确保像素对齐
        y = padding_y_int + i * config.CELL_SIZE
        pygame.draw.line(surface, config.GRID_LINE_COLOR,
                        (padding_x_int, y),
                        (padding_x_int + config.GRID_COLS * config.CELL_SIZE, y),
                        config.GRID_LINE_WIDTH)

def draw_fog_blocks(surface):
    """绘制迷雾方块（根据格子大小动态计算，居中于每个土地格子）"""
    # 迷雾方块大小：格子大小 - 边距×2（参考网页版：getCurrentCellSize() - blockPadding * 2）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    FOG_BLOCK_SIZE = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 迷雾格子大小
    
    # 使用统一的整数基准，确保像素对齐（与土地格子使用相同的基准）
    padding_x_int, padding_y_int = get_padding_int()
    
    # 计算偏移量，确保四边距离一致
    # 迷雾方块距离格子边缘：每边FOG_BLOCK_PADDING像素
    offset = FOG_BLOCK_PADDING
    
    for block_key in blocks:
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        # 土地格子左上角位置（与draw_board中使用完全相同的计算方式）
        land_x = padding_x_int + col * config.CELL_SIZE
        land_y = padding_y_int + row * config.CELL_SIZE
        
        # 迷雾格子左上角位置：土地格子左上角 + 偏移量（完全居中，每边2像素边距）
        fog_x = land_x + offset
        fog_y = land_y + offset
        
        # 绘制迷雾方块（根据格子大小动态计算）
        # 如果该格子处于暴露状态，使用半透明颜色（加强不透明度，让暴露图标更不明显）
        if block_key in exposed_danger_blocks or block_key in exposed_safe_blocks:
            # 暴露状态：半透明迷雾（rgba(58, 58, 58, 0.99)）- 进一步弱化暴露图标
            fog_color = (*config.FOG_COLOR, 253)  # 255 * 0.99 ≈ 253
            fog_surface = pygame.Surface((FOG_BLOCK_SIZE, FOG_BLOCK_SIZE), pygame.SRCALPHA)
            fog_surface.fill(fog_color)
            surface.blit(fog_surface, (fog_x, fog_y))
        else:
            # 正常状态：不透明迷雾
            pygame.draw.rect(surface, config.FOG_COLOR, (fog_x, fog_y, FOG_BLOCK_SIZE, FOG_BLOCK_SIZE))

def draw_exposed_pieces_on_fog(surface):
    """在暴露状态下，将棋子图案透过半透明迷雾显示出来"""
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    block_size = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 地块大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    # 危险地块：绘制怪物方块（半透明：深红色方块，中间有红色三角形）
    for block_key in list(exposed_danger_blocks):
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，清除暴露状态
            exposed_danger_blocks.discard(block_key)
            continue
        
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        # 土地格子左上角位置（与draw_fog_blocks保持一致）
        land_x = padding_x_int + col * config.CELL_SIZE
        land_y = padding_y_int + row * config.CELL_SIZE
        
        # 地块左上角位置（完全居中，每边2像素边距）
        offset = FOG_BLOCK_PADDING
        x = land_x + offset
        y = land_y + offset
        
        # 创建半透明surface用于绘制怪物方块
        monster_surface = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
        
        # 绘制怪物方块背景（深红色，半透明）
        monster_rect = pygame.Rect(0, 0, block_size, block_size)
        pygame.draw.rect(monster_surface, (100, 40, 40, int(255 * 0.6)), monster_rect)  # 深红色背景，半透明
        
        # 绘制红色三角形（在方块中间，半透明）
        # 三角形大小：地块大小的36%（参考网页版）
        triangle_size = block_size * 0.36
        # 相对于surface的坐标（surface左上角为(0,0)），转换为整数确保像素对齐
        surface_center_x = int(block_size / 2)
        surface_center_y = int(block_size / 2)
        # 计算三角形尺寸（转换为整数确保对称）
        half_width = int(triangle_size / 2)
        height = int(triangle_size)
        
        # 三角形的三个顶点：顶点在上，底部两点在下（相对于surface的坐标，完全对称）
        top_y = surface_center_y - height // 2
        bottom_y = surface_center_y + height // 2
        
        # 绘制半透明三角形（红色 rgba(255, 68, 68, 0.6)）
        triangle_points = [
            (surface_center_x, top_y),  # 顶点（居中）
            (surface_center_x - half_width, bottom_y),  # 左下角
            (surface_center_x + half_width, bottom_y)  # 右下角
        ]
        pygame.draw.polygon(monster_surface, (255, 68, 68, int(255 * 0.6)), triangle_points)  # rgba(255, 68, 68, 0.6)
        surface.blit(monster_surface, (x, y))
    
    # 安全地块/终点：绘制对应真实外形（半透明）
    for block_key in list(exposed_safe_blocks):
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，清除暴露状态
            exposed_safe_blocks.discard(block_key)
            continue
        
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        center_x = padding_x_int + col * config.CELL_SIZE + config.CELL_SIZE / 2
        center_y = padding_y_int + row * config.CELL_SIZE + config.CELL_SIZE / 2
        
        if block_key in safe_land_blocks:
            block_type = safe_land_block_types.get(block_key, 'heal')
            if block_type == 'heal':
                # 治疗草：绘制绿色方块（半透明）
                square_size = config.CELL_SIZE * 0.6 * 0.55
                # 创建半透明surface用于绘制绿色方块
                square_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
                # 在surface上绘制矩形（相对于surface中心的坐标）
                rect = pygame.Rect(
                    int(config.CELL_SIZE / 2 - square_size / 2),  # 相对于surface中心的x坐标
                    int(config.CELL_SIZE / 2 - square_size / 2),  # 相对于surface中心的y坐标
                    int(square_size),
                    int(square_size)
                )
                pygame.draw.rect(square_surface, (68, 255, 68, int(255 * 0.6)), rect)  # rgba(68, 255, 68, 0.6)
                surface.blit(square_surface, (padding_x_int + col * config.CELL_SIZE, padding_y_int + row * config.CELL_SIZE))
            elif block_type == 'endpoint':
                # 终点：根据任务完成状态绘制不同外观（半透明）
                radius = config.CELL_SIZE * 0.25 * 0.8
                circle_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
                # 检查是否所有怪物都被消灭
                all_monsters_defeated = are_all_monsters_defeated()
                if all_monsters_defeated:
                    # 任务完成：正常黄色圆圈（半透明）
                    pygame.draw.circle(circle_surface, (255, 216, 75, int(255 * 0.6)),
                                      (int(config.CELL_SIZE / 2), int(config.CELL_SIZE / 2)),
                                      int(radius), 2)
                else:
                    # 任务未完成：灰暗外观（深灰色圆圈，半透明）
                    pygame.draw.circle(circle_surface, (100, 100, 100, int(255 * 0.6)),
                                      (int(config.CELL_SIZE / 2), int(config.CELL_SIZE / 2)),
                                      int(radius), 2)
                surface.blit(circle_surface, (padding_x_int + col * config.CELL_SIZE, padding_y_int + row * config.CELL_SIZE))

def get_danger_exposed_tooltip_lines(block_key):
    """获取危险地块的暴露提示信息"""
    # 获取怪物的当前战力
    current_power = get_monster_power(block_key)
    
    return [
        '名称：普通怪物_N01',
        f'战力：{current_power}',
        '伤害：1',
        '特性：每次被玩家点击到所在格子时，对玩家造成1点伤害'
    ]

def get_safe_exposed_tooltip_lines(block_key):
    """获取安全地块的暴露提示信息"""
    if block_key not in safe_land_blocks:
        return []
    
    block_type = safe_land_block_types.get(block_key, 'heal')
    if block_type == 'heal':
        return [
            '名称：治疗草',
            '效果：恢复1点生命'
        ]
    elif block_type == 'endpoint':
        # 检查是否所有怪物都被消灭
        all_monsters_defeated = are_all_monsters_defeated()
        global danger_land_blocks
        remaining_monsters = len(danger_land_blocks)
        
        if all_monsters_defeated:
            return [
                '名称：终点',
                '任务目标：消灭所有怪物',
                '状态：已完成',
                '点击后获得胜利'
            ]
        else:
            return [
                '名称：终点',
                '任务目标：消灭所有怪物',
                f'状态：剩余{remaining_monsters}个怪物',
                '完成目标后可点击'
            ]
    return []

def calculate_warrior_power_statistics(monster_key):
    """计算针对指定怪物的勇士战力统计
    返回：(total_power, formations_info)
    formations_info: 列表，每个元素是 (formation_type, warriors, base_power, bonus, total_power)
    """
    global warrior_blocks
    
    parsed = parse_block_key(monster_key)
    if parsed is None:
        return (0, [])
    row, col = parsed
    
    # 收集怪物周围8格内的勇士
    adjacent_warriors = []
    warrior_positions = {}  # block_key -> (warrior_letter, warrior_power)
    
    for warrior_letter, warrior_pos in warrior_blocks:
        parsed = parse_block_key(warrior_pos)
        if parsed is None:
            continue
        warrior_row, warrior_col = parsed
        # 检查是否在怪物周围8格内
        if abs(warrior_row - row) <= 1 and abs(warrior_col - col) <= 1:
            if warrior_row != row or warrior_col != col:  # 不包括怪物本身的位置
                warrior_power = int(warrior_letter)
                adjacent_warriors.append((warrior_letter, warrior_pos, warrior_power))
                warrior_positions[warrior_pos] = (warrior_letter, warrior_power)
    
    if not adjacent_warriors:
        return 0, []
    
    # 识别阵型（上下左右相连的勇士）
    def get_adjacent_positions(pos_key):
        """获取上下左右4个方向的相邻位置"""
        parsed = parse_block_key(pos_key)
        if parsed is None:
            return []
        r, c = parsed
        adjacent = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 上下左右
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < config.GRID_ROWS and 0 <= new_c < config.GRID_COLS:
                adjacent.append(f"{new_r},{new_c}")
        return adjacent
    
    # 使用BFS识别阵型
    visited = set()
    formations = []
    
    for warrior_letter, warrior_pos, warrior_power in adjacent_warriors:
        if warrior_pos in visited:
            continue
        
        # 从当前勇士开始，BFS查找所有相连的勇士
        formation_warriors = []
        queue = [warrior_pos]
        visited.add(warrior_pos)
        
        while queue:
            current_pos = queue.pop(0)
            if current_pos in warrior_positions:
                warrior_data = warrior_positions[current_pos]
                if warrior_data and len(warrior_data) >= 2:
                    formation_warriors.append(warrior_data)
            
            # 检查上下左右4个方向
            for adj_pos in get_adjacent_positions(current_pos):
                if adj_pos in warrior_positions and adj_pos not in visited:
                    visited.add(adj_pos)
                    queue.append(adj_pos)
        
        if formation_warriors:
            formations.append(formation_warriors)
    
    # 计算每个阵型的信息
    formations_info = []
    total_power = 0
    
    for formation in formations:
        # 计算基础战力（所有勇士战力之和）
        if not formation:
            continue
        try:
            base_power = sum(int(w[0]) for w in formation if w and isinstance(w, (tuple, list)) and len(w) > 0)
        except (ValueError, TypeError, IndexError):
            base_power = 0
        
        # 阵型加成（目前为0，未来可以扩展）
        bonus = 0
        
        # 阵型类型识别（简化版，未来可以更复杂）
        formation_type = "阵型"
        if len(formation) == 1:
            formation_type = "单独勇士"
        elif len(formation) == 2:
            formation_type = "双人阵型"
        elif len(formation) == 3:
            formation_type = "三人阵型"
        else:
            formation_type = f"{len(formation)}人阵型"
        
        total_formation_power = base_power + bonus
        total_power += total_formation_power
        
        formations_info.append((formation_type, formation, base_power, bonus, total_formation_power))
    
    return total_power, formations_info

def draw_warrior_power_statistics(surface, monster_key, x, y, target_height=None):
    """绘制勇士战力统计框（战斗预览面板左侧）
    参考怪物战力统计框的设计，左侧显示勇士信息，右侧有战力值框
    背景框大小和怪物战力统计框一样
    
    参数：
        surface: 绘制表面
        monster_key: 怪物位置
        x, y: 信息框的左上角坐标
        target_height: 目标高度（如果提供，使用此高度，使背景框大小和怪物战力统计框一致）
    """
    global warrior_blocks
    
    # 检查是否是怪物
    is_monster = monster_key in danger_land_blocks or monster_key in exposed_danger_blocks
    if not is_monster:
        return
    
    # 计算勇士战力统计
    total_power, formations_info = calculate_warrior_power_statistics(monster_key)
    
    # 如果没有勇士，不显示
    if total_power == 0 or not formations_info:
        return
    
    # 收集所有参与战斗的勇士（展平所有阵型）
    all_warriors = []
    for formation_type, formation, base_power, bonus, total_formation_power in formations_info:
        for warrior_data in formation:
            if warrior_data and len(warrior_data) >= 2:
                warrior_letter = warrior_data[0]
                warrior_power = warrior_data[1] if len(warrior_data) > 1 else int(warrior_letter)
                all_warriors.append((warrior_letter, warrior_power))
    
    if not all_warriors:
        return
    
    # 创建字体
    font_size = 14
    tooltip_font = get_font_with_fallback(font_size)
    name_font_size = 12
    name_font = get_font_with_fallback(name_font_size)
    power_font_size = 11
    power_font = get_font_with_fallback(power_font_size)
    plus_font_size = 16
    plus_font = get_font_with_fallback(plus_font_size)
    
    # 计算高度（如果提供了目标高度，使用目标高度；否则根据内容计算）
    padding = 12
    if target_height is not None:
        height = target_height
    else:
        # 估算高度：勇士方块大小 + 名字高度 + 战力高度 + 间距
        warrior_block_size = 40  # 勇士方块大小
        name_height_est = name_font.get_height()
        power_height_est = power_font.get_height()
        spacing = 4  # 各部分之间的间距
        estimated_height = warrior_block_size + spacing + name_height_est + spacing + power_height_est + padding * 2
        height = max(estimated_height, 80)  # 最小高度80像素
    
    # 右侧正方形空间（大小等于高度，用于战力值框）
    square_size = height
    
    # 计算勇士单元尺寸
    warrior_block_size = min(40, height - padding * 2 - 30)  # 勇士方块大小，留出名字和战力的空间
    warrior_unit_spacing = 8  # 勇士单元之间的间距（包括加号）
    plus_symbol_width = plus_font.render("+", True, (255, 255, 255)).get_width()
    
    # 计算每个勇士单元的宽度（方块 + 名字宽度 + 战力宽度，取最大值）
    max_name_width = 0
    max_power_width = 0
    for warrior_letter, warrior_power in all_warriors:
        warrior_name = f"步兵_{warrior_letter}"
        name_surface = name_font.render(warrior_name, True, (255, 255, 255))
        power_text = f"战力：{warrior_power}"
        power_surface = power_font.render(power_text, True, (255, 255, 255))
        max_name_width = max(max_name_width, name_surface.get_width())
        max_power_width = max(max_power_width, power_surface.get_width())
    
    warrior_unit_width = max(warrior_block_size, max_name_width, max_power_width)
    
    # 计算总宽度：内边距 + 勇士单元（包括加号） + 间距 + 正方形空间
    num_warriors = len(all_warriors)
    num_pluses = max(0, num_warriors - 1)  # 加号数量
    content_width = num_warriors * warrior_unit_width + num_pluses * (plus_symbol_width + warrior_unit_spacing)
    text_spacing = 8  # 内容与战力值框左边缘的间距
    width = padding + content_width + text_spacing + square_size
    
    # 绘制提示框背景
    bg_color = (15, 15, 15, 242)  # rgba(15, 15, 15, 0.95)
    tooltip_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    tooltip_surface.fill(bg_color)
    
    # 绘制提示框边框（蓝色，表示勇士信息）
    border_color = (74, 158, 255)  # #4a9eff
    pygame.draw.rect(tooltip_surface, border_color, (0, 0, width, height), 1)
    
    # 定义文本颜色
    text_color = (200, 220, 255)  # 浅蓝色
    
    # 绘制勇士单元（从右往左排列）
    content_start_x = padding  # 内容起始x坐标
    content_end_x = content_start_x + content_width  # 内容区域右边缘（战力值框左边缘 - text_spacing）
    
    # 计算垂直居中位置
    available_height = height - padding * 2
    warrior_block_size = min(40, available_height - 30)  # 勇士方块大小
    name_height = name_font.get_height()
    power_height = power_font.get_height()
    spacing = 4  # 各部分之间的间距
    total_unit_height = warrior_block_size + spacing + name_height + spacing + power_height
    unit_start_y = padding + (available_height - total_unit_height) / 2
    
    # 从右往左绘制
    current_x = content_end_x  # 从右侧开始
    
    for i, (warrior_letter, warrior_power) in enumerate(all_warriors):
        # 计算当前勇士单元的左边缘（从右往左）
        unit_left_x = current_x - warrior_unit_width
        
        # 计算当前勇士单元的中心x坐标
        unit_center_x = unit_left_x + warrior_unit_width / 2
        
        # 如果不是第一个，先绘制加号（在当前单元右侧）
        if i > 0:
            plus_x = current_x
            plus_y = unit_start_y + warrior_block_size / 2
            plus_surface = plus_font.render("+", True, text_color)
            plus_rect = plus_surface.get_rect(center=(plus_x + plus_symbol_width / 2, plus_y))
            tooltip_surface.blit(plus_surface, plus_rect)
        
        # 绘制勇士方块（深蓝色方块 + 灰色字母）
        block_x = unit_center_x - warrior_block_size / 2
        block_y = unit_start_y
        warrior_rect = pygame.Rect(block_x, block_y, warrior_block_size, warrior_block_size)
        pygame.draw.rect(tooltip_surface, (30, 70, 140), warrior_rect)  # 深蓝色背景，与棋盘上的勇士方块一致
        
        # 绘制勇士字母（灰色）
        letter_font_size = int(warrior_block_size * 0.5)
        letter_font = get_font_with_fallback(letter_font_size)
        letter_surface = letter_font.render(warrior_letter, True, (187, 187, 187))  # #bbb
        letter_rect = letter_surface.get_rect(center=(block_x + warrior_block_size / 2, block_y + warrior_block_size / 2))
        tooltip_surface.blit(letter_surface, letter_rect)
        
        # 绘制勇士名字（在方块下方）
        warrior_name = f"步兵_{warrior_letter}"
        name_surface = name_font.render(warrior_name, True, text_color)
        name_x = unit_center_x - name_surface.get_width() / 2
        name_y = block_y + warrior_block_size + spacing
        tooltip_surface.blit(name_surface, (name_x, name_y))
        
        # 绘制勇士战力（在名字下方）
        power_text = f"战力：{warrior_power}"
        power_surface = power_font.render(power_text, True, text_color)
        power_x = unit_center_x - power_surface.get_width() / 2
        power_y = name_y + name_height + spacing
        tooltip_surface.blit(power_surface, (power_x, power_y))
        
        # 移动到下一个位置（向左）
        current_x = unit_left_x - warrior_unit_spacing - plus_symbol_width
    
    # 绘制右侧战力值框
    box_margin = 8  # 战力值框与正方形区域边框的间距
    box_size = square_size - box_margin * 2
    
    # 计算战力值框位置（在右侧正方形区域内居中）
    box_x = width - square_size + box_margin  # 右侧正方形区域的起始x坐标 + 边距
    box_y = box_margin
    
    # 绘制战力值框（使用与提示框边框相同的颜色）
    pygame.draw.rect(tooltip_surface, border_color, (box_x, box_y, box_size, box_size), 2)
    
    # 绘制战力值数字（大字体，居中）
    power_font_size = int(box_size * 0.5)  # 字体大小为战力值框大小的50%
    power_font = get_font_with_fallback(power_font_size)
    power_text = str(total_power)
    power_surface = power_font.render(power_text, True, text_color)
    # 计算数字在战力值框内的居中位置
    power_rect = power_surface.get_rect(center=(box_x + box_size / 2, box_y + box_size / 2))
    tooltip_surface.blit(power_surface, power_rect)
    
    # 将提示框绘制到主surface上
    surface.blit(tooltip_surface, (x, y))
    
    # 返回信息框的尺寸，供调用者使用
    return width, height

def draw_exposed_tooltip(surface):
    """绘制暴露地块的信息提示框（鼠标悬停时显示）
    当怪物周围有勇士时，会显示战斗预览面板：
    - 左侧：勇士战力统计框
    - 右侧：怪物战力统计框
    当怪物周围没有勇士时，只显示怪物信息框（单独显示）
    """
    global hovered_cell, is_game_over, is_game_won
    
    if hovered_cell is None:
        return
    
    # 如果游戏失败或已获胜，不显示提示框
    if is_game_over or is_game_won:
        return
    
    block_key = f"{hovered_cell[0]},{hovered_cell[1]}"
    lines = None
    
    if block_key in exposed_danger_blocks:
        lines = get_danger_exposed_tooltip_lines(block_key)
    elif block_key in exposed_safe_blocks:
        lines = get_safe_exposed_tooltip_lines(block_key)
    elif block_key not in blocks:
        # 如果该格子没有迷雾（已打开），显示棋子地块的信息
        if block_key in danger_land_blocks:
            lines = get_danger_exposed_tooltip_lines(block_key)
        elif block_key in safe_land_blocks:
            lines = get_safe_exposed_tooltip_lines(block_key)
        # 注意：终点的提示信息还未实现，等实现后再添加
        else:
            return  # 非棋子地块且无暴露，不显示信息框
    else:
        return  # 仍有迷雾且未暴露，不显示信息框
    
    if not lines or len(lines) == 0:
        return
    
    # 创建等宽字体（用于提示框）
    font_size = 14
    tooltip_font = get_font_with_fallback(font_size)
    
    # 计算提示框大小
    padding = 12
    line_height = 18
    text_width = 0
    for line in lines:
        text_surface = tooltip_font.render(line, True, (255, 255, 255))
        text_width = max(text_width, text_surface.get_width())
    height = line_height * len(lines) + padding * 2
    # 左侧正方形空间（大小等于高度）
    square_size = height
    # 总宽度 = 正方形空间 + 文本区域宽度
    width = square_size + text_width + padding * 2
    
    # 获取窗口大小
    window_width, window_height = window.get_size()
    
    # 判断是危险地块还是安全地块
    is_danger = block_key in danger_land_blocks or block_key in exposed_danger_blocks
    
    # 检查是否是怪物且周围有勇士（用于判断是否显示战斗预览面板）
    has_warrior_stats = False
    formations_info = None
    stats_text_width = 0
    warrior_stats_height = 0
    
    if is_danger:
        _, formations_info = calculate_warrior_power_statistics(block_key)
        if formations_info:
            has_warrior_stats = True
            # 计算勇士战力统计框的文本宽度（用于布局计算）
            # 注意：实际宽度会在draw_warrior_power_statistics中根据target_height重新计算
            stats_font = tooltip_font  # 复用已创建的字体
            stats_line_height = line_height  # 复用已定义的常量
            
            # 计算文本行数（不包括总战力，因为总战力显示在右侧战力值框中）
            stats_lines = 1 + len(formations_info)  # 标题 + 每个阵型
            if len(formations_info) > 1:
                stats_lines += 1  # 多个阵型时，显示总战力计算过程
            
            # 构建文本并计算宽度（与draw_warrior_power_statistics中的逻辑一致）
            stats_lines_text = ["勇士战力统计："]
            for formation_type, formation, base_power, bonus, total_formation_power in formations_info:
                try:
                    warrior_list = " + ".join([f"勇士{w[0]}({int(w[0])})" for w in formation if w and len(w) > 0])
                except (ValueError, TypeError, IndexError):
                    warrior_list = "勇士(?)"
                if len(formation) > 1:
                    if bonus > 0:
                        line = f"{formation_type}：{warrior_list} = {base_power}，加成+{bonus}，总计{total_formation_power}"
                    else:
                        line = f"{formation_type}：{warrior_list} = {base_power}"
                else:
                    line = f"{formation_type}：{warrior_list} = {base_power}"
                stats_lines_text.append(line)
            
            if len(formations_info) > 1:
                try:
                    total_parts = [str(tp) for _, _, _, _, tp in formations_info]
                    total_sum = sum(tp for _, _, _, _, tp in formations_info)
                    total_line = "总战力：" + " + ".join(total_parts) + f" = {total_sum}"
                    stats_lines_text.append(total_line)
                except (ValueError, TypeError):
                    stats_lines_text.append("总战力：计算错误")
            
            # 计算文本宽度
            for line in stats_lines_text:
                text_surface = stats_font.render(line, True, (255, 255, 255))
                stats_text_width = max(stats_text_width, text_surface.get_width())
            
            # 计算高度（初始值，后面会根据怪物战力统计框的高度调整）
            warrior_stats_height = stats_line_height * stats_lines + padding * 2
            
    # 如果是战斗预览面板，计算怪物信息并调整框的尺寸
    monster_power = None
    monster_name = None
    name_font = None
    power_label_font = None
    name_width = 0
    name_height = 0
    power_label_width = 0
    power_label_height = 0
    if is_danger and has_warrior_stats:
        # 获取怪物信息（只获取一次，后续复用）
        monster_power = get_monster_power(block_key)
        monster_name = "普通怪物_N01"  # 从get_danger_exposed_tooltip_lines获取
        
        # 创建字体（与勇士框的字体大小完全一致）
        name_font_size = 12  # 与勇士框的名字字体大小一致
        name_font = get_font_with_fallback(name_font_size)
        power_label_font_size = 11  # 与勇士框的战力字体大小一致
        power_label_font = get_font_with_fallback(power_label_font_size)
        
        # 计算文本尺寸（用于宽度和高度计算，后续绘制时复用这些尺寸）
        name_surface_temp = name_font.render(monster_name, True, (255, 255, 255))
        power_label_text = f"战力：{monster_power}"
        power_label_surface_temp = power_label_font.render(power_label_text, True, (255, 255, 255))
        
        name_width = name_surface_temp.get_width()
        name_height = name_surface_temp.get_height()
        power_label_width = power_label_surface_temp.get_width()
        power_label_height = power_label_surface_temp.get_height()
        spacing = 8  # 各部分之间的间距
        
        # 如果只有一个怪物，根据实际内容计算高度，避免过多空白
        if len(formations_info) == 1:
            # 估算怪物外观大小（使用一个合理的估算值）
            monster_appearance_size_est = 50  # 估算值，约50像素
            # 计算实际内容高度
            actual_content_height = name_height + spacing + monster_appearance_size_est + spacing + power_label_height
            # 使用实际内容高度，但至少要与正方形空间匹配（正方形空间至少需要容纳战力值框）
            min_square_size = 60  # 最小正方形空间，确保战力值框有足够空间
            actual_height = max(actual_content_height + padding * 2, min_square_size)
            # 如果实际高度小于勇士战力统计框高度，使用实际高度；否则使用勇士战力统计框高度
            if actual_height < warrior_stats_height:
                height = actual_height
                square_size = height
                # 重新计算宽度（因为square_size改变了）
                width = square_size + text_width + padding * 2
        
        # 计算实际内容宽度并调整背景框宽度
        # 计算怪物外观大小（根据高度估算）
        available_height = height - padding * 2
        monster_appearance_size_est = available_height - name_height - power_label_height - spacing * 2
        monster_appearance_size_est = max(monster_appearance_size_est, 20)
        
        # 计算实际内容宽度（名称、外观、战力标签的最大宽度）
        actual_content_width = max(name_width, monster_appearance_size_est, power_label_width)
        
        # 减小内容与战力值框的间距，让内容更靠近战力值框
        text_spacing = 8  # 内容与战力值框右边缘的间距
        
        # 根据实际内容宽度重新计算背景框宽度
        square_size = height
        actual_width = square_size + text_spacing + actual_content_width + padding
        # 如果新宽度小于原宽度，使用新宽度
        if actual_width < width:
            width = actual_width
    
    # 计算战斗预览面板的布局
    gap = 20  # 两个框之间的间距
    
    # 计算整体宽度和高度
    if has_warrior_stats:
        # 战斗预览面板：勇士战力统计框 + 怪物战力统计框
        # 使用两个框中较大的高度作为统一高度，确保两个框高度一致
        total_height = max(warrior_stats_height, height)
        
        # 重新计算勇士战力统计框的实际宽度（基于total_height）
        # 需要与draw_warrior_power_statistics中的实际宽度计算保持一致
        # 宽度 = padding + content_width + text_spacing + square_size
        # 其中 content_width = num_warriors * warrior_unit_width + num_pluses * (plus_symbol_width + warrior_unit_spacing)
        
        # 计算勇士单元尺寸（与draw_warrior_power_statistics中的逻辑一致）
        warrior_stats_text_spacing = 8  # 内容与战力值框左边缘的间距
        square_size = total_height  # 右侧正方形空间（大小等于高度）
        
        # 计算勇士单元宽度（需要与draw_warrior_power_statistics中的计算一致）
        # 创建临时字体用于计算
        temp_name_font = get_font_with_fallback(12)
        temp_power_font = get_font_with_fallback(11)
        temp_plus_font = get_font_with_fallback(16)
        
        warrior_block_size_est = min(40, total_height - padding * 2 - 30)  # 勇士方块大小估算
        warrior_unit_spacing = 8  # 勇士单元之间的间距
        plus_symbol_width = temp_plus_font.render("+", True, (255, 255, 255)).get_width()
        
        # 计算每个勇士单元的宽度
        max_name_width = 0
        max_power_width = 0
        for formation_type, formation, base_power, bonus, total_formation_power in formations_info:
            for warrior_data in formation:
                if warrior_data and len(warrior_data) >= 2:
                    warrior_letter = warrior_data[0]
                    warrior_name = f"步兵_{warrior_letter}"
                    name_surface = temp_name_font.render(warrior_name, True, (255, 255, 255))
                    power_text = f"战力：{warrior_data[1] if len(warrior_data) > 1 else int(warrior_letter)}"
                    power_surface = temp_power_font.render(power_text, True, (255, 255, 255))
                    max_name_width = max(max_name_width, name_surface.get_width())
                    max_power_width = max(max_power_width, power_surface.get_width())
        
        warrior_unit_width = max(warrior_block_size_est, max_name_width, max_power_width)
        
        # 计算内容宽度
        num_warriors = sum(len(formation) for _, formation, _, _, _ in formations_info)
        num_pluses = max(0, num_warriors - 1)  # 加号数量
        content_width = num_warriors * warrior_unit_width + num_pluses * (plus_symbol_width + warrior_unit_spacing)
        
        # 计算实际宽度
        actual_warrior_stats_width = padding + content_width + warrior_stats_text_spacing + square_size
        
        # 计算整体位置（在画面正下方居中）
        total_y = window_height - total_height - 20  # 距离底部20像素
        
        # 计算各个信息框的位置
        # 策略：使勇士框和红色中轴线的间距等同于怪物框和红色中轴线的间距
        # 画面中轴线固定在屏幕中央（window_width / 2.0）
        
        # 画面中轴线位置（固定在屏幕中央）
        screen_center_x = window_width / 2.0
        
        # 先确定怪物框的位置（基于间距的中轴线，保持原有逻辑）
        # 间距的中轴线位置（固定在屏幕中央）
        gap_center_x = screen_center_x
        
        # 怪物框的左边缘 = 间距的中轴线 + 间距的一半
        tooltip_x = gap_center_x + gap / 2.0
        tooltip_y = total_y
        
        # 计算怪物框的左边缘距离画面中轴线的距离
        monster_left_distance_from_center = tooltip_x - screen_center_x
        
        # 勇士框的右边缘应该距离画面中轴线相同的距离（在左侧，所以是负值）
        warrior_stats_right_edge = screen_center_x - monster_left_distance_from_center
        
        # 计算勇士框的位置（左边缘）
        warrior_stats_x = warrior_stats_right_edge - actual_warrior_stats_width
        warrior_stats_y = total_y
    else:
        # 只有怪物信息框（单独显示）
        total_width = width
        total_height = height
        
        # 计算整体位置（在画面正下方居中）
        total_x = (window_width - total_width) // 2  # 整体水平居中
        total_y = window_height - total_height - 20  # 距离底部20像素
        
        # 只有怪物信息框，居中显示
        tooltip_x = total_x
        tooltip_y = total_y
    
    # 如果是战斗预览面板，使用total_height确保两个框的高度一致
    if has_warrior_stats:
        # 使用total_height作为实际高度
        actual_height = total_height
    else:
        # 单独显示时，使用原来的height
        actual_height = height
    
    # 绘制信息框背景（怪物信息框或怪物战力统计框）
    bg_color = (15, 15, 15, 242)  # rgba(15, 15, 15, 0.95) ≈ 242
    tooltip_surface = pygame.Surface((width, actual_height), pygame.SRCALPHA)
    tooltip_surface.fill(bg_color)
    
    # 绘制信息框边框
    # 在战斗预览面板中为怪物战力统计框，单独显示时为怪物信息框
    border_color = (255, 68, 68) if is_danger else (111, 226, 138)  # #ff4444 或 #6fe28a
    pygame.draw.rect(tooltip_surface, border_color, (0, 0, width, actual_height), 1)
    
    # 定义文本颜色（在绘制战力值之前定义）
    text_color = (255, 204, 204) if is_danger else (255, 221, 221)  # #ffcccc 或 #ffdddd
    
    # 左侧正方形空间
    square_size = actual_height
    
    # 如果是危险地块（怪物），绘制左侧战力值框
    if is_danger:
        # 怪物战力值已在前面计算过（在战斗预览面板的情况下）
        if monster_power is None:
            monster_power = get_monster_power(block_key)
        
        # 计算战力值框大小（尽可能大，但与边框保留间距）
        box_margin = 8  # 战力值框与正方形区域边框的间距
        box_size = square_size - box_margin * 2
        
        # 计算战力值框位置（在正方形区域内居中）
        box_x = box_margin
        box_y = box_margin
        
        # 绘制战力值框（使用与提示框边框相同的颜色）
        pygame.draw.rect(tooltip_surface, border_color, (box_x, box_y, box_size, box_size), 2)
        
        # 绘制战力值数字（大字体，居中）
        power_font_size = int(box_size * 0.5)  # 字体大小为战力值框大小的50%
        power_font = get_font_with_fallback(power_font_size)
        power_text = str(monster_power)
        power_surface = power_font.render(power_text, True, text_color)
        # 计算数字在战力值框内的居中位置
        power_rect = power_surface.get_rect(center=(box_x + box_size / 2, box_y + box_size / 2))
        tooltip_surface.blit(power_surface, power_rect)
    
    # 绘制右侧内容
    if is_danger and has_warrior_stats:
        # 在战斗预览面板中：显示怪物外观、名称和战力
        # 参考勇士框的布局：方块在上，名字在中，战力在下
        # 怪物信息和字体已在前面计算过，直接复用
        name_surface = name_font.render(monster_name, True, text_color)
        power_label_text = f"战力：{monster_power}"
        power_label_surface = power_label_font.render(power_label_text, True, text_color)
        
        # 复用前面计算的尺寸
        spacing = 4  # 各部分之间的间距（与勇士框一致）
        
        # 计算怪物方块大小（与勇士框中的勇士方块大小完全一致）
        # 勇士框的计算方式：warrior_block_size = min(40, available_height - 30)
        # 其中 available_height = height - padding * 2
        # 注意：勇士框的计算中没有减去name_height和power_height，所以怪物框也不应该减去
        available_height = actual_height - padding * 2
        monster_block_size = min(40, available_height - 30)  # 与勇士框计算方式完全一致
        
        # 减小内容与战力值框的间距，让内容更靠近战力值框
        text_spacing = 8  # 内容与战力值框右边缘的间距
        content_start_x = square_size + text_spacing  # 内容起始x坐标
        content_area_width = width - content_start_x - padding  # 内容区域宽度
        
        # 计算垂直布局（居中）
        total_content_height = monster_block_size + spacing + name_height + spacing + power_label_height
        content_start_y = padding + (available_height - total_content_height) / 2
        
        # 绘制怪物外观（怪物方块：深红色方块，中间有红色三角形）- 在上方
        appearance_x = content_start_x + (content_area_width - monster_block_size) / 2
        appearance_y = content_start_y
        appearance_center_x = appearance_x + monster_block_size / 2
        appearance_center_y = appearance_y + monster_block_size / 2
        
        # 绘制怪物方块背景（深红色，与draw_danger_land_blocks中的绘制方式一致）
        monster_rect = pygame.Rect(appearance_x, appearance_y, monster_block_size, monster_block_size)
        pygame.draw.rect(tooltip_surface, (100, 40, 40), monster_rect)  # 深红色背景
        
        # 绘制红色三角形（在方块中间）
        triangle_size = monster_block_size * 0.36
        half_width = int(triangle_size / 2)
        triangle_height = int(triangle_size)
        top_y = int(appearance_center_y - triangle_height / 2)
        bottom_y = int(appearance_center_y + triangle_height / 2)
        
        triangle_points = [
            (int(appearance_center_x), top_y),  # 顶点（居中）
            (int(appearance_center_x - half_width), bottom_y),  # 左下角
            (int(appearance_center_x + half_width), bottom_y)  # 右下角
        ]
        pygame.draw.polygon(tooltip_surface, (255, 68, 68), triangle_points)  # #ff4444
        
        # 绘制怪物名称（在方块下方）- 在中间
        name_x = content_start_x + (content_area_width - name_surface.get_width()) / 2
        name_y = appearance_y + monster_block_size + spacing
        tooltip_surface.blit(name_surface, (name_x, name_y))
        
        # 绘制怪物战力（在名字下方）- 在下方
        power_label_x = content_start_x + (content_area_width - power_label_surface.get_width()) / 2
        power_label_y = name_y + name_height + spacing
        tooltip_surface.blit(power_label_surface, (power_label_x, power_label_y))
    else:
        # 不在战斗预览面板中：显示原来的文本信息（怪物信息框）
        text_spacing = 12  # 内容与战力值框右边缘的间距
        content_start_x = square_size + text_spacing  # 内容起始x坐标
        content_area_width = width - content_start_x - padding  # 内容区域宽度
        for i, line in enumerate(lines):
            text_surface = tooltip_font.render(line, True, text_color)
            text_y = padding + line_height * i + line_height / 2
            # 文本左对齐，从content_start_x开始
            tooltip_surface.blit(text_surface, (content_start_x, text_y - text_surface.get_height() / 2))
    
    # 将信息框绘制到主surface上
    # 如果在战斗预览面板中，这是怪物战力统计框；否则是怪物信息框
    surface.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    # 如果是战斗预览面板，绘制勇士战力统计框（在左侧）
    if has_warrior_stats:
        # 使用和怪物战力统计框相同的高度，使背景框大小一致
        # 使用total_height确保两个框的高度完全一致
        draw_warrior_power_statistics(surface, block_key, warrior_stats_x, warrior_stats_y, target_height=total_height)

def draw_battle_range(surface):
    """绘制怪物的有效战斗范围（红色方框，表示玩家只有把勇士方块放在这个范围内才能触发战斗）
    在怪物处于暴露状态或已现身时显示
    """
    global hovered_cell, is_game_over, is_game_won, exposed_danger_blocks, danger_land_blocks, blocks
    
    # 如果游戏失败或已获胜，不显示战斗范围
    if is_game_over or is_game_won:
        return
    
    # 如果没有悬停的格子，不显示
    if hovered_cell is None:
        return
    
    row, col = hovered_cell
    block_key = f"{row},{col}"
    
    # 检查是否是暴露状态或已现身的怪物
    is_exposed_monster = block_key in exposed_danger_blocks
    is_revealed_monster = block_key in danger_land_blocks and block_key not in blocks
    
    # 如果不是怪物，不显示战斗范围
    if not is_exposed_monster and not is_revealed_monster:
        return
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    # 战斗范围颜色：弱化的红色（降低亮度和饱和度）
    battle_range_color = (153, 51, 51)  # 弱化的红色，约为原色的60%
    border_width = 1  # 边框宽度减小为1像素，更弱化
    
    # 计算怪物周围8格的位置并绘制红色方框
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            # 跳过怪物自身所在的格子
            if dr == 0 and dc == 0:
                continue
            
            new_row = row + dr
            new_col = col + dc
            
            # 检查是否在棋盘范围内
            if 0 <= new_row < config.GRID_ROWS and 0 <= new_col < config.GRID_COLS:
                # 计算格子的屏幕坐标
                cell_x = padding_x_int + new_col * config.CELL_SIZE
                cell_y = padding_y_int + new_row * config.CELL_SIZE
                
                # 绘制弱化的红色方框（边框）
                pygame.draw.rect(surface, battle_range_color, 
                               (cell_x, cell_y, config.CELL_SIZE, config.CELL_SIZE), 
                               border_width)

def draw_marks(surface):
    """绘制标记（在迷雾方块上）"""
    # 迷雾方块参数（与draw_fog_blocks保持一致）
    FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
    FOG_BLOCK_SIZE = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 迷雾格子大小
    
    # 使用统一的整数基准，确保像素对齐
    padding_x_int, padding_y_int = get_padding_int()
    
    for block_key in list(marked_blocks):  # 使用list避免在迭代时修改set
        if block_key not in blocks:
            # 如果该格子的迷雾已经被打开，移除标记
            marked_blocks.discard(block_key)
            continue
        
        parsed = parse_block_key(block_key)
        if parsed is None:
            continue
        row, col = parsed
        # 土地格子左上角位置（与draw_fog_blocks保持一致）
        land_x = padding_x_int + col * config.CELL_SIZE
        land_y = padding_y_int + row * config.CELL_SIZE
        
        # 迷雾方块左上角位置（完全居中，每边2像素边距）
        offset = FOG_BLOCK_PADDING
        fog_x = land_x + offset
        fog_y = land_y + offset
        
        # 迷雾方块中心位置（标记应该绘制在迷雾方块中心，而不是格子中心）
        center_x = fog_x + FOG_BLOCK_SIZE / 2
        center_y = fog_y + FOG_BLOCK_SIZE / 2
        mark_size = FOG_BLOCK_SIZE * 0.3  # 标记大小基于迷雾方块大小
        
        # 绘制浅灰色X
        half_size = mark_size / 2
        # X的第一条线（从左上到右下）
        pygame.draw.line(surface, config.MARK_COLOR,
                        (center_x - half_size, center_y - half_size),
                        (center_x + half_size, center_y + half_size), 2)
        # X的第二条线（从右上到左下）
        pygame.draw.line(surface, config.MARK_COLOR,
                        (center_x + half_size, center_y - half_size),
                        (center_x - half_size, center_y + half_size), 2)

def draw_game_over(surface):
    """绘制游戏失败提示"""
    global is_game_over
    
    if not is_game_over:
        return
    
    # 获取窗口大小
    window_width, window_height = window.get_size()
    
    # 绘制半透明黑色背景（rgba(0, 0, 0, 0.7)）
    overlay_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay_color = (0, 0, 0, int(255 * 0.7))  # rgba(0, 0, 0, 0.7) ≈ 178
    overlay_surface.fill(overlay_color)
    surface.blit(overlay_surface, (0, 0))
    
    # 绘制"你已死亡"文字（红色，60px，加粗，居中）
    # 使用支持中文的字体
    font_size = 60
    game_over_font = get_font_with_fallback(font_size, bold=True)
    
    text_surface = game_over_font.render('你已死亡', True, (255, 68, 68))  # 红色 #ff4444
    text_rect = text_surface.get_rect(center=(window_width / 2, window_height / 2))
    surface.blit(text_surface, text_rect)

def draw_game_win(surface):
    """绘制游戏胜利提示"""
    global is_game_won
    
    if not is_game_won:
        return
    
    window_width, window_height = window.get_size()
    
    overlay_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay_color = (0, 0, 0, int(255 * 0.5))
    overlay_surface.fill(overlay_color)
    surface.blit(overlay_surface, (0, 0))
    
    # 使用支持中文的字体
    font_size = 60
    win_font = get_font_with_fallback(font_size, bold=True)
    
    text_surface = win_font.render('游戏胜利', True, (255, 216, 75))
    text_rect = text_surface.get_rect(center=(window_width / 2, window_height / 2))
    surface.blit(text_surface, text_rect)

def draw_hover_highlight(surface):
    """绘制鼠标悬停高亮效果"""
    global hovered_cell
    
    if hovered_cell is None:
        return
    
    row, col = hovered_cell
    block_key = f"{row},{col}"
    
    # 如果该格子有迷雾方块，绘制悬停效果（半透明白色覆盖）
    if block_key in blocks:
        # 迷雾方块参数（与draw_fog_blocks保持一致）
        FOG_BLOCK_PADDING = 2  # 迷雾方块边距（每边2像素）
        FOG_BLOCK_SIZE = config.CELL_SIZE - FOG_BLOCK_PADDING * 2  # 迷雾格子大小
        
        # 使用统一的整数基准，确保像素对齐
        padding_x_int, padding_y_int = get_padding_int()
        
        # 土地格子左上角位置（与draw_fog_blocks保持一致）
        land_x = padding_x_int + col * config.CELL_SIZE
        land_y = padding_y_int + row * config.CELL_SIZE
        
        # 迷雾方块左上角位置（完全居中，每边2像素边距）
        offset = FOG_BLOCK_PADDING
        fog_x = land_x + offset
        fog_y = land_y + offset
        
        # 绘制半透明白色覆盖（rgba(255, 255, 255, 0.2)）
        highlight_surface = pygame.Surface((FOG_BLOCK_SIZE, FOG_BLOCK_SIZE), pygame.SRCALPHA)
        highlight_color = (255, 255, 255, int(255 * 0.2))  # rgba(255, 255, 255, 0.2)
        highlight_surface.fill(highlight_color)
        surface.blit(highlight_surface, (fog_x, fog_y))

def draw_health_bar(surface):
    """绘制玩家生命UI"""
    global current_hp
    
    # 血条参数
    health_bar_height = config.HEALTH_BAR_HEIGHT
    health_bar_width = config.HEALTH_BAR_WIDTH
    health_bar_y = config.HEALTH_BAR_Y
    label_x = config.HEALTH_BAR_LABEL_X
    label_spacing = config.HEALTH_BAR_LABEL_SPACING
    padding = config.HEALTH_BAR_PADDING
    border_width = config.HEALTH_BAR_BORDER_WIDTH
    
    # 获取字体
    font_medium = font_manager.get_medium()  # 用于标签
    font_small = font_manager.get_small()  # 用于数值
    
    # 测量标签宽度
    label_text = "生命"
    label_surface = font_medium.render(label_text, True, config.HEALTH_BAR_TEXT_COLOR)
    label_width = label_surface.get_width()
    
    # 计算整体宽度（生命UI + 间距 + 灵火UI）
    window_width, _ = window.get_size()
    
    # 测量灵火标签宽度（用于计算整体宽度）
    spirit_fire_label_text = "灵火"
    spirit_fire_label_surface = font_medium.render(spirit_fire_label_text, True, config.SPIRIT_FIRE_BAR_TEXT_COLOR)
    spirit_fire_label_width = spirit_fire_label_surface.get_width()
    
    # 计算整体宽度：
    # 生命标签 + 间距 + 生命条 + 两个条之间的间距 + 灵火条 + 间距 + 灵火标签
    total_width = (label_width + label_spacing + health_bar_width + 
                   config.SPIRIT_FIRE_BAR_SPACING + 
                   config.SPIRIT_FIRE_BAR_WIDTH + label_spacing + spirit_fire_label_width)
    
    # 计算整体居中的起始位置
    overall_start_x = (window_width - total_width) / 2
    
    # 计算生命UI的位置（整体左侧）
    health_bar_x = overall_start_x + label_width + label_spacing
    label_x = overall_start_x  # 生命标签在最左侧
    label_y = health_bar_y + health_bar_height / 2
    
    # 绘制"生命"标签
    label_rect = label_surface.get_rect(midleft=(label_x, label_y))
    surface.blit(label_surface, label_rect)
    
    # 绘制血条背景（深灰色）
    pygame.draw.rect(surface, config.HEALTH_BAR_BG_COLOR, 
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    
    # 绘制血条边框
    pygame.draw.rect(surface, config.HEALTH_BAR_BORDER_COLOR,
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 
                    border_width)
    
    # 计算当前血量对应的宽度
    current_width = (current_hp / config.MAX_HP) * health_bar_width
    
    # 绘制当前血量（绿色，带内边距）
    if current_width > 0:
        # 由于pygame不支持直接的外发光效果，我们绘制一个稍微放大的血量条模拟外发光
        # 先绘制外发光层（半透明，稍微放大）
        glow_width = max(0, current_width - padding * 2 + 4)  # 稍微放大
        glow_height = health_bar_height - padding * 2 + 4
        
        if glow_width > 0:
            glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
            # 外发光颜色（半透明）
            glow_color = (*config.HEALTH_BAR_SHADOW_COLOR, int(255 * 0.4))
            glow_surface.fill(glow_color)
            surface.blit(glow_surface, 
                        (health_bar_x + padding - 2, health_bar_y + padding - 2))
        
        # 绘制血量条（绿色）
        fill_rect = pygame.Rect(
            health_bar_x + padding,
            health_bar_y + padding,
            max(0, current_width - padding * 2),
            health_bar_height - padding * 2
        )
        pygame.draw.rect(surface, config.HEALTH_BAR_FILL_COLOR, fill_rect)
    
    # 绘制血条数值（当前/最大）
    value_text = f"{current_hp}/{config.MAX_HP}"
    value_surface = font_small.render(value_text, True, config.HEALTH_BAR_VALUE_COLOR)
    value_rect = value_surface.get_rect(center=(health_bar_x + health_bar_width / 2, 
                                                 health_bar_y + health_bar_height / 2))
    surface.blit(value_surface, value_rect)


def draw_spirit_fire_bar(surface):
    """绘制玩家灵火UI"""
    global current_spirit_fire
    
    # 灵火条参数
    spirit_fire_bar_height = config.SPIRIT_FIRE_BAR_HEIGHT
    spirit_fire_bar_width = config.SPIRIT_FIRE_BAR_WIDTH
    spirit_fire_bar_y = config.SPIRIT_FIRE_BAR_Y
    label_spacing = config.HEALTH_BAR_LABEL_SPACING
    padding = config.SPIRIT_FIRE_BAR_PADDING
    border_width = config.SPIRIT_FIRE_BAR_BORDER_WIDTH
    spacing = config.SPIRIT_FIRE_BAR_SPACING
    
    # 获取字体
    font_medium = font_manager.get_medium()  # 用于标签
    font_small = font_manager.get_small()  # 用于数值
    
    # 计算整体宽度（与draw_health_bar中的计算保持一致）
    window_width, _ = window.get_size()
    
    # 测量标签宽度
    label_text = "生命"
    health_label_surface = font_medium.render(label_text, True, config.HEALTH_BAR_TEXT_COLOR)
    health_label_width = health_label_surface.get_width()
    
    # 测量灵火标签宽度
    spirit_fire_label_text = "灵火"
    spirit_fire_label_surface = font_medium.render(spirit_fire_label_text, True, config.SPIRIT_FIRE_BAR_TEXT_COLOR)
    spirit_fire_label_width = spirit_fire_label_surface.get_width()
    
    # 计算整体宽度（与draw_health_bar保持一致）
    # 生命标签 + 间距 + 生命条 + 两个条之间的间距 + 灵火条 + 间距 + 灵火标签
    total_width = (health_label_width + label_spacing + config.HEALTH_BAR_WIDTH + 
                   spacing + 
                   spirit_fire_bar_width + label_spacing + spirit_fire_label_width)
    
    # 计算整体居中的起始位置
    overall_start_x = (window_width - total_width) / 2
    
    # 计算生命UI的位置（用于定位灵火UI）
    health_bar_x = overall_start_x + health_label_width + label_spacing
    
    # 计算灵火条位置（在生命条右侧，中间有间距）
    spirit_fire_bar_x = health_bar_x + config.HEALTH_BAR_WIDTH + spacing
    
    # 计算灵火标签位置（在灵火条右边）
    label_x = spirit_fire_bar_x + spirit_fire_bar_width + label_spacing
    label_y = spirit_fire_bar_y + spirit_fire_bar_height / 2
    
    # 使用已测量的标签表面
    label_surface = spirit_fire_label_surface
    label_width = spirit_fire_label_width
    
    # 绘制"灵火"标签（在灵火条右侧）
    label_rect = label_surface.get_rect(midleft=(label_x, label_y))
    surface.blit(label_surface, label_rect)
    
    # 绘制灵火条背景（深灰色）
    pygame.draw.rect(surface, config.SPIRIT_FIRE_BAR_BG_COLOR, 
                    (spirit_fire_bar_x, spirit_fire_bar_y, spirit_fire_bar_width, spirit_fire_bar_height))
    
    # 绘制灵火条边框
    pygame.draw.rect(surface, config.SPIRIT_FIRE_BAR_BORDER_COLOR,
                    (spirit_fire_bar_x, spirit_fire_bar_y, spirit_fire_bar_width, spirit_fire_bar_height), 
                    border_width)
    
    # 计算当前灵火值对应的宽度
    current_width = (current_spirit_fire / config.MAX_SPIRIT_FIRE) * spirit_fire_bar_width
    
    # 绘制当前灵火值（蓝色，带内边距）
    if current_width > 0:
        # 由于pygame不支持直接的外发光效果，我们绘制一个稍微放大的灵火条模拟外发光
        # 先绘制外发光层（半透明，稍微放大）
        glow_width = max(0, current_width - padding * 2 + 4)  # 稍微放大
        glow_height = spirit_fire_bar_height - padding * 2 + 4
        
        if glow_width > 0:
            glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
            # 外发光颜色（半透明）
            glow_color = (*config.SPIRIT_FIRE_BAR_SHADOW_COLOR, int(255 * 0.4))
            glow_surface.fill(glow_color)
            surface.blit(glow_surface, 
                        (spirit_fire_bar_x + padding - 2, spirit_fire_bar_y + padding - 2))
        
        # 绘制灵火条（蓝色）
        fill_rect = pygame.Rect(
            spirit_fire_bar_x + padding,
            spirit_fire_bar_y + padding,
            max(0, current_width - padding * 2),
            spirit_fire_bar_height - padding * 2
        )
        pygame.draw.rect(surface, config.SPIRIT_FIRE_BAR_FILL_COLOR, fill_rect)
    
    # 绘制灵火条数值（当前/最大）
    value_text = f"{current_spirit_fire}/{config.MAX_SPIRIT_FIRE}"
    value_surface = font_small.render(value_text, True, config.SPIRIT_FIRE_BAR_VALUE_COLOR)
    value_rect = value_surface.get_rect(center=(spirit_fire_bar_x + spirit_fire_bar_width / 2, 
                                                 spirit_fire_bar_y + spirit_fire_bar_height / 2))
    surface.blit(value_surface, value_rect)


def draw_game_stats(surface):
    """绘制地块统计信息（左下角）"""
    global total_piece_count, total_danger_count, total_safe_count
    
    if total_piece_count <= 0:
        return
    
    lines = [
        '地块信息统计',
        f'棋子地块：{total_piece_count}',
        f'危险地块：{total_danger_count}',
        f'安全地块：{total_safe_count}'
    ]
    
    padding = 12
    line_height = 18
    
    # 创建字体（等宽字体，便于对齐）
    font_size = 14
    stats_font = get_font_with_fallback(font_size)
    
    # 计算宽高
    width = 0
    for line in lines:
        text_surface = stats_font.render(line, True, (255, 255, 255))
        width = max(width, text_surface.get_width())
    box_width = width + padding * 2
    box_height = line_height * len(lines) + padding * 2
    
    # 定位左下角
    _, window_height = window.get_size()
    box_x = 12
    box_y = window_height - box_height - 12
    
    # 背景
    stats_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    stats_surface.fill((10, 10, 10, int(255 * 0.7)))
    pygame.draw.rect(stats_surface, (255, 255, 255, int(255 * 0.15)), 
                     (0, 0, box_width, box_height), 1)
    
    # 绘制文本
    text_color = (138, 138, 138)
    for i, line in enumerate(lines):
        text_surface = stats_font.render(line, True, text_color)
        text_y = padding + i * line_height
        stats_surface.blit(text_surface, (padding, text_y))
    
    surface.blit(stats_surface, (box_x, box_y))


def draw_warrior_drop_highlight(surface):
    """绘制勇士拖拽可放置高亮"""
    if warrior_drop_target is None:
        return
    
    row, col = warrior_drop_target
    block_key = f"{row},{col}"
    
    if not is_valid_warrior_drop(block_key):
        return
    
    padding_x_int, padding_y_int = get_padding_int()
    land_x = padding_x_int + col * config.CELL_SIZE
    land_y = padding_y_int + row * config.CELL_SIZE
    
    highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
    highlight_surface.fill((74, 158, 255, int(255 * 0.3)))
    surface.blit(highlight_surface, (land_x, land_y))
    
    pygame.draw.rect(surface, (74, 158, 255), (land_x, land_y, config.CELL_SIZE, config.CELL_SIZE), 2)


# ==================== 游戏循环框架 ====================
class GameLoop:
    """游戏循环管理器"""
    
    def __init__(self):
        """初始化游戏循环"""
        self.running = False
        self.resolution_selector = ResolutionSelector(
            config.RESOLUTION_SELECTOR_X, 
            config.RESOLUTION_SELECTOR_Y,
            font_manager.get_small()
        )
        self.difficulty_selector = DifficultySelector(font_manager.get_small())
        self.reset_button = ResetButton(font_manager.get_medium(), self)
        self.available_deck_button = AvailableDeckWindowButton(font_manager.get_medium(), label="可用牌组", offset=-115)
        # 设置全局引用，以便战斗系统可以访问弃牌堆
        global available_deck_button_global
        available_deck_button_global = self.available_deck_button
        self.warrior_list = WarriorList(font_manager.get_medium(), available_deck_button=self.available_deck_button)
        self.warrior_deck_button = WarriorDeckButton(font_manager.get_medium(), available_deck_button=self.available_deck_button, game_loop_ref=self)
    
    def init(self):
        """初始化游戏"""
        # 初始化地图大小选择器位置
        self.difficulty_selector.update_position()
        
        # 根据当前难度初始化网格大小（这已经包含了initialize_blocks、initialize_piece_land_blocks和update_padding）
        self.difficulty_selector.update_difficulty()
        
        # 每次开局时执行一次重置牌组
        self.warrior_deck_button.reset_deck()
        
        # 每次开局时执行一次重置牌组
        self.warrior_deck_button.reset_deck()
    
    def handle_events(self):
        """处理所有事件"""
        deck_buttons = [self.available_deck_button, self.warrior_deck_button]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
            
            # 处理鼠标移动事件（需要先处理，用于悬停高亮）
            if event.type == pygame.MOUSEMOTION:
                global hovered_cell, is_game_over, is_game_won, warrior_drop_target
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 如果任意牌库窗口打开，优先处理窗口事件
                deck_window_active = False
                for deck_button in deck_buttons:
                    if deck_button.open or deck_button.is_resizing:
                        deck_button.handle_event(event)
                        deck_window_active = True
                if deck_window_active:
                    # 窗口打开时或正在调整大小时，不处理棋盘悬停与拖拽
                    hovered_cell = None
                    warrior_drop_target = None
                    continue
                
                # 先处理UI组件的鼠标移动事件（用于下拉菜单悬停效果）
                self.difficulty_selector.handle_event(event)
                self.resolution_selector.handle_event(event)
                self.reset_button.handle_event(event)  # 重置按钮不需要移动事件处理，但保持一致性
                self.warrior_deck_button.handle_event(event)  # 勇士牌库按钮
                
                # 如果游戏失败或已获胜，禁用棋盘悬停
                if is_game_over or is_game_won:
                    hovered_cell = None
                    continue
                
                # 检查鼠标是否在UI组件区域内
                mouse_on_ui = False
                # 检查分辨率选择器
                res_button_rect = pygame.Rect(
                    self.resolution_selector.button_x,
                    self.resolution_selector.button_y,
                    self.resolution_selector.button_width,
                    self.resolution_selector.button_height
                )
                if res_button_rect.collidepoint(mouse_x, mouse_y):
                    mouse_on_ui = True
                if self.resolution_selector.open:
                    for i in range(len(self.resolution_selector.options)):
                        option_y = self.resolution_selector.button_y + self.resolution_selector.button_height + i * self.resolution_selector.option_height
                        option_rect = pygame.Rect(
                            self.resolution_selector.button_x,
                            option_y,
                            self.resolution_selector.options_box_width,
                            self.resolution_selector.option_height
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            mouse_on_ui = True
                            break
                
                # 检查地图大小选择器
                diff_button_rect = pygame.Rect(
                    self.difficulty_selector.button_x,
                    self.difficulty_selector.button_y,
                    self.difficulty_selector.button_width,
                    self.difficulty_selector.button_height
                )
                if diff_button_rect.collidepoint(mouse_x, mouse_y):
                    mouse_on_ui = True
                if self.difficulty_selector.open:
                    for i in range(len(self.difficulty_selector.options)):
                        option_y = self.difficulty_selector.button_y + self.difficulty_selector.button_height + i * self.difficulty_selector.option_height
                        option_rect = pygame.Rect(
                            self.difficulty_selector.button_x,
                            option_y,
                            self.difficulty_selector.options_box_width,
                            self.difficulty_selector.option_height
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            mouse_on_ui = True
                            break
                
                # 勇士拖拽高亮
                if self.warrior_list.is_dragging and not (is_game_over or is_game_won):
                    grid_pos = get_grid_position(mouse_x, mouse_y)
                    if grid_pos is not None:
                        row, col = grid_pos
                        block_key = f"{row},{col}"
                        if is_valid_warrior_drop(block_key):
                            warrior_drop_target = grid_pos
                        else:
                            warrior_drop_target = None
                    else:
                        warrior_drop_target = None
                else:
                    warrior_drop_target = None
                
                # 如果不在UI组件上，处理棋盘悬停
                if not mouse_on_ui:
                    grid_pos = get_grid_position(mouse_x, mouse_y)
                    if grid_pos is not None:
                        # 只有当格子位置改变时才更新
                        if hovered_cell is None or hovered_cell != grid_pos:
                            hovered_cell = grid_pos
                    else:
                        # 鼠标不在网格上，清除悬停状态
                        hovered_cell = None
            
            # 处理点击事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                ui_clicked = False
                
                # 优先处理任意牌库窗口（如果打开，阻止所有其他事件）
                # 特别注意：如果正在调整大小，必须处理 MOUSEBUTTONUP 事件来停止调整
                deck_window_active = False
                for deck_button in deck_buttons:
                    if deck_button.open or deck_button.is_resizing:
                        if deck_button.handle_event(event):
                            ui_clicked = True
                        deck_window_active = True
                if deck_window_active:
                    # 窗口打开时或正在调整大小时，不处理其他事件
                    continue
                
                # 优先处理勇士列表拖拽事件（需要在其他UI组件之前处理）
                if self.warrior_list.handle_event(event):
                    ui_clicked = True
                # 优先处理UI组件点击事件
                elif self.reset_button.handle_event(event):
                    # 如果点击了重置按钮，reset_game已经处理了所有重置
                    ui_clicked = True
                elif self.difficulty_selector.handle_event(event):
                    # 如果难度改变，update_difficulty已经处理了所有更新
                    ui_clicked = True
                elif self.available_deck_button.handle_event(event):
                    ui_clicked = True
                elif self.warrior_deck_button.handle_event(event):
                    # 勇士牌库按钮点击（窗口未打开时）
                    ui_clicked = True
                elif self.resolution_selector.handle_event(event):
                    # 如果分辨率改变，更新内边距并重新初始化迷雾
                    update_padding()
                    current_diff = self.difficulty_selector.options[self.difficulty_selector.current]
                    reset_game(current_diff, self)
                    # 更新地图大小选择器位置（窗口大小改变）
                    self.difficulty_selector.update_position()
                    # 更新绘制系统的surface
                    global drawer
                    drawer = DrawSystem(window.screen)
                    ui_clicked = True
                
                # 如果UI组件没有处理点击事件，处理棋盘点击
                # 如果游戏失败或已获胜，禁用棋盘点击
                if not ui_clicked and not is_game_over and not is_game_won:
                    grid_pos = get_grid_position(mouse_x, mouse_y)
                    
                    if grid_pos is not None:
                        row, col = grid_pos
                        block_key = f"{row},{col}"
                        
                        if event.button == 1:  # 左键点击
                            # 如果该格子被标记了，不能通过左键点击翻开
                            if block_key in marked_blocks:
                                continue
                            
                            # 如果该格子有迷雾方块
                            if block_key in blocks:
                                # 消耗灵火值（打开迷雾方块是行动）
                                consume_spirit_fire()
                                
                                # 检查该格子下是否有危险地块或安全地块（包含治疗草和终点）
                                has_danger = block_key in danger_land_blocks
                                has_safe = block_key in safe_land_blocks
                                
                                if has_danger:
                                    # 如果有危险地块，只打开当前格子不扩散
                                    blocks.remove(block_key)
                                    if block_key in marked_blocks:
                                        marked_blocks.remove(block_key)
                                    # 怪物现身触发：检测周围8格是否有勇士，没有则攻击玩家
                                    trigger_monster_reveal(block_key)
                                elif has_safe:
                                    # 如果有安全地块（治疗草或终点），只打开迷雾，不触发扩散，也不使用
                                    blocks.remove(block_key)
                                    if block_key in marked_blocks:
                                        marked_blocks.remove(block_key)
                                else:
                                    # 如果该格子没有危险/安全地块，执行自动展开（扩散）
                                    auto_reveal_blocks(row, col)
                                    # 自动展开不会立即触发战斗，需要检查灵火归零待处理标志
                                    check_spirit_fire_zero()
                            # 如果该格子没有迷雾方块（已打开）
                            else:
                                # 检查是否有地块
                                if block_key in danger_land_blocks:
                                    # 消耗灵火值（点击危险地块是行动）
                                    consume_spirit_fire()
                                    # 点击已打开的危险地块，仍然造成伤害
                                    trigger_danger_land_block_effect(block_key)
                                elif block_key in safe_land_blocks:
                                    # 点击已打开的安全地块，根据类型处理
                                    block_type = safe_land_block_types.get(block_key, 'heal')
                                    if block_type == 'heal':
                                        # 使用治疗草（恢复生命）
                                        trigger_safe_land_block_effect(block_key)
                                    elif block_type == 'endpoint':
                                        # 只有在所有怪物都被消灭时才能点击终点
                                        if are_all_monsters_defeated():
                                            # 消耗灵火值（点击终点是行动）
                                            consume_spirit_fire()
                                            # 触发胜利
                                            trigger_endpoint_land_block_effect(block_key)
                                        # 如果任务未完成，不执行任何操作（终点无法点击）
                        
                        elif event.button == 3:  # 右键点击
                            # 如果游戏失败或已获胜，禁用右键标记
                            if is_game_over or is_game_won:
                                continue
                            
                            # 如果该格子有迷雾方块，切换标记状态
                            if block_key in blocks:
                                if block_key in marked_blocks:
                                    # 如果已标记，则取消标记
                                    marked_blocks.remove(block_key)
                                else:
                                    # 如果未标记，则添加标记
                                    marked_blocks.add(block_key)
            
            # 处理鼠标释放事件（用于重置按钮的点击确认和勇士拖拽释放）
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    # 优先处理所有牌库窗口的调整大小停止（如果正在调整大小）
                    resizing_handled = False
                    for deck_button in deck_buttons:
                        if deck_button.is_resizing:
                            if deck_button.handle_event(event):
                                resizing_handled = True
                    if resizing_handled:
                        # 调整大小已停止
                        continue
                    # 优先处理勇士列表拖拽释放事件
                    if self.warrior_list.handle_event(event):
                        # 勇士拖拽已处理事件
                        pass
                    # 处理重置按钮的点击释放事件
                    elif self.reset_button.handle_event(event):
                        # 重置按钮已处理事件
                        pass
                
                if event.button == 3:  # 右键释放
                    pass  # 阻止默认右键菜单
    
    def update(self):
        """更新游戏状态"""
        global reveal_animation_data
        
        # 处理扩散动画
        if reveal_animation_data is not None:
            current_time = pygame.time.get_ticks()
            frame_delay = reveal_animation_data['frame_delay']
            last_frame_time = reveal_animation_data['last_frame_time']
            
            # 检查是否到了下一帧的时间
            if current_time - last_frame_time >= frame_delay:
                blocks_to_reveal = reveal_animation_data['blocks_to_reveal']
                current_level = reveal_animation_data['current_level']
                
                # 打开当前层级的所有地块
                if current_level < len(blocks_to_reveal):
                    for row, col in blocks_to_reveal[current_level]:
                        block_key = f"{row},{col}"
                        if block_key in blocks:
                            blocks.remove(block_key)
                            # 如果该格子是危险地块（怪物），触发怪物现身
                            if block_key in danger_land_blocks:
                                trigger_monster_reveal(block_key)
                        # 如果该格子有标记，也移除标记
                        if block_key in marked_blocks:
                            marked_blocks.remove(block_key)
                    
                    # 更新到下一层
                    reveal_animation_data['current_level'] = current_level + 1
                    reveal_animation_data['last_frame_time'] = current_time
                else:
                    # 动画完成
                    reveal_animation_data = None
    
    def draw(self):
        """绘制游戏画面"""
        update_screen_shake()
        # 绘制背景
        window.clear()
        
        # 绘制棋盘背景
        draw_board(window.screen)
        
        # 绘制数字提示层
        draw_number_hints(window.screen)
        
        # 绘制迷雾方块
        draw_fog_blocks(window.screen)
        
        # 更新被发现提示（每次绘制前更新）
        update_discovered_hints()
        
        # 在暴露状态下，将棋子图案透过半透明迷雾显示出来
        draw_exposed_pieces_on_fog(window.screen)
        
        # 绘制标记
        draw_marks(window.screen)
        
        # 绘制被发现提示图标（红色感叹号）
        draw_discovered_hints(window.screen)
        
        # 绘制棋子地块层（危险地块、安全地块、勇士方块、终点）
        draw_danger_land_blocks(window.screen)
        draw_safe_land_blocks(window.screen)
        draw_endpoint_land_blocks(window.screen)
        draw_warrior_blocks(window.screen)
        
        # 检查牌库窗口是否打开（统一判断，避免重复计算）
        deck_window_active = (
            self.available_deck_button.open or self.available_deck_button.is_resizing or
            self.warrior_deck_button.open or self.warrior_deck_button.is_resizing
        )
        
        # 绘制怪物的有效战斗范围（红色方框，当鼠标悬停在暴露状态的怪物上时显示）
        if not deck_window_active:
            draw_battle_range(window.screen)
        
        # 绘制暴露地块的信息提示框（鼠标悬停时显示，在战斗范围框之后绘制，确保显示在上层）
        # 当怪物周围有勇士时，会显示战斗预览面板（勇士战力统计框 + 怪物战力统计框）
        # 当怪物周围没有勇士时，只显示怪物信息框（单独显示）
        if not deck_window_active:
            draw_exposed_tooltip(window.screen)
        
        # 绘制鼠标悬停高亮效果（在最后绘制，确保不被其他层覆盖）
        # 如果游戏失败或已获胜，或勇士牌库窗口打开时，不显示悬停高亮
        if not is_game_over and not is_game_won and not deck_window_active:
            draw_hover_highlight(window.screen)
        
        # 绘制勇士可放置高亮
        draw_warrior_drop_highlight(window.screen)
        
        # 绘制玩家生命UI
        draw_health_bar(window.screen)
        
        # 绘制玩家灵火UI
        draw_spirit_fire_bar(window.screen)
        
        # 绘制统计信息（左下角）
        draw_game_stats(window.screen)
        
        # 根据画面大小UI位置调整地图大小UI的位置（位于其下方，x位置对齐）
        # 使用get_bottom()获取组件底部位置，加上适当间距
        diff_top = self.resolution_selector.get_bottom() + 8
        diff_x = self.resolution_selector.x  # 与画面大小UI左对齐
        self.difficulty_selector.set_position(x=diff_x, y=diff_top)
        
        # 绘制重置按钮（画面右侧）
        self.reset_button.draw(window.screen)
        
        # 绘制勇士列表（画面右侧，在重置按钮下方）
        self.warrior_list.draw(window.screen)
        
        # 绘制地图大小选择器（在画面大小UI下方并左对齐，先绘制）
        self.difficulty_selector.draw(window.screen)
        
        # 绘制分辨率选择器（左上角，最后绘制，确保下拉列表显示在最上层）
        self.resolution_selector.draw(window.screen)
        
        # 绘制勇士牌库按钮（右下角，最后绘制，确保菜单显示在最上层）
        self.available_deck_button.draw(window.screen)
        self.warrior_deck_button.draw(window.screen)
        
        # 绘制拖拽中的勇士方块（在最上层）
        self.warrior_list.draw_dragging(window.screen)
        
        # 统一绘制所有提示框（在窗口之后，确保不被遮挡）
        # deck_window_active 已在前面计算过，这里直接使用
        # 绘制勇士卡牌提示框（如果有悬停的卡牌）
        # 注意：即使窗口打开，也要显示提示框，但要在窗口之后绘制
        try:
            # 检查勇士列表的悬停状态
            if hasattr(self.warrior_list, 'hovered_card') and self.warrior_list.hovered_card is not None:
                try:
                    rect, warrior_id = self.warrior_list.hovered_card
                    if warrior_id is not None:
                        self.warrior_list.draw_card_tooltip(window.screen, rect, warrior_id)
                except (ValueError, TypeError) as e:
                    print(f"解析勇士列表悬停卡牌时出错: {e}, hovered_card={self.warrior_list.hovered_card}")
            
            # 检查勇士牌库按钮的悬停状态
            if hasattr(self.warrior_deck_button, 'hovered_card') and self.warrior_deck_button.hovered_card is not None:
                try:
                    rect, warrior_id = self.warrior_deck_button.hovered_card
                    if warrior_id is not None:
                        self.warrior_deck_button.draw_card_tooltip(window.screen, rect, warrior_id)
                except (ValueError, TypeError) as e:
                    print(f"解析勇士牌库按钮悬停卡牌时出错: {e}, hovered_card={self.warrior_deck_button.hovered_card}")
            
            # 检查可用牌组按钮的悬停状态
            if hasattr(self.available_deck_button, 'hovered_warrior') and self.available_deck_button.hovered_warrior is not None:
                try:
                    warrior_rect, warrior_id = self.available_deck_button.hovered_warrior
                    if warrior_id is not None:
                        self.available_deck_button.draw_card_tooltip(window.screen, warrior_rect, warrior_id)
                except (ValueError, TypeError) as e:
                    print(f"解析可用牌组按钮悬停勇士时出错: {e}, hovered_warrior={self.available_deck_button.hovered_warrior}")
            
            # 检查棋盘上勇士方块的悬停状态
            global hovered_board_warrior
            if hovered_board_warrior is not None:
                try:
                    warrior_letter, block_key, warrior_rect = hovered_board_warrior
                    if warrior_letter is not None:
                        # 使用勇士列表的 draw_card_tooltip 方法绘制提示框
                        self.warrior_list.draw_card_tooltip(window.screen, warrior_rect, warrior_letter)
                except (ValueError, TypeError) as e:
                    print(f"解析棋盘勇士方块悬停时出错: {e}, hovered_board_warrior={hovered_board_warrior}")
        except (AttributeError, pygame.error, TypeError, ValueError, KeyError) as e:
            # 捕获异常，避免崩溃
            print(f"绘制提示框时出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 绘制游戏失败/胜利提示（在最上层）
        if is_game_over:
            draw_game_over(window.screen)
        elif is_game_won:
            draw_game_win(window.screen)
    
    def run(self):
        """运行游戏主循环"""
        self.running = True
        
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 绘制游戏画面
            self.draw()
            
            # 更新显示
            window.flip()
            
            # 控制帧率
            window.tick()
        
        # 退出游戏
        window.quit()
        sys.exit()

def main():
    """游戏主函数"""
    game = GameLoop()
    game.init()
    game.run()

if __name__ == "__main__":
    main()

