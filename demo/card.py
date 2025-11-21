# -*- coding: utf-8 -*-
"""
卡牌类定义
"""
from config import UNIT_NAMES


class Card:
    """兵种卡牌"""
    
    def __init__(self, unit_type):
        """
        初始化卡牌
        :param unit_type: 兵种类型 1-8
        """
        if unit_type < 1 or unit_type > 8:
            raise ValueError(f"兵种类型必须在1-8之间，当前值: {unit_type}")
        
        self.unit_type = unit_type
        self.name = UNIT_NAMES.get(unit_type, f"兵种{unit_type}")
        self.power = unit_type  # 战力 = 数字值
    
    def __str__(self):
        return f"{self.name}(战力:{self.power})"
    
    def __repr__(self):
        return self.__str__()
    
    def create_unit(self):
        """创建对应的兵种单位（使用卡牌原始战力）"""
        from unit import Unit
        return Unit(self.unit_type)
    
    def create_unit_with_power(self, power):
        """
        创建兵种单位，但使用指定的战力值
        :param power: 指定的战力值
        :return: Unit对象
        """
        from unit import Unit
        unit = Unit(self.unit_type)
        unit.power = power  # 覆盖战力值
        return unit

