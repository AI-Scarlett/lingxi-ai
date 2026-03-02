#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务规划器 - Task Planner (优化版)
- 并行度控制
- 依赖图优化
- 智能批处理
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SubTask:
    """轻量级子任务"""
    id: str
    role: str
    desc: str
    deps: List[str] = field(default_factory=list)  # 依赖的任务 ID 列表
    payload: Dict = field(default_factory=dict)
    result: Any = None
    status: TaskStatus = TaskStatus.PENDING
    error: str = ""

class FastTaskPlanner:
    """快速任务规划器 - 优化版"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent  # ✅ 限制并发数，避免资源耗尽
        self.task_counter = 0
    
    def _gen_task_id(self) -> str:
        """生成任务 ID"""
        self.task_counter += 1
        return f"t{self.task_counter}_{datetime.now().timestamp()}"
    
    def plan(self, user_input: str, intents: List[Dict]) -> List[SubTask]:
        """根据意图规划任务 - 优化依赖关系"""
        tasks = []
        
        # ✅ 优化 1: 一次遍历完成所有任务创建
        has_content = any(i["type"] == "content_creation" for i in intents)
        has_image = any(i["type"] == "image_generation" for i in intents)
        has_publish = any(i["type"] == "social_publish" for i in intents)
        has_code = any(i["type"] == "coding" for i in intents)
        has_search = any(i["type"] == "search" for i in intents)
        
        task_map = {}
        
        # 内容创作任务
        if has_content:
            t = SubTask(
                id=self._gen_task_id(),
                role="copywriter",
                desc=f"文案创作：{user_input[:20]}...",
                payload={"input": user_input}
            )
            tasks.append(t)
            task_map["content"] = t.id
        
        # 图像生成任务
        if has_image:
            t = SubTask(
                id=self._gen_task_id(),
                role="image_expert",
                desc=f"图片生成：{user_input[:20]}...",
                payload={"input": user_input}
            )
            tasks.append(t)
            task_map["image"] = t.id
        
        # 社交发布任务（依赖 content 和 image）
        if has_publish:
            deps = []
            if has_content:
                deps.append(task_map["content"])
            if has_image:
                deps.append(task_map["image"])
            
            t = SubTask(
                id=self._gen_task_id(),
                role="operator",
                desc=f"发布到平台：{user_input[:20]}...",
                deps=deps,
                payload={"input": user_input}
            )
            tasks.append(t)
        
        # 代码任务（独立）
        if has_code:
            t = SubTask(
                id=self._gen_task_id(),
                role="coder",
                desc=f"代码编写：{user_input[:20]}...",
                payload={"input": user_input}
            )
            tasks.append(t)
        
        # 搜索任务（独立，最优先执行）
        if has_search:
            t = SubTask(
                id=self._gen_task_id(),
                role="searcher",
                desc=f"信息搜索：{user_input[:20]}...",
                payload={"input": user_input}
            )
            tasks.insert(0, t)  # 搜索放前面
        
        # 默认兜底
        if not tasks:
            t = SubTask(
                id=self._gen_task_id(),
                role="writer",
                desc=f"通用处理：{user_input}",
                payload={"input": user_input}
            )
            tasks.append(t)
        
        return tasks
    
    async def execute_parallel(self, tasks: List[SubTask], executor_func) -> List[SubTask]:
        """✅ 优化 2: 分层并行执行 + 依赖等待"""
        completed = set()
        pending = {t.id: t for t in tasks}
        results = []
        
        semaphore = asyncio.Semaphore(self.max_concurrent)  # 限流
        
        async def run_task(task: SubTask):
            async with semaphore:  # ✅ 限制并发
                await self._wait_deps(task, completed, pending)
                task.status = TaskStatus.RUNNING
                
                try:
                    # TODO: 实际调用执行器
                    task.result = await executor_func(task)
                    task.status = TaskStatus.COMPLETED
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                
                completed.add(task.id)
                results.append(task)
        
        # 启动所有任务
        coros = [run_task(t) for t in tasks]
        await asyncio.gather(*coros)
        
        return results
    
    async def _wait_deps(self, task: SubTask, completed: set, pending: dict):
        """等待依赖任务完成"""
        while task.deps:
            unfinished = [d for d in task.deps if d not in completed]
            if not unfinished:
                break
            
            # 等待至少一个依赖完成
            await asyncio.sleep(0.1)


# 测试
if __name__ == "__main__":
    import time
    
    planner = FastTaskPlanner()
    
    # 模拟意图
    intents = [
        {"type": "content_creation"},
        {"type": "image_generation"},
        {"type": "social_publish"}
    ]
    
    tasks = planner.plan("帮我写个小红书文案，配张自拍，然后发布", intents)
    
    print(f"✅ 规划了 {len(tasks)} 个子任务:")
    for t in tasks:
        dep_str = f"(依赖:{','.join(t.deps)})" if t.deps else "(无依赖)"
        print(f"  - {t.role}: {t.desc} {dep_str}")
