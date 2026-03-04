"""
灵犀记忆系统 - 参考 memU 框架设计
Memory Service for Lingxi - Inspired by memU

作者：斯嘉丽 Scarlett
日期：2026-03-04
参考：https://github.com/NevaMind-AI/memU
"""

import asyncio
import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import aiofiles


@dataclass
class MemoryItem:
    """单个记忆项 - 对应 memU 的 Item 层"""
    
    id: str
    category: str           # 所属分类：preferences/relationships/knowledge/context
    topic: str              # 主题标签
    content: str            # 记忆内容
    source: str             # 来源（对话 ID/任务 ID/文件路径）
    timestamp: float        # 创建时间戳
    confidence: float = 0.9  # 置信度（0-1）
    related_ids: List[str] = field(default_factory=list)  # 关联记忆 ID（交叉引用）
    user_id: str = "default"
    embeddings: Optional[List[float]] = None  # 向量嵌入（用于相似度检索）
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryItem":
        return cls(**data)
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式（便于人工阅读）"""
        return f"""---
id: {self.id}
category: {self.category}
topic: {self.topic}
confidence: {self.confidence}
timestamp: {datetime.fromtimestamp(self.timestamp).isoformat()}
related: {', '.join(self.related_ids) if self.related_ids else 'none'}
---

## {self.topic}

{self.content}

