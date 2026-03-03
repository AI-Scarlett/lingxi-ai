#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 高级编排器（复杂任务方法论）
心有灵犀，一点就通

基于"复杂任务方法论"优化：
1. 任务分层 - 战略层/战术层/执行层
2. 依赖管理 - 任务间的先后关系
3. 资源调度 - 智能分配计算资源
4. 容错机制 - 失败重试和降级策略
5. 进度追踪 - 实时反馈任务进展
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from task_manager import TaskManager, TaskInfo, TaskStatus, generate_task_id, get_task_manager
from async_executor import AsyncExecutor, get_executor
from orchestrator_async import AsyncOrchestrator

# ==================== 任务分层定义 ====================

class TaskLayer(Enum):
    """任务层级"""
    STRATEGIC = "strategic"      # 战略层 - 目标定义
    TACTICAL = "tactical"        # 战术层 - 任务规划
    EXECUTION = "execution"      # 执行层 - 具体操作

class DependencyType(Enum):
    """依赖类型"""
    SEQUENTIAL = "sequential"    # 顺序依赖 - A 完成后执行 B
    PARALLEL = "parallel"        # 并行依赖 - A 和 B 可同时执行
    CONDITIONAL = "conditional"  # 条件依赖 - 满足条件才执行

@dataclass
class TaskNode:
    """任务节点（DAG 中的节点）"""
    id: str
    layer: TaskLayer
    description: str
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务 ID
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0
    estimated_duration: int = 0  # 预估耗时（秒）
    actual_duration: int = 0

@dataclass
class TaskGraph:
    """任务图（DAG）"""
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_task_ids]
    
    def add_node(self, node: TaskNode):
        """添加任务节点"""
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []
        
        # 建立边
        for dep_id in node.dependencies:
            if dep_id not in self.edges:
                self.edges[dep_id] = []
            self.edges[dep_id].append(node.id)
    
    def get_ready_tasks(self) -> List[TaskNode]:
        """获取所有可执行的任务（依赖已满足）"""
        ready = []
        for node in self.nodes.values():
            if node.status != TaskStatus.PENDING:
                continue
            
            # 检查所有依赖是否完成
            deps_satisfied = True
            for dep_id in node.dependencies:
                dep_node = self.nodes.get(dep_id)
                if not dep_node or dep_node.status != TaskStatus.COMPLETED:
                    deps_satisfied = False
                    break
            
            if deps_satisfied:
                ready.append(node)
        
        # 按优先级排序
        return sorted(ready, key=lambda x: x.priority, reverse=True)
    
    def is_complete(self) -> bool:
        """检查所有任务是否完成"""
        return all(
            node.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            for node in self.nodes.values()
        )
    
    def get_progress(self) -> Tuple[int, int]:
        """获取进度 (已完成，总数)"""
        completed = sum(
            1 for node in self.nodes.values()
            if node.status == TaskStatus.COMPLETED
        )
        return completed, len(self.nodes)

# ==================== 高级编排器 ====================

