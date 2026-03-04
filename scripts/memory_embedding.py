"""
灵犀记忆系统 - Embedding 向量检索模块
Embedding-based Vector Retrieval for Lingxi Memory

版本：v2.7.0
参考：memU 框架的 RAG 检索机制
"""

import asyncio
import json
import math
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class EmbeddingConfig:
    """Embedding 配置"""
    provider: str = "local"  # local / api
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    api_url: Optional[str] = None
    api_key: Optional[str] = None


class EmbeddingService:
    """
    Embedding 服务
    
    支持：
    - 本地 TF-IDF embedding（无需 API）
    - API embedding（OpenAI 兼容接口）
    """
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self._tfidf_vectors = {}
        self._vocabulary = set()
        self._idf_scores = {}
        self._document_count = 0
    
    async def embed(self, text: str) -> List[float]:
        """
        生成 embedding 向量
        
        Args:
            text: 输入文本
        
        Returns:
            embedding 向量（List[float]）
        """
        if self.config.provider == "api" and self.config.api_url:
            return await self._api_embed(text)
        else:
            return await self._local_embed(text)
    
    async def _local_embed(self, text: str) -> List[float]:
        """
        本地 TF-IDF embedding（无需 API）
        
        使用简化的 TF-IDF 算法生成稀疏向量
        """
        # 分词（简单按空格和标点分割）
        words = self._tokenize(text)
        
        # 更新词汇表
        for word in words:
            self._vocabulary.add(word)
        
        # 计算 TF（词频）
        tf = {}
        for word in words:
            tf[word] = tf.get(word, 0) + 1
        
        # 归一化 TF
        max_freq = max(tf.values()) if tf else 1
        tf = {k: v / max_freq for k, v in tf.items()}
        
        # 更新 IDF
        self._document_count += 1
        for word in set(words):
            self._idf_scores[word] = self._idf_scores.get(word, 0) + 1
        
        # 生成向量（固定维度 1024，使用 hash 映射）
        vector = [0.0] * 1024
        
        for word, tf_score in tf.items():
            # 使用 hash 将词映射到向量索引
            idx = hash(word) % 1024
            
            # IDF 计算
            idf = math.log(
                (1 + self._document_count) / 
                (1 + self._idf_scores.get(word, 0))
            ) + 1
            
            # TF-IDF 分数
            tfidf = tf_score * idf
            
            # 累加到向量（处理冲突）
            vector[idx] += tfidf
        
        # L2 归一化
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    async def _api_embed(self, text: str) -> List[float]:
        """调用 API 生成 embedding（OpenAI 兼容接口）"""
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model,
                "input": text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    return result["data"][0]["embedding"]
        
        except Exception as e:
            print(f"API Embedding 失败：{e}，回退到本地 embedding")
            return await self._local_embed(text)
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 移除标点，转小写
        text = text.lower()
        for char in ".,!?;:，。！？；：\"'()[]{}":
            text = text.replace(char, " ")
        
        # 分割
        words = text.split()
        
        # 过滤短词
        return [w for w in words if len(w) > 1]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成 embedding"""
        return await asyncio.gather(*[self.embed(text) for text in texts])


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算余弦相似度
    
    Args:
        vec1: 向量 1
        vec2: 向量 2
    
    Returns:
        余弦相似度（-1 到 1）
    """
    if len(vec1) != len(vec2):
        return 0.0
    
    # 点积
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # 模长
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


class VectorIndex:
    """
    向量索引
    
    支持高效的相似度搜索
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embeddings = embedding_service
        self._vectors = {}  # id -> vector
        self._metadata = {}  # id -> metadata
    
    async def add(self, item_id: str, text: str, metadata: Dict = None):
        """
        添加向量到索引
        
        Args:
            item_id: 唯一 ID
            text: 文本内容
            metadata: 元数据
        """
        vector = await self.embeddings.embed(text)
        self._vectors[item_id] = vector
        self._metadata[item_id] = metadata or {}
    
    async def add_batch(self, items: List[Dict]):
        """
        批量添加
        
        Args:
            items: [{"id": str, "text": str, "metadata": dict}]
        """
        texts = [item["text"] for item in items]
        vectors = await self.embeddings.embed_batch(texts)
        
        for i, item in enumerate(items):
            self._vectors[item["id"]] = vectors[i]
            self._metadata[item["id"]] = item.get("metadata", {})
    
    async def search(
        self, 
        query: str, 
        top_k: int = 10,
        threshold: float = 0.3
    ) -> List[Tuple[str, float, Dict]]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            threshold: 相似度阈值
        
        Returns:
            [(id, score, metadata), ...]
        """
        query_vector = await self.embeddings.embed(query)
        
        # 计算所有相似度
        scored = []
        for item_id, vector in self._vectors.items():
            score = cosine_similarity(query_vector, vector)
            if score >= threshold:
                scored.append((item_id, score, self._metadata.get(item_id, {})))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[:top_k]
    
    def remove(self, item_id: str):
        """移除向量"""
        self._vectors.pop(item_id, None)
        self._metadata.pop(item_id, None)
    
    def clear(self):
        """清空索引"""
        self._vectors.clear()
        self._metadata.clear()
    
    @property
    def size(self) -> int:
        """索引大小"""
        return len(self._vectors)


