import { Cell, TaskType, CellState as CS } from '../../types';
import { TaskCellEntity, MonsterCellEntity } from '../entities';

// 辅助函数
const isRevealed = (cell: Cell): boolean => {
  return cell.state === CS.REVEALED || cell.state === CS.DEPLOYED;
};

/**
 * 任务验证系统
 */
export class TaskValidator {
  /**
   * 检查任务是否完成
   */
  validateTask(grid: Cell[][], taskCell: TaskCellEntity): boolean {
    switch (taskCell.taskType) {
      case TaskType.EXPLORE_SURROUNDING:
        return this.validateExploreSurrounding(grid, taskCell);
      case TaskType.DEFEAT_ALL_MONSTERS:
        return this.validateDefeatAllMonsters(grid);
      case TaskType.FIND_TASK:
        return this.validateFindTask(taskCell);
      default:
        return false;
    }
  }

  /**
   * 验证探查周边任务
   * 要求：任务格子周围的所有格子都已揭示
   */
  private validateExploreSurrounding(grid: Cell[][], taskCell: TaskCellEntity): boolean {
    const neighbors = this.getNeighbors(grid, taskCell.row, taskCell.col);

    // 检查所有相邻格子是否都已揭示
    for (const [row, col] of neighbors) {
      const cell = grid[row][col];
      if (!isRevealed(cell)) {
        return false;
      }
    }

    return true;
  }

  /**
   * 验证击败所有怪物任务
   * 要求：所有怪物都已战斗
   */
  private validateDefeatAllMonsters(grid: Cell[][]): boolean {
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const cell = grid[row][col];

        if (cell instanceof MonsterCellEntity) {
          // 如果有未战斗的怪物，任务未完成
          if (!cell.isBattled()) {
            return false;
          }
        }
      }
    }

    return true;
  }

  /**
   * 验证找到任务任务
   * 要求：任务格子已揭示
   */
  private validateFindTask(taskCell: TaskCellEntity): boolean {
    return taskCell.isRevealed();
  }

  /**
   * 更新任务状态
   */
  updateTaskStatus(grid: Cell[][], taskCell: TaskCellEntity): void {
    if (!taskCell.isCompleted()) {
      const completed = this.validateTask(grid, taskCell);
      if (completed) {
        taskCell.complete();
      }
    }
  }

  /**
   * 检查任务是否可以确认
   */
  canConfirmTask(grid: Cell[][], taskCell: TaskCellEntity): boolean {
    return taskCell.isCompleted() && !taskCell.isConfirmed();
  }

  /**
   * 确认任务
   */
  confirmTask(grid: Cell[][], taskCell: TaskCellEntity): boolean {
    if (this.canConfirmTask(grid, taskCell)) {
      taskCell.confirm();
      return true;
    }
    return false;
  }

  /**
   * 获取任务进度信息
   */
  getTaskProgress(grid: Cell[][], taskCell: TaskCellEntity): string {
    switch (taskCell.taskType) {
      case TaskType.EXPLORE_SURROUNDING:
        return this.getExploreSurroundingProgress(grid, taskCell);
      case TaskType.DEFEAT_ALL_MONSTERS:
        return this.getDefeatAllMonstersProgress(grid);
      case TaskType.FIND_TASK:
        return this.getFindTaskProgress(taskCell);
      default:
        return '未知任务';
    }
  }

  /**
   * 获取探查周边任务进度
   */
  private getExploreSurroundingProgress(grid: Cell[][], taskCell: TaskCellEntity): string {
    const neighbors = this.getNeighbors(grid, taskCell.row, taskCell.col);
    let revealedCount = 0;

    for (const [row, col] of neighbors) {
      const cell = grid[row][col];
      if (isRevealed(cell)) {
        revealedCount++;
      }
    }

    return `已揭示 ${revealedCount}/${neighbors.length} 个相邻格子`;
  }

  /**
   * 获取击败所有怪物任务进度
   */
  private getDefeatAllMonstersProgress(grid: Cell[][]): string {
    let totalMonsters = 0;
    let defeatedMonsters = 0;

    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const cell = grid[row][col];
        if (cell instanceof MonsterCellEntity) {
          totalMonsters++;
          if (cell.isBattled()) {
            defeatedMonsters++;
          }
        }
      }
    }

    return `已击败 ${defeatedMonsters}/${totalMonsters} 个怪物`;
  }

  /**
   * 获取找到任务任务进度
   */
  private getFindTaskProgress(taskCell: TaskCellEntity): string {
    return taskCell.isRevealed() ? '任务已找到' : '任务未找到';
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
