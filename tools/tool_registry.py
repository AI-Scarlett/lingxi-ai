#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具注册表 - Tool Registry
注册和管理所有可用工具/技能
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ToolCategory(Enum):
    """工具分类"""
    IMAGE = "image"           # 图像相关
    CONTENT = "content"       # 内容相关
    SOCIAL = "social"         # 社交相关
    CODE = "code"             # 代码相关
    DATA = "data"             # 数据相关
    SEARCH = "search"         # 搜索相关
    UTILITY = "utility"       # 工具类

@dataclass
class ToolDefinition:
    """工具定义"""
    id: str
    name: str
    description: str
    category: ToolCategory
    skills: List[str]
    models: List[str]
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    cost_per_use: float = 0.0
    estimated_time: float = 1.0
    enabled: bool = True

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        
        # 图像生成工具
        self.register(ToolDefinition(
            id="selfie_generator",
            name="自拍生成器",
            description="生成丝佳丽自拍照片",
            category=ToolCategory.IMAGE,
            skills=["scarlett-selfie"],
            models=["qwen-image-edit-plus", "qwen-image-max"],
            input_schema={
                "outfit": {"type": "string", "description": "服装描述"},
                "scene": {"type": "string", "description": "场景描述"},
                "pose": {"type": "string", "description": "姿势描述"}
            },
            output_schema={
                "image_url": {"type": "string"},
                "model_used": {"type": "string"}
            },
            cost_per_use=0.2,
            estimated_time=3.0
        ))
        
        # 文案创作工具
        self.register(ToolDefinition(
            id="copywriting",
            name="文案创作",
            description="生成营销文案、标题、广告语",
            category=ToolCategory.CONTENT,
            skills=["copywriting"],
            models=["qwen-plus", "qwen-max"],
            input_schema={
                "topic": {"type": "string", "description": "主题"},
                "style": {"type": "string", "description": "风格"},
                "platform": {"type": "string", "description": "平台"}
            },
            output_schema={
                "content": {"type": "string"},
                "title": {"type": "string"}
            },
            cost_per_use=0.01,
            estimated_time=1.0
        ))
        
        # 小红书发布
        self.register(ToolDefinition(
            id="xiaohongshu_publisher",
            name="小红书发布",
            description="发布内容到小红书",
            category=ToolCategory.SOCIAL,
            skills=["xiaohongshu-publisher"],
            models=["qwen-plus"],
            input_schema={
                "title": {"type": "string"},
                "content": {"type": "string"},
                "images": {"type": "array"}
            },
            output_schema={
                "post_id": {"type": "string"},
                "url": {"type": "string"}
            },
            cost_per_use=0.0,
            estimated_time=2.0
        ))
        
        # 微博发布
        self.register(ToolDefinition(
            id="weibo_publisher",
            name="微博发布",
            description="发布内容到微博",
            category=ToolCategory.SOCIAL,
            skills=["weibo-poster"],
            models=["qwen-plus"],
            input_schema={
                "content": {"type": "string"},
                "images": {"type": "array"}
            },
            output_schema={
                "post_id": {"type": "string"},
                "url": {"type": "string"}
            },
            cost_per_use=0.0,
            estimated_time=2.0
        ))
        
        # 代码生成
        self.register(ToolDefinition(
            id="code_generator",
            name="代码生成",
            description="生成代码、脚本",
            category=ToolCategory.CODE,
            skills=[],
            models=["qwen-coder", "qwen-plus"],
            input_schema={
                "language": {"type": "string"},
                "description": {"type": "string"}
            },
            output_schema={
                "code": {"type": "string"},
                "explanation": {"type": "string"}
            },
            cost_per_use=0.02,
            estimated_time=3.0
        ))
        
        # 数据分析
        self.register(ToolDefinition(
            id="data_analyzer",
            name="数据分析",
            description="分析数据、生成报告",
            category=ToolCategory.DATA,
            skills=[],
            models=["qwen-max"],
            input_schema={
                "data_source": {"type": "string"},
                "analysis_type": {"type": "string"}
            },
            output_schema={
                "report": {"type": "string"},
                "charts": {"type": "array"}
            },
            cost_per_use=0.05,
            estimated_time=5.0
        ))
        
        # 网页搜索
        self.register(ToolDefinition(
            id="web_search",
            name="网页搜索",
            description="搜索网页信息",
            category=ToolCategory.SEARCH,
            skills=["searxng"],
            models=[],
            input_schema={
                "query": {"type": "string"},
                "limit": {"type": "integer"}
            },
            output_schema={
                "results": {"type": "array"}
            },
            cost_per_use=0.0,
            estimated_time=1.0
        ))
        
        # 写作工具
        self.register(ToolDefinition(
            id="writing",
            name="写作助手",
            description="文章、小说、剧本创作",
            category=ToolCategory.CONTENT,
            skills=[],
            models=["qwen-plus", "qwen-max"],
            input_schema={
                "type": {"type": "string"},
                "topic": {"type": "string"},
                "length": {"type": "integer"}
            },
            output_schema={
                "content": {"type": "string"}
            },
            cost_per_use=0.03,
            estimated_time=2.0
        ))
        
        # 翻译工具
        self.register(ToolDefinition(
            id="translation",
            name="翻译助手",
            description="多语言翻译",
            category=ToolCategory.UTILITY,
            skills=[],
            models=["qwen-plus"],
            input_schema={
                "text": {"type": "string"},
                "source_lang": {"type": "string"},
                "target_lang": {"type": "string"}
            },
            output_schema={
                "translated_text": {"type": "string"}
            },
            cost_per_use=0.01,
            estimated_time=1.0
        ))
        
        # 定时提醒
        self.register(ToolDefinition(
            id="reminder",
            name="定时提醒",
            description="设置定时提醒",
            category=ToolCategory.UTILITY,
            skills=["qqbot-cron"],
            models=[],
            input_schema={
                "message": {"type": "string"},
                "time": {"type": "string"},
                "repeat": {"type": "boolean"}
            },
            output_schema={
                "job_id": {"type": "string"},
                "scheduled_time": {"type": "string"}
            },
            cost_per_use=0.0,
            estimated_time=0.5
        ))
    
    def register(self, tool: ToolDefinition):
        """注册工具"""
        self._tools[tool.id] = tool
    
    def unregister(self, tool_id: str):
        """注销工具"""
        if tool_id in self._tools:
            del self._tools[tool_id]
    
    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """获取工具"""
        return self._tools.get(tool_id)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """按分类获取工具"""
        return [t for t in self._tools.values() if t.category == category]
    
    def get_tools_by_role(self, role: str) -> List[ToolDefinition]:
        """按角色获取工具"""
        role_tool_map = {
            "copywriter": ["copywriting"],
            "image_expert": ["selfie_generator"],
            "coder": ["code_generator"],
            "data_analyst": ["data_analyzer"],
            "writer": ["writing"],
            "operator": ["xiaohongshu_publisher", "weibo_publisher"],
            "searcher": ["web_search"],
            "translator": ["translation"]
        }
        
        tool_ids = role_tool_map.get(role, [])
        return [self._tools[tid] for tid in tool_ids if tid in self._tools]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "enabled": t.enabled,
                "cost": t.cost_per_use
            }
            for t in self._tools.values()
        ]
    
    def enable_tool(self, tool_id: str):
        """启用工具"""
        if tool_id in self._tools:
            self._tools[tool_id].enabled = True
    
    def disable_tool(self, tool_id: str):
        """禁用工具"""
        if tool_id in self._tools:
            self._tools[tool_id].enabled = False

# 全局实例
_registry = None

def get_registry() -> ToolRegistry:
    """获取全局工具注册表"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry

# 测试
if __name__ == "__main__":
    registry = get_registry()
    
    print("已注册工具:")
    for tool in registry.list_tools():
        print(f"  {tool['id']}: {tool['name']} (${tool['cost']}/次)")
    
    print("\n图像相关工具:")
    for tool in registry.get_tools_by_category(ToolCategory.IMAGE):
        print(f"  {tool.name}")
    
    print("\n文案专家可用工具:")
    for tool in registry.get_tools_by_role("copywriter"):
        print(f"  {tool.name}")