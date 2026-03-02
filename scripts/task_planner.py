#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务规划器 - Task Planner
根据意图拆解任务，生成执行计划
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    HYBRID = "hybrid"          # 混合模式

@dataclass
class TaskNode:
    """任务节点"""
    id: str
    role: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # 优先级，数字越小越优先
    estimated_time: float = 1.0  # 预估时间（秒）

@dataclass
class ExecutionPlan:
    """执行计划"""
    task_id: str
    nodes: List[TaskNode]
    mode: ExecutionMode
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_execution_order(self) -> List[List[TaskNode]]:
        """获取执行顺序（分层）"""
        layers = []
        remaining = self.nodes.copy()
        completed = set()
        
        while remaining:
            # 找出当前层可以执行的任务（依赖已满足）
            current_layer = []
            for node in remaining:
                if all(dep in completed for dep in node.dependencies):
                    current_layer.append(node)
            
            if not current_layer:
                # 没有可执行的任务，说明有循环依赖
                break
            
            # 按优先级排序
            current_layer.sort(key=lambda x: x.priority)
            layers.append(current_layer)
            
            # 标记完成
            for node in current_layer:
                completed.add(node.id)
                remaining.remove(node)
        
        return layers

class TaskPlanner:
    """任务规划器"""
    
    def __init__(self):
        # 任务模板
        self.templates = {
            "content_with_image": [
                {"role": "copywriter", "priority": 0},
                {"role": "image_expert", "priority": 0, "depends_on": []},
                {"role": "operator", "priority": 1, "depends_on": ["copywriter", "image_expert"]}
            ],
            "content_only": [
                {"role": "copywriter", "priority": 0}
            ],
            "image_only": [
                {"role": "image_expert", "priority": 0}
            ],
            "publish_only": [
                {"role": "operator", "priority": 0}
            ],
            "coding": [
                {"role": "coder", "priority": 0}
            ],
            "data_analysis": [
                {"role": "data_analyst", "priority": 0}
            ],
            "search": [
                {"role": "searcher", "priority": 0}
            ]
        }
    
    def create_plan(self, intents: List[Dict], platform: Optional[str] = None) -> ExecutionPlan:
        """创建执行计划"""
        task_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        nodes = []
        
        # 根据意图组合选择模板
        intent_types = [i["type"] for i in intents]
        
        # 内容创作 + 图像生成 + 发布
        if "content_creation" in intent_types and "image_generation" in intent_types:
            nodes = self._build_nodes_from_template(
                "content_with_image", 
                task_id, 
                {"platform": platform}
            )
        # 内容创作 + 发布
        elif "content_creation" in intent_types and "social_publish" in intent_types:
            nodes = self._build_nodes_from_template(
                "content_only",
                task_id,
                {"platform": platform}
            )
            nodes.append(TaskNode(
                id=f"{task_id}_operator",
                role="operator",
                description=f"发布到{platform or '社交平台'}",
                dependencies=[f"{task_id}_copywriter"]
            ))
        # 内容创作
        elif "content_creation" in intent_types:
            nodes = self._build_nodes_from_template("content_only", task_id)
        # 图像生成
        elif "image_generation" in intent_types:
            nodes = self._build_nodes_from_template("image_only", task_id)
        # 编程
        elif "coding" in intent_types:
            nodes = self._build_nodes_from_template("coding", task_id)
        # 数据分析
        elif "data_analysis" in intent_types:
            nodes = self._build_nodes_from_template("data_analysis", task_id)
        # 搜索
        elif "search" in intent_types:
            nodes = self._build_nodes_from_template("search", task_id)
        # 默认：普通对话
        else:
            nodes = [TaskNode(
                id=f"{task_id}_chat",
                role="writer",
                description="处理用户请求"
            )]
        
        # 确定执行模式
        mode = self._determine_mode(nodes)
        
        return ExecutionPlan(task_id=task_id, nodes=nodes, mode=mode)
    
    def _build_nodes_from_template(self, template_name: str, task_id: str, extra_data: Dict = None) -> List[TaskNode]:
        """从模板构建任务节点"""
        template = self.templates.get(template_name, [])
        nodes = []
        
        for i, item in enumerate(template):
            node = TaskNode(
                id=f"{task_id}_{item['role']}_{i}",
                role=item["role"],
                description=f"执行{item['role']}任务",
                priority=item.get("priority", 0),
                input_data=extra_data or {}
            )
            
            if "depends_on" in item:
                node.dependencies = [
                    f"{task_id}_{dep}_{j}" 
                    for j, dep in enumerate(item["depends_on"])
                ]
            
            nodes.append(node)
        
        return nodes
    
    def _determine_mode(self, nodes: List[TaskNode]) -> ExecutionMode:
        """确定执行模式"""
        has_dependencies = any(node.dependencies for node in nodes)
        all_independent = all(not node.dependencies for node in nodes)
        
        if all_independent and len(nodes) > 1:
            return ExecutionMode.PARALLEL
        elif has_dependencies:
            return ExecutionMode.HYBRID
        else:
            return ExecutionMode.SEQUENTIAL
    
    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """优化执行计划"""
        # 按优先级重新排序
        plan.nodes.sort(key=lambda x: x.priority)
        
        # 调整预估时间
        for node in plan.nodes:
            if node.role == "image_expert":
                node.estimated_time = 3.0  # 图像生成较慢
            elif node.role == "coder":
                node.estimated_time = 5.0  # 代码生成可能较慢
            else:
                node.estimated_time = 1.0
        
        return plan
    
    def estimate_total_time(self, plan: ExecutionPlan) -> float:
        """估算总执行时间"""
        layers = plan.get_execution_order()
        
        total_time = 0.0
        for layer in layers:
            # 每层取最长的时间
            layer_time = max(node.estimated_time for node in layer)
            total_time += layer_time
        
        return total_time

# 测试
if __name__ == "__main__":
    planner = TaskPlanner()
    
    # 测试案例
    test_intents = [
        {"type": "content_creation", "confidence": 0.8},
        {"type": "image_generation", "confidence": 0.6},
        {"type": "social_publish", "confidence": 0.7}
    ]
    
    plan = planner.create_plan(test_intents, platform="小红书")
    
    print("执行计划:")
    for node in plan.nodes:
        print(f"  {node.role}: {node.description}")
        if node.dependencies:
            print(f"    依赖: {node.dependencies}")
    
    print(f"\n执行模式: {plan.mode.value}")
    print(f"预估时间: {planner.estimate_total_time(plan):.1f}秒")
    
    print("\n执行顺序:")
    for i, layer in enumerate(plan.get_execution_order()):
        print(f"  第{i+1}层: {[n.role for n in layer]}")