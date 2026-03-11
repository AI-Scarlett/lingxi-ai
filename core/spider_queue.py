#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Scrapling Spider 架构

功能：
- Spider 并发爬取
- 暂停/恢复功能
- 流式模式（实时获取）
- MCP 服务器（AI 辅助爬取）
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
import aiofiles


@dataclass
class SpiderTask:
    """Spider 任务"""
    id: str
    url: str
    callback: str
    status: str = "pending"  # pending/running/paused/completed/failed
    priority: int = 2
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    paused_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    checkpoint: Optional[Dict] = None


class SpiderQueue:
    """Spider 队列 - 支持暂停/恢复"""
    
    def __init__(self, max_concurrent: int = 10, checkpoint_dir: str = None):
        self.max_concurrent = max_concurrent
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else Path.home() / ".openclaw" / "workspace" / ".lingxi" / "spider_checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, SpiderTask] = {}
        self.callbacks: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
        self.running = False
        self.paused = False
        
        # 统计
        self.stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "paused": 0,
            "running": 0
        }
    
    def register_callback(self, name: str, callback: Callable):
        """注册回调函数"""
        self.callbacks[name] = callback
        print(f"✅ 注册回调：{name}")
    
    async def add_task(self, task: SpiderTask):
        """添加任务"""
        async with self._lock:
            self.stats["total"] += 1
        
        await self.queue.put((-task.priority, task))
        print(f"📝 Spider 任务入队：{task.id} (优先级：{task.priority})")
    
    async def pause_task(self, task_id: str):
        """暂停任务"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = "paused"
            task.paused_at = time.time()
            
            # 保存 checkpoint
            await self._save_checkpoint(task)
            
            self.stats["paused"] += 1
            self.stats["running"] -= 1
            
            print(f"⏸️ 任务已暂停：{task_id}")
    
    async def resume_task(self, task_id: str):
        """恢复任务"""
        # 从 checkpoint 加载
        task = await self._load_checkpoint(task_id)
        
        if task:
            task.status = "pending"
            await self.add_task(task)
            
            self.stats["paused"] -= 1
            
            print(f"▶️ 任务已恢复：{task_id}")
    
    async def process_task(self, task: SpiderTask):
        """处理任务"""
        task.status = "running"
        task.started_at = time.time()
        self.running_tasks[task.id] = task
        
        async with self._lock:
            self.stats["running"] += 1
        
        try:
            # 获取回调
            callback = self.callbacks.get(task.callback)
            if not callback:
                raise ValueError(f"未找到回调：{task.callback}")
            
            # 执行任务
            if asyncio.iscoroutinefunction(callback):
                result = await callback(task.url)
            else:
                result = callback(task.url)
            
            task.result = result
            task.status = "completed"
            task.completed_at = time.time()
            
            async with self._lock:
                self.stats["completed"] += 1
                self.stats["running"] -= 1
            
            # 删除 checkpoint
            await self._delete_checkpoint(task.id)
            
            print(f"✅ Spider 任务完成：{task.id}")
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = time.time()
            
            async with self._lock:
                self.stats["failed"] += 1
                self.stats["running"] -= 1
            
            print(f"❌ Spider 任务失败：{task.id} - {e}")
            
            # 保存 checkpoint
            await self._save_checkpoint(task)
            
            raise
        finally:
            self.running_tasks.pop(task.id, None)
    
    async def run(self):
        """运行 Spider 队列"""
        print(f"🕷️ Spider 队列启动 (最大并发：{self.max_concurrent})")
        self.running = True
        
        tasks = []
        
        while self.running:
            # 检查暂停状态
            if self.paused:
                await asyncio.sleep(0.5)
                continue
            
            # 检查并发限制
            if len(self.running_tasks) >= self.max_concurrent:
                await asyncio.sleep(0.1)
                continue
            
            # 获取任务
            try:
                priority, task = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=0.5
                )
                
                # 创建处理任务
                process_task = asyncio.create_task(self.process_task(task))
                tasks.append(process_task)
                
                # 清理已完成的任务
                tasks = [t for t in tasks if not t.done()]
                
            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
    
    async def stream(self):
        """流式模式 - 实时获取结果"""
        print("📊 启动流式模式...")
        
        while self.running:
            # 检查已完成的任务
            for task_id, task in list(self.running_tasks.items()):
                if task.status == "completed" and task.result:
                    yield {
                        "task_id": task_id,
                        "status": "completed",
                        "result": task.result,
                        "timestamp": task.completed_at
                    }
            
            await asyncio.sleep(0.5)
    
    async def _save_checkpoint(self, task: SpiderTask):
        """保存 checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{task.id}.json"
        
        checkpoint_data = asdict(task)
        checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2))
        
        print(f"💾 保存 checkpoint: {task.id}")
    
    async def _load_checkpoint(self, task_id: str) -> Optional[SpiderTask]:
        """加载 checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            checkpoint_data = json.loads(checkpoint_file.read_text())
            task = SpiderTask(**checkpoint_data)
            
            print(f"📥 加载 checkpoint: {task_id}")
            return task
        except:
            return None
    
    async def _delete_checkpoint(self, task_id: str):
        """删除 checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.json"
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            print(f"🗑️ 删除 checkpoint: {task_id}")
    
    def pause_all(self):
        """暂停所有任务"""
        self.paused = True
        print("⏸️ 已暂停所有任务")
    
    def resume_all(self):
        """恢复所有任务"""
        self.paused = False
        print("▶️ 已恢复所有任务")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "queue_size": self.queue.qsize(),
            "running": len(self.running_tasks),
            "paused": self.paused
        }
    
    def stop(self):
        """停止队列"""
        self.running = False
        print("⏹️ Spider 队列已停止")


