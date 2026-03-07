#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 带记忆的任务执行器 v3.0

任务执行参考历史记忆
任务结果反馈到记忆系统
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trinity_state import get_state_manager, TrinityStateManager
from scripts.active_memory import get_active_memory_system, ActiveMemorySystem
from scripts.heartbeat_with_memory import get_heartbeat_with_memory, HeartbeatWithMemory

class TaskWithMemory:
    """
    带记忆的任务执行器
    
    功能：
    - 任务执行参考完整记忆
    - 任务结果智能记录
    - 支持复杂多轮对话
    """
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
        self.memory = ActiveMemorySystem(state_manager)
        self.heartbeat = HeartbeatWithMemory(state_manager)
    
    async def execute(self, user_input: str, user_id: str = None, context: Dict = None) -> Any:
        """
        执行任务
        
        Args:
            user_input: 用户输入
            user_id: 用户 ID（可选，默认使用状态管理器的用户 ID）
            context: 额外上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print(f"\n🎭 任务执行器：收到任务")
        print(f"   输入：{user_input[:100]}...")
        print(f"   任务 ID: {task_id}")
        
        try:
            # 1. 设置当前任务
            self.state.set_current_task({
                "id": task_id,
                "input": user_input,
                "user_id": user_id or self.state.user_id
            })
            
            # 2. 获取完整上下文（包括所有记忆）
            base_context = self.state.get_context()
            
            # 3. 主动记忆检索（增强上下文）
            enhanced_context = self.memory.on_task_start(user_input, context)
            
            # 合并上下文
            full_context = {
                **base_context,
                **enhanced_context,
                "task_id": task_id,
                "started_at": datetime.now().isoformat()
            }
            
            print(f"   ✅ 上下文：{len(full_context['knowledge'])} 条知识，{len(full_context['preferences'])} 个偏好")
            
            # 4. 意图识别
            intent = self._parse_intent(user_input, full_context)
            print(f"   📋 意图：{intent['type']} (置信度：{intent['confidence']:.2f})")
            
            # 5. 任务规划
            plan = self._create_plan(intent, full_context)
            print(f"   📦 计划：{len(plan['steps'])} 个步骤")
            
            # 6. 执行计划
            result = await self._execute_plan(plan, full_context)
            
            # 7. 记录到记忆
            self.memory.on_task_complete(user_input, result, full_context)
            
            # 8. 完成当前任务
            self.state.complete_current_task(result)
            
            elapsed = (time.time() - start_time) * 1000
            print(f"   ✅ 任务完成，耗时：{elapsed:.2f}ms")
            
            return result
            
        except Exception as e:
            print(f"   ❌ 任务失败：{e}")
            
            # 记录错误
            self.state.complete_current_task({"error": str(e)})
            
            return {"error": str(e)}
    
    def _parse_intent(self, user_input: str, context: Dict) -> Dict:
        """
        意图识别
        
        返回：
        {
            "type": "question|task|chat|command",
            "confidence": 0.95,
            "entities": [],
            "action": ""
        }
        """
        # 简单规则匹配（实际应该用 LLM）
        user_input_lower = user_input.lower()
        
        # 问题类型
        if any(kw in user_input for kw in ["?", "？", "什么", "怎么", "为什么", "哪里"]):
            return {
                "type": "question",
                "confidence": 0.9,
                "entities": self._extract_entities(user_input),
                "action": "answer"
            }
        
        # 任务类型
        if any(kw in user_input for kw in ["帮", "请", "写", "发", "查", "搜"]):
            return {
                "type": "task",
                "confidence": 0.85,
                "entities": self._extract_entities(user_input),
                "action": "execute"
            }
        
        # 命令类型
        if any(kw in user_input for kw in ["打开", "关闭", "启动", "停止"]):
            return {
                "type": "command",
                "confidence": 0.95,
                "entities": self._extract_entities(user_input),
                "action": "control"
            }
        
        # 默认：聊天
        return {
            "type": "chat",
            "confidence": 0.7,
            "entities": self._extract_entities(user_input),
            "action": "respond"
        }
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """提取实体"""
        # 简单实现：提取时间、地点等
        entities = []
        
        # 时间实体
        time_patterns = ["今天", "明天", "后天", "早上", "下午", "晚上"]
        for pattern in time_patterns:
            if pattern in text:
                entities.append({"type": "time", "value": pattern})
        
        return entities
    
    def _create_plan(self, intent: Dict, context: Dict) -> Dict:
        """创建任务计划"""
        
        plan = {
            "intent": intent,
            "steps": [],
            "context": context
        }
        
        # 根据意图类型创建计划
        if intent["type"] == "question":
            plan["steps"] = [
                {"action": "search_knowledge", "params": {"query": intent.get("entities", [])}},
                {"action": "generate_answer", "params": {"intent": intent}}
            ]
        
        elif intent["type"] == "task":
            plan["steps"] = [
                {"action": "analyze_task", "params": {"input": intent}},
                {"action": "execute_task", "params": {"intent": intent}},
                {"action": "format_result", "params": {}}
            ]
        
        elif intent["type"] == "command":
            plan["steps"] = [
                {"action": "validate_command", "params": {"intent": intent}},
                {"action": "execute_command", "params": {"intent": intent}}
            ]
        
        else:  # chat
            plan["steps"] = [
                {"action": "generate_response", "params": {"intent": intent, "context": context}}
            ]
        
        return plan
    
    async def _execute_plan(self, plan: Dict, context: Dict) -> Any:
        """执行计划"""
        
        results = []
        
        for step in plan["steps"]:
            action = step["action"]
            params = step.get("params", {})
            
            print(f"   🔧 执行步骤：{action}")
            
            # 分发到不同的处理器
            if action == "search_knowledge":
                result = await self._search_knowledge(params, context)
            elif action == "generate_answer":
                result = await self._generate_answer(params, context)
            elif action == "analyze_task":
                result = await self._analyze_task(params, context)
            elif action == "execute_task":
                result = await self._execute_task(params, context)
            elif action == "format_result":
                result = self._format_result(results, context)
            elif action == "generate_response":
                result = await self._generate_response(params, context)
            else:
                result = {"action": action, "status": "unknown"}
            
            results.append(result)
        
        # 返回最后一步的结果
        return results[-1] if results else None
    
    async def _search_knowledge(self, params: Dict, context: Dict) -> List[Dict]:
        """搜索知识"""
        query = str(params.get("query", ""))
        results = self.state.search_knowledge(query, top_k=5)
        print(f"      📚 找到 {len(results)} 条知识")
        return results
    
    async def _generate_answer(self, params: Dict, context: Dict) -> Dict:
        """生成答案"""
        # TODO: 调用 LLM 生成答案
        return {
            "type": "answer",
            "content": "这是模拟的答案",
            "based_on": "knowledge_search"
        }
    
    async def _analyze_task(self, params: Dict, context: Dict) -> Dict:
        """分析任务"""
        return {
            "type": "task_analysis",
            "complexity": "simple",
            "estimated_time": "1m"
        }
    
    async def _execute_task(self, params: Dict, context: Dict) -> Any:
        """执行任务"""
        # TODO: 根据任务类型调用不同的工具
        return {
            "type": "task_complete",
            "status": "success",
            "content": "任务已完成"
        }
    
    def _format_result(self, results: List[Any], context: Dict) -> Dict:
        """格式化结果"""
        return {
            "type": "formatted_result",
            "results": results,
            "count": len(results)
        }
    
    async def _generate_response(self, params: Dict, context: Dict) -> Dict:
        """生成回复"""
        # TODO: 调用 LLM 生成回复
        return {
            "type": "response",
            "content": "这是模拟的回复",
            "style": context.get("preferences", {}).get("response_style", "default")
        }

# ========== 工厂函数 ==========

def get_task_with_memory(user_id: str) -> TaskWithMemory:
    """获取带记忆的任务执行器"""
    state_manager = get_state_manager(user_id)
    return TaskWithMemory(state_manager)

# ========== 测试入口 ==========

if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("🎭 测试带记忆的任务执行器")
    print("=" * 60)
    
    # 创建执行器
    user_id = "test_user_123"
    executor = get_task_with_memory(user_id)
    
    async def test():
        # 测试问题
        print("\n1️⃣ 测试问题：今天天气怎么样")
        result = await executor.execute("今天天气怎么样")
        print(f"   结果：{result}")
        
        # 测试任务
        print("\n2️⃣ 测试任务：帮我写今天的工作日报")
        result = await executor.execute("帮我写今天的工作日报，用简洁的风格")
        print(f"   结果：{result}")
        
        # 测试聊天
        print("\n3️⃣ 测试聊天：你好")
        result = await executor.execute("你好")
        print(f"   结果：{result}")
        
        # 查看记忆
        print("\n4️⃣ 查看已保存的记忆")
        state = executor.state.state
        print(f"   任务历史数：{len(state.task['history'])}")
        print(f"   知识数：{len(state.memory['knowledge'])}")
        
        # 查看完整状态
        print("\n5️⃣ 查看完整状态")
        full_state = executor.state.get_full_state()
        print(f"   状态键：{list(full_state.keys())}")
    
    asyncio.run(test())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
