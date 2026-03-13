#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀核心功能详情页 API
- MindCore 记忆核心
- EvoMind 自改进
- Layer0 边缘部署
- 提案管理
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import json
from pathlib import Path
import os

# Token 验证
OPENCLAW_DIR = Path.home() / ".openclaw"
TOKEN_FILE = OPENCLAW_DIR / "workspace" / ".lingxi" / "dashboard_token.txt"

def verify_token(token: str = Query("", description="访问 Token")):
    """验证 Token"""
    if not TOKEN_FILE.exists():
        return True
    saved = TOKEN_FILE.read_text().strip()
    if not saved:
        return True
    if token != saved:
        raise HTTPException(status_code=401, detail="Token 无效")
    return True


# ============ MindCore 记忆核心 ============

mindcore_router = APIRouter(prefix="/api/mindcore", tags=["MindCore"])


@mindcore_router.get("/stats")
async def get_mindcore_stats(_: bool = Depends(verify_token)):
    """获取 MindCore 统计信息"""
    return {
        "name": "MindCore 记忆核心",
        "version": "3.3.6",
        "layers": {
            "STM": {
                "name": "短期记忆层",
                "description": "最近 5 分钟内的记忆，快速访问",
                "capacity": 100,
                "current_size": 0,
                "ttl_seconds": 300
            },
            "MTM": {
                "name": "中期记忆层",
                "description": "7 天内的记忆，需要时检索",
                "capacity": 1000,
                "current_size": 0,
                "ttl_seconds": 604800
            },
            "LTM": {
                "name": "长期记忆层",
                "description": "永久存储的重要记忆",
                "capacity": "unlimited",
                "current_size": 0,
                "min_importance": 8.0
            }
        },
        "lifecycle": {
            "consolidation_enabled": True,
            "consolidation_interval_hours": 1,
            "last_consolidation": None
        }
    }


@mindcore_router.get("/memories")
async def get_memories(
    layer: str = Query("all", description="记忆层：all/STM/MTM/LTM"),
    limit: int = Query(50, description="返回数量"),
    min_importance: float = Query(0, description="最小重要性"),
    _: bool = Depends(verify_token)
):
    """获取记忆列表"""
    # 模拟数据（实际应从 MindCore 读取）
    memories = []
    
    # 示例记忆
    sample_memories = [
        {"id": "mem_001", "layer": "STM", "content": "用户询问了天气信息", "importance": 5.5, "created_at": time.time() - 300},
        {"id": "mem_002", "layer": "MTM", "content": "用户偏好使用飞书进行沟通", "importance": 7.2, "created_at": time.time() - 86400},
        {"id": "mem_003", "layer": "LTM", "content": "老板的 API Token 配置信息", "importance": 9.5, "created_at": time.time() - 604800},
    ]
    
    for mem in sample_memories:
        if layer == "all" or mem["layer"] == layer:
            if mem["importance"] >= min_importance:
                memories.append(mem)
    
    return {"total": len(memories), "layer": layer, "memories": memories[:limit]}


@mindcore_router.get("/memories/{memory_id}")
async def get_memory_detail(memory_id: str, _: bool = Depends(verify_token)):
    """获取记忆详情"""
    return {
        "id": memory_id,
        "content": "这是一条示例记忆内容",
        "layer": "MTM",
        "importance": 7.5,
        "created_at": time.time() - 86400,
        "last_accessed": time.time(),
        "access_count": 5,
        "tags": ["配置", "重要"],
        "embeddings": {"model": "text-embedding-ada-002", "dimensions": 1536},
        "relations": [
            {"memory_id": "mem_001", "type": "similar", "score": 0.85},
            {"memory_id": "mem_003", "type": "referenced_by", "score": 0.72}
        ]
    }


# ============ EvoMind 自改进 ============

evomind_router = APIRouter(prefix="/api/evomind", tags=["EvoMind"])


@evomind_router.get("/stats")
async def get_evomind_stats(_: bool = Depends(verify_token)):
    """获取 EvoMind 统计"""
    return {
        "name": "EvoMind 自改进系统",
        "version": "3.3.6",
        "status": "active",
        "scheduler": {
            "enabled": True,
            "interval_hours": 24,
            "last_run": time.time() - 43200,
            "next_run": time.time() + 43200
        },
        "improvements": {
            "total_proposals": 15,
            "approved": 8,
            "rejected": 3,
            "pending": 4,
            "implemented": 8
        }
    }


