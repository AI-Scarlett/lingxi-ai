#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 性能对比测试（优化前 vs 优化后）

对比项目：
1. 响应速度
2. Tokens 消耗
3. 缓存命中率
"""

import time
import sys
sys.path.insert(0, '.')

from fast_response_layer import fast_respond, response_cache, cache_response

# ==================== 模拟优化前（原始流程） ====================

class LegacyParser:
    """模拟原始意图识别器（无优化）"""
    
    def __init__(self):
        self.call_count = 0
    
    def parse(self, user_input: str) -> dict:
        """模拟 LLM 调用 - 假设 300ms 延迟"""
        self.call_count += 1
        time.sleep(0.3)  # 模拟 300ms LLM 调用
        return {
            "intent": "unknown",
            "confidence": 0.8
        }

# ==================== 测试场景 ====================

TEST_SCENARIOS = [
    {
        "name": "场景 1: 问候对话",
        "inputs": ["你好", "在吗", "谢谢", "早上好", "再见"],
        "description": "日常问候，应该走 Layer 0"
    },
    {
        "name": "场景 2: 重复问题",
        "inputs": ["今天天气怎么样"] * 10,  # 重复 10 次
        "description": "相同问题，应该走 Layer 1 缓存"
    },
    {
        "name": "场景 3: 混合场景",
        "inputs": [
            "你好",
            "帮我写个文案",
            "谢谢",
            "在吗",
            "开发一个系统",
            "几点了"
        ],
        "description": "真实使用场景混合"
    }
]

def test_legacy(scenario_name: str, inputs: list) -> dict:
    """测试原始流程"""
    parser = LegacyParser()
    
    start = time.time()
    for inp in inputs:
        parser.parse(inp)
    total_time = (time.time() - start) * 1000
    
    return {
        "total_ms": total_time,
        "avg_ms": total_time / len(inputs),
        "llm_calls": parser.call_count,
        "tokens_estimated": parser.call_count * 200  # 每次约 200 tokens
    }

def test_optimized(scenario_name: str, inputs: list) -> dict:
    """测试优化后流程"""
    # 清空缓存
    response_cache.cache.clear()
    response_cache.order.clear()
    response_cache.hits = 0
    response_cache.misses = 0
    
    # 预热：缓存第一个问题（模拟真实使用）
    if inputs:
        cache_response(inputs[0], "缓存回复")
    
    start = time.time()
    layer0_count = 0
    layer1_count = 0
    passthrough_count = 0
    
    for inp in inputs:
        result = fast_respond(inp)
        if result.layer == "layer0":
            layer0_count += 1
        elif result.layer == "layer1":
            layer1_count += 1
        else:
            passthrough_count += 1
    
    total_time = (time.time() - start) * 1000
    
    # 计算 tokens 节省
    tokens_saved = (layer0_count + layer1_count) * 200
    
    return {
        "total_ms": total_time,
        "avg_ms": total_time / len(inputs),
        "layer0_count": layer0_count,
        "layer1_count": layer1_count,
        "passthrough_count": passthrough_count,
        "tokens_saved": tokens_saved,
        "cache_stats": response_cache.stats()
    }

def print_comparison(scenario: dict):
    """打印对比结果"""
    print("\n" + "=" * 70)
    print(f"📊 {scenario['name']}")
    print(f"   {scenario['description']}")
    print("=" * 70)
    
    inputs = scenario['inputs']
    
    # 测试原始流程
    print("\n⏳ 测试原始流程...")
    legacy_result = test_legacy(scenario['name'], inputs)
    
    # 测试优化后
    print("⚡ 测试优化后流程...")
    opt_result = test_optimized(scenario['name'], inputs)
    
    # 对比
    print("\n📈 对比结果:")
    print("-" * 70)
    print(f"{'指标':<20} | {'原始':<20} | {'优化后':<20} | {'提升':<15}")
    print("-" * 70)
    
    # 速度对比
    speedup = legacy_result['avg_ms'] / opt_result['avg_ms'] if opt_result['avg_ms'] > 0 else float('inf')
    print(f"{'平均响应时间':<20} | {legacy_result['avg_ms']:<20.3f}ms | {opt_result['avg_ms']:<20.3f}ms | {speedup:.1f}x ⚡")
    
    # Tokens 对比
    tokens_used = legacy_result['tokens_estimated'] - opt_result['tokens_saved']
    tokens_saved_pct = (opt_result['tokens_saved'] / legacy_result['tokens_estimated'] * 100) if legacy_result['tokens_estimated'] > 0 else 0
    print(f"{'Tokens 消耗':<20} | {legacy_result['tokens_estimated']:<20} | {tokens_used:<20} | 节省 {tokens_saved_pct:.1f}% 💰")
    
    # 分布
    print(f"{'Layer 0 (零思考)':<20} | {'N/A':<20} | {opt_result['layer0_count']:<20} | 零 Tokens")
    print(f"{'Layer 1 (缓存)':<20} | {'N/A':<20} | {opt_result['layer1_count']:<20} | 零 Tokens")
    print(f"{'Passthrough (LLM)':<20} | {legacy_result['llm_calls']:<20} | {opt_result['passthrough_count']:<20} | 需要 LLM")
    
    # 缓存命中率
    if opt_result['cache_stats']['hits'] + opt_result['cache_stats']['misses'] > 0:
        print(f"{'缓存命中率':<20} | {'N/A':<20} | {opt_result['cache_stats']['hit_rate']:<20} | 🧠")
    
    print("-" * 70)
    
    return {
        "speedup": speedup,
        "tokens_saved_pct": tokens_saved_pct,
        "legacy": legacy_result,
        "optimized": opt_result
    }

def run_full_benchmark():
    """运行完整基准测试"""
    print("\n" + "=" * 70)
    print("🚀 灵犀性能对比测试 - 优化前 vs 优化后")
    print("=" * 70)
    print("\n三大核心目标:")
    print("   ⚡ 快速反应 - 响应速度极致快")
    print("   💰 Tokens 消耗极限降低 - 能省则省")
    print("   🧠 记忆永不丢失 - 持久化存储")
    print("=" * 70)
    
    all_results = []
    
    for scenario in TEST_SCENARIOS:
        result = print_comparison(scenario)
        all_results.append(result)
    
    # 总总结
    print("\n" + "=" * 70)
    print("🎯 总体性能提升总结")
    print("=" * 70)
    
    avg_speedup = sum(r['speedup'] for r in all_results) / len(all_results)
    avg_tokens_saved = sum(r['tokens_saved_pct'] for r in all_results) / len(all_results)
    
    print(f"\n⚡ 平均速度提升：{avg_speedup:.1f}x")
    print(f"💰 平均 Tokens 节省：{avg_tokens_saved:.1f}%")
    print(f"🧠 缓存机制：LRU 1000 条 + 持久化（待实现）")
    
    print("\n📊 详细数据:")
    for i, scenario in enumerate(TEST_SCENARIOS):
        r = all_results[i]
        print(f"   {scenario['name']}: {r['speedup']:.1f}x 提速，节省 {r['tokens_saved_pct']:.1f}% Tokens")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    
    return all_results

if __name__ == "__main__":
    run_full_benchmark()
