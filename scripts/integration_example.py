#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v3.0 - 集成共享记忆库示例
Lingxi v3.0 - Shared Memory Integration Example

作者：斯嘉丽 Scarlett
日期：2026-03-08

展示如何在灵犀主入口中集成共享记忆库功能
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
import sys

# 添加脚本路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from shared_memory import SharedMemoryService
from channel_linking import ChannelLinkingManager
from sync_scheduler import SyncSchedulerService


class LingxiWithSharedMemory:
    """
    集成共享记忆库的灵犀调度器示例
    
    功能：
    1. 会话启动时加载跨渠道记忆
    2. 对话过程中自动记忆重要信息
    3. 支持显式查询共享记忆
    4. 任务完成后回写记忆
    """
    
    def __init__(self):
        self.memory_service = SharedMemoryService()
        self.link_manager = ChannelLinkingManager()
        self.sync_service = SyncSchedulerService()
        self._initialized = False
    
    async def initialize(self):
        """初始化"""
        if not self._initialized:
            await self.memory_service.initialize()
            await self.link_manager.initialize()
            await self.sync_service.initialize()
            self._initialized = True
    
    async def on_session_start(self, channel: str, user_id: str) -> dict:
        """
        会话启动时的处理
        
        Args:
            channel: 来源渠道
            user_id: 用户 ID
        
        Returns:
            加载的上下文信息
        """
        await self.initialize()
        
        # 1. 查询跨渠道记忆（最近 7 天）
        memories = await self.memory_service.query_memories(
            channel=channel,
            user_id=user_id,
            start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            cross_channel=True
        )
        
        # 2. 检查是否有绑定渠道
        binding = await self.link_manager.get_binding(channel, user_id)
        linked_channels = binding['linked_channels'] if binding else {}
        
        # 3. 构建上下文
        context = {
            "channel": channel,
            "user_id": user_id,
            "memories_count": len(memories),
            "memories": memories,
            "linked_channels": linked_channels,
            "has_cross_channel": len(linked_channels) > 0
        }
        
        # 4. 如果有跨渠道记忆，提示用户
        if context['has_cross_channel'] and context['memories_count'] > 0:
            context['welcome_message'] = (
                f"欢迎回来！我注意到您在 {', '.join(linked_channels.keys())} "
                f"也有账号，已为您加载了 {len(memories)} 条历史记忆。"
            )
        else:
            context['welcome_message'] = "欢迎回来！"
        
        return context
    
    async def on_message_received(self, channel: str, user_id: str, 
                                  message: str, conversation_id: str) -> dict:
        """
        收到用户消息时的处理
        
        Args:
            channel: 来源渠道
            user_id: 用户 ID
            message: 用户消息
            conversation_id: 对话 ID
        
        Returns:
            处理结果（包括是否触发记忆查询）
        """
        await self.initialize()
        
        result = {
            "should_query_memory": False,
            "query_results": None,
            "should_memorize": False,
            "memory_content": None
        }
        
        # 1. 检测是否触发记忆查询
        query_triggers = [
            "昨天", "上次", "之前", "记得", "查一下", "共享记忆",
            "其他渠道", "飞书", "QQ", "微信"
        ]
        
        if any(trigger in message for trigger in query_triggers):
            result["should_query_memory"] = True
            result["query_results"] = await self.memory_service.query_memories(
                channel=channel,
                user_id=user_id,
                start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                cross_channel=True
            )
        
        # 2. 检测是否需要记忆（简单规则，实际应该用 LLM 判断）
        memory_keywords = [
            "记住", "偏好", "喜欢", "不喜欢", "习惯", "通常",
            "我的", "我是", "我在", "我做"
        ]
        
        if any(kw in message for kw in memory_keywords):
            result["should_memorize"] = True
            result["memory_content"] = {
                "content": message,
                "topic": "用户消息",
                "timestamp": time.time()
            }
        
        return result
    
    async def on_task_completed(self, channel: str, user_id: str,
                                task_input: str, task_result: str) -> bool:
        """
        任务完成后的处理
        
        Args:
            channel: 来源渠道
            user_id: 用户 ID
            task_input: 任务输入
            task_result: 任务结果
        
        Returns:
            是否成功写入记忆
        """
        await self.initialize()
        
        # 判断任务结果是否值得记忆
        should_remember = self._should_remember_task(task_input, task_result)
        
        if should_remember:
            # 提取关键信息
            summary = self._extract_task_summary(task_input, task_result)
            
            # 写入记忆
            await self.memory_service.save_memory(
                channel=channel,
                user_id=user_id,
                content=summary,
                metadata={
                    "topic": "任务完成",
                    "task_input": task_input,
                    "timestamp": time.time()
                }
            )
            
            return True
        
        return False
    
    def _should_remember_task(self, task_input: str, task_result: str) -> bool:
        """判断任务是否值得记忆"""
        # 简单规则示例
        # 实际应该用 LLM 判断
        
        # 用户偏好相关的任务
        if "偏好" in task_input or "风格" in task_input:
            return True
        
        # 重要决策
        if "决定" in task_result or "选择" in task_result:
            return True
        
        # 学习到的新知识
        if "发现" in task_result or "了解到" in task_result:
            return True
        
        return False
    
    def _extract_task_summary(self, task_input: str, task_result: str) -> str:
        """提取任务摘要"""
        # 简单摘要，实际应该用 LLM 生成
        return f"""
**任务:** {task_input[:100]}

**结果:** {task_result[:200]}

**时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    async def explicit_query(self, channel: str, user_id: str, 
                            query: str) -> dict:
        """
        显式查询共享记忆
        
        Args:
            channel: 来源渠道
            user_id: 用户 ID
            query: 查询内容
        
        Returns:
            查询结果
        """
        await self.initialize()
        
        # 解析查询（简单版本，实际应该用 LLM）
        days = 7
        if "最近" in query:
            days = 7
        elif "上个月" in query:
            days = 30
        elif "全部" in query:
            days = 365
        
        # 执行查询
        memories = await self.memory_service.query_memories(
            channel=channel,
            user_id=user_id,
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            cross_channel=True
        )
        
        # 语义过滤（简单版本，实际应该用 embedding）
        filtered = {}
        for key, content in memories.items():
            if any(word in content.lower() for word in query.lower().split()):
                filtered[key] = content
        
        return {
            "query": query,
            "days": days,
            "total_found": len(memories),
            "filtered_count": len(filtered),
            "results": filtered
        }
    
    async def bind_my_channels(self, channel: str, user_id: str,
                               other_channels: dict) -> dict:
        """
        帮助用户绑定多渠道
        
        Args:
            channel: 当前渠道
            user_id: 当前渠道用户 ID
            other_channels: 其他渠道映射 {channel_name: user_id}
        
        Returns:
            绑定结果
        """
        await self.initialize()
        
        # 构建完整的渠道映射
        all_channels = {channel: user_id}
        all_channels.update(other_channels)
        
        # 创建绑定
        result = await self.link_manager.create_binding(
            channels=all_channels,
            user_note=f"从 {channel} 渠道创建"
        )
        
        return result
    
    async def get_sync_status(self) -> dict:
        """获取同步状态"""
        await self.initialize()
        return await self.sync_service.check_sync_status()


# 使用示例
async def demo_usage():
    """演示使用"""
    print("\n" + "="*60)
    print("灵犀 v3.0 - 共享记忆库集成演示")
    print("="*60 + "\n")
    
    lingxi = LingxiWithSharedMemory()
    
    # 场景 1: 会话启动
    print("📱 场景 1: 用户从飞书发起会话")
    context = await lingxi.on_session_start(
        channel="feishu",
        user_id="ou_4192609eb71f18ae82f9163f02bef144"
    )
    print(f"欢迎消息：{context['welcome_message']}")
    print(f"加载记忆数：{context['memories_count']}")
    print(f"绑定渠道：{list(context['linked_channels'].keys())}\n")
    
    # 场景 2: 收到消息
    print("💬 场景 2: 用户发送消息")
    message = "我记得昨天在 QQ 上问过你一个问题"
    result = await lingxi.on_message_received(
        channel="feishu",
        user_id="ou_4192609eb71f18ae82f9163f02bef144",
        message=message,
        conversation_id="conv_123"
    )
    print(f"消息：{message}")
    print(f"触发记忆查询：{result['should_query_memory']}")
    if result['query_results']:
        print(f"查询结果数：{len(result['query_results'])}\n")
    
    # 场景 3: 显式查询
    print("🔍 场景 3: 用户显式查询共享记忆")
    query_result = await lingxi.explicit_query(
        channel="feishu",
        user_id="ou_4192609eb71f18ae82f9163f02bef144",
        query="查一下共享记忆里关于偏好的内容"
    )
    print(f"查询：{query_result['query']}")
    print(f"找到记忆：{query_result['total_found']} 条")
    print(f"过滤后：{query_result['filtered_count']} 条\n")
    
    # 场景 4: 任务完成
    print("✅ 场景 4: 任务完成后写入记忆")
    remembered = await lingxi.on_task_completed(
        channel="feishu",
        user_id="ou_4192609eb71f18ae82f9163f02bef144",
        task_input="帮我分析用户的工作习惯",
        task_result="用户通常在早上 9 点开始工作，偏好简洁的回复风格"
    )
    print(f"任务结果：{remembered}")
    print(f"已写入记忆：{remembered}\n")
    
    # 场景 5: 同步状态
    print("📊 场景 5: 查看同步状态")
    status = await lingxi.get_sync_status()
    print(f"当前时间：{status['current_time']}")
    print(f"下次同步：{status['next_sync_time']}")
    print(f"距离同步：{status['hours_until_sync']:.2f} 小时\n")
    
    print("✅ 演示完成\n")


if __name__ == "__main__":
    from datetime import timedelta  # 需要导入
    asyncio.run(demo_usage())
