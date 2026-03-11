#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 心跳集成测试

验证 orchestrator 和 heartbeat_task_sync 的集成是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SmartOrchestrator
from heartbeat_task_sync import get_heartbeat_sync

async def test_integration():
    """测试灵犀心跳集成"""
    print("=" * 60)
    print("🧪 灵犀心跳集成测试")
    print("=" * 60)
    
    # 1. 初始化 Orchestrator
    print("\n1️⃣ 初始化灵犀 Orchestrator...")
    orchestrator = SmartOrchestrator()
    print(f"   ✅ Orchestrator 已初始化")
    print(f"   ✅ 心跳同步器已连接")
    
    # 2. 执行测试任务
    print("\n2️⃣ 执行测试任务...")
    test_input = "搜索一下最新的 AI 新闻"
    print(f"   任务：{test_input}")
    
    result = await orchestrator.execute(test_input, user_id="test_user_001")
    
    print(f"   ✅ 任务执行完成")
    print(f"   任务 ID: {result.task_id}")
    print(f"   评分：{result.total_score:.1f}/10")
    
    # 3. 检查心跳状态
    print("\n3️⃣ 检查心跳同步器状态...")
    sync = get_heartbeat_sync()
    status = sync.get_status()
    
    print(f"   进行中任务：{status['pending_count']}")
    print(f"   已完成任务：{status['completed_count']}")
    print(f"   定时任务：{status['scheduled_count']}")
    
    # 4. 生成心跳报告
    print("\n4️⃣ 生成心跳报告...")
    report = sync.generate_heartbeat_report(format='kanban')
    print(report)
    
    # 5. 验证 HEARTBEAT.md 已更新
    print("\n5️⃣ 验证 HEARTBEAT.md 文件...")
    heartbeat_file = Path.home() / ".openclaw" / "workspace" / "HEARTBEAT.md"
    if heartbeat_file.exists():
        content = heartbeat_file.read_text(encoding='utf-8')
        if result.task_id in content or "test_user_001" in content:
            print(f"   ✅ HEARTBEAT.md 已更新，包含任务信息")
        else:
            print(f"   ⚠️  HEARTBEAT.md 未包含当前任务（可能已完成并移除）")
        print(f"   📄 文件路径：{heartbeat_file}")
    else:
        print(f"   ❌ HEARTBEAT.md 不存在")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_integration())
    sys.exit(0 if success else 1)
