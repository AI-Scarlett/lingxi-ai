#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 性能和 Tokens 监控

功能:
1. 记录每次请求的响应时间和 Tokens 消耗
2. 按渠道统计性能数据
3. 生成日报/周报
4. 定时发送汇报
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# 监控数据路径
MONITOR_DIR = Path("/root/.openclaw/workspace/.learnings/performance")
MONITOR_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class PerformanceRecord:
    """性能记录"""
    timestamp: str
    channel: str
    user_id: str
    response_time_ms: float
    tokens_in: int
    tokens_out: int
    tokens_total: int
    success: bool
    error: str = None

def log_performance(channel: str, response_time_ms: float, 
                    tokens_in: int = 0, tokens_out: int = 0,
                    success: bool = True, error: str = None,
                    user_id: str = "unknown"):
    """记录性能数据"""
    record = PerformanceRecord(
        timestamp=datetime.now().isoformat(),
        channel=channel,
        user_id=user_id,
        response_time_ms=response_time_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        tokens_total=tokens_in + tokens_out,
        success=success,
        error=error
    )
    
    # 写入日志文件
    log_file = MONITOR_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    
    return record

def get_today_stats() -> Dict:
    """获取今日统计"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = MONITOR_DIR / f"{today}.jsonl"
    
    if not log_file.exists():
        return None
    
    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    
    if not records:
        return None
    
    # 计算统计
    total_requests = len(records)
    success_requests = sum(1 for r in records if r['success'])
    total_tokens = sum(r['tokens_total'] for r in records)
    avg_response_time = sum(r['response_time_ms'] for r in records) / total_requests
    
    # 按渠道统计
    channel_stats = {}
    for record in records:
        channel = record['channel']
        if channel not in channel_stats:
            channel_stats[channel] = {
                'count': 0,
                'total_tokens': 0,
                'total_time': 0
            }
        channel_stats[channel]['count'] += 1
        channel_stats[channel]['total_tokens'] += record['tokens_total']
        channel_stats[channel]['total_time'] += record['response_time_ms']
    
    # 计算平均值
    for channel in channel_stats:
        count = channel_stats[channel]['count']
        channel_stats[channel]['avg_time'] = channel_stats[channel]['total_time'] / count
        channel_stats[channel]['avg_tokens'] = channel_stats[channel]['total_tokens'] / count
    
    return {
        'date': today,
        'total_requests': total_requests,
        'success_requests': success_requests,
        'success_rate': f"{success_requests/total_requests*100:.1f}%",
        'total_tokens': total_tokens,
        'avg_response_time_ms': f"{avg_response_time:.1f}",
        'channel_stats': channel_stats
    }

def generate_daily_report() -> str:
    """生成日报"""
    stats = get_today_stats()
    
    if not stats:
        return "📊 今日暂无性能数据"
    
    report = f"""📊 **灵犀性能日报** - {stats['date']}

**总体统计**
- 总请求数：{stats['total_requests']}
- 成功请求：{stats['success_requests']} ({stats['success_rate']})
- 总 Tokens 消耗：{stats['total_tokens']:,}
- 平均响应时间：{stats['avg_response_time_ms']}ms

**按渠道统计**"""
    
    for channel, channel_stats in stats['channel_stats'].items():
        report += f"""

**{channel}**
- 请求数：{channel_stats['count']}
- 平均响应：{channel_stats['avg_time']:.1f}ms
- 平均 Tokens: {channel_stats['avg_tokens']:.0f}"""
    
    report += f"""

**优化建议**"""
    
    # 根据数据给出建议
    if float(stats['avg_response_time_ms']) > 500:
        report += "\n- ⚠️ 平均响应时间较长，建议检查 Layer 0 配置"
    
    if stats['total_tokens'] > 100000:
        report += "\n- ⚠️ Tokens 消耗较高，建议优化提示词"
    
    if float(stats['success_rate'].rstrip('%')) < 95:
        report += "\n- ⚠️ 成功率偏低，建议检查错误日志"
    
    report += "\n\n_数据自动生成于 " + datetime.now().strftime('%H:%M') + "_"
    
    return report

def get_weekly_stats() -> Dict:
    """获取周统计"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    total_requests = 0
    total_tokens = 0
    total_time = 0
    
    for i in range(7):
        date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
        log_file = MONITOR_DIR / f"{date}.jsonl"
        
        if not log_file.exists():
            continue
        
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                total_requests += 1
                total_tokens += record['tokens_total']
                total_time += record['response_time_ms']
    
    if total_requests == 0:
        return None
    
    return {
        'week_start': week_start.strftime('%Y-%m-%d'),
        'total_requests': total_requests,
        'total_tokens': total_tokens,
        'avg_response_time_ms': total_time / total_requests,
        'avg_daily_requests': total_requests / 7
    }

def generate_weekly_report() -> str:
    """生成周报"""
    stats = get_weekly_stats()
    
    if not stats:
        return "📊 本周暂无性能数据"
    
    report = f"""📊 **灵犀性能周报** - {stats['week_start']} 起

**本周统计**
- 总请求数：{stats['total_requests']:,}
- 日均请求：{stats['avg_daily_requests']:.0f}
- 总 Tokens 消耗：{stats['total_tokens']:,}
- 平均响应时间：{stats['avg_response_time_ms']:.1f}ms

**趋势分析**"""
    
    # 简单趋势分析
    if stats['avg_response_time_ms'] < 100:
        report += "\n- ✅ 响应速度优秀"
    elif stats['avg_response_time_ms'] < 500:
        report += "\n- 👍 响应速度良好"
    else:
        report += "\n- ⚠️ 响应速度有待提升"
    
    if stats['total_tokens'] < 500000:
        report += "\n- ✅ Tokens 消耗合理"
    else:
        report += "\n- ⚠️ Tokens 消耗较高，建议优化"
    
    report += f"""

**优化建议**
1. 检查 Layer 0 技能配置，提升快速响应命中率
2. 优化提示词，减少不必要的 Tokens 消耗
3. 监控错误日志，及时处理异常情况

_数据自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    return report

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 灵犀性能监控测试")
    print("=" * 60)
    
    # 测试记录
    print("\n📝 测试记录性能数据...")
    log_performance("qqbot", 5.2, 100, 50, True, user_id="test_user")
    log_performance("qqbot", 850.3, 2000, 1500, True, user_id="test_user")
    log_performance("feishu", 320.1, 1000, 800, True, user_id="test_user")
    print("✅ 记录完成")
    
    # 测试日报
    print("\n📋 生成今日报告...")
    report = generate_daily_report()
    print(report)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
