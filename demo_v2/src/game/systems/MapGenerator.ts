import { Cell, Difficulty } from '../../types';
import { NumberCellEntity, MonsterCellEntity, TaskCellEntity } from '../entities';
import { getMapConfig } from '../../config/difficultyConfig';
import { getRandomTaskType } from '../../config/taskConfig';

/**
 * 地图生成器
 */
export class MapGenerator {
  private width: number;
  private height: number;
  private mineCount: number;

  constructor(difficulty: Difficulty) {
    const config = getMapConfig(difficulty);
    this.width = config.width;
    this.height = config.height;
    this.mineCount = config.mineCount;
  }

  /**
   * 生成游戏地图
   */
  generate(): Cell[][] {
    // 1. 创建空白地图
    const grid = this.createEmptyGrid();

    // 2. 随机放置怪物
    this.placeMonsters(grid);

    // 3. 随机放置任务
    this.placeTask(grid);

    // 4. 计算数字格子
    this.calculateNumbers(grid);

    return grid;
  }

  /**
   * 创建空白地图
   */
  private createEmptyGrid(): Cell[][] {
    const grid: Cell[][] = [];

    for (let row = 0; row < this.height; row++) {
      grid[row] = [];
      for (let col = 0; col < this.width; col++) {
        // 初始都创建数字格子，后续会替换为怪物或任务格子
        grid[row][col] = new NumberCellEntity(row, col, 0);
      }
    }

    return grid;
  }

  /**
   * 随机放置怪物
   */
  private placeMonsters(grid: Cell[][]): void {
    let placed = 0;
    const maxAttempts = this.mineCount * 10; // 防止无限循环
    let attempts = 0;

    while (placed < this.mineCount && attempts < maxAttempts) {
      const row = Math.floor(Math.random() * this.height);
      const col = Math.floor(Math.random() * this.width);

      // 确保该位置还没有怪物
      if (!(grid[row][col] instanceof MonsterCellEntity)) {
        grid[row][col] = new MonsterCellEntity(row, col);
        placed++;
      }

      attempts++;
    }

    if (placed < this.mineCount) {
      console.warn(`只放置了 ${placed}/${this.mineCount} 个怪物`);
    }
  }

  /**
   * 随机放置任务
   */
  private placeTask(grid: Cell[][]): void {
    let placed = false;
    let attempts = 0;
    const maxAttempts = 100;

    while (!placed && attempts < maxAttempts) {
      const row = Math.floor(Math.random() * this.height);
      const col = Math.floor(Math.random() * this.width);

      // 任务不能放在怪物格子上
      if (!(grid[row][col] instanceof MonsterCellEntity)) {
        const taskType = getRandomTaskType();
        grid[row][col] = new TaskCellEntity(row, col, taskType);
        placed = true;
      }

      attempts++;
    }

    if (!placed) {
      console.warn('无法放置任务格子');
    }
  }

  /**
   * 计算数字格子的数字（周围怪物数量）
   */
  private calculateNumbers(grid: Cell[][]): void {
    for (let row = 0; row < this.height; row++) {
      for (let col = 0; col < this.width; col++) {
        const cell = grid[row][col];

        // 只计算数字格子
        if (cell instanceof NumberCellEntity) {
          const monsterCount = this.countAdjacentMonsters(grid, row, col);
          (cell as NumberCellEntity).number = monsterCount;
        }
      }
    }
  }

  /**
   * 计算指定格子周围的怪物数量
   */
  private countAdjacentMonsters(grid: Cell[][], row: number, col: number): number {
    let count = 0;
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],           [0, 1],
      [1, -1],  [1, 0],  [1, 1]
    ];

    for (const [dr, dc] of directions) {
      const newRow = row + dr;
      const newCol = col + dc;

      if (newRow >= 0 && newRow < this.height && newCol >= 0 && newCol < this.width) {
        if (grid[newRow][newCol] instanceof MonsterCellEntity) {
          count++;
        }
      }
    }

    return count;
  }

  /**
   * 获取指定格子的所有相邻格子坐标
   */
  getNeighbors(row: number, col: number): [number, number][] {
    const neighbors: [number, number][] = [];
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],           [0, 1],
      [1, -1],  [1, 0],  [1, 1]
    ];

    for (const [dr, dc] of directions) {
      const newRow = row + dr;
      const newCol = col + dc;

      if (newRow >= 0 && newRow < this.height && newCol >= 0 && newCol < this.width) {
        neighbors.push([newRow, newCol]);
      }
    }

    return neighbors;
  }
}
