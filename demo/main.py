# -*- coding: utf-8 -*-
"""
游戏主程序
"""
import pygame
import sys
import random
from config_mgr import *
from game import Game
from cell import MonsterCell, NumberCell, CellState
from card import Card


def get_chinese_font(size):
    """获取支持中文的字体"""
    # 尝试使用Windows系统字体
    font_names = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong']
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试字体是否支持中文
            test_surface = font.render('测试', True, (0, 0, 0))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    # 如果都失败，使用默认字体
    return pygame.font.Font(None, size)


def draw_cell(screen, cell, x, y, game=None):
    """绘制单个格子"""
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    # 确定颜色
    if isinstance(cell, MonsterCell):
        # 检查战斗结果
        if cell.battle_won is not None:
            # 已战斗：False=怪物胜利（红色），True=玩家胜利（灰色）
            if cell.battle_won:  # 玩家胜利
                color = COLOR_MONSTER_LOST
            else:  # 怪物胜利
                color = COLOR_MONSTER_WON
        elif cell.state == CellState.REVEALED:
            color = COLOR_MONSTER
        else:
            color = COLOR_HIDDEN
    elif isinstance(cell, NumberCell):
        if cell.state == CellState.DEPLOYED:
            color = COLOR_DEPLOYED
        elif cell.state == CellState.REVEALED:
            color = COLOR_NUMBER
        else:
            color = COLOR_HIDDEN
    else:
        color = COLOR_HIDDEN
    
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
            # 格子是 50x50，留出 6 像素边距，实际可用空间是 44x44
            available_width = CELL_SIZE - 6
            available_height = CELL_SIZE - 6
            
            # 初始字体大小：根据行数计算
            base_font_size = min(14, available_height // len(lines) - 2)
            base_font_size = max(10, base_font_size)  # 最小字体大小 10
            
            # 为每一行找到合适的字体大小
            font_sizes = []
            for line in lines:
                # 先尝试基础字体大小
                test_font = get_chinese_font(base_font_size)
                test_surface = test_font.render(line, True, COLOR_TEXT)
                
                # 如果宽度超出，缩小字体
                if test_surface.get_width() > available_width:
                    scale_factor = available_width / test_surface.get_width()
                    font_size = max(10, int(base_font_size * scale_factor))
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
                final_font_size = max(10, final_font_size)
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


def get_card_at_position(game, x, y):
    """获取指定位置的手牌卡牌"""
    hand_y = HAND_AREA_Y
    hand_x_start = HAND_AREA_X
    
    for i, card in enumerate(game.hand):
        card_x = hand_x_start + i * (CARD_WIDTH + CARD_MARGIN)
        card_rect = pygame.Rect(card_x, hand_y, CARD_WIDTH, CARD_HEIGHT)
        if card_rect.collidepoint(x, y):
            return card, i
    return None, -1


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


def get_hovered_object(game, mouse_x, mouse_y):
    """
    检测鼠标悬停的对象
    :param game: 游戏实例
    :param mouse_x: 鼠标X坐标
    :param mouse_y: 鼠标Y坐标
    :return: (object_type, object) 元组，object_type可以是 'card', 'cell', 'monster', None
    """
    # 检查是否悬停在手牌上
    hand_y = HAND_AREA_Y
    hand_x_start = HAND_AREA_X
    
    for i, card in enumerate(game.hand):
        card_x = hand_x_start + i * (CARD_WIDTH + CARD_MARGIN)
        card_rect = pygame.Rect(card_x, hand_y, CARD_WIDTH, CARD_HEIGHT)
        if card_rect.collidepoint(mouse_x, mouse_y):
            return ('card', card)
    
    # 检查是否悬停在地图格子上
    col = int((mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
    row = int((mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
    
    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        cell = game.get_cell(row, col)
        if cell:
            if isinstance(cell, MonsterCell):
                return ('monster', cell)
            else:
                return ('cell', cell)
    
    return (None, None)


def get_hover_info(game, hovered_type, hovered_object):
    """
    获取悬停对象的详细信息
    :param game: 游戏实例
    :param hovered_type: 悬停对象类型
    :param hovered_object: 悬停对象
    :return: 详细信息文本列表
    """
    if hovered_type == 'card' and hovered_object:
        info = []
        info.append(f"卡牌: {hovered_object.name}")
        info.append(f"类型: {hovered_object.unit_type}")
        info.append(f"战力: {hovered_object.power}")
        return info
    elif hovered_type == 'cell' and hovered_object:
        row, col = hovered_object.row, hovered_object.col
        return game.get_cell_info(row, col)
    elif hovered_type == 'monster' and hovered_object:
        return game.get_monster_info(hovered_object)
    else:
        return ["悬停查看详细信息"]


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
        # 根据文本内容选择颜色
        if "战力优势" in text or "玩家胜利" in text:
            color = (100, 255, 100)  # 绿色
        elif "战力不足" in text or "怪物胜利" in text:
            color = (255, 100, 100)  # 红色
        elif "怪物战力" in text:
            color = (255, 150, 150)  # 浅红色
        elif "玩家战力" in text or "周围玩家战力" in text:
            color = (150, 255, 150)  # 浅绿色
        elif "已部署" in text:
            color = (100, 255, 200)  # 青色
        elif "未部署" in text or "未触发" in text:
            color = (200, 200, 200)  # 灰色
        else:
            color = COLOR_UI_TEXT  # 默认白色
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (ui_x + 10, y_offset))
        y_offset += line_spacing


def main():
    """主函数"""
    pygame.init()
    
    # 确保布局根据当前窗口大小计算（如果窗口大小被修改）
    from config_mgr import calculate_layout
    calculate_layout()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("魔法军团：地雷战场")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
    game = Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
    
    # 拖拽状态
    dragging_card = None  # 当前拖拽的卡牌
    drag_offset_x = 0  # 拖拽偏移量
    drag_offset_y = 0
    
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    mouse_x, mouse_y = event.pos
                    
                    # 检查是否点击在结束回合按钮上
                    button_rect = pygame.Rect(
                        BUTTON_X,
                        BUTTON_Y,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT
                    )
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        game.end_turn()
                        continue
                    
                    # 检查是否点击在手牌上
                    card, card_index = get_card_at_position(game, mouse_x, mouse_y)
                    if card:
                        # 开始拖拽
                        dragging_card = card
                        # 计算拖拽偏移量（鼠标相对于卡牌的位置）
                        hand_y = HAND_AREA_Y
                        hand_x_start = HAND_AREA_X
                        card_x = hand_x_start + card_index * (CARD_WIDTH + CARD_MARGIN)
                        drag_offset_x = mouse_x - (card_x + CARD_WIDTH // 2)
                        drag_offset_y = mouse_y - (hand_y + CARD_HEIGHT // 2)
                    else:
                        # 检查是否点击在地图区域内（揭示格子）
                        col = int((mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
                        row = int((mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
                        
                        if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
                            game.click_cell(row, col)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_card:  # 左键释放
                    mouse_x, mouse_y = event.pos
                    
                    # 计算释放位置的格子坐标
                    col = int((mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
                    row = int((mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
                    
                    # 尝试部署卡牌
                    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
                        game.deploy_card(dragging_card, row, col)
                    
                    # 结束拖拽
                    dragging_card = None
            elif event.type == pygame.KEYDOWN:
                # 按R或r重新开始游戏
                if event.key == pygame.K_r:
                    monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
                    game = Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
                    dragging_card = None
                elif hasattr(event, 'unicode') and event.unicode:
                    if event.unicode.lower() == 'r':
                        monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
                        game = Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
                        dragging_card = None
        
        # 更新游戏状态
        game.update()
        
        # 绘制
        screen.fill(COLOR_BACKGROUND)
        
        # 绘制顶部血条
        draw_health_bar(screen, game)
        
        # 绘制地图
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                cell = game.get_cell(row, col)
                if cell:
                    x = MAP_START_X + CELL_MARGIN + col * (CELL_SIZE + CELL_MARGIN)
                    y = MAP_START_Y + CELL_MARGIN + row * (CELL_SIZE + CELL_MARGIN)
                    
                    # 如果正在拖拽卡牌，检查是否可以部署到这个格子
                    # 规则：卡牌数值必须 >= 格子数值（允许高数值卡牌放到低数值区域）
                    highlight = False
                    if dragging_card:
                        if (cell.is_revealed() and isinstance(cell, NumberCell) and 
                            cell.number > 0 and  # 不能部署到数字为0的格子
                            cell.number <= dragging_card.unit_type and  # 卡牌数值 >= 格子数值
                            not cell.has_unit()):
                            highlight = True
                    
                    draw_cell(screen, cell, x, y, game)
                    
                    # 高亮显示可以部署的格子
                    if highlight:
                        highlight_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        highlight_surface.fill((100, 255, 100, 100))  # 半透明绿色
                        screen.blit(highlight_surface, highlight_rect)
        
        # 绘制手牌
        draw_hand(screen, game, dragging_card)
        
        # 绘制拖拽中的卡牌
        if dragging_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            card_x = mouse_x - drag_offset_x - CARD_WIDTH // 2
            card_y = mouse_y - drag_offset_y - CARD_HEIGHT // 2
            draw_card(screen, dragging_card, card_x, card_y, selected=True)
        
        # 绘制左侧操作说明面板
        draw_left_panel(screen)
        
        # 绘制右侧悬停对象信息UI
        draw_ui(screen, game, mouse_pos)
        
        # 绘制结束回合按钮（在右侧面板底部）
        draw_end_turn_button(screen, mouse_pos)
        
        # 绘制游戏结束信息（字体大小根据窗口大小动态调整）
        if game.game_over:
            # 原始比例：WINDOW_WIDTH=1920时，font_large=48, font_small=24
            window_scale = min(WINDOW_WIDTH / 1920.0, WINDOW_HEIGHT / 1080.0)
            font_large_size = max(24, int(48 * window_scale))
            font_small_size = max(12, int(24 * window_scale))
            
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
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            screen.blit(text_surface, text_rect)
            
            # 提示按R重新开始
            font_small = get_chinese_font(font_small_size)
            restart_text = font_small.render("按 R 键重新开始", True, COLOR_UI_TEXT)
            restart_rect = restart_text.get_rect()
            restart_rect.centerx = WINDOW_WIDTH // 2
            restart_offset = max(25, int(50 * window_scale))
            restart_rect.centery = WINDOW_HEIGHT // 2 + restart_offset
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

