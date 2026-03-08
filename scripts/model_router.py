#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 智能模型路由配置
Smart Model Routing for Lingxi

作者：斯嘉丽 Scarlett
日期：2026-03-08

功能：
- 根据任务类型自动选择最优模型
- 代码任务 → Qwen-Coder
- 分析任务 → Qwen-Max
- 写作任务 → Qwen-Plus
- 聊天 → Qwen-Turbo
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum


class TaskType(Enum):
    """任务类型"""
    CODING = "coding"           # 编程、脚本、调试
    ANALYSIS = "analysis"       # 数据分析、报告
    WRITING = "writing"         # 文案、文章、创作
    SEARCH = "search"           # 搜索、调研
    TRANSLATION = "translation" # 翻译
    MATH = "math"              # 数学、计算
    CHAT = "chat"              # 聊天、问答
    PLANNING = "planning"      # 规划、编排
    IMAGE = "image"            # 图像生成/处理
    UNKNOWN = "unknown"        # 未知


@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str              # 模型 ID
    max_tokens: int            # 最大输出 token
    temperature: float         # 温度参数
    cost_per_1k: float         # 每 1K token 成本（美元）
    description: str           # 描述


# 模型配置表
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "qwen-coder": ModelConfig(
        model_id="qwen-coder",
        max_tokens=8192,
        temperature=0.1,
        cost_per_1k=0.002,
        description="代码专用模型，擅长编程、调试、代码生成"
    ),
    "qwen-max": ModelConfig(
        model_id="qwen-max",
        max_tokens=8192,
        temperature=0.3,
        cost_per_1k=0.004,
        description="最强通用模型，适合复杂分析、推理"
    ),
    "qwen-plus": ModelConfig(
        model_id="qwen-plus",
        max_tokens=8192,
        temperature=0.5,
        cost_per_1k=0.001,
        description="平衡性能和成本，适合写作、创作"
    ),
    "qwen-turbo": ModelConfig(
        model_id="qwen-turbo",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k=0.0005,
        description="快速响应，适合聊天、简单问答"
    ),
    "qwencode/qwen3.5-plus": ModelConfig(
        model_id="qwencode/qwen3.5-plus",
        max_tokens=8192,
        temperature=0.5,
        cost_per_1k=0.001,
        description="默认模型，平衡性能和成本"
    ),
}

# 任务类型 → 模型映射
TASK_MODEL_MAP: Dict[TaskType, str] = {
    TaskType.CODING: "qwen-coder",
    TaskType.ANALYSIS: "qwen-max",
    TaskType.WRITING: "qwen-plus",
    TaskType.SEARCH: "qwen-plus",
    TaskType.TRANSLATION: "qwen-plus",
    TaskType.MATH: "qwen-max",
    TaskType.CHAT: "qwen-turbo",
    TaskType.PLANNING: "qwen-plus",
    TaskType.IMAGE: "qwen-max",  # 需要多模态能力
    TaskType.UNKNOWN: "qwencode/qwen3.5-plus",  # 默认
}

# 任务类型关键词
TASK_KEYWORDS: Dict[TaskType, List[str]] = {
    TaskType.CODING: [
        "代码", "编程", "脚本", "函数", "类", "调试", "bug", "错误",
        "python", "java", "javascript", "c++", "写个", "实现",
        "算法", "数据结构", "api", "接口", "开发", "程序"
    ],
    TaskType.ANALYSIS: [
        "分析", "数据", "报表", "统计", "图表", "趋势", "洞察",
        "对比", "评估", "研究", "调查", "报告", "总结"
    ],
    TaskType.WRITING: [
        "写", "文案", "文章", "邮件", "通知", "公告", "博客",
        "小说", "故事", "剧本", "诗歌", "作文", "创作", "编辑",
        "润色", "修改", "优化", "改写"
    ],
    TaskType.SEARCH: [
        "搜索", "查找", "调研", "了解", "查询", "google", "百度"
    ],
    TaskType.TRANSLATION: [
        "翻译", "译成", "英文", "中文", "日文", "韩文", "语言"
    ],
    TaskType.MATH: [
        "计算", "数学", "公式", "方程", "求解", "算一下", "多少"
    ],
    TaskType.CHAT: [
        "你好", "嗨", "在吗", "聊聊", "聊天", "怎么样", "如何"
    ],
    TaskType.PLANNING: [
        "计划", "安排", "规划", "方案", "策略", "步骤", "流程"
    ],
    TaskType.IMAGE: [
        "图片", "图像", "生成", "设计", "封面", "海报", "画图"
    ],
}


