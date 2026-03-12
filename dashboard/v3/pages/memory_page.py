#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard 记忆管理页

功能：
- 查看记忆列表
- 搜索记忆
- 编辑/删除记忆
- 记忆统计
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryItem(BaseModel):
    """记忆项"""
    id: str
    content: str
    importance: float
    created_at: float
    last_accessed: Optional[float] = None
    access_count: int = 0
    tags: List[str] = []
    source: str = "unknown"


class MemoryListResponse(BaseModel):
    """记忆列表响应"""
    total: int
    memories: List[MemoryItem]
    stats: Dict


@router.get("/list")
async def list_memories(
    source: str = "all",
    limit: int = 100,
    offset: int = 0
):
    """获取记忆列表"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    memories = []
    
    # 从各层获取记忆
    if source in ["all", "stm"]:
        for m in mindcore.stm.get_all()[:limit]:
            memories.append(MemoryItem(
                id=m.id,
                content=m.content,
                importance=m.importance,
                created_at=m.created_at,
                last_accessed=m.last_accessed,
                access_count=m.access_count,
                source="stm"
            ))
    
    if source in ["all", "mtm"]:
        mtm_memories = await mindcore.mtm.get_recent(days=7, limit=limit)
        for m in mtm_memories:
            memories.append(MemoryItem(
                id=m["id"],
                content=m["content"],
                importance=m["importance"],
                created_at=m["created_at"],
                last_accessed=m["last_accessed"],
                access_count=m["access_count"],
                tags=[],
                source="mtm"
            ))
    
    if source in ["all", "ltm"]:
        ltm_memories = await mindcore.ltm.get_by_importance(min_importance=8.0, limit=limit)
        for m in ltm_memories:
            memories.append(MemoryItem(
                id=m["id"],
                content=m["content"],
                importance=m["importance"],
                created_at=m["created_at"],
                last_accessed=m["last_accessed"],
                access_count=m["access_count"],
                tags=[],
                source="ltm"
            ))
    
    # 分页
    paginated = memories[offset:offset+limit]
    
    return {
        "total": len(memories),
        "memories": paginated,
        "stats": {
            "stm": mindcore.stm.stats(),
            "mtm": mindcore.mtm.stats(),
            "ltm": mindcore.ltm.stats()
        }
    }


@router.get("/search")
async def search_memories(query: str, top_k: int = 10):
    """搜索记忆"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    # 从各层搜索
    stm_results = await mindcore.stm.search(query, top_k=top_k)
    mtm_results = await mindcore.mtm.search(query, top_k=top_k)
    ltm_results = await mindcore.ltm.search(query, top_k=top_k)
    
    # 合并结果
    all_results = []
    for m in stm_results:
        all_results.append({
            "id": m.id,
            "content": m.content,
            "importance": m.importance,
            "source": "stm"
        })
    
    for m in mtm_results:
        all_results.append({
            "id": m["id"],
            "content": m["content"],
            "importance": m["importance"],
            "source": "mtm"
        })
    
    for m in ltm_results:
        all_results.append({
            "id": m["id"],
            "content": m["content"],
            "importance": m["importance"],
            "source": "ltm"
        })
    
    # 去重
    seen = set()
    unique = []
    for m in all_results:
        if m["id"] not in seen:
            seen.add(m["id"])
            unique.append(m)
    
    return {
        "query": query,
        "total": len(unique),
        "memories": unique[:top_k]
    }


@router.get("/stats")
async def get_memory_stats():
    """获取记忆统计"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    return {
        "stm": mindcore.stm.stats(),
        "mtm": mindcore.mtm.stats(),
        "ltm": mindcore.ltm.stats(),
        "lifecycle": mindcore.lifecycle.get_lifecycle_report()
    }


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, source: str = "stm"):
    """删除记忆"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    if source == "stm":
        # STM 不支持单独删除（队列自动管理）
        raise HTTPException(status_code=400, detail="STM 记忆不支持单独删除")
    elif source == "mtm":
        await mindcore.mtm.delete(memory_id)
    elif source == "ltm":
        await mindcore.ltm.delete(memory_id)
    else:
        raise HTTPException(status_code=400, detail="未知的记忆源")
    
    return {"success": True, "deleted_id": memory_id}


@router.get("/{memory_id}")
async def get_memory(memory_id: str, source: str = "stm"):
    """获取单个记忆"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    if source == "stm":
        memory = await mindcore.stm.get(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return {
            "id": memory.id,
            "content": memory.content,
            "importance": memory.importance,
            "source": "stm"
        }
    elif source == "mtm":
        memory = await mindcore.mtm.get(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return memory
    elif source == "ltm":
        memory = await mindcore.ltm.get(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return memory
    else:
        raise HTTPException(status_code=400, detail="未知的记忆源")
