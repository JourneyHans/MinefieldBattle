# -*- coding: utf-8 -*-
"""
兵种单位类
"""
from config.card_config import BASE_UNITS


class Unit:
    """兵种单位"""
    
    def __init__(self, unit_name):
        """
        初始化兵种
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
        self.unity_bonus_count = 0  # 团结一致效果叠加次数（0=无效果，1=翻倍，2=翻倍两次=4倍）
    
    def get_effective_power(self):
        """
        获取实际战力（考虑团结一致效果）
        效果可以叠加：1次翻倍=2倍，2次翻倍=4倍
        注意：团结一致效果只对士兵（力量类型）生效
        :return: 实际战力值
        """
        if self.unity_bonus_count == 0:
            return self.power
        elif self.unity_bonus_count == 1:
            return self.power * 2
        else:  # unity_bonus_count >= 2
            return self.power * 4
    
    def __str__(self):
        return f"{self.name}(战力:{self.power}, 生命:{self.health})"
    
    def __repr__(self):
        return self.__str__()

