#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) v2.0 - OpenClaw 入口
智慧调度系统，心有灵犀，一点就通

🚀 v2.0 优化亮点:
- ⚡ 快速响应层：简单问题 <5ms 秒回
- 💾 LRU 缓存：重复问题 <1ms
- 🚀 并行执行：复杂任务快 9x
- 💰 节省 Tokens: 57% 请求零 LLM 消耗
"""

import sys
import os

# 添加技能路径
SKILL_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_PATH)

# ✅ 使用优化后的 v2 版本
from scripts.orchestrator_v2 import SmartOrchestrator, TaskResult, get_orchestrator as get_v2_orchestrator
from scripts.fast_response_layer import fast_respond, cache_response

# 全局实例
_orchestrator = None

def get_orchestrator(max_concurrent: int = 3) -> SmartOrchestrator:
    """获取灵犀调度器实例 (v2.0)"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SmartOrchestrator(max_concurrent=max_concurrent, enable_fast_response=True)
    return _orchestrator

async def process_request(user_input: str, channel: str = None, user_id: str = None) -> str:
    """
    处理用户请求 - 灵犀统一入口 (v2.0)
    
    Args:
        user_input: 用户输入
        channel: 来源渠道 (qqbot, telegram, etc.)
        user_id: 用户 ID
    
    Returns:
        处理结果
    """
    orch = get_orchestrator()
    
    # ✅ v2.0: 自动处理快速响应、缓存、并行执行
    result = await orch.execute(user_input, user_id)
    
    # ✅ v2.0: 结果包含性能指标
    # result.total_elapsed_ms - 总耗时
    # result.fast_response_layer - 使用的响应层
    # result.total_score - 评分
    
    return result.final_output

def process_sync(user_input: str, channel: str = None, user_id: str = None) -> str:
    """同步处理用户请求"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(process_request(user_input, channel, user_id))

def get_stats() -> str:
    """获取性能统计"""
    if _orchestrator:
        return _orchestrator.get_stats()
    return "灵犀尚未初始化"

# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀 v2.0 - 智慧调度系统")
    parser.add_argument("input", help="用户输入")
    parser.add_argument("--channel", help="来源渠道")
    parser.add_argument("--user-id", help="用户 ID")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    if args.stats:
        print(get_stats())
    else:
        result = process_sync(args.input, args.channel, args.user_id)
        print(result)
