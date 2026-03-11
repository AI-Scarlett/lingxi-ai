from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import sqlite3
import time
import json
import asyncio
from pathlib import Path
from typing import Optional, List

# 静态文件目录
DASHBOARD_DIR = Path(__file__).parent

app = FastAPI(title="灵犀 Dashboard")

# OpenClaw 数据源
OPENCLAW_SESSIONS_FILE = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
OPENCLAW_CONVERSATIONS_DIR = Path.home() / ".openclaw" / "workspace" / "conversations"
OPENCLAW_TASK_STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".learnings" / "task_state.json"

def get_session_conversations(session_id: str, limit: int = 10):
    """从 OpenClaw session .jsonl 文件获取对话历史（提取真实用户指令）"""
    session_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / f"{session_id}.jsonl"
    
    if not session_file.exists():
        return []
    
    conversations = []
    try:
        lines = session_file.read_text().strip().split('\n')
        
        # 遍历所有消息
        for line in lines:
            try:
                event = json.loads(line)
                if event.get("type") == "message":
                    msg = event.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", [])
                    
                    # 跳过 toolResult 类型
                    if role == "toolResult":
                        continue
                    
                    # 提取文本内容
                    text = ""
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                break
                        elif isinstance(item, str):
                            text = item
                    
                    if text and role in ["user", "assistant"]:
                        # 提取用户真实消息：ou_...: 后面的内容
                        if role == "user" and "ou_4192609eb71f18ae82f9163f02bef144:" in text:
                            parts = text.split("ou_4192609eb71f18ae82f9163f02bef144:")
                            real_msg = parts[-1].strip()
                            if real_msg and len(real_msg) > 5:
                                text = real_msg
                        
                        conversations.append({
                            "role": "👤 用户" if role == "user" else "🤖 助手",
                            "content": text[:300],
                            "timestamp": event.get("timestamp", ""),
                            "is_user": role == "user"
                        })
            except:
                pass
        
        # 只保留最后 N 条
        return conversations[-limit:]
    except Exception as e:
        print(f"读取对话历史失败: {e}")
        return []


def get_session_title(session_id: str):
    """从对话历史提取任务标题（用户真实指令）"""
    session_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / f"{session_id}.jsonl"
    
    if not session_file.exists():
        return "未知任务"
    
    try:
        lines = session_file.read_text().strip().split('\n')
        
        for line in lines:
            try:
                event = json.loads(line)
                if event.get("type") == "message":
                    msg = event.get("message", {})
                    if msg.get("role") == "user":
                        content = msg.get("content", [])
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text = item.get("text", "")
                                # 提取用户真实消息：ou_4192609eb71f18ae82f9163f02bef144: 后面的内容
                                if "ou_4192609eb71f18ae82f9163f02bef144:" in text:
                                    # 找到最后一次出现的 ou_...: 后面的内容
                                    parts = text.split("ou_4192609eb71f18ae82f9163f02bef144:")
                                    real_msg = parts[-1].strip()
                                    if real_msg and len(real_msg) > 5:
                                        # 限制长度
                                        title = real_msg[:60]
                                        if len(real_msg) > 60:
                                            title += "..."
                                        return title
            except:
                pass
        
        return "未知任务"
    except Exception as e:
        print(f"提取标题失败: {e}")
        return "未知任务"


def get_openclaw_sessions():
    """从 OpenClaw sessions.json 获取真实会话数据"""
    if not OPENCLAW_SESSIONS_FILE.exists():
        return {}
    try:
        return json.loads(OPENCLAW_SESSIONS_FILE.read_text())
    except:
        return {}

def get_openclaw_tasks():
    """从 OpenClaw task_state.json 获取任务数据"""
    if not OPENCLAW_TASK_STATE_FILE.exists():
        return {}
    try:
        return json.loads(OPENCLAW_TASK_STATE_FILE.read_text())
    except:
        return {}

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token
DASHBOARD_TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
DASHBOARD_TOKEN = DASHBOARD_TOKEN_FILE.read_text().strip() if DASHBOARD_TOKEN_FILE.exists() else "default_token"

