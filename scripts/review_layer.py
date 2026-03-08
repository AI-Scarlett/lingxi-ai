#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 质量审核层 (QA Review Layer)

功能:
1. 审核任务输出质量
2. 支持驳回重做
3. 质量检查清单
4. 新旧版本兼容

使用方式:
    from review_layer import ReviewLayer, ReviewResult
    
    review = ReviewLayer()
    result = review.review(task_output, quality_threshold=0.8)
    
    if result.should_reject:
        # 打回重做
        return {"action": "reject", "reason": result.reason}
    else:
        # 通过
        return {"action": "approve"}
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ==================== 数据结构 ====================

class ReviewStatus(Enum):
    """审核状态"""
    APPROVED = "approved"  # 通过
    REJECTED = "rejected"  # 驳回
    NEEDS_REVIEW = "needs_review"  # 需要人工审核

@dataclass
class ReviewResult:
    """审核结果"""
    status: ReviewStatus
    score: float  # 质量分数 0-1
    reason: str  # 审核意见
    suggestions: List[str] = field(default_factory=list)  # 改进建议
    should_reject: bool = False  # 是否应该驳回
    auto_approved: bool = False  # 是否自动通过（旧版本兼容）
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "score": self.score,
            "reason": self.reason,
            "suggestions": self.suggestions,
            "should_reject": self.should_reject,
            "auto_approved": self.auto_approved
        }

# ==================== 质量检查清单 ====================

class QualityChecker:
    """质量检查器"""
    
    # 通用检查项
    COMMON_CHECKS = [
        ("内容完整性", lambda x: len(x) > 10, "内容太短，可能不完整"),
        ("无乱码", lambda x: not re.search(r'[^\x00-\x7F\u4e00-\u9fff]', x) or len(x) < 100, "包含乱码或特殊字符"),
        ("无占位符", lambda x: "xxx" not in x.lower() and "{{" not in x, "包含未替换的占位符"),
        ("逻辑连贯", lambda x: x.count("但是") <= x.count("因为") + 2, "逻辑可能不连贯"),
    ]
    
    # 文案类检查
    COPYWRITING_CHECKS = [
        ("有标题", lambda x: len(x.split("\n")[0]) < 50, "缺少标题或标题过长"),
        ("有 emoji", lambda x: any(ord(c) > 127 for c in x), "缺少 emoji 点缀"),
        ("有分段", lambda x: "\n" in x, "缺少分段，阅读体验差"),
        ("有行动号召", lambda x: any(kw in x for kw in ["快来", "立即", "马上", "点击", "关注"]), "缺少行动号召"),
    ]
    
    # 代码类检查
    CODE_CHECKS = [
        ("语法正确", lambda x: not re.search(r'[{}()\[\]]', x).group() if re.search(r'[{}()\[\]]', x) else True, "代码语法可能错误"),
        ("有注释", lambda x: "#" in x or "//" in x or "/*" in x, "缺少代码注释"),
        ("无硬编码", lambda x: "TODO" not in x and "FIXME" not in x, "包含待修复标记"),
    ]
    
    # 数据分析类检查
    ANALYSIS_CHECKS = [
        ("有数据支撑", lambda x: any(c.isdigit() for c in x), "缺少数据支撑"),
        ("有结论", lambda x: any(kw in x for kw in ["总结", "结论", "因此", "所以"]), "缺少明确结论"),
        ("有建议", lambda x: any(kw in x for kw in ["建议", "应该", "可以", "推荐"]), "缺少行动建议"),
    ]
    
    @classmethod
    def check(cls, content: str, content_type: str = "general") -> Tuple[float, List[str]]:
        """
        检查内容质量
        
        Returns:
            (score, issues)
        """
        issues = []
        passed = 0
        total = 0
        
        # 通用检查
        for name, check_fn, msg in cls.COMMON_CHECKS:
            total += 1
            try:
                if check_fn(content):
                    passed += 1
                else:
                    issues.append(f"❌ {name}: {msg}")
            except Exception as e:
                # 容错处理
                issues.append(f"⚠️ {name}: 检查失败")
        
        # 类型特定检查
        type_checks = {
            "copywriting": cls.COPYWRITING_CHECKS,
            "code": cls.CODE_CHECKS,
            "analysis": cls.ANALYSIS_CHECKS,
        }
        
        for name, check_fn, msg in type_checks.get(content_type, []):
            total += 1
            try:
                if check_fn(content):
                    passed += 1
                else:
                    issues.append(f"❌ {name}: {msg}")
            except Exception as e:
                # 容错处理
                issues.append(f"⚠️ {name}: 检查失败")
        
        score = passed / total if total > 0 else 1.0
        return score, issues

# ==================== 审核层 ====================

