#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 性能主动监控系统 v2.8.5

目标：主动发现性能问题，提前预警
1. 实时监控关键指标
2. 对比基线发现异常
3. 主动告警和推荐优化
4. 生成性能趋势报告
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import deque

# ==================== 配置 ====================

@dataclass
class MonitorConfig:
    """监控配置"""
    baseline_window_hours: int = 24  # 基线窗口（24 小时）
    alert_window_minutes: int = 5  # 告警窗口（5 分钟）
    latency_threshold_multiplier: float = 1.5  # 延迟阈值（基线的 1.5 倍）
    error_rate_threshold: float = 0.1  # 错误率阈值（10%）
    check_interval_seconds: int = 60  # 检查间隔（60 秒）

# ==================== 性能指标 ====================

@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    request_count: int
    error_count: int
    error_rate: float
    fast_response_rate: float
    cache_hit_rate: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "avg_latency_ms": self.avg_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "fast_response_rate": self.fast_response_rate,
            "cache_hit_rate": self.cache_hit_rate
        }

# ==================== 性能监控器 ====================

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.config = MonitorConfig()
        self.metrics_history = deque(maxlen=1000)  # 保留最近 1000 个数据点
        self.baseline = None
        self.alerts = []
        self.stats_file = Path.home() / ".openclaw" / "workspace" / ".learnings" / "performance_stats.json"
        
        # 加载历史数据
        self._load_history()
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        self.metrics_history.append(metrics)
        
        # 检查异常
        self._check_anomalies(metrics)
        
        # 定期保存
        if len(self.metrics_history) % 10 == 0:
            self._save_history()
    
    def _check_anomalies(self, current: PerformanceMetrics):
        """检查性能异常"""
        if not self.baseline:
            return
        
        alerts = []
        
        # 1. 检查延迟异常
        if current.avg_latency_ms > self.baseline["avg_latency_ms"] * self.config.latency_threshold_multiplier:
            alerts.append({
                "type": "high_latency",
                "severity": "warning",
                "message": f"⚠️  响应时间异常：{current.avg_latency_ms:.1f}ms (基线：{self.baseline['avg_latency_ms']:.1f}ms)",
                "suggestion": "检查系统负载、网络连接、或考虑优化慢查询"
            })
        
        # 2. 检查错误率异常
        if current.error_rate > self.config.error_rate_threshold:
            alerts.append({
                "type": "high_error_rate",
                "severity": "critical",
                "message": f"🚨 错误率过高：{current.error_rate*100:.1f}% (阈值：{self.config.error_rate_threshold*100:.0f}%)",
                "suggestion": "立即检查错误日志，可能是系统故障或依赖服务问题"
            })
        
        # 3. 检查快速响应率下降
        if self.baseline["fast_response_rate"] and current.fast_response_rate < self.baseline["fast_response_rate"] * 0.8:
            alerts.append({
                "type": "low_fast_response",
                "severity": "warning",
                "message": f"⚠️  快速响应率下降：{current.fast_response_rate*100:.1f}% (基线：{self.baseline['fast_response_rate']*100:.1f}%)",
                "suggestion": "检查 Layer 0 规则是否生效，或缓存是否失效"
            })
        
        # 添加告警
        for alert in alerts:
            if not self._is_duplicate_alert(alert):
                alert["timestamp"] = datetime.now().isoformat()
                self.alerts.append(alert)
                self._send_alert(alert)
    
    def _is_duplicate_alert(self, alert: Dict) -> bool:
        """检查是否是重复告警"""
        if not self.alerts:
            return False
        
        last_alert = self.alerts[-1]
        return (last_alert["type"] == alert["type"] and 
                datetime.fromisoformat(last_alert["timestamp"]) > datetime.now() - timedelta(minutes=5))
    
    def _send_alert(self, alert: Dict):
        """发送告警"""
        print(f"\n{alert['message']}")
        print(f"   建议：{alert['suggestion']}\n")
    
    def calculate_baseline(self, hours: int = 24, use_ewma: bool = True) -> Dict:
        """计算性能基线（支持 EWMA 指数加权移动平均）"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]
        
        if not recent_metrics:
            return {}
        
        if use_ewma:
            # EWMA 指数加权移动平均（新数据权重更高）
            alpha = 0.3  # 平滑系数：0.3 = 新数据占 30% 权重
            
            # 初始化
            ewma_latency = recent_metrics[0].avg_latency_ms
            ewma_error = recent_metrics[0].error_rate
            ewma_fast = recent_metrics[0].fast_response_rate
            
            # 迭代计算 EWMA
            for m in recent_metrics[1:]:
                ewma_latency = alpha * m.avg_latency_ms + (1 - alpha) * ewma_latency
                ewma_error = alpha * m.error_rate + (1 - alpha) * ewma_error
                ewma_fast = alpha * m.fast_response_rate + (1 - alpha) * ewma_fast
            
            avg_latency = ewma_latency
            avg_error_rate = ewma_error
            avg_fast_response = ewma_fast
        else:
            # 简单平均
            avg_latency = sum(m.avg_latency_ms for m in recent_metrics) / len(recent_metrics)
            avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
            avg_fast_response = sum(m.fast_response_rate for m in recent_metrics) / len(recent_metrics)
        
        self.baseline = {
            "avg_latency_ms": avg_latency,
            "avg_error_rate": avg_error_rate,
            "fast_response_rate": avg_fast_response,
            "calculated_at": datetime.now().isoformat(),
            "sample_count": len(recent_metrics),
            "method": "ewma" if use_ewma else "simple"
        }
        
        return self.baseline
    
    def get_current_status(self) -> Dict:
        """获取当前性能状态"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        
        status = "healthy"
        issues = []
        
        if self.baseline:
            if latest.avg_latency_ms > self.baseline["avg_latency_ms"] * self.config.latency_threshold_multiplier:
                status = "degraded"
                issues.append("高延迟")
            
            if latest.error_rate > self.config.error_rate_threshold:
                status = "critical"
                issues.append("高错误率")
        
        return {
            "status": status,
            "issues": issues,
            "metrics": latest.to_dict(),
            "baseline": self.baseline
        }
    
    def _load_history(self):
        """加载历史记录"""
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text(encoding='utf-8'))
                self.baseline = data.get("baseline")
                # 恢复最近的指标
                for m in data.get("recent_metrics", [])[-10:]:
                    self.metrics_history.append(PerformanceMetrics(**m))
            except:
                pass
    
    def _save_history(self):
        """保存历史记录"""
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "baseline": self.baseline,
            "recent_metrics": [m.to_dict() for m in list(self.metrics_history)[-100:]],
            "last_updated": datetime.now().isoformat()
        }
        
        self.stats_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "metrics_count": len(self.metrics_history),
            "alerts_count": len(self.alerts),
            "has_baseline": self.baseline is not None,
            "baseline": self.baseline
        }

