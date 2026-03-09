#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 智能模型路由 v3.0.1

基于阿里云百炼大模型特性，根据任务类型自动选择最优模型

📊 模型特性分析 (阿里云百炼官方):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
模型                      | 文本生成 | 深度思考 | 视觉理解 | 定位
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
qwen3.5-plus             |    ✓    |    ✓    |    ✓    | 全能均衡
qwen3-max-2026-01-23     |    ✓    |    ✓    |    ✗    | 高端推理
qwen3-coder-next         |    ✓    |    ✗    |    ✗    | 轻量代码
qwen3-coder-plus         |    ✓    |    ✗    |    ✗    | 专业代码
glm-5                    |    ✓    |    ✓    |    ✗    | 中文深度
glm-4.7                  |    ✓    |    ✓    |    ✗    | 性价比
kimi-k2.5                |    ✓    |    ✓    |    ✓    | 长文本 + 视觉
MiniMax-M2.5             |    ✓    |    ✓    |    ✗    | 创意对话
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


# ==================== 模型配置 ====================

class ModelTier(Enum):
    """模型等级"""
    ECONOMY = "economy"      # 经济型 - 快速便宜
    STANDARD = "standard"    # 标准型 - 平衡
    PREMIUM = "premium"      # 高级型 - 高质量
    SPECIALIST = "specialist" # 专家型 - 特定领域


@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str
    name: str
    tier: ModelTier
    strengths: List[str]           # 擅长领域
    weak_areas: List[str]          # 不擅长领域
    cost_level: int                # 1-5，1 最便宜
    speed_level: int               # 1-5，1 最快
    max_context: int               # 最大上下文长度
    recommended_for: List[str]     # 推荐使用场景


# 阿里云百炼模型配置 (根据官方特性优化)
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "qwen3.5-plus": ModelConfig(
        model_id="qwen3.5-plus",
        name="通义千问 3.5 Plus",
        tier=ModelTier.STANDARD,
        strengths=["文本生成", "深度思考", "视觉理解", "全能均衡"],
        weak_areas=[],  # 无明显短板
        cost_level=2,
        speed_level=2,
        max_context=32768,
        recommended_for=["日常对话", "通用任务", "图像理解", "多模态任务", "快速响应"]
    ),
    
    "qwen3-max-2026-01-23": ModelConfig(
        model_id="qwen3-max-2026-01-23",
        name="通义千问 3 Max",
        tier=ModelTier.PREMIUM,
        strengths=["文本生成", "深度思考", "复杂推理", "高质量输出"],
        weak_areas=["视觉理解"],
        cost_level=5,
        speed_level=3,
        max_context=65536,
        recommended_for=["重要决策", "复杂分析", "专业咨询", "深度思考", "高质量文案"]
    ),
    
    "qwen3-coder-next": ModelConfig(
        model_id="qwen3-coder-next",
        name="通义千问 Coder Next",
        tier=ModelTier.SPECIALIST,
        strengths=["文本生成", "代码生成", "轻量快速"],
        weak_areas=["深度思考", "视觉理解"],
        cost_level=2,
        speed_level=1,  # 最快
        max_context=32768,
        recommended_for=["代码生成", "简单脚本", "快速原型", "代码补全"]
    ),
    
    "qwen3-coder-plus": ModelConfig(
        model_id="qwen3-coder-plus",
        name="通义千问 Coder Plus",
        tier=ModelTier.SPECIALIST,
        strengths=["文本生成", "代码生成", "复杂编程"],
        weak_areas=["深度思考", "视觉理解"],
        cost_level=4,
        speed_level=2,
        max_context=65536,
        recommended_for=["复杂代码", "架构设计", "系统开发", "代码重构", "技术文档"]
    ),
    
    "glm-5": ModelConfig(
        model_id="glm-5",
        name="智谱 GLM-5",
        tier=ModelTier.STANDARD,
        strengths=["文本生成", "深度思考", "中文理解", "逻辑推理"],
        weak_areas=["视觉理解"],
        cost_level=3,
        speed_level=2,
        max_context=128000,
        recommended_for=["中文任务", "知识问答", "文档理解", "长文分析", "逻辑推理"]
    ),
    
    "glm-4.7": ModelConfig(
        model_id="glm-4.7",
        name="智谱 GLM-4.7",
        tier=ModelTier.ECONOMY,
        strengths=["文本生成", "深度思考", "性价比", "快速响应"],
        weak_areas=["视觉理解"],
        cost_level=1,  # 最便宜
        speed_level=1,  # 最快
        max_context=32768,
        recommended_for=["简单问答", "日常聊天", "快速查询", "低成本任务", "高频调用"]
    ),
    
    "kimi-k2.5": ModelConfig(
        model_id="kimi-k2.5",
        name="月之暗面 Kimi K2.5",
        tier=ModelTier.SPECIALIST,
        strengths=["文本生成", "深度思考", "视觉理解", "超长上下文"],
        weak_areas=[],  # 无明显短板
        cost_level=3,
        speed_level=3,
        max_context=200000,  # 最长上下文
        recommended_for=["长文档", "多文件分析", "图像理解", "资料汇总", "论文阅读", "合同审查"]
    ),
    
    "MiniMax-M2.5": ModelConfig(
        model_id="MiniMax-M2.5",
        name="MiniMax M2.5",
        tier=ModelTier.STANDARD,
        strengths=["文本生成", "深度思考", "创意内容", "对话互动"],
        weak_areas=["视觉理解"],
        cost_level=2,
        speed_level=2,
        max_context=32768,
        recommended_for=["创意写作", "角色扮演", "情感陪伴", "故事创作", "营销文案", "对话互动"]
    ),
}


