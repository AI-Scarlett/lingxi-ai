#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀数据看板 - 测试脚本
测试任务记录和实时更新功能
"""

import asyncio
import time
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import (
    record_task_start,
    record_task_stage,
    record_task_complete,
    record_task_error
)


async def test_task_flow():
    """测试完整任务流程"""
    print("=" * 60)
    print("🧪 灵犀看板 - 任务流程测试")
    print("=" * 60)
    print()
    
    task_id = f"test_{int(time.time())}"
    user_id = "test_user_001"
    channel = "feishu"
    user_input = "生成今天的 Hunter 每日商机报告"
    
    # 1. 任务开始
    print(f"📝 任务开始：{task_id}")
    await record_task_start(task_id, user_id, channel, user_input)
    await asyncio.sleep(1)
    
    # 2. 意图分析
    print("🔍 阶段：意图分析")
    await record_task_stage(task_id, "intent_analysis", {
        "intent_types": ["content_creation", "data_analysis"]
    })
    await asyncio.sleep(1)
    
    # 3. 任务拆解
    print("📦 阶段：任务拆解")
    await record_task_stage(task_id, "task_decomposition", {
        "subtask_count": 2
    })
    await asyncio.sleep(1)
    
    # 4. 执行中
    print("⚙️  阶段：执行中")
    await record_task_stage(task_id, "executing", {
        "subtasks": [
            {"role": "文案专家", "status": "completed"},
            {"role": "数据专家", "status": "completed"}
        ]
    })
    await asyncio.sleep(1)
    
    # 5. LLM 调用
    print("🤖 LLM 调用")
    await record_task_stage(task_id, "llm_call", {
        "llm_called": True,
        "llm_model": "qwen-plus",
        "llm_tokens_in": 150,
        "llm_tokens_out": 300,
        "llm_cost": 0.00045
    })
    await asyncio.sleep(1)
    
    # 6. 任务完成
    print("✅ 任务完成")
    await record_task_complete(task_id, {
        "response_time_ms": 50.5,
        "execution_time_ms": 1250.3,
        "final_output": "Hunter 报告已生成",
        "score": 9.5
    })
    
    print()
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print()
    print(f"📊 查看看板：http://localhost:8765")
    print(f"📋 任务 ID: {task_id}")
    print()


async def test_error_flow():
    """测试错误流程"""
    print("=" * 60)
    print("🧪 灵犀看板 - 错误流程测试")
    print("=" * 60)
    print()
    
    task_id = f"test_error_{int(time.time())}"
    user_id = "test_user_002"
    channel = "qqbot"
    user_input = "测试错误处理"
    
    # 1. 任务开始
    print(f"📝 任务开始：{task_id}")
    await record_task_start(task_id, user_id, channel, user_input)
    await asyncio.sleep(1)
    
    # 2. 执行中
    print("⚙️  阶段：执行中")
    await record_task_stage(task_id, "executing")
    await asyncio.sleep(1)
    
    # 3. 任务错误
    print("❌ 任务错误")
    await record_task_error(task_id, "TimeoutError", "LLM 调用超时", "Traceback...")
    
    print()
    print("=" * 60)
    print("✅ 错误测试完成！")
    print("=" * 60)
    print()
    print(f"📊 查看看板：http://localhost:8765")
    print(f"⚠️  错误面板会显示此任务")
    print()


if __name__ == "__main__":
    print()
    print("选择测试:")
    print("1. 完整任务流程测试")
    print("2. 错误流程测试")
    print("3. 全部测试")
    print()
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(test_task_flow())
    elif choice == "2":
        asyncio.run(test_error_flow())
    elif choice == "3":
        asyncio.run(test_task_flow())
        print()
        input("按回车继续错误测试...")
        print()
        asyncio.run(test_error_flow())
    else:
        print("❌ 无效选择")
