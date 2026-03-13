#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务详情页 API

功能：
- 查看单个任务的完整信息
- 任务执行链路追踪
- 子任务详情
- LLM 调用详情
- 错误信息追踪
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class SubTaskDetail(BaseModel):
    """子任务详情"""
    id: str
    name: str
    description: str
    status: str
    agent: Optional[str] = None
    skill: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    result: Optional[str] = None
    error: Optional[str] = None


class LLMCallDetail(BaseModel):
    """LLM 调用详情"""
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    latency_ms: float
    prompt_preview: Optional[str] = None
    completion_preview: Optional[str] = None


class TaskDetailResponse(BaseModel):
    """任务详情响应"""
    # 基本信息
    id: str
    user_id: str
    channel: str
    user_input: str
    
    # 状态
    status: str
    stage: str
    score: float
    
    # 时间信息
    created_at: float
    updated_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    
    # 时间统计
    response_time_ms: float
    execution_time_ms: float
    wait_time_ms: float
    total_duration_ms: float
    
    # 任务类型
    task_type: str
    schedule_name: Optional[str]
    cron_expr: Optional[str]
    
    # 意图识别
    intent_types: List[str]
    
    # 子任务
    subtask_count: int
    subtasks: List[SubTaskDetail]
    
    # LLM 调用
    llm_called: bool
    llm_calls: List[LLMCallDetail]
    total_tokens_in: int
    total_tokens_out: int
    total_cost: float
    
    # 技能信息
    skill_name: Optional[str]
    skill_agent: Optional[str]
    
    # 错误信息
    error_type: Optional[str]
    error_message: Optional[str]
    error_traceback: Optional[str]
    
    # 结果
    final_output: Optional[str]


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(task_id: str):
    """
    获取任务详情
    
    返回任务的完整执行链路，包括：
    - 基本信息
    - 执行阶段
    - 子任务分解
    - LLM 调用详情
    - 性能指标
    - 错误追踪
    """
    from ..database import db
    
    # 从数据库获取任务
    task = db.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 解析子任务
    import json
    subtasks_data = []
    if task.get('subtasks'):
        try:
            subtasks_raw = json.loads(task['subtasks']) if isinstance(task['subtasks'], str) else task['subtasks']
            for st in subtasks_raw:
                subtasks_data.append(SubTaskDetail(
                    id=st.get('id', ''),
                    name=st.get('name', ''),
                    description=st.get('description', ''),
                    status=st.get('status', 'pending'),
                    agent=st.get('agent'),
                    skill=st.get('skill'),
                    started_at=st.get('started_at'),
                    completed_at=st.get('completed_at'),
                    duration_ms=st.get('duration_ms'),
                    result=st.get('result'),
                    error=st.get('error')
                ))
        except Exception:
            pass
    
    # 解析意图类型
    intent_types = []
    if task.get('intent_types'):
        try:
            intent_types = json.loads(task['intent_types']) if isinstance(task['intent_types'], str) else task['intent_types']
        except Exception:
            pass
    
    # 计算总耗时
    total_duration = 0
    if task.get('completed_at') and task.get('created_at'):
        total_duration = (task['completed_at'] - task['created_at']) * 1000
    
    # 构建 LLM 调用详情
    llm_calls = []
    if task.get('llm_called'):
        llm_calls.append(LLMCallDetail(
            model=task.get('llm_model', 'unknown'),
            tokens_in=task.get('llm_tokens_in', 0),
            tokens_out=task.get('llm_tokens_out', 0),
            cost=task.get('llm_cost', 0),
            latency_ms=task.get('execution_time_ms', 0)
        ))
    
    return TaskDetailResponse(
        id=task['id'],
        user_id=task['user_id'],
        channel=task['channel'],
        user_input=task['user_input'],
        status=task['status'],
        stage=task['stage'],
        score=task.get('score', 0),
        created_at=task['created_at'],
        updated_at=task['updated_at'],
        started_at=task.get('started_at'),
        completed_at=task.get('completed_at'),
        response_time_ms=task.get('response_time_ms', 0),
        execution_time_ms=task.get('execution_time_ms', 0),
        wait_time_ms=task.get('wait_time_ms', 0),
        total_duration_ms=total_duration,
        task_type=task.get('task_type', 'realtime'),
        schedule_name=task.get('schedule_name'),
        cron_expr=task.get('cron_expr'),
        intent_types=intent_types,
        subtask_count=len(subtasks_data),
        subtasks=subtasks_data,
        llm_called=task.get('llm_called', False),
        llm_calls=llm_calls,
        total_tokens_in=task.get('llm_tokens_in', 0),
        total_tokens_out=task.get('llm_tokens_out', 0),
        total_cost=task.get('llm_cost', 0),
        skill_name=task.get('skill_name'),
        skill_agent=task.get('skill_agent'),
        error_type=task.get('error_type'),
        error_message=task.get('error_message'),
        error_traceback=task.get('error_traceback'),
        final_output=task.get('final_output')
    )


