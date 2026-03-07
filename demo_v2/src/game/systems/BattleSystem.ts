import { Cell, BattleSettlementResult, BattleResult, UnitType, CellState as CS } from '../../types';
import { MonsterCellEntity, NumberCellEntity } from '../entities';
import { UNITY_CONFIG } from '../../config/gameConfig';

// 辅助函数
const isRevealed = (cell: Cell): boolean => {
  return cell.state === CS.REVEALED || cell.state === CS.DEPLOYED;
};

/**
 * 战斗系统
 */
export class BattleSystem {
  /**
   * 计算指定格子周围8格的玩家总战力
   */
  calculatePlayerPower(grid: Cell[][], row: number, col: number): number {
    let totalPower = 0;
    const neighbors = this.getNeighbors(grid, row, col);

    for (const [nRow, nCol] of neighbors) {
      const cell = grid[nRow][nCol];

      // 只计算已部署兵种的格子
      if (cell.unit && isRevealed(cell)) {
        totalPower += this.getUnitEffectivePower(grid, nRow, nCol);
      }
    }

    return totalPower;
  }

  /**
   * 获取兵种的实际战力（考虑团结一致效果）
   */
  private getUnitEffectivePower(grid: Cell[][], row: number, col: number): number {
    const cell = grid[row][col];

    if (!cell.unit) {
      return 0;
    }

    let power = cell.unit.power;

    // 检查团结一致效果
    if (cell.unit.unitType === UnitType.WARRIOR) {
      const unityBonus = this.checkUnityBonus(grid, row, col);
      if (unityBonus >= 1) {
        power *= UNITY_CONFIG.BONUS_MULTIPLIER; // 2倍
      }
      if (unityBonus >= 2) {
        power *= UNITY_CONFIG.BONUS_MULTIPLIER; // 再2倍，总共4倍
      }
    }

    return power;
  }

  /**
   * 检查团结一致效果
   * 返回值: 0 = 无效果, 1 = 行或列满足, 2 = 行和列都满足
   */
  checkUnityBonus(grid: Cell[][], row: number, col: number): number {
    let bonusCount = 0;
    const cell = grid[row][col];

    // 只有战士才能触发团结一致效果
    if (!cell.unit || cell.unit.unitType !== UnitType.WARRIOR) {
      return 0;
    }

    // 检查行的战士数量
    const warriorCountInRow = this.countWarriorsInRow(grid, row);
    if (warriorCountInRow >= UNITY_CONFIG.MIN_COUNT) {
      bonusCount++;
    }

    // 检查列的战士数量
    const warriorCountInCol = this.countWarriorsInCol(grid, col);
    if (warriorCountInCol >= UNITY_CONFIG.MIN_COUNT) {
      bonusCount++;
    }

    return bonusCount;
  }

  /**
   * 计算指定行的战士数量
   */
  private countWarriorsInRow(grid: Cell[][], row: number): number {
    let count = 0;
    for (let col = 0; col < grid[row].length; col++) {
      const cell = grid[row][col];
      if (cell.unit && cell.unit.unitType === UnitType.WARRIOR) {
        count++;
      }
    }
    return count;
  }

  /**
   * 计算指定列的战士数量
   */
  private countWarriorsInCol(grid: Cell[][], col: number): number {
    let count = 0;
    for (let row = 0; row < grid.length; row++) {
      const cell = grid[row][col];
      if (cell.unit && cell.unit.unitType === UnitType.WARRIOR) {
        count++;
      }
    }
    return count;
  }

  /**
   * 战斗结算
   */
  resolveBattle(playerPower: number, monsterPower: number): BattleSettlementResult {
    const victory = playerPower >= monsterPower;

    return {
      result: victory ? BattleResult.VICTORY : BattleResult.DEFEAT,
      playerPower,
      monsterPower,
      damage: victory ? 0 : 1,
    };
  }

  /**
   * 应用团结一致效果到所有兵种
   */
  applyUnityEffects(grid: Cell[][]): void {
    // 首先重置所有兵种的团结一致效果
    this.resetAllUnityBonuses(grid);

    // 然后检查并应用新的团结一致效果
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const cell = grid[row][col];
        if (cell.unit && cell.unit.unitType === UnitType.WARRIOR) {
          const bonusCount = this.checkUnityBonus(grid, row, col);
          if (bonusCount > 0) {
            // 应用团结一致效果
            for (let i = 0; i < bonusCount; i++) {
              if (cell.unit) {
                cell.unit.unityBonusCount++;
              }
            }
          }
        }
      }
    }
  }

  /**
   * 重置所有兵种的团结一致效果
   */
  private resetAllUnityBonuses(grid: Cell[][]): void {
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const cell = grid[row][col];
        if (cell.unit) {
          cell.unit.unityBonusCount = 0;
        }
      }
    }
  }

  /**
   * 获取指定格子的所有相邻格子坐标
   */
  private getNeighbors(grid: Cell[][], row: number, col: number): [number, number][] {
    const neighbors: [number, number][] = [];
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],           [0, 1],
      [1, -1],  [1, 0],  [1, 1]
    ];

    for (const [dr, dc] of directions) {
      const newRow = row + dr;
      const newCol = col + dc;

      if (newRow >= 0 && newRow < grid.length && newCol >= 0 && newCol < grid[row].length) {
        neighbors.push([newRow, newCol]);
      }
    }

    return neighbors;
  }
}
