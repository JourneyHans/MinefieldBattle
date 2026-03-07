import { UnitType } from '../types';

/**
 * 游戏配置常量
 */

// 生命值配置
export const HEALTH_CONFIG = {
  INITIAL_HEALTH: 4,
  MAX_HEALTH: 10,
  DAMAGE_PER_DEFEAT: 1,
} as const;

// 卡牌配置
export const CARD_CONFIG = {
  DEAL_COUNT: 5,              // 每回合发牌数量
  MAX_HAND_SIZE: 10,          // 手牌上限
  MIN_DECK_SIZE: 20,          // 最小牌组数量
} as const;

// 兵种配置
export const UNIT_CONFIG: Record<UnitType, {
  name: string;
  power: number;
  color: number;
  description: string;
}> = {
  [UnitType.WARRIOR]: {
    name: '战士',
    power: 1,
    color: 0xFF6B6B,          // 红色
    description: '近战肉盾，血量高'
  },
  [UnitType.ARCHER]: {
    name: '弓箭手',
    power: 2,
    color: 0x4ECDC4,          // 青色
    description: '远程输出，攻击力中等'
  },
  [UnitType.MAGE]: {
    name: '法师',
    power: 3,
    color: 0x95E1D3,          // 浅青色
    description: '魔法攻击，攻击力高但血量低'
  },
  [UnitType.PALADIN]: {
    name: '圣骑士',
    power: 4,
    color: 0xF38181,          // 粉红色
    description: '治疗+防御，全能型职业'
  },
  [UnitType.ROGUE]: {
    name: '盗贼',
    power: 5,
    color: 0xAA96DA,          // 紫色
    description: '高暴击，闪避能力强'
  },
  [UnitType.DRUID]: {
    name: '德鲁伊',
    power: 6,
    color: 0xFCBAD3,          // 浅粉色
    description: '召唤+自然魔法，平衡型'
  },
  [UnitType.DRAGON_KNIGHT]: {
    name: '龙骑士',
    power: 7,
    color: 0xFFFFD2,          // 浅黄色
    description: '飞行单位，全属性优秀'
  },
  [UnitType.ARCH_MAGE]: {
    name: '大法师',
    power: 8,
    color: 0xA8E6CF,          // 绿色
    description: '终极魔法，范围攻击'
  },
};

// 团结一致效果配置
export const UNITY_CONFIG = {
  MIN_COUNT: 3,               // 触发团结一致的最少兵种数量
  BONUS_MULTIPLIER: 2,        // 每次翻倍的倍数
  MAX_MULTIPLIER: 4,          // 最大倍数（行+列）
} as const;

// 怪物战力配置
export const MONSTER_POWER_CONFIG = {
  MIN_POWER: 1,
  MAX_POWER: 32,
  WEIGHTS: {
    1: 12, 2: 11, 3: 11, 4: 10, 5: 9, 6: 8, 7: 8, 8: 7,
    9: 7, 10: 6, 11: 5, 12: 5, 13: 4, 14: 4, 15: 3, 16: 3,
    17: 2, 18: 2, 19: 2, 20: 2, 21: 1, 22: 1, 23: 1, 24: 1,
    25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1
  }
} as const;

// 卡牌发牌权重配置
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

// UI配置
export const UI_CONFIG = {
  CELL_SIZE: 60,
  CELL_PADDING: 6,
  CARD_WIDTH: 80,
  CARD_HEIGHT: 120,
  HAND_PADDING: 10,
  ANIMATION_DURATION: 300,    // 毫秒
} as const;

// 游戏性能配置
export const PERFORMANCE_CONFIG = {
  MAX_CACHE_SIZE: 100,        // 最大缓存对象数量
  ANIMATION_FPS: 60,          // 动画帧率
  RENDER_FPS: 60,             // 渲染帧率
} as const;
