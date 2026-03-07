#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 主动记忆系统 v3.0

主动检索相关记忆参与任务决策
智能分类存储任务结果
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trinity_state import TrinityStateManager

class MemoryType:
    """记忆类型枚举"""
    PREFERENCE = "preference"      # 用户偏好
    KNOWLEDGE = "knowledge"        # 知识点
    CONVERSATION = "conversation"  # 对话记录
    TASK_RESULT = "task_result"    # 任务结果
    HEARTBEAT_DISCOVERY = "heartbeat_discovery"  # 心跳发现

class ActiveMemorySystem:
    """
    主动记忆系统
    
    功能：
    - 任务开始时主动提供相关记忆
    - 任务完成后智能记录
    - 向量检索（简单关键词匹配）
    - 记忆分类存储
    """
    
    def __init__(self, state_manager: TrinityStateManager):
        self.state = state_manager
        self.memory_index = {}  # 简单索引
    
    def on_task_start(self, task_input: str, context: Dict = None) -> Dict:
        """
        任务开始时，主动提供相关记忆
        
        Args:
            task_input: 用户输入
            context: 额外上下文
        
        Returns:
            增强后的上下文
        """
        print(f"\n🧠 主动记忆：任务开始")
        print(f"   输入：{task_input[:50]}...")
        
        # 1. 提取关键词
        keywords = self._extract_keywords(task_input)
        print(f"   关键词：{keywords}")
        
        # 2. 检索相关记忆
        relevant_memories = {
            "preferences": self._search_preferences(keywords),
            "knowledge": self._search_knowledge(keywords, top_k=5),
            "conversation": self._get_recent_conversation(limit=5),
            "task_history": self._search_task_history(keywords, top_k=3)
        }
        
        # 3. 生成记忆提示
        memory_hint = self._generate_memory_hint(relevant_memories)
        
        # 4. 返回增强上下文
        enhanced_context = {
            **(context or {}),
            "relevant_memories": relevant_memories,
            "memory_hint": memory_hint
        }
        
        if memory_hint:
            print(f"   💡 记忆提示：{memory_hint[:100]}...")
        
        return enhanced_context
    
    def on_task_complete(self, task_input: str, result: Any, context: Dict = None):
        """
        任务完成后，智能记录
        
        Args:
            task_input: 用户输入
            result: 任务结果
            context: 上下文
        """
        print(f"\n🧠 主动记忆：任务完成")
        print(f"   输入：{task_input[:50]}...")
        
        # 1. 判断是否值得记录
        if not self._worth_recording(result):
            print(f"   ⏭️  跳过记录（结果不重要）")
            return
        
        # 2. 提取记忆
        memory = self._extract_memory(task_input, result, context or {})
        
        if not memory:
            print(f"   ⏭️  跳过记录（无法提取记忆）")
            return
        
        # 3. 分类存储
        memory_type = memory.get("type")
        
        if memory_type == MemoryType.PREFERENCE:
            self._save_preference(memory)
            print(f"   ✅ 保存偏好：{memory['key']}={memory['value']}")
        
        elif memory_type == MemoryType.KNOWLEDGE:
            self._save_knowledge(memory)
            print(f"   ✅ 保存知识：{memory['content'][:50]}...")
        
        elif memory_type == MemoryType.TASK_RESULT:
            self._save_task_result(memory)
            print(f"   ✅ 保存任务结果")
        
        elif memory_type == MemoryType.CONVERSATION:
            self._save_conversation(memory)
            print(f"   ✅ 保存对话记录")
    
    # ========== 记忆检索 ==========
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词（中文按字符，英文按单词）
        # 移除停用词
        stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个"}
        
        # 提取名词、动词等实词
        keywords = []
        
        # 中文关键词（简单按 2-4 字切分）
        for i in range(len(text) - 1):
            word = text[i:i+2]
            if word not in stopwords and not word.isdigit() and not word.isspace():
                keywords.append(word)
            
            if i < len(text) - 2:
                word = text[i:i+3]
                if word not in stopwords and not word.isdigit():
                    keywords.append(word)
        
        # 去重
        return list(set(keywords))[:20]
    
    def _search_preferences(self, keywords: List[str]) -> List[Dict]:
        """搜索相关偏好"""
        preferences = self.state.state.memory.get("preferences", {})
        relevant = []
        
        for key, value in preferences.items():
            # 检查关键词是否匹配
            for kw in keywords:
                if kw in key.lower() or kw in str(value).lower():
                    relevant.append({"key": key, "value": value, "match_score": 1})
                    break
        
        return relevant
    
    def _search_knowledge(self, keywords: List[str], top_k: int = 5) -> List[Dict]:
        """搜索相关知识"""
        knowledge_list = self.state.state.memory.get("knowledge", [])
        scored = []
        
        for knowledge in knowledge_list:
            score = 0
            content = str(knowledge.get("content", "")).lower()
            tags = knowledge.get("tags", [])
            
            # 关键词匹配
            for kw in keywords:
                if kw in content:
                    score += 2
                if kw in tags:
                    score += 1
            
            if score > 0:
                scored.append((score, knowledge))
        
        # 按分数排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
    
    def _get_recent_conversation(self, limit: int = 5) -> List[Dict]:
        """获取最近的对话"""
        # TODO: 实现对话历史检索
        return []
    
    def _search_task_history(self, keywords: List[str], top_k: int = 3) -> List[Dict]:
        """搜索相关任务历史"""
        task_history = self.state.state.task.get("history", [])
        scored = []
        
        for task in task_history:
            score = 0
            input_text = str(task.get("input", "")).lower()
            result_text = str(task.get("result", "")).lower()
            
            for kw in keywords:
                if kw in input_text:
                    score += 2
                if kw in result_text:
                    score += 1
            
            if score > 0:
                scored.append((score, task))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
    
    # ========== 记忆提示生成 ==========
    
    def _generate_memory_hint(self, relevant_memories: Dict) -> str:
        """生成记忆提示"""
        hints = []
        
        # 偏好提示
        prefs = relevant_memories.get("preferences", [])
        if prefs:
            for pref in prefs:
                hints.append(f"用户偏好：{pref['key']}={pref['value']}")
        
        # 知识提示
        knowledge = relevant_memories.get("knowledge", [])
        if knowledge:
            for k in knowledge[:2]:  # 最多 2 条
                hints.append(f"相关知识：{k['content'][:50]}")
        
        # 任务历史提示
        tasks = relevant_memories.get("task_history", [])
        if tasks:
            for task in tasks[:1]:  # 最多 1 条
                hints.append(f"历史任务：{task.get('input', '')[:30]}")
        
        return "；".join(hints) if hints else ""
    
    # ========== 记忆存储 ==========
    
    def _worth_recording(self, result: Any) -> bool:
        """判断是否值得记录"""
        if result is None:
            return False
        
        # 字符串结果（如"已记录您的偏好"）也值得记录
        if isinstance(result, str) and len(result) > 0:
            return True
        
        if isinstance(result, dict):
            # 有明确类型的结果值得记录
            if "type" in result or "error" in result:
                return True
            
            # 有具体内容值得记录
            if len(str(result)) > 20:
                return True
        
        return False
    
    def _extract_memory(self, task_input: str, result: Any, context: Dict) -> Optional[Dict]:
        """提取记忆"""
        
        # 1. 检查是否包含偏好
        preference_keywords = ["喜欢", "不喜欢", "偏好", "习惯", "经常", "总是"]
        for kw in preference_keywords:
            if kw in task_input:
                return {
                    "type": MemoryType.PREFERENCE,
                    "key": self._extract_preference_key(task_input),
                    "value": result
                }
        
        # 2. 检查结果类型
        if isinstance(result, dict):
            result_type = result.get("type", "")
            
            if result_type == "news_summary":
                return {
                    "type": MemoryType.KNOWLEDGE,
                    "content": f"新闻摘要：{result.get('count', 0)} 条新闻",
                    "tags": ["新闻", "摘要"],
                    "metadata": result
                }
            
            elif result_type == "task_complete":
                return {
                    "type": MemoryType.TASK_RESULT,
                    "input": task_input,
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }
        
        # 3. 默认：保存为任务结果
        return {
            "type": MemoryType.TASK_RESULT,
            "input": task_input,
            "result": result,
            "completed_at": datetime.now().isoformat()
        }
    
    def _extract_preference_key(self, text: str) -> str:
        """从文本中提取偏好键"""
        # 简单实现：使用前 10 个字符
        return text[:10].strip()
    
    def _save_preference(self, memory: Dict):
        """保存偏好"""
        self.state.add_preference(memory["key"], memory["value"])
    
    def _save_knowledge(self, memory: Dict):
        """保存知识"""
        self.state.add_knowledge(memory)
    
    def _save_task_result(self, memory: Dict):
        """保存任务结果"""
        # 彻底简化结果，避免任何循环引用
        def simplify(obj, max_depth=2):
            """递归简化对象"""
            if max_depth <= 0:
                return str(obj)[:100]
            if obj is None:
                return None
            if isinstance(obj, str):
                return obj[:200]
            if isinstance(obj, (int, float, bool)):
                return obj
            if isinstance(obj, dict):
                return {k: simplify(v, max_depth - 1) for k, v in list(obj.items())[:10]}
            if isinstance(obj, (list, tuple)):
                return [simplify(v, max_depth - 1) for v in obj[:10]]
            return str(obj)[:100]
        
        simple_result = simplify(memory["result"])
        
        # 直接操作
        self.state.state.task["history"].append({
            "input": memory["input"][:200],
            "result": simple_result,
            "completed_at": memory["completed_at"]
        })
        # 保留最近 50 条
        self.state.state.task["history"] = self.state.state.task["history"][-50:]
    
    def _save_conversation(self, memory: Dict):
        """保存对话记录"""
        # TODO: 实现对话记录保存
        pass

