#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 异步任务执行器
负责后台任务执行、状态追踪、完成通知
支持多任务并行处理
"""

import json
import os
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from task_manager import TaskManager, TaskInfo, TaskStatus, generate_task_id, get_task_manager

# ==================== 异步执行器 ====================

class AsyncExecutor:
    """异步任务执行器
    
    功能:
    - 后台执行耗时任务
    - 追踪任务状态
    - 完成后主动通知用户
    - 支持多任务并行
    """
    
    def __init__(self, task_manager: TaskManager = None):
        """初始化执行器
        
        Args:
            task_manager: 任务管理器实例
        """
        self.task_manager = task_manager or get_task_manager()
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute(
        self,
        task_type: str,
        description: str,
        command: str,
        user_id: str,
        channel: str = "qqbot",
        notify_on_complete: bool = True,
        priority: int = 0,
        env: Dict[str, str] = None
    ) -> str:
        """执行后台任务
        
        Args:
            task_type: 任务类型 (wechat-publish, xhs-post, etc.)
            description: 任务描述
            command: 执行的命令
            user_id: 用户 ID (QQ openid)
            channel: 通知渠道
            notify_on_complete: 完成后是否通知
            priority: 优先级
            env: 环境变量
            
        Returns:
            任务 ID
        """
        # 创建任务信息
        task = TaskInfo(
            id=generate_task_id(),
            type=task_type,
            description=description,
            status=TaskStatus.PENDING,
            user_id=user_id,
            channel=channel,
            notify_on_complete=notify_on_complete,
            priority=priority
        )
        
        # 注册任务
        self.task_manager.register(task)
        
        # 立即回复用户
        await self._send_immediate_reply(
            user_id=user_id,
            channel=channel,
            task_id=task.id,
            description=description
        )
        
        # 启动后台执行
        asyncio.create_task(
            self._run_task(task, command, env)
        )
        
        print(f"🚀 任务已启动：{task.id}")
        return task.id
    
    async def _run_task(
        self,
        task: TaskInfo,
        command: str,
        env: Dict[str, str] = None
    ):
        """运行任务（后台执行）
        
        Args:
            task: 任务信息
            command: 执行命令
            env: 环境变量
        """
        # 更新状态为运行中
        self.task_manager.update(
            task.id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now().timestamp() * 1000
        )
        
        try:
            # 执行命令
            print(f"⚙️ 执行任务 {task.id}: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **(env or {})}
            )
            
            stdout, stderr = await process.communicate()
            
            # 处理结果
            if process.returncode == 0:
                result = {
                    "success": True,
                    "stdout": stdout.decode('utf-8', errors='ignore'),
                    "stderr": stderr.decode('utf-8', errors='ignore'),
                    "returncode": process.returncode
                }
                
                self.task_manager.update(
                    task.id,
                    status=TaskStatus.COMPLETED,
                    completed_at=datetime.now().timestamp() * 1000,
                    result=result
                )
                
                print(f"✅ 任务完成：{task.id}")
                
                # 发送完成通知
                if task.notify_on_complete:
                    await self._send_completion_notification(task, result)
                
            else:
                error_msg = stderr.decode('utf-8', errors='ignore') or f"返回码：{process.returncode}"
                
                self.task_manager.update(
                    task.id,
                    status=TaskStatus.FAILED,
                    completed_at=datetime.now().timestamp() * 1000,
                    error=error_msg
                )
                
                print(f"❌ 任务失败：{task.id} - {error_msg}")
                
                # 发送失败通知
                if task.notify_on_complete:
                    await self._send_failure_notification(task, error_msg)
        
        except Exception as e:
            error_msg = str(e)
            
            self.task_manager.update(
                task.id,
                status=TaskStatus.FAILED,
                completed_at=datetime.now().timestamp() * 1000,
                error=error_msg
            )
            
            print(f"❌ 任务异常：{task.id} - {error_msg}")
            
            # 发送失败通知
            if task.notify_on_complete:
                await self._send_failure_notification(task, error_msg)
    
    async def _send_immediate_reply(
        self,
        user_id: str,
        channel: str,
        task_id: str,
        description: str
    ):
        """发送立即回复（不阻塞）
        
        告诉用户任务已接收，正在后台处理
        """
        message = f"好的老板，任务已接收～ 💋\n\n📋 {description}\n⚙️ 正在后台处理中，完成后我马上 QQ 通知你！"
        
        # 通过 OpenClaw message 工具发送
        await self._send_message(
            channel=channel,
            to=user_id,
            message=message
        )
    
    async def _send_completion_notification(
        self,
        task: TaskInfo,
        result: Dict[str, Any]
    ):
        """发送完成通知
        
        Args:
            task: 任务信息
            result: 执行结果
        """
        # 根据任务类型生成通知消息
        if task.type == "wechat-publish":
            url = result.get("stdout", "").split("链接：")[-1].strip() if "链接：" in result.get("stdout", "") else "未知"
            message = f"""老板，文章发布成功啦！💋

