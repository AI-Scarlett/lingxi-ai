#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书专用 Agent
"""

import asyncio
from typing import Dict, Any
from .base import BaseAgent


class FeishuAgent(BaseAgent):
    """飞书专用 Agent"""
    
    def __init__(self):
        super().__init__("feishu_agent", "feishu")
        self.api_base = "https://open.feishu.cn/open-apis"
        self.tenant_access_token = None
    
    async def initialize(self):
        """初始化飞书 Agent"""
        # TODO: 获取 tenant_access_token
        pass
    
    async def handle(self, task: Dict) -> Dict:
        """处理飞书任务"""
        self.task_count += 1
        self.last_active = time.time()
        
        try:
            # 飞书特定逻辑
            task_type = task.get("type", "message")
            
            if task_type == "message":
                return await self._handle_message(task)
            elif task_type == "reminder":
                return await self._handle_reminder(task)
            else:
                return await self._handle_default(task)
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_message(self, task: Dict) -> Dict:
        """处理消息任务"""
        content = task.get("content", "")
        session_id = task.get("session_id")
        
        # 更新会话
        if session_id:
            self.update_session(session_id, {"role": "user", "content": content})
        
        # 调用灵犀主流程处理
        # TODO: 集成 orchestrator
        
        return {
            "success": True,
            "result": "消息已处理",
            "agent_id": self.agent_id
        }
    
    async def _handle_reminder(self, task: Dict) -> Dict:
        """处理提醒任务"""
        reminder_text = task.get("text", "")
        target_user = task.get("user_id")
        
        # 发送飞书提醒
        # TODO: 调用飞书 API
        
        return {
            "success": True,
            "result": f"提醒已发送给 {target_user}",
            "agent_id": self.agent_id
        }
    
    async def _handle_default(self, task: Dict) -> Dict:
        """默认处理"""
        return {
            "success": True,
            "result": "任务已处理",
            "agent_id": self.agent_id
        }


# 单例
_agent = None


def get_feishu_agent() -> FeishuAgent:
    """获取飞书 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = FeishuAgent()
    return _agent
