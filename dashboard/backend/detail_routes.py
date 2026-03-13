#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详情页 API 路由 - 独立模块（带 Token 验证）
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import json
from pathlib import Path
from pathlib import Path as SysPath

# Token 验证配置
OPENCLAW_DIR = SysPath.home() / ".openclaw"
TOKEN_FILE = OPENCLAW_DIR / "workspace" / ".lingxi" / "dashboard_token.txt"

def verify_token(token: str = Query("", description="访问 Token")):
    """验证 Token"""
    if not TOKEN_FILE.exists():
        # 如果 Token 文件不存在，不强制验证（首次启动）
        return True
    saved = TOKEN_FILE.read_text().strip()
    if not saved:
        return True
    if token != saved:
        raise HTTPException(status_code=401, detail="Token 无效")
    return True

# 任务详情路由
task_router = APIRouter(prefix="/api/tasks", tags=["tasks_detail"])


class SubTaskDetail(BaseModel):
    id: str
    name: str
    description: str
    status: str
    agent: Optional[str] = None
    skill: Optional[str] = None
    duration_ms: Optional[float] = None
    result: Optional[str] = None
    error: Optional[str] = None


class LLMCallDetail(BaseModel):
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    latency_ms: float


@task_router.get("/{task_id}")
async def get_task_detail(task_id: str, _: bool = Depends(verify_token)):
    """获取任务详情"""
    from main import db
    
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 解析子任务
    subtasks_data = []
    if task.get('subtasks'):
        try:
            subtasks_raw = json.loads(task['subtasks']) if isinstance(task['subtasks'], str) else task['subtasks']
            for st in subtasks_raw:
                subtasks_data.append(SubTaskDetail(**{k: st.get(k) for k in ['id', 'name', 'description', 'status', 'agent', 'skill', 'duration_ms', 'result', 'error']}).model_dump())
        except:
            pass
    
    # 解析意图
    intent_types = []
    if task.get('intent_types'):
        try:
            intent_types = json.loads(task['intent_types']) if isinstance(task['intent_types'], str) else task['intent_types']
        except:
            pass
    
    total_duration = 0
    if task.get('completed_at') and task.get('created_at'):
        total_duration = (task['completed_at'] - task['created_at']) * 1000
    
    llm_calls = []
    if task.get('llm_called'):
        llm_calls.append({
            "model": task.get('llm_model', 'unknown'),
            "tokens_in": task.get('llm_tokens_in', 0),
            "tokens_out": task.get('llm_tokens_out', 0),
            "cost": task.get('llm_cost', 0),
            "latency_ms": task.get('execution_time_ms', 0)
        })
    
    return {
        "id": task['id'],
        "user_id": task['user_id'],
        "channel": task['channel'],
        "user_input": task['user_input'],
        "status": task['status'],
        "stage": task['stage'],
        "score": task.get('score', 0),
        "created_at": task['created_at'],
        "updated_at": task['updated_at'],
        "started_at": task.get('started_at'),
        "completed_at": task.get('completed_at'),
        "response_time_ms": task.get('response_time_ms', 0),
        "execution_time_ms": task.get('execution_time_ms', 0),
        "wait_time_ms": task.get('wait_time_ms', 0),
        "total_duration_ms": total_duration,
        "task_type": task.get('task_type', 'realtime'),
        "schedule_name": task.get('schedule_name'),
        "cron_expr": task.get('cron_expr'),
        "intent_types": intent_types,
        "subtask_count": len(subtasks_data),
        "subtasks": subtasks_data,
        "llm_called": task.get('llm_called', False),
        "llm_calls": llm_calls,
        "total_tokens_in": task.get('llm_tokens_in', 0),
        "total_tokens_out": task.get('llm_tokens_out', 0),
        "total_cost": task.get('llm_cost', 0),
        "skill_name": task.get('skill_name'),
        "skill_agent": task.get('skill_agent'),
        "error_type": task.get('error_type'),
        "error_message": task.get('error_message'),
        "error_traceback": task.get('error_traceback'),
        "final_output": task.get('final_output')
    }


