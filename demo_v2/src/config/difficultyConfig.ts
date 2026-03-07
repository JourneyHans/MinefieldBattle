import { Difficulty, MapConfig } from '../types';

/**
 * 难度配置
 */

export const DIFFICULTY_CONFIGS: Record<Difficulty, MapConfig & { name: string; description: string }> = {
  [Difficulty.BEGINNER]: {
    name: '初级',
    description: '适合新手的简单难度',
    width: 9,
    height: 9,
    mineCount: 10,
  },
  [Difficulty.INTERMEDIATE]: {
    name: '中级',
    description: '适合有经验玩家的中等难度',
    width: 16,
    height: 16,
    mineCount: 40,
  },
  [Difficulty.EXPERT]: {
    name: '高级',
    description: '适合高手的挑战难度',
    width: 16,
    height: 30,
    mineCount: 99,
  },
};

// 获取难度配置
export function getDifficultyConfig(difficulty: Difficulty): MapConfig & { name: string; description: string } {
  return DIFFICULTY_CONFIGS[difficulty];
}

// 获取地图配置
export function getMapConfig(difficulty: Difficulty): MapConfig {
  const config = DIFFICULTY_CONFIGS[difficulty];
  return {
    width: config.width,
    height: config.height,
    mineCount: config.mineCount,
  };
}
