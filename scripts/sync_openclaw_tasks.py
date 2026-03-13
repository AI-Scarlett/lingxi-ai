#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 会话同步到 Dashboard

功能：
- 定期扫描 OpenClaw 会话文件
- 提取未同步的对话
- 批量写入 Dashboard 数据库

使用：
python3 sync_openclaw_tasks.py
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 配置
OPENCLAW_SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
DB_PATH = Path("/root/lingxi-ai-latest/data/dashboard_v3.db")
STATE_FILE = Path("/root/lingxi-ai-latest/data/sync_state.json")

def load_sync_state() -> Dict:
    """加载同步状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"synced_messages": []}

def save_sync_state(state: Dict):
    """保存同步状态"""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_synced_messages() -> set:
    """获取已同步的消息 ID"""
    state = load_sync_state()
    return set(state.get("synced_messages", []))

def mark_as_synced(message_id: str):
    """标记为已同步"""
    state = load_sync_state()
    if "synced_messages" not in state:
        state["synced_messages"] = []
    if message_id not in state["synced_messages"]:
        state["synced_messages"].append(message_id)
        # 只保留最近 1000 条
        state["synced_messages"] = state["synced_messages"][-1000:]
    save_sync_state(state)

def scan_sessions() -> List[Dict]:
    """扫描所有会话文件，提取未同步的消息"""
    synced_ids = get_synced_messages()
    tasks = []
    
    if not OPENCLAW_SESSIONS_DIR.exists():
        print(f"⚠️ 会话目录不存在：{OPENCLAW_SESSIONS_DIR}")
        return tasks
    
    for session_file in OPENCLAW_SESSIONS_DIR.glob("*.jsonl"):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                try:
                    msg = json.loads(line.strip())
                    msg_id = msg.get('id', '')
                    
                    # 跳过已同步的消息
                    if msg_id in synced_ids:
                        continue
                    
                    msg_type = msg.get('type', '')
                    if msg_type != 'message':
                        continue
                    
                    message_data = msg.get('message', {})
                    role = message_data.get('role', '')
                    
                    # 只处理用户消息
                    if role != 'user':
                        continue
                    
                    # 提取内容
                    content_list = message_data.get('content', [])
                    content = ''
                    if isinstance(content_list, list):
                        for item in content_list:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                content += item.get('text', '')
                    
                    if not content.strip():
                        continue
                    
                    # 提取时间戳（支持 ISO 格式和数字格式）
                    ts = msg.get('timestamp', time.time())
                    if isinstance(ts, str):
                        # ISO 格式：2026-03-13T07:35:25.381Z
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            timestamp = time.time()
                    else:
                        timestamp = ts
                    
                    # 提取渠道信息
                    channel = 'unknown'
                    if 'channel' in msg:
                        channel = msg['channel']
                    # 不要从内容中判断渠道，因为系统 prompt 包含渠道关键字会导致误判
                    # 如果没有明确的 channel 字段，使用 'unknown'
                    
                    # 提取用户 ID
                    user_id = message_data.get('user_id', 'unknown')
                    
                    tasks.append({
                        'id': msg_id,
                        'user_input': content[:500],
                        'user_id': user_id,
                        'channel': channel,
                        'created_at': timestamp,
                        'session_file': session_file.name
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"⚠️ 读取会话文件失败 {session_file}: {e}")
            continue
    
    return tasks

def sync_to_dashboard(tasks: List[Dict]) -> int:
    """同步任务到 Dashboard"""
    if not tasks:
        print("✅ 没有新任务需要同步")
        return 0
    
    if not DB_PATH.exists():
        print(f"❌ Dashboard 数据库不存在：{DB_PATH}")
        return 0
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    synced_count = 0
    
    for task in tasks:
        try:
            now = time.time()
            task_id = f"task_{int(now)}_{task['id'][:8]}"
            
            # 确保 created_at 是数字类型
            created_at_val = task['created_at']
            if isinstance(created_at_val, str):
                try:
                    created_at_val = float(created_at_val)
                except:
                    created_at_val = now
            
            # 使用任务自带的 task_type（如果存在）
            task_type = task.get('task_type', 'realtime')
            
            cursor.execute("""
                INSERT OR REPLACE INTO tasks (
                    id, user_id, channel, user_input, status, task_type,
                    created_at, updated_at, completed_at, skill_name, llm_model, schedule_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                task_id,
                task['user_id'],
                task['channel'],
                task['user_input'],
                'completed',
                task_type,
                created_at_val,
                now,
                now,
                'openclaw',
                'qwen3.5-plus',
                'heartbeat' if task_type == 'scheduled' else None
            ])
            
            # 标记为已同步
            mark_as_synced(task['id'])
            synced_count += 1
            
        except Exception as e:
            print(f"⚠️ 同步任务失败 {task['id']}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    return synced_count

def main():
    """主函数"""
    print(f"\n🦞 OpenClaw 会话同步到 Dashboard")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"会话目录：{OPENCLAW_SESSIONS_DIR}")
    print(f"数据库：{DB_PATH}")
    print()
    
    # 扫描会话
    print("📋 扫描会话文件...")
    tasks = scan_sessions()
    print(f"发现 {len(tasks)} 条未同步的消息")
    
    # 同步到 Dashboard
    print("\n🔄 同步到 Dashboard...")
    synced_count = sync_to_dashboard(tasks)
    print(f"✅ 成功同步 {synced_count} 条任务")
    
    print(f"\n✨ 同步完成")

if __name__ == "__main__":
    main()
