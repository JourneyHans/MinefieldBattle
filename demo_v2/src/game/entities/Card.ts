import { Card as CardType, UnitType } from '../../types';
import { UNIT_CONFIG } from '../../config/gameConfig';
import { generateId } from '../utils/WeightedRandom';

/**
 * 卡牌
 */
export class CardEntity implements CardType {
  readonly id: string;
  readonly unitType: UnitType;
  readonly name: string;
  readonly power: number;
  readonly color: number;

  constructor(unitType: UnitType) {
    const config = UNIT_CONFIG[unitType];
    this.id = generateId('card');
    this.unitType = unitType;
    this.name = config.name;
    this.power = config.power;
    this.color = config.color;
  }

  // 检查卡牌是否可以部署到指定数字的格子
  canDeployTo(cellNumber: number): boolean {
    return this.power >= cellNumber;
  }

  // 获取部署后的实际战力
  getDeployedPower(cellNumber: number): number {
    if (!this.canDeployTo(cellNumber)) {
      return 0;
    }

    // 如果卡牌战力大于格子数字，实际战力等于格子数字
    return Math.min(this.power, cellNumber);
  }

  // 克隆卡牌
  clone(): CardEntity {
    return new CardEntity(this.unitType);
  }

  // 转换为DTO
  toDTO(): CardType {
    return {
      id: this.id,
      unitType: this.unitType,
      name: this.name,
      power: this.power,
      color: this.color,
    };
  }

  // 创建卡牌
  static create(unitType: UnitType): CardEntity {
    return new CardEntity(unitType);
  }

  // 从DTO创建卡牌
  static fromDTO(dto: CardType): CardEntity {
    return new CardEntity(dto.unitType);
  }
}
