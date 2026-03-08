#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀共享记忆库测试脚本
Test Script for Shared Memory System

作者：斯嘉丽 Scarlett
日期：2026-03-08
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加脚本路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from shared_memory import SharedMemoryService, ChannelLink
from sync_scheduler import SyncSchedulerService
from channel_linking import ChannelLinkingManager


async def test_shared_memory():
    """测试共享记忆库基础功能"""
    print("\n" + "="*60)
    print("🧪 测试 1: 共享记忆库基础功能")
    print("="*60)
    
    service = SharedMemoryService()
    
    # 测试 1.1: 保存记忆
    print("\n📝 测试保存记忆...")
    await service.save_memory(
        channel="feishu",
        user_id="ou_test123",
        content="这是测试记忆内容",
        metadata={"topic": "测试", "test": True}
    )
    print("✅ 记忆保存成功")
    
    # 测试 1.2: 查询记忆
    print("\n🔍 测试查询记忆...")
    memories = await service.query_memories(
        channel="feishu",
        user_id="ou_test123",
        cross_channel=False
    )
    print(f"✅ 查询到 {len(memories)} 条记忆")
    for key, value in list(memories.items())[:2]:
        print(f"   - {key}: {value[:100]}...")
    
    # 测试 1.3: 创建渠道绑定
    print("\n🔗 测试创建渠道绑定...")
    link = await service.bind_channels(
        channels={
            "feishu": "ou_test123",
            "qqbot": "7941TEST123"
        },
        user_note="测试绑定"
    )
    print(f"✅ 创建绑定成功：{link.link_id}")
    print(f"   渠道：{link.channels}")
    
    # 测试 1.4: 查询绑定
    print("\n🔍 测试查询绑定...")
    binding = await service.store.find_link_by_channel_id("feishu", "ou_test123")
    if binding:
        print(f"✅ 找到绑定：{binding.link_id}")
        print(f"   所有渠道：{binding.channels}")
    
    # 测试 1.5: 跨渠道查询
    print("\n🌐 测试跨渠道查询...")
    # 先为 qqbot 保存一些记忆
    await service.save_memory(
        channel="qqbot",
        user_id="7941TEST123",
        content="这是 QQ 渠道的记忆",
        metadata={"topic": "跨渠道测试"}
    )
    
    # 从 feishu 查询（应该能看到 qqbot 的记忆）
    cross_memories = await service.query_memories(
        channel="feishu",
        user_id="ou_test123",
        cross_channel=True
    )
    print(f"✅ 跨渠道查询到 {len(cross_memories)} 条记忆")
    for key in cross_memories.keys():
        print(f"   - {key}")
    
    print("\n✅ 共享记忆库测试完成\n")


async def test_sync_scheduler():
    """测试同步调度器"""
    print("\n" + "="*60)
    print("🧪 测试 2: 同步调度器")
    print("="*60)
    
    service = SyncSchedulerService()
    
    # 测试 2.1: 检查同步状态
    print("\n📊 检查同步状态...")
    status = await service.check_sync_status()
    print(f"当前时间：{status['current_time']}")
    print(f"下次同步：{status['next_sync_time']}")
    print(f"距离同步：{status['hours_until_sync']:.2f} 小时")
    
    # 测试 2.2: 立即执行同步
    print("\n🔄 执行立即同步...")
    result = await service.sync_now()
    print(f"同步状态：{result['status']}")
    print(f"同步 ID: {result['sync_id']}")
    print(f"渠道数：{len(result['channels_synced'])}")
    print(f"记忆数：{result['memories_synced']}")
    
    # 测试 2.3: 查看同步历史
    print("\n📜 查看同步历史...")
    history = await service.get_sync_history(7)
    print(f"最近 7 天同步次数：{len(history)}")
    if history:
        latest = history[0]
        print(f"最近一次：{latest.get('started_at', 'N/A')}")
        print(f"状态：{latest.get('status', 'N/A')}")
    
    print("\n✅ 同步调度器测试完成\n")


