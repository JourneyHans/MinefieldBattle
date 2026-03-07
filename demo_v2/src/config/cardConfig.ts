import { UnitType } from '../types';

/**
 * 卡牌配置
 */

// 卡牌发牌权重
export const CARD_DEAL_WEIGHTS: Record<UnitType, number> = {
  [UnitType.WARRIOR]: 5,
  [UnitType.ARCHER]: 5,
  [UnitType.MAGE]: 5,
  [UnitType.PALADIN]: 4,
  [UnitType.ROGUE]: 4,
  [UnitType.DRUID]: 3,
  [UnitType.DRAGON_KNIGHT]: 2,
  [UnitType.ARCH_MAGE]: 1,
};

// 卡牌稀有度
export enum CardRarity {
  COMMON = 'COMMON',
  UNCOMMON = 'UNCOMMON',
  RARE = 'RARE',
  EPIC = 'EPIC',
  LEGENDARY = 'LEGENDARY'
}

// 卡牌稀有度配置
export const CARD_RARITY_CONFIG: Record<UnitType, CardRarity> = {
  [UnitType.WARRIOR]: CardRarity.COMMON,
  [UnitType.ARCHER]: CardRarity.COMMON,
  [UnitType.MAGE]: CardRarity.COMMON,
  [UnitType.PALADIN]: CardRarity.UNCOMMON,
  [UnitType.ROGUE]: CardRarity.UNCOMMON,
  [UnitType.DRUID]: CardRarity.RARE,
  [UnitType.DRAGON_KNIGHT]: CardRarity.EPIC,
  [UnitType.ARCH_MAGE]: CardRarity.LEGENDARY,
};

// 稀有度颜色
export const RARITY_COLORS: Record<CardRarity, number> = {
  [CardRarity.COMMON]: 0xCCCCCC,
  [CardRarity.UNCOMMON]: 0x4ECDC4,
  [CardRarity.RARE]: 0x95E1D3,
  [CardRarity.EPIC]: 0xAA96DA,
  [CardRarity.LEGENDARY]: 0xFFD700,
};

// 卡牌背纹颜色
export const CARD_BACK_COLOR = 0x16213e;
export const CARD_BACK_BORDER = 0xe94560;

// 计算卡牌稀有度
export function getCardRarity(unitType: UnitType): CardRarity {
  return CARD_RARITY_CONFIG[unitType];
}

// 获取稀有度颜色
export function getRarityColor(rarity: CardRarity): number {
  return RARITY_COLORS[rarity];
}
