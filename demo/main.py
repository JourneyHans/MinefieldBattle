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


def draw_cell(screen, cell, x, y, active_monster):
    """绘制单个格子"""
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    # 确定颜色
    if isinstance(cell, MonsterCell):
        if cell.triggered and cell.is_countdown_active():
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
    
    # 绘制文字
    if cell.is_revealed():
        text = cell.get_display_text()
        if text:
            font = get_chinese_font(20)  # 稍微减小字体以适应更多内容
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line:  # 只绘制非空行
                    text_surface = font.render(line, True, COLOR_TEXT)
                    text_rect = text_surface.get_rect()
                    text_rect.centerx = x + CELL_SIZE // 2
                    # 调整垂直位置，使多行文本居中
                    total_height = len([l for l in lines if l]) * 18
                    start_y = y + CELL_SIZE // 2 - total_height // 2
                    text_rect.centery = start_y + i * 18
                    screen.blit(text_surface, text_rect)


def draw_ui(screen, game):
    """绘制UI信息"""
    ui_x = MAP_WIDTH * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN + 20
    
    # 绘制UI背景
    ui_rect = pygame.Rect(ui_x - 10, 10, UI_PANEL_WIDTH, WINDOW_HEIGHT - 20)
    pygame.draw.rect(screen, COLOR_UI_BG, ui_rect)
    
    # 绘制游戏状态
    font = get_chinese_font(28)
    state_texts = game.get_game_state_text()
    
    y_offset = 30
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
        elif "倒计时回合" in text:
            color = (255, 200, 100)  # 橙色
        else:
            color = COLOR_UI_TEXT  # 默认白色
        
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (ui_x, y_offset))
        y_offset += 32
    
    # 绘制操作说明
    y_offset += 20
    font_small = get_chinese_font(20)
    instructions = [
        "操作说明:",
        "左键点击:",
        "  - 揭示格子",
        "  - 部署兵种",
        "",
        "规则:",
        "- 数字=兵种类型",
        "- 点击数字格子",
        "  可部署兵种",
        "- 触发怪物后",
        "  只能操作相邻",
        "  格子",
        "- 倒计时结束",
        "  自动战斗结算"
    ]
    
    for instruction in instructions:
        text_surface = font_small.render(instruction, True, COLOR_UI_TEXT)
        screen.blit(text_surface, (ui_x, y_offset))
        y_offset += 22


def main():
    """主函数"""
    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("魔法军团：地雷战场")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
    game = Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
    
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    # 计算点击的格子位置
                    mouse_x, mouse_y = event.pos
                    col = (mouse_x - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                    row = (mouse_y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN)
                    
                    # 检查是否点击在地图区域内
                    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
                        game.click_cell(row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 按R重新开始
                    monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
                    game = Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
        
        # 更新游戏状态
        game.update()
        
        # 绘制
        screen.fill(COLOR_BACKGROUND)
        
        # 绘制地图
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                cell = game.get_cell(row, col)
                if cell:
                    x = CELL_MARGIN + col * (CELL_SIZE + CELL_MARGIN)
                    y = CELL_MARGIN + row * (CELL_SIZE + CELL_MARGIN)
                    draw_cell(screen, cell, x, y, game.active_monster)
        
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

