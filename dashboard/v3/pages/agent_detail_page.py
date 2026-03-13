#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 详情页 API

功能：
- 查看 Agent 的详细信息
- Agent 状态监控
- Agent 能力列表
- Agent 调用统计
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import os
from pathlib import Path

router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentCapability(BaseModel):
    """Agent 能力"""
    name: str
    description: str
    enabled: bool
    tools: List[str]


class AgentHealth(BaseModel):
    """Agent 健康状态"""
    status: str  # healthy, warning, error, offline
    last_seen: Optional[float]
    uptime_seconds: Optional[float]
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate: float
    avg_response_time_ms: float


class AgentStat(BaseModel):
    """Agent 统计"""
    total_tasks: int
    success_rate: float
    avg_execution_time_ms: float
    total_tokens: int
    total_cost: float
    today_tasks: int
    week_tasks: int
    active_sessions: int


class AgentDetailResponse(BaseModel):
    """Agent 详情响应"""
    # 基本信息
    id: str
    name: str
    display_name: str
    description: str
    version: str
    
    # 类型
    agent_type: str  # main, subagent, acp, external
    
    # 状态
    status: str  # active, idle, busy, offline
    health: AgentHealth
    
    # 能力
    capabilities: List[AgentCapability]
    tools: List[str]
    skills: List[str]
    
    # 配置
    model: str
    thinking_enabled: bool
    max_context_length: int
    timeout_seconds: int
    
    # 统计
    stats: AgentStat
    
    # 会话
    active_sessions: List[Dict]
    recent_tasks: List[Dict]
    
    # 环境
    environment: Dict[str, Any]
    workspace: str


@router.get("/list")
async def list_agents(
    include_stats: bool = Query(True, description="是否包含统计信息"),
    include_health: bool = Query(True, description="是否包含健康状态")
):
    """获取 Agent 列表"""
    from ..database import db
    
    agents = []
    
    # 主 Agent
    main_agent = {
        "id": "main",
        "name": "main",
        "display_name": "主 Agent",
        "description": "主要的对话 Agent",
        "type": "main",
        "status": "active"
    }
    
    if include_stats:
        main_agent['stats'] = get_agent_stats("main")
    
    if include_health:
        main_agent['health'] = get_agent_health("main")
    
    agents.append(main_agent)
    
    # 查询子 Agent
    subagents = get_subagents_from_db()
    for subagent in subagents:
        agent_info = {
            "id": subagent['id'],
            "name": subagent['name'],
            "display_name": subagent.get('display_name', subagent['name']),
            "description": subagent.get('description', ''),
            "type": subagent.get('type', 'subagent'),
            "status": subagent.get('status', 'unknown')
        }
        
        if include_stats:
            agent_info['stats'] = get_agent_stats(subagent['id'])
        
        if include_health:
            agent_info['health'] = get_agent_health(subagent['id'])
        
        agents.append(agent_info)
    
    return {"total": len(agents), "agents": agents}


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent_detail(agent_id: str):
    """获取 Agent 详情"""
    from ..database import db
    
    # 获取 Agent 基本信息
    if agent_id == "main":
        agent_info = {
            "id": "main",
            "name": "main",
            "display_name": "主 Agent",
            "description": "主要的对话 Agent，处理所有用户请求",
            "version": "3.3.6",
            "agent_type": "main"
        }
    else:
        # 从数据库查询子 Agent
        agent_data = db.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent 不存在")
        
        agent_info = {
            "id": agent_data['id'],
            "name": agent_data['name'],
            "display_name": agent_data.get('display_name', agent_data['name']),
            "description": agent_data.get('description', ''),
            "version": agent_data.get('version', '1.0.0'),
            "agent_type": agent_data.get('type', 'subagent')
        }
    
    # 获取健康状态
    health = get_agent_health(agent_id)
    
    # 获取能力列表
    capabilities = get_agent_capabilities(agent_id)
    
    # 获取工具列表
    tools = get_agent_tools(agent_id)
    
    # 获取技能列表
    skills = get_agent_skills(agent_id)
    
    # 获取配置
    config = get_agent_config(agent_id)
    
    # 获取统计
    stats = get_agent_stats(agent_id)
    
    # 获取活跃会话
    active_sessions = get_agent_active_sessions(agent_id)
    
    # 获取最近任务
    recent_tasks = get_agent_recent_tasks(agent_id)
    
    # 环境信息
    environment = {
        "python_version": "3.10+",
        "platform": "Linux",
        "workspace": str(Path.home() / ".openclaw" / "workspace")
    }
    
    return AgentDetailResponse(
        id=agent_info['id'],
        name=agent_info['name'],
        display_name=agent_info['display_name'],
        description=agent_info['description'],
        version=agent_info['version'],
        agent_type=agent_info['agent_type'],
        status=health.status,
        health=health,
        capabilities=capabilities,
        tools=tools,
        skills=skills,
        model=config['model'],
        thinking_enabled=config['thinking_enabled'],
        max_context_length=config['max_context_length'],
        timeout_seconds=config['timeout_seconds'],
        stats=stats,
        active_sessions=active_sessions,
        recent_tasks=recent_tasks,
        environment=environment,
        workspace=environment['workspace']
    )


@router.get("/{agent_id}/sessions")
async def get_agent_sessions(agent_id: str, limit: int = Query(20, description="返回数量限制")):
    """获取 Agent 的会话列表"""
    from ..database import db
    
    sessions = db.get_agent_sessions(agent_id, limit=limit)
    
    return {
        "agent_id": agent_id,
        "total": len(sessions),
        "sessions": sessions
    }


