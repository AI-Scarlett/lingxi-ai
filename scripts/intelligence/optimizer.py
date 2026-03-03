#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化器 - Optimizer
自动优化任务执行策略 💋

功能：
- 模型推荐（根据任务类型和成本）
- Token 成本优化
- 执行顺序优化（并行/串行）
- 缓存策略优化
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .task_logger import TaskLogger
from .pattern_learner import PatternLearner, get_learner

@dataclass
class OptimizationResult:
    """优化结果"""
    task_type: str
    suggested_model: str          # 推荐模型
    estimated_cost: int           # 预估 token 成本
    estimated_duration_ms: float  # 预估耗时
    parallel_suggestions: List[str]  # 并行建议
    cache_suggestions: List[str]     # 缓存建议
    confidence: float             # 置信度 (0-1)


class Optimizer:
    """优化器"""
    
    # 模型成本（每 1000 token）
    MODEL_COSTS = {
        "qwen-turbo": 0.002,
        "qwen-plus": 0.004,
        "qwen-max": 0.02,
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.03,
        "gpt-4o": 0.05,
    }
    
    # 模型性能评分（1-10）
    MODEL_PERFORMANCE = {
        "qwen-turbo": 6,
        "qwen-plus": 8,
        "qwen-max": 9,
        "gpt-3.5-turbo": 6,
        "gpt-4": 9,
        "gpt-4o": 10,
    }
    
    def __init__(self, 
                 learner: Optional[PatternLearner] = None,
                 logger: Optional[TaskLogger] = None):
        self.learner = learner or get_learner()
        self.logger = logger or TaskLogger()
    
    def optimize(self, task_type: str, input_text: str) -> OptimizationResult:
        """
        优化任务执行策略
        
        Args:
            task_type: 任务类型
            input_text: 输入文本
            
        Returns:
            优化结果
        """
        # 获取历史模式
        pattern = self.learner.get_pattern(task_type)
        
        # 模型推荐
        suggested_model = self._recommend_model(task_type, pattern, input_text)
        
        # 成本预估
        estimated_cost = self._estimate_cost(task_type, pattern, suggested_model)
        
        # 耗时预估
        estimated_duration = self._estimate_duration(task_type, pattern)
        
        # 并行建议
        parallel_suggestions = self._suggest_parallel(task_type, input_text)
        
        # 缓存建议
        cache_suggestions = self._suggest_cache(task_type, input_text)
        
        # 置信度
        confidence = self._calculate_confidence(pattern)
        
        return OptimizationResult(
            task_type=task_type,
            suggested_model=suggested_model,
            estimated_cost=estimated_cost,
            estimated_duration_ms=estimated_duration,
            parallel_suggestions=parallel_suggestions,
            cache_suggestions=cache_suggestions,
            confidence=confidence
        )
    
    def _recommend_model(self, 
                         task_type: str, 
                         pattern: Optional[Any], 
                         input_text: str) -> str:
        """推荐模型"""
        # 1. 如果有历史偏好，优先使用
        if pattern and pattern.preferred_model:
            # 检查成功率
            if pattern.success_rate >= 0.9:
                return pattern.preferred_model
        
        # 2. 根据任务复杂度推荐
        complexity = self._analyze_complexity(input_text)
        
        if complexity >= 8:
            # 复杂任务用 qwen-max
            return "qwen-max"
        elif complexity >= 5:
            # 中等任务用 qwen-plus
            return "qwen-plus"
        else:
            # 简单任务用 qwen-turbo
            return "qwen-turbo"
    
    def _analyze_complexity(self, input_text: str) -> float:
        """
        分析任务复杂度（1-10）
        
        基于：
        - 输入长度
        - 关键词（开发、分析、创作等）
        - 步骤数
        """
        score = 0
        
        # 长度评分
        if len(input_text) > 200:
            score += 3
        elif len(input_text) > 100:
            score += 2
        elif len(input_text) > 50:
            score += 1
        
        # 关键词评分
        complex_keywords = ["开发", "分析", "设计", "架构", "系统", "优化", "研究"]
        for kw in complex_keywords:
            if kw in input_text:
                score += 1
        
        # 步骤数评分
        if "第一步" in input_text or "1." in input_text:
            score += 2
        
        return min(score, 10)
    
    def _estimate_cost(self, 
                       task_type: str, 
                       pattern: Optional[Any],
                       model: str) -> int:
        """预估 token 成本"""
        # 1. 使用历史平均
        if pattern and pattern.avg_token_cost > 0:
            return int(pattern.avg_token_cost)
        
        # 2. 基于模型默认估算
        base_costs = {
            "content_creation": 500,
            "image_generation": 200,
            "social_publish": 300,
            "coding": 800,
            "data_analysis": 600,
            "search": 200,
            "translation": 300,
            "reminder": 100,
            "chat": 200,
        }
        
        return base_costs.get(task_type, 400)
    
    def _estimate_duration(self, 
                           task_type: str, 
                           pattern: Optional[Any]) -> float:
        """预估耗时（毫秒）"""
        # 1. 使用历史平均
        if pattern and pattern.avg_duration_ms > 0:
            return pattern.avg_duration_ms
        
        # 2. 基于任务类型默认估算
        base_durations = {
            "content_creation": 2000,
            "image_generation": 5000,
            "social_publish": 3000,
            "coding": 5000,
            "data_analysis": 4000,
            "search": 1000,
            "translation": 1500,
            "reminder": 500,
            "chat": 800,
        }
        
        return base_durations.get(task_type, 2000)
    
    def _suggest_parallel(self, 
                          task_type: str, 
                          input_text: str) -> List[str]:
        """并行执行建议"""
        suggestions = []
        
        # 检测是否包含多个子任务
        if "和" in input_text and task_type in ["content_creation", "coding"]:
            suggestions.append("检测到多个子任务，建议并行执行")
        
        # 图片生成任务
        if task_type == "image_generation":
            if "多张" in input_text or "系列" in input_text:
                suggestions.append("多张图片生成，建议并行处理")
        
        # 发布任务
        if task_type == "social_publish":
            if "多平台" in input_text or "同时" in input_text:
                suggestions.append("多平台发布，建议并行执行")
        
        if not suggestions:
            suggestions.append("串行执行即可")
        
        return suggestions
    
    def _suggest_cache(self, 
                       task_type: str, 
                       input_text: str) -> List[str]:
        """缓存策略建议"""
        suggestions = []
        
        # 重复性问题
        if "?" in input_text or "吗" in input_text:
            suggestions.append("可能是重复性问题，启用缓存")
        
        # 模板类任务
        if task_type in ["content_creation", "social_publish"]:
            suggestions.append("模板类任务，缓存提示词模板")
        
        # 查询类任务
        if task_type in ["search", "translation"]:
            suggestions.append("查询类任务，缓存查询结果")
        
        if not suggestions:
            suggestions.append("按需缓存")
        
        return suggestions
    
    def _calculate_confidence(self, pattern: Optional[Any]) -> float:
        """计算置信度（0-1）"""
        if not pattern:
            return 0.3  # 无历史数据，置信度低
        
        # 基于执行次数
        if pattern.total_executions >= 20:
            exec_confidence = 1.0
        elif pattern.total_executions >= 10:
            exec_confidence = 0.8
        elif pattern.total_executions >= 5:
            exec_confidence = 0.6
        else:
            exec_confidence = 0.4
        
        # 基于成功率稳定性
        if pattern.success_rate >= 0.95:
            success_confidence = 1.0
        elif pattern.success_rate >= 0.9:
            success_confidence = 0.9
        elif pattern.success_rate >= 0.8:
            success_confidence = 0.8
        else:
            success_confidence = 0.6
        
        return (exec_confidence + success_confidence) / 2
    
    def get_cost_optimization_report(self, days: int = 7) -> str:
        """
        生成成本优化报告
        
        Returns:
            报告文本
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = self.logger.get_logs(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if not logs:
            return "数据不足，继续积累任务日志"
        
        # 按模型分组统计
        model_stats = {}
        for log in logs:
            model = log.model_used
            if model not in model_stats:
                model_stats[model] = {
                    "count": 0,
                    "total_tokens": 0,
                    "success": 0
                }
            model_stats[model]["count"] += 1
            model_stats[model]["total_tokens"] += log.token_cost
            if log.success:
                model_stats[model]["success"] += 1
        
        # 生成报告
        report = []
        report.append("💰 成本优化报告\n")
        report.append("=" * 50 + "\n")
        
        total_cost = 0
        for model, stats in model_stats.items():
            cost_per_1k = self.MODEL_COSTS.get(model, 0.004)
            model_cost = (stats["total_tokens"] / 1000) * cost_per_1k
            total_cost += model_cost
            
            report.append(f"\n{model}:\n")
            report.append(f"   使用次数：{stats['count']}\n")
            report.append(f"   Token 总量：{stats['total_tokens']}\n")
            report.append(f"   成功率：{stats['success']/stats['count']:.1%}\n")
            report.append(f"   成本：¥{model_cost:.2f}\n")
        
        report.append(f"\n总成本：¥{total_cost:.2f}\n")
        report.append(f"平均每天：¥{total_cost/days:.2f}\n")
        
        # 优化建议
        report.append("\n💡 优化建议:\n")
        
        # 找出高成本低成功率的任务
        for model, stats in model_stats.items():
            success_rate = stats["success"] / stats["count"]
            if success_rate < 0.8 and stats["count"] >= 5:
                report.append(f"⚠️ {model} 成功率较低 ({success_rate:.1%})，考虑更换模型\n")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# 全局单例
_optimizer = None

def get_optimizer() -> Optimizer:
    """获取全局优化器实例"""
    global _optimizer
    if _optimizer is None:
        _optimizer = Optimizer()
    return _optimizer


# 使用示例
if __name__ == "__main__":
    optimizer = Optimizer()
    
    # 优化示例
    result = optimizer.optimize(
        task_type="content_creation",
        input_text="帮我写个小红书文案，关于 AI 助手的"
    )
    
    print(f"✅ 优化结果:")
    print(f"   推荐模型：{result.suggested_model}")
    print(f"   预估成本：{result.estimated_cost} token")
    print(f"   预估耗时：{result.estimated_duration_ms/1000:.1f}s")
    print(f"   置信度：{result.confidence:.1%}")
    print(f"   并行建议：{result.parallel_suggestions}")
    print(f"   缓存建议：{result.cache_suggestions}")
    
    # 成本报告
    report = optimizer.get_cost_optimization_report(days=7)
    print("\n" + report)
