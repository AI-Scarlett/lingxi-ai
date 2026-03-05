#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 学习层自动 Review 系统 v2.8.5

目标：让 AI 主动学习，不需要人工 Review
1. 自动分析错误模式
2. 自动提炼通用经验
3. 自动更新核心记忆
4. 生成周报/月报
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import defaultdict

# ==================== 配置 ====================

LEARNINGS_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"

@dataclass
class ReviewConfig:
    """Review 配置"""
    review_interval_days: int = 7  # 每周 Review 一次
    min_error_count: int = 3  # 至少 3 次错误才分析
    confidence_threshold: float = 0.7  # 置信度阈值
    auto_apply: bool = True  # 自动应用修复方案

# ==================== 错误模式分析器 ====================

class ErrorPatternAnalyzer:
    """错误模式分析器"""
    
    def __init__(self):
        self.config = ReviewConfig()
        self.error_clusters = defaultdict(list)
    
    def load_errors(self, days: int = 7) -> List[Dict]:
        """加载最近的错误日志"""
        errors_file = LEARNINGS_DIR / "ERRORS.md"
        if not errors_file.exists():
            return []
        
        errors = []
        content = errors_file.read_text(encoding='utf-8')
        
        # 解析 Markdown 格式的错误日志
        error_blocks = re.split(r'\n## \[', content)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for block in error_blocks[1:]:  # 跳过第一个空块
            try:
                # 提取错误 ID 和时间
                match = re.match(r'(ERR-\d+-\d+)\]\s+(.+?)\s+-\s+(.+?)\n\*\*时间\*\*:\s+(\d{4}-\d{2}-\d{2}T[\d:]+)', block)
                if match:
                    error_id, error_type, status, timestamp_str = match.groups()
                    timestamp = datetime.fromisoformat(timestamp_str)
                    
                    if timestamp >= cutoff_date:
                        errors.append({
                            "id": error_id,
                            "type": error_type,
                            "status": status.strip(),
                            "timestamp": timestamp,
                            "raw": block
                        })
            except Exception as e:
                continue
        
        return errors
    
    def cluster_errors(self, errors: List[Dict]) -> Dict[str, List[Dict]]:
        """聚类相似错误"""
        clusters = defaultdict(list)
        
        for error in errors:
            # 使用 Pattern-Key 聚类
            pattern_key = self._extract_pattern_key(error["raw"])
            clusters[pattern_key].append(error)
        
        # 过滤掉只有 1-2 次的错误
        filtered = {k: v for k, v in clusters.items() if len(v) >= self.config.min_error_count}
        
        return filtered
    
    def _extract_pattern_key(self, raw: str) -> str:
        """从错误日志中提取 Pattern-Key"""
        match = re.search(r'\*\*Pattern-Key\*\*:\s+`([^`]+)`', raw)
        return match.group(1) if match else "unknown"
    
    def analyze_root_cause(self, cluster: List[Dict]) -> Dict[str, Any]:
        """分析根本原因"""
        if not cluster:
            return {}
        
        # 统计错误类型
        type_counts = defaultdict(int)
        for error in cluster:
            type_counts[error["type"]] += 1
        
        most_common_type = max(type_counts, key=type_counts.get)
        
        # 提取共同的上下文特征
        common_context = self._find_common_context(cluster)
        
        # 生成根本原因假设
        root_cause = self._generate_root_cause_hypothesis(most_common_type, common_context)
        
        return {
            "error_type": most_common_type,
            "occurrence_count": len(cluster),
            "common_context": common_context,
            "root_cause": root_cause,
            "confidence": self._calculate_confidence(cluster)
        }
    
    def _find_common_context(self, cluster: List[Dict]) -> Dict:
        """找出共同的上下文特征"""
        contexts = []
        for error in cluster:
            match = re.search(r'```json\n(.+?)\n```', error["raw"], re.DOTALL)
            if match:
                try:
                    context = json.loads(match.group(1))
                    contexts.append(context)
                except:
                    continue
        
        if not contexts:
            return {}
        
        # 找出共同的键值对
        common = {}
        for key in contexts[0].keys():
            values = [c.get(key) for c in contexts if key in c]
            if len(values) == len(contexts) and len(set(str(v) for v in values)) == 1:
                common[key] = values[0]
        
        return common
    
    def _generate_root_cause_hypothesis(self, error_type: str, common_context: Dict) -> str:
        """生成根本原因假设"""
        hypotheses = {
            "Connection Timeout": "网络连接不稳定或 API 响应超时",
            "Execution Error": "任务执行环境配置问题",
            "Permission Error": "权限配置不正确",
            "Memory Error": "内存不足或泄漏",
            "File Error": "文件路径或权限问题"
        }
        
        base_hypothesis = hypotheses.get(error_type, "未知错误类型")
        
        # 根据上下文细化
        if "task" in common_context:
            base_hypothesis += f" (任务类型：{common_context['task']})"
        
        return base_hypothesis
    
    def _calculate_confidence(self, cluster: List[Dict]) -> float:
        """计算分析置信度"""
        count = len(cluster)
        
        # 错误次数越多，置信度越高
        if count >= 10:
            return 0.95
        elif count >= 5:
            return 0.85
        elif count >= 3:
            return 0.7
        else:
            return 0.5

