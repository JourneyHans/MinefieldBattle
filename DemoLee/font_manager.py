#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字体管理模块
负责字体的加载和管理
"""

import pygame
import config

def get_chinese_font(size=config.FONT_SIZE_SMALL):
    """
    获取支持中文的字体
    :param size: 字体大小
    :return: pygame字体对象
    """
    # 直接尝试加载字体，不检查列表（更可靠）
    for font_name in config.CHINESE_FONT_NAMES:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试是否能渲染中文
            test_surface = font.render('测试', True, (255, 255, 255))
            if test_surface.get_width() > 0:  # 如果能渲染，宽度应该大于0
                return font
        except:
            continue
    
    # 如果都找不到，使用默认字体（可能不支持中文，但至少能运行）
    return pygame.font.Font(None, size)

class FontManager:
    """字体管理器"""
    
    def __init__(self):
        """初始化字体管理器"""
        self.fonts = {}
        self._init_fonts()
    
    def _init_fonts(self):
        """初始化所有字体"""
        self.fonts['small'] = get_chinese_font(config.FONT_SIZE_SMALL)
        self.fonts['medium'] = get_chinese_font(config.FONT_SIZE_MEDIUM)
        self.fonts['large'] = get_chinese_font(config.FONT_SIZE_LARGE)
    
    def get(self, name):
        """
        获取字体
        :param name: 字体名称 ('small', 'medium', 'large')
        :return: pygame字体对象
        """
        return self.fonts.get(name, self.fonts['small'])
    
    def get_small(self):
        """获取小号字体"""
        return self.fonts['small']
    
    def get_medium(self):
        """获取中号字体"""
        return self.fonts['medium']
    
    def get_large(self):
        """获取大号字体"""
        return self.fonts['large']