@router.get("/{agent_id}/tasks")
async def get_agent_tasks(
    agent_id: str,
    days: int = Query(7, description="查询天数"),
    limit: int = Query(50, description="返回数量限制"),
    status: Optional[str] = Query(None, description="按状态筛选")
):
    """获取 Agent 的任务列表"""
    from ..database import db
    
    tasks = db.get_agent_tasks(agent_id, days=days, limit=limit, status=status)
    
    return {
        "agent_id": agent_id,
        "days": days,
        "total": len(tasks),
        "tasks": tasks
    }


@router.get("/{agent_id}/health")
async def get_agent_health_detail(agent_id: str):
    """获取 Agent 详细健康状态"""
    from ..database import db
    
    health = get_agent_health(agent_id)
    
    # 获取历史健康数据
    health_history = db.get_agent_health_history(agent_id, hours=24)
    
    # 获取性能指标
    metrics = db.get_agent_metrics(agent_id, hours=24)
    
    return {
        "agent_id": agent_id,
        "current": health,
        "history": health_history,
        "metrics": metrics
    }


def get_subagents_from_db() -> List[Dict]:
    """从数据库获取子 Agent 列表"""
    from ..database import db
    
    # 查询最近的子 Agent 记录
    subagents = db.get_recent_subagents(limit=50)
    return subagents


def get_agent_stats(agent_id: str) -> AgentStat:
    """获取 Agent 统计信息"""
    from ..database import db
    
    stats = db.get_agent_stats(agent_id)
    
    if not stats:
        return AgentStat(
            total_tasks=0,
            success_rate=100.0,
            avg_execution_time_ms=0,
            total_tokens=0,
            total_cost=0,
            today_tasks=0,
            week_tasks=0,
            active_sessions=0
        )
    
    return AgentStat(
        total_tasks=stats.get('total_tasks', 0),
        success_rate=stats.get('success_rate', 100.0),
        avg_execution_time_ms=stats.get('avg_execution_time_ms', 0),
        total_tokens=stats.get('total_tokens', 0),
        total_cost=stats.get('total_cost', 0),
        today_tasks=stats.get('today_tasks', 0),
        week_tasks=stats.get('week_tasks', 0),
        active_sessions=stats.get('active_sessions', 0)
    )


def get_agent_health(agent_id: str) -> AgentHealth:
    """获取 Agent 健康状态"""
    from ..database import db
    
    # 检查 Agent 是否活跃
    last_seen = db.get_agent_last_seen(agent_id)
    
    now = time.time()
    if not last_seen:
        status = "offline"
        uptime = None
    elif now - last_seen < 60:
        status = "healthy"
        uptime = now - last_seen
    elif now - last_seen < 300:
        status = "warning"
        uptime = now - last_seen
    else:
        status = "error"
        uptime = now - last_seen
    
    # 获取性能指标
    metrics = db.get_agent_recent_metrics(agent_id)
    
    return AgentHealth(
        status=status,
        last_seen=last_seen,
        uptime_seconds=uptime,
        memory_usage_mb=metrics.get('memory_mb', 0),
        cpu_usage_percent=metrics.get('cpu_percent', 0),
        error_rate=metrics.get('error_rate', 0),
        avg_response_time_ms=metrics.get('avg_response_ms', 0)
    )


def get_agent_capabilities(agent_id: str) -> List[AgentCapability]:
    """获取 Agent 能力列表"""
    # 根据 Agent 类型返回不同的能力
    if agent_id == "main":
        return [
            AgentCapability(
                name="conversation",
                description="自然语言对话",
                enabled=True,
                tools=["message", "browser", "exec"]
            ),
            AgentCapability(
                name="task_execution",
                description="任务执行和分解",
                enabled=True,
                tools=["sessions_spawn", "subagents"]
            ),
            AgentCapability(
                name="file_operations",
                description="文件读写和管理",
                enabled=True,
                tools=["read", "write", "edit"]
            ),
            AgentCapability(
                name="web_access",
                description="网络搜索和浏览",
                enabled=True,
                tools=["web_search", "web_fetch", "browser"]
            ),
            AgentCapability(
                name="feishu_integration",
                description="飞书集成",
                enabled=True,
                tools=["feishu_doc", "feishu_bitable", "feishu_chat"]
            )
        ]
    
    return [
        AgentCapability(
            name="specialized_task",
            description="专用任务处理",
            enabled=True,
            tools=[]
        )
    ]


def get_agent_tools(agent_id: str) -> List[str]:
    """获取 Agent 可用工具列表"""
    return [
        "read", "write", "edit", "exec", "process",
        "web_search", "web_fetch", "browser",
        "message", "sessions_spawn", "sessions_send", "subagents",
        "feishu_doc", "feishu_bitable", "feishu_chat", "feishu_drive",
        "memory_search", "memory_get", "session_status"
    ]


def get_agent_skills(agent_id: str) -> List[str]:
    """获取 Agent 已加载技能"""
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    
    skills = []
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
                skills.append(skill_folder.name)
    
    return skills


def get_agent_config(agent_id: str) -> Dict:
    """获取 Agent 配置"""
    return {
        "model": "qwencode/qwen3.5-plus",
        "thinking_enabled": False,
        "max_context_length": 128000,
        "timeout_seconds": 300
    }


def get_agent_active_sessions(agent_id: str) -> List[Dict]:
    """获取 Agent 活跃会话"""
    from ..database import db
    
    sessions = db.get_agent_active_sessions(agent_id, limit=10)
    return sessions


def get_agent_recent_tasks(agent_id: str) -> List[Dict]:
    """获取 Agent 最近任务"""
    from ..database import db
    
    tasks = db.get_agent_recent_tasks(agent_id, limit=10)
    return tasks
