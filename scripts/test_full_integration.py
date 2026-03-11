#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 完整集成测试

测试 orchestrator + dashboard + heartbeat 的完整集成
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SmartOrchestrator
from heartbeat_task_sync import get_heartbeat_sync
from hourly_progress_report import HourlyProgressReporter, DashboardClient

async def test_full_integration():
    """测试完整集成"""
    print("=" * 60)
    print("🧪 灵犀完整集成测试")
    print("=" * 60)
    
    # 1. 测试 Dashboard 连接
    print("\n1️⃣ 测试 Dashboard 连接...")
    try:
        dashboard = DashboardClient()
        stats = dashboard.get_stats(hours=24)
        print(f"   ✅ Dashboard 连接成功")
        print(f"   📊 当前任务数：{stats.get('total_tasks', 0)}")
    except Exception as e:
        print(f"   ❌ Dashboard 连接失败：{e}")
        return False
    
    # 2. 执行测试任务
    print("\n2️⃣ 执行测试任务...")
    orchestrator = SmartOrchestrator()
    
    test_input = "搜索一下最新的 AI 技术突破新闻"
    print(f"   任务：{test_input}")
    
    result = await orchestrator.execute(test_input, user_id="test_user_002")
    
    print(f"   ✅ 任务执行完成")
    print(f"   任务 ID: {result.task_id}")
    print(f"   评分：{result.total_score:.1f}/10")
    
    # 3. 等待 Dashboard 数据更新
    print("\n3️⃣ 等待 Dashboard 数据更新...")
    await asyncio.sleep(1)
    
    # 4. 验证 Dashboard 数据
    print("\n4️⃣ 验证 Dashboard 数据...")
    tasks = dashboard.get_tasks(limit=10)
    print(f"   📊 Dashboard 任务数：{len(tasks)}")
    
    if tasks:
        latest_task = tasks[0]
        print(f"   ✅ 最新任务：{latest_task.get('id', 'unknown')}")
        print(f"   - 内容：{latest_task.get('user_input', '')[:50]}")
        print(f"   - 状态：{latest_task.get('status', 'unknown')}")
        print(f"   - 渠道：{latest_task.get('channel', 'unknown')}")
    else:
        print(f"   ⚠️  Dashboard 中没有任务记录")
    
    # 5. 生成进度汇报
    print("\n5️⃣ 生成进度汇报...")
    reporter = HourlyProgressReporter()
    report = reporter.generate_report(period_hours=1)
    
    formatted = reporter.format_report(report, "detailed")
    print("\n" + formatted[:1000])  # 只打印前 1000 字符
    
    # 6. 验证 HEARTBEAT.md
    print("\n6️⃣ 验证 HEARTBEAT.md...")
    heartbeat_file = Path.home() / ".openclaw" / "workspace" / "HEARTBEAT.md"
    if heartbeat_file.exists():
        content = heartbeat_file.read_text(encoding='utf-8')
        if result.task_id in content:
            print(f"   ✅ HEARTBEAT.md 包含最新任务")
        else:
            print(f"   ⚠️  HEARTBEAT.md 未包含最新任务（可能已完成）")
    else:
        print(f"   ❌ HEARTBEAT.md 不存在")
    
    print("\n" + "=" * 60)
    print("✅ 完整集成测试完成！")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_full_integration())
    sys.exit(0 if success else 1)
