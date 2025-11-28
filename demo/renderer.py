# -*- coding: utf-8 -*-
"""
渲染模块
负责所有游戏元素的绘制
"""
import pygame
import time
import config_mgr
from cell import MonsterCell, NumberCell, TaskCell, CellState
from constants import *
from utils import get_chinese_font, get_cell_position
from ui_helper import get_hovered_object, get_hover_info

# 动态获取配置值的辅助函数
def get_config(name):
    """动态获取配置值"""
    return getattr(config_mgr, name)


def get_cell_color(cell):
    """获取格子的颜色"""
    COLOR_HIDDEN = get_config('COLOR_HIDDEN')
    COLOR_MONSTER = get_config('COLOR_MONSTER')
    COLOR_MONSTER_WON = get_config('COLOR_MONSTER_WON')
    COLOR_MONSTER_LOST = get_config('COLOR_MONSTER_LOST')
    COLOR_TASK = get_config('COLOR_TASK')
    COLOR_TASK_COMPLETED = get_config('COLOR_TASK_COMPLETED')
    COLOR_TASK_CLAIMED = get_config('COLOR_TASK_CLAIMED')
    COLOR_DEPLOYED = get_config('COLOR_DEPLOYED')
    COLOR_NUMBER = get_config('COLOR_NUMBER')
    
    if isinstance(cell, MonsterCell):
        # 检查战斗结果
        if cell.battle_won is not None:
            return COLOR_MONSTER_LOST if cell.battle_won else COLOR_MONSTER_WON
        elif cell.state == CellState.REVEALED:
            return COLOR_MONSTER
        else:
            return COLOR_HIDDEN
    elif isinstance(cell, TaskCell):
        # 任务格子：根据状态显示不同颜色
        if cell.task_claimed:
            return COLOR_TASK_CLAIMED
        elif cell.task_completed:
            return COLOR_TASK_COMPLETED
        elif cell.state == CellState.REVEALED:
            return COLOR_TASK
        else:
            return COLOR_HIDDEN
    elif isinstance(cell, NumberCell):
        if cell.state == CellState.DEPLOYED:
            return COLOR_DEPLOYED
        elif cell.state == CellState.REVEALED:
            return COLOR_NUMBER
        else:
            return COLOR_HIDDEN
    else:
        return COLOR_HIDDEN


def calculate_text_font_size(lines, available_width, available_height):
    """计算文本的合适字体大小"""
    COLOR_TEXT = get_config('COLOR_TEXT')
    
    # 初始字体大小：根据行数计算
    base_font_size = min(14, available_height // len(lines) - 2)
    base_font_size = max(MIN_FONT_SIZE, base_font_size)
    
    # 为每一行找到合适的字体大小
    font_sizes = []
    for line in lines:
        test_font = get_chinese_font(base_font_size)
        test_surface = test_font.render(line, True, COLOR_TEXT)
        
        # 如果宽度超出，缩小字体
        if test_surface.get_width() > available_width:
            scale_factor = available_width / test_surface.get_width()
            font_size = max(MIN_FONT_SIZE, int(base_font_size * scale_factor))
        else:
            font_size = base_font_size
        
        font_sizes.append(font_size)
    
    # 使用最小的字体大小以确保所有行都能显示
    final_font_size = min(font_sizes)
    
    # 计算行高
    line_height = final_font_size + 2
    total_height = len(lines) * line_height
    
    # 如果总高度超出，进一步缩小
    if total_height > available_height:
        final_font_size = (available_height - 2 * len(lines)) // len(lines)
        final_font_size = max(MIN_FONT_SIZE, final_font_size)
    
    return final_font_size


def draw_cell(screen, cell, x, y, game=None):
    """绘制单个格子"""
    CELL_SIZE = get_config('CELL_SIZE')
    COLOR_TEXT = get_config('COLOR_TEXT')
    
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    # 确定颜色
    color = get_cell_color(cell)
    
    # 绘制格子
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, COLOR_TEXT, rect, 1)  # 边框
    
    # 绘制文字
    if cell.is_revealed():
        text = cell.get_display_text()
        if text:
            lines = [l for l in text.split('\n') if l]  # 过滤空行
            if not lines:
                return
            
            # 根据格子大小和行数动态调整字体大小
            available_width = CELL_SIZE - CELL_PADDING
            available_height = CELL_SIZE - CELL_PADDING
            
            # 计算合适的字体大小
            final_font_size = calculate_text_font_size(lines, available_width, available_height)
            
            # 计算行高和总高度
            line_height = final_font_size + 2
            total_height = len(lines) * line_height
            
            # 绘制每一行文本
            start_y = y + CELL_SIZE // 2 - total_height // 2
            font = get_chinese_font(final_font_size)
            
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, COLOR_TEXT)
                text_rect = text_surface.get_rect()
                text_rect.centerx = x + CELL_SIZE // 2
                text_rect.centery = start_y + i * line_height
                screen.blit(text_surface, text_rect)


