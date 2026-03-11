#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆提取器 (Memory Extractor)

功能：
- 从对话中提取关键记忆
- 识别用户偏好、重要事实、项目信息
- LLM 驱动的智能提取

版本：v3.3.3
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import sys
sys.path.insert(0, '/root/.openclaw/skills/lingxi')


class MemoryExtractor:
    """记忆提取器"""
    
    def __init__(self):
        # 提取规则
        self.patterns = {
            "preference": [
                r"我喜欢 (.+?)(?:。|！|,|,|$)",
                r"我不喜欢 (.+?)(?:。|！|,|,|$)",
                r"我习惯 (.+?)(?:。|！|,|,|$)",
                r"我偏好 (.+?)(?:。|！|,|,|$)",
            ],
            "fact": [
                r"我是 (.+?)(?:。|！|,|,|$)",
                r"我在 (.+?)(?:工作 | 生活 | 居住)(.+?)(?:。|！|,|,|$)",
                r"我的 (.+?) 是 (.+?)(?:。|！|,|,|$)",
            ],
            "instruction": [
                r"记住 (.+?)(?:。|！|,|,|$)",
                r"不要忘记 (.+?)(?:。|！|,|,|$)",
                r"记得 (.+?)(?:。|！|,|,|$)",
            ]
        }
    
    def extract(self, user_content: str, assistant_content: str = "") -> List[dict]:
        """
        从对话中提取记忆
        
        Args:
            user_content: 用户消息内容
            assistant_content: 助手回复内容（可选）
        
        Returns:
            提取的记忆列表
        """
        memories = []
        
        # 1. 基于规则提取
        memories.extend(self._extract_by_rules(user_content))
        
        # 2. 检测重要性关键词
        importance = self._calculate_importance(user_content, assistant_content)
        
        # 3. 为每个记忆添加元数据
        for memory in memories:
            memory["importance"] = importance
            memory["source"] = "rule_based"
            memory["extracted_at"] = datetime.now().isoformat()
        
        return memories
    
    def _extract_by_rules(self, content: str) -> List[dict]:
        """基于规则提取记忆"""
        memories = []
        
        # 偏好提取
        for pattern in self.patterns["preference"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                memories.append({
                    "type": "preference",
                    "content": match.strip(),
                    "tags": ["偏好", "习惯"]
                })
        
        # 事实提取
        for pattern in self.patterns["fact"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    content_text = " ".join(match)
                else:
                    content_text = match
                memories.append({
                    "type": "fact",
                    "content": content_text.strip(),
                    "tags": ["事实", "身份"]
                })
        
        # 指令提取
        for pattern in self.patterns["instruction"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                memories.append({
                    "type": "instruction",
                    "content": match.strip(),
                    "tags": ["指令", "待办"]
                })
        
        return memories
    
    def _calculate_importance(self, user_content: str, assistant_content: str) -> float:
        """计算记忆重要性（1-10 分）"""
        importance = 5.0  # 基础分
        
        # 包含明确指令关键词 +2
        if any(kw in user_content for kw in ["记住", "不要忘记", "记得", "重要"]):
            importance += 2.0
        
        # 包含偏好关键词 +1
        if any(kw in user_content for kw in ["喜欢", "不喜欢", "习惯", "偏好"]):
            importance += 1.0
        
        # 包含身份/事实关键词 +1
        if any(kw in user_content for kw in ["我是", "我在", "我的"]):
            importance += 1.0
        
        # 重复提及（简单检测）+1
        words = user_content.split()
        if len(words) > 10:
            word_count = {}
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1
            if any(count > 2 for count in word_count.values()):
                importance += 1.0
        
        return min(10.0, max(1.0, importance))
    
    def extract_from_conversation(self, conversation: List[dict]) -> List[dict]:
        """
        从完整对话历史中提取记忆
        
        Args:
            conversation: 对话列表 [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            提取的记忆列表
        """
        memories = []
        
        # 遍历对话
        for i, msg in enumerate(conversation):
            if msg["role"] == "user":
                # 获取下一条助手回复（如果有）
                assistant_content = ""
                if i + 1 < len(conversation) and conversation[i + 1]["role"] == "assistant":
                    assistant_content = conversation[i + 1]["content"]
                
                # 提取记忆
                extracted = self.extract(msg["content"], assistant_content)
                memories.extend(extracted)
        
        return memories
    
    def summarize_for_memory(self, content: str, max_length: int = 200) -> str:
        """
        为记忆优化内容摘要
        
        Args:
            content: 原始内容
            max_length: 最大长度
        
        Returns:
            优化后的记忆内容
        """
        # 去除多余空格
        content = " ".join(content.split())
        
        # 截断
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return content
