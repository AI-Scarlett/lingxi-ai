#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard 学习监控页

功能：
- 查看学习进度
- 改进提案列表
- 审批历史
- 学习效果统计
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

router = APIRouter(prefix="/api/learning", tags=["learning"])


class ProposalItem(BaseModel):
    """改进提案项"""
    id: str
    type: str
    title: str
    importance: float
    status: str
    created_at: float


@router.get("/proposals")
async def get_proposals(status: str = "pending", limit: int = 20):
    """获取改进提案"""
    from ..evomind.approval import get_approval_manager
    
    manager = get_approval_manager()
    
    if status == "pending":
        proposals = await manager.get_pending_proposals(limit)
    else:
        # 从数据库查询其他状态
        proposals = []
    
    return {
        "total": len(proposals),
        "proposals": proposals
    }


@router.get("/stats")
async def get_learning_stats():
    """获取学习统计"""
    from ..evomind.approval import get_approval_manager
    
    manager = get_approval_manager()
    stats = manager.get_stats()
    
    return {
        "proposals": stats,
        "learning_cycles": 0,  # TODO: 实现学习周期统计
        "memory_improvements": 0  # TODO: 实现记忆改进统计
    }


@router.get("/history")
async def get_approval_history(limit: int = 50):
    """获取审批历史"""
    # TODO: 从数据库查询审批历史
    return {
        "total": 0,
        "history": []
    }


@router.post("/improvements/run")
async def run_improvement_cycle():
    """运行改进周期"""
    from ..mindcore import get_mindcore
    
    mindcore = get_mindcore()
    
    report = await mindcore.run_improvement_cycle()
    
    return {
        "success": True,
        "report": report
    }
