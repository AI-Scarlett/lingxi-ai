#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆详情页 API

功能：
- 查看单个记忆的详细信息
- 记忆关联图谱
- 记忆访问历史
- 记忆重要性分析
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemorySource(BaseModel):
    """记忆来源"""
    layer: str  # stm, mtm, ltm
    created_at: float
    original_content: Optional[str] = None


class MemoryAccess(BaseModel):
    """记忆访问记录"""
    timestamp: float
    session_id: Optional[str]
    task_id: Optional[str]
    access_type: str  # read, write, search, retrieve


class MemoryRelation(BaseModel):
    """记忆关联"""
    related_memory_id: str
    relation_type: str  # similar, derived_from, referenced_by
    similarity_score: float


class MemoryDetailResponse(BaseModel):
    """记忆详情响应"""
    # 基本信息
    id: str
    content: str
    content_preview: str
    
    # 重要性
    importance: float
    importance_level: str  # low, medium, high, critical
    
    # 来源
    source: MemorySource
    
    # 时间
    created_at: float
    last_accessed: Optional[float]
    
    # 访问统计
    access_count: int
    recent_accesses: List[MemoryAccess]
    
    # 标签
    tags: List[str]
    categories: List[str]
    
    # 关联
    relations: List[MemoryRelation]
    
    # 元数据
    metadata: Dict[str, Any]
    
    # 状态
    is_consolidated: bool
    consolidation_scheduled: bool


