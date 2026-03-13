#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 任务记录器 - 自动记录所有对话到 Dashboard

功能：
- 拦截 OpenClaw 的所有消息处理
- 自动记录任务到灵犀 Dashboard
- 支持多渠道（feishu/telegram/qq 等）

使用：
在 OpenClaw 启动时导入此模块即可自动启用
"""

import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Dashboard 配置
DASHBOARD_URL = "http://localhost:8765"
TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
DB_PATH = Path.home() / "lingxi-ai-latest" / "data" / "dashboard_v3.db"


def load_token() -> str:
    """加载 Dashboard Token"""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return ""


def record_task(
    user_input: str,
    user_id: str,
    channel: str,
    status: str = "completed",
    task_type: str = "realtime",
    skill_name: str = "openclaw",
    llm_model: str = "qwen3.5-plus",
    response_time_ms: float = 0,
    final_output: str = ""
) -> bool:
    """
    记录任务到 Dashboard 数据库
    
    Args:
        user_input: 用户输入
        user_id: 用户 ID
        channel: 渠道（feishu/telegram/qq 等）
        status: 任务状态
        task_type: 任务类型（realtime/scheduled）
        skill_name: 技能名称
        llm_model: 使用的模型
        response_time_ms: 响应时间（毫秒）
        final_output: 最终输出
    
    Returns:
        是否成功
    """
    try:
        if not DB_PATH.exists():
            print(f"⚠️ Dashboard 数据库不存在：{DB_PATH}")
            return False
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        now = time.time()
        task_id = f"task_{int(now)}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks (
                id, user_id, channel, user_input, status, task_type,
                created_at, updated_at, completed_at, skill_name, llm_model,
                response_time_ms, final_output
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            task_id,
            user_id,
            channel,
            user_input[:500],
            status,
            task_type,
            now,
            now,
            now,
            skill_name,
            llm_model,
            response_time_ms,
            final_output[:1000] if final_output else ""
        ])
        
        conn.commit()
        conn.close()
        
        print(f"✅ 任务已记录：{task_id}")
        return True
        
    except Exception as e:
        print(f"❌ 记录任务失败：{e}")
        return False


# ============ OpenClaw 钩子函数 ============

def on_message_received(user_input: str, user_id: str, channel: str, metadata: Dict = None):
    """
    OpenClaw 消息接收钩子
    
    在 OpenClaw 处理消息前调用
    """
    print(f"📝 [TaskRecorder] 收到消息：{user_input[:50]}...")


def on_message_completed(
    user_input: str,
    user_id: str,
    channel: str,
    response: str,
    model: str = "qwen3.5-plus",
    response_time_ms: float = 0,
    metadata: Dict = None
):
    """
    OpenClaw 消息处理完成钩子
    
    在 OpenClaw 处理完消息后自动记录到 Dashboard
    """
    record_task(
        user_input=user_input,
        user_id=user_id,
        channel=channel,
        status="completed",
        task_type="realtime",
        skill_name="openclaw",
        llm_model=model,
        response_time_ms=response_time_ms,
        final_output=response
    )


# ============ 自动注入 OpenClaw ============

def inject_openclaw():
    """
    自动注入到 OpenClaw 消息处理流程
    
    这会修改 OpenClaw 的行为，确保所有消息都被记录
    """
    try:
        # 尝试导入 OpenClaw 核心模块
        import openclaw
        print("✅ OpenClaw 已加载，准备注入任务记录器...")
        
        # 保存原始函数
        original_dispatch = getattr(openclaw, 'dispatch', None)
        
        if original_dispatch:
            def wrapped_dispatch(message, **kwargs):
                # 提取消息信息
                user_input = message.get('text', '') if isinstance(message, dict) else str(message)
                user_id = message.get('user_id', 'unknown') if isinstance(message, dict) else 'unknown'
                channel = message.get('channel', 'unknown') if isinstance(message, dict) else 'unknown'
                
                # 记录开始时间
                start_time = time.time()
                
                # 调用原始函数
                result = original_dispatch(message, **kwargs)
                
                # 计算响应时间
                response_time_ms = (time.time() - start_time) * 1000
                
                # 记录到 Dashboard
                on_message_completed(
                    user_input=user_input,
                    user_id=user_id,
                    channel=channel,
                    response=str(result),
                    response_time_ms=response_time_ms
                )
                
                return result
            
            # 替换原始函数
            openclaw.dispatch = wrapped_dispatch
            print("✅ 任务记录器已注入到 OpenClaw.dispatch")
        
    except ImportError:
        print("⚠️ OpenClaw 未加载，跳过注入")
    except Exception as e:
        print(f"⚠️ 注入失败：{e}")


# ============ 启动时自动注入 ============

if __name__ == "__main__":
    # 测试
    print("🦞 OpenClaw Task Recorder")
    print(f"Dashboard: {DASHBOARD_URL}")
    print(f"Database: {DB_PATH}")
    
    # 测试记录
    test_result = record_task(
        user_input="测试任务记录",
        user_id="test_user",
        channel="test",
        final_output="测试成功"
    )
    print(f"测试结果：{'✅' if test_result else '❌'}")
    
    # 自动注入
    inject_openclaw()
