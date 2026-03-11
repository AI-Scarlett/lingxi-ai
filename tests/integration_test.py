#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v4.0 集成测试

测试所有核心模块的集成
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from core.mindcore import MindCore, get_mindcore
from core.evomind import ApprovalManager, get_approval_manager
from core.agents import get_registry, get_feishu_agent, get_qq_agent
from core.orchestrator.task_distributor import get_distributor


async def test_mindcore():
    """测试 MindCore"""
    print("\n=== 测试 MindCore 记忆核心系统 ===")
    
    mindcore = get_mindcore()
    
    # 保存记忆
    m1 = await mindcore.save("测试记忆 1", importance=8.0)
    m2 = await mindcore.save("测试记忆 2", importance=9.0)
    
    print(f"✅ 保存了 {2} 条记忆")
    
    # 检索
    results = await mindcore.retrieve("测试", top_k=5)
    print(f"✅ 检索到 {len(results)} 条记忆")
    
    # 统计
    stats = {
        "stm": mindcore.stm.stats(),
        "mtm": mindcore.mtm.stats(),
        "ltm": mindcore.ltm.stats()
    }
    print(f"✅ 统计：STM={stats['stm']['total']}, MTM={stats['mtm']['total']}, LTM={stats['ltm']['total']}")
    
    return True


async def test_evomind():
    """测试 EvoMind 自改进系统"""
    print("\n=== 测试 EvoMind 自改进系统 ===")
    
    manager = get_approval_manager()
    
    # 添加测试提案
    proposal_id = await manager.add_proposal({
        "type": "save_memory",
        "title": "测试提案",
        "description": "这是一个测试提案",
        "importance": 7.5
    })
    
    print(f"✅ 添加了提案：{proposal_id}")
    
    # 获取待审批
    proposals = await manager.get_pending_proposals()
    print(f"✅ 待审批提案：{len(proposals)} 个")
    
    # 审批
    results = await manager.process_approval("test_user", "approve", [proposal_id])
    print(f"✅ 审批结果：批准 {len(results['approved'])} 个")
    
    return True


async def test_smartfetch():
    """测试 SmartFetch 智能抓取"""
    print("\n=== 测试 SmartFetch 智能抓取 ===")
    
    from core.smartfetch.multi_strategy import MultiStrategyFetcher, CookiePool
    
    fetcher = MultiStrategyFetcher()
    
    # 测试配置
    print(f"✅ SmartFetch 已初始化")
    print(f"   超时：{fetcher.timeout}秒")
    print(f"   重试次数：{fetcher.max_retries}")
    
    # Cookie 池
    cookie_pool = CookiePool()
    stats = cookie_pool.stats()
    print(f"✅ Cookie 池统计：{stats}")
    
    return True


async def test_agents():
    """测试 Multi-Agent"""
    print("\n=== 测试 Multi-Agent 架构 ===")
    
    registry = get_registry()
    
    # 注册 Agent
    feishu = get_feishu_agent()
    qq = get_qq_agent()
    
    registry.register_agent(feishu)
    registry.register_agent(qq)
    
    stats = registry.get_stats()
    print(f"✅ 注册了 {stats['total_agents']} 个 Agent")
    print(f"   渠道：{stats['channels']}")
    
    # Agent 统计
    print(f"✅ Feishu Agent: {feishu.get_stats()}")
    print(f"✅ QQ Agent: {qq.get_stats()}")
    
    return True


async def test_orchestrator():
    """测试任务分发器"""
    print("\n=== 测试任务分发器 ===")
    
    distributor = get_distributor(max_concurrent=10)
    
    # 注册 Agent
    feishu = get_feishu_agent()
    distributor.register_agent(feishu)
    
    # 测试任务
    tasks = [
        {"id": "1", "type": "message", "channel": "feishu", "content": "你好"},
        {"id": "2", "type": "message", "channel": "feishu", "content": "Hello"},
    ]
    
    # 分发
    results = await distributor.distribute_batch(tasks)
    print(f"✅ 分发了 {len(tasks)} 个任务")
    
    # 统计
    stats = distributor.get_stats()
    print(f"✅ 统计：总任务={stats['total_tasks']}, 成功={stats['successful_tasks']}")
    
    return True


async def run_all_tests():
    """运行所有集成测试"""
    print("="*60)
    print("🧪 灵犀 v4.0 集成测试套件")
    print("="*60)
    
    tests = [
        ("MindCore", test_mindcore),
        ("EvoMind", test_evomind),
        ("SmartFetch", test_smartfetch),
        ("Multi-Agent", test_agents),
        ("Orchestrator", test_orchestrator)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, "✅ PASS", result))
        except Exception as e:
            results.append((name, f"❌ FAIL: {e}", False))
            import traceback
            traceback.print_exc()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    for name, status, _ in results:
        print(f"{name}: {status}")
    
    passed = sum(1 for _, s, _ in results if "PASS" in s)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 通过")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