@router.get("/list")
async def list_memories(
    source: str = Query("all", description="记忆层：all/stm/mtm/ltm"),
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    min_importance: Optional[float] = Query(None, description="最小重要性"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取记忆列表"""
    from ..database import db
    
    memories = db.get_memories(
        source=source if source != "all" else None,
        limit=limit,
        offset=offset,
        min_importance=min_importance,
        search=search
    )
    
    result = []
    for memory in memories:
        memory_info = {
            "id": memory['id'],
            "content": memory['content'],
            "content_preview": memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content'],
            "importance": memory.get('importance', 0),
            "importance_level": get_importance_level(memory.get('importance', 0)),
            "source": memory.get('source', 'unknown'),
            "created_at": memory.get('created_at', 0),
            "last_accessed": memory.get('last_accessed'),
            "access_count": memory.get('access_count', 0),
            "tags": memory.get('tags', []),
            "is_consolidated": memory.get('is_consolidated', False)
        }
        result.append(memory_info)
    
    return {
        "total": len(memories),
        "limit": limit,
        "offset": offset,
        "memories": result
    }


@router.get("/{memory_id}", response_model=MemoryDetailResponse)
async def get_memory_detail(memory_id: str, source: str = Query("stm", description="记忆层")):
    """获取记忆详情"""
    from ..database import db
    
    # 获取记忆基本信息
    memory = db.get_memory(memory_id, source=source)
    
    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")
    
    # 获取访问历史
    recent_accesses = get_memory_accesses(memory_id, limit=10)
    
    # 获取关联记忆
    relations = get_memory_relations(memory_id)
    
    # 构建来源信息
    memory_source = MemorySource(
        layer=source,
        created_at=memory.get('created_at', 0),
        original_content=memory.get('original_content')
    )
    
    return MemoryDetailResponse(
        id=memory['id'],
        content=memory['content'],
        content_preview=memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content'],
        importance=memory.get('importance', 0),
        importance_level=get_importance_level(memory.get('importance', 0)),
        source=memory_source,
        created_at=memory.get('created_at', 0),
        last_accessed=memory.get('last_accessed'),
        access_count=memory.get('access_count', 0),
        recent_accesses=recent_accesses,
        tags=memory.get('tags', []),
        categories=memory.get('categories', []),
        relations=relations,
        metadata=memory.get('metadata', {}),
        is_consolidated=memory.get('is_consolidated', False),
        consolidation_scheduled=memory.get('consolidation_scheduled', False)
    )


@router.get("/{memory_id}/accesses")
async def get_memory_accesses_api(
    memory_id: str,
    days: int = Query(7, description="查询天数"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取记忆访问历史"""
    from ..database import db
    
    accesses = db.get_memory_accesses(memory_id, days=days, limit=limit)
    
    return {
        "memory_id": memory_id,
        "days": days,
        "total": len(accesses),
        "accesses": accesses
    }


@router.get("/{memory_id}/relations")
async def get_memory_relations_api(memory_id: str):
    """获取记忆关联"""
    from ..database import db
    
    relations = get_memory_relations(memory_id)
    
    return {
        "memory_id": memory_id,
        "total": len(relations),
        "relations": relations
    }


@router.get("/{memory_id}/timeline")
async def get_memory_timeline(memory_id: str):
    """获取记忆时间线"""
    from ..database import db
    
    memory = db.get_memory_by_id(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")
    
    timeline = []
    
    # 创建时间
    timeline.append({
        "event": "created",
        "time": memory['created_at'],
        "label": "记忆创建",
        "description": f"在 {memory.get('source', 'unknown')} 层创建"
    })
    
    # 访问时间
    accesses = db.get_memory_accesses(memory_id, days=30, limit=20)
    for access in accesses:
        timeline.append({
            "event": "accessed",
            "time": access['timestamp'],
            "label": "被访问",
            "description": f"类型：{access.get('access_type', 'read')}"
        })
    
    # 巩固时间（如果有）
    if memory.get('consolidated_at'):
        timeline.append({
            "event": "consolidated",
            "time": memory['consolidated_at'],
            "label": "记忆巩固",
            "description": "从短期记忆转为长期记忆"
        })
    
    # 按时间排序
    timeline.sort(key=lambda x: x['time'], reverse=True)
    
    return {
        "memory_id": memory_id,
        "timeline": timeline
    }


@router.post("/{memory_id}/update")
async def update_memory(
    memory_id: str,
    content: Optional[str] = None,
    importance: Optional[float] = None,
    tags: Optional[List[str]] = None
):
    """更新记忆"""
    from ..database import db
    
    updates = {}
    if content is not None:
        updates['content'] = content
    if importance is not None:
        updates['importance'] = importance
    if tags is not None:
        updates['tags'] = tags
    
    if not updates:
        raise HTTPException(status_code=400, detail="没有提供更新内容")
    
    db.update_memory(memory_id, updates)
    
    return {"success": True, "memory_id": memory_id, "updates": updates}


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, source: str = Query("stm", description="记忆层")):
    """删除记忆"""
    from ..database import db
    
    db.delete_memory(memory_id, source=source)
    
    return {"success": True, "deleted_memory": memory_id}


def get_importance_level(importance: float) -> str:
    """根据重要性分数返回等级"""
    if importance >= 9.0:
        return "critical"
    elif importance >= 7.0:
        return "high"
    elif importance >= 4.0:
        return "medium"
    else:
        return "low"


def get_memory_accesses(memory_id: str, limit: int = 10) -> List[MemoryAccess]:
    """获取记忆访问记录"""
    from ..database import db
    
    accesses_raw = db.get_memory_accesses(memory_id, limit=limit)
    
    accesses = []
    for acc in accesses_raw:
        accesses.append(MemoryAccess(
            timestamp=acc.get('timestamp', 0),
            session_id=acc.get('session_id'),
            task_id=acc.get('task_id'),
            access_type=acc.get('access_type', 'read')
        ))
    
    return accesses


def get_memory_relations(memory_id: str) -> List[MemoryRelation]:
    """获取记忆关联"""
    from ..database import db
    
    # 从数据库查询关联记忆
    relations_raw = db.get_memory_relations(memory_id)
    
    relations = []
    for rel in relations_raw:
        relations.append(MemoryRelation(
            related_memory_id=rel.get('related_memory_id', ''),
            relation_type=rel.get('relation_type', 'similar'),
            similarity_score=rel.get('similarity_score', 0)
        ))
    
    return relations
