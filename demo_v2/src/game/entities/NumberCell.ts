import { CellEntity } from './Cell';
import { CellType, NumberCell as NumberCellType } from '../../types';

/**
 * 数字格子 - 显示周围怪物数量
 */
export class NumberCellEntity extends CellEntity implements NumberCellType {
  readonly type = CellType.NUMBER;
  number: number;  // 周围怪物数量

  constructor(row: number, col: number, number: number) {
    super(row, col, CellType.NUMBER);
    this.number = number;
  }

  // 检查是否可以部署兵种
  canDeploy(unitPower: number): boolean {
    if (!this.isRevealed()) {
      return false;
    }

    if (this.number === 0) {
      return false;  // 数字为0的格子不能部署
    }

    return unitPower >= this.number;
  }

  // 获取部署后的实际战力
  getDeployedPower(unitPower: number): number {
    if (!this.canDeploy(unitPower)) {
      return 0;
    }

    // 如果卡牌战力大于格子数字，实际战力等于格子数字
    return Math.min(unitPower, this.number);
  }

  // 克隆数字格子
  clone(): NumberCellEntity {
    const cloned = new NumberCellEntity(this.row, this.col, this.number);
    cloned.state = this.state;
    cloned.unit = this.unit ? { ...this.unit } : null;
    return cloned;
  }

  // 转换为DTO
  toDTO(): NumberCellType {
    return {
      row: this.row,
      col: this.col,
      type: this.type,
      state: this.state,
      number: this.number,
      unit: this.unit,
    };
  }
}
