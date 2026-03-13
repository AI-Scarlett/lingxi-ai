#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话详情页 API

功能：
- 查看会话的完整对话历史
- 会话统计信息
- 消息详情
- 工具调用追踪
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import json
from pathlib import Path

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class MessageDetail(BaseModel):
    """消息详情"""
    id: str
    role: str  # user, assistant, system
    content: str
    timestamp: float
    tool_calls: Optional[List[Dict]] = None
    tool_responses: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None


class SessionStat(BaseModel):
    """会话统计"""
    total_messages: int
    user_messages: int
    assistant_messages: int
    tool_calls: int
    total_tokens: int
    total_cost: float
    duration_seconds: float
    avg_response_time_ms: float


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    # 基本信息
    id: str
    session_key: str
    label: Optional[str]
    
    # 状态
    status: str  # active, completed, archived
    is_active: bool
    
    # 时间
    created_at: float
    updated_at: float
    last_message_at: Optional[float]
    
    # 参与者
    user_id: str
    agent_id: str
    channel: str
    
    # 模型信息
    model: str
    thinking_enabled: bool
    
    # 统计
    stats: SessionStat
    
    # 消息历史
    messages: List[MessageDetail]
    
    # 工具调用
    tool_calls: List[Dict]
    
    # 关联
    parent_session: Optional[str]
    sub_sessions: List[str]


@router.get("/list")
async def list_sessions(
    status: str = Query("all", description="状态筛选：all/active/archived"),
    limit: int = Query(50, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    include_stats: bool = Query(True, description="是否包含统计")
):
    """获取会话列表"""
    from ..database import db
    
    sessions = db.get_sessions(
        status=status if status != "all" else None,
        limit=limit,
        offset=offset
    )
    
    result = []
    for session in sessions:
        session_info = {
            "id": session['id'],
            "session_key": session['session_key'],
            "label": session.get('label'),
            "status": session.get('status', 'active'),
            "is_active": session.get('is_active', False),
            "created_at": session.get('created_at', 0),
            "updated_at": session.get('updated_at', 0),
            "user_id": session.get('user_id', ''),
            "agent_id": session.get('agent_id', 'main'),
            "channel": session.get('channel', 'unknown')
        }
        
        if include_stats:
            session_info['stats'] = get_session_stats(session['id'])
        
        result.append(session_info)
    
    return {
        "total": len(sessions),
        "limit": limit,
        "offset": offset,
        "sessions": result
    }


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    include_messages: bool = Query(True, description="是否包含消息历史"),
    message_limit: int = Query(100, description="消息数量限制")
):
    """获取会话详情"""
    from ..database import db
    
    # 获取会话基本信息
    session = db.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 获取统计
    stats = get_session_stats(session_id)
    
    # 获取消息历史
    messages = []
    if include_messages:
        messages = get_session_messages(session_id, limit=message_limit)
    
    # 获取工具调用
    tool_calls = get_session_tool_calls(session_id)
    
    # 获取关联会话
    sub_sessions = db.get_sub_sessions(session_id)
    
    return SessionDetailResponse(
        id=session['id'],
        session_key=session['session_key'],
        label=session.get('label'),
        status=session.get('status', 'active'),
        is_active=session.get('is_active', False),
        created_at=session.get('created_at', 0),
        updated_at=session.get('updated_at', 0),
        last_message_at=session.get('last_message_at'),
        user_id=session.get('user_id', ''),
        agent_id=session.get('agent_id', 'main'),
        channel=session.get('channel', 'unknown'),
        model=session.get('model', 'qwencode/qwen3.5-plus'),
        thinking_enabled=session.get('thinking_enabled', False),
        stats=stats,
        messages=messages,
        tool_calls=tool_calls,
        parent_session=session.get('parent_session'),
        sub_sessions=sub_sessions
    )


@router.get("/{session_id}/messages")
async def get_session_messages_api(
    session_id: str,
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    role: Optional[str] = Query(None, description="按角色筛选：user/assistant")
):
    """获取会话消息列表"""
    from ..database import db
    
    messages = db.get_session_messages(session_id, limit=limit, offset=offset, role=role)
    
    return {
        "session_id": session_id,
        "total": len(messages),
        "limit": limit,
        "offset": offset,
        "messages": messages
    }


