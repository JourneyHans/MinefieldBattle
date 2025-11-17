# -*- coding: utf-8 -*-
"""
检查pygame是否安装
"""
import sys

try:
    import pygame
    print(f"pygame {pygame.version.ver} 已安装")
    sys.exit(0)
except ImportError:
    print("错误：pygame 未安装")
    sys.exit(1)
