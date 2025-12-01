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
from ui_components import Dropdown
from enum import Enum

# 游戏状态枚举
class GameState(Enum):
    MENU = "menu"          # 主菜单
    PLAYING = "playing"    # 游戏中
    SETTINGS = "settings"  # 设置界面

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
draw_main_menu = renderer.draw_main_menu
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
    pygame.display.set_caption("Magic Legion: Minefield Battle")
    clock = pygame.time.Clock()
    
    # 游戏状态
    game_state = GameState.MENU
    previous_state = None  # 用于从设置界面返回
    
    # 游戏实例（初始为None，在开始游戏时创建）
    game = None
    
    # 拖拽状态
    dragging_card = None  # 当前拖拽的卡牌
    drag_offset_x = 0  # 拖拽偏移量
    drag_offset_y = 0
    
    # 设置界面状态
    settings_panel_rects = None
    
    # 主菜单组件
    from config.difficulty_config import Difficulty, DIFFICULTY_CONFIGS
    difficulty_options = [
        (Difficulty.BEGINNER, DIFFICULTY_CONFIGS[Difficulty.BEGINNER]["name"]),
        (Difficulty.INTERMEDIATE, DIFFICULTY_CONFIGS[Difficulty.INTERMEDIATE]["name"]),
        (Difficulty.EXPERT, DIFFICULTY_CONFIGS[Difficulty.EXPERT]["name"])
    ]
    
    # 初始化当前难度
    config_mgr.current_difficulty = Difficulty.BEGINNER
    
    # 创建难度下拉列表
    WINDOW_WIDTH = ui_config.WINDOW_WIDTH
    WINDOW_HEIGHT = ui_config.WINDOW_HEIGHT
    dropdown_width = int(WINDOW_WIDTH * 0.28)
    dropdown_height = max(40, int(WINDOW_HEIGHT * 0.05))
    dropdown_x = (WINDOW_WIDTH - dropdown_width) // 2
    dropdown_y = int(WINDOW_HEIGHT * 0.4)
    difficulty_dropdown = Dropdown(dropdown_x, dropdown_y, dropdown_width, dropdown_height, difficulty_options, 0)
    
    # 主菜单界面元素
    menu_rects = None
    
    def create_new_game():
        """根据当前难度创建新游戏"""
        from config.difficulty_config import DIFFICULTY_CONFIGS
        from config.game_config import get_monster_count
        
        # 更新地图配置
        difficulty_config = DIFFICULTY_CONFIGS[config_mgr.current_difficulty]
        config_mgr.MAP_WIDTH = difficulty_config["width"]
        config_mgr.MAP_HEIGHT = difficulty_config["height"]
        
        # 重新计算布局
        calculate_layout()
        
        # 获取地雷数量
        monster_count = get_monster_count()
        
        # 创建游戏实例
        return Game(config_mgr.MAP_WIDTH, config_mgr.MAP_HEIGHT, monster_count)
    
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    if game_state == GameState.SETTINGS:
                        # 处理设置界面点击
                        mouse_x, mouse_y = event.pos
                        
                        # 检查关闭按钮
                        if settings_panel_rects['close'].collidepoint(mouse_x, mouse_y):
                            game_state = previous_state
                            previous_state = None
                            settings_panel_rects = None
                            continue
                        
                        # 检查重新开始按钮（只在游戏中有效）
                        if previous_state == GameState.PLAYING and settings_panel_rects['restart'].collidepoint(mouse_x, mouse_y):
                            game = create_new_game()
                            dragging_card = None
                            game_state = previous_state
                            previous_state = None
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
                                    # 更新下拉列表位置
                                    dropdown_width = int(ui_config.WINDOW_WIDTH * 0.28)
                                    dropdown_height = max(40, int(ui_config.WINDOW_HEIGHT * 0.05))
                                    dropdown_x = (ui_config.WINDOW_WIDTH - dropdown_width) // 2
                                    dropdown_y = int(ui_config.WINDOW_HEIGHT * 0.4)
                                    difficulty_dropdown.x = dropdown_x
                                    difficulty_dropdown.y = dropdown_y
                                    difficulty_dropdown.width = dropdown_width
                                    difficulty_dropdown.height = dropdown_height
                                break
                    elif game_state == GameState.MENU:
                        # 处理主菜单点击
                        mouse_x, mouse_y = event.pos
                        
                        # 处理难度下拉列表
                        handled, new_difficulty = difficulty_dropdown.handle_click(mouse_x, mouse_y)
                        if handled and new_difficulty is not None:
                            config_mgr.current_difficulty = new_difficulty
                            continue
                        
                        # 处理主菜单按钮
                        if menu_rects:
                            if menu_rects['start'].collidepoint(mouse_x, mouse_y):
                                # 开始游戏
                                game = create_new_game()
                                dragging_card = None
                                game_state = GameState.PLAYING
                                continue
                            elif menu_rects['settings'].collidepoint(mouse_x, mouse_y):
                                # 打开设置
                                previous_state = game_state
                                game_state = GameState.SETTINGS
                                continue
                    elif game_state == GameState.PLAYING:
                        # 处理游戏内事件
                        mouse_x, mouse_y = event.pos
                        
                        # 检查是否点击了设置按钮
                        settings_button_rect = pygame.Rect(ui_config.SETTINGS_BUTTON_X, ui_config.SETTINGS_BUTTON_Y, 
                                                          ui_config.SETTINGS_BUTTON_SIZE_SCALED, ui_config.SETTINGS_BUTTON_SIZE_SCALED)
                        if settings_button_rect.collidepoint(mouse_x, mouse_y):
                            previous_state = game_state
                            game_state = GameState.SETTINGS
                            continue
                        
                        # 检查游戏结束界面的返回主菜单按钮
                        if game and game.game_over:
                            # 临时绘制以获取按钮rect
                            from constants import BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT, BASE_FONT_LARGE, BASE_FONT_SMALL, OVERLAY_ALPHA, RESTART_TEXT_OFFSET_BASE
                            WINDOW_WIDTH = config_mgr.WINDOW_WIDTH
                            WINDOW_HEIGHT = config_mgr.WINDOW_HEIGHT
                            BUTTON_COLOR = config_mgr.BUTTON_COLOR
                            BUTTON_HOVER_COLOR = config_mgr.BUTTON_HOVER_COLOR
                            BUTTON_TEXT_COLOR = config_mgr.BUTTON_TEXT_COLOR
                            COLOR_TEXT = config_mgr.COLOR_TEXT
                            
                            window_scale = min(WINDOW_WIDTH / BASE_WINDOW_WIDTH, WINDOW_HEIGHT / BASE_WINDOW_HEIGHT)
                            font_small_size = max(12, int(BASE_FONT_SMALL * window_scale))
                            
                            button_width = int(WINDOW_WIDTH * 0.15)
                            button_height = max(40, int(WINDOW_HEIGHT * 0.05))
                            button_x = WINDOW_WIDTH // 2 - button_width // 2
                            button_y = WINDOW_HEIGHT // 2 + max(60, int(WINDOW_HEIGHT * 0.08))
                            menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                            
                            if menu_button_rect.collidepoint(mouse_x, mouse_y):
                                game = None
                                game_state = GameState.MENU
                                dragging_card = None
                                continue
                        
                        # 处理游戏内事件
                        result = handle_mouse_button_down(event, game, dragging_card)
                        if result[0] is None and result[1] == 0:  # 点击了按钮
                            continue
                        dragging_card, drag_offset_x, drag_offset_y = result
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and game_state == GameState.PLAYING:  # 左键释放（只在游戏中处理）
                    dragging_card = handle_mouse_button_up(event, game, dragging_card)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC键关闭设置界面或返回主菜单
                    if game_state == GameState.SETTINGS:
                        game_state = previous_state
                        previous_state = None
                        settings_panel_rects = None
                        continue
                    elif game_state == GameState.PLAYING:
                        previous_state = game_state
                        game_state = GameState.SETTINGS
                        continue
                elif game_state == GameState.PLAYING:  # 游戏中的按键处理
                    new_game = handle_keydown(event, game)
                    if new_game != game:
                        game = new_game
                        dragging_card = None
        
        # 更新游戏状态
        if game_state == GameState.PLAYING and game:
            game.update()
        
        # 绘制
        COLOR_BACKGROUND = config_mgr.COLOR_BACKGROUND
        screen.fill(COLOR_BACKGROUND)
        
        if game_state == GameState.SETTINGS:
            # 绘制设置界面
            settings_panel_rects = draw_settings_panel(screen, mouse_pos, ui_config.WINDOW_SCALE)
        elif game_state == GameState.MENU:
            # 绘制主菜单
            menu_rects = draw_main_menu(screen, mouse_pos, difficulty_dropdown)
        elif game_state == GameState.PLAYING and game:
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
            if game.game_over:
                draw_game_over_screen(screen, game)
        
        # 绘制设置按钮（只在游戏中显示）
        if game_state == GameState.PLAYING:
            draw_settings_button(screen, mouse_pos)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
