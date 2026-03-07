import { CellState, CellType, Unit } from '../../types';

/**
 * 格子基类
 */
export abstract class CellEntity {
  readonly row: number;
  readonly col: number;
  state: CellState;
  unit: Unit | null;
  readonly type: CellType;

  constructor(row: number, col: number, type: CellType) {
    this.row = row;
    this.col = col;
    this.type = type;
    this.state = CellState.HIDDEN;
    this.unit = null;
  }

  // 检查格子是否已揭示
  isRevealed(): boolean {
    return this.state === CellState.REVEALED || this.state === CellState.DEPLOYED;
  }

  // 检查格子是否已部署兵种
  isDeployed(): boolean {
    return this.state === CellState.DEPLOYED;
  }

  // 检查格子是否隐藏
  isHidden(): boolean {
    return this.state === CellState.HIDDEN;
  }

  // 揭示格子
  reveal(): void {
    this.state = CellState.REVEALED;
  }

  // 部署兵种
  deployUnit(unit: Unit): void {
    this.unit = unit;
    this.state = CellState.DEPLOYED;
  }

  // 移除兵种
  removeUnit(): void {
    this.unit = null;
    if (this.state === CellState.DEPLOYED) {
      this.state = CellState.REVEALED;
    }
  }

  // 获取相邻格子坐标
  getNeighbors(width: number, height: number): [number, number][] {
    const neighbors: [number, number][] = [];
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],           [0, 1],
      [1, -1],  [1, 0],  [1, 1]
    ];

    for (const [dr, dc] of directions) {
      const newRow = this.row + dr;
      const newCol = this.col + dc;

      if (newRow >= 0 && newRow < height && newCol >= 0 && newCol < width) {
        neighbors.push([newRow, newCol]);
      }
    }

    return neighbors;
  }

  // 克隆格子
  abstract clone(): CellEntity;
}
