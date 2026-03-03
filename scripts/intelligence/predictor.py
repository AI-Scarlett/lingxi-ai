#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测调度器 - Predictor
预测用户需求，提前准备资源 💋

功能：
- 时间模式预测（根据历史推测下次执行时间）
- 资源预加载（提前准备模型/模板）
- 智能提醒（预测用户可能需要帮助）
- 自动优化（预测性调整策略）
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .task_logger import TaskLogger
from .pattern_learner import PatternLearner, get_learner

@dataclass
class Prediction:
    """预测结果"""
    task_type: str                    # 预测任务类型
    probability: float                # 概率 (0-1)
    estimated_time: str               # 预计执行时间 (ISO 格式)
    confidence: str                   # 置信度 (high/medium/low)
    suggested_prep: List[str]         # 建议准备工作
    reasoning: str                    # 预测依据
    
    def to_dict(self) -> Dict:
        return {
            "task_type": self.task_type,
            "probability": self.probability,
            "estimated_time": self.estimated_time,
            "confidence": self.confidence,
            "suggested_prep": self.suggested_prep,
            "reasoning": self.reasoning
        }


class Predictor:
    """预测调度器"""
    
    def __init__(self, 
                 learner: Optional[PatternLearner] = None,
                 logger: Optional[TaskLogger] = None):
        self.learner = learner or get_learner()
        self.logger = logger or TaskLogger()
        self._preloaded_resources: Dict[str, Any] = {}
    
    def predict_next_task(self, user_id: str) -> Optional[Prediction]:
        """
        预测用户下一个任务
        
        Returns:
            预测结果，如果数据不足返回 None
        """
        patterns = self.learner.get_all_patterns()
        
        if not patterns:
            return None
        
        # 找出最可能的任务类型
        best_prediction = None
        best_score = 0
        
        for task_type, pattern in patterns.items():
            # 计算评分
            score = self._calculate_prediction_score(pattern)
            
            if score > best_score:
                best_score = score
                best_prediction = self._create_prediction(task_type, pattern)
        
        return best_prediction
    
    def _calculate_prediction_score(self, pattern) -> float:
        """
        计算预测评分
        
        基于：
        - 频率（越高越可能）
        - 最近执行时间（越近越可能）
        - 成功率（越高越可能）
        - 规律性（越规律越可能）
        """
        score = 0
        
        # 频率评分（0-4 分）
        if pattern.frequency >= 2:
            score += 4
        elif pattern.frequency >= 1:
            score += 3
        elif pattern.frequency >= 0.5:
            score += 2
        elif pattern.frequency >= 0.2:
            score += 1
        
        # 最近执行时间评分（0-3 分）
        if pattern.last_executed:
            last_exec = datetime.fromisoformat(pattern.last_executed)
            hours_ago = (datetime.now() - last_exec).total_seconds() / 3600
            
            if hours_ago <= 24:
                score += 3
            elif hours_ago <= 48:
                score += 2
            elif hours_ago <= 168:  # 7 天
                score += 1
        
        # 成功率评分（0-2 分）
        if pattern.success_rate >= 0.95:
            score += 2
        elif pattern.success_rate >= 0.9:
            score += 1
        
        # 规律性评分（0-1 分）
        if pattern.preferred_hours and len(pattern.preferred_hours) <= 2:
            score += 1  # 时间段集中，规律性强
        
        return score
    
    def _create_prediction(self, task_type: str, pattern) -> Prediction:
        """创建预测结果"""
        # 预计执行时间
        estimated_time = self._estimate_next_execution_time(pattern)
        
        # 概率
        probability = min(pattern.frequency / 3, 1.0)  # 归一化到 0-1
        
        # 置信度
        if pattern.total_executions >= 20 and pattern.success_rate >= 0.9:
            confidence = "high"
        elif pattern.total_executions >= 10:
            confidence = "medium"
        else:
            confidence = "low"
        
        # 建议准备
        suggested_prep = self._suggest_preparation(task_type, pattern)
        
        # 预测依据
        reasoning = self._generate_reasoning(task_type, pattern)
        
        return Prediction(
            task_type=task_type,
            probability=probability,
            estimated_time=estimated_time,
            confidence=confidence,
            suggested_prep=suggested_prep,
            reasoning=reasoning
        )
    
    def _estimate_next_execution_time(self, pattern) -> str:
        """预测下次执行时间"""
        now = datetime.now()
        
        # 如果有偏好小时段
        if pattern.preferred_hours:
            preferred_hour = pattern.preferred_hours[0]
            current_hour = now.hour
            
            # 如果已经过了今天的偏好时间，预测明天
            if current_hour >= preferred_hour:
                next_time = now + timedelta(days=1)
                next_time = next_time.replace(hour=preferred_hour, minute=0, second=0)
            else:
                next_time = now.replace(hour=preferred_hour, minute=0, second=0)
            
            return next_time.isoformat()
        
        # 没有偏好时间，预测 24 小时后
        next_time = now + timedelta(days=1)
        return next_time.isoformat()
    
    def _suggest_preparation(self, task_type: str, pattern) -> List[str]:
        """建议准备工作"""
        suggestions = []
        
        # 根据任务类型建议
        if task_type == "content_creation":
            suggestions.append("预加载文案模板")
            suggestions.append(f"准备模型：{pattern.preferred_model or 'qwen-plus'}")
        
        elif task_type == "image_generation":
            suggestions.append("预加载图片生成模型")
            suggestions.append("准备参考图片库")
        
        elif task_type == "social_publish":
            suggestions.append("预加载发布模板")
            suggestions.append("检查平台 API 状态")
        
        elif task_type == "coding":
            suggestions.append("预加载代码模板")
            suggestions.append("准备开发环境")
        
        # 根据偏好模型建议
        if pattern.preferred_model:
            suggestions.append(f"预热模型：{pattern.preferred_model}")
        
        # 根据时间段建议
        if pattern.preferred_hours:
            hour = pattern.preferred_hours[0]
            if 9 <= hour <= 11:
                suggestions.append("上午工作时间，准备高效执行")
            elif 14 <= hour <= 16:
                suggestions.append("下午工作时间，准备充足资源")
            elif 20 <= hour <= 22:
                suggestions.append("晚间时间，准备轻松模式")
        
        return suggestions
    
    def _generate_reasoning(self, task_type: str, pattern) -> str:
        """生成预测依据"""
        reasons = []
        
        # 频率依据
        if pattern.frequency >= 1:
            reasons.append(f"高频任务（{pattern.frequency:.1f}次/天）")
        
        # 时间依据
        if pattern.preferred_hours:
            hours = pattern.preferred_hours
            reasons.append(f"偏好时段：{hours[0]}点")
        
        # 成功率依据
        if pattern.success_rate >= 0.9:
            reasons.append(f"高成功率（{pattern.success_rate:.1%}）")
        
        # 执行次数依据
        if pattern.total_executions >= 20:
            reasons.append(f"充足样本（{pattern.total_executions}次执行）")
        
        return "，".join(reasons) if reasons else "基于历史数据分析"
    
    def preload_resources(self, prediction: Prediction):
        """
        预加载资源
        
        Args:
            prediction: 预测结果
        """
        task_type = prediction.task_type
        
        # 标记资源已预加载
        self._preloaded_resources[task_type] = {
            "preloaded_at": datetime.now().isoformat(),
            "suggestions": prediction.suggested_prep,
            "estimated_time": prediction.estimated_time
        }
    
    def get_preload_status(self) -> Dict[str, Any]:
        """获取预加载状态"""
        return {
            "preloaded_count": len(self._preloaded_resources),
            "resources": self._preloaded_resources
        }
    
    def should_remind(self, prediction: Prediction, advance_minutes: int = 30) -> bool:
        """
        判断是否应该发送提醒
        
        Args:
            prediction: 预测结果
            advance_minutes: 提前多少分钟提醒
            
        Returns:
            是否应该提醒
        """
        if prediction.confidence == "low":
            return False
        
        estimated_time = datetime.fromisoformat(prediction.estimated_time)
        now = datetime.now()
        time_diff = (estimated_time - now).total_seconds() / 60
        
        # 在提前时间内
        if 0 < time_diff <= advance_minutes:
            return True
        
        return False
    
    def generate_reminder_message(self, prediction: Prediction) -> str:
        """
        生成提醒消息
        
        Args:
            prediction: 预测结果
            
        Returns:
            提醒消息文本
        """
        messages = {
            "content_creation": "📝 创作任务",
            "image_generation": "🎨 图片生成",
            "social_publish": "📱 发布任务",
            "coding": "💻 开发任务",
            "data_analysis": "📊 数据分析",
            "search": "🔍 搜索任务",
            "translation": "🌐 翻译任务",
            "reminder": "⏰ 提醒任务",
            "chat": "💬 聊天",
        }
        
        task_name = messages.get(prediction.task_type, prediction.task_type)
        
        # 时间格式化
        estimated_time = datetime.fromisoformat(prediction.estimated_time)
        time_str = estimated_time.strftime("%H:%M")
        
        # 置信度图标
        confidence_icons = {
            "high": "✅",
            "medium": "⚠️",
            "low": "❓"
        }
        icon = confidence_icons.get(prediction.confidence, "❓")
        
        message = f"""{icon} 智能提醒

预测任务：{task_name}
预计时间：今天 {time_str}
置信度：{prediction.confidence}
预测依据：{prediction.reasoning}

💡 建议准备：
"""
        
        for prep in prediction.suggested_prep[:3]:
            message += f"   • {prep}\n"
        
        message += "\n需要我现在准备吗？"
        
        return message
    
    def get_prediction_report(self, days: int = 7) -> str:
        """
        生成预测报告
        
        Returns:
            报告文本
        """
        patterns = self.learner.get_all_patterns()
        
        if not patterns:
            return "数据不足，继续积累任务日志"
        
        report = []
        report.append("🔮 智能预测报告\n")
        report.append("=" * 50 + "\n")
        
        for task_type, pattern in patterns.items():
            prediction = self._create_prediction(task_type, pattern)
            
            report.append(f"\n📋 {task_type}\n")
            report.append(f"   概率：{prediction.probability:.1%}\n")
            report.append(f"   预计时间：{prediction.estimated_time[11:16]}\n")
            report.append(f"   置信度：{prediction.confidence}\n")
            report.append(f"   依据：{prediction.reasoning}\n")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# 全局单例
_predictor = None

def get_predictor() -> Predictor:
    """获取全局预测调度器实例"""
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor


# 使用示例
if __name__ == "__main__":
    predictor = Predictor()
    
    # 预测下一个任务
    prediction = predictor.predict_next_task("test_user")
    
    if prediction:
        print(f"✅ 预测结果:")
        print(f"   任务类型：{prediction.task_type}")
        print(f"   概率：{prediction.probability:.1%}")
        print(f"   预计时间：{prediction.estimated_time}")
        print(f"   置信度：{prediction.confidence}")
        print(f"   建议准备：{prediction.suggested_prep}")
        print(f"   预测依据：{prediction.reasoning}")
        
        # 预加载资源
        predictor.preload_resources(prediction)
        print(f"\n✅ 资源已预加载")
        
        # 生成提醒消息
        reminder = predictor.generate_reminder_message(prediction)
        print(f"\n📱 提醒消息:\n{reminder}")
    else:
        print("数据不足，无法预测")
    
    # 预测报告
    report = predictor.get_prediction_report(days=7)
    print("\n" + report)
