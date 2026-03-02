#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行器基础类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseExecutor(ABC):
    """执行器基类"""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model
    
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取执行器描述"""
        pass