/**
 * 全局类型定义
 */

// 难度级别
export enum Difficulty {
  BEGINNER = 'BEGINNER',
  INTERMEDIATE = 'INTERMEDIATE',
  EXPERT = 'EXPERT'
}

// 格子状态
export enum CellState {
  HIDDEN = 'HIDDEN',       // 隐藏状态
  REVEALED = 'REVEALED',   // 已揭示状态
  DEPLOYED = 'DEPLOYED'    // 已部署兵种状态
}

// 格子类型
export enum CellType {
  NUMBER = 'NUMBER',       // 数字格子
  MONSTER = 'MONSTER',     // 怪物格子
  TASK = 'TASK'           // 任务格子
}

// 任务类型
export enum TaskType {
  EXPLORE_SURROUNDING = 'EXPLORE_SURROUNDING',  // 探查周边
  DEFEAT_ALL_MONSTERS = 'DEFEAT_ALL_MONSTERS',  // 击败所有怪物
  FIND_TASK = 'FIND_TASK'                       // 找到任务
}

// 兵种类型
export enum UnitType {
  WARRIOR = 'WARRIOR',       // 战士 (1)
  ARCHER = 'ARCHER',         // 弓箭手 (2)
  MAGE = 'MAGE',             // 法师 (3)
  PALADIN = 'PALADIN',       // 圣骑士 (4)
  ROGUE = 'ROGUE',           // 盗贼 (5)
  DRUID = 'DRUID',           // 德鲁伊 (6)
  DRAGON_KNIGHT = 'DRAGON_KNIGHT', // 龙骑士 (7)
  ARCH_MAGE = 'ARCH_MAGE'    // 大法师 (8)
}

// 战斗结果
export enum BattleResult {
  PENDING = 'PENDING',       // 待定
  VICTORY = 'VICTORY',       // 胜利
  DEFEAT = 'DEFEAT'          // 失败
}

// 游戏状态
export interface GameStatus {
  health: number;            // 生命值
  currentTurn: number;       // 当前回合数
  gameOver: boolean;         // 游戏结束标志
  gameWon: boolean;          // 游戏胜利标志
  difficulty: Difficulty;    // 难度级别
}

// 地图配置
export interface MapConfig {
  width: number;             // 地图宽度
  height: number;            // 地图高度
  mineCount: number;         // 怪物数量
}

// 格子接口
export interface Cell {
  row: number;
  col: number;
  state: CellState;
  type: CellType;
  unit: Unit | null;
}

// 数字格子
export interface NumberCell extends Cell {
  type: CellType.NUMBER;
  number: number;            // 周围怪物数量
}

// 怪物格子
export interface MonsterCell extends Cell {
  type: CellType.MONSTER;
  power: number;             // 怪物战力
  triggered: boolean;        // 是否已触发
  battled: boolean;          // 是否已战斗
  battleResult: BattleResult | null;
}

// 任务格子
export interface TaskCell extends Cell {
  type: CellType.TASK;
  taskType: TaskType;
  completed: boolean;        // 任务是否完成
  confirmed: boolean;        // 任务是否已确认
}

// 兵种单位
export interface Unit {
  unitType: UnitType;
  name: string;
  power: number;
  color: number;
  unityBonusCount: number;   // 团结一致效果叠加次数
}

// 卡牌
export interface Card {
  id: string;
  unitType: UnitType;
  name: string;
  power: number;
  color: number;
}

// 游戏状态
export interface GameState {
  status: GameStatus;
  grid: Cell[][];
  hand: Card[];
  maxHandSize: number;
  taskCell: TaskCell | null;
}

// 游戏设置
export interface GameSettings {
  soundEnabled: boolean;
  musicEnabled: boolean;
  effectsEnabled: boolean;
  autoSave: boolean;
  windowScale: number;
}

// 部署结果
export interface DeployResult {
  success: boolean;
  message?: string;
  cardUsed?: boolean;
}

// 揭示结果
export interface RevealResult {
  success: boolean;
  cellRevealed?: Cell;
  areaRevealed?: Cell[];
  monsterTriggered?: MonsterCell;
  taskRevealed?: TaskCell;
}

// 战斗结算结果
export interface BattleSettlementResult {
  result: BattleResult;
  playerPower: number;
  monsterPower: number;
  damage: number;
}