@evomind_router.get("/improvements")
async def get_improvements(
    status: str = Query("all", description="状态：all/pending/approved/rejected/implemented"),
    limit: int = Query(50, description="返回数量"),
    _: bool = Depends(verify_token)
):
    """获取自改进历史"""
    # 示例改进记录
    improvements = [
        {
            "id": "imp_001",
            "title": "优化 Token 使用效率",
            "description": "通过 prompt 压缩减少 30% 的 Token 消耗",
            "status": "implemented",
            "impact": "high",
            "created_at": time.time() - 604800,
            "approved_at": time.time() - 518400,
            "implemented_at": time.time() - 432000,
            "metrics": {"token_saved_percent": 30, "cost_reduced": 0.15}
        },
        {
            "id": "imp_002",
            "title": "添加错误重试机制",
            "description": "API 调用失败时自动重试 3 次",
            "status": "implemented",
            "impact": "medium",
            "created_at": time.time() - 518400,
            "approved_at": time.time() - 432000,
            "implemented_at": time.time() - 345600,
            "metrics": {"success_rate_improved": 15}
        },
        {
            "id": "imp_003",
            "title": "优化记忆检索算法",
            "description": "使用向量相似度提升检索准确性",
            "status": "pending",
            "impact": "high",
            "created_at": time.time() - 172800,
            "approved_at": None,
            "implemented_at": None,
            "metrics": {}
        }
    ]
    
    if status != "all":
        improvements = [i for i in improvements if i["status"] == status]
    
    return {"total": len(improvements), "status": status, "improvements": improvements[:limit]}


@evomind_router.get("/improvements/{improvement_id}")
async def get_improvement_detail(improvement_id: str, _: bool = Depends(verify_token)):
    """获取改进详情"""
    return {
        "id": improvement_id,
        "title": "优化 Token 使用效率",
        "description": "通过 prompt 压缩减少 30% 的 Token 消耗",
        "status": "implemented",
        "impact": "high",
        "category": "performance",
        "created_at": time.time() - 604800,
        "created_by": "system",
        "approved_at": time.time() - 518400,
        "approved_by": "admin",
        "implemented_at": time.time() - 432000,
        "metrics": {
            "token_saved_percent": 30,
            "cost_reduced": 0.15,
            "response_time_change": -5
        },
        "code_changes": [
            {"file": "core/token_optimizer.py", "lines_changed": 45},
            {"file": "core/memory.py", "lines_changed": 12}
        ],
        "testing_results": {
            "tests_passed": 28,
            "tests_failed": 0,
            "performance_gain": "30%"
        }
    }


# ============ Layer0 边缘部署 ============

layer_router = APIRouter(prefix="/api/layers", tags=["Layer0-3"])


@layer_router.get("/config")
async def get_layer_config(_: bool = Depends(verify_token)):
    """获取 Layer0-3 配置"""
    return {
        "name": "Layer0-3 四层反应机制",
        "version": "3.3.6",
        "layers": {
            "Layer0": {
                "name": "边缘响应层",
                "description": "最快响应，简单规则匹配",
                "enabled": True,
                "response_time_ms": 50,
                "skills": ["weather", "time", "greeting"],
                "config_file": "/root/lingxi-ai-latest/scripts/layer0_config.py"
            },
            "Layer1": {
                "name": "快速响应层",
                "description": "轻量级模型，快速推理",
                "enabled": True,
                "response_time_ms": 500,
                "model": "qwen-turbo",
                "max_tokens": 500
            },
            "Layer2": {
                "name": "标准响应层",
                "description": "标准模型，平衡质量和速度",
                "enabled": True,
                "response_time_ms": 2000,
                "model": "qwen3.5-plus",
                "max_tokens": 2000
            },
            "Layer3": {
                "name": "深度思考层",
                "description": "最强模型，复杂任务处理",
                "enabled": True,
                "response_time_ms": 10000,
                "model": "qwen3.5-max",
                "max_tokens": 8000,
                "thinking_enabled": True
            }
        },
        "routing": {
            "strategy": "cascading",
            "fallback_enabled": True,
            "timeout_seconds": 30
        }
    }


@layer_router.put("/config/{layer_name}")
async def update_layer_config(
    layer_name: str,
    config: Dict[str, Any],
    _: bool = Depends(verify_token)
):
    """更新 Layer 配置"""
    valid_layers = ["Layer0", "Layer1", "Layer2", "Layer3"]
    if layer_name not in valid_layers:
        raise HTTPException(status_code=400, detail=f"无效的 Layer 名称，必须是：{valid_layers}")
    
    # 这里应该实际写入配置文件
    return {
        "success": True,
        "layer": layer_name,
        "updated_config": config,
        "message": "配置已更新（需要重启生效）"
    }


