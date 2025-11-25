# -*- coding: utf-8 -*-
"""
渲染模块
负责所有游戏元素的绘制
"""
import pygame
import time
from config_mgr import *
from cell import MonsterCell, NumberCell, TaskCell, CellState
from constants import *
from utils import get_chinese_font, get_cell_position
from ui_helper import get_hovered_object, get_hover_info


def get_cell_color(cell):
    """获取格子的颜色"""
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
    # 卡牌背景
    card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    if selected:
        # 选中的卡牌用更亮的颜色
        color = (200, 200, 255)
    else:
        color = (180, 180, 220)
    pygame.draw.rect(screen, color, card_rect)
    pygame.draw.rect(screen, COLOR_TEXT, card_rect, 2)  # 边框
    
    # 绘制卡牌内容（字体大小根据卡牌大小动态调整）
    # 原始比例：CARD_WIDTH=80时，name_font=18, power_font=24, type_font=32
    card_scale = CARD_WIDTH / 80.0
    name_font_size = max(10, int(18 * card_scale))
    power_font_size = max(12, int(24 * card_scale))
    type_font_size = max(16, int(32 * card_scale))
    
    # 兵种名称
    name_font = get_chinese_font(name_font_size)
    name_text = name_font.render(card.name, True, COLOR_TEXT)
    name_rect = name_text.get_rect()
    name_rect.centerx = x + CARD_WIDTH // 2
    name_rect.centery = y + int(CARD_HEIGHT * 0.25)
    screen.blit(name_text, name_rect)
    
    # 战力值
    power_font = get_chinese_font(power_font_size)
    power_text = power_font.render(f"战力: {card.power}", True, COLOR_TEXT)
    power_rect = power_text.get_rect()
    power_rect.centerx = x + CARD_WIDTH // 2
    power_rect.centery = y + CARD_HEIGHT - int(CARD_HEIGHT * 0.25)
    screen.blit(power_text, power_rect)
    
    # 兵种类型（数字）
    type_font = get_chinese_font(type_font_size)
    type_text = type_font.render(str(card.unit_type), True, COLOR_TEXT)
    type_rect = type_text.get_rect()
    type_rect.centerx = x + CARD_WIDTH // 2
    type_rect.centery = y + CARD_HEIGHT // 2
    screen.blit(type_text, type_rect)


def draw_hand(screen, game, dragging_card=None):
    """绘制手牌"""
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
    from config_mgr import INITIAL_HEALTH
    
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
        "数字=兵种类型",
        "卡牌需匹配",
        "格子数字",
        "点击结束回合",
        "消耗倒计时"
    ]
    
    y_offset = LEFT_PANEL_Y + max(10, int(15 * ui_scale))
    small_line_spacing = max(10, int(16 * ui_scale))
    
    for instruction in instructions:
        text_surface = font_small.render(instruction, True, (100, 100, 100))  # 灰色文字，不显眼
        screen.blit(text_surface, (LEFT_PANEL_X + 5, y_offset))
        y_offset += small_line_spacing


def get_text_color(text):
    """根据文本内容获取颜色"""
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


def draw_ui(screen, game, mouse_pos):
    """绘制右侧悬停对象信息UI"""
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
    
    y_offset = UI_PANEL_Y + max(15, int(20 * ui_scale))
    for text in info_texts:
        color = get_text_color(text)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (ui_x + 10, y_offset))
        y_offset += line_spacing


def draw_end_turn_button(screen, mouse_pos):
    """绘制结束回合按钮"""
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


def draw_game_over_screen(screen, game):
    """绘制游戏结束界面"""
    if not game.game_over:
        return
    
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

