#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 带记忆的心跳机制 v3.0

心跳任务执行结果自动记录到记忆系统
心跳执行时获取完整上下文
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trinity_state import get_state_manager, TrinityStateManager

class HeartbeatWithMemory:
    """
    带记忆的心跳机制
    
    功能：
    - 心跳任务执行结果记录到记忆
    - 心跳执行时获取完整上下文
    - 心跳历史可查询
    """
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
    
    async def execute_task(self, task: Dict, context_override: Dict = None) -> Dict:
        """
        执行心跳任务
        
        Args:
            task: 任务配置
            context_override: 可选的上下文覆盖
        
        Returns:
            执行结果
        """
        task_name = task.get("name", "unknown")
        
        print(f"\n⏰ 心跳任务：{task_name}")
        print(f"   开始时间：{datetime.now().isoformat()}")
        
        try:
            # 1. 获取完整上下文（包括所有记忆）
            context = context_override or self.state.get_context()
            print(f"   ✅ 获取上下文：{len(context['knowledge'])} 条知识，{len(context['preferences'])} 个偏好")
            
            # 2. 执行任务（调用实际的任务逻辑）
            result = await self._execute_task_logic(task, context)
            
            # 3. 记录到心跳历史
            self.state.add_heartbeat_history({
                "task": task_name,
                "executed_at": datetime.now().isoformat(),
                "result_summary": self._summarize_result(result),
                "saved_to_memory": True
            })
            
            # 4. 重要结果保存到长期记忆
            if self._is_important_result(result):
                memory_id = self.state.add_knowledge({
                    "type": "heartbeat_discovery",
                    "content": self._summarize_result(result),
                    "tags": task.get("tags", ["heartbeat"]),
                    "metadata": {
                        "task_name": task_name,
                        "executed_at": datetime.now().isoformat()
                    }
                })
                print(f"   ✅ 保存到记忆：{memory_id}")
            
            # 5. 更新心跳状态
            self.state.update_heartbeat(
                last_check=datetime.now().isoformat(),
                last_task=task_name,
                last_result=result
            )
            
            print(f"   ✅ 任务完成")
            return result
            
        except Exception as e:
            print(f"   ❌ 任务失败：{e}")
            
            # 记录失败
            self.state.add_heartbeat_history({
                "task": task_name,
                "executed_at": datetime.now().isoformat(),
                "error": str(e),
                "saved_to_memory": False
            })
            
            return {"error": str(e)}
    
    async def _execute_task_logic(self, task: Dict, context: Dict) -> Any:
        """
        执行实际的任务逻辑
        
        这个方法应该被重写或动态加载实际的任务处理器
        """
        task_name = task.get("name", "")
        
        # 根据任务名分发到不同的处理器
        if "新闻" in task_name or "news" in task_name.lower():
            return await self._handle_news_task(task, context)
        elif "提醒" in task_name or "reminder" in task_name.lower():
            return await self._handle_reminder_task(task, context)
        else:
            # 默认：执行任务描述中的指令
            return await self._handle_generic_task(task, context)
    
    async def _handle_news_task(self, task: Dict, context: Dict) -> Dict:
        """处理新闻监控任务"""
        
        # 从上下文获取用户偏好
        preferences = context.get("preferences", {})
        news_topics = preferences.get("news_topics", ["创新创业", "社会保障", "民生"])
        
        # 获取历史新闻（避免重复推送）
        recent_news = self.state.search_knowledge("新闻", top_k=5)
        recent_titles = [n.get("content", "")[:50] for n in recent_news]
        
        print(f"   📰 新闻偏好：{news_topics}")
        print(f"   📰 历史新闻：{len(recent_news)} 条")
        
        # TODO: 实际调用新闻搜索 API
        # 这里返回模拟结果
        return {
            "type": "news_summary",
            "topics": news_topics,
            "count": 3,
            "news": [
                {
                    "title": "模拟新闻 1",
                    "source": "新华网",
                    "summary": "这是模拟的新闻内容"
                }
            ],
            "filtered_duplicates": len(recent_titles)
        }
    
    async def _handle_reminder_task(self, task: Dict, context: Dict) -> Dict:
        """处理提醒任务"""
        
        # 从上下文获取待办任务
        pending_tasks = context.get("pending_tasks", [])
        
        print(f"   ⏰ 待办任务：{len(pending_tasks)} 个")
        
        return {
            "type": "reminder_check",
            "pending_count": len(pending_tasks),
            "tasks": pending_tasks
        }
    
    async def _handle_generic_task(self, task: Dict, context: Dict) -> Dict:
        """处理通用任务"""
        
        print(f"   🔧 通用任务处理")
        
        return {
            "type": "generic",
            "task": task.get("name"),
            "context_keys": list(context.keys())
        }
    
    def _summarize_result(self, result: Any) -> str:
        """总结执行结果"""
        if isinstance(result, dict):
            if "type" in result:
                return f"{result['type']}: {str(result)[:200]}"
            return str(result)[:200]
        elif isinstance(result, str):
            return result[:200]
        else:
            return str(result)[:200]
    
    def _is_important_result(self, result: Any) -> bool:
        """判断结果是否重要（需要保存到长期记忆）"""
        if isinstance(result, dict):
            # 新闻摘要、任务完成结果等是重要的
            important_types = ["news_summary", "task_complete", "discovery"]
            return result.get("type") in important_types
        return False
    
    def get_heartbeat_history(self, limit: int = 10) -> List[Dict]:
        """获取心跳历史"""
        return self.state.state.heartbeat.get("history", [])[-limit:]
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """获取已调度的任务列表"""
        return self.state.state.heartbeat.get("tasks", [])

# ========== 工厂函数 ==========

def get_heartbeat_with_memory(user_id: str) -> HeartbeatWithMemory:
    """获取带记忆的心跳处理器"""
    state_manager = get_state_manager(user_id)
    return HeartbeatWithMemory(state_manager)

# ========== 测试入口 ==========

if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("⏰ 测试带记忆的心跳机制")
    print("=" * 60)
    
    # 创建处理器
    user_id = "test_user_123"
    heartbeat = get_heartbeat_with_memory(user_id)
    
    async def test():
        # 测试新闻监控任务
        print("\n1️⃣ 测试新闻监控任务")
        result = await heartbeat.execute_task({
            "name": "每日新闻监控",
            "schedule": "0 9 * * *",
            "tags": ["新闻", "两会"]
        })
        print(f"   结果：{result}")
        
        # 测试提醒任务
        print("\n2️⃣ 测试提醒任务")
        result = await heartbeat.execute_task({
            "name": "待办提醒",
            "schedule": "0 */2 * * *"
        })
        print(f"   结果：{result}")
        
        # 查看心跳历史
        print("\n3️⃣ 查看心跳历史")
        history = heartbeat.get_heartbeat_history(limit=5)
        for entry in history:
            print(f"   - {entry['task']}: {entry['result_summary']}")
        
        # 查看已保存的知识
        print("\n4️⃣ 查看已保存的知识")
        state_manager = get_state_manager(user_id)
        knowledge = state_manager.state.memory["knowledge"]
        for k in knowledge[-3:]:
            print(f"   - {k['type']}: {k['content'][:50]}")
    
    asyncio.run(test())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
