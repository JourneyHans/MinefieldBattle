# -*- coding: utf-8 -*-
"""
任务判定模块
处理任务完成判定逻辑
"""
from config.task_config import TaskType


class TaskValidator:
    """任务判定器"""
    
    def check_explore_adjacent(self, task_cell, game):
        """
        检查是否探查了任务格子相邻8格
        :param task_cell: 任务格子
        :param game: 游戏实例
        :return: 是否完成
        """
        if not task_cell or not task_cell.is_revealed():
            return False
        
        # 获取相邻8格
        adjacent_cells = game._get_adjacent_cells(task_cell.row, task_cell.col)
        
        # 检查所有相邻格子是否都已揭示
        for cell in adjacent_cells:
            if not cell.is_revealed():
                return False
        
        return True
    
    def check_all_monsters_battled(self, game):
        """
        检查是否与所有怪物交战
        :param game: 游戏实例
        :return: 是否完成
        """
        from cell import MonsterCell
        # 遍历所有格子，检查所有怪物是否都已战斗结算
        for row in range(game.height):
            for col in range(game.width):
                cell = game.get_cell(row, col)
                if isinstance(cell, MonsterCell):
                    # 如果怪物还没有战斗结算（battle_won为None），则未完成
                    if cell.battle_won is None:
                        return False
        
        return True
    
    def check_task_found(self, task_cell):
        """
        检查是否找到了任务格子（已揭示）
        :param task_cell: 任务格子
        :return: 是否完成
        """
        if not task_cell:
            return False
        return task_cell.is_revealed()
    
    def is_task_completed(self, task_type, task_cell, game):
        """
        统一的任务完成判定接口
        :param task_type: 任务类型（TaskType枚举）
        :param task_cell: 任务格子
        :param game: 游戏实例
        :return: 是否完成
        """
        if task_type == TaskType.EXPLORE_ADJACENT:
            return self.check_explore_adjacent(task_cell, game)
        elif task_type == TaskType.BATTLE_ALL_MONSTERS:
            return self.check_all_monsters_battled(game)
        elif task_type == TaskType.FIND_TASK:
            return self.check_task_found(task_cell)
        else:
            return False

