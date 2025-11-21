# -*- coding: utf-8 -*-
"""
游戏核心逻辑
"""
import random
from cell import Cell, NumberCell, MonsterCell, CellState
from unit import Unit
from card import Card
from config import CARDS_PER_TURN, MAX_HAND_SIZE


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
        self.monsters = []  # 所有怪物列表
        self.reveal_animation_queue = []  # 揭示动画队列 [(row, col, reveal_time), ...]
        
        # 回合系统
        self.current_turn = 1  # 当前回合数
        self.hand = []  # 玩家手牌列表
        
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
            # 如果是怪物格子，触发战斗
            if isinstance(cell, MonsterCell):
                cell.trigger()
                # 计算怪物战力
                adjacent_numbers = self._get_adjacent_numbers(row, col)
                monster_power = sum(adjacent_numbers) / 2
                cell.set_monster_power(monster_power)
            else:
                # 数字格子，实现空白区域自动展开（只有数字为0时才展开）
                if isinstance(cell, NumberCell) and cell.number == 0:
                    # 数字为0，自动展开空白区域
                    self._reveal_blank_area(row, col)
                else:
                    # 数字>0，只揭示当前格子
                    cell.reveal()
            
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
        
        return True
    
    def end_turn(self):
        """
        结束当前回合
        规则：丢弃手上现有卡牌，并重新抽牌
        :return: 是否成功结束回合
        """
        if self.game_over:
            return False
        
        # 消耗所有激活怪物的倒计时回合
        self._consume_all_active_monsters_countdown()
        
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
        # 5-6: 每个权重 2 (总共4)
        # 7-8: 每个权重 1 (总共2)
        # 总权重: 26
        weights = {
            1: 5, 2: 5, 3: 5, 4: 5,  # 低数值，高权重
            5: 2, 6: 2,              # 中数值，中权重
            7: 1, 8: 1               # 高数值，低权重
        }
        
        # 构建加权列表
        weighted_list = []
        for unit_type, weight in weights.items():
            weighted_list.extend([unit_type] * weight)
        
        # 从加权列表中随机选择
        return random.choice(weighted_list)
    
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
        
        # 检查胜利条件：玩家生命值没有降到0，且所有怪物都被结算了
        if self.health > 0 and not self.game_over:
            # 检查所有怪物是否都已结算（battle_won不为None）
            all_monsters_settled = self._check_all_monsters_settled()
            
            if all_monsters_settled:
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
    
    def _consume_all_active_monsters_countdown(self):
        """消耗所有激活怪物的倒计时回合"""
        monsters_to_settle = []
        for monster in self.monsters:
            if monster.is_countdown_active():
                monster.consume_countdown_round()
                # 检查倒计时是否结束
                if not monster.is_countdown_active():
                    monsters_to_settle.append(monster)
        
        # 结算所有倒计时结束的怪物
        for monster in monsters_to_settle:
            self._battle_settlement(monster)
    
    def get_active_monsters(self):
        """获取所有激活的怪物（倒计时中的）"""
        return [m for m in self.monsters if m.is_countdown_active()]
    
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
        state.append(f"回合数: {self.current_turn}")
        state.append(f"手牌数: {len(self.hand)}")
        active_monsters = self.get_active_monsters()
        state.append(f"激活怪物: {len(active_monsters)}")
        # 剩余怪物 = 所有未结算的怪物（battle_won为None）
        remaining_monsters = sum(1 for row in range(self.height) for col in range(self.width) 
                                if isinstance(self.grid[row][col], MonsterCell) 
                                and self.grid[row][col].battle_won is None)
        state.append(f"剩余怪物: {remaining_monsters}")
        
        # 显示所有激活怪物的信息
        if active_monsters:
            state.append("")
            for i, monster in enumerate(active_monsters[:3]):  # 最多显示3个
                remaining = monster.get_countdown_remaining()
                state.append(f"怪物{i+1} 回合: {remaining}")
                monster_power = monster.monster_power
                player_power = self.get_player_power_around_monster(monster)
                power_diff = player_power - monster_power
                if power_diff >= 0:
                    state.append(f"  优势: +{power_diff:.1f}")
                else:
                    state.append(f"  不足: {power_diff:.1f}")
            if len(active_monsters) > 3:
                state.append(f"...还有{len(active_monsters)-3}个")
        
        if self.game_over:
            state.append("")
            if self.game_won:
                state.append("游戏胜利！")
            else:
                state.append("游戏失败！")
        
        return state