# 数据库
DB_PATH = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/tasks")
async def get_tasks(limit: int = 50, channel: str = None, status: str = None, date_range: str = None, schedule_name: str = None):
    """从 OpenClaw 和数据库获取真实任务数据 - 支持筛选"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 优先从数据库获取（包含所有渠道）
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if channel:
        query += " AND channel = ?"
        params.append(channel)
    if status:
        query += " AND status = ?"
        params.append(status)
    if schedule_name:
        query += " AND schedule_name = ?"
        params.append(schedule_name)
    if date_range:
        now = time.time()
        if date_range == 'today':
            today_start = now - (now % 86400)
            query += " AND created_at > ?"
            params.append(today_start)
        elif date_range == 'week':
            query += " AND created_at > ?"
            params.append(now - 7 * 86400)
        elif date_range == 'month':
            query += " AND created_at > ?"
            params.append(now - 30 * 86400)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "user_id": row[1],
            "channel": row[2],
            "user_input": row[3],
            "status": row[4],
            "stage": row[5],
            "created_at": row[6],
            "updated_at": row[7],
            "started_at": row[8],
            "completed_at": row[9],
            "task_type": row[10],
            "schedule_name": row[11],
            "cron_expr": row[12],
            "response_time_ms": row[13],
            "execution_time_ms": row[14],
            "wait_time_ms": row[15],
            "llm_called": row[16],
            "llm_model": row[17],
            "llm_tokens_in": row[18],
            "llm_tokens_out": row[19],
            "llm_cost": row[20],
            "intent_types": row[21],
            "subtask_count": row[22],
            "subtasks": row[23],
            "error_type": row[24],
            "error_message": row[25],
            "error_traceback": row[26],
            "final_output": row[27],
            "score": row[28],
            "skill_name": row[29],
            "skill_agent": row[30],
            "execution_context": row[31]
        })
    
    # 如果数据库数据少，补充 sessions 数据
    if len(tasks) < 10:
        sessions = get_openclaw_sessions()
        now = time.time()
        
        for session_key, session_data in sessions.items():
            session_id = session_data.get("sessionId", session_key)
            updated_at = session_data.get("updatedAt", 0)
            if updated_at and (now - updated_at / 1000) > 7 * 24 * 3600:
                continue
            
            session_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / f"{session_id}.jsonl"
            if not session_file.exists():
                continue
            
            # 判断渠道
            channel = "unknown"
            if "deliveryContext" in session_data:
                dc = session_data["deliveryContext"]
                if "qqbot" in str(dc):
                    channel = "qqbot"
                elif "feishu" in str(dc):
                    channel = "feishu"
                elif "wecom" in str(dc):
                    channel = "wecom"
            elif "qqbot" in session_key:
                channel = "qqbot"
            elif "feishu" in session_key:
                channel = "feishu"
            elif "wecom" in session_key:
                channel = "wecom"
            
            try:
                lines = session_file.read_text().strip().split('\n')
                msg_index = 0
                
                for line in lines:
                    try:
                        event = json.loads(line)
                        if event.get("type") == "message":
                            msg = event.get("message", {})
                            if msg.get("role") == "user":
                                content = msg.get("content", [])
                                for item in content:
                                    if isinstance(item, dict) and item.get("type") == "text":
                                        text = item.get("text", "")
                                        real_msg = ""
                                        if "ou_" in text or "wx_" in text or "oc_" in text:
                                            import re
                                            match = re.search(r'(ou_|wx_|oc_)[a-z0-9]+', text)
                                            if match:
                                                user_id = match.group(0)
                                                parts = text.split(user_id + ":")
                                                real_msg = parts[-1].strip() if len(parts) > 1 else text.strip()
                                            else:
                                                real_msg = text.strip()
                                        else:
                                            real_msg = text.strip()
                                        
                                        if real_msg and len(real_msg) >= 2:
                                            msg_index += 1
                                            timestamp = event.get("timestamp", "")
                                            if timestamp:
                                                try:
                                                    from datetime import datetime
                                                    dt = datetime.fromisoformat(timestamp.replace("Z", ""))
                                                    created_at = dt.timestamp()
                                                except:
                                                    created_at = updated_at / 1000 if updated_at else 0
                                            else:
                                                created_at = updated_at / 1000 if updated_at else 0
                                            
                                            skills_snapshot = session_data.get("skillsSnapshot", {})
                                            resolved_skills = skills_snapshot.get("resolvedSkills", [])
                                            skill_names = [s.get("name", "") for s in resolved_skills if s.get("name")]
                                            
                                            task = {
                                                "id": f"{session_id}_msg{msg_index}",
                                                "session_id": session_id,
                                                "title": real_msg[:60],
                                                "full_message": real_msg,
                                                "user_input": real_msg,
                                                "channel": channel,
                                                "user_id": user_id if 'user_id' in locals() else "unknown",
                                                "llm_model": session_data.get("model", ""),
                                                "llm_tokens_in": session_data.get("inputTokens") or 0,
                                                "llm_tokens_out": session_data.get("outputTokens") or 0,
                                                "created_at": created_at,
                                                "updated_at": created_at,
                                                "status": "completed",
                                                "stage": "completed",
                                                "skill_name": skill_names[0] if skill_names else "openclaw",
                                                "chat_type": "direct"
                                            }
                                            
                                            # 检查是否已在数据库中
                                            existing_ids = [t["id"] for t in tasks]
                                            if task["id"] not in existing_ids:
                                                tasks.append(task)
                                        break
                    except:
                        pass
            except Exception as e:
                print(f"处理 session {session_id} 失败：{e}")
        
        tasks.sort(key=lambda x: x.get("created_at", 0) or 0, reverse=True)
    
    return {"tasks": tasks[:limit], "total": len(tasks)}
    
    # 从每个 session 中提取所有用户消息作为独立任务
    for session_key, session_data in sessions.items():
        session_id = session_data.get("sessionId", session_key)
        
        # 跳过太旧的会话（超过 7 天）
        updated_at = session_data.get("updatedAt", 0)
        if updated_at and (now - updated_at / 1000) > 7 * 24 * 3600:
            continue
        
        # 从 session 文件中提取所有用户消息
        session_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / f"{session_id}.jsonl"
        if not session_file.exists():
            continue
        
        try:
            lines = session_file.read_text().strip().split('\n')
            msg_index = 0
            
            for line in lines:
                try:
                    event = json.loads(line)
                    if event.get("type") == "message":
                        msg = event.get("message", {})
                        if msg.get("role") == "user":
                            content = msg.get("content", [])
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text = item.get("text", "")
                                    # 提取用户真实消息
                                    if "ou_4192609eb71f18ae82f9163f02bef144:" in text:
                                        parts = text.split("ou_4192609eb71f18ae82f9163f02bef144:")
                                        real_msg = parts[-1].strip()
                                        if real_msg and len(real_msg) >= 2:  # 至少2个字符
                                            msg_index += 1
                                            timestamp = event.get("timestamp", "")
                                            # 解析时间戳
                                            if timestamp:
                                                try:
                                                    from datetime import datetime
                                                    dt = datetime.fromisoformat(timestamp.replace("Z", ""))
                                                    created_at = dt.timestamp()
                                                except:
                                                    created_at = updated_at / 1000 if updated_at else 0
                                            else:
                                                created_at = updated_at / 1000 if updated_at else 0
                                            
                                            # 提取技能信息
                                            skills_snapshot = session_data.get("skillsSnapshot", {})
                                            resolved_skills = skills_snapshot.get("resolvedSkills", [])
                                            skill_names = [s.get("name", "") for s in resolved_skills if s.get("name")]
                                            
                                            task = {
                                                "id": f"{session_id}_msg{msg_index}",
                                                "session_id": session_id,
                                                "title": real_msg[:60] + ("..." if len(real_msg) > 60 else ""),
                                                "full_message": real_msg,
                                                "channel": "qqbot" if ("qqbot" in session_key or ("deliveryContext" in session_data and "qqbot" in str(session_data.get("deliveryContext", {})))) else "feishu" if "feishu" in session_key else "unknown",
                                                "user_id": "ou_4192609eb71f18ae82f9163f02bef144",
                                                "llm_model": session_data.get("model", ""),
                                                "llm_tokens_in": session_data.get("inputTokens") or 0,
                                                "llm_tokens_out": session_data.get("outputTokens") or 0,
                                                "created_at": created_at,
                                                "updated_at": created_at,
                                                "status": "completed",
                                                "stage": "completed",
                                                "skill_name": skill_names[0] if skill_names else "openclaw",
                                                "skill_names": skill_names[:3],
                                                "chat_type": "direct"
                                            }
                                            tasks.append(task)
                                    break
                except:
                    pass
        except Exception as e:
            print(f"处理 session {session_id} 失败: {e}")
    
    # 按时间排序
    tasks.sort(key=lambda x: x.get("created_at", 0) or 0, reverse=True)
    
    return {"tasks": tasks[:limit], "total": len(tasks)}


@app.get("/api/tasks/{task_id}")
async def get_task_detail(task_id: str):
    """获取任务详情（包含对话历史）"""
    sessions = get_openclaw_sessions()
    
    # 解析任务ID：格式为 {session_id}_msg{index}
    if "_msg" in task_id:
        parts = task_id.split("_msg")
        session_id = parts[0]
        msg_index = int(parts[1]) if len(parts) > 1 else 1
    else:
        session_id = task_id
        msg_index = None
    
    # 从 sessions 查找
    for session_key, session_data in sessions.items():
        if session_data.get("sessionId") == session_id or session_id in session_key:
            # 获取对话历史
            conversations = get_session_conversations(session_id, limit=20)
            
            # 找到对应的消息
            if msg_index:
                session_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / f"{session_id}.jsonl"
                if session_file.exists():
                    lines = session_file.read_text().strip().split('\n')
                    current_index = 0
                    for line in lines:
                        try:
                            event = json.loads(line)
                            if event.get("type") == "message":
                                msg = event.get("message", {})
                                if msg.get("role") == "user":
                                    content = msg.get("content", [])
                                    for item in content:
                                        if isinstance(item, dict) and item.get("type") == "text":
                                            text = item.get("text", "")
                                            if "ou_4192609eb71f18ae82f9163f02bef144:" in text:
                                                parts_text = text.split("ou_4192609eb71f18ae82f9163f02bef144:")
                                                real_msg = parts_text[-1].strip()
                                                if real_msg and len(real_msg) >= 2:
                                                    current_index += 1
                                                    if current_index == msg_index:
                                                        # 找到了对应的任务
                                                        # 提取技能信息
                                                        skills_snapshot = session_data.get("skillsSnapshot", {})
                                                        resolved_skills = skills_snapshot.get("resolvedSkills", [])
                                                        skill_names = [s.get("name", "") for s in resolved_skills if s.get("name")]
                                                        
                                                        timestamp = event.get("timestamp", "")
                                                        if timestamp:
                                                            try:
                                                                from datetime import datetime
                                                                dt = datetime.fromisoformat(timestamp.replace("Z", ""))
                                                                created_at = dt.timestamp()
                                                            except:
                                                                created_at = session_data.get("updatedAt", 0) / 1000 if session_data.get("updatedAt") else 0
                                                        else:
                                                            created_at = session_data.get("updatedAt", 0) / 1000 if session_data.get("updatedAt") else 0
                                                        
                                                        return {
                                                            "id": task_id,
                                                            "title": real_msg[:60] + ("..." if len(real_msg) > 60 else ""),
                                                            "full_message": real_msg,
                                                            "session_id": session_id,
                                                            "channel": "qqbot" if ("qqbot" in session_key or ("deliveryContext" in session_data and "qqbot" in str(session_data.get("deliveryContext", {})))) else "feishu" if "feishu" in session_key else "unknown",
                                                            "user_id": "ou_4192609eb71f18ae82f9163f02bef144",
                                                            "llm_model": session_data.get("model", ""),
                                                            "llm_tokens_in": session_data.get("inputTokens") or 0,
                                                            "llm_tokens_out": session_data.get("outputTokens") or 0,
                                                            "created_at": created_at,
                                                            "status": "completed",
                                                            "stage": "completed",
                                                            "skill_name": skill_names[0] if skill_names else "openclaw",
                                                            "skill_names": skill_names[:3],
                                                            "conversations": conversations,
                                                            "response_time_ms": 0
                                                        }
                        except:
                            pass
    
    return JSONResponse({"error": "Task not found", "task_id": task_id}, status_code=404)

@app.get("/api/stats")
async def get_stats(hours: int = 24):
    """从 OpenClaw 和数据库获取真实统计"""
    sessions = get_openclaw_sessions()
    
    now = time.time()
    cutoff = now - hours * 3600
    
    total_tasks = 0
    total_tokens_in = 0
    total_tokens_out = 0
    total_cost = 0.0
    model_stats = {}
    
    # 从 sessions 统计（实时任务）
    for session_key, session_data in sessions.items():
        updated_at = session_data.get("updatedAt", 0)
        if updated_at and updated_at / 1000 < cutoff:
            continue
        
        total_tasks += 1
        tokens_in = session_data.get("inputTokens", 0)
        tokens_out = session_data.get("outputTokens", 0)
        total_tokens_in += tokens_in
        total_tokens_out += tokens_out
        
        # 估算成本（简单计算）
        cost = (tokens_in * 0.002 / 1000) + (tokens_out * 0.006 / 1000)
        total_cost += cost
        
        model = session_data.get("model", "unknown")
        if model not in model_stats:
            model_stats[model] = {"count": 0, "tokens_in": 0, "tokens_out": 0, "cost": 0}
        model_stats[model]["count"] += 1
        model_stats[model]["tokens_in"] += tokens_in
        model_stats[model]["tokens_out"] += tokens_out
        model_stats[model]["cost"] += cost
    
    # 从数据库获取统计（优先使用数据库，因为包含所有渠道的任务）
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 计算时间范围
        if hours >= 87600:  # 所有时间
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(llm_tokens_in), 0), COALESCE(SUM(llm_tokens_out), 0), COALESCE(SUM(llm_cost), 0) FROM tasks")
        else:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(llm_tokens_in), 0), COALESCE(SUM(llm_tokens_out), 0), COALESCE(SUM(llm_cost), 0)
                FROM tasks 
                WHERE created_at > ?
            """, (now - hours * 3600,))
        
        db_result = cursor.fetchone()
        if db_result and db_result[0]:
            db_count = db_result[0] or 0
            db_tokens_in = db_result[1] or 0
            db_tokens_out = db_result[2] or 0
            db_cost = db_result[3] or 0
            
            # 优先使用数据库数据（更准确）
            if db_count > 0:
                total_tasks = db_count
                total_tokens_in = db_tokens_in
                total_tokens_out = db_tokens_out
                total_cost = db_cost
        
        conn.close()
    except Exception as e:
        print(f"数据库统计失败：{e}")
    
    # 计算平均响应时间
    avg_response_ms = 0
    try:
        conn = get_db()
        cursor = conn.cursor()
        if hours >= 87600:
            cursor.execute("SELECT AVG(response_time_ms) FROM tasks WHERE response_time_ms > 0")
        else:
            cursor.execute("SELECT AVG(response_time_ms) FROM tasks WHERE created_at > ? AND response_time_ms > 0", (now - hours * 3600,))
        result = cursor.fetchone()
        if result and result[0]:
            avg_response_ms = result[0]
        conn.close()
    except:
        pass
    
    # 计算错误率
    error_rate = 0.0
    try:
        conn = get_db()
        cursor = conn.cursor()
        if hours >= 87600:
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
            failed_count = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_count = cursor.fetchone()[0] or 1
        else:
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE created_at > ? AND status = 'failed'", (now - hours * 3600,))
            failed_count = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE created_at > ?", (now - hours * 3600,))
            total_count = cursor.fetchone()[0] or 1
        error_rate = (failed_count / total_count) * 100 if total_count > 0 else 0
        conn.close()
    except:
        pass
    
    # 计算平均执行时间
    avg_execution_ms = 0
    try:
        conn = get_db()
        cursor = conn.cursor()
        if hours >= 87600:
            cursor.execute("SELECT AVG(execution_time_ms) FROM tasks WHERE execution_time_ms > 0")
        else:
            cursor.execute("SELECT AVG(execution_time_ms) FROM tasks WHERE created_at > ? AND execution_time_ms > 0", (now - hours * 3600,))
        result = cursor.fetchone()
        if result and result[0]:
            avg_execution_ms = result[0]
        conn.close()
    except:
        pass
    
    return {
        "total_tasks": total_tasks,
        "llm_calls": total_tasks,
        "llm_cost": total_cost,
        "llm_tokens_in": total_tokens_in,
        "llm_tokens_out": total_tokens_out,
        "avg_response_ms": avg_response_ms,
        "avg_execution_ms": avg_execution_ms,
        "error_rate": error_rate,
        "model_stats": model_stats
    }

