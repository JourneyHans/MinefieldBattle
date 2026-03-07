import { Unit, UnitType } from '../../types';
import { UNIT_CONFIG, UNITY_CONFIG } from '../../config/gameConfig';

/**
 * 兵种单位
 */
export class UnitEntity implements Unit {
  readonly unitType: UnitType;
  readonly name: string;
  readonly power: number;
  readonly color: number;
  unityBonusCount: number;   // 团结一致效果叠加次数

  constructor(unitType: UnitType) {
    const config = UNIT_CONFIG[unitType];
    this.unitType = unitType;
    this.name = config.name;
    this.power = config.power;
    this.color = config.color;
    this.unityBonusCount = 0;
  }

  // 获取实际战力（考虑团结一致效果）
  getEffectivePower(): number {
    if (this.unityBonusCount === 0) {
      return this.power;
    } else if (this.unityBonusCount === 1) {
      return this.power * UNITY_CONFIG.BONUS_MULTIPLIER;  // 2倍
    } else {
      return this.power * UNITY_CONFIG.MAX_MULTIPLIER;    // 4倍
    }
  }

  // 增加团结一致效果
  addUnityBonus(): void {
    if (this.unityBonusCount < 2) {
      this.unityBonusCount++;
    }
  }

  // 重置团结一致效果
  resetUnityBonus(): void {
    this.unityBonusCount = 0;
  }

  // 检查是否是战士（用于团结一致效果）
  isWarrior(): boolean {
    return this.unitType === UnitType.WARRIOR;
  }

  // 克隆兵种单位
  clone(): UnitEntity {
    const cloned = new UnitEntity(this.unitType);
    cloned.unityBonusCount = this.unityBonusCount;
    return cloned;
  }

  // 转换为DTO
  toDTO(): Unit {
    return {
      unitType: this.unitType,
      name: this.name,
      power: this.power,
      color: this.color,
      unityBonusCount: this.unityBonusCount,
    };
  }

  // 创建兵种单位
  static create(unitType: UnitType): UnitEntity {
    return new UnitEntity(unitType);
  }

  // 从DTO创建兵种单位
  static fromDTO(dto: Unit): UnitEntity {
    const unit = new UnitEntity(dto.unitType);
    unit.unityBonusCount = dto.unityBonusCount;
    return unit;
  }
}
