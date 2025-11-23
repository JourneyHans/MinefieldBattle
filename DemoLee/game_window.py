#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
游戏窗口模块
负责窗口的初始化和管理
"""

import pygame
import config

class GameWindow:
    """游戏窗口管理类"""
    
    def __init__(self):
        """初始化游戏窗口"""
        pygame.init()
        
        # 当前分辨率
        self.current_resolution_key = config.DEFAULT_RESOLUTION_KEY
        self.width = config.RESOLUTIONS[self.current_resolution_key]['width']
        self.height = config.RESOLUTIONS[self.current_resolution_key]['height']
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(config.WINDOW_TITLE)
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        
    def resize(self, resolution_key):
        """改变窗口大小"""
        if resolution_key in config.RESOLUTIONS:
            self.current_resolution_key = resolution_key
            self.width = config.RESOLUTIONS[resolution_key]['width']
            self.height = config.RESOLUTIONS[resolution_key]['height']
            self.screen = pygame.display.set_mode((self.width, self.height))
            return True
        return False
    
    def get_size(self):
        """获取窗口大小"""
        return (self.width, self.height)
    
    def tick(self):
        """控制帧率"""
        self.clock.tick(config.FPS)
    
    def flip(self):
        """更新显示"""
        pygame.display.flip()
    
    def clear(self):
        """清空屏幕"""
        self.screen.fill(config.BACKGROUND_COLOR)
    
    def quit(self):
        """退出窗口"""
        pygame.quit()



