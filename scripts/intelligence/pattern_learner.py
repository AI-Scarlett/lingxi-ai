#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模式学习器 - Pattern Learner
分析用户任务模式，学习执行偏好 💋

功能：
- 频率分析（任务执行频率）
- 时间模式识别（偏好时间段）
- 模型偏好学习
- 成本模式分析
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .task_logger import TaskLogger, TaskLog

@dataclass
class TaskPattern:
    """任务模式"""
    task_type: str                    # 任务类型
    frequency: float                  # 执行频率（次/天）
    preferred_hours: List[int]        # 偏好小时段
    preferred_model: str              # 偏好模型
    avg_token_cost: float             # 平均 token 消耗
    avg_duration_ms: float            # 平均耗时
    success_rate: float               # 成功率
    last_executed: str                # 最后执行时间
    total_executions: int             # 总执行次数
    
    def to_dict(self) -> Dict:
        return {
            "task_type": self.task_type,
            "frequency": self.frequency,
            "preferred_hours": self.preferred_hours,
            "preferred_model": self.preferred_model,
            "avg_token_cost": self.avg_token_cost,
            "avg_duration_ms": self.avg_duration_ms,
            "success_rate": self.success_rate,
            "last_executed": self.last_executed,
            "total_executions": self.total_executions
        }