@router.get("/{task_id}/timeline")
async def get_task_timeline(task_id: str):
    """
    获取任务执行时间线
    
    返回任务在各个阶段的耗时和状态变化
    """
    from ..database import db
    
    task = db.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    timeline = []
    
    # 创建时间点
    timeline.append({
        "stage": "received",
        "time": task['created_at'],
        "label": "任务接收",
        "description": f"从 {task['channel']} 渠道接收到任务"
    })
    
    if task.get('started_at'):
        timeline.append({
            "stage": "started",
            "time": task['started_at'],
            "label": "开始处理",
            "description": "任务开始执行"
        })
    
    # 添加阶段变化
    stage_order = ["received", "intent_analysis", "task_decomposition", "executing", "aggregating", "completed"]
    current_stage = task.get('stage', 'received')
    
    for i, stage in enumerate(stage_order):
        if stage == current_stage or (stage in stage_order[:stage_order.index(current_stage)+1] if current_stage in stage_order else False):
            if stage not in ["received", "started", "completed"]:
                timeline.append({
                    "stage": stage,
                    "time": task['created_at'] + (i * 0.1),  # 估算时间
                    "label": get_stage_label(stage),
                    "description": get_stage_description(stage)
                })
    
    if task.get('completed_at'):
        timeline.append({
            "stage": "completed",
            "time": task['completed_at'],
            "label": "任务完成",
            "description": f"最终得分：{task.get('score', 0)}"
        })
    
    # 按时间排序
    timeline.sort(key=lambda x: x['time'])
    
    return {"task_id": task_id, "timeline": timeline}


def get_stage_label(stage: str) -> str:
    """获取阶段的中文标签"""
    labels = {
        "intent_analysis": "意图分析",
        "task_decomposition": "任务分解",
        "executing": "执行中",
        "aggregating": "结果聚合"
    }
    return labels.get(stage, stage)


def get_stage_description(stage: str) -> str:
    """获取阶段的描述"""
    descriptions = {
        "intent_analysis": "分析用户意图，识别任务类型",
        "task_decomposition": "将复杂任务分解为可执行的子任务",
        "executing": "执行子任务，调用相应的技能和 Agent",
        "aggregating": "聚合所有子任务的结果"
    }
    return descriptions.get(stage, "")


@router.get("/{task_id}/subtasks")
async def get_task_subtasks(task_id: str):
    """获取任务的子任务列表"""
    from ..database import db
    import json
    
    task = db.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    subtasks = []
    if task.get('subtasks'):
        try:
            subtasks_raw = json.loads(task['subtasks']) if isinstance(task['subtasks'], str) else task['subtasks']
            subtasks = subtasks_raw
        except Exception:
            pass
    
    return {"task_id": task_id, "subtasks": subtasks, "total": len(subtasks)}