def draw_unity_animation(screen, game):
    """绘制团结一致动画效果（扫光效果）"""
    CELL_SIZE = get_config('CELL_SIZE')
    current_time = time.time()
    
    for row, col, start_time in game.unity_animation_queue:
        # 计算动画进度（0.0到1.0）
        elapsed = current_time - start_time
        if elapsed >= ANIMATION_DURATION:
            continue  # 动画已结束
        
        progress = elapsed / ANIMATION_DURATION  # 0.0 到 1.0
        
        # 计算格子位置
        x, y = get_cell_position(row, col)
        
        # 创建扫光效果：从左到右的渐变高光
        sweep_width = int(CELL_SIZE * SWEEP_WIDTH_RATIO)
        sweep_x = int(x + progress * (CELL_SIZE + sweep_width) - sweep_width)
        
        # 创建半透明表面用于扫光
        sweep_surface = pygame.Surface((sweep_width, CELL_SIZE), pygame.SRCALPHA)
        
        # 绘制渐变扫光（从透明到半透明白色，再到透明）
        for i in range(sweep_width):
            # 计算当前位置的alpha值（中间最亮，两边透明）
            alpha = int(255 * (1.0 - abs(i - sweep_width // 2) / (sweep_width // 2)))
            alpha = max(0, min(255, alpha))
            # 使用金色/黄色扫光效果
            color = (255, 215, 0, alpha)  # 金色，带透明度
            pygame.draw.line(sweep_surface, color, (i, 0), (i, CELL_SIZE))
        
        # 只在格子范围内绘制
        if sweep_x + sweep_width >= x and sweep_x <= x + CELL_SIZE:
            # 计算实际绘制区域
            draw_x = max(x, sweep_x)
            draw_width = min(x + CELL_SIZE, sweep_x + sweep_width) - draw_x
            if draw_width > 0:
                # 裁剪表面到实际绘制区域
                clip_x = draw_x - sweep_x
                clipped_surface = sweep_surface.subsurface((clip_x, 0, draw_width, CELL_SIZE))
                screen.blit(clipped_surface, (draw_x, y))


def draw_card(screen, card, x, y, selected=False):
    """绘制一张卡牌"""
    from config.card_config import UnitCategory
    CARD_WIDTH = get_config('CARD_WIDTH')
    CARD_HEIGHT = get_config('CARD_HEIGHT')
    COLOR_TEXT = get_config('COLOR_TEXT')
    
    # 卡牌背景（使用卡牌类型对应的颜色）
    card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    if selected:
        # 选中的卡牌用更亮的颜色（在原有颜色基础上加亮）
        base_color = card.card_color
        color = tuple(min(255, c + 30) for c in base_color)
    else:
        color = card.card_color
    pygame.draw.rect(screen, color, card_rect)
    pygame.draw.rect(screen, COLOR_TEXT, card_rect, 2)  # 边框
    
    # 绘制卡牌内容（字体大小根据卡牌大小动态调整）
    # 原始比例：CARD_WIDTH=80时，name_font=18, power_font=20, category_font=16, health_font=16
    card_scale = CARD_WIDTH / 80.0
    name_font_size = max(10, int(18 * card_scale))
    power_font_size = max(12, int(20 * card_scale))
    category_font_size = max(12, int(16 * card_scale))
    health_font_size = max(12, int(16 * card_scale))
    
    # 兵种名称
    name_font = get_chinese_font(name_font_size)
    name_text = name_font.render(card.name, True, COLOR_TEXT)
    name_rect = name_text.get_rect()
    name_rect.centerx = x + CARD_WIDTH // 2
    name_rect.centery = y + int(CARD_HEIGHT * 0.2)
    screen.blit(name_text, name_rect)
    
    # 兵种类型（力量/敏捷/智慧）
    category_names = {
        UnitCategory.STRENGTH: "力量",
        UnitCategory.AGILITY: "敏捷",
        UnitCategory.WISDOM: "智慧"
    }
    category_font = get_chinese_font(category_font_size)
    category_name = category_names.get(card.category, "未知")
    category_text = category_font.render(category_name, True, COLOR_TEXT)
    category_rect = category_text.get_rect()
    category_rect.centerx = x + CARD_WIDTH // 2
    category_rect.centery = y + int(CARD_HEIGHT * 0.4)
    screen.blit(category_text, category_rect)
    
    # 战力值
    power_font = get_chinese_font(power_font_size)
    power_text = power_font.render(f"战力: {card.power}", True, COLOR_TEXT)
    power_rect = power_text.get_rect()
    power_rect.centerx = x + CARD_WIDTH // 2
    power_rect.centery = y + int(CARD_HEIGHT * 0.7)
    screen.blit(power_text, power_rect)
    
    # 生命值
    health_font = get_chinese_font(health_font_size)
    health_text = health_font.render(f"生命: {card.health}", True, COLOR_TEXT)
    health_rect = health_text.get_rect()
    health_rect.centerx = x + CARD_WIDTH // 2
    health_rect.centery = y + int(CARD_HEIGHT * 0.85)
    screen.blit(health_text, health_rect)


def draw_hand(screen, game, dragging_card=None):
    """绘制手牌"""
    HAND_AREA_X = get_config('HAND_AREA_X')
    HAND_AREA_Y = get_config('HAND_AREA_Y')
    HAND_AREA_WIDTH = get_config('HAND_AREA_WIDTH')
    CARD_WIDTH = get_config('CARD_WIDTH')
    CARD_HEIGHT = get_config('CARD_HEIGHT')
    CARD_MARGIN = get_config('CARD_MARGIN')
    COLOR_TEXT = get_config('COLOR_TEXT')
    
    hand_y = HAND_AREA_Y
    hand_x_start = HAND_AREA_X
    
    # 绘制手牌区域背景（高度根据卡牌大小动态调整）
    hand_area_padding = max(5, int(10 * (CARD_HEIGHT / 120.0)))
    hand_area_rect = pygame.Rect(HAND_AREA_X, hand_y - hand_area_padding, HAND_AREA_WIDTH, CARD_HEIGHT + hand_area_padding * 2)
    pygame.draw.rect(screen, (220, 220, 220), hand_area_rect)
    pygame.draw.rect(screen, COLOR_TEXT, hand_area_rect, 2)
    
    # 绘制每张卡牌
    for i, card in enumerate(game.hand):
        if card == dragging_card:
            continue  # 拖拽中的卡牌不在这里绘制
        
        card_x = hand_x_start + i * (CARD_WIDTH + CARD_MARGIN)
        draw_card(screen, card, card_x, hand_y)


def draw_health_bar(screen, game):
    """在窗口顶部绘制生命值血条"""
    WINDOW_WIDTH = get_config('WINDOW_WIDTH')
    WINDOW_HEIGHT = get_config('WINDOW_HEIGHT')
    INITIAL_HEALTH = get_config('INITIAL_HEALTH')
    COLOR_UI_TEXT = get_config('COLOR_UI_TEXT')
    
    # 血条配置
    bar_height = max(30, int(WINDOW_HEIGHT * 0.04))
    bar_y = max(5, int(WINDOW_HEIGHT * 0.01))
    bar_width = int(WINDOW_WIDTH * 0.3)  # 血条宽度为窗口宽度的30%
    bar_x = (WINDOW_WIDTH - bar_width) // 2  # 居中
    
    # 计算生命值百分比
    health_percent = max(0.0, min(1.0, game.health / INITIAL_HEALTH))
    
    # 根据生命值百分比计算颜色（绿色→黄色→红色）
    if health_percent > 0.6:
        # 绿色到黄色
        r = int(255 * (1.0 - (health_percent - 0.6) / 0.4))
        g = 255
        b = 0
    elif health_percent > 0.3:
        # 黄色到红色
        r = 255
        g = int(255 * ((health_percent - 0.3) / 0.3))
        b = 0
    else:
        # 红色
        r = 255
        g = 0
        b = 0
    
    # 绘制血条背景（深灰色）
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, (50, 50, 50), bg_rect)
    pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2)
    
    # 绘制血条（当前生命值）
    if health_percent > 0:
        health_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_percent), bar_height)
        pygame.draw.rect(screen, (r, g, b), health_rect)
    
    # 绘制文字标签
    font_size = max(16, int(bar_height * 0.6))
    font = get_chinese_font(font_size)
    label_text = f"生命值: {game.health}/{INITIAL_HEALTH}"
    text_surface = font.render(label_text, True, COLOR_UI_TEXT)
    text_rect = text_surface.get_rect()
    text_rect.centerx = bar_x + bar_width // 2
    text_rect.centery = bar_y + bar_height // 2
    screen.blit(text_surface, text_rect)