@app.get("/api/skills")
async def get_skills():
    """从 OpenClaw 获取技能列表"""
    skill_dirs = [Path("/root/.openclaw/skills"), Path("/root/.openclaw/workspace/skills")]
    
    # 从 sessions 统计技能使用
    sessions = get_openclaw_sessions()
    skill_usage = {}
    
    for session_key, session_data in sessions.items():
        # 从 skillsSnapshot 提取
        skills_snapshot = session_data.get("skillsSnapshot", {})
        resolved_skills = skills_snapshot.get("resolvedSkills", [])
        for skill in resolved_skills:
            name = skill.get("name", "")
            if name:
                if name not in skill_usage:
                    skill_usage[name] = {"count": 0, "tokens": 0}
                skill_usage[name]["count"] += 1
                skill_usage[name]["tokens"] += session_data.get("inputTokens", 0) + session_data.get("outputTokens", 0)
    
    skills = []
    for skill_dir in skill_dirs:
        if skill_dir.exists():
            for item in skill_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    skill_info = {
                        "name": item.name,
                        "status": "active",
                        "emoji": "📦",
                        "description": "",
                        "model": "qwen3.5-plus",
                        "model_provider": "阿里云百炼",
                        "usage_24h": skill_usage.get(item.name, {}).get("count", 0),
                        "tokens_24h": skill_usage.get(item.name, {}).get("tokens", 0)
                    }
                    
                    # 读取 SKILL.md
                    skill_md = item / "SKILL.md"
                    if not skill_md.exists():
                        skill_md = item / "skill" / "SKILL.md"
                    if not skill_md.exists():
                        skill_md = item / "SKILL_HEAD.md"
                    
                    if skill_md.exists():
                        content = skill_md.read_text()[:1000]
                        for line in content.split('\n'):
                            if line.startswith('description:') or line.startswith('描述:'):
                                skill_info["description"] = line.split(':', 1)[1].strip()[:100]
                                break
                    
                    skills.append(skill_info)
    
    return {"skills": skills, "total": len(skills)}

