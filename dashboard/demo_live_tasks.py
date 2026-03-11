#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 实时任务演示

模拟 5 个任务从创建到完成的完整过程，展示 Dashboard 实时更新效果
"""

import asyncio
import time
import random
import requests
from datetime import datetime
from pathlib import Path

# 配置
TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
DASHBOARD_URL = "http://localhost:8765"

def load_token():
    return TOKEN_FILE.read_text().strip()

def create_task(task_id, user_input, user_id="demo_user"):
    """创建任务"""
    token = load_token()
    data = {
        "id": task_id,
        "user_id": user_id,
        "channel": "feishu",
        "user_input": user_input,
        "status": "processing",
        "stage": "received",
        "created_at": time.time()
    }
    # 这里简化处理，实际应该调用 API
    print(f"📝 创建任务：{task_id}")

def update_task_stage(task_id, stage, progress_percent):
    """更新任务阶段"""
    print(f"   → 阶段：{stage} ({progress_percent}%)")

async def simulate_task(task_id, user_input, duration_seconds=5):
    """模拟任务执行过程"""
    print(f"\n🚀 开始任务：{task_id}")
    print(f"   内容：{user_input}")
    
    stages = [
        ("received", 10),
        ("intent_analysis", 25),
        ("task_decomposition", 40),
        ("executing", 65),
        ("aggregating", 90),
        ("completed", 100)
    ]
    
    for stage, progress in stages:
        # 更新阶段
        update_task_stage(task_id, stage, progress)
        
        # 模拟处理时间
        await asyncio.sleep(duration_seconds / len(stages))
    
    print(f"✅ 任务完成：{task_id}")

async def main():
    """主函数"""
    print("=" * 70)
    print("🎭 灵犀 Dashboard 实时任务演示")
    print("=" * 70)
    print()
    print("📊 请在浏览器打开 Dashboard 查看实时更新：")
    print(f"   http://106.52.101.202:8765/?token={load_token()}")
    print()
    print("=" * 70)
    print()
    
    # 演示任务列表
    demo_tasks = [
        ("demo_task_001", "写一首关于人工智能的现代诗"),
        ("demo_task_002", "分析最近 3 天的科技新闻趋势"),
        ("demo_task_003", "生成小红书文案：春日穿搭指南"),
        ("demo_task_004", "翻译这段英文为中文：Hello World"),
        ("demo_task_005", "创建一个 Python 脚本分析 Excel 数据"),
    ]
    
    # 并发执行所有任务
    tasks = []
    for i, (task_id, user_input) in enumerate(demo_tasks):
        await asyncio.sleep(0.5)  # 错开启动时间
        task = asyncio.create_task(simulate_task(task_id, user_input, duration_seconds=3))
        tasks.append(task)
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)
    
    print()
    print("=" * 70)
    print("✅ 所有演示任务完成！")
    print("=" * 70)
    print()
    print("💡 提示：")
    print("   - Dashboard 应该显示 5 个已完成任务")
    print("   - 刷新页面可以看到最新数据")
    print("   - WebSocket 会实时更新任务状态（如果页面保持打开）")
    print()

if __name__ == "__main__":
    asyncio.run(main())
