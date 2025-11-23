#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础绘制系统
提供统一的绘制接口和绘制函数
"""

import pygame
import config

class DrawSystem:
    """基础绘制系统"""
    
    def __init__(self, surface):
        """
        初始化绘制系统
        :param surface: 绘制目标Surface
        """
        self.surface = surface
    
    def draw_rect(self, x, y, width, height, color, border_width=0):
        """绘制矩形"""
        pygame.draw.rect(self.surface, color, (x, y, width, height), border_width)
    
    def draw_line(self, start_pos, end_pos, color, width=1):
        """绘制直线"""
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)
    
    def draw_circle(self, center_x, center_y, radius, color, border_width=0):
        """绘制圆形"""
        pygame.draw.circle(self.surface, color, (int(center_x), int(center_y)), radius, border_width)
    
    def draw_polygon(self, points, color, border_width=0):
        """绘制多边形"""
        pygame.draw.polygon(self.surface, color, points, border_width)
    
    def draw_text(self, text, x, y, font, color, align='left', valign='top'):
        """
        绘制文字
        :param text: 文字内容
        :param x, y: 位置
        :param font: 字体对象
        :param color: 颜色
        :param align: 水平对齐 ('left', 'center', 'right')
        :param valign: 垂直对齐 ('top', 'middle', 'bottom')
        """
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # 水平对齐
        if align == 'center':
            text_rect.centerx = x
        elif align == 'right':
            text_rect.right = x
        else:  # left
            text_rect.left = x
        
        # 垂直对齐
        if valign == 'middle':
            text_rect.centery = y
        elif valign == 'bottom':
            text_rect.bottom = y
        else:  # top
            text_rect.top = y
        
        self.surface.blit(text_surface, text_rect)
        return text_rect
    
    def blit(self, source, dest):
        """绘制另一个Surface"""
        self.surface.blit(source, dest)
    
    def fill(self, color):
        """填充整个Surface"""
        self.surface.fill(color)