def draw_left_panel(screen):
    """绘制左侧操作说明面板（不显眼）"""
    LEFT_PANEL_X = get_config('LEFT_PANEL_X')
    LEFT_PANEL_Y = get_config('LEFT_PANEL_Y')
    LEFT_PANEL_WIDTH = get_config('LEFT_PANEL_WIDTH')
    LEFT_PANEL_HEIGHT = get_config('LEFT_PANEL_HEIGHT')
    
    # 绘制左侧面板背景（浅灰色，不显眼）
    left_rect = pygame.Rect(LEFT_PANEL_X, LEFT_PANEL_Y, LEFT_PANEL_WIDTH, LEFT_PANEL_HEIGHT)
    pygame.draw.rect(screen, (220, 220, 220), left_rect)
    pygame.draw.rect(screen, (180, 180, 180), left_rect, 1)
    
    # 绘制操作说明（小字体，不显眼）
    ui_scale = LEFT_PANEL_WIDTH / 150.0
    font_small_size = max(10, int(14 * ui_scale))
    font_small = get_chinese_font(font_small_size)
    
    instructions = [
        "操作说明:",
        "左键点击:",
        "  揭示格子",
        "",
        "拖拽卡牌:",
        "  拖到数字格子",
        "  部署兵种",
        "",
        "规则:",
        "数字=周围怪物数",
        "任意卡牌可部署",
        "到任意数字格子",
        "点击结束回合",
        "获得新卡牌"
    ]
    
    y_offset = LEFT_PANEL_Y + max(10, int(15 * ui_scale))
    small_line_spacing = max(10, int(16 * ui_scale))
    
    for instruction in instructions:
        text_surface = font_small.render(instruction, True, (100, 100, 100))  # 灰色文字，不显眼
        screen.blit(text_surface, (LEFT_PANEL_X + 5, y_offset))
        y_offset += small_line_spacing


