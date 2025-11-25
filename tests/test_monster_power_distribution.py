# -*- coding: utf-8 -*-
"""
怪物战力分布测试
测试怪物战力生成函数的分布是否符合预期
"""
import random
import sys
import os

# 添加项目路径以便导入（但测试本身是独立的）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'demo'))


# 复制权重表（与项目解耦）
MONSTER_POWER_WEIGHTS = {
    1: 12,
    2: 11,
    3: 11,
    4: 10,
    5: 9,
    6: 8,
    7: 8,
    8: 7,
    9: 7,
    10: 6,
    11: 5,
    12: 5,
    13: 4,
    14: 4,
    15: 3,
    16: 3,
    17: 2,
    18: 2,
    19: 2,
    20: 2,
    21: 1,
    22: 1,
    23: 1,
    24: 1,
    25: 1,
    26: 1,
    27: 1,
    28: 1,
    29: 1,
    30: 1,
    31: 1,
    32: 1,
}

MONSTER_POWER_TOTAL_WEIGHT = sum(MONSTER_POWER_WEIGHTS.values())


def weighted_random_monster_power():
    """
    使用预定义权重表生成怪物战力（1-32）
    低数值拥有更高权重，使整体战力分布更低
    返回: 1-32 的怪物战力值
    """
    target = random.randint(1, MONSTER_POWER_TOTAL_WEIGHT)
    cumulative = 0
    for power, weight in MONSTER_POWER_WEIGHTS.items():
        cumulative += weight
        if target <= cumulative:
            return power
    
    # 理论上不会到这里，兜底返回最低权重对应值
    return 1


def test_monster_power_distribution(sample_size=10000):
    """
    测试怪物战力分布
    
    :param sample_size: 采样数量，默认10000
    """
    print("=" * 80)
    print(f"怪物战力分布测试 (采样数量: {sample_size:,})")
    print("=" * 80)
    
    # 统计每个战力值的出现次数
    power_counts = {power: 0 for power in range(1, 33)}
    
    # 生成样本
    print(f"\n正在生成 {sample_size:,} 个样本...")
    for _ in range(sample_size):
        power = weighted_random_monster_power()
        power_counts[power] += 1
    
    # 计算统计信息
    total_weight = MONSTER_POWER_TOTAL_WEIGHT
    power_values = []
    
    print("\n" + "=" * 80)
    print("战力分布统计")
    print("=" * 80)
    print(f"{'战力':<6} {'出现次数':<12} {'实际概率':<12} {'理论概率':<12} {'权重':<8} {'偏差':<10}")
    print("-" * 80)
    
    for power in range(1, 33):
        count = power_counts[power]
        actual_prob = count / sample_size * 100
        theoretical_weight = MONSTER_POWER_WEIGHTS[power]
        theoretical_prob = theoretical_weight / total_weight * 100
        deviation = actual_prob - theoretical_prob
        
        power_values.extend([power] * count)  # 用于计算统计量
        
        print(f"{power:<6} {count:<12,} {actual_prob:>10.2f}% {theoretical_prob:>10.2f}% "
              f"{theoretical_weight:<8} {deviation:>9.2f}%")
    
    # 计算统计量
    mean_power = sum(power_values) / len(power_values)
    sorted_powers = sorted(power_values)
    median_power = sorted_powers[len(sorted_powers) // 2]
    
    # 计算分位数
    q25 = sorted_powers[len(sorted_powers) // 4]
    q75 = sorted_powers[len(sorted_powers) * 3 // 4]
    
    # 计算标准差
    variance = sum((p - mean_power) ** 2 for p in power_values) / len(power_values)
    std_dev = variance ** 0.5
    
    # 计算最小值、最大值
    min_power = min(power_values)
    max_power = max(power_values)
    
    print("\n" + "=" * 80)
    print("统计摘要")
    print("=" * 80)
    print(f"平均值 (Mean):        {mean_power:.2f}")
    print(f"中位数 (Median):      {median_power:.2f}")
    print(f"25%分位数 (Q25):     {q25:.2f}")
    print(f"75%分位数 (Q75):     {q75:.2f}")
    print(f"标准差 (Std Dev):     {std_dev:.2f}")
    print(f"最小值 (Min):         {min_power}")
    print(f"最大值 (Max):         {max_power}")
    print(f"范围 (Range):         {max_power - min_power}")
    
    # 按区间统计
    print("\n" + "=" * 80)
    print("区间分布")
    print("=" * 80)
    ranges = [
        (1, 5, "1-5 (低战力)"),
        (6, 10, "6-10 (中低战力)"),
        (11, 15, "11-15 (中等战力)"),
        (16, 20, "16-20 (中高战力)"),
        (21, 25, "21-25 (高战力)"),
        (26, 32, "26-32 (极高战力)"),
    ]
    
    for min_val, max_val, label in ranges:
        count = sum(power_counts[p] for p in range(min_val, max_val + 1))
        percentage = count / sample_size * 100
        print(f"{label:<20} {count:>8,} ({percentage:>6.2f}%)")
    
    # 验证权重总和
    print("\n" + "=" * 80)
    print("权重验证")
    print("=" * 80)
    print(f"总权重: {total_weight}")
    print(f"权重总和验证: {sum(MONSTER_POWER_WEIGHTS.values()) == total_weight}")
    
    # 计算期望值（理论平均值）
    theoretical_mean = sum(power * weight for power, weight in MONSTER_POWER_WEIGHTS.items()) / total_weight
    print(f"理论期望值: {theoretical_mean:.2f}")
    print(f"实际平均值: {mean_power:.2f}")
    print(f"偏差: {abs(mean_power - theoretical_mean):.2f}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return {
        'mean': mean_power,
        'median': median_power,
        'std_dev': std_dev,
        'min': min_power,
        'max': max_power,
        'power_counts': power_counts,
    }


if __name__ == "__main__":
    # 设置随机种子以便结果可复现（可选）
    # random.seed(42)
    
    # 运行测试
    result = test_monster_power_distribution(sample_size=10000)
    
    # 可以在这里添加断言来验证分布是否符合预期
    # 例如：平均值应该小于某个值
    assert result['mean'] < 12.0, f"平均值 {result['mean']:.2f} 过高，应该小于12.0"
    print(f"\n[PASS] 断言通过：平均值 {result['mean']:.2f} < 12.0")

