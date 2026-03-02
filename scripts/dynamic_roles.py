#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态角色系统 - Dynamic Role System
让每个用户自定义自己的 AI 专家团队 💋

核心特性：
1. JSON/YAML 配置角色
2. 智能模型推荐
3. 插件化技能框架
4. 场景模板库
5. 成本优化策略
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

class ModelCapability(Enum):
    """模型能力类型"""
    TEXT = "text"           # 纯文本
    CODING = "coding"       # 代码生成
    IMAGE = "image"         # 图像生成
    VISION = "vision"       # 视觉理解
    AUDIO = "audio"         # 语音处理
    MULTIMODAL = "multimodal"  # 多模态

@dataclass
class ModelConfig:
    """大模型配置"""
    name: str              # 模型名称 (如 qwen-max, glm-edge)
    provider: str          # 提供商 (dashscope, zhipu, openai)
    capability: ModelCapability
    cost_per_1k: float     # 每 1K token 成本 (元)
    max_tokens: int        # 最大输出长度
    latency_ms: int        # 平均延迟 (ms)
    quality_score: float   # 质量评分 0-10
    recommended_for: List[str] = field(default_factory=list)  # 推荐场景
    
    def value_ratio(self) -> float:
        """性价比 = 质量/成本"""
        if self.cost_per_1k == 0:
            return self.quality_score
        return self.quality_score / (self.cost_per_1k * 10)

@dataclass
class SkillConfig:
    """技能配置"""
    name: str              # 技能名称
    type: str              # tool/function/http
    config: Dict = field(default_factory=dict)  # 技能参数

@dataclass
class RoleDefinition:
    """角色定义"""
    name: str              # 角色名称
    description: str       # 角色描述
    skills: List[SkillConfig] = field(default_factory=list)
    model: Optional[ModelConfig] = None
    prompt_template: str = ""  # 系统提示词模板
    temperature: float = 0.7
    enabled: bool = True
    
    # 动态配置
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