**来源：** {self.source}
"""


class MemoryStructure:
    """
    文件系统式记忆结构 - 参考 memU 设计
    
    memory/
    ├── preferences/          # 用户偏好
    │   ├── communication_style.md
    │   ├── topic_interests.md
    │   └── working_hours.md
    ├── relationships/        # 关系网络
    │   ├── contacts.json
    │   └── history/          # 按日期分文件
    ├── knowledge/            # 知识库
    │   ├── domains/
    │   └── skills/
    ├── context/              # 上下文
    │   ├── conversations/
    │   └── tasks.json
    └── items/                # 原始记忆项（JSONL 格式）
        └── memories.jsonl
    """
    
    def __init__(self, base_path: str = "~/.openclaw/workspace/memory"):
        self.base = Path(base_path).expanduser()
        
        # 定义目录结构
        self.dirs = {
            "preferences": self.base / "preferences",
            "relationships": self.base / "relationships",
            "knowledge": self.base / "knowledge",
            "context": self.base / "context",
            "items": self.base / "items",
            "history": self.base / "relationships" / "history",
            "domains": self.base / "knowledge" / "domains",
            "skills": self.base / "knowledge" / "skills",
            "conversations": self.base / "context" / "conversations",
        }
        
        # 预定义文件
        self.files = {
            "contacts": self.base / "relationships" / "contacts.json",
            "tasks": self.base / "context" / "tasks.json",
            "memories": self.base / "items" / "memories.jsonl",
        }
    
    async def ensure_structure(self):
        """确保目录结构存在"""
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化 JSON 文件
        for file_path in self.files.values():
            if not file_path.exists():
                if file_path.suffix == ".json":
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps({}, ensure_ascii=False, indent=2))
                elif file_path.suffix == ".jsonl":
                    # JSONL 文件不需要初始化
                    pass
    
    async def save_memory_item(self, item: MemoryItem):
        """保存单个记忆项到 JSONL 文件"""
        await self.ensure_structure()
        
        async with aiofiles.open(self.files["memories"], 'a', encoding='utf-8') as f:
            await f.write(json.dumps(item.to_dict(), ensure_ascii=False) + '\n')
    
    async def load_all_items(self) -> List[MemoryItem]:
        """加载所有记忆项"""
        items = []
        
        if not self.files["memories"].exists():
            return items
        
        async with aiofiles.open(self.files["memories"], 'r', encoding='utf-8') as f:
            async for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        items.append(MemoryItem.from_dict(data))
                    except json.JSONDecodeError:
                        continue
        
        return items
    
    async def save_category_file(self, category: str, filename: str, data: Any):
        """保存分类文件"""
        file_path = self.dirs.get(category, self.base / category) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                await f.write(data)
            else:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    async def load_category_file(self, category: str, filename: str) -> Optional[Any]:
        """加载分类文件"""
        file_path = self.dirs.get(category, self.base / category) / filename
        
        if not file_path.exists():
            return None
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
    
    async def save_conversation(self, conv_id: str, conversation: List[Dict]):
        """保存对话记录（Resource 层）"""
        file_path = self.dirs["conversations"] / f"{conv_id}.json"
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps({
                "id": conv_id,
                "timestamp": time.time(),
                "messages": conversation
            }, ensure_ascii=False, indent=2))
    
    async def load_conversation(self, conv_id: str) -> Optional[Dict]:
        """加载对话记录"""
        file_path = self.dirs["conversations"] / f"{conv_id}.json"
        
        if not file_path.exists():
            return None
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return json.loads(await f.read())


class MemoryExtractor:
    """
    自动记忆提取器 - 参考 memU 的实时提取机制
    
    从对话和任务中自动提取：
    - 用户偏好（沟通风格、工作时间、兴趣话题）
    - 事实信息（姓名、职业、关系）
    - 任务意图（目标、截止日期、优先级）
    - 知识技能（专业领域、已掌握技能）
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.extraction_prompt = """
从以下对话中提取用户记忆信息：

对话内容：
{conversation}

请提取以下类型的记忆（JSON 格式）：
{{
    "items": [
        {{
            "category": "preferences|relationships|knowledge|context",
            "topic": "简短主题标签",
            "content": "具体记忆内容",
            "confidence": 0.8,
            "metadata": {{"key": "value"}}
        }}
    ]
}}

分类说明：
- preferences: 用户偏好（沟通风格、工作时间、兴趣爱好等）
- relationships: 人际关系（联系人、交互历史等）
- knowledge: 知识技能（专业领域、已掌握技能等）
- context: 上下文信息（当前任务、待办事项等）

要求：
1. 只提取明确提到的信息
2. confidence 根据信息明确程度打分（0.5-1.0）
3. 如果没有可提取的记忆，返回空列表
"""
    
    async def extract_from_conversation(self, conversation: List[Dict], conv_id: str) -> List[MemoryItem]:
        """从对话中提取记忆"""
        
        if not self.llm:
            return []
        
        # 格式化对话
        conv_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in conversation
        ])
        
        # 调用 LLM 提取
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": self.extraction_prompt.format(
                    conversation=conv_text
                )}],
                temperature=0.3
            )
            
            # 解析结果
            result = json.loads(response)
            items = []
            
            for item_data in result.get("items", []):
                item = MemoryItem(
                    id=self._generate_id(),
                    source=conv_id,
                    timestamp=time.time(),
                    user_id="default",
                    **item_data
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"记忆提取失败：{e}")
            return []
    
    async def extract_from_task(self, task_input: str, task_result: str, task_id: str) -> List[MemoryItem]:
        """从任务执行结果中提取记忆"""
        
        if not self.llm:
            return []
        
        prompt = f"""
从以下任务执行中提取记忆：

任务输入：{task_input}
任务结果：{task_result}

提取用户技能、偏好或知识相关的记忆（JSON 格式）：
{{
    "items": [
        {{
            "category": "knowledge|preferences|context",
            "topic": "主题",
            "content": "内容",
            "confidence": 0.8
        }}
    ]
}}
"""
        
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response)
            items = []
            
            for item_data in result.get("items", []):
                item = MemoryItem(
                    id=self._generate_id(),
                    source=task_id,
                    timestamp=time.time(),
                    user_id="default",
                    **item_data
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            print(f"任务记忆提取失败：{e}")
            return []
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        return hashlib.md5(f"{time.time()}-{id(self)}".encode()).hexdigest()[:12]


class MemoryOrganizer:
    """
    记忆组织器 - 参考 memU 的自动分类和交叉引用
    
    功能：
    - 自动分类记忆项
    - 查找相关记忆（交叉引用）
    - 检测记忆中的模式
    """
    
    def __init__(self, memory_store: MemoryStructure):
        self.store = memory_store
        self.category_keywords = {
            "preferences": ["喜欢", "偏好", "习惯", "通常", "经常", "想要", "希望"],
            "relationships": ["认识", "朋友", "同事", "老板", "家人", "联系", "人"],
            "knowledge": ["知道", "了解", "学习", "技能", "专业", "领域", "经验"],
            "context": ["现在", "当前", "待办", "计划", "安排", "任务", "项目"],
        }
    
    def auto_categorize(self, content: str) -> str:
        """基于关键词自动分类（简单规则版）"""
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in content.lower())
            scores[category] = score
        
        return max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else "context"
    
    async def find_related(self, item: MemoryItem, top_k: int = 5) -> List[str]:
        """查找相关记忆（基于主题和关键词 overlap）"""
        
        all_items = await self.store.load_all_items()
        
        # 过滤掉自己
        all_items = [i for i in all_items if i.id != item.id]
        
        # 计算相似度（简单版本：主题匹配 + 关键词 overlap）
        scored = []
        item_words = set(item.content.lower().split())
        
        for other in all_items:
            # 主题匹配
            if other.topic == item.topic:
                score = 0.8
            else:
                score = 0.3
            
            # 同类别加分
            if other.category == item.category:
                score += 0.1
            
            # 关键词 overlap
            other_words = set(other.content.lower().split())
            overlap = len(item_words & other_words) / max(len(item_words | other_words), 1)
            score += overlap * 0.1
            
            scored.append((other.id, score))
        
        # 排序取 top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        return [id for id, score in scored[:top_k] if score > 0.3]
    
    async def detect_patterns(self) -> List[Dict]:
        """检测记忆中的模式"""
        
        items = await self.store.load_all_items()
        patterns = []
        
        # 统计各类别数量
        category_counts = {}
        for item in items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # 检测偏好模式
        if category_counts.get("preferences", 0) > 5:
            patterns.append({
                "type": "rich_preferences",
                "description": f"已积累{category_counts['preferences']}条用户偏好记忆",
                "confidence": 0.9
            })
        
        # 检测时间模式（简化版）
        timestamps = [item.timestamp for item in items]
        if timestamps:
            hours = [datetime.fromtimestamp(ts).hour for ts in timestamps]
            most_active_hour = max(set(hours), key=hours.count)
            patterns.append({
                "type": "active_hours",
                "description": f"用户活跃时间集中在{most_active_hour}:00左右",
                "confidence": 0.7
            })
        
        return patterns


