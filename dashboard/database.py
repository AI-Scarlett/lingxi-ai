#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀数据看板 - 数据库模型
Lingxi Dashboard Database Models

作者：斯嘉丽 Scarlett
日期：2026-03-09

功能：
- 任务执行记录存储
- 性能指标追踪
- LLM 调用日志
- 错误信息记录
"""

import aiosqlite
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"           # 等待中
    PROCESSING = "processing"     # 处理中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class TaskStage(str, Enum):
    """任务阶段"""
    RECEIVED = "received"              # 已接收
    INTENT_ANALYSIS = "intent_analysis"    # 意图分析
    TASK_DECOMPOSITION = "task_decomposition"  # 任务拆解
    EXECUTING = "executing"           # 执行中
    AGGREGATING = "aggregating"       # 结果汇总
    COMPLETED = "completed"           # 已完成


@dataclass
class TaskRecord:
    """任务记录"""
    id: str
    user_id: str
    channel: str
    user_input: str
    status: str
    stage: str
    created_at: float
    updated_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # 性能指标
    response_time_ms: float = 0.0       # 首次响应时间
    execution_time_ms: float = 0.0      # 总执行时间
    wait_time_ms: float = 0.0           # 等待时间
    
    # LLM 调用
    llm_called: bool = False
    llm_model: str = ""
    llm_tokens_in: int = 0
    llm_tokens_out: int = 0
    llm_cost: float = 0.0
    
    # 任务详情
    intent_types: List[str] = None
    subtask_count: int = 0
    subtasks: List[Dict] = None
    
    # 错误信息
    error_type: str = ""
    error_message: str = ""
    error_traceback: str = ""
    
    # 结果
    final_output: str = ""
    score: float = 0.0
    
    def __post_init__(self):
        if self.intent_types is None:
            self.intent_types = []
        if self.subtasks is None:
            self.subtasks = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskRecord':
        """从字典创建"""
        return cls(**data)


class DashboardDatabase:
    """看板数据库"""
    
    def __init__(self, db_path: str = None):
        """初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        if db_path is None:
            db_path = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """连接数据库"""
        if self._db is None:
            self._db = await aiosqlite.connect(str(self.db_path))
            self._db.row_factory = aiosqlite.Row
            await self._init_tables()
    
    async def close(self):
        """关闭数据库"""
        if self._db:
            await self._db.close()
            self._db = None
    
    async def _init_tables(self):
        """初始化表结构"""
        await self._db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                user_input TEXT NOT NULL,
                status TEXT NOT NULL,
                stage TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                response_time_ms REAL DEFAULT 0,
                execution_time_ms REAL DEFAULT 0,
                wait_time_ms REAL DEFAULT 0,
                llm_called INTEGER DEFAULT 0,
                llm_model TEXT DEFAULT '',
                llm_tokens_in INTEGER DEFAULT 0,
                llm_tokens_out INTEGER DEFAULT 0,
                llm_cost REAL DEFAULT 0,
                intent_types TEXT DEFAULT '[]',
                subtask_count INTEGER DEFAULT 0,
                subtasks TEXT DEFAULT '[]',
                error_type TEXT DEFAULT '',
                error_message TEXT DEFAULT '',
                error_traceback TEXT DEFAULT '',
                final_output TEXT DEFAULT '',
                score REAL DEFAULT 0
            )
        ''')
        
        # 创建索引
        await self._db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON tasks(user_id)')
        await self._db.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
        await self._db.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)')
        await self._db.execute('CREATE INDEX IF NOT EXISTS idx_channel ON tasks(channel)')
        
        await self._db.commit()
    
    async def insert_task(self, task: TaskRecord):
        """插入任务记录"""
        await self._db.execute('''
            INSERT OR REPLACE INTO tasks (
                id, user_id, channel, user_input, status, stage,
                created_at, updated_at, started_at, completed_at,
                response_time_ms, execution_time_ms, wait_time_ms,
                llm_called, llm_model, llm_tokens_in, llm_tokens_out, llm_cost,
                intent_types, subtask_count, subtasks,
                error_type, error_message, error_traceback,
                final_output, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.user_id, task.channel, task.user_input,
            task.status, task.stage, task.created_at, task.updated_at,
            task.started_at, task.completed_at, task.response_time_ms,
            task.execution_time_ms, task.wait_time_ms,
            1 if task.llm_called else 0, task.llm_model,
            task.llm_tokens_in, task.llm_tokens_out, task.llm_cost,
            json.dumps(task.intent_types), task.subtask_count,
            json.dumps(task.subtasks),
            task.error_type, task.error_message, task.error_traceback,
            task.final_output, task.score
        ))
        await self._db.commit()
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]):
        """更新任务记录"""
        if not updates:
            return
        
        updates['updated_at'] = time.time()
        
        # 序列化列表/字典类型为 JSON
        json_fields = ['intent_types', 'subtasks']
        for field in json_fields:
            if field in updates and isinstance(updates[field], (list, dict)):
                updates[field] = json.dumps(updates[field])
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [task_id]
        
        await self._db.execute(f'UPDATE tasks SET {set_clause} WHERE id = ?', values)
        await self._db.commit()
    
    async def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """获取任务记录"""
        async with self._db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_task(row)
        return None
    
    async def get_tasks(self, limit: int = 50, offset: int = 0,
                       user_id: str = None, status: str = None,
                       channel: str = None) -> List[TaskRecord]:
        """获取任务列表"""
        query = 'SELECT * FROM tasks'
        conditions = []
        params = []
        
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        if status:
            conditions.append('status = ?')
            params.append(status)
        if channel:
            conditions.append('channel = ?')
            params.append(channel)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        async with self._db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_task(row) for row in rows]
    
    async def get_stats(self, hours: int = 24) -> Dict:
        """获取统计数据"""
        cutoff = time.time() - (hours * 3600)
        
        # 总任务数
        async with self._db.execute(
            'SELECT COUNT(*) FROM tasks WHERE created_at > ?', (cutoff,)
        ) as cursor:
            total = (await cursor.fetchone())[0]
        
        # 各状态任务数
        async with self._db.execute(
            'SELECT status, COUNT(*) FROM tasks WHERE created_at > ? GROUP BY status',
            (cutoff,)
        ) as cursor:
            status_counts = dict(await cursor.fetchall())
        
        # LLM 调用统计
        async with self._db.execute(
            'SELECT COUNT(*), SUM(llm_tokens_in), SUM(llm_tokens_out), SUM(llm_cost) '
            'FROM tasks WHERE created_at > ? AND llm_called = 1',
            (cutoff,)
        ) as cursor:
            row = await cursor.fetchone()
            llm_calls = row[0] or 0
            llm_tokens_in = row[1] or 0
            llm_tokens_out = row[2] or 0
            llm_cost = row[3] or 0
        
        # 平均响应时间
        async with self._db.execute(
            'SELECT AVG(response_time_ms), AVG(execution_time_ms) '
            'FROM tasks WHERE created_at > ? AND status = "completed"',
            (cutoff,)
        ) as cursor:
            row = await cursor.fetchone()
            avg_response = row[0] or 0
            avg_execution = row[1] or 0
        
        # 错误率
        async with self._db.execute(
            'SELECT COUNT(*) FROM tasks WHERE created_at > ? AND status = "failed"',
            (cutoff,)
        ) as cursor:
            failed = (await cursor.fetchone())[0]
            error_rate = (failed / total * 100) if total > 0 else 0
        
        return {
            "total_tasks": total,
            "status_counts": status_counts,
            "llm_calls": llm_calls,
            "llm_tokens_in": llm_tokens_in,
            "llm_tokens_out": llm_tokens_out,
            "llm_cost": llm_cost,
            "avg_response_ms": avg_response,
            "avg_execution_ms": avg_execution,
            "error_rate": error_rate,
            "period_hours": hours
        }
    
    async def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """获取最近错误"""
        async with self._db.execute('''
            SELECT id, user_input, error_type, error_message, created_at
            FROM tasks
            WHERE status = "failed"
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _row_to_task(self, row: aiosqlite.Row) -> TaskRecord:
        """将数据库行转换为任务记录"""
        return TaskRecord(
            id=row['id'],
            user_id=row['user_id'],
            channel=row['channel'],
            user_input=row['user_input'],
            status=row['status'],
            stage=row['stage'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            response_time_ms=row['response_time_ms'],
            execution_time_ms=row['execution_time_ms'],
            wait_time_ms=row['wait_time_ms'],
            llm_called=bool(row['llm_called']),
            llm_model=row['llm_model'],
            llm_tokens_in=row['llm_tokens_in'],
            llm_tokens_out=row['llm_tokens_out'],
            llm_cost=row['llm_cost'],
            intent_types=json.loads(row['intent_types']),
            subtask_count=row['subtask_count'],
            subtasks=json.loads(row['subtasks']),
            error_type=row['error_type'],
            error_message=row['error_message'],
            error_traceback=row['error_traceback'],
            final_output=row['final_output'],
            score=row['score']
        )


# 全局数据库实例
_db_instance: Optional[DashboardDatabase] = None


def get_database(db_path: str = None) -> DashboardDatabase:
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DashboardDatabase(db_path)
    return _db_instance