def get_text_color(text):
    """根据文本内容获取颜色"""
    COLOR_UI_TEXT = get_config('COLOR_UI_TEXT')
    
    # 胜利/优势相关 - 绿色系
    if "战力优势" in text or "玩家胜利" in text:
        return (100, 255, 100)  # 绿色
    elif "已确认" in text or "已完成" in text:
        return (150, 255, 150)  # 浅绿色（任务完成）
    elif "玩家战力" in text or "周围玩家战力" in text:
        return (150, 255, 150)  # 浅绿色
    
    # 失败/劣势相关 - 红色系
    elif "战力不足" in text or "怪物胜利" in text:
        return (255, 100, 100)  # 红色
    elif "怪物战力" in text:
        return (255, 150, 150)  # 浅红色
    
    # 状态相关
    elif "已部署" in text:
        return (100, 255, 200)  # 青色
    elif "未部署" in text or "未触发" in text:
        return (200, 200, 200)  # 灰色
    elif "进行中" in text or "进度" in text:
        return (255, 255, 150)  # 黄色（任务进行中）
    elif "任务" in text or "任务格子" in text:
        return (255, 200, 255)  # 紫色（任务相关）
    
    # 默认颜色
    return COLOR_UI_TEXT


def wrap_text(text, font, max_width):
    """
    将文本按最大宽度换行（支持中英文混合）
    :param text: 要换行的文本
    :param font: 字体对象
    :param max_width: 最大宽度
    :return: 换行后的文本列表
    """
    if not text:
        return [text]
    
    # 如果文本本身不超过最大宽度，直接返回
    if font.size(text)[0] <= max_width:
        return [text]
    
    lines = []
    current_line = ""
    
    # 按字符处理（支持中文字符）
    for char in text:
        # 测试添加这个字符后的宽度
        test_line = current_line + char
        test_width = font.size(test_line)[0]
        
        if test_width <= max_width:
            current_line = test_line
        else:
            # 如果当前行不为空，保存它并开始新行
            if current_line:
                lines.append(current_line)
            # 如果单个字符就超过宽度（理论上不应该发生），直接添加
            if font.size(char)[0] > max_width:
                lines.append(char)
                current_line = ""
            else:
                current_line = char
    
    # 添加最后一行
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [text]


