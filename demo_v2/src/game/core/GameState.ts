import { GameState, GameStatus, Card, Cell, RevealResult, DeployResult, BattleSettlementResult, Difficulty, CellState, TaskCell as TaskCellType, CellState as CS } from '../../types';
import { MapGenerator } from '../systems/MapGenerator';
import { CardSystem } from '../systems/CardSystem';
import { BattleSystem } from '../systems/BattleSystem';
import { TaskValidator } from '../systems/TaskValidator';
import { TaskCellEntity, MonsterCellEntity, NumberCellEntity, UnitEntity } from '../entities';
import { HEALTH_CONFIG, CARD_CONFIG } from '../../config/gameConfig';

// 辅助函数：检查格子状态
const isRevealed = (cell: Cell): boolean => {
  return cell.state === CS.REVEALED || cell.state === CS.DEPLOYED;
};

const isHidden = (cell: Cell): boolean => {
  return cell.state === CS.HIDDEN;
};

const revealCell = (cell: Cell): void => {
  (cell as any).state = CS.REVEALED;
};

/**
 * 游戏状态核心类
 */
export class GameStateCore {
  private status: GameStatus;
  private grid: Cell[][];
  private hand: Card[];
  private maxHandSize: number;
  private taskCell: TaskCellType | null;
  private mapGenerator: MapGenerator;
  private cardSystem: CardSystem;
  private battleSystem: BattleSystem;
  private taskValidator: TaskValidator;

  constructor(difficulty: Difficulty) {
    // 初始化游戏状态
    this.status = {
      health: HEALTH_CONFIG.INITIAL_HEALTH,
      currentTurn: 1,
      gameOver: false,
      gameWon: false,
      difficulty,
    };

    this.maxHandSize = CARD_CONFIG.MAX_HAND_SIZE;
    this.hand = [];
    this.taskCell = null;

    // 初始化系统
    this.mapGenerator = new MapGenerator(difficulty);
    this.cardSystem = new CardSystem();
    this.battleSystem = new BattleSystem();
    this.taskValidator = new TaskValidator();

    // 生成地图
    this.grid = this.mapGenerator.generate();

    // 找到任务格子
    this.findTaskCell();

    // 发初始卡牌
    this.dealInitialCards();
  }

  /**
   * 获取当前游戏状态
   */
  getState(): GameState {
    return {
      status: { ...this.status },
      grid: this.grid,
      hand: [...this.hand],
      maxHandSize: this.maxHandSize,
      taskCell: this.taskCell,
    };
  }

  /**
   * 揭示格子
   */
  revealCell(row: number, col: number): RevealResult {
    if (this.status.gameOver) {
      return { success: false };
    }

    const cell = this.grid[row][col];

    // 已揭示的格子不能再揭示
    if (isRevealed(cell)) {
      return { success: false };
    }

    // 揭示格子
    revealCell(cell);

    // 根据格子类型处理
    if (cell instanceof MonsterCellEntity) {
      return this.handleMonsterReveal(cell);
    } else if (cell instanceof NumberCellEntity) {
      return this.handleNumberCellReveal(cell);
    } else if (cell instanceof TaskCellEntity) {
      return this.handleTaskReveal(cell);
    }

    return { success: true, cellRevealed: cell };
  }

  /**
   * 处理怪物格子揭示
   */
  private handleMonsterReveal(monsterCell: MonsterCellEntity): RevealResult {
    monsterCell.trigger();
    this.checkAndUpdateTask();
    return {
      success: true,
      monsterTriggered: monsterCell,
    };
  }

  /**
   * 处理数字格子揭示
   */
  private handleNumberCellReveal(numberCell: NumberCellEntity): RevealResult {
    // 如果数字为0，自动展开相邻格子
    if (numberCell.number === 0) {
      const revealedArea = this.revealBlankArea(numberCell.row, numberCell.col);
      this.checkAndUpdateTask();
      return {
        success: true,
        areaRevealed: revealedArea,
      };
    }

    this.checkAndUpdateTask();
    return {
      success: true,
      cellRevealed: numberCell,
    };
  }

  /**
   * 处理任务格子揭示
   */
  private handleTaskReveal(taskCell: TaskCellEntity): RevealResult {
    this.taskValidator.updateTaskStatus(this.grid, taskCell);
    return {
      success: true,
      taskRevealed: taskCell,
    };
  }

  /**
   * 展开空白区域（数字为0的格子）
   */
  private revealBlankArea(startRow: number, startCol: number): Cell[] {
    const revealed: Cell[] = [];
    const queue: [number, number][] = [[startRow, startCol]];
    const visited = new Set<string>();

    while (queue.length > 0) {
      const [row, col] = queue.shift()!;
      const key = `${row},${col}`;

      if (visited.has(key)) {
        continue;
      }

      visited.add(key);
      const cell = this.grid[row][col];

      if (!isHidden(cell) || cell instanceof MonsterCellEntity || cell instanceof TaskCellEntity) {
        continue;
      }

      revealCell(cell);
      revealed.push(cell);

      if (cell instanceof NumberCellEntity && cell.number === 0) {
        const neighbors = this.mapGenerator.getNeighbors(row, col);
        queue.push(...neighbors);
      }
    }

    return revealed;
  }

