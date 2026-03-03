#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务日志记录器 - Task Logger
记录所有任务执行数据，为智能学习提供数据基础 💋

功能：
- 记录任务执行日志
- 结构化存储（JSONL 格式）
- 按日期分文件
- 支持查询和统计
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

@dataclass
class TaskLog:
    """任务执行日志"""
    task_id: str                    # 任务唯一 ID
    task_type: str                  # 任务类型（content_creation, image_generation, etc.）
    user_id: str                    # 用户 ID
    input_text: str                 # 用户输入
    output_text: str                # 执行结果
    model_used: str                 # 使用的模型
    token_cost: int                 # Token 消耗
    duration_ms: float              # 执行耗时（毫秒）
    success: bool                   # 是否成功
    timestamp: str                  # 时间戳（ISO 格式）
    platform: str = "qqbot"         # 平台来源
    feedback: Optional[str] = None  # 用户反馈
    metadata: Optional[Dict] = None # 额外元数据
    
    def __post_init__(self):
        """后处理：确保 timestamp 是字符串"""
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()


class TaskLogger:
    """任务日志记录器"""
    
    def __init__(self, log_path: str = "~/.openclaw/workspace/task-logs/"):
        self.log_path = Path(log_path).expanduser()
        self.log_path.mkdir(parents=True, exist_ok=True)
        self._cache = {}  # 简单的内存缓存
    
    def _generate_task_id(self, input_text: str, timestamp: str) -> str:
        """生成任务唯一 ID"""
        content = f"{input_text}{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def log(self, 
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
        timestamp = datetime.now().isoformat()
        task_id = self._generate_task_id(input_text, timestamp)
        
        log = TaskLog(
            task_id=task_id,
            task_type=task_type,
            user_id=user_id,
            input_text=input_text,
            output_text=output_text,
            model_used=model_used,
            token_cost=token_cost,
            duration_ms=duration_ms,
            success=success,
            timestamp=timestamp,
            platform="qqbot",
            feedback=feedback,
            metadata=metadata
        )
        
        # 写入文件
        self._write_log(log)
        
        # 更新缓存
        self._update_cache(log)
        
        return task_id
    
    def _write_log(self, log: TaskLog):
        """写入日志到文件（按日期分文件）"""
        date_str = log.timestamp[:10]  # YYYY-MM-DD
        log_file = self.log_path / f"{date_str}.jsonl"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(log), ensure_ascii=False) + "\n")
    
    def _update_cache(self, log: TaskLog):
        """更新内存缓存（最近 100 条）"""
        if len(self._cache) >= 100:
            # 移除最旧的一条
            oldest_key = min(self._cache.keys())
            del self._cache[oldest_key]
        
        self._cache[log.timestamp] = log
    
    def get_logs(self, 
                 start_date: str, 
                 end_date: str,
                 task_type: Optional[str] = None,
                 user_id: Optional[str] = None) -> List[TaskLog]:
        """
        获取日志
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            task_type: 任务类型过滤
            user_id: 用户 ID 过滤
            
        Returns:
            日志列表
        """
        logs = []
        
        # 遍历日期范围内的所有文件
        current = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            log_file = self.log_path / f"{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        
                        # 过滤
                        if task_type and data.get("task_type") != task_type:
                            continue
                        if user_id and data.get("user_id") != user_id:
                            continue
                        
                        logs.append(TaskLog(**data))
            
            # 下一天
            from datetime import timedelta
            current += timedelta(days=1)
        
        return logs
    
    def get_stats(self, 
                  start_date: str, 
                  end_date: str) -> Dict[str, Any]:
        """
        获取统计数据
        
        Returns:
            统计字典
        """
        logs = self.get_logs(start_date, end_date)
        
        if not logs:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "avg_token_cost": 0,
                "task_types": {}
            }
        
        # 计算统计
        total = len(logs)
        success_count = sum(1 for log in logs if log.success)
        total_duration = sum(log.duration_ms for log in logs)
        total_tokens = sum(log.token_cost for log in logs)
        
        # 按任务类型统计
        task_types = {}
        for log in logs:
            ttype = log.task_type
            if ttype not in task_types:
                task_types[ttype] = {"count": 0, "success": 0}
            task_types[ttype]["count"] += 1
            if log.success:
                task_types[ttype]["success"] += 1
        
        return {
            "total_tasks": total,
            "success_count": success_count,
            "success_rate": success_count / total if total > 0 else 0,
            "avg_duration_ms": total_duration / total if total > 0 else 0,
            "avg_token_cost": total_tokens / total if total > 0 else 0,
            "task_types": task_types
        }
    
    def get_recent_logs(self, limit: int = 10) -> List[TaskLog]:
        """获取最近的日志"""
        # 从缓存获取
        sorted_logs = sorted(self._cache.values(), key=lambda x: x.timestamp, reverse=True)
        return sorted_logs[:limit]


# 全局单例
_logger = None

def get_logger() -> TaskLogger:
    """获取全局日志记录器实例"""
    global _logger
    if _logger is None:
        _logger = TaskLogger()
    return _logger


# 使用示例
if __name__ == "__main__":
    logger = TaskLogger()
    
    # 记录一个任务
    task_id = logger.log(
        task_type="content_creation",
        user_id="test_user",
        input_text="帮我写个小红书文案",
        output_text="文案内容...",
        model_used="qwen-plus",
        token_cost=500,
        duration_ms=1200,
        success=True
    )
    
    print(f"✅ 任务日志已记录：{task_id}")
    
    # 获取统计
    today = datetime.now().strftime("%Y-%m-%d")
    stats = logger.get_stats(today, today)
    print(f"📊 今日统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")
