#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 MindCore 记忆核心系统

核心架构：
- STM (Short-Term Memory) - 短期记忆：最近 100 条对话，内存存储，<10ms
- MTM (Mid-Term Memory) - 中期记忆：最近 7 天，SQLite 存储，<500ms
- LTM (Long-Term Memory) - 长期记忆：永久归档，JSONL+ 向量索引，<2s

版本：v3.3.3
创建时间：2026-03-11
"""

from .stm import ShortTermMemory
from .mtm import MidTermMemory
from .ltm import LongTermMemory
from .extractor import MemoryExtractor
from .compressor import MemoryCompressor
from .retriever import HybridRetriever
from .lifecycle import MemoryLifecycleManager


class MindCore:
    """灵犀记忆核心系统"""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/.lingxi/mindcore.db"):
        self.stm = ShortTermMemory(capacity=100)
        self.mtm = MidTermMemory(db_path)
        self.ltm = LongTermMemory(db_path)
        self.extractor = MemoryExtractor()
        self.compressor = MemoryCompressor()
        self.retriever = HybridRetriever()
        self.lifecycle = MemoryLifecycleManager()
    
    async def save(self, content: str, importance: float = 5.0, metadata: dict = None):
        """保存记忆"""
        # 先保存到 STM
        memory = await self.stm.add(content, importance, metadata)
        
        # 如果重要性高，同时保存到 MTM
        if importance >= 7.0:
            await self.mtm.add(content, importance, metadata)
        
        # 如果重要性非常高，同时保存到 LTM
        if importance >= 9.0:
            await self.ltm.add(content, importance, metadata)
        
        return memory
    
    async def retrieve(self, query: str, top_k: int = 10):
        """检索记忆"""
        return await self.retriever.retrieve(query, top_k)
    
    async def run_improvement_cycle(self):
        """运行改进周期"""
        return await self.lifecycle.process()


# 全局实例
_mindcore_instance = None


def get_mindcore() -> MindCore:
    """获取 MindCore 实例"""
    global _mindcore_instance
    if _mindcore_instance is None:
        _mindcore_instance = MindCore()
    return _mindcore_instance