@app.get("/api/models")
async def get_models():
    """从 OpenClaw 获取真实模型使用统计"""
    sessions = get_openclaw_sessions()
    
    model_stats = {}
    for session_key, session_data in sessions.items():
        model = session_data.get("model", "")
        if not model:
            continue
        
        if model not in model_stats:
            model_stats[model] = {
                "name": model,
                "provider": session_data.get("modelProvider", "unknown"),
                "count": 0,
                "tokens_in": 0,
                "tokens_out": 0
            }
        
        model_stats[model]["count"] += 1
        model_stats[model]["tokens_in"] += session_data.get("inputTokens", 0)
        model_stats[model]["tokens_out"] += session_data.get("outputTokens", 0)
    
    # 转换为列表并排序
    models = sorted(model_stats.values(), key=lambda x: x["count"], reverse=True)
    
    # 分为活跃和备用
    active_models = [m for m in models if m["count"] > 0]
    backup_models = []
    
    # 添加预定义的备用模型
    predefined = [
        {"name": "qwen3.5-plus", "provider": "阿里云百炼", "emoji": "🧠"},
        {"name": "qwen3-max", "provider": "阿里云百炼", "emoji": "🎯"},
        {"name": "glm-5", "provider": "智谱AI", "emoji": "🔮"},
        {"name": "glm-4.7", "provider": "智谱AI", "emoji": "💎"},
        {"name": "kimi-k2.5", "provider": "Moonshot", "emoji": "📚"},
        {"name": "DeepSeek-V3", "provider": "DeepSeek", "emoji": "🚀"},
    ]
    
    active_names = {m["name"] for m in active_models}
    for p in predefined:
        if p["name"] not in active_names:
            backup_models.append({
                "name": p["name"],
                "provider": p["provider"],
                "emoji": p["emoji"],
                "usage_count": 0,
                "tokens_used": 0,
                "skills": []
            })
    
    # 格式化活跃模型
    for m in active_models:
        m["usage_count"] = m.pop("count")
        m["tokens_used"] = m["tokens_in"] + m["tokens_out"]
        m["skills"] = []
        m["emoji"] = "🔮" if "glm" in m["name"] else "🧠"
    
    return {
        "active_models": active_models,
        "backup_models": backup_models,
        "total": len(active_models) + len(backup_models)
    }

