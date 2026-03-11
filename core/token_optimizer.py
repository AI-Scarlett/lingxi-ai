#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Token 优化系统

优化策略：
1. 上下文管理 - 智能截断 + 自动摘要
2. 响应缓存 - 相同问题直接返回
3. 模型路由 - 简单任务用小模型

目标：Token 消耗 -60%
"""

import hashlib
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class CachedResponse:
    """缓存的响应"""
    question_hash: str
    response: str
    model: str
    tokens_used: int
    created_at: float
    hit_count: int = 0
    expires_at: Optional[float] = None


class ContextManager:
    """上下文管理器 - 智能压缩对话历史"""
    
    def __init__(self, max_tokens: int = 4000, compression_ratio: float = 0.3):
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self.token_estimator = TokenEstimator()
    
    def compress_context(self, messages: List[Dict], 
                         preserve_recent: int = 5) -> Tuple[List[Dict], Dict]:
        """
        压缩上下文，保留关键信息
        
        Args:
            messages: 原始消息列表
            preserve_recent: 保留最近 N 轮完整对话
            
        Returns:
            (压缩后的消息，统计信息)
        """
        stats = {
            "original_count": len(messages),
            "original_tokens": 0,
            "compressed_count": 0,
            "compressed_tokens": 0,
            "saved_tokens": 0,
            "compression_method": []
        }
        
        if not messages:
            return [], stats
        
        # 计算原始 tokens
        stats["original_tokens"] = sum(
            self.token_estimator.estimate(msg.get("content", ""))
            for msg in messages
        )
        
        # 策略 1: 保留最近 N 轮完整对话
        recent_messages = messages[-preserve_recent*2:] if len(messages) > preserve_recent*2 else messages
        
        # 策略 2: 压缩早期对话为摘要
        early_messages = messages[:-preserve_recent*2] if len(messages) > preserve_recent*2 else []
        
        compressed = []
        
        # 添加早期对话摘要
        if early_messages:
            summary = self._summarize_conversation(early_messages)
            compressed.append({
                "role": "system",
                "content": f"【对话摘要】{summary}"
            })
            stats["compression_method"].append("early_summary")
        
        # 添加最近对话（完整保留）
        compressed.extend(recent_messages)
        
        # 计算压缩后 tokens
        stats["compressed_count"] = len(compressed)
        stats["compressed_tokens"] = sum(
            self.token_estimator.estimate(msg.get("content", ""))
            for msg in compressed
        )
        stats["saved_tokens"] = stats["original_tokens"] - stats["compressed_tokens"]
        
        return compressed, stats
    
    def _summarize_conversation(self, messages: List[Dict]) -> str:
        """
        摘要早期对话（简化版）
        
        TODO: 使用 LLM 进行智能摘要
        当前使用简单提取关键信息
        """
        key_points = []
        
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "unknown")
            
            # 提取关键信息（简单规则）
            if len(content) > 100:
                # 长消息只保留前 100 字符
                key_points.append(f"{role}: {content[:100]}...")
            else:
                key_points.append(f"{role}: {content}")
        
        # 合并摘要
        summary = " | ".join(key_points[-5:])  # 最多保留 5 条
        
        return summary
    
    def truncate_to_tokens(self, messages: List[Dict], 
                           max_tokens: int = None) -> List[Dict]:
        """
        截断消息列表到指定 token 数
        
        从最早的消息开始删除，保留最近的对话
        """
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        if not messages:
            return []
        
        # 从后向前累加 tokens，直到达到限制
        total_tokens = 0
        truncated = []
        
        for msg in reversed(messages):
            msg_tokens = self.token_estimator.estimate(msg.get("content", ""))
            
            if total_tokens + msg_tokens <= max_tokens:
                truncated.insert(0, msg)
                total_tokens += msg_tokens
            else:
                # 部分截断这条消息
                remaining = max_tokens - total_tokens
                if remaining > 0:
                    partial_content = msg.get("content", "")[:remaining*4]  # 粗略估计
                    truncated.insert(0, {
                        **msg,
                        "content": partial_content + "..."
                    })
                break
        
        return truncated


class ResponseCache:
    """LLM 响应缓存 - 避免重复消耗 tokens"""
    
    def __init__(self, db_path: str, ttl_seconds: int = 3600):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self._init_db()
        
        # 内存缓存（热数据）
        self.memory_cache: Dict[str, CachedResponse] = {}
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (
                question_hash TEXT PRIMARY KEY,
                response TEXT,
                model TEXT,
                tokens_used INTEGER,
                created_at REAL,
                hit_count INTEGER DEFAULT 0,
                expires_at REAL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expires ON response_cache(expires_at)")
        
        conn.commit()
        conn.close()
    
    def _hash_question(self, question: str) -> str:
        """生成问题哈希"""
        return hashlib.md5(question.strip().encode()).hexdigest()
    
    def get(self, question: str) -> Optional[CachedResponse]:
        """获取缓存的响应"""
        question_hash = self._hash_question(question)
        
        # 先查内存缓存
        if question_hash in self.memory_cache:
            cached = self.memory_cache[question_hash]
            
            # 检查是否过期
            if cached.expires_at and time.time() > cached.expires_at:
                del self.memory_cache[question_hash]
            else:
                cached.hit_count += 1
                return cached
        
        # 查数据库
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM response_cache 
            WHERE question_hash = ? AND (expires_at IS NULL OR expires_at > ?)
        """, [question_hash, time.time()])
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            cached = CachedResponse(**dict(row))
            self.memory_cache[question_hash] = cached
            return cached
        
        return None
    
    def set(self, question: str, response: str, model: str, 
            tokens_used: int, ttl: int = None):
        """缓存响应"""
        if ttl is None:
            ttl = self.ttl_seconds
        
        question_hash = self._hash_question(question)
        expires_at = time.time() + ttl if ttl > 0 else None
        
        cached = CachedResponse(
            question_hash=question_hash,
            response=response,
            model=model,
            tokens_used=tokens_used,
            created_at=time.time(),
            hit_count=0,
            expires_at=expires_at
        )
        
        # 写入数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO response_cache (
                question_hash, response, model, tokens_used, 
                created_at, hit_count, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            question_hash,
            response,
            model,
            tokens_used,
            cached.created_at,
            0,
            expires_at
        ])
        
        conn.commit()
        conn.close()
        
        # 更新内存缓存
        self.memory_cache[question_hash] = cached
    
    def clear_expired(self) -> int:
        """清理过期缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = time.time()
        cursor.execute("DELETE FROM response_cache WHERE expires_at < ?", [now])
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # 清理内存缓存
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v.expires_at and time.time() > v.expires_at
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        return deleted
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总缓存数
        cursor.execute("SELECT COUNT(*) FROM response_cache")
        total = cursor.fetchone()[0]
        
        # 命中率
        cursor.execute("SELECT SUM(hit_count) FROM response_cache")
        total_hits = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_cached": total,
            "memory_cached": len(self.memory_cache),
            "total_hits": total_hits,
            "hit_rate": total_hits / (total + total_hits) if total > 0 else 0
        }


class ModelRouter:
    """智能模型路由 - 根据任务复杂度选择模型"""
    
    def __init__(self):
        # 模型配置
        self.models = {
            "small": {
                "name": "qwen3.5-plus",
                "max_tokens": 2000,
                "cost_per_1k": 0.002,
                "speed": "fast"
            },
            "medium": {
                "name": "qwen3-max",
                "max_tokens": 8000,
                "cost_per_1k": 0.004,
                "speed": "medium"
            },
            "large": {
                "name": "glm-5",
                "max_tokens": 32000,
                "cost_per_1k": 0.008,
                "speed": "slow"
            }
        }
        
        # 默认模型
        self.default_model = "medium"
    
    def route(self, task: Dict) -> str:
        """
        根据任务选择模型
        
        规则：
        - 简单任务（<500 tokens）：small
        - 中等任务（500-2000 tokens）：medium
        - 复杂任务（>2000 tokens）：large
        """
        content = task.get("payload", {}).get("user_input", "")
        content_length = len(content)
        
        # 估算 tokens（中文约 1.5 字符/token）
        estimated_tokens = content_length // 1.5
        
        # 任务类型判断
        task_type = task.get("type", "realtime")
        
        # 规则 1: 定时任务用 medium
        if task_type == "scheduled":
            return self.models["medium"]["name"]
        
        # 规则 2: 根据内容长度
        if estimated_tokens < 500:
            return self.models["small"]["name"]
        elif estimated_tokens < 2000:
            return self.models["medium"]["name"]
        else:
            return self.models["large"]["name"]
    
    def get_model_info(self, model_name: str) -> Dict:
        """获取模型信息"""
        for tier, config in self.models.items():
            if config["name"] == model_name:
                return {**config, "tier": tier}
        
        return {"name": model_name, "tier": "unknown"}


class TokenEstimator:
    """Token 估算器"""
    
    def __init__(self):
        # 简单估算：中文 1.5 字符/token，英文 4 字符/token
        self.chinese_ratio = 1.5
        self.english_ratio = 4
    
    def estimate(self, text: str) -> int:
        """估算 token 数"""
        if not text:
            return 0
        
        # 检测中英文比例
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len(text)
        english_chars = total_chars - chinese_chars
        
        # 估算 tokens
        tokens = (chinese_chars / self.chinese_ratio) + (english_chars / self.english_ratio)
        
        return int(tokens)


class TokenOptimizer:
    """统一的 Token 优化器"""
    
    def __init__(self, workspace_path: str):
        workspace = Path(workspace_path)
        db_path = str(workspace / ".lingxi" / "token_cache.db")
        
        self.context_manager = ContextManager()
        self.response_cache = ResponseCache(db_path)
        self.model_router = ModelRouter()
        self.token_estimator = TokenEstimator()
        
        # Scrapling 内容获取器（集成到 Token 优化）
        try:
            from .content_fetcher import get_content_fetcher
            self.content_fetcher = get_content_fetcher(str(workspace))
        except ImportError:
            self.content_fetcher = None
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "content_cache_hits": 0,
            "tokens_saved": 0,
            "original_tokens": 0,
            "optimized_tokens": 0
        }
    
    def optimize_request(self, task: Dict, messages: List[Dict]) -> Dict:
        """
        优化 LLM 请求
        
        Returns:
            优化后的请求配置
        """
        self.stats["total_requests"] += 1
        
        # 步骤 1: 检查缓存
        question = task.get("payload", {}).get("user_input", "")
        cached = self.response_cache.get(question)
        
        if cached:
            self.stats["cache_hits"] += 1
            return {
                "use_cache": True,
                "response": cached.response,
                "tokens_saved": cached.tokens_used,
                "model": cached.model
            }
        
        # 步骤 2: 压缩上下文
        compressed_messages, compress_stats = self.context_manager.compress_context(messages)
        
        # 步骤 3: 选择模型
        model = self.model_router.route(task)
        
        # 更新统计
        self.stats["original_tokens"] += compress_stats["original_tokens"]
        self.stats["optimized_tokens"] += compress_stats["compressed_tokens"]
        self.stats["tokens_saved"] += compress_stats["saved_tokens"]
        
        return {
            "use_cache": False,
            "messages": compressed_messages,
            "model": model,
            "estimated_tokens": compress_stats["compressed_tokens"],
            "compression_stats": compress_stats
        }
    
    def cache_response(self, question: str, response: str, 
                      model: str, tokens_used: int):
        """缓存 LLM 响应"""
        self.response_cache.set(question, response, model, tokens_used)
    
    def get_stats(self) -> Dict:
        """获取优化统计"""
        cache_stats = self.response_cache.get_stats()
        
        return {
            **self.stats,
            **cache_stats,
            "save_rate": self.stats["tokens_saved"] / self.stats["original_tokens"] 
                        if self.stats["original_tokens"] > 0 else 0
        }


# 全局优化器
_optimizer = None

def get_token_optimizer(workspace_path: str) -> TokenOptimizer:
    """获取 Token 优化器实例"""
    global _optimizer
    
    if _optimizer is None:
        _optimizer = TokenOptimizer(workspace_path)
    
    return _optimizer
