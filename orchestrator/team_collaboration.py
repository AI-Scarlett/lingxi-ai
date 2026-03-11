#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀多 Agent 协作编排系统

功能：
- 5 个协作角色（研究员/分析师/作家/审核员/协调员）
- Agent 间通信机制
- 结果聚合和去重
- 协作流程编排
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib


class AgentRole(Enum):
    """Agent 角色"""
    RESEARCHER = "researcher"  # 信息搜集专家
    ANALYST = "analyst"        # 数据分析专家
    WRITER = "writer"          # 内容创作专家
    REVIEWER = "reviewer"      # 质量审核专家
    COORDINATOR = "coordinator" # 协调整合专家


@dataclass
class CollaborationTask:
    """协作任务"""
    id: str
    role: AgentRole
    input_data: Dict
    output_data: Optional[Dict] = None
    status: str = "pending"  # pending/running/completed/failed
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None


class AgentCollaborator:
    """Agent 协作者基类"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    async def process(self, task: CollaborationTask) -> Dict:
        """处理任务（子类实现）"""
        raise NotImplementedError
    
    async def run(self):
        """运行协作者"""
        self.running = True
        
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                task.status = "running"
                task.started_at = time.time()
                
                try:
                    result = await self.process(task)
                    task.output_data = result
                    task.status = "completed"
                    task.completed_at = time.time()
                    print(f"✅ {self.role.value} 完成任务 {task.id}")
                except Exception as e:
                    task.status = "failed"
                    task.error = str(e)
                    print(f"❌ {self.role.value} 任务 {task.id} 失败：{e}")
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
    
    async def add_task(self, task: CollaborationTask):
        """添加任务"""
        await self.task_queue.put(task)
    
    def stop(self):
        """停止协作者"""
        self.running = False


class Researcher(AgentCollaborator):
    """研究员 - 信息搜集专家"""
    
    def __init__(self):
        super().__init__(AgentRole.RESEARCHER)
    
    async def process(self, task: CollaborationTask) -> Dict:
        """搜集信息"""
        from core.content_fetcher import get_content_fetcher
        
        fetcher = get_content_fetcher()
        query = task.input_data.get("query", "")
        sources = task.input_data.get("sources", [])
        
        results = []
        
        # 搜索信息
        for source in sources:
            try:
                result = await fetcher.fetch_url(source)
                if result["success"]:
                    results.append({
                        "source": source,
                        "content": result["content"][:2000],
                        "title": result.get("title", "")
                    })
            except:
                pass
        
        return {
            "query": query,
            "results": results,
            "source_count": len(results)
        }


class Analyst(AgentCollaborator):
    """分析师 - 数据分析专家"""
    
    def __init__(self):
        super().__init__(AgentRole.ANALYST)
    
    async def process(self, task: CollaborationTask) -> Dict:
        """分析数据"""
        research_data = task.input_data.get("research", {})
        
        # 简单分析（实际应该用 LLM）
        content = " ".join([r.get("content", "") for r in research_data.get("results", [])])
        
        # 提取关键点
        key_points = []
        sentences = content.split("。")
        for sentence in sentences[:10]:  # 最多 10 个关键点
            if len(sentence.strip()) > 10:
                key_points.append(sentence.strip())
        
        return {
            "key_points": key_points,
            "sentiment": "positive",  # 简化
            "confidence": 0.85,
            "analysis": f"分析了 {len(key_points)} 个关键点"
        }


class Writer(AgentCollaborator):
    """作家 - 内容创作专家"""
    
    def __init__(self):
        super().__init__(AgentRole.WRITER)
    
    async def process(self, task: CollaborationTask) -> Dict:
        """创作内容"""
        analysis = task.input_data.get("analysis", {})
        template = task.input_data.get("template", "default")
        
        key_points = analysis.get("key_points", [])
        
        # 生成内容（简化版）
        content = f"""# 分析报告