def draw_ui(screen, game, mouse_pos):
    """绘制右侧悬停对象信息UI"""
    UI_PANEL_X = get_config('UI_PANEL_X')
    UI_PANEL_Y = get_config('UI_PANEL_Y')
    UI_PANEL_WIDTH = get_config('UI_PANEL_WIDTH')
    UI_PANEL_HEIGHT = get_config('UI_PANEL_HEIGHT')
    COLOR_UI_BG = get_config('COLOR_UI_BG')
    
    ui_x = UI_PANEL_X
    
    # 绘制UI背景
    ui_rect = pygame.Rect(UI_PANEL_X, UI_PANEL_Y, UI_PANEL_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(screen, COLOR_UI_BG, ui_rect)
    
    # 检测悬停对象
    mouse_x, mouse_y = mouse_pos
    hovered_type, hovered_object = get_hovered_object(game, mouse_x, mouse_y)
    
    # 获取悬停对象信息
    info_texts = get_hover_info(game, hovered_type, hovered_object)
    
    # 绘制信息（字体大小根据UI面板大小动态调整）
    ui_scale = UI_PANEL_WIDTH / 200.0
    font_size = max(16, int(24 * ui_scale))
    line_spacing = max(22, int(28 * ui_scale))
    
    font = get_chinese_font(font_size)
    
    # 计算可用宽度（留出左右边距）
    available_width = UI_PANEL_WIDTH - 20  # 左右各留10像素边距
    
    y_offset = UI_PANEL_Y + max(15, int(20 * ui_scale))
    for text in info_texts:
        color = get_text_color(text)
        
        # 对文本进行换行处理
        wrapped_lines = wrap_text(text, font, available_width)
        
        for line in wrapped_lines:
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (ui_x + 10, y_offset))
            y_offset += line_spacing
            
            # 如果超出面板高度，停止绘制
            if y_offset > UI_PANEL_Y + UI_PANEL_HEIGHT - line_spacing:
                break
        
        # 如果已经超出面板高度，停止处理后续文本
        if y_offset > UI_PANEL_Y + UI_PANEL_HEIGHT - line_spacing:
            break


