#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀工作流可视化编辑器

功能：
- 拖拽式工作流构建
- 可视化 DAG 编辑器
- 条件分支配置
- 循环配置
- 实时预览
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
import time


@dataclass
class WorkflowNode:
    """工作流节点"""
    id: str
    type: str  # task/condition/loop/start/end
    name: str
    config: Dict = field(default_factory=dict)
    position: Dict = field(default_factory=lambda: {"x": 0, "y": 0})
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class WorkflowEdge:
    """工作流边"""
    id: str
    source: str
    target: str
    condition: Optional[str] = None


@dataclass
class Workflow:
    """工作流定义"""
    id: str
    name: str
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: str = "1.0"


class WorkflowEditor:
    """工作流编辑器"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.node_templates = self._init_node_templates()
    
    def _init_node_templates(self) -> Dict:
        """初始化节点模板"""
        return {
            "task": {
                "name": "任务节点",
                "icon": "📝",
                "config": {
                    "agent": "general",
                    "timeout": 300
                }
            },
            "condition": {
                "name": "条件分支",
                "icon": "🔀",
                "config": {
                    "condition": "result.status == 'success'",
                    "true_branch": "",
                    "false_branch": ""
                }
            },
            "loop": {
                "name": "循环",
                "icon": "🔄",
                "config": {
                    "max_iterations": 10,
                    "condition": "has_more"
                }
            },
            "start": {
                "name": "开始",
                "icon": "🚀",
                "config": {}
            },
            "end": {
                "name": "结束",
                "icon": "✅",
                "config": {}
            }
        }
    
    def create_workflow(self, name: str) -> Workflow:
        """创建工作流"""
        workflow_id = f"workflow_{int(time.time()*1000)}"
        
        workflow = Workflow(
            id=workflow_id,
            name=name
        )
        
        # 添加开始和结束节点
        start_node = WorkflowNode(
            id="start",
            type="start",
            name="开始",
            config={},
            position={"x": 100, "y": 300}
        )
        
        end_node = WorkflowNode(
            id="end",
            type="end",
            name="结束",
            config={},
            position={"x": 800, "y": 300}
        )
        
        workflow.nodes = [start_node, end_node]
        self.workflows[workflow_id] = workflow
        
        print(f"✅ 创建工作流：{name} ({workflow_id})")
        return workflow
    
    def add_node(self, workflow_id: str, node_type: str, name: str, 
                 position: Dict, config: Dict = None) -> WorkflowNode:
        """添加节点"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在：{workflow_id}")
        
        node_id = f"node_{len(workflow.nodes)}_{int(time.time()*1000)}"
        
        node = WorkflowNode(
            id=node_id,
            type=node_type,
            name=name,
            config=config or {},
            position=position
        )
        
        workflow.nodes.append(node)
        workflow.updated_at = time.time()
        
        print(f"✅ 添加节点：{name} ({node_id})")
        return node
    
    def connect_nodes(self, workflow_id: str, source_id: str, 
                     target_id: str, condition: str = None) -> WorkflowEdge:
        """连接节点"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在：{workflow_id}")
        
        edge_id = f"edge_{len(workflow.edges)}"
        
        edge = WorkflowEdge(
            id=edge_id,
            source=source_id,
            target=target_id,
            condition=condition
        )
        
        workflow.edges.append(edge)
        workflow.updated_at = time.time()
        
        print(f"✅ 连接节点：{source_id} → {target_id}")
        return edge
    
    def validate_workflow(self, workflow_id: str) -> Dict:
        """验证工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"valid": False, "error": "工作流不存在"}
        
        errors = []
        
        # 检查是否有开始节点
        start_nodes = [n for n in workflow.nodes if n.type == "start"]
        if not start_nodes:
            errors.append("缺少开始节点")
        
        # 检查是否有结束节点
        end_nodes = [n for n in workflow.nodes if n.type == "end"]
        if not end_nodes:
            errors.append("缺少结束节点")
        
        # 检查节点连接
        node_ids = {n.id for n in workflow.nodes}
        for edge in workflow.edges:
            if edge.source not in node_ids:
                errors.append(f"边的源节点不存在：{edge.source}")
            if edge.target not in node_ids:
                errors.append(f"边的目标节点不存在：{edge.target}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "node_count": len(workflow.nodes),
            "edge_count": len(workflow.edges)
        }
    
    def export_workflow(self, workflow_id: str) -> str:
        """导出工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在：{workflow_id}")
        
        workflow_data = {
            "id": workflow.id,
            "name": workflow.name,
            "version": workflow.version,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "config": n.config,
                    "position": n.position
                }
                for n in workflow.nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "condition": e.condition
                }
                for e in workflow.edges
            ]
        }
        
        return json.dumps(workflow_data, indent=2, ensure_ascii=False)
    
    def import_workflow(self, workflow_json: str) -> Workflow:
        """导入工作流"""
        workflow_data = json.loads(workflow_json)
        
        workflow = Workflow(
            id=workflow_data["id"],
            name=workflow_data["name"],
            version=workflow_data.get("version", "1.0"),
            created_at=workflow_data.get("created_at", time.time()),
            updated_at=workflow_data.get("updated_at", time.time())
        )
        
        # 导入节点
        for node_data in workflow_data.get("nodes", []):
            node = WorkflowNode(
                id=node_data["id"],
                type=node_data["type"],
                name=node_data["name"],
                config=node_data.get("config", {}),
                position=node_data.get("position", {"x": 0, "y": 0})
            )
            workflow.nodes.append(node)
        
        # 导入边
        for edge_data in workflow_data.get("edges", []):
            edge = WorkflowEdge(
                id=edge_data["id"],
                source=edge_data["source"],
                target=edge_data["target"],
                condition=edge_data.get("condition")
            )
            workflow.edges.append(edge)
        
        self.workflows[workflow.id] = workflow
        
        print(f"✅ 导入工作流：{workflow.name}")
        return workflow
    
    def get_workflow_html(self, workflow_id: str) -> str:
        """生成工作流可视化 HTML"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return "工作流不存在"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>工作流：{workflow.name}</title>
    <style>
        .workflow-canvas {{
            width: 100%;
            height: 600px;
            background: #f5f5f5;
            position: relative;
        }}
        .node {{
            position: absolute;
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            min-width: 150px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .node.start {{ border-color: #4ade80; }}
        .node.end {{ border-color: #f87171; }}
        .node.condition {{ border-color: #fbbf24; }}
        .node.loop {{ border-color: #a78bfa; }}
        .node-icon {{ font-size: 24px; margin-bottom: 5px; }}
        .node-name {{ font-weight: 600; color: #333; }}
        .edge {{
            position: absolute;
            height: 2px;
            background: #999;
            transform-origin: 0 0;
        }}
    </style>
</head>
<body>
    <h1>工作流：{workflow.name}</h1>
    <div class="workflow-canvas" id="canvas">
"""
        
        # 添加节点
        for node in workflow.nodes:
            template = self.node_templates.get(node.type, {})
            icon = template.get("icon", "📝")
            
            html += f"""
        <div class="node {node.type}" style="left: {node.position['x']}px; top: {node.position['y']}px;">
            <div class="node-icon">{icon}</div>
            <div class="node-name">{node.name}</div>
        </div>
"""
        
        # TODO: 添加边（需要 SVG 或 Canvas）
        
        html += """
    </div>
    <script>
        // TODO: 实现拖拽功能
        console.log('工作流可视化');
    </script>
</body>
</html>
"""
        
        return html


# 全局编辑器
_editor = None

def get_workflow_editor() -> WorkflowEditor:
    """获取工作流编辑器实例"""
    global _editor
    
    if _editor is None:
        _editor = WorkflowEditor()
    
    return _editor


if __name__ == "__main__":
    # 测试运行
    editor = get_workflow_editor()
    
    # 创建工作流
    workflow = editor.create_workflow("新闻监控工作流")
    
    # 添加节点
    editor.add_node(
        workflow.id,
        "task",
        "获取新闻",
        {"x": 250, "y": 200},
        {"agent": "researcher", "query": "最新新闻"}
    )
    
    editor.add_node(
        workflow.id,
        "condition",
        "检查质量",
        {"x": 400, "y": 300},
        {"condition": "quality_score > 80"}
    )
    
    editor.add_node(
        workflow.id,
        "task",
        "发布新闻",
        {"x": 600, "y": 200},
        {"agent": "publisher", "channel": "wechat"}
    )
    
    # 连接节点
    editor.connect_nodes(workflow.id, "start", workflow.nodes[2].id)
    editor.connect_nodes(workflow.id, workflow.nodes[2].id, workflow.nodes[3].id)
    editor.connect_nodes(
        workflow.id,
        workflow.nodes[3].id,
        workflow.nodes[4].id,
        "result.quality > 80"
    )
    editor.connect_nodes(workflow.id, workflow.nodes[4].id, "end")
    
    # 验证工作流
    validation = editor.validate_workflow(workflow.id)
    print(f"\n📊 验证结果：{validation}")
    
    # 导出工作流
    workflow_json = editor.export_workflow(workflow.id)
    print(f"\n📄 导出工作流:\n{workflow_json[:500]}...")
    
    # 生成 HTML
    html = editor.get_workflow_html(workflow.id)
    print(f"\n🎨 生成 HTML: {len(html)} 字符")
