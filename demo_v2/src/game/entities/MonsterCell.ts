import { CellEntity } from './Cell';
import { CellType, MonsterCell as MonsterCellType, BattleResult } from '../../types';
import { weightedRandom } from '../utils/WeightedRandom';
import { MONSTER_POWER_CONFIG } from '../../config/gameConfig';

/**
 * 怪物格子 - 封印的怪物
 */
export class MonsterCellEntity extends CellEntity implements MonsterCellType {
  readonly type = CellType.MONSTER;
  power: number;             // 怪物战力
  triggered: boolean;        // 是否已触发
  battled: boolean;          // 是否已战斗
  battleResult: BattleResult | null;

  constructor(row: number, col: number) {
    super(row, col, CellType.MONSTER);
    this.power = 0;
    this.triggered = false;
    this.battled = false;
    this.battleResult = BattleResult.PENDING;
  }

  // 触发怪物 - 生成随机战力
  trigger(): void {
    if (!this.triggered) {
      this.triggered = true;
      this.power = weightedRandom(MONSTER_POWER_CONFIG.WEIGHTS);
    }
  }

  // 检查是否已触发
  isTriggered(): boolean {
    return this.triggered;
  }

  // 检查是否已战斗
  isBattled(): boolean {
    return this.battled;
  }

  // 设置战斗结果
  setBattleResult(result: BattleResult): void {
    this.battleResult = result;
    this.battled = true;
  }

  // 检查是否可以战斗
  canBattle(): boolean {
    return this.triggered && !this.battled;
  }

  // 重置怪物状态
  reset(): void {
    this.triggered = false;
    this.battled = false;
    this.battleResult = BattleResult.PENDING;
    this.power = 0;
  }

  // 克隆怪物格子
  clone(): MonsterCellEntity {
    const cloned = new MonsterCellEntity(this.row, this.col);
    cloned.state = this.state;
    cloned.unit = this.unit ? { ...this.unit } : null;
    cloned.power = this.power;
    cloned.triggered = this.triggered;
    cloned.battled = this.battled;
    cloned.battleResult = this.battleResult;
    return cloned;
  }

  // 转换为DTO
  toDTO(): MonsterCellType {
    return {
      row: this.row,
      col: this.col,
      type: this.type,
      state: this.state,
      power: this.power,
      triggered: this.triggered,
      battled: this.battled,
      battleResult: this.battleResult,
      unit: this.unit,
    };
  }
}