@app.get("/api/errors")
async def get_errors(limit: int = 10):
    """获取错误列表"""
    conn = get_db()
    cursor = conn.execute("""
        SELECT id, user_input, error_type, error_message, created_at, channel
        FROM tasks 
        WHERE status = 'failed' OR error_type != ''
        ORDER BY created_at DESC 
        LIMIT ?
    """, [limit])
    rows = cursor.fetchall()
    conn.close()
    
    errors = []
    for row in rows:
        errors.append({
            "id": row[0],
            "user_input": row[1],
            "error_type": row[2] or "执行失败",
            "error_message": row[3],
            "created_at": row[4],
            "channel": row[5]
        })
    
    return {"errors": errors, "total": len(errors)}

    # 从 OpenClaw tasks 查找
    if oc_tasks.get("tasks") and task_id in oc_tasks["tasks"]:
        task_data = oc_tasks["tasks"][task_id]
        return {
            "id": task_id,
            "title": task_data.get("description", "未知任务")[:50],
            "user_input": task_data.get("description", ""),
            "channel": task_data.get("channel", "unknown"),
            "user_id": task_data.get("user_id", "unknown"),
            "status": task_data.get("status", "unknown"),
            "created_at": task_data.get("created_at", ""),
            "skill_name": "lingxi",
            "llm_model": "",
            "llm_tokens_in": 0,
            "llm_tokens_out": 0,
            "conversations": []
        }
    
    return JSONResponse({"error": "Task not found"}, status_code=404)