class SmartCategorizer:
    """
    智能分类器
    
    使用 embedding 聚类自动分类记忆
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embeddings = embedding_service
        self._category_centers = {}  # category -> center_vector
        self._category_samples = {}  # category -> [vectors]
    
    async def add_sample(self, category: str, text: str):
        """添加样本到类别"""
        vector = await self.embeddings.embed(text)
        
        if category not in self._category_centers:
            self._category_centers[category] = vector
            self._category_samples[category] = [vector]
        else:
            # 更新类别中心（移动平均）
            old_center = self._category_centers[category]
            samples = self._category_samples[category]
            
            # 简单平均
            new_center = [
                sum(v[i] for v in samples + [vector]) / (len(samples) + 1)
                for i in range(len(vector))
            ]
            
            self._category_centers[category] = new_center
            self._category_samples[category].append(vector)
    
    async def categorize(self, text: str) -> Tuple[str, float]:
        """
        自动分类
        
        Args:
            text: 输入文本
        
        Returns:
            (category, confidence)
        """
        vector = await self.embeddings.embed(text)
        
        best_category = None
        best_score = -1
        
        for category, center in self._category_centers.items():
            score = cosine_similarity(vector, center)
            if score > best_score:
                best_score = score
                best_category = category
        
        if best_category is None:
            return "context", 0.5  # 默认类别
        
        return best_category, best_score
    
    async def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self._category_centers.keys())


class SemanticMemoryEnhancer:
    """
    语义记忆增强器
    
    整合 embedding 检索和智能分类
    """
    
    def __init__(self, embedding_config: EmbeddingConfig = None):
        self.embeddings = EmbeddingService(embedding_config)
        self.index = VectorIndex(self.embeddings)
        self.categorizer = SmartCategorizer(self.embeddings)
    
    async def add_memory(self, item_id: str, content: str, category: str, metadata: Dict = None):
        """
        添加记忆（带 embedding）
        
        Args:
            item_id: 记忆 ID
            content: 记忆内容
            category: 类别
            metadata: 元数据
        """
        # 添加到向量索引
        await self.index.add(item_id, content, {
            "category": category,
            **(metadata or {})
        })
        
        # 添加到分类器
        await self.categorizer.add_sample(category, content)
    
    async def search_similar(
        self, 
        query: str, 
        category: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        语义相似度搜索
        
        Args:
            query: 查询文本
            category: 限定类别
            top_k: 返回数量
        
        Returns:
            相关记忆列表
        """
        results = await self.index.search(query, top_k=top_k * 2)
        
        # 过滤类别
        if category:
            results = [r for r in results if r[2].get("category") == category]
        
        # 格式化结果
        return [
            {
                "id": item_id,
                "score": score,
                "metadata": metadata
            }
            for item_id, score, metadata in results[:top_k]
        ]
    
    async def auto_categorize(self, content: str) -> Dict:
        """
        自动分类
        
        Args:
            content: 记忆内容
        
        Returns:
            {category: str, confidence: float, alternatives: List[str]}
        """
        category, confidence = await self.categorizer.categorize(content)
        
        # 获取所有类别作为备选
        all_categories = await self.categorizer.get_categories()
        
        return {
            "category": category,
            "confidence": confidence,
            "alternatives": all_categories
        }
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        categories = await self.categorizer.get_categories()
        
        return {
            "total_memories": self.index.size,
            "categories": categories,
            "category_count": len(categories)
        }


# 便捷函数
async def create_enhancer() -> SemanticMemoryEnhancer:
    """创建语义记忆增强器"""
    return SemanticMemoryEnhancer()


async def embed_text(text: str) -> List[float]:
    """便捷函数：生成 embedding"""
    embeddings = EmbeddingService()
    return await embeddings.embed(text)


def similarity(text1: str, text2: str) -> float:
    """便捷函数：计算语义相似度"""
    async def _calc():
        embeddings = EmbeddingService()
        v1 = await embeddings.embed(text1)
        v2 = await embeddings.embed(text2)
        return cosine_similarity(v1, v2)
    
    return asyncio.run(_calc())