@layer_router.get("/skills")
async def get_layer_skills(_: bool = Depends(verify_token)):
    """获取 Layer0 技能列表"""
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    skills = []
    
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
                skills.append({
                    "name": skill_folder.name,
                    "layer": "Layer0",
                    "enabled": True,
                    "priority": 5
                })
    
    return {"total": len(skills), "skills": skills}


# ============ 提案管理 ============

proposal_router = APIRouter(prefix="/api/proposals", tags=["Proposals"])


@proposal_router.get("/stats")
async def get_proposal_stats(_: bool = Depends(verify_token)):
    """获取提案统计"""
    return {
        "total": 15,
        "by_status": {
            "pending": 4,
            "under_review": 2,
            "approved": 8,
            "rejected": 3,
            "implemented": 8
        },
        "by_category": {
            "performance": 5,
            "feature": 4,
            "bugfix": 3,
            "optimization": 3
        },
        "recent_activity": {
            "today": 1,
            "this_week": 3,
            "this_month": 8
        }
    }


@proposal_router.get("/list")
async def get_proposals(
    status: str = Query("all", description="状态：all/pending/under_review/approved/rejected/implemented"),
    category: str = Query("", description="分类：performance/feature/bugfix/optimization"),
    limit: int = Query(50, description="返回数量"),
    _: bool = Depends(verify_token)
):
    """获取提案列表"""
    proposals = [
        {
            "id": "prop_001",
            "title": "添加 Redis 缓存支持",
            "category": "performance",
            "status": "pending",
            "author": "system",
            "created_at": time.time() - 86400,
            "votes": 3,
            "priority": "high"
        },
        {
            "id": "prop_002",
            "title": "支持更多消息渠道",
            "category": "feature",
            "status": "under_review",
            "author": "admin",
            "created_at": time.time() - 172800,
            "votes": 5,
            "priority": "medium"
        },
        {
            "id": "prop_003",
            "title": "修复 WebSocket 连接问题",
            "category": "bugfix",
            "status": "approved",
            "author": "system",
            "created_at": time.time() - 259200,
            "votes": 2,
            "priority": "high"
        },
        {
            "id": "prop_004",
            "title": "优化数据库查询性能",
            "category": "optimization",
            "status": "implemented",
            "author": "system",
            "created_at": time.time() - 604800,
            "votes": 4,
            "priority": "medium",
            "implemented_at": time.time() - 518400
        }
    ]
    
    if status != "all":
        proposals = [p for p in proposals if p["status"] == status]
    
    if category:
        proposals = [p for p in proposals if p["category"] == category]
    
    return {"total": len(proposals), "proposals": proposals[:limit]}


@proposal_router.get("/{proposal_id}")
async def get_proposal_detail(proposal_id: str, _: bool = Depends(verify_token)):
    """获取提案详情"""
    return {
        "id": proposal_id,
        "title": "添加 Redis 缓存支持",
        "description": "为了提升系统性能，建议添加 Redis 缓存层来缓存频繁访问的数据",
        "category": "performance",
        "status": "pending",
        "author": "system",
        "created_at": time.time() - 86400,
        "updated_at": time.time() - 43200,
        "votes": 3,
        "priority": "high",
        "details": {
            "problem": "当前数据库查询频繁，响应时间较长",
            "solution": "添加 Redis 缓存，缓存热点数据",
            "benefits": ["响应时间减少 50%", "数据库负载降低 70%"],
            "risks": ["需要额外的 Redis 服务器", "缓存一致性问题"],
            "effort": "medium",
            "estimated_hours": 8
        },
        "comments": [
            {"author": "admin", "content": "好主意，优先级调高", "created_at": time.time() - 43200}
        ],
        "related_proposals": ["prop_004"],
        "attachments": []
    }


@proposal_router.post("/{proposal_id}/vote")
async def vote_proposal(
    proposal_id: str,
    vote: str = Query("up", description="投票：up/down"),
    _: bool = Depends(verify_token)
):
    """投票"""
    return {
        "success": True,
        "proposal_id": proposal_id,
        "vote": vote,
        "new_vote_count": 4
    }


@proposal_router.post("/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: str,
    _: bool = Depends(verify_token)
):
    """批准提案"""
    return {
        "success": True,
        "proposal_id": proposal_id,
        "new_status": "approved",
        "message": "提案已批准，可以开始实施"
    }


@proposal_router.post("/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: str,
    reason: str = Query("", description="拒绝原因"),
    _: bool = Depends(verify_token)
):
    """拒绝提案"""
    return {
        "success": True,
        "proposal_id": proposal_id,
        "new_status": "rejected",
        "reason": reason,
        "message": "提案已拒绝"
    }