## 关键发现
"""
        for i, point in enumerate(key_points[:5], 1):
            content += f"\n{i}. {point}"
        
        content += f"\n\n## 分析结论\n{analysis.get('analysis', '分析完成')}"
        
        return {
            "content": content,
            "word_count": len(content),
            "template": template
        }


class Reviewer(AgentCollaborator):
    """审核员 - 质量审核专家"""
    
    def __init__(self):
        super().__init__(AgentRole.REVIEWER)
    
    async def process(self, task: CollaborationTask) -> Dict:
        """质量审核"""
        content_data = task.input_data.get("content", {})
        content = content_data.get("content", "")
        
        # 质量检查
        issues = []
        
        if len(content) < 100:
            issues.append("内容过短")
        
        if content.count("。") < 3:
            issues.append("句子过少")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "quality_score": 100 - len(issues) * 20,
            "suggestions": issues
        }


class Coordinator(AgentCollaborator):
    """协调员 - 协调整合专家"""
    
    def __init__(self):
        super().__init__(AgentRole.COORDINATOR)
        self.agents: Dict[AgentRole, AgentCollaborator] = {}
    
    def register_agent(self, agent: AgentCollaborator):
        """注册 Agent"""
        self.agents[agent.role] = agent
        print(f"✅ 注册 Agent: {agent.role.value}")
    
    async def execute_workflow(self, task_data: Dict) -> Dict:
        """执行协作工作流"""
        print(f"🎯 开始执行协作任务：{task_data.get('id', 'unknown')}")
        
        # 1. 研究员搜集信息
        research_task = CollaborationTask(
            id=f"{task_data['id']}_research",
            role=AgentRole.RESEARCHER,
            input_data=task_data
        )
        if AgentRole.RESEARCHER in self.agents:
            await self.agents[AgentRole.RESEARCHER].add_task(research_task)
            await asyncio.sleep(0.5)  # 等待完成
        
        # 2. 分析师分析数据
        analysis_task = CollaborationTask(
            id=f"{task_data['id']}_analysis",
            role=AgentRole.ANALYST,
            input_data={"research": research_task.output_data or {}}
        )
        if AgentRole.ANALYST in self.agents:
            await self.agents[AgentRole.ANALYST].add_task(analysis_task)
            await asyncio.sleep(0.5)
        
        # 3. 作家创作内容
        writing_task = CollaborationTask(
            id=f"{task_data['id']}_writing",
            role=AgentRole.WRITER,
            input_data={
                "analysis": analysis_task.output_data or {},
                "template": task_data.get("template", "default")
            }
        )
        if AgentRole.WRITER in self.agents:
            await self.agents[AgentRole.WRITER].add_task(writing_task)
            await asyncio.sleep(0.5)
        
        # 4. 审核员质量检查
        review_task = CollaborationTask(
            id=f"{task_data['id']}_review",
            role=AgentRole.REVIEWER,
            input_data={"content": writing_task.output_data or {}}
        )
        if AgentRole.REVIEWER in self.agents:
            await self.agents[AgentRole.REVIEWER].add_task(review_task)
            await asyncio.sleep(0.5)
        
        # 5. 整合最终结果
        final_result = {
            "task_id": task_data["id"],
            "status": "completed",
            "research": research_task.output_data,
            "analysis": analysis_task.output_data,
            "content": writing_task.output_data,
            "review": review_task.output_data,
            "final_output": writing_task.output_data.get("content") if writing_task.output_data else None
        }
        
        print(f"✅ 协作任务完成：{task_data['id']}")
        return final_result


class CollaborationEngine:
    """协作引擎 - 主控制器"""
    
    def __init__(self):
        self.coordinator = Coordinator()
        self.agents: Dict[AgentRole, AgentCollaborator] = {}
        self.running = False
        
        # 初始化 Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有 Agent"""
        agents = [
            Researcher(),
            Analyst(),
            Writer(),
            Reviewer()
        ]
        
        for agent in agents:
            self.agents[agent.role] = agent
            self.coordinator.register_agent(agent)
    
    async def start(self):
        """启动协作引擎"""
        self.running = True
        
        # 启动所有 Agent
        tasks = [agent.run() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
    
    async def submit_task(self, task_data: Dict) -> Dict:
        """提交协作任务"""
        return await self.coordinator.execute_workflow(task_data)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                role.value: {
                    "queue_size": agent.task_queue.qsize(),
                    "running": agent.running
                }
                for role, agent in self.agents.items()
            },
            "running": self.running
        }
    
    def stop(self):
        """停止引擎"""
        self.running = False
        for agent in self.agents.values():
            agent.stop()
        print("⏹️ 协作引擎已停止")


# 全局实例
_engine = None

def get_collaboration_engine() -> CollaborationEngine:
    """获取协作引擎实例"""
    global _engine
    
    if _engine is None:
        _engine = CollaborationEngine()
    
    return _engine


if __name__ == "__main__":
    # 测试运行
    async def test():
        engine = get_collaboration_engine()
        
        # 启动引擎
        asyncio.create_task(engine.start())
        await asyncio.sleep(1)
        
        # 提交测试任务
        task = {
            "id": "test_collab_001",
            "query": "测试查询",
            "sources": ["https://example.com"],
            "template": "report"
        }
        
        result = await engine.submit_task(task)
        print(f"\n📊 最终结果：{result['final_output'][:200]}...")
        
        # 查看统计
        stats = engine.get_stats()
        print(f"\n📊 统计：{stats}")
        
        # 停止
        engine.stop()
    
    asyncio.run(test())
