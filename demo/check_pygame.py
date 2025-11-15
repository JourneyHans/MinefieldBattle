# -*- coding: utf-8 -*-
"""
检查 pygame 是否已正确安装
"""
import sys

print("=" * 50)
print("检查 pygame 安装状态")
print("=" * 50)

try:
    import pygame
    print(f"✓ pygame 已安装")
    print(f"  版本: {pygame.version.ver}")
    print(f"  路径: {pygame.__file__}")
    
    # 测试初始化
    try:
        pygame.init()
        print("✓ pygame.init() 成功")
        pygame.quit()
    except Exception as e:
        print(f"✗ pygame.init() 失败: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("所有检查通过！可以开始打包。")
    print("=" * 50)
    
except ImportError as e:
    print(f"✗ pygame 未安装或无法导入: {e}")
    print("\n请运行以下命令安装 pygame:")
    print("  pip install pygame")
    sys.exit(1)
except Exception as e:
    print(f"✗ 检查过程中出现错误: {e}")
    sys.exit(1)