class MemoryRetriever:
    """
    记忆检索器 - 参考 memU 的双模式检索
    
    支持：
    - RAG 模式：快速 embedding 相似度检索
    - LLM 模式：深度推理式检索
    """
    
    def __init__(self, memory_store: MemoryStructure, llm_client=None):
        self.store = memory_store
        self.llm = llm_client
    
    async def retrieve(self, query: str, method: str = "keyword", 
                       category: Optional[str] = None, top_k: int = 10) -> Dict:
        """
        检索记忆
        
        Args:
            query: 查询语句
            method: 检索方法（keyword/rag/llm）
            category: 限定类别
            top_k: 返回数量
        
        Returns:
            检索结果
        """
        
        if method == "keyword":
            return await self._keyword_retrieve(query, category, top_k)
        elif method == "llm":
            return await self._llm_retrieve(query, category, top_k)
        else:
            return await self._keyword_retrieve(query, category, top_k)
    
    async def _keyword_retrieve(self, query: str, category: Optional[str], top_k: int) -> Dict:
        """关键词检索（快速版）"""
        
        items = await self.store.load_all_items()
        
        # 过滤类别
        if category:
            items = [i for i in items if i.category == category]
        
        # 关键词匹配打分
        query_words = set(query.lower().split())
        scored = []
        
        for item in items:
            item_words = set(item.content.lower().split())
            
            # 主题匹配
            if query.lower() in item.topic.lower():
                score = 0.9
            else:
                score = 0.3
            
            # 关键词 overlap
            overlap = len(query_words & item_words) / max(len(query_words | item_words), 1)
            score += overlap * 0.5
            
            scored.append((item, score))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        results = [(item.to_dict(), score) for item, score in scored[:top_k] if score > 0.2]
        
        return {
            "method": "keyword",
            "items": [r[0] for r in results],
            "scores": [r[1] for r in results],
            "total": len(results)
        }
    
    async def _llm_retrieve(self, query: str, category: Optional[str], top_k: int) -> Dict:
        """LLM 深度检索"""
        
        # 先用关键词检索获取候选
        candidates = await self._keyword_retrieve(query, category, top_k=20)
        
        if not self.llm or not candidates["items"]:
            return candidates
        
        # 让 LLM 筛选和推理
        prompt = f"""
基于以下记忆候选，回答用户查询：

用户查询：{query}

候选记忆：
{json.dumps(candidates["items"], ensure_ascii=False, indent=2)}

请：
1. 筛选最相关的记忆（最多{top_k}条）
2. 推理隐含信息
3. 预测用户可能的后续问题

输出 JSON：
{{
    "relevant_items": [...],  // 相关记忆 ID 列表
    "inferences": ["推理 1", "推理 2"],
    "next_step_query": "预测的后续查询"
}}
"""
        
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response)
            
            # 获取完整记忆
            relevant_items = []
            for item_id in result.get("relevant_items", []):
                for item in candidates["items"]:
                    if item.get("id") == item_id:
                        relevant_items.append(item)
                        break
            
            return {
                "method": "llm",
                "items": relevant_items,
                "inferences": result.get("inferences", []),
                "next_step_query": result.get("next_step_query", "")
            }
            
        except Exception as e:
            print(f"LLM 检索失败：{e}")
            return candidates
    
    async def proactive_context(self, user_id: str = "default") -> Dict:
        """主动上下文加载（后台运行）"""
        
        items = await self.store.load_all_items()
        
        # 获取最近记忆
        recent = sorted(items, key=lambda x: x.timestamp, reverse=True)[:10]
        
        # 检测模式
        organizer = MemoryOrganizer(self.store)
        patterns = await organizer.detect_patterns()
        
        return {
            "recent_context": [r.to_dict() for r in recent],
            "predicted_needs": patterns,
            "total_memories": len(items)
        }


