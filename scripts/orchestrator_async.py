#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 异步编排器（支持多任务并行）
心有灵犀，一点就通

在原有 orchestrator 基础上增加：
- 异步任务执行
- 后台任务不阻塞主对话
- 完成后主动通知用户
- HEARTBEAT.md 任务状态同步
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from task_manager import TaskManager, TaskInfo, TaskStatus, generate_task_id, get_task_manager
from async_executor import AsyncExecutor, get_executor

# 导入原有编排器组件
from orchestrator import (
    SmartOrchestrator,
    parse_intent,
    decompose_task,
    ROLE_CONFIG,
    TaskStatus as OrchTaskStatus,
    RoleType
)

# 导入心跳同步模块
try:
    from heartbeat_task_sync import on_task_received, on_task_completed, get_heartbeat_sync
    HEARTBEAT_ENABLED = True
except ImportError:
    HEARTBEAT_ENABLED = False
    print("⚠️  heartbeat_task_sync 未找到，心跳同步功能已禁用")

# ==================== 异步编排器 ====================

class AsyncOrchestrator(SmartOrchestrator):
    """灵犀 - 异步智慧调度系统
    
    支持多任务并行处理，后台任务不阻塞主对话
    """
    
    def __init__(self):
        super().__init__()
        self.task_manager = get_task_manager()
        self.executor = get_executor()
    
    async def execute_async(
        self,
        user_input: str,
        user_id: str,
        channel: str = "qqbot",
        is_background: bool = False
    ) -> str:
        """异步执行用户任务
        
        Args:
            user_input: 用户输入
            user_id: 用户 ID (QQ openid)
            channel: 通知渠道
            is_background: 是否后台执行（不阻塞）
            
        Returns:
            立即回复消息（后台任务）或完整结果（即时任务）
        """
        print(f"\n🎭 {self.name}（{self.role}）: 收到任务，开始分析...\n")
        
        # 生成任务 ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 1. 解析意图
        intent = parse_intent(user_input, user_id)
        print(f"📋 意图识别：{intent['types']}")
        
        # ❤️ 心跳同步：任务收到时自动写入 HEARTBEAT.md
        if HEARTBEAT_ENABLED:
            try:
                on_task_received(
                    task_id=task_id,
                    description=user_input[:100],
                    channel=channel,
                    user_id=user_id
                )
                print(f"💓 心跳同步：任务 {task_id} 已写入 HEARTBEAT.md")
            except Exception as e:
                print(f"⚠️ 心跳同步失败：{e}")
        
        # 2. 判断是否为耗时任务
        is_long_running = self._is_long_running_task(intent)
        
        if is_long_running and is_background:
            # 后台异步执行
            return await self._execute_background(
                user_input=user_input,
                user_id=user_id,
                channel=channel,
                intent=intent,
                task_id=task_id
            )
        else:
            # 同步执行（原有逻辑）
            try:
                result = await self.execute(user_input, user_id)
                # ❤️ 心跳同步：任务完成时更新状态
                if HEARTBEAT_ENABLED:
                    on_task_completed(task_id=task_id)
                    print(f"💓 心跳同步：任务 {task_id} 已完成")
                return result.final_output
            except Exception as e:
                # 失败也要标记完成
                if HEARTBEAT_ENABLED:
                    on_task_completed(task_id=task_id)
                raise e
    
    def _is_long_running_task(self, intent: Dict[str, Any]) -> bool:
        """判断是否为耗时任务
        
        耗时任务包括：
        - 微信公众号发布
        - 小红书发布
        - 图片生成
        - 复杂数据处理
        """
        long_running_types = ["social_publish", "image_generation"]
        long_running_keywords = ["公众号", "微信", "发布", "小红书", "生成图片", "自拍"]
        
        # 检查意图类型
        for t in long_running_types:
            if t in intent.get("types", []):
                return True
        
        # 检查关键词
        for kw in long_running_keywords:
            if kw in intent.get("keywords", []):
                return True
        
        return False
    
    async def _execute_background(
        self,
        user_input: str,
        user_id: str,
        channel: str,
        intent: Dict[str, Any],
        task_id: str = None
    ) -> str:
        """后台执行耗时任务
        
        立即返回接收确认，实际任务在后台执行
        """
        # 确定任务类型
        task_type = self._determine_task_type(intent)
        
        # 构建执行命令
        command = self._build_command(user_input, intent)
        
        # 启动后台任务
        executor_task_id = await self.executor.execute(
            task_type=task_type,
            description=user_input[:100],
            command=command,
            user_id=user_id,
            channel=channel,
            notify_on_complete=True
        )
        
        # 如果没有传入 task_id，使用 executor 返回的 ID
        if task_id is None:
            task_id = executor_task_id
        
        # ❤️ 心跳同步：后台任务完成时更新状态
        async def execute_and_sync():
            try:
                # 等待任务执行完成
                result = await self.executor.get_task_result(executor_task_id)
                # 标记完成
                if HEARTBEAT_ENABLED:
                    on_task_completed(task_id=task_id)
                    print(f"💓 心跳同步：后台任务 {task_id} 已完成")
                return result
            except Exception as e:
                # 失败也要标记完成
                if HEARTBEAT_ENABLED:
                    on_task_completed(task_id=task_id)
                raise e
        
        # 启动后台执行
        asyncio.create_task(execute_and_sync())
        
        # 返回立即回复（不阻塞）
        return f"好的老板，任务已接收～ 💋\n\n📋 {user_input[:50]}...\n⚙️ 正在后台处理中，完成后我马上 QQ 通知你！\n\n任务 ID: `{task_id}`"
    
    def _determine_task_type(self, intent: Dict[str, Any]) -> str:
        """根据意图确定任务类型"""
        if "social_publish" in intent.get("types", []):
            platform = intent.get("platform") or ""
            if "微信" in platform or "公众号" in platform:
                return "wechat-publish"
            elif "小红书" in platform:
                return "xhs-post"
            elif "微博" in platform:
                return "weibo-post"
            elif "抖音" in platform:
                return "douyin-post"
        
        if "image_generation" in intent.get("types", []):
            return "image-gen"
        
        if "coding" in intent.get("types", []):
            return "code-exec"
        
        if "data_analysis" in intent.get("types", []):
            return "data-analysis"
        
        return "general-task"
    
    def _build_command(self, user_input: str, intent: Dict[str, Any]) -> str:
        """根据用户输入构建执行命令
        
        这里需要根据实际技能/工具来构建命令
        示例：
        - 微信公众号：wenyan publish article.md --theme lapis
        - 小红书：openclaw xhs publish --text "文案" --images "图片路径"
        """
        task_type = self._determine_task_type(intent)
        
        if task_type == "wechat-publish":
            # 微信公众号发布
            return f"echo '发布微信公众号：{user_input}' && sleep 5 && echo '链接：https://mp.weixin.qq.com/s/example'"
        
        elif task_type == "xhs-post":
            # 小红书发布
            return f"echo '发布小红书：{user_input}' && sleep 3 && echo '发布成功'"
        
        elif task_type == "image-gen":
            # 图片生成
            return f"echo '生成图片：{user_input}' && sleep 10 && echo '图片生成完成'"
        
        else:
            # 通用任务
            return f"echo '执行任务：{user_input}'"
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态信息
        """
        return self.executor.get_task_status(task_id)
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """列出任务
        
        Args:
            status: 状态过滤
            limit: 数量限制
            
        Returns:
            任务列表
        """
        return self.executor.get_all_tasks(status)[:limit]
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否取消成功
        """
        task = self.task_manager.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            print(f"⚠️ 任务已完成/失败，无法取消：{task_id}")
            return False
        
        self.task_manager.update(task_id, status=TaskStatus.CANCELLED)
        print(f"🚫 任务已取消：{task_id}")
        return True