def draw_end_turn_button(screen, mouse_pos):
    """绘制结束回合按钮"""
    BUTTON_X = get_config('BUTTON_X')
    BUTTON_Y = get_config('BUTTON_Y')
    BUTTON_WIDTH = get_config('BUTTON_WIDTH')
    BUTTON_HEIGHT = get_config('BUTTON_HEIGHT')
    BUTTON_COLOR = get_config('BUTTON_COLOR')
    BUTTON_HOVER_COLOR = get_config('BUTTON_HOVER_COLOR')
    BUTTON_TEXT_COLOR = get_config('BUTTON_TEXT_COLOR')
    COLOR_TEXT = get_config('COLOR_TEXT')
    
    button_x = BUTTON_X
    button_y = BUTTON_Y
    
    button_rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    
    # 检查鼠标是否悬停
    is_hover = button_rect.collidepoint(mouse_pos)
    button_color = BUTTON_HOVER_COLOR if is_hover else BUTTON_COLOR
    
    # 绘制按钮
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, COLOR_TEXT, button_rect, 2)
    
    # 绘制按钮文字（字体大小根据按钮大小动态调整）
    # 原始比例：BUTTON_WIDTH=120时，font=24
    button_scale = BUTTON_WIDTH / 120.0
    font_size = max(12, int(24 * button_scale))
    font = get_chinese_font(font_size)
    text = font.render("结束回合", True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect()
    text_rect.center = button_rect.center
    screen.blit(text, text_rect)
    
    return button_rect


def draw_settings_button(screen, mouse_pos):
    """绘制设置按钮（右上角）"""
    SETTINGS_BUTTON_X = get_config('SETTINGS_BUTTON_X')
    SETTINGS_BUTTON_Y = get_config('SETTINGS_BUTTON_Y')
    SETTINGS_BUTTON_SIZE_SCALED = get_config('SETTINGS_BUTTON_SIZE_SCALED')
    SETTINGS_BUTTON_COLOR = get_config('SETTINGS_BUTTON_COLOR')
    SETTINGS_BUTTON_HOVER_COLOR = get_config('SETTINGS_BUTTON_HOVER_COLOR')
    COLOR_TEXT = get_config('COLOR_TEXT')
    COLOR_UI_TEXT = get_config('COLOR_UI_TEXT')
    
    button_rect = pygame.Rect(SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y, SETTINGS_BUTTON_SIZE_SCALED, SETTINGS_BUTTON_SIZE_SCALED)
    
    # 检查鼠标是否悬停
    is_hover = button_rect.collidepoint(mouse_pos)
    button_color = SETTINGS_BUTTON_HOVER_COLOR if is_hover else SETTINGS_BUTTON_COLOR
    
    # 绘制按钮
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, COLOR_TEXT, button_rect, 2)
    
    # 绘制齿轮图标（简单的⚙符号）
    font_size = max(16, int(SETTINGS_BUTTON_SIZE_SCALED * 0.6))
    font = get_chinese_font(font_size)
    # 使用"⚙"符号，如果没有则使用"设置"
    try:
        icon_text = font.render("⚙", True, COLOR_UI_TEXT)
    except:
        icon_text = font.render("设", True, COLOR_UI_TEXT)
    icon_rect = icon_text.get_rect()
    icon_rect.center = button_rect.center
    screen.blit(icon_text, icon_rect)
    
    return button_rect