@task_router.get("/{task_id}/timeline")
async def get_task_timeline(task_id: str, _: bool = Depends(verify_token)):
    """获取任务时间线"""
    from main import db
    
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    timeline = [
        {"stage": "received", "time": task['created_at'], "label": "任务接收", "description": f"从 {task['channel']} 渠道接收到任务"}
    ]
    
    if task.get('started_at'):
        timeline.append({"stage": "started", "time": task['started_at'], "label": "开始处理", "description": "任务开始执行"})
    
    if task.get('completed_at'):
        timeline.append({"stage": "completed", "time": task['completed_at'], "label": "任务完成", "description": f"最终得分：{task.get('score', 0)}"})
    
    timeline.sort(key=lambda x: x['time'])
    return {"task_id": task_id, "timeline": timeline}


@task_router.get("/{task_id}/subtasks")
async def get_task_subtasks(task_id: str, _: bool = Depends(verify_token)):
    """获取子任务列表"""
    from main import db
    import json
    
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    subtasks = []
    if task.get('subtasks'):
        try:
            subtasks = json.loads(task['subtasks']) if isinstance(task['subtasks'], str) else task['subtasks']
        except:
            pass
    
    return {"task_id": task_id, "subtasks": subtasks, "total": len(subtasks)}


# 技能详情路由
skill_router = APIRouter(prefix="/api/skills", tags=["skills_detail"])


@skill_router.get("/list")
async def list_skills(include_stats: bool = True, _: bool = Depends(verify_token)):
    """获取技能列表"""
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    skills = []
    
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
                skill_info = {
                    "name": skill_folder.name,
                    "display_name": skill_folder.name,
                    "description": "",
                    "version": "1.0.0",
                    "is_loaded": True
                }
                
                # 读取 SKILL.md
                skill_file = skill_folder / "SKILL.md"
                if skill_file.exists():
                    try:
                        content = skill_file.read_text(encoding='utf-8')[:2000]
                        if 'description:' in content:
                            start = content.find('description:') + 12
                            end = content.find('\n', start)
                            if end > start:
                                skill_info['description'] = content[start:end].strip()
                    except:
                        pass
                
                skills.append(skill_info)
    
    return {"total": len(skills), "skills": skills}


@skill_router.get("/{skill_name}")
async def get_skill_detail(skill_name: str, _: bool = Depends(verify_token)):
    """获取技能详情"""
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    skill_path = skills_dir / skill_name
    
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="技能不存在")
    
    skill_info = {
        "name": skill_name,
        "display_name": skill_name,
        "description": "",
        "version": "1.0.0",
        "location": str(skill_path),
        "is_loaded": True,
        "config": {
            "enabled": True,
            "priority": 5,
            "timeout_seconds": 60,
            "max_retries": 3,
            "require_auth": False,
            "allowed_channels": ["all"]
        },
        "stats": {
            "total_calls": 0,
            "success_rate": 100.0,
            "avg_response_time_ms": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "today_calls": 0,
            "week_calls": 0,
            "month_calls": 0
        },
        "versions": [{"version": "1.0.0", "released_at": time.time(), "changes": ["初始版本"], "is_current": True}],
        "triggers": [],
        "keywords": [],
        "dependencies": [],
        "required_envs": []
    }
    
    # 读取 SKILL.md
    skill_file = skill_path / "SKILL.md"
    if skill_file.exists():
        try:
            content = skill_file.read_text(encoding='utf-8')[:2000]
            if 'description:' in content:
                start = content.find('description:') + 12
                end = content.find('\n', start)
                if end > start:
                    skill_info['description'] = content[start:end].strip()
        except:
            pass
    
    return skill_info


@skill_router.get("/{skill_name}/stats")
async def get_skill_stats(skill_name: str, _: bool = Depends(verify_token)):
    """获取技能统计"""
    return {
        "skill_name": skill_name,
        "overview": {
            "total_calls": 0,
            "success_rate": 100.0,
            "avg_response_time_ms": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "today_calls": 0,
            "week_calls": 0,
            "month_calls": 0
        },
        "daily": [],
        "by_channel": {},
        "errors": []
    }


# Agent 详情路由
agent_router = APIRouter(prefix="/api/agents", tags=["agents_detail"])


@agent_router.get("/list")
async def list_agents(_: bool = Depends(verify_token)):
    """获取 Agent 列表"""
    return {
        "total": 1,
        "agents": [{
            "id": "main",
            "name": "main",
            "display_name": "主 Agent",
            "description": "主要的对话 Agent",
            "type": "main",
            "status": "active"
        }]
    }