# ==================== 经验提炼器 ====================

class ExperienceExtractor:
    """经验提炼器"""
    
    def __init__(self):
        self.config = ReviewConfig()
    
    def extract_from_cluster(self, cluster_analysis: Dict) -> Optional[Dict]:
        """从错误聚类中提炼经验"""
        if cluster_analysis["occurrence_count"] < self.config.min_error_count:
            return None
        
        root_cause = cluster_analysis["root_cause"]
        error_type = cluster_analysis["error_type"]
        
        # 生成修复建议
        suggestion = self._generate_suggestion(error_type, cluster_analysis["common_context"])
        
        # 生成预防措施
        prevention = self._generate_prevention(error_type)
        
        return {
            "title": f"避免{error_type}的最佳实践",
            "lesson": f"当遇到{root_cause}时，{suggestion}",
            "prevention": prevention,
            "related_errors": cluster_analysis["occurrence_count"],
            "confidence": cluster_analysis["confidence"]
        }
    
    def _generate_suggestion(self, error_type: str, context: Dict) -> str:
        """生成修复建议"""
        suggestions = {
            "Connection Timeout": "增加超时时间、添加重试机制、使用备用 API",
            "Execution Error": "检查环境配置、添加错误处理、实施降级方案",
            "Permission Error": "检查权限配置、使用正确的认证方式",
            "Memory Error": "优化内存使用、添加缓存清理、增加内存限制",
            "File Error": "检查文件路径、确保文件存在、验证权限"
        }
        
        return suggestions.get(error_type, "检查相关配置和日志")
    
    def _generate_prevention(self, error_type: str) -> str:
        """生成预防措施"""
        preventions = {
            "Connection Timeout": "实施连接池、添加健康检查、监控 API 可用性",
            "Execution Error": "添加单元测试、实施监控告警、建立回滚机制",
            "Permission Error": "定期审计权限、使用最小权限原则、自动化权限管理",
            "Memory Error": "实施内存监控、定期重启服务、优化数据结构",
            "File Error": "实施文件监控、添加备份机制、使用绝对路径"
        }
        
        return preventions.get(error_type, "建立标准化流程")

# ==================== 记忆更新器 ====================

class MemoryUpdater:
    """记忆更新器"""
    
    def __init__(self):
        self.memory_file = MEMORY_DIR / "learnings.md"
    
    def update_core_memory(self, experience: Dict) -> bool:
        """更新核心记忆"""
        if not self.memory_file.exists():
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text("# 学习经验\n\n> 自动更新 - 灵犀 v2.8.5\n\n")
        
        # 检查是否已存在相似经验
        if self._is_duplicate(experience):
            print(f"⚠️  经验已存在，跳过：{experience['title']}")
            return False
        
        # 添加到记忆文件
        entry = self._format_memory_entry(experience)
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"✅ 核心记忆已更新：{experience['title']}")
        return True
    
    def _is_duplicate(self, experience: Dict) -> bool:
        """检查是否是重复经验"""
        if not self.memory_file.exists():
            return False
        
        content = self.memory_file.read_text(encoding='utf-8')
        return experience["title"] in content
    
    def _format_memory_entry(self, experience: Dict) -> str:
        """格式化记忆条目"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"""
## {experience['title']}

**更新时间**: {timestamp}  
**相关错误**: {experience['related_errors']} 次  
**置信度**: {experience['confidence']*100:.0f}%

### 经验教训
{experience['lesson']}

### 预防措施
{experience['prevention']}

---
"""

# ==================== 周报生成器 ====================

class WeeklyReportGenerator:
    """周报生成器"""
    
    def generate(self, errors: List[Dict], clusters: Dict, experiences: List[Dict]) -> str:
        """生成周报"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        
        report = f"""# 📊 灵犀学习周报

**报告周期**: {week_start.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}  
**生成时间**: {now.strftime('%Y-%m-%d %H:%M')}

---

## 📈 总体统计

- **错误总数**: {len(errors)} 次
- **错误模式**: {len(clusters)} 种
- **提炼经验**: {len(experiences)} 条
- **自动修复**: {sum(1 for e in experiences if e['confidence'] > 0.8)} 条

---

## 🔴 主要错误模式

"""
        
        # 添加主要错误模式
        for pattern_key, cluster in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            report += f"""### {pattern_key}
- **出现次数**: {len(cluster)} 次
- **错误类型**: {cluster[0]['type']}
- **状态**: {'✅ 已解决' if 'resolved' in cluster[0]['status'].lower() else '❌ 未解决'}

"""
        
        # 添加新提炼的经验
        if experiences:
            report += """## 💡 新提炼的经验

"""
            for exp in experiences[:5]:
                report += f"""### {exp['title']}
{exp['lesson']}

"""
        
        # 添加改进建议
        report += """## 🎯 下周改进建议

"""
        if len(errors) > 10:
            report += "- ⚠️  错误数量较多，建议加强监控\n"
        if len(clusters) > 3:
            report += "- 🔄 错误模式分散，建议统一错误处理\n"
        if experiences:
            report += "- ✅ 已有经验积累，建议应用到生产环境\n"
        
        report += "\n---\n*本报告由灵犀 Learning Layer 自动生成*\n"
        
        return report
    
    def save_report(self, report: str):
        """保存周报"""
        reports_dir = LEARNINGS_DIR / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        filename = f"weekly_{now.strftime('%Y_W%V')}.md"
        report_path = reports_dir / filename
        
        report_path.write_text(report, encoding='utf-8')
        print(f"📄 周报已保存：{report_path}")