  /**
   * 部署卡牌
   */
  deployCard(cardIndex: number, row: number, col: number): DeployResult {
    if (this.status.gameOver) {
      return { success: false, message: '游戏已结束' };
    }

    if (cardIndex < 0 || cardIndex >= this.hand.length) {
      return { success: false, message: '无效的卡牌索引' };
    }

    const card = this.hand[cardIndex];
    const cell = this.grid[row][col];

    // 检查是否可以部署
    if (!(cell instanceof NumberCellEntity)) {
      return { success: false, message: '只能部署到数字格子' };
    }

    if (!isRevealed(cell)) {
      return { success: false, message: '格子未揭示' };
    }

    if (!this.cardSystem.canDeployCard(card, cell.number)) {
      return { success: false, message: '卡牌战力不足' };
    }

    if (cell.unit) {
      return { success: false, message: '格子已有兵种' };
    }

    // 部署卡牌
    const unit = new UnitEntity(card.unitType);
    cell.deployUnit(unit);

    // 从手牌中移除卡牌
    this.hand = this.cardSystem.removeCardFromHand(this.hand, cardIndex);

    // 应用团结一致效果
    this.battleSystem.applyUnityEffects(this.grid);

    return { success: true, cardUsed: true };
  }

  /**
   * 战斗怪物
   */
  battleMonster(row: number, col: number): BattleSettlementResult {
    if (this.status.gameOver) {
      return {
        result: 'PENDING' as any,
        playerPower: 0,
        monsterPower: 0,
        damage: 0,
      };
    }

    const cell = this.grid[row][col];

    if (!(cell instanceof MonsterCellEntity)) {
      return {
        result: 'PENDING' as any,
        playerPower: 0,
        monsterPower: 0,
        damage: 0,
      };
    }

    if (!cell.canBattle()) {
      return {
        result: 'PENDING' as any,
        playerPower: 0,
        monsterPower: 0,
        damage: 0,
      };
    }

    // 计算玩家战力
    const playerPower = this.battleSystem.calculatePlayerPower(this.grid, row, col);
    const monsterPower = cell.power;

    // 战斗结算
    const result = this.battleSystem.resolveBattle(playerPower, monsterPower);
    cell.setBattleResult(result.result);

    // 处理战斗结果
    if (result.result === 'DEFEAT') {
      this.status.health -= result.damage;
      if (this.status.health <= 0) {
        this.status.gameOver = true;
        this.status.gameWon = false;
      }
    }

    // 检查任务状态
    this.checkAndUpdateTask();

    return result;
  }

  /**
   * 结束回合
   */
  endTurn(): void {
    if (this.status.gameOver) {
      return;
    }

    // 丢弃当前手牌
    this.hand = [];

    // 发新牌
    const newCards = this.cardSystem.dealCards(CARD_CONFIG.DEAL_COUNT);
    this.hand = newCards.slice(0, Math.min(newCards.length, this.maxHandSize));

    // 增加回合数
    this.status.currentTurn++;
  }

  /**
   * 确认任务
   */
  confirmTask(): boolean {
    if (!this.taskCell || !(this.taskCell instanceof TaskCellEntity)) {
      return false;
    }

    const success = this.taskValidator.confirmTask(this.grid, this.taskCell);
    if (success) {
      this.status.gameWon = true;
      this.status.gameOver = true;
    }

    return success;
  }

  /**
   * 发初始卡牌
   */
  private dealInitialCards(): void {
    this.hand = this.cardSystem.dealCards(CARD_CONFIG.DEAL_COUNT);
  }

  /**
   * 找到任务格子
   */
  private findTaskCell(): void {
    for (let row = 0; row < this.grid.length; row++) {
      for (let col = 0; col < this.grid[row].length; col++) {
        const cell = this.grid[row][col];
        if (cell instanceof TaskCellEntity) {
          this.taskCell = cell.toDTO();
          return;
        }
      }
    }
  }

  /**
   * 检查并更新任务状态
   */
  private checkAndUpdateTask(): void {
    if (!this.taskCell) {
      return;
    }

    // 找到任务格子实体
    let taskEntity: TaskCellEntity | null = null;
    for (let row = 0; row < this.grid.length; row++) {
      for (let col = 0; col < this.grid[row].length; col++) {
        const cell = this.grid[row][col];
        if (cell instanceof TaskCellEntity) {
          taskEntity = cell;
          break;
        }
      }
      if (taskEntity) break;
    }

    if (taskEntity) {
      this.taskValidator.updateTaskStatus(this.grid, taskEntity);
      this.taskCell = taskEntity.toDTO();
    }
  }

  /**
   * 获取游戏状态
   */
  getGameStatus(): GameStatus {
    return { ...this.status };
  }

  /**
   * 获取地图
   */
  getGrid(): Cell[][] {
    return this.grid;
  }

  /**
   * 获取手牌
   */
  getHand(): Card[] {
    return [...this.hand];
  }

  /**
   * 获取任务格子
   */
  getTaskCell(): TaskCellType | null {
    return this.taskCell;
  }
}
