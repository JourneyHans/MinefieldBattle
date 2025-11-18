# -*- coding: utf-8 -*-
"""
游戏主程序
"""
import pygame
import sys
import random
from config import *
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
        elif cell.triggered and cell.is_countdown_active():
            color = COLOR_COUNTDOWN
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
    
    # 如果是激活的怪物，在格子上方显示倒计时数字
    if isinstance(cell, MonsterCell) and cell.is_countdown_active():
        countdown = cell.get_countdown_remaining()
        if countdown > 0:
            # 在格子上方绘制倒计时数字
            countdown_font = get_chinese_font(20)
            countdown_text = countdown_font.render(str(countdown), True, (255, 255, 0))  # 黄色
            countdown_rect = countdown_text.get_rect()
            countdown_rect.centerx = x + CELL_SIZE // 2
            countdown_rect.centery = y - 12  # 在格子上方12像素
            # 绘制半透明背景（圆形或圆角矩形）
            bg_radius = max(countdown_rect.width, countdown_rect.height) // 2 + 4
            bg_rect = pygame.Rect(countdown_rect.centerx - bg_radius, 
                                countdown_rect.centery - bg_radius,
                                bg_radius * 2, bg_radius * 2)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.circle(bg_surface, (0, 0, 0, 200), (bg_radius, bg_radius), bg_radius)
            screen.blit(bg_surface, bg_rect)
            screen.blit(countdown_text, countdown_rect)
    
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
    
    # 绘制卡牌内容
    font = get_chinese_font(18)
    # 兵种名称
    name_text = font.render(card.name, True, COLOR_TEXT)
    name_rect = name_text.get_rect()
    name_rect.centerx = x + CARD_WIDTH // 2
    name_rect.centery = y + 30
    screen.blit(name_text, name_rect)
    
    # 战力值
    power_font = get_chinese_font(24)
    power_text = power_font.render(f"战力: {card.power}", True, COLOR_TEXT)
    power_rect = power_text.get_rect()
    power_rect.centerx = x + CARD_WIDTH // 2
    power_rect.centery = y + CARD_HEIGHT - 30
    screen.blit(power_text, power_rect)
    
    # 兵种类型（数字）
    type_font = get_chinese_font(32)
    type_text = type_font.render(str(card.unit_type), True, COLOR_TEXT)
    type_rect = type_text.get_rect()
    type_rect.centerx = x + CARD_WIDTH // 2
    type_rect.centery = y + CARD_HEIGHT // 2
    screen.blit(type_text, type_rect)


def draw_hand(screen, game, dragging_card=None):
    """绘制手牌"""
    hand_y = HAND_AREA_Y
    hand_x_start = HAND_AREA_X
    
    # 绘制手牌区域背景
    hand_area_rect = pygame.Rect(HAND_AREA_X, hand_y - 10, HAND_AREA_WIDTH, CARD_HEIGHT + 20)
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
    
    # 绘制按钮文字
    font = get_chinese_font(24)
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


def draw_ui(screen, game):
    """绘制UI信息"""
    ui_x = UI_PANEL_X
    
    # 绘制UI背景
    ui_rect = pygame.Rect(UI_PANEL_X, UI_PANEL_Y, UI_PANEL_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(screen, COLOR_UI_BG, ui_rect)
    
    # 绘制游戏状态
    font = get_chinese_font(28)
    state_texts = game.get_game_state_text()
    
    y_offset = UI_PANEL_Y + 30
    for text in state_texts:
        # 根据文本内容选择颜色
        if "战力优势" in text or "游戏胜利" in text:
            color = (100, 255, 100)  # 绿色
        elif "战力不足" in text or "游戏失败" in text:
            color = (255, 100, 100)  # 红色
        elif "怪物战力" in text:
            color = (255, 150, 150)  # 浅红色
        elif "玩家战力" in text:
            color = (150, 255, 150)  # 浅绿色
        elif "倒计时回合" in text or "回合数" in text:
            color = (255, 200, 100)  # 橙色
        else:
            color = COLOR_UI_TEXT  # 默认白色
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (ui_x, y_offset))
        y_offset += 32
    
    # 绘制操作说明
    y_offset += 20
    font_small = get_chinese_font(18)
    instructions = [
        "操作说明:",
        "左键点击:",
        "  - 揭示格子",
        "",
        "拖拽卡牌:",
        "  - 拖到数字格子",
        "  - 部署兵种",
        "",
        "规则:",
        "- 数字=兵种类型",
        "- 卡牌类型需",
        "  匹配格子数字",
        "- 点击结束回合",
        "  消耗怪物倒计时"
    ]
    
    for instruction in instructions:
        text_surface = font_small.render(instruction, True, COLOR_UI_TEXT)
        screen.blit(text_surface, (ui_x, y_offset))
        y_offset += 20


def main():
    """主函数"""
    pygame.init()
    
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
                        col = (mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                        row = (mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                        
                        if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
                            game.click_cell(row, col)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_card:  # 左键释放
                    mouse_x, mouse_y = event.pos
                    
                    # 计算释放位置的格子坐标
                    col = (mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                    row = (mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                    
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
        
        # 绘制地图
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                cell = game.get_cell(row, col)
                if cell:
                    x = MAP_START_X + CELL_MARGIN + col * (CELL_SIZE + CELL_MARGIN)
                    y = MAP_START_Y + CELL_MARGIN + row * (CELL_SIZE + CELL_MARGIN)
                    
                    # 如果正在拖拽卡牌，检查是否可以部署到这个格子
                    highlight = False
                    if dragging_card:
                        if (cell.is_revealed() and isinstance(cell, NumberCell) and 
                            cell.number == dragging_card.unit_type and not cell.has_unit()):
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
        
        # 绘制结束回合按钮
        draw_end_turn_button(screen, mouse_pos)
        
        # 绘制UI
        draw_ui(screen, game)
        
        # 绘制游戏结束信息
        if game.game_over:
            font_large = get_chinese_font(48)
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
            font_small = get_chinese_font(24)
            restart_text = font_small.render("按 R 键重新开始", True, COLOR_UI_TEXT)
            restart_rect = restart_text.get_rect()
            restart_rect.centerx = WINDOW_WIDTH // 2
            restart_rect.centery = WINDOW_HEIGHT // 2 + 50
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