# ==================== 任务类型定义 ====================

class TaskType(Enum):
    """任务类型"""
    # 对话类
    CHAT = "chat"
    GREETING = "greeting"
    EMOTIONAL = "emotional"
    
    # 创作类
    CREATIVE_WRITING = "creative_writing"
    COPYWRITING = "copywriting"
    STORY = "story"
    POEM = "poem"
    
    # 代码类
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUG = "debug"
    ARCHITECTURE = "architecture"
    
    # 分析类
    ANALYSIS = "analysis"
    RESEARCH = "research"
    DATA_PROCESSING = "data_processing"
    DECISION = "decision"
    
    # 文档类
    DOCUMENT = "document"
    SUMMARY = "summary"
    TRANSLATION = "translation"
    
    # 专业类
    PROFESSIONAL = "professional"
    CONSULTING = "consulting"
    
    # 视觉类 (支持视觉理解的模型：qwen3.5-plus, kimi-k2.5)
    VISION = "vision"
    IMAGE_ANALYSIS = "image_analysis"
    
    # 默认
    GENERAL = "general"


# ==================== 任务识别规则 ====================

TASK_PATTERNS: Dict[TaskType, List[str]] = {
    # ========== 对话类 ==========
    TaskType.GREETING: ["你好", "早", "嗨", "hello", "hi", "在吗", "在不在"],
    TaskType.EMOTIONAL: ["开心", "难过", "生气", "累", "无聊", "想你了", "爱你"],
    TaskType.CHAT: ["聊天", "聊聊", "说说", "讲讲", "你怎么看", "你觉得"],
    
    # ========== 创作类 ==========
    TaskType.CREATIVE_WRITING: ["写", "创作", "生成", "文案", "文章", "内容"],
    TaskType.COPYWRITING: ["小红书", "微博", "广告", "营销", "推广", "标题"],
    TaskType.STORY: ["故事", "小说", "剧情", "编一个", "写个故事"],
    TaskType.POEM: ["诗", "诗词", "歌词", "写首诗"],
    
    # ========== 代码类 ==========
    TaskType.CODE_GENERATION: ["代码", "脚本", "程序", "函数", "写个", "实现"],
    TaskType.CODE_REVIEW: ["审查", "检查代码", "代码质量", "优化代码"],
    TaskType.DEBUG: ["bug", "错误", "报错", "修复", "调试", "为什么不行"],
    TaskType.ARCHITECTURE: ["架构", "设计", "系统", "方案", "技术选型"],
    
    # ========== 分析类 ==========
    TaskType.ANALYSIS: ["分析", "解析", "剖析", "拆解", "对比"],
    TaskType.RESEARCH: ["研究", "调研", "了解", "查一下", "搜索"],
    TaskType.DATA_PROCESSING: ["数据", "处理", "整理", "统计", "报表"],
    TaskType.DECISION: ["建议", "推荐", "选择", "哪个更好", "怎么办"],
    
    # ========== 文档类 ==========
    TaskType.DOCUMENT: ["文档", "报告", "说明", "指南", "教程"],
    TaskType.SUMMARY: ["总结", "摘要", "概括", "要点", "提炼"],
    TaskType.TRANSLATION: ["翻译", "translate", "英文", "中文", "中英"],
    
    # ========== 专业类 ==========
    TaskType.PROFESSIONAL: ["专业", "法律", "医疗", "金融", "财务", "税务"],
    TaskType.CONSULTING: ["咨询", "请教", "指导", "建议", "方案"],
    
    # ========== 视觉类 (新增) ==========
    TaskType.VISION: ["图片", "图像", "看图", "识图", "视觉", "截图", "照片"],
    TaskType.IMAGE_ANALYSIS: ["分析图片", "看图说话", "图片内容", "这是什么图"],
}