@app.get("/api/scheduled-tasks")
async def get_scheduled_tasks():
    """获取定时任务列表"""
    oc_tasks = get_openclaw_tasks()
    
    scheduled = []
    if oc_tasks.get("scheduled_tasks"):
        for i, task in enumerate(oc_tasks["scheduled_tasks"]):
            scheduled.append({
                "id": f"sched_{i+1}",
                "name": task.get("name", "未命名"),
                "schedule": task.get("schedule", ""),
                "description": task.get("description", "")[:100],
                "source": task.get("source", "unknown"),
                "status": "active"
            })
    
    # 也从 HEARTBEAT.md 读取
    heartbeat_file = Path.home() / ".openclaw" / "workspace" / "HEARTBEAT.md"
    if heartbeat_file.exists():
        content = heartbeat_file.read_text()
        # 解析定时任务
        import re
        matches = re.findall(r'- ⏰ \*\*(.+?)\*\*:\s*(.+?)(?:\n|$)', content)
        for name, desc in matches:
            # 检查是否已存在
            if not any(s["name"] == name for s in scheduled):
                scheduled.append({
                    "id": f"heartbeat_{len(scheduled)+1}",
                    "name": name,
                    "schedule": "0 * * * *",
                    "description": desc[:100],
                    "source": "heartbeat",
                    "status": "active"
                })
    
    return {"scheduled_tasks": scheduled, "total": len(scheduled)}