# ==================== 自动 Review 主控制器 ====================

class AutoReviewManager:
    """自动 Review 管理器"""
    
    def __init__(self):
        self.config = ReviewConfig()
        self.analyzer = ErrorPatternAnalyzer()
        self.extractor = ExperienceExtractor()
        self.memory_updater = MemoryUpdater()
        self.report_generator = WeeklyReportGenerator()
    
    async def run_review(self, days: int = 7, auto_apply: bool = True) -> Dict[str, Any]:
        """执行自动 Review"""
        print("🧠 开始自动 Review...\n")
        
        # 1. 加载错误日志
        print("1️⃣ 加载错误日志...")
        errors = self.analyzer.load_errors(days=days)
        print(f"   找到 {len(errors)} 个错误\n")
        
        if not errors:
            return {"status": "no_errors", "message": "没有错误日志"}
        
        # 2. 聚类分析
        print("2️⃣ 聚类分析...")
        clusters = self.analyzer.cluster_errors(errors)
        print(f"   发现 {len(clusters)} 个错误模式\n")
        
        if not clusters:
            return {"status": "no_patterns", "message": "没有达到最小聚类阈值"}
        
        # 3. 分析根本原因
        print("3️⃣ 分析根本原因...")
        analyses = {}
        for pattern_key, cluster in clusters.items():
            analysis = self.analyzer.analyze_root_cause(cluster)
            analyses[pattern_key] = analysis
            print(f"   - {pattern_key}: {analysis['root_cause']} (置信度：{analysis['confidence']*100:.0f}%)")
        print()
        
        # 4. 提炼经验
        print("4️⃣ 提炼经验...")
        experiences = []
        for pattern_key, analysis in analyses.items():
            experience = self.extractor.extract_from_cluster(analysis)
            if experience:
                experiences.append(experience)
                print(f"   ✅ 提炼：{experience['title']}")
        print()
        
        # 5. 更新核心记忆
        print("5️⃣ 更新核心记忆...")
        updated_count = 0
        for experience in experiences:
            if auto_apply and experience["confidence"] >= self.config.confidence_threshold:
                if self.memory_updater.update_core_memory(experience):
                    updated_count += 1
        print(f"   更新了 {updated_count} 条记忆\n")
        
        # 6. 生成周报
        print("6️⃣ 生成周报...")
        report = self.report_generator.generate(errors, clusters, experiences)
        self.report_generator.save_report(report)
        print()
        
        # 7. 返回结果
        result = {
            "status": "success",
            "errors_analyzed": len(errors),
            "patterns_found": len(clusters),
            "experiences_extracted": len(experiences),
            "memories_updated": updated_count,
            "analyses": analyses,
            "experiences": experiences
        }
        
        print("✅ 自动 Review 完成！\n")
        return result
    
    def get_statistics(self) -> Dict:
        """获取 Review 统计"""
        return {
            "review_interval_days": self.config.review_interval_days,
            "min_error_count": self.config.min_error_count,
            "auto_apply": self.config.auto_apply
        }

# ==================== 全局实例 ====================

_auto_review_manager: Optional[AutoReviewManager] = None

def get_auto_review_manager() -> AutoReviewManager:
    """获取自动 Review 管理器实例"""
    global _auto_review_manager
    if _auto_review_manager is None:
        _auto_review_manager = AutoReviewManager()
    return _auto_review_manager

# ==================== 测试入口 ====================

async def main():
    """测试入口"""
    print("=" * 60)
    print("🧠 灵犀自动 Review 系统测试")
    print("=" * 60)
    
    manager = get_auto_review_manager()
    
    # 执行 Review
    result = await manager.run_review(days=7, auto_apply=True)
    
    print("\n📊 结果摘要:")
    print(f"   状态：{result.get('status', 'unknown')}")
    print(f"   分析错误：{result.get('errors_analyzed', 0)}")
    print(f"   发现模式：{result.get('patterns_found', 0)}")
    print(f"   提炼经验：{result.get('experiences_extracted', 0)}")
    print(f"   更新记忆：{result.get('memories_updated', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
