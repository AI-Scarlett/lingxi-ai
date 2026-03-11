#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务分发器

功能：
- 根据渠道/任务类型分发到对应 Agent
- 智能路由
- 并发控制
"""

import asyncio
from typing import Dict, List, Optional, Any
import time

# 使用 asyncio 信号量
from asyncio import Semaphore


class TaskDistributor:
    """任务分发器"""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = Semaphore(max_concurrent)
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "pending_tasks": 0
        }
    
    def register_agent(self, agent):
        """注册 Agent"""
        self.agents[agent.agent_id] = agent
        self.agents[agent.channel] = agent  # 也按渠道注册
    
    def get_agent_for_task(self, task: Dict) -> Optional[Any]:
        """为任务选择合适的 Agent"""
        # 优先按渠道匹配
        channel = task.get("channel")
        if channel and channel in self.agents:
            return self.agents[channel]
        
        # 按任务类型匹配
        task_type = task.get("type")
        if task_type:
            # 消息类任务
            if "message" in task_type:
                if "feishu" in task.get("source", ""):
                    return self.agents.get("feishu_agent")
                elif "qq" in task.get("source", ""):
                    return self.agents.get("qq_agent")
                elif "wecom" in task.get("source", ""):
                    return self.agents.get("wecom_agent")
        
        # 默认返回第一个可用的 Agent
        for agent in self.agents.values():
            if isinstance(agent, object):  # 简单的可用性检查
                return agent
        
        return None
    
    async def distribute(self, task: Dict) -> Dict:
        """分发任务"""
        self.stats["total_tasks"] += 1
        self.stats["pending_tasks"] += 1
        
        # 获取合适的 Agent
        agent = self.get_agent_for_task(task)
        
        if not agent:
            self.stats["pending_tasks"] -= 1
            self.stats["failed_tasks"] += 1
            return {
                "success": False,
                "error": "没有可用的 Agent",
                "task_id": task.get("id")
            }
        
        # 并发控制
        async with self.semaphore:
            try:
                # 执行任务
                result = await agent.handle(task)
                
                self.stats["pending_tasks"] -= 1
                if result.get("success"):
                    self.stats["successful_tasks"] += 1
                else:
                    self.stats["failed_tasks"] += 1
                
                return result
            
            except Exception as e:
                self.stats["pending_tasks"] -= 1
                self.stats["failed_tasks"] += 1
                return {
                    "success": False,
                    "error": str(e),
                    "task_id": task.get("id")
                }
    
    async def distribute_batch(self, tasks: List[Dict]) -> List[Dict]:
        """批量分发任务"""
        # 创建所有任务
        coroutines = [self.distribute(task) for task in tasks]
        
        # 并发执行
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        return results
    
    async def distribute_with_priority(self, tasks: List[Dict]) -> List[Dict]:
        """按优先级分发任务"""
        # 按优先级排序
        priority_order = {
            "urgent": 0,
            "high": 1,
            "normal": 2,
            "low": 3
        }
        
        sorted_tasks = sorted(
            tasks,
            key=lambda t: priority_order.get(t.get("priority", "normal"), 2)
        )
        
        # 分发
        return await self.distribute_batch(sorted_tasks)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "registered_agents": len(self.agents),
            "max_concurrent": self.max_concurrent,
            "available_slots": self.max_concurrent - self.stats["pending_tasks"]
        }


class SmartRouter:
    """智能路由器"""
    
    def __init__(self):
        self.routing_rules = []
        self.load_balancer = {}
    
    def add_rule(self, condition: callable, agent_selector: callable):
        """添加路由规则"""
        self.routing_rules.append((condition, agent_selector))
    
    def route(self, task: Dict, available_agents: List) -> Optional[Any]:
        """路由任务到合适的 Agent"""
        for condition, selector in self.routing_rules:
            if condition(task):
                return selector(available_agents, task)
        
        # 默认路由：负载均衡
        return self._load_balance(available_agents, task)
    
    def _load_balance(self, agents: List, task: Dict) -> Optional[Any]:
        """负载均衡"""
        if not agents:
            return None
        
        # 选择任务数最少的 Agent
        agent_stats = [(agent, agent.task_count) for agent in agents]
        agent_stats.sort(key=lambda x: x[1])
        
        return agent_stats[0][0]


# 全局实例
_distributor = None
_router = None


def get_distributor(max_concurrent: int = 100) -> TaskDistributor:
    """获取任务分发器实例"""
    global _distributor
    if _distributor is None:
        _distributor = TaskDistributor(max_concurrent)
    return _distributor


def get_router() -> SmartRouter:
    """获取路由器实例"""
    global _router
    if _router is None:
        _router = SmartRouter()
    return _router


async def demo():
    """演示任务分发"""
    print("="*60)
    print("📦 任务分发器演示")
    print("="*60)
    
    # 创建分发器
    distributor = get_distributor(max_concurrent=10)
    
    # 注册 Agent
    from .feishu import get_feishu_agent
    from .qq import get_qq_agent
    
    feishu = get_feishu_agent()
    qq = get_qq_agent()
    
    distributor.register_agent(feishu)
    distributor.register_agent(qq)
    
    # 创建测试任务
    tasks = [
        {"id": "1", "type": "message", "channel": "feishu", "content": "你好"},
        {"id": "2", "type": "message", "channel": "qqbot", "content": "Hello"},
        {"id": "3", "type": "reminder", "channel": "feishu", "text": "提醒"},
    ]
    
    # 分发任务
    print(f"\n📤 分发 {len(tasks)} 个任务...")
    results = await distributor.distribute_batch(tasks)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success") else "❌"
        print(f"   {status} 任务 {i}: {result.get('result', result.get('error'))}")
    
    # 查看统计
    stats = distributor.get_stats()
    print(f"\n📊 统计：{stats}")
    
    print("\n✨ 演示完成！")


if __name__ == "__main__":
    asyncio.run(demo())
