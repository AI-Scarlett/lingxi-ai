#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 复杂任务三步法实现
基于"这是我迄今为止开发的最满意的一个技能"文档

Complex Task Three-Step Methodology — A Layered Assessment & Execution Framework

S0: 零成本预筛选 (规则匹配 · 0 token · 过滤 ~80% 消息)
S1: 轻量复杂度评估 (五维打分 · ~300 token)
S2: 深度规划 & 审计 (Plan Mode → Audit Mode → DAG 执行蓝图)
S3: 分阶段执行 & 质量控制 (Phase 并行 · QA 审计 · 缺陷分级)
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# ==================== S0: 零成本预筛选 ====================

@dataclass
class S0Rule:
    """S0 规则"""
    name: str
    pattern: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    min_length: int = 0
    action: str = "pass"  # pass → 直接执行，evaluate → 进入 S1

# S0 白名单 - 直接放行
S0_WHITELIST = [
    S0Rule("单轮问答", keywords=["几点了", "天气", "是什么", "为什么", "怎么"]),
    S0Rule("延续指令", keywords=["继续", "下一步", "然后呢", "还有吗"]),
    S0Rule("简单指令", keywords=["搜索", "发消息", "提醒我", "翻译"]),
    S0Rule("闲聊确认", keywords=["好的", "谢谢", "你好", "在吗", "再见"]),
]

# S0 触发信号 - 进入 S1
S0_TRIGGER_SIGNALS = [
    S0Rule("长度", min_length=200, action="evaluate"),
    S0Rule("意图动词", keywords=["开发", "构建", "设计", "部署", "迁移", "重构", "发布", "创建"], action="evaluate"),
    S0Rule("范围词", keywords=["整个", "全部", "系统", "架构", "从零开始", "完整"], action="evaluate"),
    S0Rule("多步模式", keywords=["先…然后", "首先…其次", "第一步…第二步", "先…再…最后"], action="evaluate"),
    S0Rule("显式触发", keywords=["复杂任务", "三步法", "需要规划", "详细计划"], action="evaluate"),
]

def s0_pre_filter(message: str) -> Tuple[bool, str]:
    """S0 零成本预筛选
    
    Args:
        message: 用户消息
        
    Returns:
        (需要评估，原因)
        - (False, "白名单") → 直接执行
        - (True, "触发信号") → 进入 S1
    """
    # 检查白名单
    for rule in S0_WHITELIST:
        if any(kw in message for kw in rule.keywords):
            return False, f"白名单：{rule.name}"
    
    # 检查触发信号
    # 1. 长度
    if len(message) > 200:
        return True, "长度 > 200 字"
    
    # 2. 关键词匹配
    for rule in S0_TRIGGER_SIGNALS:
        if any(kw in message for kw in rule.keywords):
            return True, f"触发信号：{rule.name}"
    
    # 3. 多步模式（正则）
    multi_step_patterns = [
        r"先.*然后.*最后",
        r"首先.*其次.*最后",
        r"第一步.*第二步.*第三步",
    ]
    for pattern in multi_step_patterns:
        if re.search(pattern, message):
            return True, "多步模式"
    
    # 默认直接执行
    return False, "默认简单"

# ==================== S1: 轻量复杂度评估 ====================

@dataclass
class ComplexityScore:
    """复杂度评分"""
    steps: int = 1          # 步骤数 (1-5)
    knowledge_domains: int = 1  # 知识域 (1-5)
    uncertainty: int = 1    # 不确定性 (1-5)
    failure_cost: int = 1   # 失败代价 (1-5)
    tool_chain: int = 1     # 工具链 (1-5)
    
    @property
    def total(self) -> int:
        return self.steps + self.knowledge_domains + self.uncertainty + self.failure_cost + self.tool_chain
    
    @property
    def level(self) -> str:
        if self.total <= 8:
            return "SIMPLE"
        elif self.total <= 15:
            return "MEDIUM"
        else:
            return "COMPLEX"

# 复杂度评估关键词
COMPLEXITY_KEYWORDS = {
    "steps": ["然后", "接着", "之后", "下一步", "最后", "首先", "其次"],
    "knowledge_domains": ["技术", "业务", "设计", "测试", "部署", "运维", "产品"],
    "uncertainty": ["可能", "也许", "不确定", "需要确认", "未知", "调研"],
    "failure_cost": ["重要", "关键", "核心", "生产", "线上", "用户数据"],
    "tool_chain": ["API", "数据库", "服务器", "第三方", "工具", "系统"],
}