async def test_channel_linking():
    """测试多渠道绑定管理"""
    print("\n" + "="*60)
    print("🧪 测试 3: 多渠道绑定管理")
    print("="*60)
    
    manager = ChannelLinkingManager()
    
    # 测试 3.1: 创建绑定
    print("\n🔗 测试创建绑定...")
    result = await manager.create_binding(
        channels={
            "feishu": "ou_linktest1",
            "qqbot": "7941LINKTEST1",
            "wechat": "wx_linktest1"
        },
        user_note="测试多渠道绑定"
    )
    
    if result["success"]:
        print(f"✅ 绑定成功：{result['link_id']}")
        print(f"   渠道：{', '.join(result['channels'].keys())}")
    else:
        print(f"❌ 绑定失败：{result.get('error')}")
    
    # 测试 3.2: 查询绑定
    print("\n🔍 测试查询绑定...")
    binding = await manager.get_binding("feishu", "ou_linktest1")
    if binding:
        print(f"✅ 找到绑定：{binding['link_id']}")
        print(f"   已绑定渠道：{', '.join(binding['channels'].keys())}")
        print(f"   其他渠道：{list(binding['linked_channels'].keys())}")
    
    # 测试 3.3: 列出所有绑定
    print("\n📋 列出所有绑定...")
    all_bindings = await manager.list_all_bindings()
    print(f"总绑定数：{len(all_bindings)}")
    for i, b in enumerate(all_bindings[:3], 1):
        print(f"  {i}. {b['link_id']} - {len(b['channels'])} 个渠道")
    
    # 测试 3.4: 跨渠道记忆查询
    print("\n🌐 测试跨渠道记忆查询...")
    memories = await manager.get_cross_channel_memories(
        channel="feishu",
        user_id="ou_linktest1",
        days=7
    )
    print(f"查询到 {memories['total_entries']} 条记忆")
    print(f"涉及渠道：{list(memories['memories_by_channel'].keys())}")
    
    print("\n✅ 多渠道绑定管理测试完成\n")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "🎯"*30)
    print("   灵犀共享记忆库系统测试")
    print("🎯"*30 + "\n")
    
    try:
        await test_shared_memory()
        await test_sync_scheduler()
        await test_channel_linking()
        
        print("\n" + "✅"*30)
        print("   所有测试通过！")
        print("✅"*30 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


async def demo_scenario():
    """演示场景：用户跨渠道使用"""
    print("\n" + "="*60)
    print("🎬 演示场景：用户跨渠道使用灵犀")
    print("="*60)
    
    manager = ChannelLinkingManager()
    
    # 场景 1: 用户在飞书首次使用
    print("\n📱 场景 1: 用户在飞书首次使用")
    feishu_user = "ou_4192609eb71f18ae82f9163f02bef144"
    print(f"   渠道：feishu")
    print(f"   用户：{feishu_user}")
    
    # 保存飞书记忆
    await manager.service.save_memory(
        channel="feishu",
        user_id=feishu_user,
        content="用户喜欢早上 9 点开始工作，偏好简洁的回复风格",
        metadata={"topic": "用户偏好"}
    )
    print("   ✅ 保存用户偏好记忆")
    
    # 场景 2: 用户绑定 QQ 渠道
    print("\n🔗 场景 2: 用户绑定 QQ 渠道")
    qq_user = "7941E72A6252ADA08CC281AC26D9920B"
    result = await manager.create_binding(
        channels={
            "feishu": feishu_user,
            "qqbot": qq_user
        },
        user_note="老板的多渠道绑定"
    )
    if result["success"]:
        print(f"   ✅ 绑定成功：{result['link_id']}")
    
    # 场景 3: 用户在 QQ 渠道继续对话
    print("\n📱 场景 3: 用户在 QQ 渠道继续对话")
    print(f"   渠道：qqbot")
    print(f"   用户：{qq_user}")
    
    # 查询跨渠道记忆
    memories = await manager.get_cross_channel_memories(
        channel="qqbot",
        user_id=qq_user,
        days=7
    )
    print(f"   ✅ 查询到 {memories['total_entries']} 条记忆")
    print(f"   📊 涉及渠道：{list(memories['memories_by_channel'].keys())}")
    
    # 场景 4: 凌晨 2 点自动同步
    print("\n🕑 场景 4: 凌晨 2 点自动同步")
    sync_service = SyncSchedulerService()
    sync_result = await sync_service.sync_now()
    print(f"   ✅ 同步完成")
    print(f"   📦 同步记忆数：{sync_result['memories_synced']}")
    print(f"   📊 涉及渠道：{len(sync_result['channels_synced'])}")
    
    print("\n✅ 演示场景完成\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀共享记忆库测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--memory", action="store_true", help="只测试共享记忆库")
    parser.add_argument("--sync", action="store_true", help="只测试同步调度器")
    parser.add_argument("--link", action="store_true", help="只测试渠道绑定")
    parser.add_argument("--demo", action="store_true", help="运行演示场景")
    
    args = parser.parse_args()
    
    if args.all:
        asyncio.run(run_all_tests())
    elif args.memory:
        asyncio.run(test_shared_memory())
    elif args.sync:
        asyncio.run(test_sync_scheduler())
    elif args.link:
        asyncio.run(test_channel_linking())
    elif args.demo:
        asyncio.run(demo_scenario())
    else:
        # 默认运行演示场景
        asyncio.run(demo_scenario())
