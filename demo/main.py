# -*- coding: utf-8 -*-
"""
游戏主程序
"""
import pygame
import sys
import random
import config_mgr
from game import Game
from cell import NumberCell
from utils import get_cell_position
import renderer
import event_handler
import utils
import ui_helper

# 初始导入函数
draw_cell = renderer.draw_cell
draw_unity_animation = renderer.draw_unity_animation
draw_hand = renderer.draw_hand
draw_card = renderer.draw_card
draw_health_bar = renderer.draw_health_bar
draw_left_panel = renderer.draw_left_panel
draw_ui = renderer.draw_ui
draw_end_turn_button = renderer.draw_end_turn_button
draw_game_over_screen = renderer.draw_game_over_screen
draw_settings_button = renderer.draw_settings_button
draw_settings_panel = renderer.draw_settings_panel
handle_mouse_button_down = event_handler.handle_mouse_button_down
handle_mouse_button_up = event_handler.handle_mouse_button_up
handle_keydown = event_handler.handle_keydown
get_cell_position = utils.get_cell_position


def main():
    """主函数"""
    pygame.init()
    
    # 导入配置模块
    from config_mgr import calculate_layout, BASE_WIDTH, BASE_HEIGHT
    import config.ui_config as ui_config
    
    # 初始化窗口
    ui_config.WINDOW_SCALE = 1.5  # 默认1.5倍
    ui_config.WINDOW_WIDTH = int(BASE_WIDTH * ui_config.WINDOW_SCALE)
    ui_config.WINDOW_HEIGHT = int(BASE_HEIGHT * ui_config.WINDOW_SCALE)
    calculate_layout()
    
    screen = pygame.display.set_mode((ui_config.WINDOW_WIDTH, ui_config.WINDOW_HEIGHT))
    pygame.display.set_caption("魔法军团：地雷战场")
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    monster_count = random.randint(config_mgr.MONSTER_COUNT_MIN, config_mgr.MONSTER_COUNT_MAX)
    game = Game(config_mgr.MAP_WIDTH, config_mgr.MAP_HEIGHT, monster_count)
    
    # 拖拽状态
    dragging_card = None  # 当前拖拽的卡牌
    drag_offset_x = 0  # 拖拽偏移量
    drag_offset_y = 0
    
    # 设置界面状态
    show_settings = False
    settings_panel_rects = None
    
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    if show_settings:
                        # 处理设置界面点击
                        mouse_x, mouse_y = event.pos
                        
                        # 检查关闭按钮
                        if settings_panel_rects['close'].collidepoint(mouse_x, mouse_y):
                            show_settings = False
                            settings_panel_rects = None
                            continue
                        
                        # 检查重新开始按钮
                        if settings_panel_rects['restart'].collidepoint(mouse_x, mouse_y):
                            monster_count = random.randint(config_mgr.MONSTER_COUNT_MIN, config_mgr.MONSTER_COUNT_MAX)
                            game = Game(config_mgr.MAP_WIDTH, config_mgr.MAP_HEIGHT, monster_count)
                            dragging_card = None
                            show_settings = False
                            settings_panel_rects = None
                            continue
                        
                        # 检查退出游戏按钮
                        if settings_panel_rects['quit'].collidepoint(mouse_x, mouse_y):
                            running = False
                            continue
                        
                        # 检查分辨率选择
                        for i, rect in enumerate(settings_panel_rects['resolutions']):
                            if rect.collidepoint(mouse_x, mouse_y):
                                new_scale = settings_panel_rects['resolution_scales'][i]
                                if abs(new_scale - ui_config.WINDOW_SCALE) > 0.1:
                                    # 切换分辨率 - 使用动态适配，只需重新计算布局
                                    ui_config.WINDOW_SCALE = new_scale
                                    ui_config.WINDOW_WIDTH = int(BASE_WIDTH * ui_config.WINDOW_SCALE)
                                    ui_config.WINDOW_HEIGHT = int(BASE_HEIGHT * ui_config.WINDOW_SCALE)
                                    screen = pygame.display.set_mode((ui_config.WINDOW_WIDTH, ui_config.WINDOW_HEIGHT))
                                    # 重新计算布局（所有UI元素会自动适配新分辨率）
                                    calculate_layout()
                                break
                    else:
                        # 检查是否点击了设置按钮
                        settings_button_rect = pygame.Rect(ui_config.SETTINGS_BUTTON_X, ui_config.SETTINGS_BUTTON_Y, 
                                                          ui_config.SETTINGS_BUTTON_SIZE_SCALED, ui_config.SETTINGS_BUTTON_SIZE_SCALED)
                        if settings_button_rect.collidepoint(event.pos):
                            show_settings = True
                            continue
                        
                        # 处理游戏内事件
                        result = handle_mouse_button_down(event, game, dragging_card)
                        if result[0] is None and result[1] == 0:  # 点击了按钮
                            continue
                        dragging_card, drag_offset_x, drag_offset_y = result
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and not show_settings:  # 左键释放（设置界面打开时不处理）
                    dragging_card = handle_mouse_button_up(event, game, dragging_card)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC键关闭设置界面
                    if show_settings:
                        show_settings = False
                        settings_panel_rects = None
                        continue
                if not show_settings:  # 设置界面打开时不处理其他按键
                    new_game = handle_keydown(event, game)
                    if new_game != game:
                        game = new_game
                        dragging_card = None
        
        # 更新游戏状态
        if not show_settings:
            game.update()
        
        # 绘制
        COLOR_BACKGROUND = config_mgr.COLOR_BACKGROUND
        screen.fill(COLOR_BACKGROUND)
        
        if show_settings:
            # 绘制设置界面
            settings_panel_rects = draw_settings_panel(screen, mouse_pos, ui_config.WINDOW_SCALE)
        else:
            # 绘制游戏界面
            # 绘制顶部血条
            draw_health_bar(screen, game)
            
            # 绘制地图（动态获取配置值）
            MAP_WIDTH = config_mgr.MAP_WIDTH
            MAP_HEIGHT = config_mgr.MAP_HEIGHT
            CELL_SIZE = config_mgr.CELL_SIZE
            CARD_WIDTH = config_mgr.CARD_WIDTH
            CARD_HEIGHT = config_mgr.CARD_HEIGHT
            
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
        
        # 绘制设置按钮（始终显示，在设置界面时会被覆盖）
        if not show_settings:
            draw_settings_button(screen, mouse_pos)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