# ==================== 性能报告生成器 ====================

class PerformanceReportGenerator:
    """性能报告生成器"""
    
    def generate_daily_report(self, monitor: PerformanceMonitor) -> str:
        """生成日报"""
        now = datetime.now()
        
        # 获取今天的数据
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_metrics = [
            m for m in monitor.metrics_history
            if datetime.fromisoformat(m.timestamp) >= today_start
        ]
        
        if not today_metrics:
            return "今日暂无性能数据"
        
        # 计算统计
        avg_latency = sum(m.avg_latency_ms for m in today_metrics) / len(today_metrics)
        avg_error_rate = sum(m.error_rate for m in today_metrics) / len(today_metrics)
        total_requests = sum(m.request_count for m in today_metrics)
        
        report = f"""# 📊 灵犀性能日报

**日期**: {now.strftime('%Y-%m-%d')}  
**生成时间**: {now.strftime('%H:%M')}

---

## 📈 今日概览

- **总请求数**: {total_requests}
- **平均响应时间**: {avg_latency:.1f}ms
- **平均错误率**: {avg_error_rate*100:.2f}%
- **数据点数**: {len(today_metrics)}

---

## 🎯 性能状态

"""
        
        # 添加性能状态
        status = monitor.get_current_status()
        status_emoji = {"healthy": "✅", "degraded": "⚠️", "critical": "🚨"}.get(status["status"], "❓")
        report += f"**当前状态**: {status_emoji} {status['status'].upper()}\n"
        
        if status["issues"]:
            report += f"\n**问题**: {', '.join(status['issues'])}\n"
        
        # 添加基线对比
        if monitor.baseline:
            report += f"""
---

## 📊 基线对比

- **基线延迟**: {monitor.baseline['avg_latency_ms']:.1f}ms
- **当前延迟**: {avg_latency:.1f}ms
- **偏差**: {((avg_latency / monitor.baseline['avg_latency_ms']) - 1) * 100:+.1f}%

"""
        
        # 添加告警摘要
        if monitor.alerts:
            today_alerts = [
                a for a in monitor.alerts
                if datetime.fromisoformat(a["timestamp"]).date() == today.date()
            ]
            if today_alerts:
                report += f"""
---

## 🚨 今日告警

共 {len(today_alerts)} 次告警

"""
                for alert in today_alerts[:5]:
                    report += f"- {alert['message']}\n"
        
        report += "\n---\n*本报告由灵犀 Performance Monitor 自动生成*\n"
        
        return report
    
    def save_report(self, report: str):
        """保存报告"""
        reports_dir = Path.home() / ".openclaw" / "workspace" / ".learnings" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"performance_{datetime.now().strftime('%Y%m%d')}.md"
        report_path = reports_dir / filename
        
        report_path.write_text(report, encoding='utf-8')
        print(f"📄 性能报告已保存：{report_path}")