class AdvancedOrchestrator(AsyncOrchestrator):
    """灵犀 - 高级智慧调度系统
    
    基于复杂任务方法论：
    1. 任务分层 - 战略/战术/执行三层
    2. DAG 调度 - 有向无环图管理依赖
    3. 智能重试 - 失败自动重试
    4. 进度追踪 - 实时反馈
    5. 资源优化 - 并发控制
    """
    
    def __init__(self, max_concurrency: int = 5):
        super().__init__()
        self.max_concurrency = max_concurrency  # 最大并发数
        self.task_graphs: Dict[str, TaskGraph] = {}  # 任务图缓存
    
    async def execute_complex_task(
        self,
        user_input: str,
        user_id: str,
        channel: str = "qqbot"
    ) -> str:
        """执行复杂任务
        
        Args:
            user_input: 用户输入
            user_id: 用户 ID
            channel: 通知渠道
            
        Returns:
            任务接受确认
        """
        print(f"\n🎯 复杂任务处理：{user_input[:100]}")
        
        # 1. 战略层 - 理解目标
        strategic_nodes = await self._strategic_analysis(user_input, user_id)
        
        # 2. 战术层 - 规划任务
        tactical_nodes = await self._tactical_planning(strategic_nodes, user_input)
        
        # 3. 执行层 - 拆解操作
        execution_nodes = await self._execution_breakdown(tactical_nodes, user_input)
        
        # 4. 构建任务图
        all_nodes = strategic_nodes + tactical_nodes + execution_nodes
        task_graph = self._build_task_graph(all_nodes)
        
        # 5. 创建主任务
        main_task_id = generate_task_id("complex")
        main_task = TaskInfo(
            id=main_task_id,
            type="complex-task",
            description=user_input[:200],
            user_id=user_id,
            channel=channel,
            priority=5
        )
        self.task_manager.register(main_task)
        
        # 6. 保存任务图
        self.task_graphs[main_task_id] = task_graph
        
        # 7. 立即回复用户
        reply = self._generate_progress_report(main_task_id, task_graph)
        
        # 8. 后台执行任务图
        asyncio.create_task(
            self._execute_task_graph(main_task_id, task_graph, user_id, channel)
        )
        
        return reply
    
    async def _strategic_analysis(
        self,
        user_input: str,
        user_id: str
    ) -> List[TaskNode]:
        """战略层分析 - 理解用户目标
        
        输出：1-2 个战略目标节点
        """
        nodes = []
        
        # 目标定义节点
        goal_node = TaskNode(
            id=generate_task_id("goal"),
            layer=TaskLayer.STRATEGIC,
            description=f"理解用户需求：{user_input[:100]}",
            priority=10,
            estimated_duration=2
        )
        nodes.append(goal_node)
        
        return nodes
    
    async def _tactical_planning(
        self,
        strategic_nodes: List[TaskNode],
        user_input: str
    ) -> List[TaskNode]:
        """战术层规划 - 拆解为子任务
        
        输出：3-5 个战术任务节点
        """
        nodes = []
        
        # 示例：根据输入类型规划
        if "发布" in user_input or "公众号" in user_input:
            # 发布任务规划
            nodes.extend([
                TaskNode(
                    id=generate_task_id("plan"),
                    layer=TaskLayer.TACTICAL,
                    description="规划发布内容",
                    dependencies=[strategic_nodes[0].id],
                    dependency_type=DependencyType.SEQUENTIAL,
                    priority=8,
                    estimated_duration=5
                ),
                TaskNode(
                    id=generate_task_id("prepare"),
                    layer=TaskLayer.TACTICAL,
                    description="准备发布素材",
                    dependencies=[strategic_nodes[0].id],
                    dependency_type=DependencyType.PARALLEL,
                    priority=8,
                    estimated_duration=10
                ),
                TaskNode(
                    id=generate_task_id("publish"),
                    layer=TaskLayer.TACTICAL,
                    description="执行发布操作",
                    dependencies=[f"{nodes[0].id}", f"{nodes[1].id}"] if nodes else [strategic_nodes[0].id],
                    dependency_type=DependencyType.SEQUENTIAL,
                    priority=9,
                    estimated_duration=30
                )
            ])
        else:
            # 通用任务规划
            nodes.append(TaskNode(
                id=generate_task_id("plan"),
                layer=TaskLayer.TACTICAL,
                description="任务规划",
                dependencies=[strategic_nodes[0].id] if strategic_nodes else [],
                priority=8,
                estimated_duration=5
            ))
        
        return nodes
    
    async def _execution_breakdown(
        self,
        tactical_nodes: List[TaskNode],
        user_input: str
    ) -> List[TaskNode]:
        """执行层拆解 - 具体操作步骤
        
        输出：多个执行节点
        """
        nodes = []
        
        # 为每个战术任务生成执行节点
        for tactical in tactical_nodes:
            if "发布" in tactical.description or "publish" in tactical.description.lower():
                # 发布相关的执行步骤
                nodes.extend([
                    TaskNode(
                        id=generate_task_id("exec"),
                        layer=TaskLayer.EXECUTION,
                        description="生成文案内容",
                        dependencies=[tactical.id],
                        priority=7,
                        estimated_duration=15
                    ),
                    TaskNode(
                        id=generate_task_id("exec"),
                        layer=TaskLayer.EXECUTION,
                        description="准备图片/素材",
                        dependencies=[tactical.id],
                        priority=7,
                        estimated_duration=20
                    ),
                    TaskNode(
                        id=generate_task_id("exec"),
                        layer=TaskLayer.EXECUTION,
                        description="调用发布 API",
                        dependencies=[tactical.id],
                        priority=9,
                        estimated_duration=30
                    )
                ])
            else:
                # 通用执行节点
                nodes.append(TaskNode(
                    id=generate_task_id("exec"),
                    layer=TaskLayer.EXECUTION,
                    description=f"执行：{tactical.description}",
                    dependencies=[tactical.id],
                    priority=7,
                    estimated_duration=10
                ))
        
        return nodes
    
    def _build_task_graph(self, nodes: List[TaskNode]) -> TaskGraph:
        """构建任务图"""
        graph = TaskGraph()
        for node in nodes:
            graph.add_node(node)
        return graph
    
    async def _execute_task_graph(
        self,
        main_task_id: str,
        graph: TaskGraph,
        user_id: str,
        channel: str
    ):
        """执行任务图（DAG 调度）"""
        print(f"🚀 开始执行任务图：{main_task_id}")
        
        running_tasks: Set[str] = set()
        
        while not graph.is_complete():
            # 获取可执行的任务
            ready_tasks = graph.get_ready_tasks()
            
            # 并发控制
            available_slots = self.max_concurrency - len(running_tasks)
            tasks_to_start = ready_tasks[:available_slots]
            
            # 启动任务
            for task_node in tasks_to_start:
                if task_node.id in running_tasks:
                    continue
                
                task_node.status = TaskStatus.RUNNING
                running_tasks.add(task_node.id)
                
                # 异步执行
                asyncio.create_task(
                    self._execute_single_node(
                        main_task_id, task_node, user_id, channel, graph
                    )
                )
            
            # 等待一小段时间
            await asyncio.sleep(1)
        
        # 所有任务完成
        print(f"✅ 任务图执行完成：{main_task_id}")
        
        # 更新主任务状态
        completed, total = graph.get_progress()
        self.task_manager.update(
            main_task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now().timestamp() * 1000,
            result={"completed": completed, "total": total}
        )
    
    async def _execute_single_node(
        self,
        main_task_id: str,
        node: TaskNode,
        user_id: str,
        channel: str,
        graph: TaskGraph
    ):
        """执行单个任务节点"""
        print(f"⚙️ 执行任务节点：{node.id} - {node.description}")
        
        start_time = datetime.now()
        
        try:
            # 根据任务层级执行
            if node.layer == TaskLayer.STRATEGIC:
                result = await self._execute_strategic_task(node)
            elif node.layer == TaskLayer.TACTICAL:
                result = await self._execute_tactical_task(node)
            else:
                result = await self._execute_execution_task(node, user_id, channel)
            
            node.status = TaskStatus.COMPLETED
            node.result = result
            node.actual_duration = int((datetime.now() - start_time).total_seconds())
            
        except Exception as e:
            node.error = str(e)
            node.retry_count += 1
            
            # 重试机制
            if node.retry_count < node.max_retries:
                print(f"⚠️ 任务失败，重试 {node.retry_count}/{node.max_retries}: {node.id}")
                node.status = TaskStatus.PENDING
                asyncio.create_task(
                    self._execute_single_node(main_task_id, node, user_id, channel, graph)
                )
                return
            else:
                node.status = TaskStatus.FAILED
                node.actual_duration = int((datetime.now() - start_time).total_seconds())
        
        print(f"{'✅' if node.status == TaskStatus.COMPLETED else '❌'} 任务节点完成：{node.id}")
    
    async def _execute_strategic_task(self, node: TaskNode) -> Dict[str, Any]:
        """执行战略层任务"""
        # 战略层任务通常是分析、理解
        await asyncio.sleep(node.estimated_duration)
        return {"layer": "strategic", "status": "completed"}
    
    async def _execute_tactical_task(self, node: TaskNode) -> Dict[str, Any]:
        """执行战术层任务"""
        # 战术层任务是规划、协调
        await asyncio.sleep(node.estimated_duration)
        return {"layer": "tactical", "status": "completed"}
    
    async def _execute_execution_task(
        self,
        node: TaskNode,
        user_id: str,
        channel: str
    ) -> Dict[str, Any]:
        """执行执行层任务"""
        # 执行层任务是具体操作
        executor = get_executor()
        
        task_id = await executor.execute(
            task_type="execution-node",
            description=node.description,
            command=f"echo '执行：{node.description}'",
            user_id=user_id,
            channel=channel,
            notify_on_complete=False
        )
        
        # 等待任务完成
        while True:
            status = executor.get_task_status(task_id)
            if status and status['status'] in ['completed', 'failed']:
                break
            await asyncio.sleep(1)
        
        return {"layer": "execution", "task_id": task_id, "status": status['status']}
    
    def _generate_progress_report(
        self,
        main_task_id: str,
        graph: TaskGraph
    ) -> str:
        """生成进度报告"""
        completed, total = graph.get_progress()
        
        # 统计各层级进度
        strategic_completed = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.STRATEGIC and n.status == TaskStatus.COMPLETED
        )
        strategic_total = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.STRATEGIC
        )
        
        tactical_completed = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.TACTICAL and n.status == TaskStatus.COMPLETED
        )
        tactical_total = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.TACTICAL
        )
        
        execution_completed = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.EXECUTION and n.status == TaskStatus.COMPLETED
        )
        execution_total = sum(
            1 for n in graph.nodes.values()
            if n.layer == TaskLayer.EXECUTION
        )
        
        reply = f"""🎯 复杂任务已启动！

📋 任务：{self.task_manager.get(main_task_id).description[:100]}...

📊 总体进度：{completed}/{total}

📈 分层进度:
  🎭 战略层：{strategic_completed}/{strategic_total}
  🗺️ 战术层：{tactical_completed}/{tactical_total}
  ⚙️ 执行层：{execution_completed}/{execution_total}

⏰ 预计耗时：{sum(n.estimated_duration for n in graph.nodes.values())}秒

💡 任务正在后台执行，完成后我会 QQ 通知你～"""
        
        return reply
    
    async def get_task_progress(self, main_task_id: str) -> Dict[str, Any]:
        """获取任务进度"""
        if main_task_id not in self.task_graphs:
            return {"error": "任务不存在"}
        
        graph = self.task_graphs[main_task_id]
        completed, total = graph.get_progress()
        
        # 各层级详情
        layers = {}
        for layer in TaskLayer:
            layer_nodes = [n for n in graph.nodes.values() if n.layer == layer]
            layer_completed = sum(1 for n in layer_nodes if n.status == TaskStatus.COMPLETED)
            layers[layer.value] = {
                "completed": layer_completed,
                "total": len(layer_nodes),
                "running": sum(1 for n in layer_nodes if n.status == TaskStatus.RUNNING),
                "failed": sum(1 for n in layer_nodes if n.status == TaskStatus.FAILED)
            }
        
        return {
            "task_id": main_task_id,
            "progress": f"{completed}/{total}",
            "layers": layers,
            "is_complete": graph.is_complete()
        }

# ==================== 单例 ====================

_advanced_orchestrator: Optional[AdvancedOrchestrator] = None

def get_advanced_orchestrator() -> AdvancedOrchestrator:
    """获取高级编排器实例"""
    global _advanced_orchestrator
    if _advanced_orchestrator is None:
        _advanced_orchestrator = AdvancedOrchestrator()
    return _advanced_orchestrator

# ==================== 测试 ====================

async def test_advanced():
    """测试高级编排器"""
    orch = get_advanced_orchestrator()
    
    # 测试复杂任务
    reply = await orch.execute_complex_task(
        user_input="帮我发布一篇公众号文章，主题是 AI 发展趋势，需要配 3 张图",
        user_id="test_user_123",
        channel="qqbot"
    )
    
    print("\n📋 任务启动回复:")
    print(reply)
    
    # 等待任务执行
    await asyncio.sleep(5)
    
    # 查询进度
    print("\n📊 任务进度:")
    # 这里需要获取 task_id，简化测试
    print("任务执行中...")

if __name__ == "__main__":
    asyncio.run(test_advanced())
