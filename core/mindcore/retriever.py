#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合检索器 (Hybrid Retriever)

功能：
- BM25 关键词检索
- 向量语义检索（预留）
- 图检索（关联记忆，预留）
- LLM 重排序（预留）
"""

from typing import List, Dict, Optional
import math
from collections import defaultdict


class HybridRetriever:
    """混合检索器"""
    
    def __init__(self):
        self.bm25_k1 = 1.5  # BM25 参数
        self.bm25_b = 0.75
    
    async def retrieve(self, query: str, top_k: int = 10, sources: dict = None) -> List[dict]:
        """
        混合检索
        
        Args:
            query: 查询语句
            top_k: 返回数量
            sources: 记忆源 {"stm": [...], "mtm": [...], "ltm": [...]}
        
        Returns:
            检索结果
        """
        if not sources:
            return []
        
        # 1. 从各源检索
        all_memories = []
        
        # STM 检索
        if "stm" in sources:
            for memory in sources["stm"]:
                memory["_source"] = "stm"
                all_memories.append(memory)
        
        # MTM 检索
        if "mtm" in sources:
            for memory in sources["mtm"]:
                memory["_source"] = "mtm"
                all_memories.append(memory)
        
        # LTM 检索
        if "ltm" in sources:
            for memory in sources["ltm"]:
                memory["_source"] = "ltm"
                all_memories.append(memory)
        
        # 2. BM25 评分
        scored = self._bm25_score(query, all_memories)
        
        # 3. 排序返回
        scored.sort(reverse=True, key=lambda x: x["_score"])
        
        return scored[:top_k]
    
    def _bm25_score(self, query: str, documents: List[dict]) -> List[dict]:
        """BM25 评分"""
        query_terms = query.lower().split()
        
        # 计算文档频率
        df = defaultdict(int)
        for doc in documents:
            content = doc.get("content", "").lower()
            terms = set(content.split())
            for term in query_terms:
                if term in terms:
                    df[term] += 1
        
        # 计算每个文档的分数
        scored = []
        for doc in documents:
            content = doc.get("content", "").lower()
            doc_terms = content.split()
            doc_length = len(doc_terms)
            
            score = 0.0
            for term in query_terms:
                if term in doc_terms:
                    # 词频
                    tf = doc_terms.count(term)
                    
                    # 逆文档频率
                    n_df = df[term]
                    idf = math.log((len(documents) - n_df + 0.5) / (n_df + 0.5) + 1)
                    
                    # BM25 公式
                    numerator = tf * (self.bm25_k1 + 1)
                    denominator = tf + self.bm25_k1 * (1 - self.bm25_b + self.bm25_b * doc_length / 100)
                    
                    score += idf * (numerator / denominator)
            
            doc["_score"] = score
            scored.append(doc)
        
        return scored
    
    def _reciprocal_rank_fusion(self, results_list: List[List[dict]], k: int = 60) -> List[dict]:
        """
        RRF 融合排序（Reciprocal Rank Fusion）
        
        Args:
            results_list: 多个检索结果列表
            k: 平滑参数
        
        Returns:
            融合后的结果
        """
        fused_scores = defaultdict(float)
        doc_map = {}
        
        for results in results_list:
            for rank, doc in enumerate(results, 1):
                doc_id = doc.get("id")
                if doc_id:
                    fused_scores[doc_id] += 1.0 / (k + rank)
                    doc_map[doc_id] = doc
        
        # 排序
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        return [doc_map[doc_id] for doc_id in sorted_ids]