class MemoryService:
    """
    记忆服务 - 统一接口
    
    整合所有组件，提供简洁 API
    """
    
    def __init__(self, llm_client=None):
        self.store = MemoryStructure()
        self.extractor = MemoryExtractor(llm_client)
        self.organizer = MemoryOrganizer(self.store)
        self.retriever = MemoryRetriever(self.store, llm_client)
        self.llm = llm_client
        self._initialized = False
    
    async def initialize(self):
        """初始化记忆系统"""
        if not self._initialized:
            await self.store.ensure_structure()
            self._initialized = True
    
    async def memorize(self, conversation: List[Dict], conv_id: str) -> Dict:
        """
        记忆对话（自动提取 + 存储）
        
        Args:
            conversation: 对话历史
            conv_id: 对话 ID
        
        Returns:
            提取的记忆项
        """
        await self.initialize()
        
        # 保存原始对话（Resource 层）
        await self.store.save_conversation(conv_id, conversation)
        
        # 提取记忆（Item 层）
        items = await self.extractor.extract_from_conversation(conversation, conv_id)
        
        # 自动分类和关联
        for item in items:
            if not item.category:
                item.category = self.organizer.auto_categorize(item.content)
            item.related_ids = await self.organizer.find_related(item)
            await self.store.save_memory_item(item)
        
        return {
            "conv_id": conv_id,
            "extracted_items": len(items),
            "items": [i.to_dict() for i in items]
        }
    
    async def retrieve(self, query: str, method: str = "keyword", **kwargs) -> Dict:
        """检索记忆"""
        await self.initialize()
        return await self.retriever.retrieve(query, method, **kwargs)
    
    async def get_context(self, user_id: str = "default") -> Dict:
        """获取主动上下文"""
        await self.initialize()
        return await self.retriever.proactive_context(user_id)
    
    async def get_stats(self) -> Dict:
        """获取记忆统计"""
        await self.initialize()
        
        items = await self.store.load_all_items()
        
        # 按类别统计
        category_counts = {}
        for item in items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        return {
            "total_items": len(items),
            "by_category": category_counts,
            "recent_items": len([i for i in items if time.time() - i.timestamp < 86400])
        }


# 便捷函数
async def memorize(conversation: List[Dict], conv_id: str, llm_client=None) -> Dict:
    """便捷函数：记忆对话"""
    service = MemoryService(llm_client)
    return await service.memorize(conversation, conv_id)


async def retrieve(query: str, method: str = "keyword", llm_client=None) -> Dict:
    """便捷函数：检索记忆"""
    service = MemoryService(llm_client)
    return await service.retrieve(query, method)


async def get_context(llm_client=None) -> Dict:
    """便捷函数：获取上下文"""
    service = MemoryService(llm_client)
    return await service.get_context()
