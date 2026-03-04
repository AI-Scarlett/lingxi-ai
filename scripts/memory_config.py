"""
灵犀记忆系统 - 配置管理
Configuration Management for Lingxi Memory System

版本：v2.7.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import aiofiles


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    
    # ===== 基础功能（v2.6.0）=====
    enabled: bool = True                    # 总开关
    auto_memorize: bool = True              # 自动记忆对话
    auto_context_load: bool = True          # 自动加载上下文
    
    # ===== Embedding 功能（v2.7.0）=====
    embedding_enabled: bool = True          # Embedding 开关
    embedding_provider: str = "local"       # local / api
    embedding_dimension: int = 1024         # 向量维度
    semantic_search: bool = True            # 语义搜索开关
    auto_categorize: bool = True            # 自动分类开关
    
    # ===== 主动学习功能（v2.7.0）=====
    proactive_learning_enabled: bool = True  # 主动学习开关
    learning_interval: int = 30             # 学习检查间隔（秒）
    pattern_detection_interval: int = 300   # 模式检测间隔（秒）
    batch_size: int = 10                    # 批量处理对话数
    
    # ===== 意图预测功能（v2.7.0）=====
    intent_prediction_enabled: bool = True  # 意图预测开关
    prediction_confidence_threshold: float = 0.6  # 置信度阈值
    context_window: int = 10                # 考虑最近 N 条记忆
    
    # ===== 主动任务功能（v2.7.0）=====
    proactive_tasks_enabled: bool = True    # 主动任务开关
    work_hours_reminder: bool = True        # 工作时间提醒（9:00）
    lunch_reminder: bool = True             # 午休提醒（12:00）
    task_followup: bool = True              # 任务跟进（每小时）
    memory_cleanup: bool = True             # 记忆整理（每周）
    
    # ===== 性能优化 =====
    keyword_search_cache_size: int = 256    # 关键词检索缓存
    embedding_cache_size: int = 512         # Embedding 缓存
    max_memories_in_context: int = 20       # 上下文中最大记忆数
    
    # ===== Token 控制 =====
    max_tokens_per_extraction: int = 500    # 单次记忆提取最大 tokens
    extraction_batch_size: int = 5          # 批量提取大小
    use_llm_for_retrieval: bool = False     # 是否使用 LLM 深度检索（耗 tokens）
    
    # ===== 存储配置 =====
    storage_path: str = "~/.openclaw/workspace/memory"
    conversation_retention_days: int = 30   # 对话保留天数
    auto_cleanup: bool = True               # 自动清理过期数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryConfig":
        """从字典创建"""
        # 过滤掉不存在的字段（兼容旧版本）
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
    
    def get_optimization_level(self) -> str:
        """获取当前优化级别"""
        if not self.proactive_learning_enabled and not self.embedding_enabled:
            return "minimal"  # 最小消耗
        elif not self.proactive_learning_enabled:
            return "balanced"  # 平衡模式
        else:
            return "full"  # 全功能


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "~/.openclaw/workspace/memory_config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config = MemoryConfig()
        self._loaded = False
    
    async def load(self) -> MemoryConfig:
        """加载配置"""
        if self._loaded:
            return self.config
        
        if self.config_path.exists():
            async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())
                self.config = MemoryConfig.from_dict(data)
        else:
            # 创建默认配置
            await self.save()
        
        self._loaded = True
        return self.config
    
    async def save(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(self.config_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.config.to_dict(), ensure_ascii=False, indent=2))
    
    async def update(self, **kwargs):
        """更新配置"""
        await self.load()
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        await self.save()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        await self.load()
        return getattr(self.config, key, default)
    
    async def set(self, key: str, value: Any):
        """设置配置项"""
        await self.update(**{key: value})
    
    async def reset(self):
        """重置为默认配置"""
        self.config = MemoryConfig()
        await self.save()
    
    async def get_token_optimization_preset(self) -> Dict[str, bool]:
        """获取 Token 优化预设"""
        return {
            # 关闭 Embedding（节省计算）
            "embedding_enabled": False,
            "semantic_search": False,
            "auto_categorize": False,
            
            # 关闭主动学习（节省大量 tokens）
            "proactive_learning_enabled": False,
            "intent_prediction_enabled": False,
            "proactive_tasks_enabled": False,
            
            # 保留基础功能
            "enabled": True,
            "auto_memorize": True,
            "auto_context_load": True,
            
            # 关闭 LLM 深度检索
            "use_llm_for_retrieval": False,
        }
    
    async def get_balanced_preset(self) -> Dict[str, bool]:
        """获取平衡模式预设（推荐）"""
        return {
            # 开启 Embedding（本地 TF-IDF，零 API 成本）
            "embedding_enabled": True,
            "semantic_search": True,
            "auto_categorize": True,
            
            # 关闭主动学习（节省 tokens）
            "proactive_learning_enabled": False,
            "intent_prediction_enabled": False,
            "proactive_tasks_enabled": False,
            
            # 保留基础功能
            "enabled": True,
            "auto_memorize": True,
            "auto_context_load": True,
            
            # 关闭 LLM 深度检索
            "use_llm_for_retrieval": False,
        }
    
    async def get_full_features_preset(self) -> Dict[str, bool]:
        """获取全功能预设（默认）"""
        return {
            # 开启所有功能
            "enabled": True,
            "embedding_enabled": True,
            "proactive_learning_enabled": True,
            "intent_prediction_enabled": True,
            "proactive_tasks_enabled": True,
            "semantic_search": True,
            "auto_categorize": True,
            "auto_memorize": True,
            "auto_context_load": True,
            "use_llm_for_retrieval": False,  # 默认关闭，太耗 tokens
        }


# 预设配置模板

PRESETS = {
    "minimal": {
        "name": "最小消耗模式",
        "description": "仅基础记忆功能，Token 消耗最低",
        "estimated_monthly_tokens": "~50K",
        "estimated_monthly_cost": "~$1.5",
        "features": [
            "✅ 基础记忆存储",
            "✅ 关键词检索",
            "✅ 自动记忆对话",
            "❌ Embedding 向量检索",
            "❌ 语义搜索",
            "❌ 主动学习",
            "❌ 意图预测",
            "❌ 主动提醒"
        ]
    },
    "balanced": {
        "name": "平衡模式（推荐）",
        "description": "开启 Embedding，关闭主动学习，性价比最优",
        "estimated_monthly_tokens": "~100K",
        "estimated_monthly_cost": "~$3",
        "features": [
            "✅ 基础记忆存储",
            "✅ 关键词检索",
            "✅ Embedding 向量检索（本地 TF-IDF）",
            "✅ 语义相似度搜索",
            "✅ 智能分类",
            "✅ 自动记忆对话",
            "❌ 24/7 主动学习",
            "❌ 意图预测",
            "❌ 主动提醒"
        ]
    },
    "full": {
        "name": "全功能模式",
        "description": "所有高级功能，最佳体验",
        "estimated_monthly_tokens": "~2.4M",
        "estimated_monthly_cost": "~$72",
        "features": [
            "✅ 基础记忆存储",
            "✅ 关键词检索",
            "✅ Embedding 向量检索",
            "✅ 语义相似度搜索",
            "✅ 智能分类",
            "✅ 24/7 主动学习",
            "✅ 意图预测",
            "✅ 主动提醒（工作时间/午休等）",
            "✅ 自动记忆整理"
        ]
    }
}


# 便捷函数

async def load_config() -> MemoryConfig:
    """加载配置"""
    manager = ConfigManager()
    return await manager.load()


async def save_config(config: MemoryConfig):
    """保存配置"""
    manager = ConfigManager()
    manager.config = config
    await manager.save()


async def apply_preset(preset_name: str):
    """应用预设配置"""
    manager = ConfigManager()
    
    if preset_name == "minimal":
        await manager.update(**manager.get_token_optimization_preset())
    elif preset_name == "balanced":
        await manager.update(**manager.get_balanced_preset())
    elif preset_name == "full":
        await manager.update(**manager.get_full_features_preset())
    else:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    await manager.save()


async def get_presets_info() -> Dict[str, Dict]:
    """获取预设信息"""
    return PRESETS
