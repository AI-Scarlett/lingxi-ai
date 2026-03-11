#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard 改进审批页

功能：
- 查看待审批提案
- 批量审批
- 审批结果查看
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

router = APIRouter(prefix="/api/improvements", tags=["improvements"])


class ApprovalRequest(BaseModel):
    """审批请求"""
    action: str  # approve, reject, defer
    proposal_ids: List[str]
    user_id: Optional[str] = None


@router.get("/pending")
async def get_pending_proposals(limit: int = 10):
    """获取待审批提案"""
    from ..evomind.approval import get_approval_manager
    
    manager = get_approval_manager()
    proposals = await manager.get_pending_proposals(limit)
    
    return {
        "total": len(proposals),
        "proposals": proposals
    }


@router.post("/approve")
async def approve_proposals(request: ApprovalRequest):
    """审批提案"""
    from ..evomind.approval import get_approval_manager
    
    manager = get_approval_manager()
    
    if not request.user_id:
        request.user_id = "dashboard_user"
    
    results = await manager.process_approval(
        request.user_id,
        request.action,
        request.proposal_ids
    )
    
    return {
        "success": True,
        "results": results
    }


@router.get("/stats")
async def get_improvement_stats():
    """获取改进统计"""
    from ..evomind.approval import get_approval_manager
    
    manager = get_approval_manager()
    stats = manager.get_stats()
    
    return stats
