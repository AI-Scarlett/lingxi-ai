#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行器工厂 - 根据角色类型创建执行器

✅ v3.0.2: 修复相对导入问题，支持直接导入
"""

from typing import Dict, Any, Optional

# ✅ 支持两种导入方式
try:
    from .image_expert import ImageExpertExecutor
    from .copywriter import CopywriterExecutor
except ImportError:
    # 直接导入（非包模式）
    from image_expert import ImageExpertExecutor
    from copywriter import CopywriterExecutor

class BaseExecutor:
    """基础执行器"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        raise NotImplementedError

class GenericExecutor(BaseExecutor):
    """通用执行器 - 兜底方案"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """通用执行"""
        return {
            "output": "任务已处理",
            "input": input_data,
            "executor": "generic"
        }

class ExecutorFactory:
    """执行器工厂"""
    
    _executors: Dict[str, BaseExecutor] = {}
    
    @classmethod
    def get_executor(cls, role: str) -> Optional[BaseExecutor]:
        """获取执行器实例"""
        if role in cls._executors:
            return cls._executors[role]
        
        executor = cls._create_executor(role)
        if executor:
            cls._executors[role] = executor
        return executor
    
    @classmethod
    def _create_executor(cls, role: str) -> Optional[BaseExecutor]:
        """创建执行器"""
        # 映射表 - 支持多种角色名称格式
        executors_map = {
            # 完整角色名
            "图像专家": ImageExpertExecutor,
            "文案专家": CopywriterExecutor,
            "代码专家": GenericExecutor,
            "数据专家": GenericExecutor,
            "写作专家": GenericExecutor,
            "运营专家": GenericExecutor,
            "搜索专家": GenericExecutor,
            "翻译专家": GenericExecutor,
            # 英文角色名
            "image_expert": ImageExpertExecutor,
            "copywriter": CopywriterExecutor,
            "coder": GenericExecutor,
            "data_analyst": GenericExecutor,
            "writer": GenericExecutor,
            "operator": GenericExecutor,
            "searcher": GenericExecutor,
            "translator": GenericExecutor,
        }
        
        executor_class = executors_map.get(role)
        if executor_class:
            return executor_class()
        
        # 兜底：返回通用执行器
        return GenericExecutor()
    
    @classmethod
    def list_available_executors(cls) -> list:
        """列出可用的执行器"""
        return [
            "image_expert", "copywriter", "coder", "data_analyst",
            "writer", "operator", "searcher", "translator"
        ]

# 便捷函数
def get_executor(role: str) -> Optional[BaseExecutor]:
    """获取执行器（便捷函数）"""
    return ExecutorFactory.get_executor(role)
