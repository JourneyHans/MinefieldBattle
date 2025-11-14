# -*- coding: utf-8 -*-
"""
游戏核心逻辑
"""
import random
from cell import Cell, NumberCell, MonsterCell, CellState
from unit import Unit


class Game:
    """游戏主类"""
    
    def __init__(self, width, height, monster_count):
        """
        初始化游戏
        :param width: 地图宽度
        :param height: 地图高度
        :param monster_count: 怪物数量
        """
        self.width = width
        self.height = height
        self.monster_count = monster_count
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.health = 3  # 初始生命值
        self.game_over = False
        self.game_won = False
        self.active_monster = None  # 当前激活的怪物（倒计时中）
        self.monsters = []  # 所有怪物列表
        
        self._generate_map()
    
    def _generate_map(self):
        """生成地图"""
        # 1. 随机放置怪物
        monster_positions = []
        attempts = 0
        max_attempts = 1000
        
        while len(monster_positions) < self.monster_count and attempts < max_attempts:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            
            if (row, col) not in monster_positions:
                monster_positions.append((row, col))
                monster = MonsterCell(row, col)
                self.grid[row][col] = monster
                self.monsters.append(monster)
            attempts += 1
        
        # 2. 计算每个格子的数字（相邻怪物数量）
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] is None:  # 不是怪物格子
                    # 计算相邻怪物数量
                    count = self._count_adjacent_monsters(row, col)
                    # 创建数字格子（如果没有相邻怪物，数字为0，但显示为空白）
                    self.grid[row][col] = NumberCell(row, col, count)
    
    def _count_adjacent_monsters(self, row, col):
        """计算相邻8个格子中的怪物数量"""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if isinstance(self.grid[nr][nc], MonsterCell):
                        count += 1
        return count
    
    def _get_adjacent_cells(self, row, col):
        """获取相邻8个格子"""
        adjacent = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    adjacent.append(self.grid[nr][nc])
        return adjacent
    
    def _get_adjacent_numbers(self, row, col):
        """获取相邻8个格子的数字值（用于计算怪物战力）"""
        numbers = []
        for cell in self._get_adjacent_cells(row, col):
            if isinstance(cell, NumberCell):
                numbers.append(cell.number)
            elif isinstance(cell, MonsterCell):
                # 怪物格子不算数字
                pass
        return numbers
    
    def _reveal_blank_area(self, row, col):
        """
        揭示空白区域（数字=0的格子自动展开）
        经典扫雷机制：点击数字为0的格子时，自动展开所有相邻的空白格子（数字=0），
        直到遇到数字>0的格子或怪物格子为止
        :param row: 起始行
        :param col: 起始列
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            return
        
        cell = self.grid[row][col]
        
        # 如果已经揭示，跳过
        if cell.is_revealed():
            return
        
        # 如果是怪物格子，不自动展开
        if isinstance(cell, MonsterCell):
            return
        
        # 如果是数字>0的格子，只揭示它自己，不展开相邻格子
        if isinstance(cell, NumberCell) and cell.number > 0:
            cell.reveal()
            return
        
        # 如果是数字为0的格子，揭示它并继续展开相邻格子
        if isinstance(cell, NumberCell) and cell.number == 0:
            cell.reveal()
            # 递归展开所有相邻的空白格子
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        adj_cell = self.grid[nr][nc]
                        # 只展开未揭示的格子
                        if not adj_cell.is_revealed():
                            # 如果是数字为0的格子，递归展开
                            if isinstance(adj_cell, NumberCell) and adj_cell.number == 0:
                                self._reveal_blank_area(nr, nc)
                            # 如果是数字>0的格子，只揭示它自己
                            elif isinstance(adj_cell, NumberCell) and adj_cell.number > 0:
                                adj_cell.reveal()
                            # 怪物格子不展开
    
    def click_cell(self, row, col):
        """
        点击格子
        :param row: 行
        :param col: 列
        :return: 操作是否成功
        """
        if self.game_over:
            return False
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        
        cell = self.grid[row][col]
        
        # 如果有激活的怪物倒计时，只能操作相邻格子，且操作会消耗倒计时回合
        if self.active_monster and self.active_monster.is_countdown_active():
            # 检查是否在激活怪物的相邻格子
            adjacent_positions = [(c.row, c.col) for c in self._get_adjacent_cells(
                self.active_monster.row, self.active_monster.col)]
            if (row, col) not in adjacent_positions and (row, col) != (self.active_monster.row, self.active_monster.col):
                return False  # 不能操作非相邻格子
        
        # 如果格子已揭示且是数字格子，尝试部署兵种
        if cell.is_revealed() and isinstance(cell, NumberCell):
            if not cell.has_unit() and cell.number > 0:
                # 部署兵种
                unit = Unit(cell.number)
                cell.deploy_unit(unit)
                # 如果在倒计时期间，消耗倒计时回合
                if self.active_monster and self.active_monster.is_countdown_active():
                    self.active_monster.consume_countdown_round()
                    # 检查倒计时是否结束
                    if not self.active_monster.is_countdown_active():
                        self._battle_settlement(self.active_monster)
                        self.active_monster = None
                return True
        
        # 如果格子未揭示，揭示它
        if not cell.is_revealed():
            # 如果是怪物格子，触发战斗
            if isinstance(cell, MonsterCell):
                cell.trigger()
                self.active_monster = cell
                # 计算怪物战力
                adjacent_numbers = self._get_adjacent_numbers(row, col)
                monster_power = sum(adjacent_numbers) / 2
                cell.set_monster_power(monster_power)
                # 触发怪物不消耗倒计时回合（第一次触发）
            else:
                # 数字格子，实现空白区域自动展开（只有数字为0时才展开）
                if isinstance(cell, NumberCell) and cell.number == 0:
                    # 数字为0，自动展开空白区域
                    self._reveal_blank_area(row, col)
                else:
                    # 数字>0，只揭示当前格子
                    cell.reveal()
                
                # 如果在倒计时期间，消耗倒计时回合
                if self.active_monster and self.active_monster.is_countdown_active():
                    self.active_monster.consume_countdown_round()
                    # 检查倒计时是否结束
                    if not self.active_monster.is_countdown_active():
                        self._battle_settlement(self.active_monster)
                        self.active_monster = None
            
            return True
        
        return False
    
    def update(self):
        """
        更新游戏状态
        """
        if self.game_over:
            return
        
        # 检查胜利条件（所有怪物都被消灭）
        if len(self.monsters) == 0 and self.health > 0:
            self.game_over = True
            self.game_won = True
    
    def _battle_settlement(self, monster_cell):
        """
        战斗结算
        :param monster_cell: 怪物格子
        """
        # 计算玩家战力（相邻8格已部署兵种总战力）
        player_power = 0
        for cell in self._get_adjacent_cells(monster_cell.row, monster_cell.col):
            player_power += cell.get_power()
        
        # 获取怪物战力
        monster_power = monster_cell.monster_power
        
        # 判断胜负
        if player_power >= monster_power:
            # 玩家获胜，消灭怪物
            # 从monsters列表中移除（标记为已消灭）
            if monster_cell in self.monsters:
                self.monsters.remove(monster_cell)
        else:
            # 玩家失败，扣除生命值
            self.health -= 1
            if self.health <= 0:
                self.game_over = True
                self.game_won = False
    
    def get_cell(self, row, col):
        """获取指定位置的格子"""
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col]
        return None
    
    def get_player_power_around_monster(self, monster_cell):
        """获取怪物周围玩家的战力"""
        player_power = 0
        for cell in self._get_adjacent_cells(monster_cell.row, monster_cell.col):
            player_power += cell.get_power()
        return player_power
    
    def get_game_state_text(self):
        """获取游戏状态文本"""
        state = []
        state.append(f"生命值: {self.health}")
        state.append(f"剩余怪物: {len([m for m in self.monsters if not m.triggered])}")
        
        if self.active_monster and self.active_monster.is_countdown_active():
            remaining = self.active_monster.get_countdown_remaining()
            state.append(f"倒计时回合: {remaining}")
            
            # 显示怪物战力和玩家战力对比
            monster_power = self.active_monster.monster_power
            player_power = self.get_player_power_around_monster(self.active_monster)
            state.append(f"怪物战力: {monster_power:.1f}")
            state.append(f"玩家战力: {player_power:.1f}")
            
            # 显示战力差距
            power_diff = player_power - monster_power
            if power_diff >= 0:
                state.append(f"战力优势: +{power_diff:.1f}")
            else:
                state.append(f"战力不足: {power_diff:.1f}")
        
        if self.game_over:
            if self.game_won:
                state.append("游戏胜利！")
            else:
                state.append("游戏失败！")
        
        return state

