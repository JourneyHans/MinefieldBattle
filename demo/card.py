# -*- coding: utf-8 -*-
"""
卡牌类定义
"""
from config.card_config import BASE_UNITS


class Card:
    """兵种卡牌"""
    
    def __init__(self, unit_name):
        """
        初始化卡牌
        :param unit_name: 兵种名称（士兵/游侠/法师）
        """
        if unit_name not in BASE_UNITS:
            raise ValueError(f"未知的兵种名称: {unit_name}，支持的兵种: {list(BASE_UNITS.keys())}")
        
        unit_config = BASE_UNITS[unit_name]
        self.unit_name = unit_name
        self.category = unit_config["category"]
        self.name = unit_config["name"]
        self.power = unit_config["power"]  # 固定为1
        self.health = unit_config["health"]  # 固定为1
        self.card_color = unit_config["color"]  # 卡牌背景颜色
    
    def __str__(self):
        return f"{self.name}(战力:{self.power}, 生命:{self.health})"
    
    def __repr__(self):
        return self.__str__()
    
    def create_unit(self):
        """创建对应的兵种单位（使用卡牌原始战力）"""
        from unit import Unit
        return Unit(self.unit_name)
    
    def create_unit_with_power(self, power):
        """
        创建兵种单位，但使用指定的战力值
        :param power: 指定的战力值
        :return: Unit对象
        """
        from unit import Unit
        unit = Unit(self.unit_name)
        unit.power = power  # 覆盖战力值
        return unit