@agent_router.get("/{agent_id}")
async def get_agent_detail(agent_id: str, _: bool = Depends(verify_token)):
    """获取 Agent 详情"""
    return {
        "id": agent_id,
        "name": agent_id,
        "display_name": "主 Agent" if agent_id == "main" else agent_id,
        "description": "主要的对话 Agent，处理所有用户请求",
        "version": "3.3.6",
        "agent_type": "main" if agent_id == "main" else "subagent",
        "status": "active",
        "health": {
            "status": "healthy",
            "last_seen": time.time(),
            "uptime_seconds": 3600,
            "memory_usage_mb": 256.5,
            "cpu_usage_percent": 2.3,
            "error_rate": 0.0,
            "avg_response_time_ms": 150
        },
        "capabilities": [
            {"name": "conversation", "description": "自然语言对话", "enabled": True, "tools": ["message", "browser", "exec"]},
            {"name": "task_execution", "description": "任务执行和分解", "enabled": True, "tools": ["sessions_spawn", "subagents"]},
            {"name": "file_operations", "description": "文件读写和管理", "enabled": True, "tools": ["read", "write", "edit"]}
        ],
        "tools": ["read", "write", "edit", "exec", "web_search", "browser", "message"],
        "skills": ["weather", "github", "obsidian", "tavily"],
        "model": "qwencode/qwen3.5-plus",
        "thinking_enabled": False,
        "max_context_length": 128000,
        "timeout_seconds": 300,
        "stats": {
            "total_tasks": 100,
            "success_rate": 98.5,
            "avg_execution_time_ms": 2500,
            "total_tokens": 50000,
            "total_cost": 0.5,
            "today_tasks": 15,
            "week_tasks": 80,
            "active_sessions": 1
        },
        "active_sessions": [],
        "recent_tasks": [],
        "environment": {"python_version": "3.12", "platform": "Linux"},
        "workspace": str(Path.home() / ".openclaw" / "workspace")
    }


@agent_router.get("/{agent_id}/sessions")
async def get_agent_sessions(agent_id: str, limit: int = 20, _: bool = Depends(verify_token)):
    """获取 Agent 会话"""
    return {"agent_id": agent_id, "total": 0, "sessions": []}


@agent_router.get("/{agent_id}/tasks")
async def get_agent_tasks(agent_id: str, days: int = 7, limit: int = 50, _: bool = Depends(verify_token)):
    """获取 Agent 任务"""
    return {"agent_id": agent_id, "days": days, "total": 0, "tasks": []}


@agent_router.get("/{agent_id}/health")
async def get_agent_health(agent_id: str, _: bool = Depends(verify_token)):
    """获取 Agent 健康状态"""
    return {
        "agent_id": agent_id,
        "current": {
            "status": "healthy",
            "last_seen": time.time(),
            "uptime_seconds": 3600,
            "memory_usage_mb": 256.5,
            "cpu_usage_percent": 2.3,
            "error_rate": 0.0,
            "avg_response_time_ms": 150
        },
        "history": [],
        "metrics": []
    }


# 会话详情路由
session_router = APIRouter(prefix="/api/sessions", tags=["sessions_detail"])


@session_router.get("/list")
async def list_sessions(status: str = "all", limit: int = 50, offset: int = 0, _: bool = Depends(verify_token)):
    """获取会话列表"""
    from main import db
    
    sessions = []
    try:
        # 尝试从数据库获取
        sessions = db.get_sessions(limit=limit) or []
    except:
        sessions = []
    
    return {"total": len(sessions), "limit": limit, "offset": offset, "sessions": sessions}


@session_router.get("/{session_id}")
async def get_session_detail(session_id: str, include_messages: bool = True, message_limit: int = 100, _: bool = Depends(verify_token)):
    """获取会话详情"""
    from main import db
    
    session = db.get_session(session_id) if hasattr(db, 'get_session') else None
    
    if not session:
        # 返回模拟数据
        session = {
            "id": session_id,
            "session_key": session_id,
            "label": None,
            "status": "active",
            "is_active": True,
            "created_at": time.time() - 3600,
            "updated_at": time.time(),
            "last_message_at": time.time(),
            "user_id": "user_001",
            "agent_id": "main",
            "channel": "feishu",
            "model": "qwencode/qwen3.5-plus",
            "thinking_enabled": False
        }
    
    return {
        **session,
        "stats": {
            "total_messages": 10,
            "user_messages": 5,
            "assistant_messages": 5,
            "tool_calls": 3,
            "total_tokens": 5000,
            "total_cost": 0.05,
            "duration_seconds": 300,
            "avg_response_time_ms": 150
        },
        "messages": [],
        "tool_calls": [],
        "parent_session": None,
        "sub_sessions": []
    }


