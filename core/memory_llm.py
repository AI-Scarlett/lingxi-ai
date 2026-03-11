#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀记忆系统 LLM 集成

功能：
- LLM 智能摘要（长记忆自动压缩）
- 记忆关联算法（自动发现相关记忆）
- 记忆强化（定期复习重要记忆）
- 记忆提取优化（语义检索）
"""

import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sqlite3


@dataclass
class MemorySummary:
    """记忆摘要"""
    memory_id: str
    original_length: int
    summary_length: int
    compression_ratio: float
    key_points: List[str]
    created_at: float


class MemoryLLMIntegrator:
    """记忆系统 LLM 集成器"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.db_path = str(self.workspace / ".lingxi" / "memory.db")
        
        # LLM 配置
        self.llm_model = "qwen3.5-plus"
        self.max_tokens = 2000
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 记忆摘要表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_summaries (
                memory_id TEXT PRIMARY KEY,
                summary TEXT,
                key_points TEXT,
                compression_ratio REAL,
                created_at REAL
            )
        """)
        
        # 记忆关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_links (
                memory_id_1 TEXT,
                memory_id_2 TEXT,
                similarity_score REAL,
                link_type TEXT,
                created_at REAL,
                PRIMARY KEY (memory_id_1, memory_id_2)
            )
        """)
        
        # 记忆强化表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_reinforcements (
                memory_id TEXT PRIMARY KEY,
                strength REAL,
                last_reviewed_at REAL,
                next_review_at REAL,
                review_count INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def summarize_memory(self, memory_content: str, 
                               max_length: int = 200) -> MemorySummary:
        """
        LLM 智能摘要
        
        Args:
            memory_content: 原始记忆内容
            max_length: 摘要最大长度
        
        Returns:
            MemorySummary 对象
        """
        # 如果内容较短，直接返回
        if len(memory_content) <= max_length:
            return MemorySummary(
                memory_id=hashlib.md5(memory_content.encode()).hexdigest(),
                original_length=len(memory_content),
                summary_length=len(memory_content),
                compression_ratio=1.0,
                key_points=[memory_content],
                created_at=time.time()
            )
        
        # TODO: 使用 LLM 进行智能摘要
        # 当前使用简单摘要
        
        # 提取关键句
        sentences = memory_content.split("。")
        key_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) > 10:
                key_sentences.append(sentence.strip())
                if len(key_sentences) >= 5:  # 最多 5 个关键点
                    break
        
        # 生成摘要
        summary = "。".join(key_sentences[:3]) + "..."
        
        memory_id = hashlib.md5(memory_content.encode()).hexdigest()
        
        # 保存到数据库
        self._save_summary(MemorySummary(
            memory_id=memory_id,
            original_length=len(memory_content),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(memory_content),
            key_points=key_sentences,
            created_at=time.time()
        ))
        
        return MemorySummary(
            memory_id=memory_id,
            original_length=len(memory_content),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(memory_content),
            key_points=key_sentences,
            created_at=time.time()
        )
    
    def _save_summary(self, summary: MemorySummary):
        """保存摘要到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memory_summaries (
                memory_id, summary, key_points, compression_ratio, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, [
            summary.memory_id,
            summary.summary,
            json.dumps(summary.key_points),
            summary.compression_ratio,
            summary.created_at
        ])
        
        conn.commit()
        conn.close()
    
    def find_related_memories(self, memory_content: str, 
                             limit: int = 10) -> List[Tuple[str, float]]:
        """
        查找相关记忆（基于语义相似度）
        
        Args:
            memory_content: 查询内容
            limit: 返回数量限制
        
        Returns:
            [(memory_id, similarity_score), ...]
        """
        # TODO: 使用向量数据库进行语义检索
        # 当前使用简单关键词匹配
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 提取关键词
        keywords = memory_content.split()[:5]  # 前 5 个词
        
        # 搜索包含关键词的记忆
        results = []
        for keyword in keywords:
            cursor.execute("""
                SELECT id, content FROM long_term_memories
                WHERE content LIKE ?
            """, [f"%{keyword}%"])
            
            for row in cursor.fetchall():
                memory_id = row[0]
                # 简单相似度计算
                similarity = self._calculate_similarity(memory_content, row[1])
                results.append((memory_id, similarity))
        
        conn.close()
        
        # 排序并去重
        results = list(set(results))
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单版）"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def create_memory_links(self, memory_id: str, related_ids: List[str]):
        """创建记忆关联"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for related_id in related_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO memory_links (
                    memory_id_1, memory_id_2, similarity_score, link_type, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, [
                memory_id,
                related_id,
                0.8,  # 默认相似度
                "related",
                time.time()
            ])
        
        conn.commit()
        conn.close()
    
    def reinforce_memory(self, memory_id: str, strength: float = 1.0):
        """
        强化记忆（艾宾浩斯遗忘曲线）
        
        Args:
            memory_id: 记忆 ID
            strength: 强化强度 (0-1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前强化信息
        cursor.execute("SELECT * FROM memory_reinforcements WHERE memory_id = ?", [memory_id])
        row = cursor.fetchone()
        
        if row:
            # 更新现有强化
            new_strength = min(1.0, row[1] + strength * 0.1)
            new_count = row[4] + 1
            
            # 计算下次复习时间（基于强化程度）
            days_until_review = int(2 ** new_count)  # 指数增长
            next_review = time.time() + (days_until_review * 86400)
            
            cursor.execute("""
                UPDATE memory_reinforcements
                SET strength = ?, last_reviewed_at = ?, next_review_at = ?, review_count = ?
                WHERE memory_id = ?
            """, [new_strength, time.time(), next_review, new_count, memory_id])
        else:
            # 新建强化记录
            next_review = time.time() + 86400  # 1 天后复习
            
            cursor.execute("""
                INSERT INTO memory_reinforcements (
                    memory_id, strength, last_reviewed_at, next_review_at, review_count
                ) VALUES (?, ?, ?, ?, ?)
            """, [memory_id, strength, time.time(), next_review, 1])
        
        conn.commit()
        conn.close()
    
    def get_due_memories(self) -> List[str]:
        """获取需要复习的记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = time.time()
        
        cursor.execute("""
            SELECT memory_id FROM memory_reinforcements
            WHERE next_review_at < ?
            ORDER BY next_review_at ASC
        """, [now])
        
        due_memories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return due_memories
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {}
        
        # 摘要统计
        cursor.execute("SELECT COUNT(*) FROM memory_summaries")
        stats["total_summaries"] = cursor.fetchone()[0]
        
        # 关联统计
        cursor.execute("SELECT COUNT(*) FROM memory_links")
        stats["total_links"] = cursor.fetchone()[0]
        
        # 强化统计
        cursor.execute("""
            SELECT AVG(strength), AVG(review_count) FROM memory_reinforcements
        """)
        row = cursor.fetchone()
        stats["avg_strength"] = row[0] or 0
        stats["avg_reviews"] = row[1] or 0
        
        # 待复习记忆
        due_count = len(self.get_due_memories())
        stats["due_memories"] = due_count
        
        conn.close()
        
        return stats


