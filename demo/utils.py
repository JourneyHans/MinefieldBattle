# -*- coding: utf-8 -*-
"""
工具函数模块
提供字体、坐标计算等通用工具函数
"""
import pygame
from config_mgr import *


# 字体缓存：避免重复测试字体
_font_cache = {}
_working_font_name = None


def get_chinese_font(size):
    """获取支持中文的字体（带缓存）"""
    # 如果已经找到可用的字体名称，直接使用
    if _working_font_name:
        try:
            return pygame.font.SysFont(_working_font_name, size)
        except:
            pass
    
    # 如果缓存中有该大小的字体，直接返回
    if size in _font_cache:
        return _font_cache[size]
    
    # 尝试使用Windows系统字体
    font_names = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong']
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试字体是否支持中文
            test_surface = font.render('测试', True, (0, 0, 0))
            if test_surface.get_width() > 0:
                # 缓存字体名称和字体对象
                global _working_font_name
                _working_font_name = font_name
                _font_cache[size] = font
                return font
        except:
            continue
    # 如果都失败，使用默认字体
    font = pygame.font.Font(None, size)
    _font_cache[size] = font
    return font


# 坐标计算辅助函数
def get_cell_position(row, col):
    """计算格子的屏幕坐标"""
    x = MAP_START_X + CELL_MARGIN + col * (CELL_SIZE + CELL_MARGIN)
    y = MAP_START_Y + CELL_MARGIN + row * (CELL_SIZE + CELL_MARGIN)
    return x, y


def get_cell_from_screen_pos(mouse_x, mouse_y):
    """从屏幕坐标获取格子坐标"""
    col = int((mouse_x - MAP_START_X - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
    row = int((mouse_y - MAP_START_Y - CELL_MARGIN) // (CELL_SIZE + CELL_MARGIN))
    return row, col


def get_card_position(card_index):
    """计算手牌的屏幕坐标"""
    card_x = HAND_AREA_X + card_index * (CARD_WIDTH + CARD_MARGIN)
    card_y = HAND_AREA_Y
    return card_x, card_y


def get_card_at_position(game, x, y):
    """获取指定位置的手牌卡牌"""
    for i, card in enumerate(game.hand):
        card_x, card_y = get_card_position(i)
        card_rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
        if card_rect.collidepoint(x, y):
            return card, i
    return None, -1

