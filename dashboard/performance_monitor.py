#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 性能监控模块

功能：
- 实时性能指标（CPU/内存/磁盘）
- 任务执行时间追踪
- Token 消耗实时监控
- 告警和通知
- 性能趋势分析
"""

import time
import psutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import json


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict = None


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.db_path = str(self.workspace / ".lingxi" / "performance.db")
        
        # 指标历史（内存缓存）
        self.metrics_history: Dict[str, deque] = {}
        self.max_history = 1000  # 最多保留 1000 条记录
        
        # 告警阈值
        self.alerts_threshold = {
            "cpu_percent": 80.0,
            "memory_percent": 80.0,
            "disk_percent": 90.0,
            "task_duration": 300.0,  # 5 分钟
            "token_rate": 10000  # 每分钟 10k tokens
        }
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 性能指标表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                value REAL,
                unit TEXT,
                timestamp REAL,
                tags TEXT
            )
        """)
        
        # 告警表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                threshold REAL,
                actual_value REAL,
                timestamp REAL,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp)")
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self) -> Dict[str, PerformanceMetric]:
        """收集系统指标"""
        metrics = {}
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics["cpu_percent"] = PerformanceMetric(
            name="cpu_percent",
            value=cpu_percent,
            unit="%",
            timestamp=time.time(),
            tags={"type": "system"}
        )
        
        # 内存使用
        memory = psutil.virtual_memory()
        metrics["memory_percent"] = PerformanceMetric(
            name="memory_percent",
            value=memory.percent,
            unit="%",
            timestamp=time.time(),
            tags={"type": "system"}
        )
        metrics["memory_available"] = PerformanceMetric(
            name="memory_available",
            value=memory.available / 1024 / 1024,
            unit="MB",
            timestamp=time.time(),
            tags={"type": "system"}
        )
        
        # 磁盘使用
        disk = psutil.disk_usage("/")
        metrics["disk_percent"] = PerformanceMetric(
            name="disk_percent",
            value=disk.percent,
            unit="%",
            timestamp=time.time(),
            tags={"type": "system", "mount": "/"}
        )
        
        # 保存指标
        self._save_metrics(metrics)
        
        # 检查告警
        self._check_alerts(metrics)
        
        return metrics
    
    def track_task_execution(self, task_id: str, duration: float, 
                            tokens_used: int = 0):
        """追踪任务执行"""
        metrics = {
            f"task_{task_id}_duration": PerformanceMetric(
                name="task_duration",
                value=duration,
                unit="s",
                timestamp=time.time(),
                tags={"task_id": task_id}
            ),
            f"task_{task_id}_tokens": PerformanceMetric(
                name="task_tokens",
                value=tokens_used,
                unit="tokens",
                timestamp=time.time(),
                tags={"task_id": task_id}
            )
        }
        
        self._save_metrics(metrics)
    
    def track_token_usage(self, tokens_in: int, tokens_out: int, 
                         model: str = "unknown"):
        """追踪 Token 使用"""
        metrics = {
            "tokens_in": PerformanceMetric(
                name="tokens_in",
                value=tokens_in,
                unit="tokens",
                timestamp=time.time(),
                tags={"model": model}
            ),
            "tokens_out": PerformanceMetric(
                name="tokens_out",
                value=tokens_out,
                unit="tokens",
                timestamp=time.time(),
                tags={"model": model}
            ),
            "tokens_total": PerformanceMetric(
                name="tokens_total",
                value=tokens_in + tokens_out,
                unit="tokens",
                timestamp=time.time(),
                tags={"model": model}
            )
        }
        
        self._save_metrics(metrics)
    
    def _save_metrics(self, metrics: Dict[str, PerformanceMetric]):
        """保存指标到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics.values():
            cursor.execute("""
                INSERT INTO metrics (name, value, unit, timestamp, tags)
                VALUES (?, ?, ?, ?, ?)
            """, [
                metric.name,
                metric.value,
                metric.unit,
                metric.timestamp,
                json.dumps(metric.tags) if metric.tags else None
            ])
            
            # 更新内存缓存
            if metric.name not in self.metrics_history:
                self.metrics_history[metric.name] = deque(maxlen=self.max_history)
            
            self.metrics_history[metric.name].append({
                "value": metric.value,
                "timestamp": metric.timestamp
            })
        
        conn.commit()
        conn.close()
    
    def _check_alerts(self, metrics: Dict[str, PerformanceMetric]):
        """检查告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name, metric in metrics.items():
            threshold = self.alerts_threshold.get(name)
            
            if threshold and metric.value > threshold:
                # 触发告警
                cursor.execute("""
                    INSERT INTO alerts (metric_name, threshold, actual_value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, [name, threshold, metric.value, metric.timestamp])
                
                print(f"⚠️ 告警：{name} = {metric.value:.1f} (阈值：{threshold})")
        
        conn.commit()
        conn.close()
    
    def get_current_metrics(self) -> Dict:
        """获取当前指标"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新指标
        cursor.execute("""
            SELECT name, value, unit, timestamp, tags
            FROM metrics
            WHERE (name, timestamp) IN (
                SELECT name, MAX(timestamp)
                FROM metrics
                GROUP BY name
            )
        """)
        
        metrics = {}
        for row in cursor.fetchall():
            metrics[row["name"]] = {
                "value": row["value"],
                "unit": row["unit"],
                "timestamp": row["timestamp"],
                "tags": json.loads(row["tags"]) if row["tags"] else {}
            }
        
        conn.close()
        return metrics
    
    def get_metrics_trend(self, metric_name: str, 
                         hours: int = 24) -> List[Dict]:
        """获取指标趋势"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = time.time() - (hours * 3600)
        
        cursor.execute("""
            SELECT value, timestamp
            FROM metrics
            WHERE name = ? AND timestamp > ?
            ORDER BY timestamp ASC
        """, [metric_name, cutoff])
        
        trend = [
            {"value": row["value"], "timestamp": row["timestamp"]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return trend
    
    def get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM alerts
            WHERE resolved = FALSE
            ORDER BY timestamp DESC
        """)
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return alerts
    
    def resolve_alert(self, alert_id: int):
        """解决告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts
            SET resolved = TRUE
            WHERE id = ?
        """, [alert_id])
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 指标总数
        cursor.execute("SELECT COUNT(*) FROM metrics")
        stats["total_metrics"] = cursor.fetchone()[0]
        
        # 告警统计
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = FALSE")
        stats["active_alerts"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        stats["total_alerts"] = cursor.fetchone()[0]
        
        # 平均响应时间
        cursor.execute("""
            SELECT AVG(value) FROM metrics
            WHERE name = 'task_duration'
        """)
        stats["avg_task_duration"] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return stats


# 全局监控器
_monitor = None

def get_performance_monitor(workspace_path: str = None) -> PerformanceMonitor:
    """获取性能监控器实例"""
    global _monitor
    
    if _monitor is None:
        workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        _monitor = PerformanceMonitor(workspace)
    
    return _monitor


if __name__ == "__main__":
    # 测试运行
    monitor = get_performance_monitor()
    
    # 收集系统指标
    print("📊 收集系统指标...")
    metrics = monitor.collect_system_metrics()
    
    for name, metric in metrics.items():
        print(f"  {name}: {metric.value:.1f} {metric.unit}")
    
    # 追踪任务执行
    print("\n📝 追踪任务执行...")
    monitor.track_task_execution("test_task", duration=2.5, tokens_used=1000)
    
    # 追踪 Token 使用
    print("\n💰 追踪 Token 使用...")
    monitor.track_token_usage(500, 300, model="qwen3.5-plus")
    
    # 获取当前指标
    print("\n📊 当前指标:")
    current = monitor.get_current_metrics()
    for name, data in current.items():
        print(f"  {name}: {data['value']:.1f} {data['unit']}")
    
    # 获取统计
    print("\n📊 统计:")
    stats = monitor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