# ==================== 智能路由引擎 ====================

@dataclass
class RoutingResult:
    """路由结果"""
    model_id: str
    model_name: str
    confidence: float           # 置信度 0-1
    reason: str                 # 选择理由
    task_type: TaskType
    alternative_models: List[str]  # 备选模型


class ModelRouter:
    """智能模型路由器"""
    
    def __init__(self):
        self.default_model = "qwen3.5-plus"  # 默认模型
        self.premium_model = "qwen3-max-2026-01-23"  # 高质量任务模型
    
    def detect_task_type(self, user_input: str) -> Tuple[TaskType, List[str]]:
        """
        检测任务类型
        
        Returns:
            (task_type, matched_keywords)
        """
        normalized = user_input.lower()
        matches: Dict[TaskType, List[str]] = {}
        
        # 匹配任务模式
        for task_type, patterns in TASK_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in normalized:
                    if task_type not in matches:
                        matches[task_type] = []
                    matches[task_type].append(pattern)
        
        if not matches:
            return TaskType.GENERAL, []
        
        # 选择匹配最多的任务类型
        best_type = max(matches.keys(), key=lambda t: len(matches[t]))
        return best_type, matches[best_type]
    
    def route(self, user_input: str, 
              priority: str = "balanced",
              max_cost: int = None,
              require_speed: bool = False) -> RoutingResult:
        """
        智能路由 - 根据任务类型选择最优模型
        
        Args:
            user_input: 用户输入
            priority: 优先级策略
                - "balanced": 平衡模式（默认）
                - "quality": 质量优先
                - "speed": 速度优先
                - "economy": 经济优先
            max_cost: 最大成本等级 (1-5)
            require_speed: 是否要求快速响应
        
        Returns:
            RoutingResult: 路由结果
        """
        # 1. 检测任务类型
        task_type, keywords = self.detect_task_type(user_input)
        
        # 2. 根据任务类型获取推荐模型
        recommended_models = self._get_recommended_models(task_type)
        
        # 3. 应用优先级策略
        if priority == "quality":
            # 质量优先：选择最高级的模型
            selected = self._select_by_quality(recommended_models)
        elif priority == "speed":
            # 速度优先：选择最快的模型
            selected = self._select_by_speed(recommended_models)
        elif priority == "economy":
            # 经济优先：选择最便宜的模型
            selected = self._select_by_economy(recommended_models)
        else:
            # 平衡模式：综合评分
            selected = self._select_balanced(recommended_models, task_type)
        
        # 4. 应用约束
        if max_cost and selected.cost_level > max_cost:
            # 成本超限，降级
            selected = self._downgrade_for_cost(recommended_models, max_cost)
        
        if require_speed and selected.speed_level > 3:
            # 速度不达标，换更快的
            selected = self._upgrade_for_speed(recommended_models)
        
        # 5. 生成结果
        config = MODEL_REGISTRY[selected.model_id]
        alternatives = [m for m in recommended_models if m != selected.model_id][:2]
        
        return RoutingResult(
            model_id=selected.model_id,
            model_name=config.name,
            confidence=self._calculate_confidence(task_type, keywords),
            reason=self._generate_reason(selected, task_type, priority),
            task_type=task_type,
            alternative_models=alternatives
        )
    
    def _get_recommended_models(self, task_type: TaskType) -> List[str]:
        """
        获取任务类型推荐的模型列表
        
        基于阿里云百炼官方特性:
        - 深度思考任务优先：qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5
        - 视觉理解任务：qwen3.5-plus, kimi-k2.5
        - 代码任务：qwen3-coder-next (轻量), qwen3-coder-plus (专业)
        - 性价比：glm-4.7
        """
        recommendations = {
            # ========== 对话类 ==========
            TaskType.GREETING: ["glm-4.7", "qwen3.5-plus"],  # 快速 + 便宜
            TaskType.EMOTIONAL: ["MiniMax-M2.5", "qwen3.5-plus"],  # 情感表达强
            TaskType.CHAT: ["qwen3.5-plus", "MiniMax-M2.5", "glm-4.7"],  # 均衡
            
            # ========== 创作类 (需要深度思考) ==========
            TaskType.CREATIVE_WRITING: ["MiniMax-M2.5", "qwen3-max-2026-01-23"],  # 创意 + 深度
            TaskType.COPYWRITING: ["MiniMax-M2.5", "qwen3.5-plus"],  # 营销文案
            TaskType.STORY: ["MiniMax-M2.5", "qwen3-max-2026-01-23"],  # 故事创作
            TaskType.POEM: ["MiniMax-M2.5", "glm-5"],  # 诗词需要深度思考
            
            # ========== 代码类 (文本生成，不需要深度思考) ==========
            TaskType.CODE_GENERATION: ["qwen3-coder-next", "qwen3-coder-plus"],  # 轻量优先
            TaskType.CODE_REVIEW: ["qwen3-coder-plus", "qwen3-coder-next"],  # 专业优先
            TaskType.DEBUG: ["qwen3-coder-next", "qwen3-coder-plus"],  # 快速定位
            TaskType.ARCHITECTURE: ["qwen3-coder-plus", "qwen3-max-2026-01-23"],  # 需要深度思考
            
            # ========== 分析类 (需要深度思考) ==========
            TaskType.ANALYSIS: ["qwen3-max-2026-01-23", "glm-5"],  # 深度分析
            TaskType.RESEARCH: ["glm-5", "kimi-k2.5"],  # 长文本研究
            TaskType.DATA_PROCESSING: ["glm-5", "qwen3.5-plus"],  # 数据处理
            TaskType.DECISION: ["qwen3-max-2026-01-23", "glm-5"],  # 重要决策
            
            # ========== 文档类 (需要深度思考 + 长文本) ==========
            TaskType.DOCUMENT: ["kimi-k2.5", "glm-5"],  # 长文档
            TaskType.SUMMARY: ["kimi-k2.5", "glm-5"],  # 摘要总结
            TaskType.TRANSLATION: ["qwen3.5-plus", "glm-5"],  # 翻译
            
            # ========== 专业类 (需要深度思考) ==========
            TaskType.PROFESSIONAL: ["qwen3-max-2026-01-23", "glm-5"],  # 专业咨询
            TaskType.CONSULTING: ["qwen3-max-2026-01-23", "glm-5"],  # 深度咨询
            
            # ========== 视觉理解类 ==========
            TaskType.VISION: ["qwen3.5-plus", "kimi-k2.5"],  # 图像理解
            
            # ========== 默认 ==========
            TaskType.GENERAL: ["qwen3.5-plus", "glm-4.7"],  # 全能均衡
        }
        
        return recommendations.get(task_type, ["qwen3.5-plus"])
    
    def _select_by_quality(self, model_ids: List[str]) -> ModelConfig:
        """质量优先选择"""
        best = None
        best_tier = -1
        
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            tier_value = {
                ModelTier.ECONOMY: 1,
                ModelTier.STANDARD: 2,
                ModelTier.PREMIUM: 3,
                ModelTier.SPECIALIST: 3,
            }.get(config.tier, 0)
            
            if tier_value > best_tier:
                best_tier = tier_value
                best = config
        
        return best or MODEL_REGISTRY[self.default_model]
    
    def _select_by_speed(self, model_ids: List[str]) -> ModelConfig:
        """速度优先选择"""
        best = None
        best_speed = 999
        
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            if config.speed_level < best_speed:
                best_speed = config.speed_level
                best = config
        
        return best or MODEL_REGISTRY[self.default_model]
    
    def _select_by_economy(self, model_ids: List[str]) -> ModelConfig:
        """经济优先选择"""
        best = None
        best_cost = 999
        
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            if config.cost_level < best_cost:
                best_cost = config.cost_level
                best = config
        
        return best or MODEL_REGISTRY[self.default_model]
    
    def _select_balanced(self, model_ids: List[str], task_type: TaskType) -> ModelConfig:
        """平衡模式选择 - 综合评分"""
        best = None
        best_score = -1
        
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            
            # 综合评分：考虑等级、速度、成本
            tier_score = {
                ModelTier.ECONOMY: 1,
                ModelTier.STANDARD: 2,
                ModelTier.PREMIUM: 3,
                ModelTier.SPECIALIST: 3,
            }.get(config.tier, 0)
            
            # 任务匹配度
            match_score = 0
            if task_type.value in config.recommended_for or \
               any(t in config.recommended_for for t in task_type.value.split('_')):
                match_score = 2
            
            # 综合得分
            score = tier_score + match_score - (config.cost_level * 0.1)
            
            if score > best_score:
                best_score = score
                best = config
        
        return best or MODEL_REGISTRY[self.default_model]
    
    def _downgrade_for_cost(self, model_ids: List[str], max_cost: int) -> ModelConfig:
        """成本降级"""
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            if config.cost_level <= max_cost:
                return config
        
        return MODEL_REGISTRY[self.default_model]
    
    def _upgrade_for_speed(self, model_ids: List[str]) -> ModelConfig:
        """速度升级"""
        best = None
        best_speed = 999
        
        for mid in model_ids:
            if mid not in MODEL_REGISTRY:
                continue
            config = MODEL_REGISTRY[mid]
            if config.speed_level < best_speed:
                best_speed = config.speed_level
                best = config
        
        return best or MODEL_REGISTRY[self.default_model]
    
    def _calculate_confidence(self, task_type: TaskType, keywords: List[str]) -> float:
        """计算置信度"""
        base_confidence = 0.7
        
        # 关键词越多，置信度越高
        keyword_bonus = min(len(keywords) * 0.1, 0.3)
        
        # 明确的任务类型置信度更高
        if task_type != TaskType.GENERAL:
            base_confidence = 0.8
        
        return min(base_confidence + keyword_bonus, 1.0)
    
    def _generate_reason(self, config: ModelConfig, task_type: TaskType, priority: str) -> str:
        """生成选择理由"""
        reasons = {
            "quality": f"质量优先：选择{config.name}以获得最佳输出质量",
            "speed": f"速度优先：选择{config.name}以实现快速响应",
            "economy": f"经济优先：选择{config.name}以降低成本",
            "balanced": f"平衡模式：{config.name}在{task_type.value}任务中表现优秀",
        }
        
        return reasons.get(priority, f"根据任务类型选择{config.name}")


