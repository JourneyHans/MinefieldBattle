"""
兵种单位类
"""
from config import UNIT_NAMES


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
    
    def __str__(self):
        return f"{self.name}(战力:{self.power})"
    
    def __repr__(self):
        return self.__str__()

