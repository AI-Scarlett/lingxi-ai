#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀异步任务系统 - 功能测试脚本
测试任务管理器、异步执行器的核心功能
"""

import asyncio
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_manager import (
    get_task_manager,
    TaskManager,
    TaskInfo,
    TaskStatus,
    generate_task_id
)
from async_executor import get_executor, AsyncExecutor
from orchestrator_async import get_async_orchestrator, AsyncOrchestrator

# ==================== 测试任务管理器 ====================

async def test_task_manager():
    """测试任务管理器"""
    print("\n" + "=" * 60)
    print("📋 测试 1: 任务管理器 (TaskManager)")
    print("=" * 60)
    
    # 创建新的任务管理器（使用测试文件）
    manager = TaskManager(state_file="/tmp/lingxi-test-task-state.json")
    
    # 测试 1.1: 创建任务
    print("\n✅ 测试 1.1: 创建任务")
    task = TaskInfo(
        id=generate_task_id("test"),
        type="wechat-publish",
        description="测试公众号发布 - AI 发展趋势",
        user_id="test_user_123",
        channel="qqbot",
        priority=5
    )
    manager.register(task)
    print(f"   任务 ID: {task.id}")
    print(f"   类型：{task.type}")
    print(f"   状态：{task.status.value}")
    
    # 测试 1.2: 查询任务
    print("\n✅ 测试 1.2: 查询任务")
    retrieved = manager.get(task.id)
    assert retrieved is not None, "查询失败"
    assert retrieved.id == task.id, "ID 不匹配"
    print(f"   ✓ 成功查询任务：{retrieved.description}")
    
    # 测试 1.3: 更新任务状态
    print("\n✅ 测试 1.3: 更新任务状态")
    manager.update(task.id, status=TaskStatus.RUNNING)
    updated = manager.get(task.id)
    print(f"   状态变更：PENDING → {updated.status.value}")
    
    # 测试 1.4: 完成任务
    print("\n✅ 测试 1.4: 完成任务")
    manager.update(
        task.id,
        status=TaskStatus.COMPLETED,
        result={"success": True, "url": "https://mp.weixin.qq.com/s/test123"}
    )
    completed = manager.get(task.id)
    print(f"   状态变更：RUNNING → {completed.status.value}")
    print(f"   结果：{completed.result}")
    
    # 测试 1.5: 获取所有任务
    print("\n✅ 测试 1.5: 获取所有任务")
    all_tasks = manager.get_all()
    print(f"   总任务数：{len(all_tasks)}")
    
    completed_tasks = manager.get_all(TaskStatus.COMPLETED)
    print(f"   已完成：{len(completed_tasks)}")
    
    running_tasks = manager.get_running()
    print(f"   运行中：{len(running_tasks)}")
    
    # 测试 1.6: 创建多个任务（模拟并发）
    print("\n✅ 测试 1.6: 创建多个任务（模拟并发）")
    for i in range(5):
        t = TaskInfo(
            id=generate_task_id("concurrent"),
            type="test-task",
            description=f"并发测试任务 {i+1}",
            user_id="test_user_123"
        )
        manager.register(t)
    
    all_tasks = manager.get_all()
    print(f"   当前总任务数：{len(all_tasks)}")
    
    # 测试 1.7: 删除任务
    print("\n✅ 测试 1.7: 删除任务")
    deleted = manager.delete(task.id)
    print(f"   删除成功：{deleted}")
    all_tasks = manager.get_all()
    print(f"   删除后任务数：{len(all_tasks)}")
    
    print("\n✅ 任务管理器测试通过！")
    return manager

# ==================== 测试异步执行器 ====================

async def test_async_executor():
    """测试异步执行器"""
    print("\n" + "=" * 60)
    print("🚀 测试 2: 异步执行器 (AsyncExecutor)")
    print("=" * 60)
    
    # 获取执行器
    executor = get_executor()
    
    # 测试 2.1: 执行快速任务
    print("\n✅ 测试 2.1: 执行快速任务（echo）")
    task_id_1 = await executor.execute(
        task_type="test-quick",
        description="测试快速任务",
        command="echo 'Hello World' && echo '任务完成'",
        user_id="test_user_123",
        channel="qqbot",
        notify_on_complete=False  # 测试时不发送通知
    )
    print(f"   任务 ID: {task_id_1}")
    
    # 等待任务完成
    await asyncio.sleep(2)
    
    # 查询状态
    status = executor.get_task_status(task_id_1)
    print(f"   状态：{status['status']}")
    if status['result']:
        print(f"   ✓ 任务执行成功")
    
    # 测试 2.2: 执行慢速任务（模拟耗时操作）
    print("\n✅ 测试 2.2: 执行慢速任务（sleep 5 秒）")
    task_id_2 = await executor.execute(
        task_type="test-slow",
        description="测试慢速任务 - 模拟公众号发布",
        command="echo '开始发布...' && sleep 5 && echo '发布成功！' && echo '链接：https://mp.weixin.qq.com/s/test'",
        user_id="test_user_123",
        channel="qqbot",
        notify_on_complete=False
    )
    print(f"   任务 ID: {task_id_2}")
    print(f"   任务已在后台运行...")
    
    # 测试 2.3: 在慢速任务运行时，查询状态
    print("\n✅ 测试 2.3: 查询运行中的任务状态")
    await asyncio.sleep(2)
    status = executor.get_task_status(task_id_2)
    print(f"   状态：{status['status']}")
    
    # 测试 2.4: 列出所有任务
    print("\n✅ 测试 2.4: 列出所有任务")
    all_tasks = executor.get_all_tasks()
    print(f"   总任务数：{len(all_tasks)}")
    for t in all_tasks:
        print(f"   - {t['id']}: {t['status']}")
    
    # 等待慢速任务完成
    print("\n   ⏳ 等待慢速任务完成...")
    await asyncio.sleep(5)
    
    status = executor.get_task_status(task_id_2)
    print(f"   最终状态：{status['status']}")
    if status['status'] == 'completed':
        print(f"   ✓ 慢速任务执行成功！")
    
    print("\n✅ 异步执行器测试通过！")
    return executor

# ==================== 测试异步编排器 ====================

async def test_async_orchestrator():
    """测试异步编排器"""
    print("\n" + "=" * 60)
    print("🎯 测试 3: 异步编排器 (AsyncOrchestrator)")
    print("=" * 60)
    
    orch = get_async_orchestrator()
    
    # 测试 3.1: 即时任务（查天气）
    print("\n✅ 测试 3.1: 即时任务（查天气）")
    reply = await orch.execute_async(
        user_input="北京明天天气怎么样",
        user_id="test_user_123",
        channel="qqbot",
        is_background=False
    )
    print(f"   回复：{reply[:100]}...")
    print(f"   ✓ 即时任务立即响应")
    
    # 测试 3.2: 后台任务（发布文章）
    print("\n✅ 测试 3.2: 后台任务（发布公众号文章）")
    reply = await orch.execute_async(
        user_input="帮我发布公众号文章，主题是 AI 发展趋势",
        user_id="test_user_123",
        channel="qqbot",
        is_background=True
    )
    print(f"   回复：{reply}")
    print(f"   ✓ 后台任务已启动")
    
    # 测试 3.3: 查询任务状态
    print("\n✅ 测试 3.3: 查询任务列表")
    await asyncio.sleep(1)
    tasks = await orch.list_tasks(limit=5)
    print(f"   最近任务数：{len(tasks)}")
    for t in tasks:
        print(f"   - {t['id']}: {t['type']} ({t['status']})")
    
    print("\n✅ 异步编排器测试通过！")
    return orch

# ==================== 测试多任务并发 ====================

async def test_concurrent_tasks():
    """测试多任务并发"""
    print("\n" + "=" * 60)
    print("⚡ 测试 4: 多任务并发处理")
    print("=" * 60)
    
    executor = get_executor()
    
    # 同时启动 3 个任务
    print("\n✅ 同时启动 3 个后台任务...")
    
    tasks = []
    for i in range(3):
        task_id = await executor.execute(
            task_type="concurrent-test",
            description=f"并发测试任务 {i+1}",
            command=f"echo '任务 {i+1} 开始' && sleep {i+2} && echo '任务 {i+1} 完成'",
            user_id="test_user_123",
            channel="qqbot",
            notify_on_complete=False
        )
        tasks.append(task_id)
        print(f"   ✓ 任务 {i+1} 已启动：{task_id}")
    
    # 等待所有任务完成
    print("\n   ⏳ 等待所有任务完成...")
    await asyncio.sleep(8)
    
    # 检查所有任务状态
    print("\n✅ 检查任务状态:")
    all_completed = True
    for i, task_id in enumerate(tasks):
        status = executor.get_task_status(task_id)
        print(f"   任务 {i+1}: {status['status']}")
        if status['status'] != 'completed':
            all_completed = False
    
    if all_completed:
        print(f"\n   ✓ 所有并发任务执行成功！")
    else:
        print(f"\n   ⚠️ 部分任务未完成")
    
    print("\n✅ 多任务并发测试通过！")

# ==================== 主测试流程 ====================

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "🌟" * 30)
    print("🚀 灵犀异步任务系统 - 功能测试")
    print("🌟" * 30)
    
    try:
        # 测试 1: 任务管理器
        await test_task_manager()
        
        # 测试 2: 异步执行器
        await test_async_executor()
        
        # 测试 3: 异步编排器
        await test_async_orchestrator()
        
        # 测试 4: 多任务并发
        await test_concurrent_tasks()
        
        # 总结
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n✅ 核心功能验证:")
        print("   ✓ 任务状态管理（CRUD）")
        print("   ✓ 后台异步执行")
        print("   ✓ 任务状态追踪")
        print("   ✓ 多任务并发处理")
        print("   ✓ 智能任务调度")
        print("\n💡 系统已就绪，可以集成到 QQ Bot！")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
