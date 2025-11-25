# -*- coding: utf-8 -*-
"""
UI辅助函数模块
提供UI相关的辅助函数
"""
from config_mgr import *
from cell import MonsterCell, TaskCell
from utils import get_card_position, get_cell_from_screen_pos


def get_hovered_object(game, mouse_x, mouse_y):
    """
    检测鼠标悬停的对象
    :param game: 游戏实例
    :param mouse_x: 鼠标X坐标
    :param mouse_y: 鼠标Y坐标
    :return: (object_type, object) 元组，object_type可以是 'card', 'cell', 'monster', None
    """
    import pygame
    from config_mgr import CARD_WIDTH, CARD_HEIGHT
    
    # 检查是否悬停在手牌上
    for i, card in enumerate(game.hand):
        card_x, card_y = get_card_position(i)
        card_rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
        if card_rect.collidepoint(mouse_x, mouse_y):
            return ('card', card)
    
    # 检查是否悬停在地图格子上
    row, col = get_cell_from_screen_pos(mouse_x, mouse_y)
    
    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        cell = game.get_cell(row, col)
        if cell:
            if isinstance(cell, MonsterCell):
                return ('monster', cell)
            elif isinstance(cell, TaskCell):
                return ('task', cell)
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
        from config.card_config import UnitCategory
        
        category_names = {
            UnitCategory.STRENGTH: "力量",
            UnitCategory.AGILITY: "敏捷",
            UnitCategory.WISDOM: "智慧"
        }
        
        info = []
        info.append(f"卡牌: {hovered_object.name}")
        category_name = category_names.get(hovered_object.category, "未知")
        info.append(f"类型: {category_name}")
        info.append(f"战力: {hovered_object.power}")
        info.append(f"生命: {hovered_object.health}")
        return info
    elif hovered_type == 'cell' and hovered_object:
        row, col = hovered_object.row, hovered_object.col
        return game.get_cell_info(row, col)
    elif hovered_type == 'monster' and hovered_object:
        return game.get_monster_info(hovered_object)
    elif hovered_type == 'task' and hovered_object:
        row, col = hovered_object.row, hovered_object.col
        return game.get_task_info(row, col)
    else:
        return ["悬停查看详细信息"]