# ========== 工厂函数 ==========

def get_active_memory_system(user_id: str) -> ActiveMemorySystem:
    """获取主动记忆系统"""
    from scripts.trinity_state import get_state_manager
    state_manager = get_state_manager(user_id)
    return ActiveMemorySystem(state_manager)

# ========== 测试入口 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 测试主动记忆系统")
    print("=" * 60)
    
    # 创建系统
    user_id = "test_user_123"
    memory = get_active_memory_system(user_id)
    
    print("\n1️⃣ 测试任务开始 - 主动检索记忆")
    enhanced_context = memory.on_task_start("帮我写今天的工作日报，用简洁的风格")
    print(f"   增强上下文键：{list(enhanced_context.keys())}")
    if enhanced_context.get("memory_hint"):
        print(f"   记忆提示：{enhanced_context['memory_hint']}")
    
    print("\n2️⃣ 测试任务完成 - 智能记录")
    memory.on_task_complete(
        "帮我写今天的工作日报",
        {
            "type": "task_complete",
            "content": "已生成工作日报",
            "word_count": 500
        }
    )
    
    print("\n3️⃣ 测试偏好学习")
    memory.on_task_complete(
        "我喜欢简洁幽默的回复风格",
        "已记录您的偏好"
    )
    
    print("\n4️⃣ 查看已保存的记忆")
    state = memory.state.state
    print(f"   偏好数：{len(state.memory['preferences'])}")
    print(f"   知识数：{len(state.memory['knowledge'])}")
    print(f"   任务历史数：{len(state.task['history'])}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