def s1_complexity_assessment(message: str) -> ComplexityScore:
    """S1 轻量复杂度评估
    
    五个维度，每项 1-5 分
    """
    score = ComplexityScore()
    
    # 1. 步骤数
    step_keywords = COMPLEXITY_KEYWORDS["steps"]
    step_count = sum(1 for kw in step_keywords if kw in message)
    score.steps = min(5, 1 + step_count)
    
    # 2. 知识域
    domain_keywords = COMPLEXITY_KEYWORDS["knowledge_domains"]
    domain_count = sum(1 for kw in domain_keywords if kw in message)
    score.knowledge_domains = min(5, 1 + domain_count)
    
    # 3. 不确定性
    uncertainty_keywords = COMPLEXITY_KEYWORDS["uncertainty"]
    uncertainty_count = sum(1 for kw in uncertainty_keywords if kw in message)
    score.uncertainty = min(5, 1 + uncertainty_count)
    
    # 4. 失败代价
    cost_keywords = COMPLEXITY_KEYWORDS["failure_cost"]
    cost_count = sum(1 for kw in cost_keywords if kw in message)
    score.failure_cost = min(5, 1 + cost_count)
    
    # 5. 工具链
    tool_keywords = COMPLEXITY_KEYWORDS["tool_chain"]
    tool_count = sum(1 for kw in tool_keywords if kw in message)
    score.tool_chain = min(5, 1 + tool_count)
    
    return score

def s1_decision(score: ComplexityScore) -> str:
    """S1 决策
    
    Returns:
        "execute" - 直接执行
        "light_plan" - 轻规划
        "full_plan" - 完整三步法
    """
    if score.total <= 8:
        return "execute"
    elif score.total <= 15:
        return "light_plan"
    else:
        return "full_plan"

# ==================== S2: 深度规划 & 审计 ====================

@dataclass
class DAGStep:
    """DAG 步骤"""
    id: str
    action: str
    depends_on: List[str] = field(default_factory=list)
    phase: int = 0
    estimated_duration: int = 0  # 秒
    risk_level: str = "low"  # low/medium/high

@dataclass
class ExecutionBlueprint:
    """执行蓝图"""
    steps: List[DAGStep] = field(default_factory=list)
    phases: Dict[int, List[str]] = field(default_factory=dict)  # phase_id → [step_ids]
    locked: bool = False
    audit_passed: bool = False

def s2_plan(message: str, score: ComplexityScore) -> ExecutionBlueprint:
    """S2 深度规划
    
    Plan Mode: 任务分解为 DAG 结构
    """
    blueprint = ExecutionBlueprint()
    
    # 示例：根据消息内容生成 DAG
    # 实际实现应该调用 LLM 进行任务分解
    
    # 简单示例：发布公众号文章
    if "发布" in message and "公众号" in message:
        blueprint.steps = [
            DAGStep(id="1", action="分析需求", depends_on=[], phase=0, estimated_duration=5),
            DAGStep(id="2a", action="生成文案", depends_on=["1"], phase=1, estimated_duration=15),
            DAGStep(id="2b", action="准备图片", depends_on=["1"], phase=1, estimated_duration=20),
            DAGStep(id="3", action="调用发布 API", depends_on=["2a", "2b"], phase=2, estimated_duration=30),
            DAGStep(id="4", action="验证发布结果", depends_on=["3"], phase=3, estimated_duration=5),
        ]
        
        # 构建 phases
        for step in blueprint.steps:
            if step.phase not in blueprint.phases:
                blueprint.phases[step.phase] = []
            blueprint.phases[step.phase].append(step.id)
    
    return blueprint

def s2_audit(blueprint: ExecutionBlueprint) -> Tuple[bool, List[str]]:
    """S2 审计
    
    Audit Mode: 检查完整性、合理性、可行性
    
    Returns:
        (通过，问题列表)
    """
    issues = []
    
    # 1. 检查完整性
    if not blueprint.steps:
        issues.append("步骤列表为空")
    
    # 2. 检查依赖关系
    step_ids = {step.id for step in blueprint.steps}
    for step in blueprint.steps:
        for dep in step.depends_on:
            if dep not in step_ids:
                issues.append(f"步骤 {step.id} 依赖不存在的步骤 {dep}")
    
    # 3. 检查循环依赖（简化版）
    # 实际应该用拓扑排序检测
    
    # 4. 检查 phase 合理性
    for step in blueprint.steps:
        if step.phase < 0:
            issues.append(f"步骤 {step.id} 的 phase 为负数")
    
    return len(issues) == 0, issues

