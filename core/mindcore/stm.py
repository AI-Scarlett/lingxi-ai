#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短期记忆 (Short-Term Memory)

特性：
- 容量：最近 100 条对话
- 存储：内存（collections.deque）
- 过期：24 小时自动清理
- 响应：<10ms
"""

import time
from collections import deque
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid


class Memory:
    """记忆对象"""
    
    def __init__(self, content: str, importance: float = 5.0, metadata: dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.importance = importance
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count
        }
    
    def touch(self):
        """更新访问时间"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def __repr__(self):
        return f"Memory(id={self.id}, importance={self.importance}, content={self.content[:50]}...)"


class ShortTermMemory:
    """短期记忆存储"""
    
    def __init__(self, capacity: int = 100, ttl_hours: int = 24):
        self.capacity = capacity
        self.ttl_seconds = ttl_hours * 3600
        self.memories: deque[Memory] = deque(maxlen=capacity)
        self.index: Dict[str, Memory] = {}  # 快速查找
    
    async def add(self, content: str, importance: float = 5.0, metadata: dict = None) -> Memory:
        """添加记忆"""
        memory = Memory(content, importance, metadata)
        
        # 添加到队列
        self.memories.append(memory)
        self.index[memory.id] = memory
        
        # 清理过期记忆
        await self._cleanup()
        
        return memory
    
    async def get(self, memory_id: str) -> Optional[Memory]:
        """获取记忆"""
        memory = self.index.get(memory_id)
        if memory:
            memory.touch()
        return memory
    
    async def search(self, query: str, top_k: int = 10) -> List[Memory]:
        """搜索记忆（简单关键词匹配）"""
        query_lower = query.lower()
        
        # 按相关性和访问时间排序
        scored = []
        for memory in self.memories:
            score = 0
            if query_lower in memory.content.lower():
                score += 10
            # 最近访问的记忆优先
            recency_score = 1.0 / (time.time() - memory.last_accessed + 1)
            score += recency_score
            
            scored.append((score, memory))
        
        # 排序并返回 top_k
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:top_k]]
    
    async def _cleanup(self):
        """清理过期记忆"""
        now = time.time()
        expired = []
        
        for memory in list(self.memories):
            if now - memory.created_at > self.ttl_seconds:
                expired.append(memory.id)
        
        for memory_id in expired:
            if memory_id in self.index:
                del self.index[memory_id]
    
    def get_all(self) -> List[Memory]:
        """获取所有记忆"""
        return list(self.memories)
    
    def stats(self) -> dict:
        """统计信息"""
        now = time.time()
        return {
            "total": len(self.memories),
            "capacity": self.capacity,
            "oldest_age_hours": (now - self.memories[0].created_at) / 3600 if self.memories else 0,
            "newest_age_minutes": (now - self.memories[-1].created_at) / 60 if self.memories else 0
        }
