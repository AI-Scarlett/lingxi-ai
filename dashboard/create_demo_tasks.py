#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 创建演示任务数据

直接在 Dashboard 数据库中创建真实的演示任务，让老板看到效果
"""

import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

DB_PATH = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard.db"

def create_demo_tasks():
    """创建演示任务"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 演示任务列表
    demo_tasks = [
        {
            "id": "demo_20260310_001",
            "user_input": "帮我分析 2026 年 AI 行业发展趋势",
            "user_id": "boss_demo",
            "channel": "feishu",
            "status": "completed",
            "stage": "completed",
            "duration": 15.3,
            "llm_model": "qwen3.5-plus",
            "llm_tokens": 2500
        },
        {
            "id": "demo_20260310_002",
            "user_input": "生成小红书文案：春季穿搭指南",
            "user_id": "boss_demo",
            "channel": "feishu",
            "status": "completed",
            "stage": "completed",
            "duration": 8.7,
            "llm_model": "qwen3.5-plus",
            "llm_tokens": 1200
        },
        {
            "id": "demo_20260310_003",
            "user_input": "搜索最新的量子计算突破新闻",
            "user_id": "boss_demo",
            "channel": "feishu",
            "status": "processing",
            "stage": "executing",
            "duration": None,
            "llm_model": "qwen3.5-plus",
            "llm_tokens": 800
        },
        {
            "id": "demo_20260310_004",
            "user_input": "翻译这篇英文文章为中文",
            "user_id": "boss_demo",
            "channel": "feishu",
            "status": "pending",
            "stage": "received",
            "duration": None,
            "llm_model": None,
            "llm_tokens": 0
        }
    ]
    
    now = time.time()
    
    for i, task in enumerate(demo_tasks):
        # 检查是否已存在
        cursor.execute("SELECT id FROM tasks WHERE id=?", (task["id"],))
        if cursor.fetchone():
            print(f"⚠️  任务已存在：{task['id']}")
            continue
        
        created_at = now - (len(demo_tasks) - i) * 300  # 每个任务间隔 5 分钟
        
        insert_sql = """
        INSERT INTO tasks (
            id, user_id, channel, user_input, status, stage,
            created_at, updated_at, started_at, completed_at,
            execution_time_ms, llm_called, llm_model, llm_tokens_in,
            subtask_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        completed_at = None
        execution_time = 0
        if task["status"] == "completed":
            completed_at = created_at + task["duration"]
            execution_time = task["duration"] * 1000
        
        cursor.execute(insert_sql, (
            task["id"],
            task["user_id"],
            task["channel"],
            task["user_input"],
            task["status"],
            task["stage"],
            created_at,
            created_at + 1,
            created_at + 1 if task["status"] != "pending" else None,
            completed_at,
            execution_time,
            task["llm_model"] is not None,
            task["llm_model"] or "",
            task["llm_tokens"],
            1
        ))
        
        print(f"✅ 创建任务：{task['id']} - {task['user_input'][:30]}...")
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 60)
    print("✅ 演示任务创建完成！")
    print("=" * 60)
    print()
    print("📊 请在 Dashboard 查看：")
    print("   http://106.52.101.202:8765/?token=" + Path.home().joinpath(".openclaw/workspace/.lingxi/dashboard_token.txt").read_text().strip())
    print()

if __name__ == "__main__":
    create_demo_tasks()
