#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀延迟诊断工具
找出响应慢的根本原因
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def benchmark_imports():
    """测试导入耗时"""
    print("=" * 60)
    print("📦 测试模块导入耗时")
    print("=" * 60)
    
    modules = [
        "asyncio",
        "scripts.fast_response_layer",
        "scripts.orchestrator_v2",
    ]
    
    for module in modules:
        start = time.time()
        __import__(module)
        elapsed = (time.time() - start) * 1000
        print(f"  {module:<40} {elapsed:>8.1f}ms")

def benchmark_layer0():
    """测试 Layer 0 匹配速度"""
    print("\n" + "=" * 60)
    print("⚡ 测试 Layer 0 匹配速度")
    print("=" * 60)
    
    from scripts.fast_response_layer import fast_respond
    
    test_cases = ["你好", "在吗", "谢谢", "再见", "几点了"]
    
    for text in test_cases:
        # 预热
        fast_respond(text)
        
        # 测试 100 次
        start = time.time()
        for _ in range(100):
            fast_respond(text)
        elapsed = (time.time() - start) * 1000 / 100
        print(f"  '{text}' 平均耗时：{elapsed:.3f}ms")

def benchmark_intent_parse():
    """测试意图识别速度"""
    print("\n" + "=" * 60)
    print("🧠 测试意图识别速度")
    print("=" * 60)
    
    from scripts.orchestrator_v2 import parse_intent
    
    test_cases = [
        "你好",
        "帮我写个文案",
        "搜索一下新闻",
        "帮我写个小红书文案，配张自拍，然后发布",
    ]
    
    for text in test_cases:
        start = time.time()
        for _ in range(100):
            parse_intent(text)
        elapsed = (time.time() - start) * 1000 / 100
        print(f"  '{text[:30]:<30}' 平均耗时：{elapsed:.3f}ms")

def benchmark_full_pipeline():
    """测试完整流程"""
    print("\n" + "=" * 60)
    print("🚀 测试完整流程 (端到端)")
    print("=" * 60)
    
    import asyncio
    from scripts.orchestrator_v2 import get_orchestrator
    
    orch = get_orchestrator()
    
    test_cases = {
        "简单问候": "你好",
        "简单任务": "帮我写个文案",
        "复杂任务": "帮我写个小红书文案，配张自拍，然后发布",
    }
    
    async def run_tests():
        for name, text in test_cases.items():
            # 预热
            await orch.execute(text)
            
            # 测试 10 次
            start = time.time()
            for _ in range(10):
                result = await orch.execute(text)
            elapsed = (time.time() - start) * 1000 / 10
            
            print(f"  {name:<15} 平均耗时：{elapsed:>8.1f}ms (Layer: {result.fast_response_layer})")
    
    asyncio.run(run_tests())

def check_bottlenecks():
    """分析瓶颈"""
    print("\n" + "=" * 60)
    print("🔍 性能瓶颈分析")
    print("=" * 60)
    
    bottlenecks = []
    
    # 检查导入时间
    start = time.time()
    import scripts.orchestrator_v2
    import_time = (time.time() - start) * 1000
    if import_time > 100:
        bottlenecks.append(f"⚠️  导入时间过长：{import_time:.0f}ms (建议优化到<50ms)")
    else:
        print(f"✅ 导入时间：{import_time:.0f}ms")
    
    # 检查快速响应层
    from scripts.fast_response_layer import LAYER0_RULES
    rule_count = len(LAYER0_RULES)
    if rule_count < 50:
        bottlenecks.append(f"⚠️  Layer 0 规则较少：{rule_count}条 (建议增加到 100+ 条)")
    else:
        print(f"✅ Layer 0 规则数：{rule_count}条")
    
    # 检查缓存
    from scripts.fast_response_layer import response_cache
    stats = response_cache.stats()
    if stats['capacity'] < 1000:
        bottlenecks.append(f"⚠️  缓存容量较小：{stats['capacity']} (建议增加到 1000+)")
    else:
        print(f"✅ 缓存容量：{stats['capacity']}")
    
    # 显示瓶颈
    if bottlenecks:
        print("\n🔴 发现的瓶颈:")
        for b in bottlenecks:
            print(f"  {b}")
    else:
        print("\n🎉 未发现明显瓶颈")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔬 灵犀性能诊断工具 v2.0")
    print("=" * 60 + "\n")
    
    benchmark_imports()
    benchmark_layer0()
    benchmark_intent_parse()
    benchmark_full_pipeline()
    check_bottlenecks()
    
    print("\n" + "=" * 60)
    print("📊 诊断完成")
    print("=" * 60)
