# -*- coding: utf-8 -*-
"""
事件处理模块
处理用户输入事件（鼠标、键盘）
"""
import pygame
import random
from config_mgr import *
from game import Game
from utils import get_card_at_position, get_card_position, get_cell_from_screen_pos


def handle_mouse_button_down(event, game, dragging_card):
    """处理鼠标按下事件"""
    mouse_x, mouse_y = event.pos
    
    # 检查是否点击在结束回合按钮上
    button_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
    if button_rect.collidepoint(mouse_x, mouse_y):
        game.end_turn()
        return None, 0, 0
    
    # 检查是否点击在手牌上
    card, card_index = get_card_at_position(game, mouse_x, mouse_y)
    if card:
        # 开始拖拽
        card_x, card_y = get_card_position(card_index)
        drag_offset_x = mouse_x - (card_x + CARD_WIDTH // 2)
        drag_offset_y = mouse_y - (card_y + CARD_HEIGHT // 2)
        return card, drag_offset_x, drag_offset_y
    
    # 检查是否点击在地图区域内（揭示格子）
    row, col = get_cell_from_screen_pos(mouse_x, mouse_y)
    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        game.click_cell(row, col)
    
    return None, 0, 0


def handle_mouse_button_up(event, game, dragging_card):
    """处理鼠标释放事件"""
    if not dragging_card:
        return None
    
    mouse_x, mouse_y = event.pos
    
    # 计算释放位置的格子坐标
    row, col = get_cell_from_screen_pos(mouse_x, mouse_y)
    
    # 尝试部署卡牌
    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        game.deploy_card(dragging_card, row, col)
    
    return None


def handle_keydown(event, game):
    """处理键盘按下事件"""
    # 按R或r重新开始游戏
    if event.key == pygame.K_r or (hasattr(event, 'unicode') and event.unicode and event.unicode.lower() == 'r'):
        monster_count = random.randint(MONSTER_COUNT_MIN, MONSTER_COUNT_MAX)
        return Game(MAP_WIDTH, MAP_HEIGHT, monster_count)
    return game