# ==================== 全局实例 ====================

_performance_monitor: Optional[PerformanceMonitor] = None
_report_generator: Optional[PerformanceReportGenerator] = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def get_report_generator() -> PerformanceReportGenerator:
    """获取报告生成器实例"""
    global _report_generator
    if _report_generator is None:
        _report_generator = PerformanceReportGenerator()
    return _report_generator

# ==================== 测试入口 ====================

async def main():
    """测试入口"""
    print("=" * 60)
    print("📊 灵犀性能监控系统测试")
    print("=" * 60)
    
    monitor = get_performance_monitor()
    
    # 模拟一些指标
    print("\n1️⃣ 模拟性能指标...")
    for i in range(10):
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            avg_latency_ms=30 + i * 2,
            p95_latency_ms=50 + i * 3,
            p99_latency_ms=100 + i * 5,
            request_count=100,
            error_count=2 if i > 7 else 0,
            error_rate=0.02 if i > 7 else 0,
            fast_response_rate=0.65,
            cache_hit_rate=0.3
        )
        monitor.record_metrics(metrics)
    
    # 计算基线
    print("\n2️⃣ 计算基线...")
    baseline = monitor.calculate_baseline(hours=1)
    print(f"   基线延迟：{baseline.get('avg_latency_ms', 'N/A')}ms")
    
    # 获取状态
    print("\n3️⃣ 当前状态...")
    status = monitor.get_current_status()
    print(f"   状态：{status['status']}")
    if status['issues']:
        print(f"   问题：{', '.join(status['issues'])}")
    
    # 生成报告
    print("\n4️⃣ 生成报告...")
    generator = get_report_generator()
    report = generator.generate_daily_report(monitor)
    generator.save_report(report)
    
    # 统计信息
    print("\n5️⃣ 统计信息...")
    stats = monitor.get_statistics()
    print(f"   指标数量：{stats['metrics_count']}")
    print(f"   告警数量：{stats['alerts_count']}")
    print(f"   基线状态：{'已计算' if stats['has_baseline'] else '未计算'}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