# ==================== S3: 分阶段执行 & 质量控制 ====================

class DefectSeverity(Enum):
    """缺陷严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DefectReport:
    """缺陷报告"""
    step_id: str
    severity: DefectSeverity
    description: str
    fix_action: str
    auto_approved: bool = False

def s3_execute_phase(blueprint: ExecutionBlueprint, phase: int) -> Dict[str, Any]:
    """S3 执行某个 Phase
    
    同 Phase 内步骤可并行
    """
    if phase not in blueprint.phases:
        return {"status": "completed", "steps": []}
    
    step_ids = blueprint.phases[phase]
    results = {}
    
    # 并行执行（示例）
    for step_id in step_ids:
        step = next(s for s in blueprint.steps if s.id == step_id)
        # 实际执行逻辑
        results[step_id] = {
            "status": "completed",
            "action": step.action,
        }
    
    return {"status": "completed", "steps": results}

def s3_qa_audit(step_result: Dict[str, Any]) -> Tuple[bool, Optional[DefectReport]]:
    """S3 QA 审计
    
    每步完成后审计
    
    Returns:
        (通过，缺陷报告)
    """
    # 简化示例
    if step_result.get("status") == "completed":
        return True, None
    else:
        return False, DefectReport(
            step_id=step_result.get("step_id", "unknown"),
            severity=DefectSeverity.MEDIUM,
            description="步骤执行失败",
            fix_action="重试或人工介入",
            auto_approved=False
        )

def s3_defect_fix(decision: DefectReport) -> str:
    """S3 缺陷修改决策
    
    分级处理：
    - Critical: 自动批准
    - High: 自动批准 + 通知人类
    - Medium: 人类确认后修改
    - Low: QA 自行决定
    """
    if decision.severity == DefectSeverity.CRITICAL:
        return "自动批准修复"
    elif decision.severity == DefectSeverity.HIGH:
        return "自动批准修复 + 通知人类"
    elif decision.severity == DefectSeverity.MEDIUM:
        return "等待人类确认"
    else:
        return "QA 自行决定"

# ==================== 主流程 ====================

class ComplexTaskProcessor:
    """复杂任务处理器"""
    
    def __init__(self):
        self.blueprint: Optional[ExecutionBlueprint] = None
        self.dynamic_upgrade_count = 0
    
    def process(self, message: str) -> str:
        """处理复杂任务
        
        完整 S0→S1→S2→S3 流程
        """
        # S0: 零成本预筛选
        need_evaluate, reason = s0_pre_filter(message)
        
        if not need_evaluate:
            return f"S0 直接执行：{reason}"
        
        # S1: 轻量复杂度评估
        score = s1_complexity_assessment(message)
        decision = s1_decision(score)
        
        if decision == "execute":
            return f"S1 直接执行：总分 {score.total}"
        elif decision == "light_plan":
            return f"S1 轻规划：总分 {score.total}"
        
        # S2: 深度规划 & 审计
        blueprint = s2_plan(message, score)
        audit_passed, issues = s2_audit(blueprint)
        
        if not audit_passed:
            return f"S2 审计失败：{', '.join(issues)}"
        
        blueprint.locked = True
        blueprint.audit_passed = True
        self.blueprint = blueprint
        
        # S3: 分阶段执行
        for phase in sorted(blueprint.phases.keys()):
            result = s3_execute_phase(blueprint, phase)
            
            # QA 审计
            for step_id, step_result in result.get("steps", {}).items():
                passed, defect = s3_qa_audit(step_result)
                
                if not passed and defect:
                    fix_decision = s3_defect_fix(defect)
                    # 处理缺陷...
        
        return "S3 执行完成"

# ==================== 测试 ====================

if __name__ == "__main__":
    processor = ComplexTaskProcessor()
    
    test_cases = [
        ("北京天气怎么样", "S0 白名单"),
        ("帮我发布公众号文章，主题是 AI 发展趋势，需要配 3 张图", "S2 完整规划"),
        ("开发一个完整的电商系统，包括前端、后端、数据库、部署", "S2 复杂任务"),
    ]
    
    for message, expected in test_cases:
        print(f"\n测试：{message}")
        result = processor.process(message)
        print(f"结果：{result}")
        print(f"预期：{expected}")
