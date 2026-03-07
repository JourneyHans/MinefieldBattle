import { create } from 'zustand';
import { GameState, Difficulty, Card, Cell, RevealResult, DeployResult, BattleSettlementResult } from '../types';
import { GameStateCore } from '../game/core/GameState';

/**
 * 游戏状态管理接口
 */
interface GameStore {
  // 游戏状态
  gameState: GameState | null;
  gameInstance: GameStateCore | null;

  // 操作方法
  initGame: (difficulty: Difficulty) => void;
  revealCell: (row: number, col: number) => RevealResult;
  deployCard: (cardIndex: number, row: number, col: number) => DeployResult;
  battleMonster: (row: number, col: number) => BattleSettlementResult;
  endTurn: () => void;
  confirmTask: () => boolean;

  // 获取方法
  getGameState: () => GameState | null;
  getGameStatus: () => GameState['status'] | null;
  getGrid: () => Cell[][] | null;
  getHand: () => Card[];
  getTaskCell: () => GameState['taskCell'];
}

/**
 * 游戏状态管理Store
 */
export const useGameStore = create<GameStore>((set, get) => ({
  // 初始状态
  gameState: null,
  gameInstance: null,

  /**
   * 初始化游戏
   */
  initGame: (difficulty: Difficulty) => {
    const gameInstance = new GameStateCore(difficulty);
    const gameState = gameInstance.getState();

    set({ gameInstance, gameState });
  },

  /**
   * 揭示格子
   */
  revealCell: (row: number, col: number) => {
    const { gameInstance } = get();
    if (!gameInstance) {
      return { success: false };
    }

    const result = gameInstance.revealCell(row, col);

    // 更新游戏状态
    set({ gameState: gameInstance.getState() });

    return result;
  },

  /**
   * 部署卡牌
   */
  deployCard: (cardIndex: number, row: number, col: number) => {
    const { gameInstance } = get();
    if (!gameInstance) {
      return { success: false, message: '游戏未初始化' };
    }

    const result = gameInstance.deployCard(cardIndex, row, col);

    // 更新游戏状态
    set({ gameState: gameInstance.getState() });

    return result;
  },

  /**
   * 战斗怪物
   */
  battleMonster: (row: number, col: number) => {
    const { gameInstance } = get();
    if (!gameInstance) {
      return {
        result: 'PENDING' as any,
        playerPower: 0,
        monsterPower: 0,
        damage: 0,
      };
    }

    const result = gameInstance.battleMonster(row, col);

    // 更新游戏状态
    set({ gameState: gameInstance.getState() });

    return result;
  },

  /**
   * 结束回合
   */
  endTurn: () => {
    const { gameInstance } = get();
    if (!gameInstance) {
      return;
    }

    gameInstance.endTurn();

    // 更新游戏状态
    set({ gameState: gameInstance.getState() });
  },

  /**
   * 确认任务
   */
  confirmTask: () => {
    const { gameInstance } = get();
    if (!gameInstance) {
      return false;
    }

    const success = gameInstance.confirmTask();

    // 更新游戏状态
    set({ gameState: gameInstance.getState() });

    return success;
  },

  /**
   * 获取游戏状态
   */
  getGameState: () => {
    return get().gameState;
  },

  /**
   * 获取游戏状态信息
   */
  getGameStatus: () => {
    return get().gameState?.status || null;
  },

  /**
   * 获取地图
   */
  getGrid: () => {
    return get().gameState?.grid || null;
  },

  /**
   * 获取手牌
   */
  getHand: () => {
    return get().gameState?.hand || [];
  },

  /**
   * 获取任务格子
   */
  getTaskCell: () => {
    return get().gameState?.taskCell || null;
  },
}));