# MCP 服务器（AI 辅助爬取）
class MCPServer:
    """MCP 服务器 - AI 辅助爬取"""
    
    def __init__(self, spider_queue: SpiderQueue):
        self.spider_queue = spider_queue
        self.app = None  # FastAPI 应用
    
    async def suggest_next_url(self, current_url: str, content: str) -> List[str]:
        """AI 建议下一个要爬取的 URL"""
        # TODO: 使用 LLM 分析内容，建议相关 URL
        return []
    
    async def auto_extract(self, html: str, target: str) -> Dict:
        """AI 自动提取目标数据"""
        # TODO: 使用 LLM 从 HTML 中提取目标数据
        return {}


# 全局 Spider 队列
_spider_queue = None

def get_spider_queue(max_concurrent: int = 10) -> SpiderQueue:
    """获取 Spider 队列实例"""
    global _spider_queue
    
    if _spider_queue is None:
        _spider_queue = SpiderQueue(max_concurrent=max_concurrent)
    
    return _spider_queue


if __name__ == "__main__":
    # 测试运行
    async def test():
        queue = get_spider_queue(max_concurrent=5)
        
        # 注册回调
        async def test_callback(url: str) -> Dict:
            await asyncio.sleep(0.5)
            return {"url": url, "status": "success"}
        
        queue.register_callback("test", test_callback)
        
        # 启动队列
        asyncio.create_task(queue.run())
        
        # 添加测试任务
        for i in range(10):
            task = SpiderTask(
                id=f"spider_{i}",
                url=f"https://example.com/{i}",
                callback="test",
                priority=2
            )
            await queue.add_task(task)
        
        # 等待任务完成
        await asyncio.sleep(5)
        
        # 查看统计
        stats = queue.get_stats()
        print(f"\n📊 统计：{stats}")
        
        # 测试暂停/恢复
        queue.pause_all()
        await asyncio.sleep(2)
        queue.resume_all()
        
        # 停止
        queue.stop()
    
    asyncio.run(test())
