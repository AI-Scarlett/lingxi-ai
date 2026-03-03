#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能学习系统 - Intelligence Engine
灵犀 2.3.0 核心功能 - 让灵犀越用越聪明 💋

整合模块：
- TaskLogger: 任务日志记录
- PatternLearner: 模式学习
- Optimizer: 自动优化
- Predictor: 预测调度

使用示例：
    from intelligence import IntelligenceEngine
    
    engine = IntelligenceEngine()
    
    # 记录任务
    engine.log_task(...)
    
    # 获取优化建议
    suggestion = engine.get_optimization("content_creation")
    
    # 预测下一个任务
    prediction = engine.predict_next_task()
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from .task_logger import TaskLogger, get_logger
from .pattern_learner import PatternLearner, get_learner
from .optimizer import Optimizer, get_optimizer
from .predictor import Predictor, get_predictor


class IntelligenceEngine:
    """智能学习引擎"""
    
    def __init__(self):
        self.logger = get_logger()
        self.learner = get_learner()
        self.optimizer = get_optimizer()
        self.predictor = get_predictor()
        self._initialized = False
    
    def initialize(self, analyze_days: int = 7):
        """
        初始化智能学习系统
        
        Args:
            analyze_days: 分析最近 N 天的数据
        """
        # 分析历史模式
        self.learner.analyze_patterns(days=analyze_days)
        self._initialized = True
    
    def log_task(self,
                 task_type: str,
                 user_id: str,
                 input_text: str,
                 output_text: str,
                 model_used: str,
                 token_cost: int,
                 duration_ms: float,
                 success: bool,
                 feedback: Optional[str] = None,
                 metadata: Optional[Dict] = None) -> str:
        """
        记录任务日志
        
        Returns:
            task_id: 任务唯一 ID
        """
        return self.logger.log(
            task_type=task_type,
            user_id=user_id,
            input_text=input_text,
            output_text=output_text,
            model_used=model_used,
            token_cost=token_cost,
            duration_ms=duration_ms,
            success=success,
            feedback=feedback,
            metadata=metadata
        )
    
    def get_optimization(self, task_type: str, input_text: str) -> Dict[str, Any]:
        """
        获取优化建议
        
        Args:
            task_type: 任务类型
            input_text: 输入文本
            
        Returns:
            优化建议字典
        """
        result = self.optimizer.optimize(task_type, input_text)
        
        return {
            "suggested_model": result.suggested_model,
            "estimated_cost": result.estimated_cost,
            "estimated_duration_ms": result.estimated_duration_ms,
            "parallel_suggestions": result.parallel_suggestions,
            "cache_suggestions": result.cache_suggestions,
            "confidence": result.confidence
        }
    
    def predict_next_task(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        预测下一个任务
        
        Args:
            user_id: 用户 ID
            
        Returns:
            预测结果字典，如果数据不足返回 None
        """
        prediction = self.predictor.predict_next_task(user_id)
        
        if not prediction:
            return None
        
        return {
            "task_type": prediction.task_type,
            "probability": prediction.probability,
            "estimated_time": prediction.estimated_time,
            "confidence": prediction.confidence,
            "suggested_prep": prediction.suggested_prep,
            "reasoning": prediction.reasoning
        }
    
    def get_patterns(self) -> Dict[str, Any]:
        """获取所有学习到的模式"""
        patterns = self.learner.get_all_patterns()
        return {k: v.to_dict() for k, v in patterns.items()}
    
    def get_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        获取统计数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            统计字典
        """
        return self.logger.get_stats(start_date, end_date)
    
    def generate_report(self, days: int = 7) -> str:
        """
        生成综合报告
        
        Args:
            days: 报告天数
            
        Returns:
            报告文本
        """
        report = []
        report.append("🧠 灵犀智能学习系统报告\n")
        report.append("=" * 60 + "\n")
        report.append(f"统计周期：最近{days}天\n")
        report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("=" * 60 + "\n\n")
        
        # 1. 统计概览
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        stats = self.get_stats(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        report.append("📊 统计概览\n")
        report.append(f"   总任务数：{stats['total_tasks']}\n")
        report.append(f"   成功率：{stats['success_rate']:.1%}\n")
        report.append(f"   平均耗时：{stats['avg_duration_ms']/1000:.1f}s\n")
        report.append(f"   平均 Token: {stats['avg_token_cost']:.0f}\n\n")
        
        # 2. 学习到的模式
        patterns = self.get_patterns()
        if patterns:
            report.append("🎯 学习到的模式\n")
            for task_type, pattern in patterns.items():
                report.append(f"\n   {task_type}:\n")
                report.append(f"      频率：{pattern['frequency']:.1f} 次/天\n")
                report.append(f"      偏好时段：{pattern['preferred_hours']}\n")
                report.append(f"      偏好模型：{pattern['preferred_model']}\n")
                report.append(f"      成功率：{pattern['success_rate']:.1%}\n")
                report.append(f"      总执行：{pattern['total_executions']} 次\n")
        
        # 3. 优化建议
        report.append("\n💡 优化建议\n")
        for task_type in patterns.keys():
            suggestions = self.learner.get_optimization_suggestions(task_type)
            report.append(f"   {task_type}: {suggestions[0]}\n")
        
        # 4. 预测
        report.append("\n🔮 智能预测\n")
        prediction = self.predict_next_task("default_user")
        if prediction:
            report.append(f"   最可能任务：{prediction['task_type']}\n")
            report.append(f"   概率：{prediction['probability']:.1%}\n")
            report.append(f"   预计时间：{prediction['estimated_time'][11:16]}\n")
            report.append(f"   置信度：{prediction['confidence']}\n")
        else:
            report.append("   数据不足，继续积累\n")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def should_remind(self, advance_minutes: int = 30) -> Optional[str]:
        """
        判断是否应该发送提醒
        
        Args:
            advance_minutes: 提前多少分钟提醒
            
        Returns:
            提醒消息，如果不需要提醒返回 None
        """
        prediction = self.predict_next_task("default_user")
        
        if not prediction:
            return None
        
        if prediction['confidence'] == 'low':
            return None
        
        # 检查是否应该提醒
        if self.predictor.should_remind(
            type('Prediction', (), prediction)(),  # 转换为对象
            advance_minutes
        ):
            return self.predictor.generate_reminder_message(
                type('Prediction', (), prediction)()
            )
        
        return None


# 全局单例
_engine = None

def get_engine() -> IntelligenceEngine:
    """获取全局智能学习引擎实例"""
    global _engine
    if _engine is None:
        _engine = IntelligenceEngine()
    return _engine


# 使用示例
if __name__ == "__main__":
    engine = IntelligenceEngine()
    
    # 初始化（分析最近 7 天数据）
    print("🧠 初始化智能学习系统...")
    engine.initialize(analyze_days=7)
    
    # 生成报告
    report = engine.generate_report(days=7)
    print(report)
    
    # 记录示例任务
    print("\n📝 记录示例任务...")
    task_id = engine.log_task(
        task_type="content_creation",
        user_id="test_user",
        input_text="帮我写个小红书文案",
        output_text="文案内容...",
        model_used="qwen-plus",
        token_cost=500,
        duration_ms=1200,
        success=True
    )
    print(f"✅ 任务已记录：{task_id}")
    
    # 获取优化建议
    print("\n💡 获取优化建议...")
    optimization = engine.get_optimization(
        task_type="content_creation",
        input_text="帮我写个小红书文案，关于 AI 助手的"
    )
    print(f"   推荐模型：{optimization['suggested_model']}")
    print(f"   预估成本：{optimization['estimated_cost']} token")
    print(f"   预估耗时：{optimization['estimated_duration_ms']/1000:.1f}s")
    
    # 预测下一个任务
    print("\n🔮 预测下一个任务...")
    prediction = engine.predict_next_task("test_user")
    if prediction:
        print(f"   任务类型：{prediction['task_type']}")
        print(f"   概率：{prediction['probability']:.1%}")
        print(f"   预计时间：{prediction['estimated_time']}")
        print(f"   置信度：{prediction['confidence']}")
    else:
        print("   数据不足，无法预测")
