#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 性能诊断工具

用于快速定位响应慢的问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.orchestrator_v2 import get_orchestrator
import time
import asyncio

def diagnose(user_input: str):
    """诊断用户输入的处理流程"""
    
    print("=" * 60)
    print("🔍 灵犀性能诊断")
    print("=" * 60)
    print(f"输入：{user_input}")
    print()
    
    # 1. 检查 Layer 0 快速响应
    print("1️⃣ 检查 Layer 0 快速响应...")
    from scripts.fast_response_layer_v2 import fast_respond
    
    start = time.time()
    result = fast_respond(user_input)
    elapsed = (time.time() - start) * 1000
    
    if result.response:
        print(f"   ✅ Layer 0 命中！耗时：{elapsed:.2f}ms")
        print(f"   层级：{result.layer}")
        print(f"   响应：{result.response[:100]}...")
    else:
        print(f"   ❌ Layer 0 未命中，将进入完整流程")
    
    print()
    
    # 2. 检查渠道路由
    print("2️⃣ 检查渠道路由...")
    from scripts.channel_router import get_channel_orchestrator
    
    start = time.time()
    orch = get_channel_orchestrator(channel="qqbot", user_id="test_user")
    elapsed = (time.time() - start) * 1000
    
    print(f"   ✅ 渠道路由耗时：{elapsed:.2f}ms")
    print(f"   配置：max_concurrent={orch.max_concurrent}")
    print(f"   审核：{orch.enable_review}")
    print(f"   审计：{orch.enable_audit}")
    print()
    
    # 3. 模拟完整执行
    print("3️⃣ 模拟完整执行流程...")
    
    async def test_execute():
        start = time.time()
        
        # 意图识别
        from scripts.orchestrator_v2 import parse_intent
        intent_start = time.time()
        intent = parse_intent(user_input)
        intent_elapsed = (time.time() - intent_start) * 1000
        print(f"   - 意图识别：{intent_elapsed:.2f}ms")
        
        # 任务拆解
        from scripts.orchestrator_v2 import decompose_task
        decompose_start = time.time()
        subtasks = decompose_task(user_input, intent)
        decompose_elapsed = (time.time() - decompose_start) * 1000
        print(f"   - 任务拆解：{decompose_elapsed:.2f}ms ({len(subtasks)}个子任务)")
        
        # 执行子任务（模拟）
        exec_start = time.time()
        for st in subtasks:
            # 模拟执行耗时
            await asyncio.sleep(0.1)
        exec_elapsed = (time.time() - exec_start) * 1000
        print(f"   - 子任务执行：{exec_elapsed:.2f}ms (模拟)")
        
        total = (time.time() - start) * 1000
        print(f"   📊 预估总耗时：{total:.2f}ms")
        
        return total
    
    total_time = asyncio.run(test_execute())
    
    print()
    print("=" * 60)
    print("💡 优化建议")
    print("=" * 60)
    
    if result.response:
        print("✅ 当前输入会走 Layer 0 快速响应，无需优化")
    else:
        print("⚠️ 当前输入会走完整流程，建议：")
        print("   1. 添加 Layer 0 快速响应规则")
        print("   2. 或优化子任务执行逻辑")
    
    if total_time > 1000:
        print("⚠️ 预估耗时超过 1 秒，用户体验较差")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 diagnose.py <用户输入>")
        print("示例：python3 diagnose.py '你好'")
        sys.exit(1)
    
    user_input = " ".join(sys.argv[1:])
    diagnose(user_input)
