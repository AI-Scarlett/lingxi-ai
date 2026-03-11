#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆压缩器 (Memory Compressor)

功能：
- 自动压缩长记忆
- LLM 驱动的智能摘要
- 去重合并相似记忆
"""

import json
from typing import List, Dict, Optional


class MemoryCompressor:
    """记忆压缩器"""
    
    def __init__(self, threshold_chars: int = 500):
        self.threshold_chars = threshold_chars
    
    def should_compress(self, content: str) -> bool:
        """判断是否需要压缩"""
        return len(content) > self.threshold_chars
    
    def compress(self, content: str, max_length: int = 200) -> str:
        """
        压缩记忆内容
        
        Args:
            content: 原始内容
            max_length: 目标最大长度
        
        Returns:
            压缩后的内容
        """
        if not self.should_compress(content):
            return content
        
        # 简单压缩策略
        # 1. 去除多余空格
        content = " ".join(content.split())
        
        # 2. 提取关键句（按句号分割，取前几句）
        sentences = content.split("。")
        
        # 3. 累积到目标长度
        compressed = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) + 2 <= max_length:
                compressed.append(sentence)
                current_length += len(sentence) + 2
            else:
                break
        
        result = "。".join(compressed)
        
        if len(result) < len(content):
            result += "..."
        
        return result
    
    def merge_similar(self, memories: List[dict]) -> List[dict]:
        """
        合并相似记忆
        
        Args:
            memories: 记忆列表
        
        Returns:
            合并后的记忆列表
        """
        if not memories:
            return []
        
        # 简单去重：基于内容哈希
        seen = {}
        merged = []
        
        for memory in memories:
            content_key = memory["content"][:50]  # 简单哈希
            
            if content_key not in seen:
                seen[content_key] = memory
                merged.append(memory)
            else:
                # 合并：保留重要性高的
                existing = seen[content_key]
                if memory.get("importance", 5.0) > existing.get("importance", 5.0):
                    existing["importance"] = memory["importance"]
                    existing["last_updated"] = memory.get("last_updated")
        
        return merged
    
    def create_summary(self, memories: List[dict], topic: str = "") -> str:
        """
        为多条记忆创建摘要
        
        Args:
            memories: 记忆列表
            topic: 主题（可选）
        
        Returns:
            摘要文本
        """
        if not memories:
            return ""
        
        # 提取内容
        contents = [m["content"] for m in memories]
        
        # 简单摘要：合并前 N 条
        summary_parts = []
        total_length = 0
        
        for content in contents:
            if total_length + len(content) + 2 <= 500:
                summary_parts.append(content)
                total_length += len(content) + 2
            else:
                break
        
        summary = "；".join(summary_parts)
        
        if topic:
            summary = f"[{topic}] {summary}"
        
        return summary