def draw_settings_panel(screen, mouse_pos, current_scale):
    """
    绘制设置界面
    :param screen: 屏幕表面
    :param mouse_pos: 鼠标位置
    :param current_scale: 当前分辨率缩放
    :return: (action, new_scale) action可以是 'close', 'restart', 'quit', 'change_resolution'
    """
    WINDOW_WIDTH = get_config('WINDOW_WIDTH')
    WINDOW_HEIGHT = get_config('WINDOW_HEIGHT')
    SETTINGS_PANEL_COLOR = get_config('SETTINGS_PANEL_COLOR')
    SETTINGS_PANEL_ALPHA = get_config('SETTINGS_PANEL_ALPHA')
    SETTINGS_BUTTON_COLOR = get_config('SETTINGS_BUTTON_COLOR')
    SETTINGS_BUTTON_HOVER_COLOR = get_config('SETTINGS_BUTTON_HOVER_COLOR')
    COLOR_UI_TEXT = get_config('COLOR_UI_TEXT')
    BASE_WIDTH = get_config('BASE_WIDTH')
    BASE_HEIGHT = get_config('BASE_HEIGHT')
    
    # 绘制半透明背景
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(SETTINGS_PANEL_ALPHA)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 计算设置面板大小和位置（居中）
    panel_width = int(WINDOW_WIDTH * 0.4)
    panel_height = int(WINDOW_HEIGHT * 0.5)
    panel_x = (WINDOW_WIDTH - panel_width) // 2
    panel_y = (WINDOW_HEIGHT - panel_height) // 2
    
    # 绘制设置面板背景
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, SETTINGS_PANEL_COLOR, panel_rect)
    pygame.draw.rect(screen, COLOR_UI_TEXT, panel_rect, 3)
    
    # 标题
    title_font_size = max(24, int(WINDOW_HEIGHT * 0.04))
    title_font = get_chinese_font(title_font_size)
    title_text = title_font.render("设置", True, COLOR_UI_TEXT)
    title_rect = title_text.get_rect()
    title_rect.centerx = panel_x + panel_width // 2
    title_rect.y = panel_y + int(WINDOW_HEIGHT * 0.03)
    screen.blit(title_text, title_rect)
    
    # 按钮配置
    button_height = max(40, int(WINDOW_HEIGHT * 0.05))
    button_margin = max(10, int(WINDOW_HEIGHT * 0.015))
    button_y_start = panel_y + int(WINDOW_HEIGHT * 0.1)
    button_width = int(panel_width * 0.7)
    button_x = panel_x + (panel_width - button_width) // 2
    
    action = None
    new_scale = current_scale
    
    # 分辨率选择
    font_size = max(18, int(WINDOW_HEIGHT * 0.03))
    font = get_chinese_font(font_size)
    resolution_label = font.render("分辨率:", True, COLOR_UI_TEXT)
    screen.blit(resolution_label, (button_x, button_y_start))
    
    # 分辨率选项按钮
    resolution_options = [1.0, 1.5, 2.0]
    resolution_labels = ["x1 (640x360)", "x1.5 (960x540)", "x2 (1280x720)"]
    button_y = button_y_start + int(WINDOW_HEIGHT * 0.06)
    
    for i, (scale, label) in enumerate(zip(resolution_options, resolution_labels)):
        btn_rect = pygame.Rect(button_x, button_y + i * (button_height + button_margin), button_width, button_height)
        is_hover = btn_rect.collidepoint(mouse_pos)
        is_selected = abs(scale - current_scale) < 0.1
        
        # 按钮颜色
        if is_selected:
            btn_color = (100, 200, 100)  # 选中状态：绿色
        elif is_hover:
            btn_color = SETTINGS_BUTTON_HOVER_COLOR
        else:
            btn_color = SETTINGS_BUTTON_COLOR
        
        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, COLOR_UI_TEXT, btn_rect, 2)
        
        # 按钮文字
        btn_text = font.render(label, True, COLOR_UI_TEXT)
        btn_text_rect = btn_text.get_rect()
        btn_text_rect.center = btn_rect.center
        screen.blit(btn_text, btn_text_rect)
    
    # 重新开始按钮
    restart_y = button_y + len(resolution_options) * (button_height + button_margin) + int(WINDOW_HEIGHT * 0.05)
    restart_rect = pygame.Rect(button_x, restart_y, button_width, button_height)
    is_hover_restart = restart_rect.collidepoint(mouse_pos)
    restart_color = SETTINGS_BUTTON_HOVER_COLOR if is_hover_restart else SETTINGS_BUTTON_COLOR
    pygame.draw.rect(screen, restart_color, restart_rect)
    pygame.draw.rect(screen, COLOR_UI_TEXT, restart_rect, 2)
    restart_text = font.render("重新开始", True, COLOR_UI_TEXT)
    restart_text_rect = restart_text.get_rect()
    restart_text_rect.center = restart_rect.center
    screen.blit(restart_text, restart_text_rect)
    
    # 退出游戏按钮
    quit_y = restart_y + button_height + button_margin
    quit_rect = pygame.Rect(button_x, quit_y, button_width, button_height)
    is_hover_quit = quit_rect.collidepoint(mouse_pos)
    quit_color = SETTINGS_BUTTON_HOVER_COLOR if is_hover_quit else SETTINGS_BUTTON_COLOR
    pygame.draw.rect(screen, quit_color, quit_rect)
    pygame.draw.rect(screen, COLOR_UI_TEXT, quit_rect, 2)
    quit_text = font.render("退出游戏", True, COLOR_UI_TEXT)
    quit_text_rect = quit_text.get_rect()
    quit_text_rect.center = quit_rect.center
    screen.blit(quit_text, quit_text_rect)
    
    # 关闭按钮（右上角X）
    close_size = max(30, int(WINDOW_HEIGHT * 0.04))
    close_rect = pygame.Rect(panel_x + panel_width - close_size - 10, panel_y + 10, close_size, close_size)
    is_hover_close = close_rect.collidepoint(mouse_pos)
    close_color = (200, 100, 100) if is_hover_close else (150, 150, 150)
    pygame.draw.rect(screen, close_color, close_rect)
    pygame.draw.rect(screen, COLOR_UI_TEXT, close_rect, 2)
    close_font = get_chinese_font(max(20, int(close_size * 0.6)))
    close_text = close_font.render("×", True, COLOR_UI_TEXT)
    close_text_rect = close_text.get_rect()
    close_text_rect.center = close_rect.center
    screen.blit(close_text, close_text_rect)
    
    return {
        'close': close_rect,
        'restart': restart_rect,
        'quit': quit_rect,
        'resolutions': [pygame.Rect(button_x, button_y + i * (button_height + button_margin), button_width, button_height) 
                       for i in range(len(resolution_options))],
        'resolution_scales': resolution_options
    }


