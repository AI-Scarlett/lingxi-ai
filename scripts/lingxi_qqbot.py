#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - QQ Bot 集成入口
将异步编排器集成到 QQ Bot 消息处理流程

用法:
    from lingxi_qqbot import handle_qq_message
    
    # QQ Bot 收到消息时调用
    reply = await handle_qq_message(user_id, message)
"""

import asyncio
import json
import os
import sys

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from orchestrator_async import get_async_orchestrator, AsyncOrchestrator
from task_manager import get_task_manager, TaskStatus

# ==================== 配置 ====================

# 是否启用异步处理（默认启用）
ENABLE_ASYNC = True

# 耗时任务关键词（自动后台执行）
LONG_RUNNING_KEYWORDS = [
    "发布", "公众号", "微信", "小红书", "微博", "抖音",
    "生成图片", "生成图", "自拍", "处理文件", "分析数据",
    "导出", "转换", "上传", "下载"
]

# 即时任务关键词（立即响应）
INSTANT_KEYWORDS = [
    "天气", "搜索", "翻译", "是什么", "为什么", "怎么",
    "你好", "在吗", "帮助", "说明"
]

# ==================== 消息处理 ====================

async def handle_qq_message(user_id: str, message: str, channel: str = "qqbot") -> str:
    """处理 QQ 消息
    
    Args:
        user_id: 用户 ID (QQ openid)
        message: 用户消息内容
        channel: 渠道 (默认 qqbot)
        
    Returns:
        回复消息
    """
    print(f"\n💬 收到 QQ 消息 - 用户：{user_id}")
    print(f"📝 消息：{message[:100]}")
    
    try:
        # 获取编排器
        orch = get_async_orchestrator()
        
        # 判断是否为耗时任务
        is_long_running = _is_long_running_task(message)
        
        if is_long_running and ENABLE_ASYNC:
            # 后台异步执行
            print(f"⚙️ 任务类型：耗时任务（后台执行）")
            reply = await _handle_background_task(orch, user_id, message, channel)
        else:
            # 即时执行
            print(f"⚡ 任务类型：即时任务（立即响应）")
            reply = await _handle_instant_task(orch, user_id, message, channel)
        
        return reply
    
    except Exception as e:
        print(f"❌ 处理消息失败：{e}")
        import traceback
        traceback.print_exc()
        return f"抱歉老板，处理出问题了... 💦\n错误：{str(e)[:100]}"

async def _handle_background_task(
    orch: AsyncOrchestrator,
    user_id: str,
    message: str,
    channel: str
) -> str:
    """处理耗时任务（后台执行）
    
    立即返回接收确认，实际任务在后台执行
    """
    # 立即返回接收确认
    reply = "已经收到请求，任务可能比较复杂，已转交给灵犀进行处理"
    
    # 后台异步执行实际任务
    asyncio.create_task(orch.execute_async(
        user_input=message,
        user_id=user_id,
        channel=channel,
        is_background=True
    ))
    
    return reply

async def _handle_instant_task(
    orch: AsyncOrchestrator,
    user_id: str,
    message: str,
    channel: str
) -> str:
    """处理即时任务（立即响应）
    """
    reply = await orch.execute_async(
        user_input=message,
        user_id=user_id,
        channel=channel,
        is_background=False
    )
    
    return reply

def _is_long_running_task(message: str) -> bool:
    """判断是否为耗时任务
    
    根据关键词自动识别
    """
    # 检查耗时任务关键词
    for kw in LONG_RUNNING_KEYWORDS:
        if kw in message:
            return True
    
    # 检查即时任务关键词（反向判断）
    for kw in INSTANT_KEYWORDS:
        if kw in message:
            return False
    
    # 默认按即时任务处理
    return False

# ==================== 任务查询 ====================

async def query_task_status(user_id: str, task_id: str = None) -> str:
    """查询任务状态
    
    Args:
        user_id: 用户 ID
        task_id: 任务 ID（可选，不填则查询所有）
        
    Returns:
        状态消息
    """
    orch = get_async_orchestrator()
    
    if task_id:
        # 查询指定任务
        status = await orch.check_task_status(task_id)
        if not status:
            return f"❌ 未找到任务：{task_id}"
        
        return f"""📋 任务状态
━━━━━━━━━━━━━━━━
ID: {status['id']}
类型：{status['type']}
状态：{status['status']}
描述：{status['description']}
创建：{status['created_at']}
完成：{status.get('completed_at', '未完成')}
"""
    else:
        # 查询所有任务
        tasks = await orch.list_tasks(limit=10)
        if not tasks:
            return "📋 暂无任务记录"
        
        lines = ["📋 最近任务", "━━━━━━━━━━━━━━━━"]
        for t in tasks:
            status_emoji = "✅" if t['status'] == 'completed' else "⏳" if t['status'] == 'running' else "⏸️"
            lines.append(f"{status_emoji} {t['type']}: {t['description'][:30]}...")
        
        return "\n".join(lines)

async def cancel_task(user_id: str, task_id: str) -> str:
    """取消任务
    
    Args:
        user_id: 用户 ID
        task_id: 任务 ID
        
    Returns:
        结果消息
    """
    orch = get_async_orchestrator()
    success = await orch.cancel_task(task_id)
    
    if success:
        return f"✅ 任务已取消：{task_id}"
    else:
        return f"❌ 取消失败，任务可能已完成或不存在"

# ==================== 命令行测试 ====================

async def test_cli():
    """命令行测试"""
    print("=" * 60)
    print("🧪 灵犀 QQ Bot 集成 - 测试模式")
    print("=" * 60)
    
    # 模拟用户消息
    test_cases = [
        ("user_123", "北京明天天气怎么样"),
        ("user_123", "帮我发布公众号文章，主题是 AI 发展"),
        ("user_123", "搜索最新的 AI 新闻"),
        ("user_123", "帮我写个小红书文案，然后发布"),
    ]
    
    for user_id, message in test_cases:
        print(f"\n{'='*60}")
        print(f"👤 用户：{user_id}")
        print(f"💬 消息：{message}")
        print(f"{'='*60}")
        
        reply = await handle_qq_message(user_id, message)
        print(f"\n🤖 回复：{reply[:200]}...")
        
        # 等待一下
        await asyncio.sleep(1)
    
    # 查询任务
    print(f"\n{'='*60}")
    print("📋 查询任务状态")
    print(f"{'='*60}")
    
    status = await query_task_status("user_123")
    print(status)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_cli())