@router.get("/{session_id}/tools")
async def get_session_tools(session_id: str):
    """获取会话中的工具调用"""
    from ..database import db
    
    tool_calls = db.get_session_tool_calls(session_id)
    
    # 按工具类型分组统计
    tool_stats = {}
    for call in tool_calls:
        tool_name = call.get('tool', 'unknown')
        if tool_name not in tool_stats:
            tool_stats[tool_name] = {
                "count": 0,
                "success": 0,
                "failed": 0
            }
        tool_stats[tool_name]["count"] += 1
        if call.get('success', True):
            tool_stats[tool_name]["success"] += 1
        else:
            tool_stats[tool_name]["failed"] += 1
    
    return {
        "session_id": session_id,
        "total_calls": len(tool_calls),
        "tool_calls": tool_calls,
        "stats": tool_stats
    }


@router.get("/{session_id}/stats")
async def get_session_stats_detail(session_id: str):
    """获取会话详细统计"""
    from ..database import db
    
    stats = get_session_stats(session_id)
    
    # 获取按时间分布的消息数
    hourly_distribution = db.get_session_hourly_distribution(session_id)
    
    # 获取工具使用统计
    tool_usage = db.get_session_tool_usage(session_id)
    
    # 获取 Token 使用详情
    token_usage = db.get_session_token_usage(session_id)
    
    return {
        "session_id": session_id,
        "overview": stats,
        "hourly": hourly_distribution,
        "tools": tool_usage,
        "tokens": token_usage
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    from ..database import db
    
    db.delete_session(session_id)
    
    return {"success": True, "deleted_session": session_id}


@router.post("/{session_id}/archive")
async def archive_session(session_id: str):
    """归档会话"""
    from ..database import db
    
    db.archive_session(session_id)
    
    return {"success": True, "archived_session": session_id}


def get_session_stats(session_id: str) -> SessionStat:
    """获取会话统计"""
    from ..database import db
    
    stats = db.get_session_stats(session_id)
    
    if not stats:
        return SessionStat(
            total_messages=0,
            user_messages=0,
            assistant_messages=0,
            tool_calls=0,
            total_tokens=0,
            total_cost=0,
            duration_seconds=0,
            avg_response_time_ms=0
        )
    
    return SessionStat(
        total_messages=stats.get('total_messages', 0),
        user_messages=stats.get('user_messages', 0),
        assistant_messages=stats.get('assistant_messages', 0),
        tool_calls=stats.get('tool_calls', 0),
        total_tokens=stats.get('total_tokens', 0),
        total_cost=stats.get('total_cost', 0),
        duration_seconds=stats.get('duration_seconds', 0),
        avg_response_time_ms=stats.get('avg_response_time_ms', 0)
    )


def get_session_messages(session_id: str, limit: int = 100) -> List[MessageDetail]:
    """获取会话消息"""
    from ..database import db
    
    messages_raw = db.get_session_messages(session_id, limit=limit)
    
    messages = []
    for msg in messages_raw:
        # 解析工具调用
        tool_calls = None
        tool_responses = None
        
        if msg.get('tool_calls'):
            try:
                tool_calls = json.loads(msg['tool_calls']) if isinstance(msg['tool_calls'], str) else msg['tool_calls']
            except Exception:
                pass
        
        if msg.get('tool_responses'):
            try:
                tool_responses = json.loads(msg['tool_responses']) if isinstance(msg['tool_responses'], str) else msg['tool_responses']
            except Exception:
                pass
        
        messages.append(MessageDetail(
            id=msg.get('id', ''),
            role=msg.get('role', 'assistant'),
            content=msg.get('content', ''),
            timestamp=msg.get('timestamp', 0),
            tool_calls=tool_calls,
            tool_responses=tool_responses,
            metadata=msg.get('metadata')
        ))
    
    return messages


def get_session_tool_calls(session_id: str) -> List[Dict]:
    """获取会话工具调用"""
    from ..database import db
    
    return db.get_session_tool_calls(session_id)
