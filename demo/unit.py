# -*- coding: utf-8 -*-
"""
兵种单位类
"""
from config_mgr import UNIT_NAMES


class Unit:
    """兵种单位"""
    
    def __init__(self, unit_type):
        """
        初始化兵种
        :param unit_type: 兵种类型 1-8
        """
        if unit_type < 1 or unit_type > 8:
            raise ValueError(f"兵种类型必须在1-8之间，当前值: {unit_type}")
        
        self.unit_type = unit_type
        self.name = UNIT_NAMES.get(unit_type, f"兵种{unit_type}")
        self.power = unit_type  # 简化版：战力 = 数字值
        self.unity_bonus_count = 0  # 团结一致效果叠加次数（0=无效果，1=翻倍，2=翻倍两次=4倍）
    
    def get_effective_power(self):
        """
        获取实际战力（考虑团结一致效果）
        效果可以叠加：1次翻倍=2倍，2次翻倍=4倍
        :return: 实际战力值
        """
        if self.unity_bonus_count == 0:
            return self.power
        elif self.unity_bonus_count == 1:
            return self.power * 2
        else:  # unity_bonus_count >= 2
            return self.power * 4
    
    def __str__(self):
        return f"{self.name}(战力:{self.power})"
    
    def __repr__(self):
        return self.__str__()