# 全局集成器
_integrator = None

def get_memory_llm_integrator(workspace_path: str = None) -> MemoryLLMIntegrator:
    """获取记忆 LLM 集成器实例"""
    global _integrator
    
    if _integrator is None:
        from pathlib import Path
        workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        _integrator = MemoryLLMIntegrator(workspace)
    
    return _integrator


if __name__ == "__main__":
    # 测试运行
    import asyncio
    
    async def test():
        integrator = get_memory_llm_integrator()
        
        # 测试摘要
        long_content = "这是一段很长的记忆内容。" * 100
        summary = await integrator.summarize_memory(long_content)
        
        print(f"📊 摘要统计:")
        print(f"  原始长度：{summary.original_length}")
        print(f"  摘要长度：{summary.summary_length}")
        print(f"  压缩率：{summary.compression_ratio:.2f}")
        print(f"  关键点：{len(summary.key_points)} 个")
        
        # 测试关联
        related = integrator.find_related_memories("记忆内容")
        print(f"\n🔗 相关记忆：{len(related)} 个")
        
        # 测试强化
        integrator.reinforce_memory("test_memory", strength=0.5)
        due = integrator.get_due_memories()
        print(f"\n⏰ 待复习记忆：{len(due)} 个")
        
        # 统计
        stats = integrator.get_stats()
        print(f"\n📊 统计：{stats}")
    
    asyncio.run(test())
