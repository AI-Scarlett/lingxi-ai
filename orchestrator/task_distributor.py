#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀多 Agent 任务分发器

功能：
- 根据任务类型和渠道分发到对应 Agent
- 支持 5 个专用 Agent（feishu/qq/wecom/coding/analysis）
- 智能路由和负载均衡
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time


class AgentType(Enum):
    """Agent 类型"""
    FEISHU = "feishu"
    QQ = "qqbot"
    WECOM = "wecom"
    CODING = "coding"
    ANALYSIS = "analysis"
    GENERAL = "general"


@dataclass
class Task:
    """任务定义"""
    id: str
    type: str
    channel: str
    content: str
    priority: int = 2
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class AgentInfo:
    """Agent 信息"""
    id: str
    type: AgentType
    status: str = "idle"  # idle/busy/error
    current_tasks: int = 0
    max_tasks: int = 10
    success_rate: float = 100.0


class TaskDistributor:
    """任务分发器"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # 初始化 Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化 Agent 池"""
        agent_configs = [
            ("feishu_agent", AgentType.FEISHU, 15),
            ("qq_agent", AgentType.QQ, 15),
            ("wecom_agent", AgentType.WECOM, 15),
            ("coding_agent", AgentType.CODING, 5),
            ("analysis_agent", AgentType.ANALYSIS, 5),
            ("general_agent", AgentType.GENERAL, 20),
        ]
        
        for agent_id, agent_type, max_tasks in agent_configs:
            self.agents[agent_id] = AgentInfo(
                id=agent_id,
                type=agent_type,
                max_tasks=max_tasks
            )
        
        print(f"✅ 初始化 {len(self.agents)} 个 Agent")
    
    async def add_task(self, task: Task) -> str:
        """添加任务到队列"""
        await self.task_queue.put(task)
        print(f"📝 任务入队：{task.id} (渠道：{task.channel})")
        return task.id
    
    async def distribute_tasks(self):
        """分发任务到 Agent"""
        self.running = True
        
        while self.running:
            try:
                # 获取任务
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # 选择最佳 Agent
                agent = self._select_best_agent(task)
                
                if agent:
                    # 分发任务
                    asyncio.create_task(self._execute_task(agent, task))
                else:
                    # 没有可用 Agent，重新入队
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.5)
            
            except asyncio.TimeoutError:
                # 队列为空，等待
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ 分发任务失败：{e}")
                await asyncio.sleep(1.0)
    
    def _select_best_agent(self, task: Task) -> Optional[AgentInfo]:
        """选择最佳 Agent"""
        # 根据渠道匹配 Agent
        channel_agent_map = {
            "feishu": "feishu_agent",
            "qqbot": "qq_agent",
            "wecom": "wecom_agent",
            "coding": "coding_agent",
            "analysis": "analysis_agent"
        }
        
        # 优先选择渠道匹配的 Agent
        if task.channel in channel_agent_map:
            agent_id = channel_agent_map[task.channel]
            agent = self.agents.get(agent_id)
            
            if agent and agent.status == "idle" and agent.current_tasks < agent.max_tasks:
                return agent
        
        # 渠道 Agent 不可用，选择通用 Agent
        general_agent = self.agents.get("general_agent")
        if general_agent and general_agent.status == "idle" and general_agent.current_tasks < general_agent.max_tasks:
            return general_agent
        
        # 所有 Agent 都忙，选择负载最低的
        available_agents = [
            a for a in self.agents.values()
            if a.status == "idle" and a.current_tasks < a.max_tasks
        ]
        
        if available_agents:
            return min(available_agents, key=lambda a: a.current_tasks)
        
        return None
    
    async def _execute_task(self, agent: AgentInfo, task: Task):
        """执行任务"""
        # 更新 Agent 状态
        agent.current_tasks += 1
        agent.status = "busy"
        
        try:
            print(f"🤖 Agent {agent.id} 开始执行任务 {task.id}")
            
            # 模拟任务执行（实际会调用对应 Agent 的处理函数）
            await asyncio.sleep(0.1)
            
            # 任务完成
            agent.success_rate = min(100.0, agent.success_rate + 0.1)
            print(f"✅ Agent {agent.id} 完成任务 {task.id}")
            
        except Exception as e:
            print(f"❌ Agent {agent.id} 任务 {task.id} 失败：{e}")
            agent.success_rate = max(0.0, agent.success_rate - 5.0)
        
        finally:
            # 更新 Agent 状态
            agent.current_tasks -= 1
            if agent.current_tasks == 0:
                agent.status = "idle"
            
            # 标记任务完成
            self.task_queue.task_done()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                agent_id: {
                    "status": agent.status,
                    "current_tasks": agent.current_tasks,
                    "max_tasks": agent.max_tasks,
                    "success_rate": agent.success_rate
                }
                for agent_id, agent in self.agents.items()
            },
            "queue_size": self.task_queue.qsize(),
            "running": self.running
        }
    
    def stop(self):
        """停止分发器"""
        self.running = False
        print("⏹️ 任务分发器已停止")


# 全局实例
_distributor = None

def get_task_distributor() -> TaskDistributor:
    """获取任务分发器实例"""
    global _distributor
    
    if _distributor is None:
        _distributor = TaskDistributor()
    
    return _distributor


if __name__ == "__main__":
    # 测试运行
    async def test():
        distributor = get_task_distributor()
        
        # 启动分发器
        asyncio.create_task(distributor.distribute_tasks())
        
        # 添加测试任务
        for i in range(10):
            task = Task(
                id=f"task_{i}",
                type="message",
                channel="feishu" if i % 2 == 0 else "qqbot",
                content=f"测试任务 {i}"
            )
            await distributor.add_task(task)
        
        # 等待任务完成
        await distributor.task_queue.join()
        
        # 查看统计
        stats = distributor.get_stats()
        print(f"\n📊 统计信息：{stats}")
        
        # 停止
        distributor.stop()
    
    asyncio.run(test())