class PatternLearner:
    """模式学习器"""
    
    def __init__(self, 
                 logger: Optional[TaskLogger] = None,
                 pattern_path: str = "~/.openclaw/workspace/patterns/"):
        self.logger = logger or TaskLogger()
        self.pattern_path = Path(pattern_path).expanduser()
        self.pattern_path.mkdir(parents=True, exist_ok=True)
        self._patterns: Dict[str, TaskPattern] = {}
        self._load_patterns()
    
    def _load_patterns(self):
        """加载已保存的模式"""
        pattern_file = self.pattern_path / "patterns.json"
        if pattern_file.exists():
            with open(pattern_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for task_type, pattern_data in data.items():
                    self._patterns[task_type] = TaskPattern(**pattern_data)
    
    def _save_patterns(self):
        """保存模式到文件"""
        pattern_file = self.pattern_path / "patterns.json"
        data = {k: v.to_dict() for k, v in self._patterns.items()}
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def analyze_patterns(self, days: int = 7) -> Dict[str, TaskPattern]:
        """
        分析任务模式
        
        Args:
            days: 分析最近 N 天的数据
            
        Returns:
            任务模式字典
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = self.logger.get_logs(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if not logs:
            return self._patterns
        
        # 按任务类型分组
        task_groups = defaultdict(list)
        for log in logs:
            task_groups[log.task_type].append(log)
        
        # 分析每种任务类型
        for task_type, task_logs in task_groups.items():
            pattern = self._analyze_task_type(task_type, task_logs, days)
            self._patterns[task_type] = pattern
        
        # 保存
        self._save_patterns()
        
        return self._patterns
    
    def _analyze_task_type(self, 
                           task_type: str, 
                           logs: List[TaskLog], 
                           days: int) -> TaskPattern:
        """分析特定任务类型的模式"""
        if not logs:
            return TaskPattern(
                task_type=task_type,
                frequency=0,
                preferred_hours=[],
                preferred_model="",
                avg_token_cost=0,
                avg_duration_ms=0,
                success_rate=0,
                last_executed="",
                total_executions=0
            )
        
        # 频率（次/天）
        frequency = len(logs) / days
        
        # 偏好小时段
        hour_counts = defaultdict(int)
        for log in logs:
            hour = datetime.fromisoformat(log.timestamp).hour
            hour_counts[hour] += 1
        
        # 取前 3 个高峰时段
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        preferred_hours = [h[0] for h in sorted_hours[:3]]
        
        # 偏好模型
        model_counts = defaultdict(int)
        for log in logs:
            model_counts[log.model_used] += 1
        preferred_model = max(model_counts.items(), key=lambda x: x[1])[0] if model_counts else ""
        
        # 平均 token 消耗
        avg_token_cost = sum(log.token_cost for log in logs) / len(logs)
        
        # 平均耗时
        avg_duration_ms = sum(log.duration_ms for log in logs) / len(logs)
        
        # 成功率
        success_count = sum(1 for log in logs if log.success)
        success_rate = success_count / len(logs)
        
        # 最后执行时间
        last_executed = max(log.timestamp for log in logs)
        
        # 总执行次数
        total_executions = len(logs)
        
        return TaskPattern(
            task_type=task_type,
            frequency=frequency,
            preferred_hours=preferred_hours,
            preferred_model=preferred_model,
            avg_token_cost=avg_token_cost,
            avg_duration_ms=avg_duration_ms,
            success_rate=success_rate,
            last_executed=last_executed,
            total_executions=total_executions
        )
    
    def get_pattern(self, task_type: str) -> Optional[TaskPattern]:
        """获取特定任务类型的模式"""
        return self._patterns.get(task_type)
    
    def get_all_patterns(self) -> Dict[str, TaskPattern]:
        """获取所有模式"""
        return self._patterns
    
    def predict_best_model(self, task_type: str) -> str:
        """预测最佳模型"""
        pattern = self.get_pattern(task_type)
        if pattern and pattern.preferred_model:
            return pattern.preferred_model
        return "qwen-plus"  # 默认模型
    
    def predict_execution_time(self, task_type: str) -> Optional[int]:
        """
        预测最佳执行时间（小时）
        
        Returns:
            建议执行小时（0-23），如果没有数据返回 None
        """
        pattern = self.get_pattern(task_type)
        if pattern and pattern.preferred_hours:
            return pattern.preferred_hours[0]
        return None
    
    def get_optimization_suggestions(self, task_type: str) -> List[str]:
        """
        获取优化建议
        
        Returns:
            建议列表
        """
        suggestions = []
        pattern = self.get_pattern(task_type)
        
        if not pattern:
            return ["数据不足，继续积累任务日志"]
        
        # 成功率低
        if pattern.success_rate < 0.8:
            suggestions.append(f"⚠️ 成功率较低 ({pattern.success_rate:.1%})，建议检查任务执行流程")
        
        # token 成本高
        if pattern.avg_token_cost > 1000:
            suggestions.append(f"💰 Token 成本较高 (平均{pattern.avg_token_cost:.0f})，考虑优化提示词")
        
        # 耗时长
        if pattern.avg_duration_ms > 5000:
            suggestions.append(f"⏱️ 执行耗时较长 (平均{pattern.avg_duration_ms/1000:.1f}s)，考虑并行优化")
        
        # 频率低
        if pattern.frequency < 0.5:
            suggestions.append(f"📅 使用频率较低 ({pattern.frequency:.1f}次/天)")
        
        if not suggestions:
            suggestions.append("✅ 表现良好，继续保持！")
        
        return suggestions
    
    def generate_report(self, days: int = 7) -> str:
        """
        生成模式分析报告
        
        Returns:
            报告文本
        """
        self.analyze_patterns(days)
        
        report = []
        report.append(f"📊 灵犀智能学习报告（最近{days}天）\n")
        report.append("=" * 50 + "\n")
        
        for task_type, pattern in self._patterns.items():
            report.append(f"\n📝 {task_type}\n")
            report.append(f"   频率：{pattern.frequency:.1f} 次/天\n")
            report.append(f"   偏好时段：{pattern.preferred_hours}\n")
            report.append(f"   偏好模型：{pattern.preferred_model}\n")
            report.append(f"   平均 Token: {pattern.avg_token_cost:.0f}\n")
            report.append(f"   平均耗时：{pattern.avg_duration_ms/1000:.1f}s\n")
            report.append(f"   成功率：{pattern.success_rate:.1%}\n")
            report.append(f"   总执行：{pattern.total_executions} 次\n")
            
            # 优化建议
            suggestions = self.get_optimization_suggestions(task_type)
            report.append(f"   建议：{suggestions[0]}\n")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)


# 全局单例
_learner = None

def get_learner() -> PatternLearner:
    """获取全局模式学习器实例"""
    global _learner
    if _learner is None:
        _learner = PatternLearner()
    return _learner


# 使用示例
if __name__ == "__main__":
    learner = PatternLearner()
    
    # 分析模式
    patterns = learner.analyze_patterns(days=7)
    
    print(f"✅ 已分析 {len(patterns)} 种任务类型")
    
    # 生成报告
    report = learner.generate_report(days=7)
    print(report)