class RoleRegistry:
    """角色注册表 - 管理所有可用角色"""
    
    def __init__(self):
        self.roles: Dict[str, RoleDefinition] = {}
        self.model_pool: Dict[str, ModelConfig] = {}
        self._load_builtin_models()
    
    def _load_builtin_models(self):
        """加载内置模型池（预配置的热门模型）"""
        builtin_models = {
            # 通义千问系列
            "qwen-max": ModelConfig(
                name="qwen-max",
                provider="dashscope",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.02,
                max_tokens=8192,
                latency_ms=800,
                quality_score=9.2,
                recommended_for=["writing", "analysis", "general"]
            ),
            "qwen-plus": ModelConfig(
                name="qwen-plus",
                provider="dashscope",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.01,
                max_tokens=32768,
                latency_ms=500,
                quality_score=8.5,
                recommended_for=["chat", "general", "translation"]
            ),
            "qwen-turbo": ModelConfig(
                name="qwen-turbo",
                provider="dashscope",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.002,
                max_tokens=8192,
                latency_ms=200,
                quality_score=7.5,
                recommended_for=["simple_chat", "classification"]
            ),
            "qwen-coder": ModelConfig(
                name="qwen-coder",
                provider="dashscope",
                capability=ModelCapability.CODING,
                cost_per_1k=0.02,
                max_tokens=16384,
                latency_ms=1000,
                quality_score=9.0,
                recommended_for=["coding", "debugging", "refactoring"]
            ),
            "qwen-vl-max": ModelConfig(
                name="qwen-vl-max",
                provider="dashscope",
                capability=ModelCapability.VISION,
                cost_per_1k=0.04,
                max_tokens=4096,
                latency_ms=1500,
                quality_score=9.0,
                recommended_for=["image_analysis", "ocr", "chart_reading"]
            ),
            "qwen-image-max": ModelConfig(
                name="qwen-image-max",
                provider="dashscope",
                capability=ModelCapability.IMAGE,
                cost_per_1k=0.08,
                max_tokens=1024,
                latency_ms=5000,
                quality_score=9.5,
                recommended_for=["image_generation", "photo_editing"]
            ),
            
            # GLM 系列
            "glm-edge": ModelConfig(
                name="glm-edge",
                provider="zhipu",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.001,
                max_tokens=8192,
                latency_ms=150,
                quality_score=7.0,
                recommended_for=["simple_tasks", "fast_response"]
            ),
            "glm-4-plus": ModelConfig(
                name="glm-4-plus",
                provider="zhipu",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.015,
                max_tokens=128000,
                latency_ms=600,
                quality_score=8.8,
                recommended_for=["long_context", "analysis"]
            ),
            
            # OpenAI 系列
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider="openai",
                capability=ModelCapability.MULTIMODAL,
                cost_per_1k=0.05,
                max_tokens=128000,
                latency_ms=1200,
                quality_score=9.5,
                recommended_for=["complex_reasoning", "multimodal"]
            ),
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                provider="openai",
                capability=ModelCapability.TEXT,
                cost_per_1k=0.008,
                max_tokens=128000,
                latency_ms=400,
                quality_score=8.5,
                recommended_for=["general", "chat", "translation"]
            ),
        }
        
        self.model_pool.update(builtin_models)
    
    def register_role(self, role: RoleDefinition):
        """注册新角色"""
        self.roles[role.name] = role
    
    def unregister_role(self, role_name: str):
        """注销角色"""
        if role_name in self.roles:
            del self.roles[role_name]
    
    def get_role(self, role_name: str) -> Optional[RoleDefinition]:
        """获取角色"""
        return self.roles.get(role_name)
    
    def list_roles(self, tags: Optional[List[str]] = None) -> List[RoleDefinition]:
        """列出角色（可选按标签过滤）"""
        if not tags:
            return [r for r in self.roles.values() if r.enabled]
        
        return [
            r for r in self.roles.values()
            if r.enabled and any(tag in r.tags for tag in tags)
        ]
    
    def recommend_model(self, task_type: str, 
                        optimize_for: str = "balance") -> ModelConfig:
        """
        智能模型推荐
        
        Args:
            task_type: 任务类型 (coding/writing/analysis/etc)
            optimize_for: 优化目标 (speed/cost/quality/balance)
        
        Returns:
            最合适的模型配置
        """
        candidates = [
            m for m in self.model_pool.values()
            if task_type in m.recommended_for or "general" in m.recommended_for
        ]
        
        if not candidates:
            # 兜底返回通用模型
            return self.model_pool.get("qwen-plus")
        
        # 根据优化目标排序
        if optimize_for == "speed":
            return min(candidates, key=lambda x: x.latency_ms)
        elif optimize_for == "cost":
            return min(candidates, key=lambda x: x.cost_per_1k)
        elif optimize_for == "quality":
            return max(candidates, key=lambda x: x.quality_score)
        else:  # balance
            return max(candidates, key=lambda x: x.value_ratio())


