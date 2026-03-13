#!/bin/bash
# OpenClaw 自动任务记录 Wrapper
# 使用方法：在 openclaw 命令前加上这个 wrapper

# 记录命令到 Dashboard
log_to_dashboard() {
    local user_input="$1"
    local user_id="$2"
    local channel="$3"
    
    python3 << EOF
import sqlite3
import time
from pathlib import Path

DB_PATH = Path("/root/lingxi-ai-latest/data/dashboard_v3.db")
if DB_PATH.exists():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("""
        INSERT INTO tasks (id, user_id, channel, user_input, status, task_type, created_at, updated_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        f"task_{int(now)}",
        "$user_id",
        "$channel",
        "$user_input"[:500],
        "completed",
        "realtime",
        now, now, now
    ])
    conn.commit()
    conn.close()
    print(f"✅ 任务已记录")
EOF
}

# 调用原始 openclaw 命令
exec /usr/local/bin/openclaw "$@"
