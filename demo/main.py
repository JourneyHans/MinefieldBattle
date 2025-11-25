# -*- coding: utf-8 -*-
"""
游戏主程序
"""
import pygame
import sys
import random
from config_mgr import *
from game import Game
from cell import NumberCell
from utils import get_cell_position
from renderer import (
    draw_cell, draw_unity_animation, draw_hand, draw_card,
    draw_health_bar, draw_left_panel, draw_ui, draw_end_turn_button,
    draw_game_over_screen
)
from event_handler import handle_mouse_button_down, handle_mouse_button_up, handle_keydown


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
                    result = handle_mouse_button_down(event, game, dragging_card)
                    if result[0] is None and result[1] == 0:  # 点击了按钮
                        continue
                    dragging_card, drag_offset_x, drag_offset_y = result
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    dragging_card = handle_mouse_button_up(event, game, dragging_card)
            elif event.type == pygame.KEYDOWN:
                new_game = handle_keydown(event, game)
                if new_game != game:
                    game = new_game
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
                    x, y = get_cell_position(row, col)
                    
                    # 如果正在拖拽卡牌，检查是否可以部署到这个格子
                    highlight = (dragging_card and 
                                cell.is_revealed() and 
                                isinstance(cell, NumberCell) and 
                            cell.number > 0 and  # 不能部署到数字为0的格子
                                not cell.has_unit())
                    
                    draw_cell(screen, cell, x, y, game)
                    
                    # 高亮显示可以部署的格子
                    if highlight:
                        highlight_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        highlight_surface.fill((100, 255, 100, 100))  # 半透明绿色
                        screen.blit(highlight_surface, highlight_rect)
        
        # 绘制团结一致动画效果
        draw_unity_animation(screen, game)
        
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
        
        # 绘制游戏结束信息
        draw_game_over_screen(screen, game)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
