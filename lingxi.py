#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - OpenClaw 入口
智慧调度系统，心有灵犀，一点就通
"""

import sys
import os

# 添加技能路径
SKILL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_PATH)

from scripts.orchestrator import SmartOrchestrator, TaskResult
from scripts.intent_parser import IntentParser

# 全局实例
_orchestrator = None
_intent_parser = None

def get_orchestrator() -> SmartOrchestrator:
    """获取灵犀调度器实例"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SmartOrchestrator()
    return _orchestrator

def get_intent_parser() -> IntentParser:
    """获取意图解析器实例"""
    global _intent_parser
    if _intent_parser is None:
        _intent_parser = IntentParser()
    return _intent_parser

async def process_request(user_input: str, channel: str = None, user_id: str = None) -> str:
    """
    处理用户请求 - 灵犀统一入口
    
    Args:
        user_input: 用户输入
        channel: 来源渠道 (qqbot, telegram, etc.)
        user_id: 用户ID
    
    Returns:
        处理结果
    """
    orch = get_orchestrator()
    parser = get_intent_parser()
    
    # 1. 解析意图
    intent = parser.parse(user_input)
    
    # 2. 检查是否跳过灵犀（特殊角色）
    if intent.get("bypass_orchestrator") and intent.get("direct_contact"):
        return f"💕 此任务可直接联系情感伴侣（QQ: {intent['direct_contact']}），不需要经过灵犀调度哦～"
    
    # 3. 执行任务
    result = await orch.execute(user_input)
    
    # 4. 返回结果
    return result.final_output

def process_sync(user_input: str, channel: str = None, user_id: str = None) -> str:
    """同步处理用户请求"""
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_request(user_input, channel, user_id))

# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀 - 智慧调度系统")
    parser.add_argument("input", help="用户输入")
    parser.add_argument("--channel", help="来源渠道")
    parser.add_argument("--user-id", help="用户ID")
    
    args = parser.parse_args()
    
    result = process_sync(args.input, args.channel, args.user_id)
    print(result)