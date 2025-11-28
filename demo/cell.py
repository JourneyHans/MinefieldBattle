# -*- coding: utf-8 -*-
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
        """获取战力（用于战斗计算，考虑团结一致效果）"""
        if self.has_unit():
            return self.unit.get_effective_power()
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
            # 已部署兵种的格子：显示兵种名称、战力、生命值
            actual_power = self.unit.get_effective_power()
            if self.unit.unity_bonus_count > 0:
                # 如果有团结一致效果，显示特殊标记
                mark = "*" * self.unit.unity_bonus_count  # 1次效果显示*，2次显示**
                return f"{self.unit.name}\n战力:{actual_power}{mark}\n生命:{self.unit.health}"
            else:
                return f"{self.unit.name}\n战力:{actual_power}\n生命:{self.unit.health}"
        else:
            # 数字格子：只显示数字（扫雷作用）
            # 数字为0时不显示
            if self.number == 0:
                return ""
            return str(self.number)


class MonsterCell(Cell):
    """怪物格子"""
    
    def __init__(self, row, col):
        super().__init__(row, col)
        self.triggered = False  # 是否已触发
        self.monster_power = 0  # 怪物战力（在触发时计算）
        self.battle_won = None  # 战斗结果：True=玩家胜利，False=怪物胜利，None=未战斗
    
    def __str__(self):
        return f"MonsterCell({self.row}, {self.col})"
    
    def trigger(self):
        """触发怪物"""
        if not self.triggered:
            self.triggered = True
            self.state = CellState.REVEALED
    
    def get_display_text(self):
        """获取显示文本"""
        if self.state == CellState.HIDDEN:
            return ""
        else:
            if self.monster_power > 0:
                return f"怪物\n战力:{int(self.monster_power)}"
            else:
                return "怪物"
    
    def set_monster_power(self, power):
        """设置怪物战力（向下取整）"""
        self.monster_power = int(power)
    
    def set_battle_result(self, player_won):
        """设置战斗结果"""
        self.battle_won = player_won


class TaskCell(Cell):
    """任务格子"""
    
    def __init__(self, row, col, task_type):
        """
        初始化任务格子
        :param row: 行
        :param col: 列
        :param task_type: 任务类型（TaskType枚举）
        """
        super().__init__(row, col)
        self.task_type = task_type  # 任务类型
        self.task_completed = False  # 任务是否已完成
        self.task_claimed = False  # 任务是否已被领取/确认
    
    def __str__(self):
        return f"TaskCell({self.row}, {self.col}, {self.task_type.value})"
    
    def complete_task(self):
        """标记任务完成"""
        self.task_completed = True
    
    def claim_task(self):
        """确认任务（再次点击时调用）"""
        if self.task_completed:
            self.task_claimed = True
            return True
        return False
    
    def get_display_text(self):
        """获取显示文本"""
        if self.state == CellState.HIDDEN:
            return ""
        
        # 已揭示状态（只显示"任务"，不显示任务名称和描述）
        if self.task_claimed:
            return "任务\n已确认"
        elif self.task_completed:
            return "任务\n已完成\n点击确认"
        else:
            return "任务"
