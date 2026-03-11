#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Agent 模块

多 Agent 架构支持
"""

from .base import BaseAgent, AgentRegistry, get_registry
from .feishu import FeishuAgent, get_feishu_agent
from .qq import QQAgent, get_qq_agent
from .wecom import WeComAgent, get_wecom_agent

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "get_registry",
    "FeishuAgent",
    "get_feishu_agent",
    "QQAgent",
    "get_qq_agent",
    "WeComAgent",
    "get_wecom_agent"
]