@session_router.get("/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 100, offset: int = 0, _: bool = Depends(verify_token)):
    """获取会话消息"""
    return {"session_id": session_id, "total": 0, "limit": limit, "offset": offset, "messages": []}


@session_router.get("/{session_id}/tools")
async def get_session_tools(session_id: str, _: bool = Depends(verify_token)):
    """获取会话工具调用"""
    return {"session_id": session_id, "total_calls": 0, "tool_calls": [], "stats": {}}


@session_router.get("/{session_id}/stats")
async def get_session_stats(session_id: str, _: bool = Depends(verify_token)):
    """获取会话统计"""
    return {
        "session_id": session_id,
        "overview": {
            "total_messages": 10,
            "user_messages": 5,
            "assistant_messages": 5,
            "tool_calls": 3,
            "total_tokens": 5000,
            "total_cost": 0.05,
            "duration_seconds": 300,
            "avg_response_time_ms": 150
        },
        "hourly": [],
        "tools": {},
        "tokens": {}
    }


# 记忆详情路由
memory_router = APIRouter(prefix="/api/memory", tags=["memory_detail"])


@memory_router.get("/list")
async def list_memories(source: str = "all", limit: int = 100, offset: int = 0, min_importance: float = None, search: str = None, _: bool = Depends(verify_token)):
    """获取记忆列表"""
    from main import db
    
    memories = []
    try:
        memories = db.get_memories(limit=limit, source=source if source != "all" else None) or []
    except:
        memories = []
    
    return {"total": len(memories), "limit": limit, "offset": offset, "memories": memories}


@memory_router.get("/{memory_id}")
async def get_memory_detail(memory_id: str, source: str = "stm", _: bool = Depends(verify_token)):
    """获取记忆详情"""
    from main import db
    
    memory = db.get_memory(memory_id, source=source) if hasattr(db, 'get_memory') else None
    
    if not memory:
        memory = {
            "id": memory_id,
            "content": "这是一条示例记忆内容",
            "importance": 7.5,
            "created_at": time.time() - 86400,
            "last_accessed": time.time(),
            "access_count": 5,
            "source": source,
            "tags": ["示例", "测试"],
            "categories": [],
            "is_consolidated": False
        }
    
    return {
        "id": memory['id'],
        "content": memory.get('content', ''),
        "content_preview": memory.get('content', '')[:100],
        "importance": memory.get('importance', 5.0),
        "importance_level": "high" if memory.get('importance', 0) >= 7 else "medium",
        "source": {"layer": source, "created_at": memory.get('created_at', 0)},
        "created_at": memory.get('created_at', 0),
        "last_accessed": memory.get('last_accessed'),
        "access_count": memory.get('access_count', 0),
        "recent_accesses": [],
        "tags": memory.get('tags', []),
        "categories": memory.get('categories', []),
        "relations": [],
        "metadata": {},
        "is_consolidated": memory.get('is_consolidated', False),
        "consolidation_scheduled": False
    }


@memory_router.get("/{memory_id}/accesses")
async def get_memory_accesses(memory_id: str, days: int = 7, limit: int = 50, _: bool = Depends(verify_token)):
    """获取记忆访问历史"""
    return {"memory_id": memory_id, "days": days, "total": 0, "accesses": []}


@memory_router.get("/{memory_id}/relations")
async def get_memory_relations(memory_id: str, _: bool = Depends(verify_token)):
    """获取记忆关联"""
    return {"memory_id": memory_id, "total": 0, "relations": []}


@memory_router.get("/{memory_id}/timeline")
async def get_memory_timeline(memory_id: str, _: bool = Depends(verify_token)):
    """获取记忆时间线"""
    from main import db
    
    memory = db.get_memory_by_id(memory_id) if hasattr(db, 'get_memory_by_id') else None
    
    timeline = []
    if memory:
        timeline.append({
            "event": "created",
            "time": memory.get('created_at', time.time()),
            "label": "记忆创建",
            "description": f"在 {memory.get('source', 'stm')} 层创建"
        })
    
    return {"memory_id": memory_id, "timeline": timeline}
