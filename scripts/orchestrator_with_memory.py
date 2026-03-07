#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - 智慧调度系统核心（增强记忆版）
心有灵犀，一点就通

多 Agent 协作架构，丝佳丽作为主控 Agent，负责任务拆解、分配、分配、汇总、评分

版本：v2.8.0
新增：完整记忆系统集成（参考 memU 框架）
"""

import json
import asyncio
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# 导入记忆系统
from .memory_service import MemoryService, MemoryItem

# ==================== 数据结构定义 ====================

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RoleType(Enum):
    COPYWRITER = "文案专家"
    IMAGE_EXPERT = "图像专家"
    CODER = "代码专家"
    DATA_ANALYST = "数据专家"
    WRITER = "写作专家"
    OPERATOR = "运营专家"
    SEARCHER = "搜索专家"
    TRANSLATOR = "翻译专家"

@dataclass
class SubTask:
    """子任务"""
    id: str
    role: RoleType
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    score: float = 0.0
    score_reason: str = ""
    error: str = ""

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    user_input: str
    subtasks: List[SubTask]
    total_score: float
    final_output: str
    created_at: datetime = field(default_factory=datetime.now)

# ==================== 角色定义 ====================

ROLE_CONFIG = {
    RoleType.COPYWRITER: {
        "name": "文案专家",
        "emoji": "📝",
        "skills": ["copywriting"],
        "model": "qwen-plus",
        "description": "负责营销文案、标题、广告语创作"
    },
    RoleType.IMAGE_EXPERT: {
        "name": "图像专家",
        "emoji": "🎨",
        "skills": ["scarlett-selfie"],
        "model": "qwen-image-max",
        "description": "负责图片生成、编辑、设计"
    },
    RoleType.CODER: {
        "name": "代码专家",
        "emoji": "💻",
        "skills": ["code-generation"],
        "model": "qwen-coder",
        "description": "负责编程、脚本、自动化"
    },
    RoleType.DATA_ANALYST: {
        "name": "数据专家",
        "emoji": "📊",
        "skills": ["data-analysis"],
        "model": "qwen-max",
        "description": "负责数据分析、报表、洞察"
    },
    RoleType.WRITER: {
        "name": "写作专家",
        "emoji": "✍️",
        "skills": ["writing"],
        "model": "qwen-plus",
        "description": "负责文章、小说、剧本创作"
    },
    RoleType.OPERATOR: {
        "name": "运营专家",
        "emoji": "📱",
        "skills": ["xiaohongshu-publisher", "weibo-poster", "douyin-poster"],
        "model": "qwen-plus",
        "description": "负责小红书、微博、抖音发布"
    },
    RoleType.SEARCHER: {
        "name": "搜索专家",
        "emoji": "🔍",
        "skills": ["multi-search-engine"],
        "model": "qwen-plus",
        "description": "负责网页搜索、信息检索 - 集成 17 个搜索引擎 (8 国内 +9 国际)"
    },
    RoleType.TRANSLATOR: {
        "name": "翻译专家",
        "emoji": "🌐",
        "skills": ["translation"],
        "model": "qwen-plus",
        "description": "负责多语言翻译"
    }
}

# ==================== 意图解析器 ====================

class IntentParser:
    """意图解析器（增强记忆版）"""
    
    def __init__(self, memory_service: MemoryService = None):
        self.memory = memory_service
        self.keyword_map = {
            "写": RoleType.WRITER,
            "文章": RoleType.WRITER,
            "文案": RoleType.COPYWRITER,
            "标题": RoleType.COPYWRITER,
            "图片": RoleType.IMAGE_EXPERT,
            "生成图片": RoleType.IMAGE_EXPERT,
            "自拍": RoleType.IMAGE_EXPERT,
            "代码": RoleType.CODER,
            "编程": RoleType.CODER,
            "脚本": RoleType.CODER,
            "数据": RoleType.DATA_ANALYST,
            "分析": RoleType.DATA_ANALYST,
            "发布": RoleType.OPERATOR,
            "小红书": RoleType.OPERATOR,
            "搜索": RoleType.SEARCHER,
            "查": RoleType.SEARCHER,
            "翻译": RoleType.TRANSLATOR,
        }
    
    async def parse(self, user_input: str, context: Dict = None) -> Dict:
        """
        解析用户意图
        
        Args:
            user_input: 用户输入
            context: 主动加载的记忆上下文
        
        Returns:
            意图解析结果
        """
        
        # 如果有记忆上下文，优先使用
        if context and self.memory:
            # 检查是否有相关偏好
            prefs = await self.memory.retrieve("用户偏好", method="keyword", category="preferences", top_k=3)
            if prefs.get("items"):
                # 根据偏好调整解析策略
                pass
        
        # 关键词匹配
        for keyword, role in self.keyword_map.items():
            if keyword in user_input:
                return {
                    "intent": "execute_task",
                    "role": role,
                    "confidence": 0.8,
                    "input": user_input
                }
        
        # 默认：聊天意图
        return {
            "intent": "chat",
            "role": None,
            "confidence": 0.9,
            "input": user_input
        }

# ==================== 主编排器 ====================

class LingxiOrchestrator:
    """
    灵犀主编排器（增强记忆版）
    
    集成 memU 风格的记忆系统，实现：
    - 主动上下文加载
    - 对话自动记忆
    - 个性化响应
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.memory = MemoryService(llm_client)
        self.parser = IntentParser(self.memory)
        self._initialized = False
    
    async def initialize(self):
        """初始化"""
        if not self._initialized:
            await self.memory.initialize()
            self._initialized = True
    
    async def execute(self, user_input: str, user_id: str = "default", 
                      session_id: str = None) -> Dict:
        """
        执行用户请求（增强记忆版）
        
        Args:
            user_input: 用户输入
            user_id: 用户 ID
            session_id: 会话 ID
        
        Returns:
            执行结果
        """
        await self.initialize()
        
        # 1. 主动加载记忆上下文（毫秒级）
        context = await self.memory.get_context(user_id)
        
        # 2. 解析意图（使用上下文）
        intent = await self.parser.parse(user_input, context)
        
        # 3. 生成会话 ID
        if not session_id:
            session_id = hashlib.md5(f"{user_id}-{time.time()}".encode()).hexdigest()[:12]
        
        # 4. 执行任务
        if intent["intent"] == "chat":
            result = await self._handle_chat(user_input, context)
        else:
            result = await self._handle_task(intent, context)
        
        # 5. 后台记录对话（异步，不阻塞响应）
        conversation = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": result.get("output", "")}
        ]
        asyncio.create_task(self._record_interaction(session_id, conversation, user_id))
        
        return {
            "session_id": session_id,
            "intent": intent,
            "output": result.get("output", ""),
            "context_loaded": context.get("total_memories", 0),
            "memory_stats": await self.memory.get_stats()
        }
    
    async def _handle_chat(self, user_input: str, context: Dict) -> Dict:
        """处理聊天请求"""
        
        # 构建提示词（包含记忆上下文）
        prompt = self._build_chat_prompt(user_input, context)
        
        # 调用 LLM
        if self.llm:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
        else:
            response = f"[聊天回复] 收到：{user_input}"
        
        return {"output": response}
    
    async def _handle_task(self, intent: Dict, context: Dict) -> Dict:
        """处理任务请求"""
        
        role = intent.get("role")
        if not role:
            return {"output": "无法识别任务类型"}
        
        # 获取角色配置
        role_config = ROLE_CONFIG.get(role, {})
        
        # 构建任务提示词
        prompt = f"""
你是{role_config.get('name', '专家')}。

{role_config.get('description', '')}

用户请求：{intent.get('input', '')}

请直接提供专业、高质量的回答。
"""
        
        # 调用 LLM
        if self.llm:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
        else:
            response = f"[{role_config.get('name', '专家')}] 任务执行中..."
        
        return {"output": response}
    
    def _build_chat_prompt(self, user_input: str, context: Dict) -> str:
        """构建聊天提示词（包含记忆上下文）"""
        
        prompt_parts = ["你是一个智能助手。"]
        
        # 添加记忆上下文
        recent = context.get("recent_context", [])
        if recent:
            prompt_parts.append("\n已知用户信息：")
            for item in recent[:5]:  # 最多 5 条
                prompt_parts.append(f"- {item.get('content', '')}")
        
        prompt_parts.append(f"\n用户：{user_input}")
        prompt_parts.append("\n助手：")
        
        return "".join(prompt_parts)
    
    async def _record_interaction(self, session_id: str, conversation: List[Dict], user_id: str):
        """记录交互到记忆系统（后台异步）"""
        try:
            await self.memory.memorize(conversation, session_id)
        except Exception as e:
            print(f"记忆记录失败：{e}")
    
    async def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        await self.initialize()
        return await self.memory.get_stats()
    
    async def search_memory(self, query: str, method: str = "keyword") -> Dict:
        """搜索记忆"""
        await self.initialize()
        return await self.memory.retrieve(query, method)


# ==================== 便捷函数 ====================

async def execute(user_input: str, user_id: str = "default", llm_client=None) -> Dict:
    """便捷函数：执行用户请求"""
    orchestrator = LingxiOrchestrator(llm_client)
    return await orchestrator.execute(user_input, user_id)


async def get_memory_stats(llm_client=None) -> Dict:
    """便捷函数：获取记忆统计"""
    orchestrator = LingxiOrchestrator(llm_client)
    return await orchestrator.get_memory_stats()


async def search_memory(query: str, llm_client=None) -> Dict:
    """便捷函数：搜索记忆"""
    orchestrator = LingxiOrchestrator(llm_client)
    return await orchestrator.search_memory(query)
