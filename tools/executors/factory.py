#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行器工厂 - 根据角色类型创建执行器
"""

from typing import Dict, Any, Optional
from .image_expert import ImageExpertExecutor
from .copywriter import CopywriterExecutor

class ExecutorFactory:
    """执行器工厂"""
    
    _executors = {}
    
    @classmethod
    def get_executor(cls, role: str):
        """获取执行器实例"""
        if role in cls._executors:
            return cls._executors[role]
        
        # 创建新的执行器
        executor = cls._create_executor(role)
        if executor:
            cls._executors[role] = executor
        return executor
    
    @classmethod
    def _create_executor(cls, role: str):
        """创建执行器"""
        executors_map = {
            "image_expert": ImageExpertExecutor,
            "copywriter": CopywriterExecutor,
            # 其他执行器待实现
        }
        
        executor_class = executors_map.get(role)
        if executor_class:
            return executor_class()
        return None
    
    @classmethod
    def list_available_executors(cls) -> list:
        """列出可用的执行器"""
        return [
            "image_expert",
            "copywriter",
            "coder",
            "data_analyst",
            "writer",
            "operator",
            "searcher",
            "translator"
        ]