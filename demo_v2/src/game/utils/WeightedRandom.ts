/**
 * 加权随机工具函数
 */

/**
 * 加权随机选择
 * @param weights 权重对象，key为值，value为权重
 * @returns 随机选择的值
 */
export function weightedRandom(weights: Record<number, number>): number {
  const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
  let random = Math.random() * totalWeight;

  for (const [value, weight] of Object.entries(weights)) {
    random -= weight;
    if (random <= 0) {
      return parseInt(value, 10);
    }
  }

  // 兜底返回第一个值
  return parseInt(Object.keys(weights)[0], 10);
}

/**
 * 加权随机选择（字符串版本）
 * @param weights 权重对象，key为值，value为权重
 * @returns 随机选择的值
 */
export function weightedRandomString<T extends string>(weights: Record<T, number>): T {
  const entries = Object.entries(weights) as [T, number][];
  const totalWeight = entries.reduce((sum: number, [, weight]: [T, number]) => sum + weight, 0);
  let random = Math.random() * totalWeight;

  for (const [value, weight] of entries) {
    random -= weight;
    if (random <= 0) {
      return value;
    }
  }

  // 兜底返回第一个值
  return entries[0][0];
}

/**
 * 从数组中按权重随机选择
 * @param items 选项数组
 * @param weightFn 权重计算函数
 * @returns 随机选择的项
 */
export function weightedRandomChoice<T>(
  items: T[],
  weightFn: (item: T) => number
): T {
  if (items.length === 0) {
    throw new Error('Cannot choose from empty array');
  }

  const totalWeight = items.reduce((sum, item) => sum + weightFn(item), 0);
  let random = Math.random() * totalWeight;

  for (const item of items) {
    random -= weightFn(item);
    if (random <= 0) {
      return item;
    }
  }

  // 兜底返回第一项
  return items[0];
}

/**
 * 生成随机ID
 * @param prefix ID前缀
 * @returns 随机ID字符串
 */
export function generateId(prefix: string = ''): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 9);
  return prefix ? `${prefix}_${timestamp}_${random}` : `${timestamp}_${random}`;
}
