#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀任务队列系统 - 支持多任务并行

- 实时任务：立即执行
- 定时任务：Cron 调度
- 延迟任务：队列延迟
- 优先级：紧急 > 高 > 中 > 低
"""

import asyncio
import time
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import aiofiles
import sqlite3


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    CRITICAL = 0  # 紧急
    HIGH = 1      # 高
    NORMAL = 2    # 中
    LOW = 3       # 低


@dataclass
class Task:
    """任务定义"""
    id: str = field(default_factory=lambda: f"task_{int(time.time()*1000)}")
    type: str = "realtime"  # realtime, scheduled, delayed
    priority: int = TaskPriority.NORMAL.value
    status: str = TaskStatus.PENDING.value
    payload: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    channel: str = "unknown"
    user_id: str = "unknown"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        return cls(**data)


class TaskQueue:
    """任务队列 - 支持优先级"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.queues: Dict[int, asyncio.Queue] = {
            priority: asyncio.Queue() 
            for priority in range(4)  # 0-3 优先级
        }
        self.running_tasks: Dict[str, Task] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
        
        # 统计
        self.stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "running": 0
        }
    
    def register_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
        print(f"✅ 注册任务处理器：{task_type}")
    
    async def enqueue(self, task: Task):
        """添加任务到队列"""
        async with self._lock:
            self.stats["total"] += 1
        
        # 根据优先级加入对应队列
        await self.queues[task.priority].put(task)
        print(f"📝 任务入队：{task.id} (优先级：{task.priority})")
    
    async def dequeue(self) -> Optional[Task]:
        """从队列获取任务（优先级最高）"""
        # 按优先级顺序检查队列
        for priority in range(4):
            if not self.queues[priority].empty():
                task = await self.queues[priority].get()
                return task
        return None
    
    async def process_task(self, task: Task):
        """处理单个任务"""
        task.status = TaskStatus.RUNNING.value
        task.started_at = time.time()
        self.running_tasks[task.id] = task
        
        async with self._lock:
            self.stats["running"] += 1
        
        try:
            # 获取处理器
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"未找到任务处理器：{task.type}")
            
            # 执行任务
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task)
            else:
                result = handler(task)
            
            task.status = TaskStatus.COMPLETED.value
            task.completed_at = time.time()
            
            async with self._lock:
                self.stats["completed"] += 1
                self.stats["running"] -= 1
            
            print(f"✅ 任务完成：{task.id}")
            return result
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            # 重试逻辑
            if task.retry_count < task.max_retries:
                print(f"⚠️ 任务失败，重试 {task.retry_count}/{task.max_retries}: {task.id}")
                task.status = TaskStatus.PENDING.value
                await self.enqueue(task)
            else:
                task.status = TaskStatus.FAILED.value
                task.completed_at = time.time()
                
                async with self._lock:
                    self.stats["failed"] += 1
                    self.stats["running"] -= 1
                
                print(f"❌ 任务失败：{task.id} - {e}")
            
            raise
        finally:
            self.running_tasks.pop(task.id, None)
    
    async def run(self):
        """运行任务处理器"""
        print(f"🚀 任务队列启动 (最大并发：{self.max_concurrent})")
        
        tasks = []
        
        while True:
            # 检查并发限制
            if len(self.running_tasks) >= self.max_concurrent:
                await asyncio.sleep(0.1)
                continue
            
            # 获取任务
            task = await self.dequeue()
            
            if task:
                # 创建处理任务
                process_task = asyncio.create_task(self.process_task(task))
                tasks.append(process_task)
                
                # 清理已完成的任务
                tasks = [t for t in tasks if not t.done()]
            else:
                await asyncio.sleep(0.1)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "queue_sizes": {
                f"priority_{i}": q.qsize() 
                for i, q in self.queues.items()
            },
            "running": len(self.running_tasks)
        }


class ScheduledTaskManager:
    """定时任务管理器"""
    
    def __init__(self, queue: TaskQueue):
        self.queue = queue
        self.schedules: List[Dict] = []
        self._running = False
    
    def add_schedule(self, name: str, cron_expr: str, task_payload: Dict, 
                     priority: int = TaskPriority.NORMAL.value):
        """添加定时任务"""
        self.schedules.append({
            "name": name,
            "cron_expr": cron_expr,
            "payload": task_payload,
            "priority": priority,
            "enabled": True
        })
        print(f"⏰ 添加定时任务：{name} ({cron_expr})")
    
    def parse_cron(self, cron_expr: str) -> List[int]:
        """解析 Cron 表达式（简化版）"""
        # 支持格式：*/N (每 N 分钟), * (每分钟), N (固定分钟)
        parts = cron_expr.split()
        if len(parts) >= 1:
            minute = parts[0]
            if minute.startswith("*/"):
                interval = int(minute[2:])
                return list(range(0, 60, interval))
            elif minute == "*":
                return list(range(60))
            else:
                return [int(minute)]
        return [0]
    
    async def run(self):
        """运行定时任务调度器"""
        print("⏰ 定时任务调度器启动")
        self._running = True
        
        last_check = -1
        
        while self._running:
            now = datetime.now()
            current_minute = now.minute
            
            # 每分钟检查一次
            if current_minute != last_check:
                last_check = current_minute
                
                for schedule in self.schedules:
                    if not schedule["enabled"]:
                        continue
                    
                    # 检查是否应该执行
                    minutes = self.parse_cron(schedule["cron_expr"])
                    
                    if current_minute in minutes:
                        # 创建任务
                        task = Task(
                            type="scheduled",
                            priority=schedule["priority"],
                            payload={
                                **schedule["payload"],
                                "schedule_name": schedule["name"],
                                "triggered_at": now.isoformat()
                            }
                        )
                        
                        await self.queue.enqueue(task)
                        print(f"⏰ 触发定时任务：{schedule['name']}")
            
            await asyncio.sleep(1)  # 每秒检查一次
    
    def stop(self):
        """停止调度器"""
        self._running = False


class TaskPersistence:
    """任务持久化"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT,
                priority INTEGER,
                status TEXT,
                payload TEXT,
                created_at REAL,
                started_at REAL,
                completed_at REAL,
                error TEXT,
                retry_count INTEGER,
                channel TEXT,
                user_id TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON tasks(created_at)")
        
        conn.commit()
        conn.close()
    
    def save_task(self, task: Task):
        """保存任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks (
                id, type, priority, status, payload, created_at, 
                started_at, completed_at, error, retry_count, channel, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            task.id,
            task.type,
            task.priority,
            task.status,
            json.dumps(task.payload),
            task.created_at,
            task.started_at,
            task.completed_at,
            task.error,
            task.retry_count,
            task.channel,
            task.user_id
        ])
        
        conn.commit()
        conn.close()
    
    def get_tasks(self, status: str = None, limit: int = 50) -> List[Task]:
        """获取任务列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [Task.from_dict(dict(row)) for row in rows]


# 全局任务队列
_task_queue = None

def get_task_queue(max_concurrent: int = 10) -> TaskQueue:
    """获取任务队列实例"""
    global _task_queue
    
    if _task_queue is None:
        _task_queue = TaskQueue(max_concurrent=max_concurrent)
    
    return _task_queue