def draw_game_over_screen(screen, game):
    """绘制游戏结束界面"""
    if not game.game_over:
        return
    
    from constants import BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT, BASE_FONT_LARGE, BASE_FONT_SMALL, OVERLAY_ALPHA, RESTART_TEXT_OFFSET_BASE
    
    WINDOW_WIDTH = get_config('WINDOW_WIDTH')
    WINDOW_HEIGHT = get_config('WINDOW_HEIGHT')
    COLOR_UI_TEXT = get_config('COLOR_UI_TEXT')
    
    # 原始比例：WINDOW_WIDTH=1920时，font_large=48, font_small=24
    window_scale = min(WINDOW_WIDTH / BASE_WINDOW_WIDTH, WINDOW_HEIGHT / BASE_WINDOW_HEIGHT)
    font_large_size = max(24, int(BASE_FONT_LARGE * window_scale))
    font_small_size = max(12, int(BASE_FONT_SMALL * window_scale))
    
    font_large = get_chinese_font(font_large_size)
    if game.game_won:
        text = "游戏胜利！"
        color = (100, 255, 100)
    else:
        text = "游戏失败！"
        color = (255, 100, 100)
    
    text_surface = font_large.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    # 绘制半透明背景
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(OVERLAY_ALPHA)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    screen.blit(text_surface, text_rect)
    
    # 提示按R重新开始
    font_small = get_chinese_font(font_small_size)
    restart_text = font_small.render("按 R 键重新开始", True, COLOR_UI_TEXT)
    restart_rect = restart_text.get_rect()
    restart_rect.centerx = WINDOW_WIDTH // 2
    restart_offset = max(25, int(RESTART_TEXT_OFFSET_BASE * window_scale))
    restart_rect.centery = WINDOW_HEIGHT // 2 + restart_offset
    screen.blit(restart_text, restart_rect)

