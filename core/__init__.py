#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀核心模块 - v4.0 重构版

包含 MindCore 记忆核心系统 + EvoMind 自改进系统
"""

from .memory import MemorySystem, get_memory_system
from .task_queue import TaskQueue, Task, TaskPriority, TaskStatus, get_task_queue
from .compat import LegacyAdapter
from .content_fetcher import SmartContentFetcher, get_content_fetcher

# MindCore v4.0 新模块
from .mindcore import MindCore, get_mindcore

__version__ = "3.3.3"
__all__ = [
    # 传统模块（向后兼容）
    "MemorySystem",
    "get_memory_system",
    "TaskQueue",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "get_task_queue",
    "LegacyAdapter",
    "SmartContentFetcher",
    "get_content_fetcher",
    
    # MindCore v4.0 新模块
    "MindCore",
    "get_mindcore"
]