class RoleLoader:
    """角色加载器 - 从文件加载用户自定义角色"""
    
    def __init__(self, registry: RoleRegistry):
        self.registry = registry
        self.config_dir = Path.home() / ".copaw" / "lingxi_roles"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_yaml(self, filepath: str) -> RoleDefinition:
        """从 YAML 文件加载角色"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在：{filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return self._parse_config(config)
    
    def load_from_json(self, filepath: str) -> RoleDefinition:
        """从 JSON 文件加载角色"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在：{filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return self._parse_config(config)
    
    def _parse_config(self, config: Dict) -> RoleDefinition:
        """解析配置文件为角色对象"""
        # 解析技能
        skills = []
        for skill_cfg in config.get("skills", []):
            skills.append(SkillConfig(**skill_cfg))
        
        # 解析模型（如果指定）
        model = None
        if "model" in config:
            model_name = config["model"]
            if model_name in self.registry.model_pool:
                model = self.registry.model_pool[model_name]
            else:
                # 使用推荐的模型
                model = self.registry.recommend_model(
                    config.get("task_type", "general"),
                    config.get("optimize_for", "balance")
                )
        
        # 创建角色
        role = RoleDefinition(
            name=config["name"],
            description=config.get("description", ""),
            skills=skills,
            model=model,
            prompt_template=config.get("prompt_template", ""),
            temperature=config.get("temperature", 0.7),
            enabled=config.get("enabled", True),
            tags=config.get("tags", []),
            metadata=config.get("metadata", {})
        )
        
        return role
    
    def save_role(self, role: RoleDefinition, filename: str):
        """保存角色到 YAML 文件"""
        filepath = self.config_dir / filename
        
        data = {
            "name": role.name,
            "description": role.description,
            "model": role.model.name if role.model else None,
            "temperature": role.temperature,
            "tags": role.tags,
            "enabled": role.enabled,
            "skills": [
                {"name": s.name, "type": s.type, "config": s.config}
                for s in role.skills
            ],
            "prompt_template": role.prompt_template,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✅ 角色已保存到：{filepath}")
    
    def load_all_user_roles(self):
        """批量加载用户目录下所有角色"""
        for filepath in self.config_dir.glob("*.yaml"):
            try:
                role = self.load_from_yaml(str(filepath))
                self.registry.register_role(role)
                print(f"✅ 加载角色：{role.name}")
            except Exception as e:
                print(f"❌ 加载失败 {filepath}: {e}")


# 场景模板
SCENE_TEMPLATES = {
    "ecommerce": {
        "name": "电商运营专家",
        "roles": ["文案专家", "图像处理师", "客服助手", "数据分析员"],
        "description": "适合电商运营的全套 AI 团队"
    },
    "content_creator": {
        "name": "内容创作者",
        "roles": ["文案专家", "视频剪辑师", "插画师", "翻译专家"],
        "description": "社交媒体内容创作全套工具"
    },
    "developer": {
        "name": "开发助手",
        "roles": ["代码专家", "测试工程师", "文档撰写员", "技术翻译"],
        "description": "软件开发全流程支持"
    }
}


def generate_role_template(scene: str = "writer") -> str:
    """生成角色模板示例"""
    
    templates = {
        "writer": """# 写作专家角色模板
name: 小说作家
description: 擅长写各类小说的专业作家
model: qwen-max
temperature: 0.9
tags: [writing, creative, story]
enabled: true

skills:
  - name: writing
    type: tool
    config:
      style: 现实主义
      word_count: 5000

prompt_template: |
  你是一位资深小说作家，擅长...
""",
        
        "coder": """# 代码专家角色模板
name: Python 工程师
description: 专业的 Python 开发工程师
model: qwen-coder
temperature: 0.3
tags: [coding, python, engineering]
enabled: true

skills:
  - name: code-generation
    type: tool
    config:
      language: python
      lint: true
  - name: code-review
    type: tool
    config:
      strict: true

prompt_template: |
  你是一位 10 年经验的 Python 专家...
""",
        
        "analyst": """# 数据分析专家角色模板
name: 数据分析师
description: 精通数据挖掘和商业分析
model: qwen-max
temperature: 0.2
tags: [data, analysis, business]
enabled: true

skills:
  - name: data-analysis
    type: tool
    config:
      output_format: markdown_table
  - name: chart-generation
    type: tool
    config:
      preferred_charts: [bar, line, pie]

prompt_template: |
  你是一位资深数据分析师，擅长...
"""
    }
    
    return templates.get(scene, templates["writer"])


if __name__ == "__main__":
    # 演示
    registry = RoleRegistry()
    loader = RoleLoader(registry)
    
    print("📦 内置模型池:")
    for name, model in list(registry.model_pool.items())[:5]:
        print(f"  - {name}: 质量{model.quality_score}/10, 成本¥{model.cost_per_1k}/1K tokens")
    
    print("\n🔍 模型推荐示例:")
    for task in ["coding", "writing", "image_analysis"]:
        model = registry.recommend_model(task, "balance")
        print(f"  [{task}] → {model.name} (性价比：{model.value_ratio():.2f})")
    
    print("\n📝 角色模板示例:")
    print(generate_role_template("writer"))
