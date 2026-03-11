#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 基类

所有专用 Agent 的抽象基类
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
import uuid


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, agent_id: str, channel: str):
        self.agent_id = agent_id
        self.channel = channel
        self.workspace = Path(f"/root/.openclaw/agents/{agent_id}")
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Dict] = {}
        self.created_at = time.time()
        self.last_active = time.time()
        self.task_count = 0
    
    @abstractmethod
    async def handle(self, task: Dict) -> Dict:
        """
        处理任务（子类必须实现）
        
        Args:
            task: 任务字典 {"id": str, "content": str, "type": str, ...}
        
        Returns:
            处理结果 {"success": bool, "result": Any, "error": str}
        """
        pass
    
    async def initialize(self):
        """初始化 Agent（可选重写）"""
        pass
    
    async def cleanup(self):
        """清理资源（可选重写）"""
        pass
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def create_session(self, session_id: str = None) -> str:
        """创建会话"""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": time.time(),
            "last_active": time.time(),
            "message_count": 0,
            "context": []
        }
        
        return session_id
    
    def update_session(self, session_id: str, message: Dict):
        """更新会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["last_active"] = time.time()
            session["message_count"] += 1
            session["context"].append(message)
            
            # 限制上下文长度（最近 100 条）
            if len(session["context"]) > 100:
                session["context"] = session["context"][-100:]
    
    def get_stats(self) -> dict:
        """获取 Agent 统计信息"""
        return {
            "agent_id": self.agent_id,
            "channel": self.channel,
            "task_count": self.task_count,
            "active_sessions": len(self.sessions),
            "uptime_hours": (time.time() - self.created_at) / 3600,
            "last_active": self.last_active
        }


class AgentRegistry:
    """Agent 注册表"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """注册 Agent"""
        self.agents[agent.agent_id] = agent
    
    def unregister(self, agent_id: str):
        """注销 Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(agent_id)
    
    def get_by_channel(self, channel: str) -> List[BaseAgent]:
        """按渠道获取 Agent"""
        return [a for a in self.agents.values() if a.channel == channel]
    
    def get_all(self) -> List[BaseAgent]:
        """获取所有 Agent"""
        return list(self.agents.values())
    
    def get_stats(self) -> dict:
        """获取注册表统计"""
        return {
            "total_agents": len(self.agents),
            "channels": list(set(a.channel for a in self.agents.values())),
            "agents_by_channel": {
                channel: len(self.get_by_channel(channel))
                for channel in set(a.channel for a in self.agents.values())
            }
        }


# 全局注册表
_registry = None


def get_registry() -> AgentRegistry:
    """获取注册表实例"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
