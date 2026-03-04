#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 真·并行执行器 (v2.8.0)

核心特性：
1. ⚡ 老板优先 - 永远预留 1 个槽位给老板
2. 🎯 智能依赖分析 - 无依赖的任务并行
3. 📊 进度实时推送 - 每步反馈
4. 🔧 最大 5 并发 - 其中 1 个永远留给老板

架构：
- 总槽位：5 个
- 老板专用：1 个（永远空闲）
- 普通任务：4 个（可并发）
"""

import asyncio
from asyncio import Semaphore
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

# ==================== 任务优先级 ====================

class Priority(Enum):
    """任务优先级"""
    BOSS = 0        # 👑 老板的命令（最高优先级）
    URGENT = 1      # 🔴 紧急任务
    HIGH = 2        # 🟡 高优先级
    NORMAL = 3      # 🔵 普通任务
    LOW = 4         # ⚪ 后台任务

# ==================== 任务模型 ====================

@dataclass
class Task:
    """任务模型"""
    id: str
    name: str
    func: Callable
    priority: Priority
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: Optional[str] = None
    
    @classmethod
    def create(cls, name: str, func: Callable, priority: Priority = Priority.NORMAL,
               dependencies: List[str] = None):
        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            func=func,
            priority=priority,
            dependencies=dependencies or []
        )

# ==================== 进度追踪器 ====================

class ProgressTracker:
    """进度追踪器 - 实时推送进度"""
    
    def __init__(self, task_id: str, user_id: str = "boss"):
        self.task_id = task_id
        self.user_id = user_id
        self.progress = 0
        self.subtasks: Dict[str, Dict] = {}
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable):
        """添加进度回调（用于推送消息）"""
        self.callbacks.append(callback)
    
    def update(self, subtask: str, progress: int, message: str):
        """更新子任务进度"""
        self.subtasks[subtask] = {
            "progress": progress,
            "message": message,
            "updated_at": datetime.now().isoformat()
        }
        
        # 计算总进度
        total_progress = sum(s["progress"] for s in self.subtasks.values()) / len(self.subtasks) if self.subtasks else 0
        self.progress = int(total_progress)
        
        # 通知所有回调
        for callback in self.callbacks:
            try:
                callback(self.task_id, self.user_id, self.progress, self.subtasks)
            except Exception as e:
                print(f"⚠️ 进度回调失败：{e}")
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "task_id": self.task_id,
            "progress": self.progress,
            "subtasks": self.subtasks,
            "updated_at": datetime.now().isoformat()
        }

# ==================== 依赖分析器 ====================

class DependencyAnalyzer:
    """依赖分析器 - 智能分层"""
    
    def analyze(self, tasks: List[Task]) -> List[List[Task]]:
        """
        分析任务依赖，返回可并行的任务组
        
        示例输入：
        [任务 A, 任务 B, 任务 C(依赖 A+B), 任务 D]
        
        返回：
        [[任务 A, 任务 B, 任务 D], [任务 C]]
        第一组并行执行，第二组等第一组完成后执行
        """
        # 构建依赖图
        task_map = {t.id: t for t in tasks}
        completed = set()
        layers = []
        
        remaining = list(tasks)
        
        while remaining:
            # 找出当前可执行的任务（依赖都已完成）
            ready = []
            waiting = []
            
            for task in remaining:
                deps_met = all(dep_id in completed for dep_id in task.dependencies)
                if deps_met:
                    ready.append(task)
                else:
                    waiting.append(task)
            
            if not ready:
                # 循环依赖检测
                if waiting:
                    print(f"⚠️ 检测到循环依赖：{[t.id for t in waiting]}")
                    # 强制执行剩余任务
                    ready = waiting
                    waiting = []
            
            if ready:
                layers.append(ready)
                for task in ready:
                    completed.add(task.id)
            
            remaining = waiting
        
        return layers

# ==================== 并行执行器 ====================

class ParallelExecutor:
    """
    真·并行执行器
    
    槽位分配：
    - 总槽位：5 个
    - 老板专用：1 个（永远预留）
    - 普通任务：4 个（可并发）
    """
    
    def __init__(self, max_concurrent: int = 5, boss_reserved: int = 1):
        self.max_concurrent = max_concurrent
        self.boss_reserved = boss_reserved
        self.normal_slots = max_concurrent - boss_reserved
        
        # 信号量控制
        self.boss_semaphore = Semaphore(boss_reserved)
        self.normal_semaphore = Semaphore(self.normal_slots)
        
        # 任务队列
        self.pending_tasks: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        
        # 依赖分析器
        self.analyzer = DependencyAnalyzer()
        
        # 进度追踪
        self.trackers: Dict[str, ProgressTracker] = {}
        
        # 执行锁
        self._lock = asyncio.Lock()
    
    async def submit(self, task: Task) -> str:
        """提交任务"""
        async with self._lock:
            self.pending_tasks.append(task)
            
            # 按优先级排序
            self.pending_tasks.sort(key=lambda t: t.priority.value)
        
        # 创建进度追踪器
        tracker = ProgressTracker(task.id)
        self.trackers[task.id] = tracker
        
        return task.id
    
    async def submit_boss(self, name: str, func: Callable) -> str:
        """提交老板任务（最高优先级）"""
        task = Task.create(name, func, Priority.BOSS)
        return await self.submit(task)
    
    async def _execute_task(self, task: Task) -> Any:
        """执行单个任务"""
        task.started_at = datetime.now().isoformat()
        task.status = "running"
        self.running_tasks[task.id] = task
        
        try:
            # 执行任务
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func()
            else:
                result = task.func()
            
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            task.progress = 100
            
            return result
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = datetime.now().isoformat()
            raise
        finally:
            # 从运行中移除
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self.completed_tasks[task.id] = task
    
    async def _execute_with_semaphore(self, task: Task) -> Any:
        """带信号量的任务执行"""
        # 老板任务使用专用槽位
        if task.priority == Priority.BOSS:
            async with self.boss_semaphore:
                return await self._execute_task(task)
        else:
            async with self.normal_semaphore:
                return await self._execute_task(task)
    
    async def execute_batch(self, tasks: List[Task]) -> List[Any]:
        """批量执行任务（智能并行）"""
        # 依赖分析
        layers = self.analyzer.analyze(tasks)
        
        all_results = []
        
        # 分层执行
        for i, layer in enumerate(layers):
            print(f"📊 执行第 {i+1}/{len(layers)} 层，共 {len(layer)} 个任务")
            
            # 本层任务并行执行
            coroutines = [self._execute_with_semaphore(task) for task in layer]
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            all_results.extend(results)
        
        return all_results
    
    async def run_pending(self) -> int:
        """运行待处理任务"""
        async with self._lock:
            if not self.pending_tasks:
                return 0
            
            # 获取当前可执行的任务
            tasks_to_run = []
            remaining = []
            
            for task in self.pending_tasks:
                # 检查依赖
                deps_met = all(
                    dep_id in self.completed_tasks
                    for dep_id in task.dependencies
                )
                
                if deps_met:
                    tasks_to_run.append(task)
                else:
                    remaining.append(task)
            
            self.pending_tasks = remaining
        
        # 并行执行
        if tasks_to_run:
            await self.execute_batch(tasks_to_run)
        
        return len(tasks_to_run)
    
    def get_status(self) -> Dict:
        """获取执行器状态"""
        return {
            "pending": len(self.pending_tasks),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "boss_slots_available": self.boss_reserved,
            "normal_slots_available": self.normal_slots - len([
                t for t in self.running_tasks.values()
                if t.priority != Priority.BOSS
            ])
        }
    
    def get_tracker(self, task_id: str) -> Optional[ProgressTracker]:
        """获取任务进度追踪器"""
        return self.trackers.get(task_id)

# ==================== 使用示例 ====================

async def demo():
    """演示使用"""
    print("🚀 灵犀真·并行执行器演示\n")
    
    executor = ParallelExecutor(max_concurrent=5, boss_reserved=1)
    
    # 模拟任务
    async def task_a():
        await asyncio.sleep(1)
        return "任务 A 完成"
    
    async def task_b():
        await asyncio.sleep(2)
        return "任务 B 完成"
    
    async def task_c():
        await asyncio.sleep(1)
        return "任务 C 完成（依赖 A+B）"
    
    async def boss_task():
        await asyncio.sleep(0.5)
        return "👑 老板任务完成（优先执行）"
    
    # 创建任务
    tasks = [
        Task.create("任务 A", task_a, Priority.NORMAL),
        Task.create("任务 B", task_b, Priority.NORMAL),
        Task.create("任务 C", task_c, Priority.NORMAL, dependencies=[]),  # 依赖 A 和 B 的 ID
        Task.create("老板的命令", boss_task, Priority.BOSS),
    ]
    
    # 设置依赖
    tasks[2].dependencies = [tasks[0].id, tasks[1].id]
    
    print("📋 任务列表:")
    for task in tasks:
        deps = f" (依赖：{task.dependencies})" if task.dependencies else ""
        priority_icon = "👑" if task.priority == Priority.BOSS else "🔵"
        print(f"  {priority_icon} {task.name}{deps}")
    
    print("\n⚡ 开始执行...\n")
    
    # 执行
    results = await executor.execute_batch(tasks)
    
    print("\n✅ 执行完成!\n")
    print("📊 最终状态:")
    status = executor.get_status()
    print(f"  待处理：{status['pending']}")
    print(f"  运行中：{status['running']}")
    print(f"  已完成：{status['completed']}")
    print(f"  老板槽位：{status['boss_slots_available']} 个")
    print(f"  普通槽位：{status['normal_slots_available']} 个")
    
    print("\n📝 任务结果:")
    for task, result in zip(tasks, results):
        icon = "✅" if task.status == "completed" else "❌"
        print(f"  {icon} {task.name}: {result if result else task.error}")

if __name__ == "__main__":
    asyncio.run(demo())