class ModelRouter:
    """
    智能模型路由器
    
    根据任务内容自动选择最优模型
    """
    
    def __init__(self, default_model: str = "qwencode/qwen3.5-plus"):
        self.default_model = default_model
        self.model_registry = MODEL_REGISTRY
        self.task_model_map = TASK_MODEL_MAP
        self.task_keywords = TASK_KEYWORDS
    
    def detect_task_type(self, user_input: str) -> TaskType:
        """
        检测任务类型
        
        Args:
            user_input: 用户输入
        
        Returns:
            任务类型
        """
        input_lower = user_input.lower()
        
        # 统计各类型匹配分数
        scores = {task_type: 0 for task_type in TaskType}
        
        for task_type, keywords in self.task_keywords.items():
            for keyword in keywords:
                if keyword.lower() in input_lower:
                    scores[task_type] += 1
        
        # 返回最高分的类型
        max_score = max(scores.values())
        if max_score == 0:
            return TaskType.UNKNOWN
        
        # 获取所有最高分的类型（可能有多个）
        top_types = [t for t, s in scores.items() if s == max_score]
        
        # 优先级：coding > analysis > writing > others
        priority_order = [
            TaskType.CODING,
            TaskType.ANALYSIS,
            TaskType.MATH,
            TaskType.WRITING,
            TaskType.PLANNING,
            TaskType.IMAGE,
            TaskType.SEARCH,
            TaskType.TRANSLATION,
            TaskType.CHAT,
            TaskType.UNKNOWN
        ]
        
        for task_type in priority_order:
            if task_type in top_types:
                return task_type
        
        return top_types[0]
    
    def get_model_for_task(self, user_input: str, 
                          force_model: Optional[str] = None) -> str:
        """
        根据任务获取推荐模型
        
        Args:
            user_input: 用户输入
            force_model: 强制使用的模型（可选）
        
        Returns:
            推荐的模型 ID
        """
        # 如果强制指定模型，直接返回
        if force_model:
            return force_model
        
        # 检测任务类型
        task_type = self.detect_task_type(user_input)
        
        # 获取对应模型
        model_id = self.task_model_map.get(task_type, self.default_model)
        
        return model_id
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self.model_registry.get(model_id)
    
    def estimate_cost(self, user_input: str, 
                     estimated_output_tokens: int = 1000) -> float:
        """
        估算任务成本
        
        Args:
            user_input: 用户输入
            estimated_output_tokens: 预估输出 token 数
        
        Returns:
            预估成本（美元）
        """
        model_id = self.get_model_for_task(user_input)
        config = self.get_model_config(model_id)
        
        if not config:
            return 0.0
        
        return (estimated_output_tokens / 1000) * config.cost_per_1k
    
    def explain_choice(self, user_input: str) -> str:
        """
        解释模型选择原因
        
        Args:
            user_input: 用户输入
        
        Returns:
            解释文本
        """
        task_type = self.detect_task_type(user_input)
        model_id = self.get_model_for_task(user_input)
        config = self.get_model_config(model_id)
        
        task_type_names = {
            TaskType.CODING: "编程开发",
            TaskType.ANALYSIS: "数据分析",
            TaskType.WRITING: "文案写作",
            TaskType.SEARCH: "信息搜索",
            TaskType.TRANSLATION: "翻译",
            TaskType.MATH: "数学计算",
            TaskType.CHAT: "聊天问答",
            TaskType.PLANNING: "规划编排",
            TaskType.IMAGE: "图像处理",
            TaskType.UNKNOWN: "通用任务"
        }
        
        task_name = task_type_names.get(task_type, "未知")
        
        if config:
            return (
                f"🧠 任务类型：{task_name}\n"
                f"🤖 使用模型：{config.model_id}\n"
                f"📝 模型特点：{config.description}\n"
                f"💰 预估成本：${self.estimate_cost(user_input):.4f}"
            )
        else:
            return f"🤖 使用模型：{model_id}"


# 全局路由器实例
_router = None

def get_model_router() -> ModelRouter:
    """获取模型路由器实例"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def select_model(user_input: str, force_model: Optional[str] = None) -> str:
    """
    便捷函数：选择模型
    
    Args:
        user_input: 用户输入
        force_model: 强制使用的模型
    
    Returns:
        选择的模型 ID
    """
    router = get_model_router()
    return router.get_model_for_task(user_input, force_model)


# 测试
if __name__ == "__main__":
    router = ModelRouter()
    
    test_cases = [
        ("帮我写个 Python 脚本分析 Excel 数据", TaskType.CODING),
        ("写一篇小红书文案", TaskType.WRITING),
        ("分析一下这个月销售数据", TaskType.ANALYSIS),
        ("你好，在吗？", TaskType.CHAT),
        ("翻译这句话成英文", TaskType.TRANSLATION),
        ("计算 1+2+3+...+100", TaskType.MATH),
        ("帮我规划下周工作安排", TaskType.PLANNING),
        ("生成一张封面图片", TaskType.IMAGE),
    ]
    
    print("\n🧪 模型路由测试\n")
    print("=" * 60)
    
    for input_text, expected_type in test_cases:
        detected = router.detect_task_type(input_text)
        model = router.get_model_for_task(input_text)
        match = "✅" if detected == expected_type else "❌"
        
        print(f"\n{match} 输入：{input_text}")
        print(f"   检测类型：{detected.value} (期望：{expected_type.value})")
        print(f"   使用模型：{model}")
        print(f"   解释：{router.explain_choice(input_text)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成\n")
