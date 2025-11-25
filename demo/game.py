# -*- coding: utf-8 -*-
"""
游戏核心逻辑
"""
import random
import math
from cell import Cell, NumberCell, MonsterCell, TaskCell, CellState
from unit import Unit
from card import Card
from task_validator import TaskValidator
from config_mgr import CARDS_PER_TURN, MAX_HAND_SIZE, MONSTER_BASE_POWER, MONSTER_POWER_DIVISOR, INITIAL_HEALTH, TaskType, TASK_COUNT


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
        self.health = INITIAL_HEALTH  # 从配置读取初始生命值
        self.game_over = False
        self.game_won = False
        self.monsters = []  # 所有怪物列表
        self.reveal_animation_queue = []  # 揭示动画队列 [(row, col, reveal_time), ...]
        self.unity_animation_queue = []  # 团结一致动画队列 [(row, col, start_time), ...]
        
        # 回合系统
        self.current_turn = 1  # 当前回合数
        self.hand = []  # 玩家手牌列表
        
        # 任务系统
        self.task_cell = None  # 任务格子
        self.task_validator = TaskValidator()  # 任务判定器
        self.main_task_type = None  # 当前通关任务类型
        
        self._generate_map()
        # 游戏开始时发牌
        self._deal_cards()
    
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
        
        # 2. 随机生成任务格子（确保不与怪物格子重叠）
        task_positions = []
        task_attempts = 0
        max_task_attempts = 1000
        
        while len(task_positions) < TASK_COUNT and task_attempts < max_task_attempts:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            
            # 确保不与怪物格子重叠
            if (row, col) not in monster_positions and (row, col) not in task_positions:
                task_positions.append((row, col))
                # 随机选择一种任务类型作为通关任务
                task_type = random.choice(list(TaskType))
                task_cell = TaskCell(row, col, task_type)
                self.grid[row][col] = task_cell
                self.task_cell = task_cell
                self.main_task_type = task_type
            task_attempts += 1
        
        # 3. 计算每个格子的数字（相邻怪物数量）
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] is None:  # 不是怪物格子也不是任务格子
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
    
    def _collect_blank_area(self, row, col, collected=None):
        """
        收集空白区域的所有格子（用于动画）
        :param row: 起始行
        :param col: 起始列
        :param collected: 已收集的格子集合
        :return: 收集到的格子列表 [(row, col, distance), ...]
        """
        if collected is None:
            collected = set()
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return []
        
        if (row, col) in collected:
            return []
        
        cell = self.grid[row][col]
        
        # 如果已经揭示，跳过
        if cell.is_revealed():
            return []
        
        # 如果是怪物格子，不自动展开
        if isinstance(cell, MonsterCell):
            return []
        
        result = []
        
        # 如果是数字>0的格子，只收集它自己
        if isinstance(cell, NumberCell) and cell.number > 0:
            collected.add((row, col))
            result.append((row, col, 0))
            return result
        
        # 如果是数字为0的格子，收集它并继续收集相邻格子
        if isinstance(cell, NumberCell) and cell.number == 0:
            collected.add((row, col))
            result.append((row, col, 0))
            
            # 递归收集所有相邻的空白格子
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        adj_cell = self.grid[nr][nc]
                        # 只收集未揭示的格子
                        if not adj_cell.is_revealed():
                            # 如果是数字为0的格子，递归收集
                            if isinstance(adj_cell, NumberCell) and adj_cell.number == 0:
                                sub_result = self._collect_blank_area(nr, nc, collected)
                                result.extend(sub_result)
                            # 如果是数字>0的格子，只收集它自己
                            elif isinstance(adj_cell, NumberCell) and adj_cell.number > 0:
                                if (nr, nc) not in collected:
                                    collected.add((nr, nc))
                                    result.append((nr, nc, 0))
        
        return result
    
    def _reveal_blank_area(self, row, col):
        """
        揭示空白区域（数字=0的格子自动展开）
        经典扫雷机制：点击数字为0的格子时，自动展开所有相邻的空白格子（数字=0），
        直到遇到数字>0的格子或怪物格子为止
        :param row: 起始行
        :param col: 起始列
        """
        # 收集所有需要揭示的格子
        cells_to_reveal = self._collect_blank_area(row, col)
        
        if not cells_to_reveal:
            return
        
        # 立即揭示第一个格子（被点击的格子）
        first_cell = self.grid[row][col]
        if not first_cell.is_revealed():
            first_cell.reveal()
        
        # 如果只有一个格子，不需要动画
        if len(cells_to_reveal) <= 1:
            return
        
        # 计算每个格子的距离（用于动画延迟）
        import time
        current_time = time.time()
        animation_delay = 0.03  # 每个格子延迟30毫秒
        
        # 使用BFS计算距离（从起始点开始）
        from collections import deque
        queue = deque([(row, col, 0)])
        visited = {(row, col): 0}
        
        # 收集所有需要揭示的格子位置
        cells_set = {(r, c) for r, c, _ in cells_to_reveal}
        
        while queue:
            r, c, dist = queue.popleft()
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if (nr, nc) not in visited and (nr, nc) in cells_set:
                            # 这个格子需要揭示，计算距离
                            visited[(nr, nc)] = dist + 1
                            # 如果是数字为0的格子，继续BFS扩展
                            cell = self.grid[nr][nc]
                            if isinstance(cell, NumberCell) and cell.number == 0:
                                queue.append((nr, nc, dist + 1))
        
        # 添加到动画队列（排除第一个已揭示的格子）
        for r, c, _ in cells_to_reveal:
            if (r, c) == (row, col):
                continue  # 跳过第一个格子（已立即揭示）
            # 获取该格子到起始点的距离
            distance = visited.get((r, c), 0)
            if distance > 0:  # 有距离的格子才添加到动画队列
                reveal_time = current_time + distance * animation_delay
                self.reveal_animation_queue.append((r, c, reveal_time))
    
    def click_cell(self, row, col):
        """
        点击格子（仅用于揭示，不再自动部署兵种）
        :param row: 行
        :param col: 列
        :return: 操作是否成功
        """
        if self.game_over:
            return False
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        
        cell = self.grid[row][col]
        
        # 如果格子未揭示，揭示它
        if not cell.is_revealed():
            # 如果是怪物格子，触发怪物（待机状态，不进行战斗）
            if isinstance(cell, MonsterCell):
                cell.trigger()
                # 使用正态分布生成怪物战力（1-32）
                monster_power = self._weighted_random_monster_power()
                cell.set_monster_power(monster_power)
                # 不进行战斗结算，怪物处于待机状态
            elif isinstance(cell, TaskCell):
                # 任务格子，揭示它
                cell.reveal()
            else:
                # 数字格子，实现空白区域自动展开（只有数字为0时才展开）
                if isinstance(cell, NumberCell) and cell.number == 0:
                    # 数字为0，自动展开空白区域
                    self._reveal_blank_area(row, col)
                else:
                    # 数字>0，只揭示当前格子
                    cell.reveal()
            
            return True
        
        # 如果格子已揭示，检查是否是已触发的怪物（待机状态）
        if isinstance(cell, MonsterCell) and cell.triggered and cell.battle_won is None:
            # 再次点击已触发的怪物，进行战斗结算
            self._battle_settlement(cell)
            return True
        
        # 如果格子已揭示，检查是否是任务格子
        if isinstance(cell, TaskCell):
            # 如果任务已完成但未确认，再次点击确认任务
            if cell.task_completed and not cell.task_claimed:
                if cell.claim_task():
                    # 任务已确认，检查是否通关
                    self._check_win_condition()
                    return True
            return True
        
        return False
    
    def deploy_card(self, card, row, col):
        """
        部署卡牌到指定格子
        规则：
        - 可以将高数值卡牌放到低数值区域，但战力会降低到区域数值
        - 不能将低数值卡牌放到高数值区域
        :param card: 要部署的卡牌
        :param row: 行
        :param col: 列
        :return: 是否部署成功
        """
        if self.game_over:
            return False
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        
        if card not in self.hand:
            return False  # 卡牌不在手牌中
        
        cell = self.grid[row][col]
        
        # 只能部署到已揭示的数字格子
        if not cell.is_revealed() or not isinstance(cell, NumberCell):
            return False
        
        # 不能部署到数字为0的格子
        if cell.number == 0:
            return False
        
        # 规则：卡牌数值必须 >= 格子数值（允许高数值卡牌放到低数值区域）
        if card.unit_type < cell.number:
            return False  # 低数值卡牌不能放到高数值区域
        
        # 格子不能已有兵种
        if cell.has_unit():
            return False
        
        # 部署兵种
        # 如果卡牌数值 > 格子数值，战力会降低到格子数值
        # 如果卡牌数值 == 格子数值，战力保持原值
        actual_power = cell.number  # 实际战力 = 格子数值
        unit = card.create_unit_with_power(actual_power)
        cell.deploy_unit(unit)
        
        # 从手牌移除卡牌
        self.hand.remove(card)
        
        # 检查并应用团结一致效果
        self._check_and_apply_unity_effect(row, col)
        
        return True
    
    def end_turn(self):
        """
        结束当前回合
        规则：丢弃手上现有卡牌，并重新抽牌
        :return: 是否成功结束回合
        """
        if self.game_over:
            return False
        
        # 丢弃手上现有卡牌
        self.hand.clear()
        
        # 发新卡牌
        self._deal_cards()
        
        # 回合数+1
        self.current_turn += 1
        
        return True
    
    def _deal_cards(self):
        """发牌（每回合发3张随机卡牌，低数值卡牌概率更高）"""
        # 如果手牌已满，不再发牌
        if len(self.hand) >= MAX_HAND_SIZE:
            return
        
        # 计算需要发的牌数
        cards_to_deal = min(CARDS_PER_TURN, MAX_HAND_SIZE - len(self.hand))
        
        # 发牌
        for _ in range(cards_to_deal):
            # 使用加权随机生成1-8的兵种类型
            # 低数值（1-4）概率高，高数值（5-8）概率低
            unit_type = self._weighted_random_unit_type()
            card = Card(unit_type)
            self.hand.append(card)
    
    def _weighted_random_unit_type(self):
        """
        加权随机生成兵种类型
        低数值卡牌（1-4）有更高概率，避免卡手
        返回: 1-8 的兵种类型
        """
        # 定义权重：低数值权重高，高数值权重低
        # 1-4: 每个权重 5 (总共20)
        # 5-6: 每个权重 3 (总共6)
        # 7-8: 每个权重 2 (总共4)
        # 总权重: 30
        weights = {
            1: 5, 2: 5, 3: 5, 4: 5,  # 低数值，高权重
            5: 3, 6: 3,              # 中数值，中权重（提升）
            7: 2, 8: 2               # 高数值，低权重（提升）
        }
        
        # 构建加权列表
        weighted_list = []
        for unit_type, weight in weights.items():
            weighted_list.extend([unit_type] * weight)
        
        # 从加权列表中随机选择
        return random.choice(weighted_list)
    
    def _weighted_random_monster_power(self):
        """
        使用正态分布生成怪物战力（1-32）
        均值约16，标准差约8，使得中间值概率高，两端概率低
        数值越高权重越小（通过正态分布自然实现）
        返回: 1-32 的怪物战力值
        """
        mean = 16.0  # 均值，接近中间值
        std_dev = 8.0  # 标准差
        
        # 使用正态分布生成值，如果超出范围则重新采样
        max_attempts = 100
        for _ in range(max_attempts):
            # 使用Box-Muller变换生成正态分布随机数
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            value = mean + std_dev * z
            
            # 截断到1-32范围
            power = int(round(value))
            if 1 <= power <= 32:
                return power
        
        # 如果多次尝试都失败，返回中间值
        return 16
    
    def update(self):
        """
        更新游戏状态
        """
        if self.game_over:
            return
        
        # 处理揭示动画
        import time
        current_time = time.time()
        new_queue = []
        for row, col, reveal_time in self.reveal_animation_queue:
            if current_time >= reveal_time:
                # 时间到了，揭示格子
                cell = self.grid[row][col]
                if not cell.is_revealed():
                    cell.reveal()
            else:
                # 还没到时间，保留在队列中
                new_queue.append((row, col, reveal_time))
        self.reveal_animation_queue = new_queue
        
        # 处理团结一致动画（0.5秒后自动清除）
        unity_animation_duration = 0.5
        new_unity_queue = []
        for row, col, start_time in self.unity_animation_queue:
            if current_time < start_time + unity_animation_duration:
                # 动画还在进行中，保留
                new_unity_queue.append((row, col, start_time))
        self.unity_animation_queue = new_unity_queue
        
        # 检查任务完成状态
        if self.task_cell and not self.task_cell.task_completed:
            self.check_task_completion()
        
        # 检查胜利条件：玩家生命值没有降到0，且通关任务已完成并已确认
        if self.health > 0 and not self.game_over:
            self._check_win_condition()
    
    def _battle_settlement(self, monster_cell):
        """
        战斗结算
        :param monster_cell: 怪物格子
        """
        # 计算玩家战力（相邻8格已部署兵种总战力），向下取整
        player_power = 0
        for cell in self._get_adjacent_cells(monster_cell.row, monster_cell.col):
            player_power += cell.get_power()
        player_power = int(player_power)
        
        # 获取怪物战力（已经是整数）
        monster_power = int(monster_cell.monster_power)
        
        # 判断胜负
        if player_power >= monster_power:
            # 玩家获胜，消灭怪物
            monster_cell.set_battle_result(True)  # 玩家胜利
            # 从monsters列表中移除（标记为已消灭）
            if monster_cell in self.monsters:
                self.monsters.remove(monster_cell)
        else:
            # 玩家失败，扣除生命值
            monster_cell.set_battle_result(False)  # 怪物胜利
            self.health -= 1
            if self.health <= 0:
                self.game_over = True
                self.game_won = False
    
    def get_cell(self, row, col):
        """获取指定位置的格子"""
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col]
        return None
    
    
    def _check_all_monsters_settled(self):
        """检查所有怪物是否都已结算（battle_won不为None）"""
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, MonsterCell):
                    # 如果怪物还没有结算（battle_won为None），则未完成
                    if cell.battle_won is None:
                        return False
        return True
    
    def check_task_completion(self):
        """
        检查任务完成状态并更新任务格子
        """
        if not self.task_cell or not self.main_task_type:
            return
        
        # 如果任务已完成，不需要再次检查
        if self.task_cell.task_completed:
            return
        
        # 使用任务判定器检查任务是否完成
        is_completed = self.task_validator.is_task_completed(
            self.main_task_type, 
            self.task_cell, 
            self
        )
        
        # 如果任务完成，标记任务格子
        if is_completed:
            self.task_cell.complete_task()
    
    def _check_win_condition(self):
        """
        检查胜利条件：通关任务是否已完成并已确认
        """
        if self.task_cell and self.task_cell.task_claimed:
            self.game_over = True
            self.game_won = True
    
    def get_player_power_around_monster(self, monster_cell):
        """获取怪物周围玩家的战力（向下取整）"""
        player_power = 0
        for cell in self._get_adjacent_cells(monster_cell.row, monster_cell.col):
            player_power += cell.get_power()
        return int(player_power)
    
    def get_cell_info(self, row, col):
        """
        获取格子的详细信息
        只有已揭示的格子才显示详细信息，未揭示的格子不显示具体信息（防止作弊）
        :param row: 行
        :param col: 列
        :return: 详细信息文本列表
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            return []
        
        cell = self.grid[row][col]
        if not cell:
            return []
        
        info = []
        
        # 如果格子未揭示，只显示基本信息，不显示具体内容
        if not cell.is_revealed():
            info.append(f"未揭示格子 ({row}, {col})")
            return info
        
        # 已揭示的格子显示详细信息
        if isinstance(cell, NumberCell):
            info.append(f"数字格子 ({row}, {col})")
            info.append(f"数字: {cell.number}")
            if cell.has_unit():
                info.append(f"已部署: {cell.unit.name}")
                # 显示实际战力（考虑团结一致效果）
                actual_power = cell.unit.get_effective_power()
                if cell.unit.unity_bonus_count > 0:
                    mark = "*" * cell.unit.unity_bonus_count
                    info.append(f"战力: {actual_power}{mark}")
                else:
                    info.append(f"战力: {actual_power}")
            else:
                info.append("未部署兵种")
        elif isinstance(cell, MonsterCell):
            info.append(f"怪物格子 ({row}, {col})")
            if cell.triggered:
                info.append(f"怪物战力: {int(cell.monster_power)}")
                player_power = self.get_player_power_around_monster(cell)
                info.append(f"周围玩家战力: {player_power}")
                power_diff = player_power - int(cell.monster_power)
                if power_diff >= 0:
                    info.append(f"战力优势: +{power_diff}")
                else:
                    info.append(f"战力不足: {power_diff}")
                if cell.battle_won is not None:
                    if cell.battle_won:
                        info.append("战斗结果: 玩家胜利")
                    else:
                        info.append("战斗结果: 怪物胜利")
            else:
                info.append("未触发")
        elif isinstance(cell, TaskCell):
            return self.get_task_info(row, col)
        else:
            info.append(f"未知格子 ({row}, {col})")
        
        return info
    
    def get_monster_info(self, monster_cell):
        """
        获取怪物的详细信息
        只有已揭示的怪物才显示详细信息，未揭示的怪物不显示具体信息（防止作弊）
        :param monster_cell: 怪物格子
        :return: 详细信息文本列表
        """
        if not isinstance(monster_cell, MonsterCell):
            return []
        
        info = []
        
        # 如果怪物未揭示，只显示基本信息，不显示具体内容
        if not monster_cell.is_revealed():
            info.append(f"未揭示格子 ({monster_cell.row}, {monster_cell.col})")
            return info
        
        # 已揭示的怪物显示详细信息
        info.append(f"怪物 ({monster_cell.row}, {monster_cell.col})")
        
        if monster_cell.triggered:
            info.append(f"怪物战力: {int(monster_cell.monster_power)}")
            player_power = self.get_player_power_around_monster(monster_cell)
            info.append(f"周围玩家战力: {player_power}")
            power_diff = player_power - int(monster_cell.monster_power)
            if power_diff >= 0:
                info.append(f"战力优势: +{power_diff}")
            else:
                info.append(f"战力不足: {power_diff}")
            if monster_cell.battle_won is not None:
                if monster_cell.battle_won:
                    info.append("战斗结果: 玩家胜利")
                else:
                    info.append("战斗结果: 怪物胜利")
        else:
            info.append("未触发")
        
        return info
    
    def get_task_info(self, row, col):
        """
        获取任务格子的详细信息
        只有已揭示的任务才显示详细信息，未揭示的任务不显示具体信息（防止作弊）
        :param row: 行
        :param col: 列
        :return: 详细信息文本列表
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            return []
        
        cell = self.grid[row][col]
        if not isinstance(cell, TaskCell):
            return []
        
        info = []
        
        # 如果任务未揭示，只显示基本信息，不显示具体内容
        if not cell.is_revealed():
            info.append(f"未揭示格子 ({row}, {col})")
            return info
        
        # 已揭示的任务显示详细信息
        from config_mgr import TASK_TYPE_NAMES, TASK_TYPE_DESCRIPTIONS
        task_name = TASK_TYPE_NAMES.get(cell.task_type, "任务")
        task_desc = TASK_TYPE_DESCRIPTIONS.get(cell.task_type, "")
        
        info.append(f"任务格子 ({row}, {col})")
        info.append(f"任务: {task_name}")
        info.append(f"要求: {task_desc}")
        
        if cell.task_claimed:
            info.append("状态: 已确认")
        elif cell.task_completed:
            info.append("状态: 已完成")
            info.append("提示: 再次点击确认")
        else:
            info.append("状态: 进行中")
            # 根据任务类型显示进度信息
            if cell.task_type == TaskType.EXPLORE_ADJACENT:
                # 显示已探查的相邻格子数量
                adjacent_cells = self._get_adjacent_cells(row, col)
                explored_count = sum(1 for c in adjacent_cells if c.is_revealed())
                info.append(f"进度: {explored_count}/8 已探查")
            elif cell.task_type == TaskType.BATTLE_ALL_MONSTERS:
                # 显示已战斗的怪物数量
                total_monsters = sum(1 for r in range(self.height) for c in range(self.width)
                                   if isinstance(self.grid[r][c], MonsterCell))
                battled_monsters = sum(1 for r in range(self.height) for c in range(self.width)
                                     if isinstance(self.grid[r][c], MonsterCell)
                                     and self.grid[r][c].battle_won is not None)
                info.append(f"进度: {battled_monsters}/{total_monsters} 已战斗")
            elif cell.task_type == TaskType.FIND_TASK:
                info.append("进度: 已完成（找到任务）")
        
        return info
    
    def get_game_state_text(self):
        """获取游戏状态文本"""
        state = []
        state.append(f"生命值: {self.health}")
        state.append(f"回合数: {self.current_turn}")
        state.append(f"手牌数: {len(self.hand)}")
        # 剩余怪物 = 所有未结算的怪物（battle_won为None）
        remaining_monsters = sum(1 for row in range(self.height) for col in range(self.width) 
                                if isinstance(self.grid[row][col], MonsterCell) 
                                and self.grid[row][col].battle_won is None)
        state.append(f"剩余怪物: {remaining_monsters}")
        
        if self.game_over:
            state.append("")
            if self.game_won:
                state.append("游戏胜利！")
            else:
                state.append("游戏失败！")
        
        return state
    
    def _check_unity_effect(self, row, col):
        """
        检查指定位置所在的行和列是否有3个或以上战士
        :param row: 行
        :param col: 列
        :return: (row_warriors, col_warriors) 元组，每个是符合条件的战士位置列表
        """
        row_warriors = []
        col_warriors = []
        
        # 检查行
        for c in range(self.width):
            cell = self.grid[row][c]
            if (isinstance(cell, NumberCell) and cell.has_unit() and 
                cell.unit.unit_type == 1):  # 战士类型为1
                row_warriors.append((row, c))
        
        # 检查列
        for r in range(self.height):
            cell = self.grid[r][col]
            if (isinstance(cell, NumberCell) and cell.has_unit() and 
                cell.unit.unit_type == 1):  # 战士类型为1
                col_warriors.append((r, col))
        
        return row_warriors, col_warriors
    
    def _apply_unity_effect(self, warriors):
        """
        为符合条件的战士应用战力翻倍效果（可以叠加）
        :param warriors: 战士位置列表 [(row, col), ...]
        :return: (应用效果的战士位置列表, 新获得效果的战士位置列表) 用于动画
        """
        applied_warriors = []
        newly_triggered = []  # 新获得效果的战士（用于动画）
        
        for row, col in warriors:
            cell = self.grid[row][col]
            if (isinstance(cell, NumberCell) and cell.has_unit() and 
                cell.unit.unit_type == 1):
                # 记录应用效果前的状态
                old_count = cell.unit.unity_bonus_count
                # 应用效果（叠加，最多2次）
                if cell.unit.unity_bonus_count < 2:
                    cell.unit.unity_bonus_count += 1
                    applied_warriors.append((row, col))
                    # 如果是新获得效果（从0到1，或从1到2），记录用于动画
                    if old_count == 0:
                        newly_triggered.append((row, col))
        
        return applied_warriors, newly_triggered
    
    def _check_and_apply_unity_effect(self, row, col):
        """
        检查并应用团结一致效果
        重新计算所有行和列，确保效果正确应用
        :param row: 行（新部署的位置，用于触发检查）
        :param col: 列（新部署的位置，用于触发检查）
        """
        # 先清除所有战士的团结一致效果（重新计算）
        self._clear_all_unity_effects()
        
        import time
        current_time = time.time()
        newly_triggered_set = set()  # 用于避免重复添加动画
        all_newly_triggered = []  # 收集所有新获得效果的战士位置（用于动画）
        
        # 检查所有行
        for r in range(self.height):
            row_warriors = []
            for c in range(self.width):
                cell = self.grid[r][c]
                if (isinstance(cell, NumberCell) and cell.has_unit() and 
                    cell.unit.unit_type == 1):  # 战士类型为1
                    row_warriors.append((r, c))
            
            # 如果行有3个或以上战士，应用效果
            if len(row_warriors) >= 3:
                applied, newly_triggered = self._apply_unity_effect(row_warriors)
                for pos in newly_triggered:
                    if pos not in newly_triggered_set:
                        newly_triggered_set.add(pos)
                        all_newly_triggered.append(pos)
        
        # 检查所有列
        for c in range(self.width):
            col_warriors = []
            for r in range(self.height):
                cell = self.grid[r][c]
                if (isinstance(cell, NumberCell) and cell.has_unit() and 
                    cell.unit.unit_type == 1):  # 战士类型为1
                    col_warriors.append((r, c))
            
            # 如果列有3个或以上战士，应用效果
            if len(col_warriors) >= 3:
                applied, newly_triggered = self._apply_unity_effect(col_warriors)
                for pos in newly_triggered:
                    if pos not in newly_triggered_set:
                        newly_triggered_set.add(pos)
                        all_newly_triggered.append(pos)
        
        # 只对新获得效果的战士播放动画，依次播放，每个动画间隔0.1秒
        if all_newly_triggered:
            animation_delay = 0.1
            for i, pos in enumerate(all_newly_triggered):
                start_time = current_time + i * animation_delay
                self.unity_animation_queue.append((pos[0], pos[1], start_time))
    
    def _clear_all_unity_effects(self):
        """清除所有战士的团结一致效果"""
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                if isinstance(cell, NumberCell) and cell.has_unit():
                    cell.unit.unity_bonus_count = 0

