#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 增强模块 - v2.0

新增功能：
1. 时间维度切换（今日/昨日/7 天/所有）
2. 实时监控（任务队列/系统负载）
3. 多渠道统计
4. 性能指标
"""

import time
import json
from pathlib import Path
from typing import Dict, List
import sqlite3


class DashboardStats:
    """Dashboard 统计数据生成器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_time_range_stats(self, time_range: str = "today") -> Dict:
        """
        获取指定时间范围的统计数据
        
        Args:
            time_range: today/yesterday/week/month/all
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 计算时间范围
        now = time.time()
        if time_range == "today":
            start = now - (now % 86400)  # 今日 0 点
        elif time_range == "yesterday":
            start = now - (now % 86400) - 86400
            end = start + 86400
        elif time_range == "week":
            start = now - 7 * 86400
        elif time_range == "month":
            start = now - 30 * 86400
        else:  # all
            start = 0
        
        # 基础统计
        if time_range == "yesterday":
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
                    SUM(llm_tokens_in) as tokens_in,
                    SUM(llm_tokens_out) as tokens_out,
                    SUM(llm_cost) as cost,
                    AVG(execution_time_ms) as avg_time
                FROM tasks
                WHERE created_at BETWEEN ? AND ?
            """, [start, end])
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
                    SUM(llm_tokens_in) as tokens_in,
                    SUM(llm_tokens_out) as tokens_out,
                    SUM(llm_cost) as cost,
                    AVG(execution_time_ms) as avg_time
                FROM tasks
                WHERE created_at > ?
            """, [start])
        
        row = cursor.fetchone()
        
        stats = {
            "total_tasks": row["total_tasks"] or 0,
            "completed": row["completed"] or 0,
            "failed": row["failed"] or 0,
            "success_rate": (row["completed"] or 0) / max(1, row["total_tasks"] or 1) * 100,
            "tokens_in": row["tokens_in"] or 0,
            "tokens_out": row["tokens_out"] or 0,
            "total_tokens": (row["tokens_in"] or 0) + (row["tokens_out"] or 0),
            "cost": round(row["cost"] or 0, 4),
            "avg_time_ms": round(row["avg_time"] or 0, 0)
        }
        
        # 渠道分布
        if time_range == "yesterday":
            cursor.execute("""
                SELECT channel, COUNT(*) as count 
                FROM tasks 
                WHERE created_at BETWEEN ? AND ?
                GROUP BY channel
            """, [start, end])
        else:
            cursor.execute("""
                SELECT channel, COUNT(*) as count 
                FROM tasks 
                WHERE created_at > ?
                GROUP BY channel
            """, [start])
        
        stats["channels"] = {
            row["channel"]: row["count"] 
            for row in cursor.fetchall()
        }
        
        # 模型分布
        if time_range == "yesterday":
            cursor.execute("""
                SELECT llm_model, COUNT(*) as count 
                FROM tasks 
                WHERE created_at BETWEEN ? AND ? AND llm_model != ''
                GROUP BY llm_model
            """, [start, end])
        else:
            cursor.execute("""
                SELECT llm_model, COUNT(*) as count 
                FROM tasks 
                WHERE created_at > ? AND llm_model != ''
                GROUP BY llm_model
            """, [start])
        
        stats["models"] = {
            row["llm_model"] or "unknown": row["count"] 
            for row in cursor.fetchall()
        }
        
        conn.close()
        
        return stats
    
    def get_realtime_stats(self) -> Dict:
        """获取实时统计（最近 5 分钟）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = time.time()
        five_min_ago = now - 300
        
        # 最近 5 分钟统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed
            FROM tasks
            WHERE created_at > ?
        """, [five_min_ago])
        
        row = cursor.fetchone()
        
        stats = {
            "recent_5min": {
                "total": row["total"] or 0,
                "completed": row["completed"] or 0,
                "rate": (row["completed"] or 0) / max(1, row["total"] or 1) * 60  # 每分钟任务数
            },
            "timestamp": now
        }
        
        conn.close()
        
        return stats
    
    def compare_periods(self, period1: str = "today", period2: str = "yesterday") -> Dict:
        """对比两个时间段的数据"""
        stats1 = self.get_time_range_stats(period1)
        stats2 = self.get_time_range_stats(period2)
        
        comparison = {
            "period1": {
                "name": period1,
                "stats": stats1
            },
            "period2": {
                "name": period2,
                "stats": stats2
            },
            "changes": {
                "tasks": {
                    "absolute": stats1["total_tasks"] - stats2["total_tasks"],
                    "percent": ((stats1["total_tasks"] - stats2["total_tasks"]) / max(1, stats2["total_tasks"])) * 100
                },
                "tokens": {
                    "absolute": stats1["total_tokens"] - stats2["total_tokens"],
                    "percent": ((stats1["total_tokens"] - stats2["total_tokens"]) / max(1, stats2["total_tokens"])) * 100
                },
                "cost": {
                    "absolute": stats1["cost"] - stats2["cost"],
                    "percent": ((stats1["cost"] - stats2["cost"]) / max(0.001, stats2["cost"])) * 100
                },
                "success_rate": {
                    "absolute": stats1["success_rate"] - stats2["success_rate"],
                    "percent": stats1["success_rate"] - stats2["success_rate"]
                }
            }
        }
        
        return comparison


class SystemMonitor:
    """系统监控"""
    
    def __init__(self):
        pass
    
    def get_system_health(self) -> Dict:
        """获取系统健康状态"""
        import os
        import psutil
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        
        # 磁盘使用
        disk = psutil.disk_usage("/")
        
        # 进程数
        process_count = len(psutil.pids())
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
            },
            "memory": {
                "percent": memory.percent,
                "available_mb": memory.available / 1024 / 1024,
                "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            },
            "disk": {
                "percent": disk.percent,
                "free_gb": disk.free / 1024 / 1024 / 1024,
                "status": "healthy" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
            },
            "processes": process_count,
            "overall_status": "healthy" if all([
                cpu_percent < 80,
                memory.percent < 80,
                disk.percent < 80
            ]) else "warning"
        }
    
    def get_task_queue_stats(self, queue) -> Dict:
        """获取任务队列统计"""
        if hasattr(queue, 'get_stats'):
            return queue.get_stats()
        
        return {
            "running": 0,
            "pending": 0,
            "completed": 0,
            "failed": 0
        }


# 便捷函数
def get_dashboard_stats(db_path: str, time_range: str = "today") -> Dict:
    """获取 Dashboard 统计数据"""
    stats_gen = DashboardStats(db_path)
    
    return {
        "time_range": time_range,
        "stats": stats_gen.get_time_range_stats(time_range),
        "realtime": stats_gen.get_realtime_stats(),
        "comparison": stats_gen.compare_periods(time_range, "yesterday")
    }


def get_system_monitor() -> SystemMonitor:
    """获取系统监控器"""
    return SystemMonitor()