# ==================== 便捷函数 ====================

_async_orchestrator: Optional[AsyncOrchestrator] = None

def get_async_orchestrator() -> AsyncOrchestrator:
    """获取异步编排器实例"""
    global _async_orchestrator
    if _async_orchestrator is None:
        _async_orchestrator = AsyncOrchestrator()
    return _async_orchestrator

# ==================== 使用示例 ====================

async def demo():
    """使用示例"""
    orch = get_async_orchestrator()
    
    # 示例 1: 后台发布微信公众号文章
    print("=" * 50)
    print("示例 1: 后台发布微信公众号文章")
    print("=" * 50)
    
    reply = await orch.execute_async(
        user_input="帮我发布一篇公众号文章，主题是 AI 发展趋势",
        user_id="test_user_123",
        channel="qqbot",
        is_background=True
    )
    print(f"立即回复：{reply}")
    
    # 示例 2: 查询任务状态
    print("\n" + "=" * 50)
    print("示例 2: 查询任务状态")
    print("=" * 50)
    
    await asyncio.sleep(2)
    tasks = await orch.list_tasks()
    for task in tasks:
        print(f"任务：{task['id']} - 状态：{task['status']}")
    
    # 示例 3: 即时任务（不阻塞）
    print("\n" + "=" * 50)
    print("示例 3: 即时任务（查天气）")
    print("=" * 50)
    
    reply = await orch.execute_async(
        user_input="北京明天天气怎么样",
        user_id="test_user_123",
        channel="qqbot",
        is_background=False
    )
    print(f"回复：{reply}")

if __name__ == "__main__":
    asyncio.run(demo())
