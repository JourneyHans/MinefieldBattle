"""
格子类定义
"""
from enum import Enum


class CellState(Enum):
    """格子状态"""
    HIDDEN = "hidden"  # 隐藏
    REVEALED = "revealed"  # 已揭示
    DEPLOYED = "deployed"  # 已部署兵种


class Cell:
    """格子基类"""
    
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = CellState.HIDDEN
        self.unit = None  # 部署的兵种单位
    
    def reveal(self):
        """揭示格子"""
        if self.state == CellState.HIDDEN:
            self.state = CellState.REVEALED
    
    def is_revealed(self):
        """是否已揭示"""
        return self.state != CellState.HIDDEN
    
    def deploy_unit(self, unit):
        """部署兵种"""
        self.unit = unit
        self.state = CellState.DEPLOYED
    
    def has_unit(self):
        """是否有兵种"""
        return self.unit is not None
    
    def get_power(self):
        """获取战力（用于战斗计算）"""
        if self.has_unit():
            return self.unit.power
        return 0


class NumberCell(Cell):
    """数字格子"""
    
    def __init__(self, row, col, number):
        super().__init__(row, col)
        self.number = number  # 数字值 1-8
    
    def __str__(self):
        return f"NumberCell({self.row}, {self.col}, {self.number})"
    
    def get_display_text(self):
        """获取显示文本"""
        if self.state == CellState.HIDDEN:
            return ""
        elif self.state == CellState.DEPLOYED and self.unit:
            return f"{self.number}\n{self.unit.name}"
        else:
            return str(self.number)


class MonsterCell(Cell):
    """怪物格子"""
    
    def __init__(self, row, col):
        super().__init__(row, col)
        self.triggered = False  # 是否已触发
        self.countdown_rounds = 0  # 倒计时回合数（初始3回合）
        self.monster_power = 0  # 怪物战力（在触发时计算）
    
    def __str__(self):
        return f"MonsterCell({self.row}, {self.col})"
    
    def trigger(self):
        """触发怪物，开始回合倒计时"""
        if not self.triggered:
            self.triggered = True
            self.countdown_rounds = 3  # 初始3回合倒计时
            self.state = CellState.REVEALED
    
    def is_countdown_active(self):
        """倒计时是否进行中"""
        return self.triggered and self.countdown_rounds > 0
    
    def consume_countdown_round(self):
        """消耗1倒计时回合"""
        if self.countdown_rounds > 0:
            self.countdown_rounds -= 1
    
    def get_countdown_remaining(self):
        """获取剩余倒计时回合数"""
        return self.countdown_rounds
    
    def get_display_text(self):
        """获取显示文本"""
        if self.state == CellState.HIDDEN:
            return ""
        else:
            if self.monster_power > 0:
                return f"怪物\n战力:{self.monster_power:.1f}"
            else:
                return "怪物"
    
    def set_monster_power(self, power):
        """设置怪物战力"""
        self.monster_power = power

