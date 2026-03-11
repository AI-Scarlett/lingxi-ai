#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 演示任务执行

让老板看到真实的任务执行和 Dashboard 实时更新
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SmartOrchestrator

async def demo_task():
    """演示任务"""
    orch = SmartOrchestrator()
    
    print("=" * 60)
    print("🎯 灵犀任务执行演示")
    print("=" * 60)
    print()
    
    # 执行一个真实任务
    user_input = "帮我写一段关于春天的诗歌，100 字以内"
    print(f"📝 任务：{user_input}")
    print(f"👤 用户：boss_demo")
    print()
    
    result = await orch.execute(user_input, user_id='boss_demo')
    
    print()
    print("=" * 60)
    print(f"✅ 任务完成！")
    print(f"📊 任务 ID: {result.task_id}")
    print(f"⭐ 评分：{result.total_score:.1f}/10")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    asyncio.run(demo_task())