# 写入 API - 记录任务
@app.post("/api/tasks")
async def create_task(task: dict):
    """记录新任务"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 确保必要字段
    task_id = task.get("id", f"task_{int(time.time()*1000)}")
    now = time.time()
    
    cursor.execute("""
        INSERT OR REPLACE INTO tasks (
            id, user_id, channel, user_input, status, stage,
            created_at, updated_at, started_at, completed_at,
            task_type, schedule_name, cron_expr,
            response_time_ms, execution_time_ms, wait_time_ms,
            llm_called, llm_model, llm_tokens_in, llm_tokens_out, llm_cost,
            intent_types, subtask_count, subtasks,
            error_type, error_message, error_traceback,
            final_output, score, skill_name, skill_agent, execution_context
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        task_id,
        task.get("user_id", "unknown"),
        task.get("channel", "unknown"),
        task.get("user_input", ""),
        task.get("status", "pending"),
        task.get("stage", "received"),
        task.get("created_at", now),
        task.get("updated_at", now),
        task.get("started_at"),
        task.get("completed_at"),
        task.get("task_type", "realtime"),
        task.get("schedule_name", ""),
        task.get("cron_expr", ""),
        task.get("response_time_ms", 0),
        task.get("execution_time_ms", 0),
        task.get("wait_time_ms", 0),
        task.get("llm_called", 0),
        task.get("llm_model", ""),
        task.get("llm_tokens_in", 0),
        task.get("llm_tokens_out", 0),
        task.get("llm_cost", 0),
        json.dumps(task.get("intent_types", [])),
        task.get("subtask_count", 0),
        json.dumps(task.get("subtasks", [])),
        task.get("error_type", ""),
        task.get("error_message", ""),
        task.get("error_traceback", ""),
        task.get("final_output", ""),
        task.get("score", 0),
        task.get("skill_name", ""),
        task.get("skill_agent", ""),
        task.get("execution_context", "")
    ])
    
    conn.commit()
    conn.close()
    
    # 广播新任务到所有 WebSocket 连接
    new_task_info = {
        "id": task_id,
        "user_input": task.get("user_input", "")[:100],
        "llm_model": task.get("llm_model", ""),
        "skill_name": task.get("skill_name", ""),
        "status": task.get("status", "pending"),
        "created_at": now
    }
    await manager.broadcast({"type": "new_task", "data": new_task_info})
    
    return {"success": True, "id": task_id}

# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket 实时连接"""
    # Token 验证
    if token != DASHBOARD_TOKEN:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await manager.connect(websocket)
    try:
        # 发送初始数据
        stats = await get_stats()
        tasks = await get_tasks(limit=20)
        await websocket.send_json({
            "type": "init",
            "data": {
                "stats": stats,
                "tasks": tasks["tasks"]
            }
        })
        
        # 保持连接，定期发送更新
        while True:
            await asyncio.sleep(5)
            stats = await get_stats()
            await websocket.send_json({
                "type": "stats_update",
                "data": stats
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

# 前端页面路由
@app.get("/")
async def serve_index(token: str = Query(None)):
    """返回前端页面"""
    if token != DASHBOARD_TOKEN:
        return JSONResponse({"error": "Invalid token"}, status_code=401)
    return FileResponse(DASHBOARD_DIR / "index.html", media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