class ReviewLayer:
    """
    质量审核层（QA Review Layer）
    
    功能：
    - 质量检查
    - 自动驳回
    - 改进建议
    - 新旧版本兼容
    """
    
    def __init__(self, auto_review_enabled: bool = True):
        """
        初始化审核层
        
        Args:
            auto_review_enabled: 是否启用自动审核（默认 True）
                               设为 False 时兼容旧版本（不审核直接通过）
        """
        self.auto_review_enabled = auto_review_enabled
        self.default_threshold = 0.6  # 默认通过阈值
        self.reject_threshold = 0.4  # 驳回阈值
        
        # 统计信息
        self.stats = {
            "total_reviews": 0,
            "approved": 0,
            "rejected": 0,
            "auto_approved": 0
        }
    
    def review(self, content: str, content_type: str = "general", 
               quality_threshold: float = None, 
               context: Dict = None) -> ReviewResult:
        """
        审核内容
        
        Args:
            content: 待审核内容
            content_type: 内容类型 (general/copywriting/code/analysis)
            quality_threshold: 通过阈值（默认 0.6）
            context: 上下文信息（用于更精准的审核）
        
        Returns:
            ReviewResult
        """
        # 旧版本兼容：如果不启用审核，直接通过
        if not self.auto_review_enabled:
            self.stats["auto_approved"] += 1
            return ReviewResult(
                status=ReviewStatus.APPROVED,
                score=1.0,
                reason="自动通过（审核层未启用）",
                auto_approved=True
            )
        
        threshold = quality_threshold or self.default_threshold
        self.stats["total_reviews"] += 1
        
        # 1. 质量检查
        score, issues = QualityChecker.check(content, content_type)
        
        # 2. 判断结果
        if score >= threshold:
            # 通过
            self.stats["approved"] += 1
            return ReviewResult(
                status=ReviewStatus.APPROVED,
                score=score,
                reason=f"✅ 质量良好（{score:.1%}），通过审核",
                suggestions=self._generate_suggestions(issues)
            )
        elif score >= self.reject_threshold:
            # 需要改进
            self.stats["approved"] += 1
            return ReviewResult(
                status=ReviewStatus.NEEDS_REVIEW,
                score=score,
                reason=f"⚠️ 质量一般（{score:.1%}），建议优化",
                suggestions=self._generate_suggestions(issues),
                should_reject=False
            )
        else:
            # 驳回
            self.stats["rejected"] += 1
            return ReviewResult(
                status=ReviewStatus.REJECTED,
                score=score,
                reason=f"❌ 质量不达标（{score:.1%}），驳回重做",
                suggestions=self._generate_suggestions(issues),
                should_reject=True
            )
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """生成改进建议"""
        if not issues:
            return ["✨ 内容质量很好，无需改进"]
        
        suggestions = []
        for issue in issues[:5]:  # 最多 5 条建议
            # 将问题转换为建议
            if "缺少" in issue:
                suggestions.append(f"💡 建议：{issue.replace('缺少', '添加')}")
            elif "包含" in issue:
                suggestions.append(f"💡 建议：{issue.replace('包含', '移除')}")
            elif "太" in issue:
                suggestions.append(f"💡 建议：{issue.replace('太', '调整')}")
            else:
                suggestions.append(f"💡 建议：检查{issue.split(':')[0].replace('❌', '').strip()}")
        
        return suggestions
    
    def should_retry(self, result: ReviewResult, retry_count: int = 0) -> bool:
        """判断是否应该重试"""
        if not result.should_reject:
            return False
        
        # 最多重试 3 次
        return retry_count < 3
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["total_reviews"]
        return {
            **self.stats,
            "approval_rate": f"{self.stats['approved']/total*100:.1f}%" if total > 0 else "N/A",
            "avg_score": "计算中..."
        }

# ==================== 全局实例 ====================

_review: Optional[ReviewLayer] = None

def get_review_layer(auto_review_enabled: bool = True) -> ReviewLayer:
    """获取全局实例"""
    global _review
    if _review is None:
        _review = ReviewLayer(auto_review_enabled)
    return _review

def review_content(content: str, content_type: str = "general", 
                   quality_threshold: float = None) -> ReviewResult:
    """便捷函数：审核内容"""
    layer = get_review_layer()
    return layer.review(content, content_type, quality_threshold)

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🏛️ 灵犀门下省审核层测试")
    print("=" * 60)
    
    layer = get_review_layer()
    
    test_cases = [
        ("你好", "general", "短文本"),
        ("这是一篇很好的文章，内容充实，逻辑清晰。", "copywriting", "普通文案"),
        ("🎉 好消息！快来关注，立即行动！", "copywriting", "营销文案"),
        ("# 标题\n\n内容xxx\n\n{{name}}", "copywriting", "有问题文案"),
        ("print('hello')\n# 这是一个测试", "code", "代码"),
        ("数据显示增长 20%，因此建议加大投入。", "analysis", "数据分析"),
    ]
    
    print("\n📋 测试审核结果:\n")
    
    for content, ctype, desc in test_cases:
        result = layer.review(content, ctype)
        print(f"{desc}: '{content[:30]}...'")
        print(f"  状态：{result.status.value}")
        print(f"  分数：{result.score:.1%}")
        print(f"  意见：{result.reason}")
        if result.suggestions:
            print(f"  建议：{result.suggestions[0]}")
        print()
    
    print("\n📊 统计信息:")
    stats = layer.get_stats()
    print(f"  总审核数：{stats['total_reviews']}")
    print(f"  通过率：{stats['approval_rate']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