# ==================== 全局实例 ====================

_router: Optional[ModelRouter] = None

def get_model_router() -> ModelRouter:
    """获取全局路由器实例"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def route_model(user_input: str, priority: str = "balanced") -> RoutingResult:
    """便捷路由函数"""
    router = get_model_router()
    return router.route(user_input, priority=priority)


# ==================== 测试 ====================

def test_router():
    """测试路由器"""
    print("=" * 80)
    print("🧠 灵犀智能模型路由测试")
    print("=" * 80)
    
    router = get_model_router()
    
    test_cases = [
        # (输入，期望模式)
        ("你好呀", "economy"),
        ("帮我写个 Python 脚本", "code"),
        ("写一个小红书文案", "creative"),
        ("这个代码有 bug，帮我看看", "code"),
        ("分析一下这个数据的趋势", "analysis"),
        ("总结这篇长文档的要点", "document"),
        ("给我一个专业的法律建议", "professional"),
        ("陪我聊聊天", "chat"),
        ("写一首诗", "creative"),
        ("设计一个微服务架构", "architecture"),
    ]
    
    for input_text, expected in test_cases:
        result = router.route(input_text)
        print(f"\n📝 输入：{input_text}")
        print(f"   任务类型：{result.task_type.value}")
        print(f"   推荐模型：{result.model_name} ({result.model_id})")
        print(f"   置信度：{result.confidence:.1%}")
        print(f"   理由：{result.reason}")
        if result.alternative_models:
            print(f"   备选：{', '.join(result.alternative_models)}")


if __name__ == "__main__":
    test_router()
