#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀异步任务系统 - 快速开始示例

展示如何在实际项目中使用灵犀异步任务系统
"""

import asyncio
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lingxi_qqbot import handle_qq_message, query_task_status
from async_executor import get_executor

# ==================== 示例 1: 基础使用 ====================

async def example_basic():
    """基础使用示例"""
    print("\n" + "=" * 60)
    print("📚 示例 1: 基础使用")
    print("=" * 60)
    
    user_id = "demo_user"
    
    # 场景 1: 即时任务（查天气）
    print("\n💬 用户：北京明天天气怎么样")
    reply = await handle_qq_message(user_id, "北京明天天气怎么样")
    print(f"🤖 灵犀：{reply[:100]}...")
    
    # 场景 2: 耗时任务（发布文章）
    print("\n💬 用户：帮我发布公众号文章，主题是 AI 发展")
    reply = await handle_qq_message(
        user_id,
        "帮我发布公众号文章，主题是 AI 发展趋势"
    )
    print(f"🤖 灵犀：{reply}")
    
    # 场景 3: 在后台任务运行时，继续发送即时任务
    print("\n💬 用户：搜索最新的 AI 新闻（不等待文章发布）")
    reply = await handle_qq_message(user_id, "搜索最新的 AI 新闻")
    print(f"🤖 灵犀：{reply[:100]}...")
    
    print("\n✅ 看到了吗？耗时任务在后台执行，不阻塞新指令！")

# ==================== 示例 2: 任务查询 ====================

async def example_query():
    """任务查询示例"""
    print("\n" + "=" * 60)
    print("📚 示例 2: 任务查询")
    print("=" * 60)
    
    user_id = "demo_user"
    
    # 查询所有任务
    print("\n📋 查询所有任务:")
    status = await query_task_status(user_id)
    print(status)
    
    # 查询指定任务（如果有 task_id）
    # status = await query_task_status(user_id, "task_xxx")
    # print(status)

# ==================== 示例 3: 直接调用执行器 ====================

async def example_executor():
    """直接调用执行器示例"""
    print("\n" + "=" * 60)
    print("📚 示例 3: 直接调用执行器")
    print("=" * 60)
    
    executor = get_executor()
    
    # 场景：自定义后台任务
    print("\n🚀 启动自定义后台任务...")
    
    task_id = await executor.execute(
        task_type="custom-demo",
        description="演示自定义任务",
        command="echo '开始执行...' && sleep 3 && echo '完成！'",
        user_id="demo_user",
        channel="qqbot",
        notify_on_complete=False  # 演示时不发送通知
    )
    
    print(f"✅ 任务已启动：{task_id}")
    
    # 等待任务完成
    await asyncio.sleep(4)
    
    # 查询状态
    status = executor.get_task_status(task_id)
    print(f"\n📋 任务状态：{status['status']}")
    print(f"✅ 任务执行完成！")

# ==================== 示例 4: 多任务并发 ====================

async def example_concurrent():
    """多任务并发示例"""
    print("\n" + "=" * 60)
    print("📚 示例 4: 多任务并发")
    print("=" * 60)
    
    user_id = "demo_user"
    
    print("\n🚀 同时启动 3 个后台任务...")
    
    # 并发启动多个任务
    tasks = [
        asyncio.create_task(handle_qq_message(user_id, "发布公众号文章 1")),
        asyncio.create_task(handle_qq_message(user_id, "发布公众号文章 2")),
        asyncio.create_task(handle_qq_message(user_id, "发布公众号文章 3")),
    ]
    
    # 等待所有任务启动
    await asyncio.gather(*tasks)
    
    print("✅ 3 个任务已全部启动（后台并行执行）")
    
    # 查询任务列表
    await asyncio.sleep(1)
    status = await query_task_status(user_id)
    print(f"\n📋 当前任务列表:")
    print(status)

# ==================== 示例 5: 集成到你的项目 ====================

async def example_integration():
    """集成示例"""
    print("\n" + "=" * 60)
    print("📚 示例 5: 集成到你的项目")
    print("=" * 60)
    
    print("""
# 方式 1: 直接导入
from lingxi_qqbot import handle_qq_message

async def on_qq_message(user_id, message):
    reply = await handle_qq_message(user_id, message)
    await send_reply(user_id, reply)

# 方式 2: 作为 HTTP 服务
from fastapi import FastAPI
from lingxi_qqbot import handle_qq_message

app = FastAPI()

@app.post("/qqbot/message")
async def webhook(data: dict):
    reply = await handle_qq_message(data['user_id'], data['message'])
    return {"reply": reply}

# 方式 3: 集成到现有 Bot
class MyBot:
    async def handle_message(self, user_id, message):
        # 先交给灵犀处理
        reply = await handle_qq_message(user_id, message)
        
        # 可以添加额外逻辑
        if "特殊关键词" in message:
            reply = "特殊处理：" + reply
        
        return reply
""")
    
    print("\n✅ 就是这么简单！")

# ==================== 主函数 ====================

async def main():
    """运行所有示例"""
    print("\n" + "🌟" * 30)
    print("🚀 灵犀异步任务系统 - 快速开始")
    print("🌟" * 30)
    
    try:
        # 运行示例
        await example_basic()
        await example_query()
        await example_executor()
        await example_concurrent()
        await example_integration()
        
        # 总结
        print("\n" + "=" * 60)
        print("🎉 所有示例运行完成！")
        print("=" * 60)
        print("\n💡 现在你可以:")
        print("   1. 在项目中导入 lingxi_qqbot")
        print("   2. 调用 handle_qq_message 处理消息")
        print("   3. 享受多任务并行的便利！")
        print("\n📚 更多文档:")
        print("   - QQBOT_INTEGRATION.md - 集成指南")
        print("   - ASYNC_GUIDE.md - 异步系统详解")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 运行失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
