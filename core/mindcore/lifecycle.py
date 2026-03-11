#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆生命周期管理 (Memory Lifecycle Manager)

功能：
- 分析记忆使用模式
- 记忆升降级（STM ↔ MTM ↔ LTM）
- 定期清理和归档
"""

import time
from typing import Dict, List, Optional
from datetime import datetime


class MemoryLifecycleManager:
    """记忆生命周期管理"""
    
    def __init__(self):
        self.promote_threshold_days = 7  # MTM 提升为 LTM 的天数
        self.demote_threshold_days = 30  # LTM 降级为归档的天数
        self.cleanup_threshold_days = 90  # 归档清理的天数
    
    async def process(self, stm=None, mtm=None, ltm=None) -> dict:
        """
        处理记忆生命周期
        
        Args:
            stm: STM 实例
            mtm: MTM 实例
            ltm: LTM 实例
        
        Returns:
            处理报告
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "promoted": [],
            "demoted": [],
            "archived": [],
            "cleaned": []
        }
        
        # 1. 分析使用模式
        patterns = await self._analyze_patterns(mtm, ltm)
        
        # 2. 提升频繁访问的记忆（MTM → LTM）
        if mtm and ltm:
            for memory in patterns.get("frequently_accessed", []):
                if memory.get("_source") == "mtm":
                    await self._promote_to_ltm(memory, mtm, ltm)
                    report["promoted"].append(memory["id"])
        
        # 3. 降级长期未访问的记忆（LTM → 归档）
        if ltm:
            for memory in patterns.get("rarely_accessed", []):
                if memory.get("_source") == "ltm":
                    days_since_access = (time.time() - memory.get("last_accessed", 0)) / 86400
                    if days_since_access > self.demote_threshold_days:
                        await self._demote_to_archive(memory, ltm)
                        report["demoted"].append(memory["id"])
        
        # 4. 清理归档记忆
        if ltm:
            for memory in patterns.get("never_accessed", []):
                if memory.get("_source") == "ltm":
                    days_since_creation = (time.time() - memory.get("created_at", 0)) / 86400
                    if days_since_creation > self.cleanup_threshold_days:
                        await self._archive(memory, ltm)
                        report["archived"].append(memory["id"])
        
        return report
    
    async def _analyze_patterns(self, mtm, ltm) -> dict:
        """分析记忆使用模式"""
        patterns = {
            "frequently_accessed": [],
            "rarely_accessed": [],
            "never_accessed": []
        }
        
        # 分析 MTM
        if mtm:
            stats = mtm.stats()
            # 获取频繁访问的记忆（简化实现）
            recent = await mtm.get_recent(days=7, limit=100)
            for memory in recent:
                if memory.get("access_count", 0) >= 10:
                    memory["_source"] = "mtm"
                    patterns["frequently_accessed"].append(memory)
        
        # 分析 LTM
        if ltm:
            stats = ltm.stats()
            # 获取高重要性记忆
            high_importance = await ltm.get_by_importance(min_importance=8.0, limit=100)
            for memory in high_importance:
                memory["_source"] = "ltm"
                if memory.get("access_count", 0) >= 5:
                    patterns["frequently_accessed"].append(memory)
                elif memory.get("access_count", 0) >= 1:
                    patterns["rarely_accessed"].append(memory)
                else:
                    patterns["never_accessed"].append(memory)
        
        return patterns
    
    async def _promote_to_ltm(self, memory: dict, mtm, ltm):
        """提升到 LTM"""
        # 添加到 LTM
        await ltm.add(
            content=memory["content"],
            importance=memory.get("importance", 8.0),
            metadata={
                "promoted_from": "mtm",
                "original_id": memory["id"],
                "access_count": memory.get("access_count", 0)
            }
        )
        
        # 从 MTM 删除
        await mtm.delete(memory["id"])
    
    async def _demote_to_archive(self, memory: dict, ltm):
        """降级到归档"""
        # 更新元数据
        await ltm.update(
            memory["id"],
            metadata={"archived": True, "demoted_at": time.time()}
        )
    
    async def _archive(self, memory: dict, ltm):
        """归档记忆"""
        # 从 LTM 删除（实际归档到冷存储）
        await ltm.delete(memory["id"])
    
    def get_lifecycle_report(self) -> dict:
        """获取生命周期报告模板"""
        return {
            "total_processed": 0,
            "promoted_to_ltm": 0,
            "demoted_to_archive": 0,
            "archived": 0,
            "timestamp": datetime.now().isoformat()
        }
