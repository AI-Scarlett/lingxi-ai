#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀核心模块 - v2.0 重构版

保持向后兼容，支持平滑迁移
"""

from .memory import MemorySystem, get_memory_system
from .task_queue import TaskQueue, Task, TaskPriority, TaskStatus, get_task_queue
from .compat import LegacyAdapter
from .content_fetcher import SmartContentFetcher, get_content_fetcher

__version__ = "3.3.3"
__all__ = [
    "MemorySystem",
    "get_memory_system",
    "TaskQueue",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "get_task_queue",
    "LegacyAdapter",  # 兼容性适配器
    "SmartContentFetcher",  # Scrapling 内容获取器
    "get_content_fetcher"
]
