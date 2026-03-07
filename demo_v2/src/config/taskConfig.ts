import { TaskType } from '../types';

/**
 * 任务配置
 */

export const TASK_CONFIG = {
  // 任务类型配置
  TASK_TYPES: [
    TaskType.EXPLORE_SURROUNDING,
    TaskType.DEFEAT_ALL_MONSTERS,
    TaskType.FIND_TASK,
  ],

  // 任务描述
  TASK_DESCRIPTIONS: {
    [TaskType.EXPLORE_SURROUNDING]: '探查周边：揭示任务格子周围的所有格子',
    [TaskType.DEFEAT_ALL_MONSTERS]: '击败所有怪物：消灭地图上的所有怪物',
    [TaskType.FIND_TASK]: '找到任务：揭示任务格子',
  },

  // 任务完成提示
  TASK_COMPLETION_MESSAGES: {
    [TaskType.EXPLORE_SURROUNDING]: '周边区域已探查完成！',
    [TaskType.DEFEAT_ALL_MONSTERS]: '所有怪物已被消灭！',
    [TaskType.FIND_TASK]: '任务目标已找到！',
  },
} as const;

// 获取任务描述
export function getTaskDescription(taskType: TaskType): string {
  return TASK_CONFIG.TASK_DESCRIPTIONS[taskType];
}

// 获取任务完成消息
export function getTaskCompletionMessage(taskType: TaskType): string {
  return TASK_CONFIG.TASK_COMPLETION_MESSAGES[taskType];
}

// 随机获取一个任务类型
export function getRandomTaskType(): TaskType {
  const taskTypes = TASK_CONFIG.TASK_TYPES;
  return taskTypes[Math.floor(Math.random() * taskTypes.length)];
}