📝 任务：{task.description}
🔗 链接：{url}

快去看看吧～ ✨"""
        
        elif task.type == "xhs-post":
            message = f"""老板，小红书笔记发布成功啦！💋

📝 任务：{task.description}

笔记已经和粉丝见面咯～ ✨"""
        
        else:
            message = f"""老板，任务完成啦！💋

📋 任务：{task.description}
✅ 状态：执行成功

随时吩咐新任务～ ✨"""
        
        await self._send_message(
            channel=task.channel,
            to=task.user_id,
            message=message
        )
    
    async def _send_failure_notification(
        self,
        task: TaskInfo,
        error_msg: str
    ):
        """发送失败通知
        
        Args:
            task: 任务信息
            error_msg: 错误信息
        """
        message = f"""老板，任务执行遇到问题了... 💦

📋 任务：{task.description}
❌ 错误：{error_msg[:200]}

需要我重新尝试吗？随时吩咐～ 💋"""
        
        await self._send_message(
            channel=task.channel,
            to=task.user_id,
            message=message
        )
    
    async def _send_message(
        self,
        channel: str,
        to: str,
        message: str
    ):
        """发送消息（通过 OpenClaw）
        
        这里使用 subprocess 调用 OpenClaw CLI
        实际部署时应该直接调用 OpenClaw API
        """
        try:
            # 构建 cron payload 用于发送消息
            # 使用 at 模式，立即执行（当前时间 + 1 秒）
            now_ms = int(datetime.now().timestamp() * 1000) + 1000
            
            payload = {
                "action": "add",
                "job": {
                    "name": f"notify_{generate_task_id('msg')}",
                    "schedule": {
                        "kind": "at",
                        "atMs": now_ms
                    },
                    "sessionTarget": "isolated",
                    "wakeMode": "now",
                    "deleteAfterRun": True,
                    "payload": {
                        "kind": "agentTurn",
                        "message": message,
                        "deliver": True,
                        "channel": channel,
                        "to": to
                    }
                }
            }
            
            # 调用 openclaw cron add
            cmd = f"openclaw cron add '{json.dumps(payload)}'"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            print(f"📤 通知消息已发送：{to}")
        
        except Exception as e:
            print(f"⚠️ 发送消息失败：{e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态信息
        """
        task = self.task_manager.get(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "type": task.type,
            "description": task.description,
            "status": task.status.value,
            "created_at": datetime.fromtimestamp(task.created_at / 1000).isoformat(),
            "started_at": datetime.fromtimestamp(task.started_at / 1000).isoformat() if task.started_at else None,
            "completed_at": datetime.fromtimestamp(task.completed_at / 1000).isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """获取所有任务状态
        
        Args:
            status: 状态过滤
            
        Returns:
            任务状态列表
        """
        tasks = self.task_manager.get_all(status)
        return [self.get_task_status(t.id) for t in tasks]

# ==================== 单例实例 ====================

_executor: Optional[AsyncExecutor] = None

def get_executor() -> AsyncExecutor:
    """获取全局执行器实例"""
    global _executor
    if _executor is None:
        _executor = AsyncExecutor()
    return _executor

# ==================== 测试 ====================

async def main():
    """测试入口"""
    executor = get_executor()
    
    # 测试任务
    task_id = await executor.execute(
        task_type="test-task",
        description="测试后台任务",
        command="echo 'Hello World' && sleep 2 && echo 'Done'",
        user_id="test_user_123",
        channel="qqbot"
    )
    
    print(f"🚀 任务已启动：{task_id}")
    
    # 等待任务完成
    await asyncio.sleep(5)
    
    # 查询状态
    status = executor.get_task_status(task_id)
    print(f"\n📋 任务状态：{json.dumps(status, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())
