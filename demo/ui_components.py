# -*- coding: utf-8 -*-
"""
UI组件模块
提供可复用的UI组件（下拉列表等）
"""
import pygame
import config_mgr


class Dropdown:
    """下拉列表组件"""
    
    def __init__(self, x, y, width, height, options, default_index=0):
        """
        初始化下拉列表
        :param x: X坐标
        :param y: Y坐标
        :param width: 宽度
        :param height: 高度
        :param options: 选项列表，每个选项为 (value, label) 元组
        :param default_index: 默认选中索引
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        
        # 计算下拉列表区域
        self.dropdown_height = height * len(options)
        self.total_height = height + (self.dropdown_height if self.is_open else 0)
    
    def get_selected_value(self):
        """获取当前选中的值"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index][0]
        return None
    
    def get_selected_label(self):
        """获取当前选中的标签"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index][1]
        return ""
    
    def handle_click(self, mouse_x, mouse_y):
        """
        处理鼠标点击
        :return: (handled, new_value) - handled表示是否处理了点击，new_value表示新选中的值（如果有变化）
        """
        # 检查是否点击在主按钮区域
        main_button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if main_button_rect.collidepoint(mouse_x, mouse_y):
            # 切换展开/收起状态
            self.is_open = not self.is_open
            return True, None
        
        # 如果展开，检查是否点击在选项区域
        if self.is_open:
            dropdown_y = self.y + self.height
            for i, (value, label) in enumerate(self.options):
                option_rect = pygame.Rect(self.x, dropdown_y + i * self.height, self.width, self.height)
                if option_rect.collidepoint(mouse_x, mouse_y):
                    # 选中该选项
                    old_value = self.get_selected_value()
                    self.selected_index = i
                    self.is_open = False
                    new_value = self.get_selected_value()
                    return True, new_value if new_value != old_value else None
        
        # 点击外部区域，收起下拉列表
        if self.is_open:
            self.is_open = False
            return True, None
        
        return False, None
    
    def check_hover(self, mouse_x, mouse_y):
        """检查鼠标是否悬停在下拉列表上"""
        if self.is_open:
            total_rect = pygame.Rect(self.x, self.y, self.width, self.height + self.dropdown_height)
        else:
            total_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return total_rect.collidepoint(mouse_x, mouse_y)
    
    def draw_main_button(self, screen, mouse_pos):
        """
        只绘制下拉列表的主按钮
        :param screen: 屏幕表面
        :param mouse_pos: 鼠标位置
        :return: 主按钮的rect
        """
        from utils import get_chinese_font
        
        mouse_x, mouse_y = mouse_pos
        BUTTON_COLOR = config_mgr.BUTTON_COLOR
        BUTTON_HOVER_COLOR = config_mgr.BUTTON_HOVER_COLOR
        BUTTON_TEXT_COLOR = config_mgr.BUTTON_TEXT_COLOR
        COLOR_TEXT = config_mgr.COLOR_TEXT
        
        # 绘制主按钮
        main_button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        is_hover_main = main_button_rect.collidepoint(mouse_x, mouse_y)
        button_color = BUTTON_HOVER_COLOR if is_hover_main else BUTTON_COLOR
        
        pygame.draw.rect(screen, button_color, main_button_rect)
        pygame.draw.rect(screen, COLOR_TEXT, main_button_rect, 2)
        
        # 绘制选中文本
        font_size = max(16, int(self.height * 0.6))
        font = get_chinese_font(font_size)
        selected_label = self.get_selected_label()
        text_surface = font.render(selected_label, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = main_button_rect.center
        screen.blit(text_surface, text_rect)
        
        # 绘制下拉箭头
        arrow_size = int(self.height * 0.3)
        arrow_x = self.x + self.width - arrow_size - 5
        arrow_y = self.y + self.height // 2
        if self.is_open:
            # 向上箭头
            points = [
                (arrow_x, arrow_y + arrow_size // 2),
                (arrow_x + arrow_size, arrow_y + arrow_size // 2),
                (arrow_x + arrow_size // 2, arrow_y - arrow_size // 2)
            ]
        else:
            # 向下箭头
            points = [
                (arrow_x, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size // 2, arrow_y + arrow_size // 2)
            ]
        pygame.draw.polygon(screen, BUTTON_TEXT_COLOR, points)
        
        return main_button_rect
    
    def draw_options(self, screen, mouse_pos):
        """
        绘制下拉列表的选项（只在展开时调用）
        :param screen: 屏幕表面
        :param mouse_pos: 鼠标位置
        """
        from utils import get_chinese_font
        
        if not self.is_open:
            return
        
        mouse_x, mouse_y = mouse_pos
        BUTTON_COLOR = config_mgr.BUTTON_COLOR
        BUTTON_HOVER_COLOR = config_mgr.BUTTON_HOVER_COLOR
        BUTTON_TEXT_COLOR = config_mgr.BUTTON_TEXT_COLOR
        COLOR_TEXT = config_mgr.COLOR_TEXT
        
        dropdown_y = self.y + self.height
        font_size = max(16, int(self.height * 0.6))
        font = get_chinese_font(font_size)
        
        for i, (value, label) in enumerate(self.options):
            option_rect = pygame.Rect(self.x, dropdown_y + i * self.height, self.width, self.height)
            is_hover_option = option_rect.collidepoint(mouse_x, mouse_y)
            is_selected = (i == self.selected_index)
            
            # 选项颜色
            if is_selected:
                option_color = (100, 200, 100)  # 选中状态：绿色
            elif is_hover_option:
                option_color = BUTTON_HOVER_COLOR
            else:
                option_color = BUTTON_COLOR
            
            pygame.draw.rect(screen, option_color, option_rect)
            pygame.draw.rect(screen, COLOR_TEXT, option_rect, 1)
            
            # 绘制选项文本
            option_text = font.render(label, True, BUTTON_TEXT_COLOR)
            option_text_rect = option_text.get_rect()
            option_text_rect.center = option_rect.center
            screen.blit(option_text, option_text_rect)
    
    def draw(self, screen, mouse_pos):
        """
        绘制下拉列表（完整版本，用于向后兼容）
        :param screen: 屏幕表面
        :param mouse_pos: 鼠标位置
        """
        # 先绘制选项（如果展开）
        self.draw_options(screen, mouse_pos)
        # 再绘制主按钮
        return self.draw_main_button(screen, mouse_pos)

