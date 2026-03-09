#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 自动学习层 v3.0.2

🧠 核心功能:
- 自动记录高频问题
- 智能识别 Layer 0 候选规则
- 定期自动生成快速响应规则
- 无需手动配置，自我进化

📊 学习策略:
- 连续 7 天统计
- 日均出现 >1 次的问题
- 自动升级为 Layer 0 规则
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


@dataclass
class QueryRecord:
    """查询记录"""
    query: str
    count: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    avg_latency_ms: float = 0.0
    layer0_candidate: bool = False
    auto_generated_response: str = ""


class QueryFrequencyAnalyzer:
    """查询频率分析器"""
    
    def __init__(self, storage_path: str = None, retention_days: int = 30):
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".openclaw" / "workspace" / ".learnings" / "query_logs"
        self.retention_days = retention_days
        self.records: Dict[str, QueryRecord] = {}
        self._load_records()
    
    def _get_date_key(self, timestamp: float = None) -> str:
        """获取日期键 (YYYY-MM-DD)"""
        dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        return dt.strftime("%Y-%m-%d")
    
    def _get_log_file(self, date_key: str = None) -> Path:
        """获取日志文件路径"""
        if not date_key:
            date_key = self._get_date_key()
        return self.storage_path / f"{date_key}.jsonl"
    
    def _load_records(self, days: int = 7):
        """加载最近 N 天的记录"""
        self.records.clear()
        
        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            return
        
        # 加载最近 N 天的数据
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            log_file = self._get_log_file(date_key)
            
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            data = json.loads(line.strip())
                            query = data.get("query", "")
                            
                            if query not in self.records:
                                self.records[query] = QueryRecord(query=query)
                            
                            record = self.records[query]
                            record.count += data.get("count", 1)
                            record.last_seen = max(record.last_seen, data.get("timestamp", time.time()))
                            record.avg_latency_ms = data.get("avg_latency_ms", record.avg_latency_ms)
                except Exception as e:
                    print(f"⚠️ 加载记录失败：{e}")
    
    def record_query(self, query: str, latency_ms: float = 0, layer: str = "passthrough"):
        """记录查询"""
        date_key = self._get_date_key()
        log_file = self._get_log_file(date_key)
        
        # 更新内存记录
        if query not in self.records:
            self.records[query] = QueryRecord(query=query)
        
        record = self.records[query]
        record.count += 1
        record.last_seen = time.time()
        
        # 平滑更新平均延迟
        if record.avg_latency_ms == 0:
            record.avg_latency_ms = latency_ms
        else:
            record.avg_latency_ms = record.avg_latency_ms * 0.9 + latency_ms * 0.1
        
        # 异步写入日志
        self._append_to_log(query, latency_ms, layer)
    
    def _append_to_log(self, query: str, latency_ms: float, layer: str):
        """追加到日志文件"""
        try:
            date_key = self._get_date_key()
            log_file = self._get_log_file(date_key)
            
            entry = {
                "timestamp": time.time(),
                "query": query,
                "count": 1,
                "latency_ms": latency_ms,
                "layer": layer
            }
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 写入日志失败：{e}")
    
    def get_frequent_queries(self, min_days: int = 7, min_daily_avg: float = 1.0) -> List[QueryRecord]:
        """
        获取高频查询
        
        Args:
            min_days: 最少统计天数
            min_daily_avg: 日均最少出现次数
        
        Returns:
            List[QueryRecord]: 符合条件的查询记录
        """
        frequent = []
        now = time.time()
        cutoff = now - (min_days * 24 * 60 * 60)  # N 天前的时间戳
        
        for query, record in self.records.items():
            # 检查时间范围
            if record.first_seen > cutoff:
                # 计算实际天数
                days_active = min(min_days, (now - record.first_seen) / (24 * 60 * 60))
                if days_active < 1:
                    days_active = 1
                
                # 计算日均次数
                daily_avg = record.count / days_active
                
                # 判断是否符合条件
                if daily_avg >= min_daily_avg:
                    record.layer0_candidate = True
                    frequent.append(record)
        
        # 按频率排序
        frequent.sort(key=lambda x: x.count, reverse=True)
        return frequent
    
    def generate_layer0_rule(self, record: QueryRecord) -> Optional[Dict]:
        """
        为高频查询生成 Layer 0 规则
        
        Args:
            record: 查询记录
        
        Returns:
            Dict: Layer 0 规则配置
        """
        query = record.query
        
        # 智能生成响应
        response = self._generate_response(query)
        
        if response:
            return {
                "patterns": [query],
                "response": response,
                "priority": 5,  # 中等优先级
                "auto_generated": True,
                "generated_at": datetime.now().isoformat(),
                "source_query": query,
                "frequency": record.count,
                "daily_avg": record.count / 7  # 假设 7 天
            }
        
        return None
    
    def _generate_response(self, query: str) -> str:
        """
        根据查询类型智能生成响应
        
        策略：
        - 创作类 → 确认 + 询问详情
        - 搜索类 → 确认 + 询问关键词
        - 图像类 → 确认 + 询问画面描述
        - 发布类 → 确认 + 询问平台
        - 分析类 → 确认 + 询问数据
        - 翻译类 → 确认 + 询问语言
        - 开发类 → 确认 + 询问需求
        - 日常对话 → 情感回应
        """
        query_lower = query.lower()
        
        # 创作类
        if any(kw in query_lower for kw in ["写", "创作", "生成文案", "写文章"]):
            return "📝 收到老板！马上为您创作～ 请告诉我具体要写什么？💋"
        
        # 搜索类
        if any(kw in query_lower for kw in ["搜索", "查找", "查询", "搜一下"]):
            return "🔍 搜索专家已启动！老板想找什么信息？📚"
        
        # 图像类
        if any(kw in query_lower for kw in ["图", "图片", "生成图", "画", "自拍"]):
            return "🎨 图像专家准备就绪～ 老板想要什么样的图片？🖼️"
        
        # 发布类
        if any(kw in query_lower for kw in ["发布", "发到", "小红书", "微博", "抖音"]):
            return "📤 发布专家就位～ 要发布到什么平台？📱"
        
        # 分析类
        if any(kw in query_lower for kw in ["分析", "统计", "报表", "数据"]):
            return "📊 数据分析专家启动～ 要分析什么数据？📈"
        
        # 翻译类
        if any(kw in query_lower for kw in ["翻译", "英文", "中文", "译"]):
            return "💬 翻译专家待命～ 要翻译什么内容？🌍"
        
        # 开发类
        if any(kw in query_lower for kw in ["开发", "代码", "程序", "脚本", "功能"]):
            return "💻 开发专家就位～ 具体要实现什么功能？🚀"
        
        # 日常对话类
        if any(kw in query_lower for kw in ["你好", "在吗", "谢谢", "再见"]):
            return "老板好呀～💋 随时待命！"
        
        # 通用响应
        return "👌 收到老板！马上处理～ 还有什么需要？😊"
    
    def get_auto_generated_rules(self, min_days: int = 7, min_daily_avg: float = 1.0) -> List[Dict]:
        """获取自动生成的 Layer 0 规则"""
        frequent = self.get_frequent_queries(min_days, min_daily_avg)
        rules = []
        
        for record in frequent:
            if not record.layer0_candidate:
                continue
            
            rule = self.generate_layer0_rule(record)
            if rule:
                rules.append(rule)
        
        return rules
    
    def cleanup_old_logs(self, keep_days: int = None):
        """清理旧日志"""
        keep_days = keep_days or self.retention_days
        cutoff = datetime.now() - timedelta(days=keep_days)
        
        if not self.storage_path.exists():
            return
        
        for log_file in self.storage_path.glob("*.jsonl"):
            try:
                # 从文件名提取日期
                date_str = log_file.stem  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff:
                    log_file.unlink()
                    print(f"🗑️ 已删除旧日志：{log_file.name}")
            except Exception as e:
                print(f"⚠️ 清理日志失败：{e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_queries = sum(r.count for r in self.records.values())
        candidates = sum(1 for r in self.records.values() if r.layer0_candidate)
        
        return {
            "total_unique_queries": len(self.records),
            "total_query_count": total_queries,
            "layer0_candidates": candidates,
            "storage_path": str(self.storage_path),
            "retention_days": self.retention_days
        }


# ==================== 自动学习器 ====================

class AutoLearner:
    """
    灵犀自动学习器
    
    功能：
    - 记录所有查询
    - 定期分析高频问题
    - 自动生成 Layer 0 规则
    - 支持手动审核或自动应用
    """
    
    def __init__(self, storage_path: str = None):
        self.analyzer = QueryFrequencyAnalyzer(storage_path)
        self.config_path = Path.home() / ".openclaw" / "workspace" / "lingxi-config.json"
        self.auto_apply = False  # 是否自动应用新规则
    
    def record(self, query: str, latency_ms: float = 0, layer: str = "passthrough"):
        """记录查询"""
        self.analyzer.record_query(query, latency_ms, layer)
    
    def analyze_and_generate(self, min_days: int = 7, min_daily_avg: float = 1.0) -> List[Dict]:
        """分析并生成新规则"""
        return self.analyzer.get_auto_generated_rules(min_days, min_daily_avg)
    
    def apply_rules(self, rules: List[Dict], dry_run: bool = True) -> Dict:
        """
        应用新规则
        
        Args:
            rules: 规则列表
            dry_run: 是否仅预览（不实际写入）
        
        Returns:
            Dict: 应用结果
        """
        result = {
            "applied": 0,
            "skipped": 0,
            "errors": 0,
            "rules": []
        }
        
        for rule in rules:
            try:
                if dry_run:
                    result["rules"].append({
                        "status": "preview",
                        "rule": rule
                    })
                    result["applied"] += 1
                else:
                    # TODO: 实际写入 Layer 0 规则文件
                    self._append_to_layer0_file(rule)
                    result["rules"].append({
                        "status": "applied",
                        "rule": rule
                    })
                    result["applied"] += 1
            except Exception as e:
                result["errors"] += 1
                result["rules"].append({
                    "status": "error",
                    "error": str(e),
                    "rule": rule
                })
        
        return result
    
    def _append_to_layer0_file(self, rule: Dict):
        """追加规则到 Layer 0 文件"""
        # TODO: 实现自动写入 fast_response_layer_v2.py
        # 这里先记录到单独的文件
        auto_rules_file = Path.home() / ".openclaw" / "workspace" / ".learnings" / "auto_layer0_rules.jsonl"
        auto_rules_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(auto_rules_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rule, ensure_ascii=False) + "\n")
        
        print(f"✅ 已添加自动规则：{rule['patterns'][0]} → {rule['response'][:30]}...")
    
    def get_learning_report(self) -> str:
        """生成学习报告"""
        stats = self.analyzer.get_stats()
        rules = self.analyze_and_generate()
        
        report = f"""
🧠 灵犀自动学习报告
{'='*50}

📊 统计信息:
   总查询数：{stats['total_query_count']}
   独立查询：{stats['total_unique_queries']}
   Layer 0 候选：{stats['layer0_candidates']}

📈 待学习规则 ({len(rules)} 条):
"""
        
        for i, rule in enumerate(rules[:10], 1):  # 只显示前 10 条
            report += f"\n   {i}. \"{rule['patterns'][0]}\" → {rule['response'][:40]}..."
            report += f" (频次：{rule['frequency']}, 日均：{rule['daily_avg']:.1f})"
        
        if len(rules) > 10:
            report += f"\n   ... 还有 {len(rules) - 10} 条"
        
        report += f"\n\n💡 建议：运行 `python3 scripts/learning_layer.py --apply` 应用新规则"
        
        return report


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀自动学习层")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--report", action="store_true", help="生成学习报告")
    parser.add_argument("--analyze", action="store_true", help="分析并显示候选规则")
    parser.add_argument("--apply", action="store_true", help="应用新规则")
    parser.add_argument("--days", type=int, default=7, help="统计天数 (默认 7)")
    parser.add_argument("--min-daily", type=float, default=1.0, help="日均最少次数 (默认 1.0)")
    parser.add_argument("--cleanup", action="store_true", help="清理旧日志")
    
    args = parser.parse_args()
    
    learner = AutoLearner()
    
    if args.stats:
        stats = learner.analyzer.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.report:
        print(learner.get_learning_report())
    
    elif args.analyze:
        rules = learner.analyze_and_generate(min_days=args.days, min_daily_avg=args.min_daily)
        print(f"\n📈 找到 {len(rules)} 条候选规则:\n")
        for i, rule in enumerate(rules[:20], 1):
            print(f"{i}. \"{rule['patterns'][0]}\"")
            print(f"   响应：{rule['response']}")
            print(f"   频次：{rule['frequency']} | 日均：{rule['daily_avg']:.1f}\n")
    
    elif args.apply:
        print("🔧 应用新规则...")
        rules = learner.analyze_and_generate(min_days=args.days, min_daily_avg=args.min_daily)
        result = learner.apply_rules(rules, dry_run=False)
        print(f"\n✅ 应用完成：{result['applied']} 条成功，{result['errors']} 条失败")
    
    elif args.cleanup:
        print("🗑️ 清理旧日志...")
        learner.analyzer.cleanup_old_logs()
        print("✅ 清理完成")
    
    else:
        # 默认显示报告
        print(learner.get_learning_report())
