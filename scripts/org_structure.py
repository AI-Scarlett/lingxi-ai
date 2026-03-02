#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 组织架构系统 - Enterprise Org System
CEO → 部门 → 团队 → 角色 四层架构 💋

核心能力：
1. 多层级组织管理
2. 跨部门协作流程
3. 预算成本控制
4. 任务自动路由
5. 绩效考核体系
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class OrgLevel(Enum):
    """组织层级"""
    COMPANY = "company"      # CEO/董事会
    DEPARTMENT = "department"  # 部门总监
    TEAM = "team"            # 团队主管
    ROLE = "role"            # 具体角色

class TaskPriority(Enum):
    """任务优先级"""
    P0 = "p0"  # 紧急重要 (CEO 决策)
    P1 = "p1"  # 重要不紧急 (部门级)
    P2 = "p2"  # 一般任务 (团队级)
    P3 = "p3"  # 日常事务 (角色级)

@dataclass
class RoleConfig:
    """最底层：AI 角色配置"""
    name: str              # 角色名称
    job_title: str         # 职位名称 (如"资深文案")
    model_name: str        # 使用模型
    skills: List[str]      # 技能列表
    budget_per_day: float  # 每日预算上限 (元)
    performance_target: float  # 绩效目标分
    escalation_to: str     # 无法处理时升级给谁 (上级角色 ID)
    
    # 状态追踪
    tasks_completed: int = 0
    total_cost: float = 0.0
    avg_score: float = 0.0

@dataclass
class TeamConfig:
    """第三层：业务团队"""
    id: str                # 团队 ID (如 marketing_team_a)
    name: str              # 团队名称
    lead_role: str         # 团队负责人角色 ID
    roles: List[str]       # 团队成员角色 ID 列表
    team_lead_model: str   # 团队主管模型 (通常是更强的模型)
    daily_budget: float    # 团队日预算
    kpi_targets: Dict = field(default_factory=dict)
    
    def get_total_budget(self) -> float:
        """计算团队总预算 = 主管 + 所有成员"""
        return self.daily_budget

@dataclass
class DepartmentConfig:
    """第二层：职能部门"""
    id: str                # 部门 ID (如 marketing_dept)
    name: str              # 部门名称
    head_role: str         # 部门负责人角色 ID
    teams: List[str]       # 下属团队 ID 列表
    department_model: str  # 部门负责人模型 (最高质量)
    monthly_budget: float  # 月度预算
    mission: str           # 部门使命
    
    def get_all_roles(self) -> List[str]:
        """获取部门下所有角色"""
        all_roles = [self.head_role]
        # TODO: 递归获取各团队成员
        return all_roles

@dataclass
class CompanyConfig:
    """第一层：公司实体"""
    id: str                # 公司 ID
    name: str              # 公司名称
    ceo_role: str          # CEO 角色 ID
    departments: List[str] # 部门 ID 列表
    company_vision: str    # 公司愿景
    annual_budget: float   # 年度 AI 预算
    risk_tolerance: str    # 风险偏好 (conservative/balanced/aggressive)
    
    # 全局配置
    default_escalation_policy: str = "immediate"  # 升级策略
    performance_review_cycle: str = "weekly"      # 考核周期

@dataclass
class TaskAssignment:
    """任务分派记录"""
    task_id: str
    description: str
    source_level: OrgLevel      # 发起层级
    target_level: OrgLevel      # 执行层级
    assigned_to: str            # 分配给谁 (角色 ID)
    priority: TaskPriority
    status: str                 # pending/in_progress/completed/escalated
    cost_so_far: float = 0.0
    score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def elapsed_hours(self) -> float:
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds() / 3600
        return (datetime.now() - self.created_at).total_seconds() / 3600

class AIEnterprise:
    """AI 企业组织管理系统 💋"""
    
    def __init__(self, config: CompanyConfig):
        self.company = config
        self.departments: Dict[str, DepartmentConfig] = {}
        self.teams: Dict[str, TeamConfig] = {}
        self.roles: Dict[str, RoleConfig] = {}
        self.task_queue: List[TaskAssignment] = []
        self.task_history: List[TaskAssignment] = []
        
        # 统计指标
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_cost": 0.0,
            "avg_completion_time": 0.0,
            "escalation_rate": 0.0
        }
    
    def add_department(self, dept: DepartmentConfig):
        """添加部门"""
        self.departments[dept.id] = dept
        if dept.id not in self.company.departments:
            self.company.departments.append(dept.id)
    
    def add_team(self, team: TeamConfig):
        """添加团队"""
        self.teams[team.id] = team
    
    def add_role(self, role: RoleConfig):
        """添加角色"""
        self.roles[role.name] = role
    
    def route_task(self, task_desc: str, 
                   priority: TaskPriority = TaskPriority.P2,
                   source_department: Optional[str] = None) -> TaskAssignment:
        """
        智能任务路由 - 根据公司架构自动分配
        
        路由逻辑:
        1. P0 级别 → CEO 决策
        2. P1 级别 → 部门总监
        3. P2 级别 → 团队主管
        4. P3 级别 → 直接分配给合适角色
        """
        task_id = f"task_{datetime.now().timestamp()}"
        
        # 根据优先级决定路由层级
        if priority == TaskPriority.P0:
            # CEO 亲自处理或授权
            target_role = self.company.ceo_role
            target_level = OrgLevel.COMPANY
            
        elif priority == TaskPriority.P1:
            # 部门级别决策
            if source_department:
                dept = self.departments.get(source_department)
                if dept:
                    target_role = dept.head_role
                    target_level = OrgLevel.DEPARTMENT
                else:
                    target_role = self.company.ceo_role
                    target_level = OrgLevel.COMPANY
            else:
                # 自动判断所属部门
                target_role, target_level = self._auto_route_by_content(task_desc)
                
        elif priority == TaskPriority.P2:
            # 团队级别
            target_role, target_level = self._auto_route_by_content(task_desc)
            
        else:  # P3
            # 直接分配给最合适的角色
            target_role = self._find_best_role_for_task(task_desc)
            target_level = OrgLevel.ROLE
        
        assignment = TaskAssignment(
            task_id=task_id,
            description=task_desc,
            source_level=target_level,
            target_level=target_level,
            assigned_to=target_role,
            priority=priority,
            status="pending"
        )
        
        self.task_queue.append(assignment)
        self.stats["total_tasks"] += 1
        
        return assignment
    
    def _auto_route_by_content(self, task_desc: str) -> tuple:
        """根据任务内容自动路由到最合适的部门 - 增强版"""
        # 扩展关键词匹配部门
        dept_keywords = {
            "marketing_dept": ["营销", "推广", "品牌", "广告", "小红书", "抖音", "seo", "SEO", "优化", "排名", "文案", "产品说明"],
            "sales_dept": ["销售", "客户", "订单", "报价", "成交"],
            "tech_dept": ["开发", "代码", "技术", "系统", "bug", "功能", "模块", "编程"],
            "hr_dept": ["招聘", "员工", "薪资", "培训"],
            "finance_dept": ["财务", "预算", "报表", "审计"]
        }
        
        best_match = None
        match_count = 0
        
        for dept_id, keywords in dept_keywords.items():
            count = sum(1 for kw in keywords if kw in task_desc)
            if count > match_count:
                match_count = count
                best_match = dept_id
        
        if best_match and best_match in self.departments:
            dept = self.departments[best_match]
            
            # 如果是 P3 优先级，尝试直接找部门内最合适的角色
            # 这里简化处理，返回部门总监，让后续逻辑再分配
            return dept.head_role, OrgLevel.DEPARTMENT
        
        # 默认路由到 CEO
        return self.company.ceo_role, OrgLevel.COMPANY
    
    def _find_best_role_for_task(self, task_desc: str) -> str:
        """找到最适合执行任务的角色 - 智能匹配版"""
        best_match = None
        best_score = 0
        
        for role_name, role in self.roles.items():
            score = 0
            
            # 技能关键词匹配（每个技能计 1 分）
            for skill in role.skills:
                if skill in task_desc:
                    score += 1
            
            # 职位头衔关键词匹配（额外加 2 分）
            job_keywords = role.job_title.lower().replace("资深", "").replace("高级", "")
            if any(kw in task_desc for kw in [job_keywords[:2], job_keywords[-2:]] if len(job_keywords) > 2):
                score += 2
            
            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = role_name
        
        # 如果有匹配，返回最佳匹配；否则按部门关键词路由
        if best_match and best_score > 0:
            return best_match
        
        # 兜底：按内容关键词找部门
        return self._auto_route_by_content(task_desc)[0]
    
    def escalate_task(self, task: TaskAssignment, reason: str):
        """任务升级 - 当前角色无法处理时向上级汇报"""
        current_role = self.roles.get(task.assigned_to)
        if not current_role:
            return
        
        # 查找升级路径
        escalation_target = current_role.escalation_to
        
        if escalation_target and escalation_target in self.roles:
            task.assigned_to = escalation_target
            task.status = "escalated"
            print(f"⚠️  任务 {task.task_id} 已升级到：{escalation_target}")
            # TODO: 记录升级原因和时间
        else:
            # 最终升级到 CEO
            task.assigned_to = self.company.ceo_role
            task.status = "escalated"
            print(f"⚠️  任务 {task.task_id} 已升级到 CEO")
    
    def complete_task(self, task: TaskAssignment, score: float, cost: float):
        """完成任务并更新统计"""
        task.status = "completed"
        task.completed_at = datetime.now()
        task.score = score
        task.cost_so_far = cost
        
        # 更新角色统计
        role = self.roles.get(task.assigned_to)
        if role:
            role.tasks_completed += 1
            role.total_cost += cost
            role.avg_score = (role.avg_score * (role.tasks_completed - 1) + score) / role.tasks_completed
        
        # 更新全局统计
        self.stats["completed_tasks"] += 1
        self.stats["total_cost"] += cost
        
        # 移动到历史记录
        self.task_queue = [t for t in self.task_queue if t.task_id != task.task_id]
        self.task_history.append(task)
    
    def get_performance_report(self, level: OrgLevel = OrgLevel.COMPANY) -> str:
        """生成绩效报告"""
        lines = [
            "="*60,
            f"📊 {self.company.name} 绩效报告",
            "="*60,
            f"📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        
        if level == OrgLevel.COMPANY:
            lines.extend([
                "🏢 公司概览:",
                f"  ├─ 总任务数：{self.stats['total_tasks']}",
                f"  ├─ 完成数：{self.stats['completed_tasks']}",
                f"  ├─ 完成率：{self.stats['completed_tasks']/max(self.stats['total_tasks'],1)*100:.1f}%",
                f"  ├─ 总成本：¥{self.stats['total_cost']:.2f}",
                f"  └─ 年度预算剩余：¥{self.company.annual_budget - self.stats['total_cost']:.2f}",
                ""
            ])
            
            # 各部门表现
            lines.append("📈 部门表现:")
            for dept_id in self.company.departments:
                dept = self.departments[dept_id]
                lines.append(f"  📁 {dept.name}:")
                lines.append(f"      ├─ 负责人：{dept.head_role}")
                lines.append(f"      ├─ 团队数：{len(dept.teams)}")
                lines.append(f"      └─ 月预算：¥{dept.monthly_budget:.2f}")
            
            # 角色排行榜
            lines.append("")
            lines.append("🏆 Top 5 高效角色:")
            sorted_roles = sorted(
                self.roles.values(),
                key=lambda r: r.tasks_completed,
                reverse=True
            )[:5]
            
            for i, role in enumerate(sorted_roles, 1):
                lines.append(f"  {i}. {role.name} ({role.job_title})")
                lines.append(f"     ├─ 完成：{role.tasks_completed} 任务")
                lines.append(f"     ├─ 评分：{role.avg_score:.1f}/10")
                lines.append(f"     └─ 成本：¥{role.total_cost:.2f}")
        
        lines.append("="*60)
        
        return "\n".join(lines)
    
    def check_budget_alerts(self) -> List[str]:
        """检查预算预警"""
        alerts = []
        
        # 检查公司总预算
        usage_rate = self.stats["total_cost"] / self.company.annual_budget
        if usage_rate > 0.9:
            alerts.append(f"⚠️  公司年度预算使用率 {usage_rate*100:.1f}%，接近上限!")
        
        # 检查各部门预算
        for dept_id, dept in self.departments.items():
            # TODO: 计算部门实际花费
            pass
        
        return alerts


def create_sample_company() -> AIEnterprise:
    """创建示例公司架构"""
    
    # 定义角色
    roles = [
        RoleConfig(
            name="ceo_ai",
            job_title="首席执行官",
            model_name="gpt-4o",
            skills=["strategy", "decision", "management"],
            budget_per_day=50.0,
            performance_target=9.5,
            escalation_to=None  # CEO 是最高级
        ),
        RoleConfig(
            name="marketing_director",
            job_title="市场总监",
            model_name="qwen-max",
            skills=["marketing", "branding", "strategy"],
            budget_per_day=30.0,
            performance_target=9.0,
            escalation_to="ceo_ai"
        ),
        RoleConfig(
            name="copywriter_senior",
            job_title="资深文案",
            model_name="qwen-plus",
            skills=["writing", "copywriting", "social_media"],
            budget_per_day=10.0,
            performance_target=8.5,
            escalation_to="marketing_director"
        ),
        RoleConfig(
            name="seo_specialist",
            job_title="SEO 专家",
            model_name="qwen-plus",
            skills=["seo", "analytics", "optimization"],
            budget_per_day=8.0,
            performance_target=8.5,
            escalation_to="marketing_director"
        ),
        RoleConfig(
            name="social_manager",
            job_title="社交媒体经理",
            model_name="qwen-plus",
            skills=["xiaohongshu", "douyin", "weibo"],
            budget_per_day=12.0,
            performance_target=8.8,
            escalation_to="marketing_director"
        ),
        RoleConfig(
            name="tech_cto",
            job_title="技术总监",
            model_name="qwen-coder",
            skills=["architecture", "technical_decision", "leadership"],
            budget_per_day=35.0,
            performance_target=9.2,
            escalation_to="ceo_ai"
        ),
        RoleConfig(
            name="senior_developer",
            job_title="高级开发工程师",
            model_name="qwen-coder",
            skills=["python", "javascript", "backend"],
            budget_per_day=15.0,
            performance_target=9.0,
            escalation_to="tech_cto"
        ),
    ]
    
    # 定义团队
    teams = [
        TeamConfig(
            id="marketing_team_a",
            name="品牌增长团队",
            lead_role="marketing_director",
            roles=["copywriter_senior", "seo_specialist", "social_manager"],
            team_lead_model="qwen-max",
            daily_budget=60.0,
            kpi_targets={"campaign_roi": 3.0, "engagement_rate": 0.05}
        ),
        TeamConfig(
            id="dev_team_core",
            name="核心研发团队",
            lead_role="tech_cto",
            roles=["senior_developer"],
            team_lead_model="qwen-coder",
            daily_budget=50.0,
            kpi_targets={"code_quality": 9.0, "deployment_freq": "daily"}
        ),
    ]
    
    # 定义部门
    departments = [
        DepartmentConfig(
            id="marketing_dept",
            name="市场营销部",
            head_role="marketing_director",
            teams=["marketing_team_a"],
            department_model="qwen-max",
            monthly_budget=2000.0,
            mission="打造行业领先的数字营销品牌"
        ),
        DepartmentConfig(
            id="tech_dept",
            name="技术研发部",
            head_role="tech_cto",
            teams=["dev_team_core"],
            department_model="qwen-coder",
            monthly_budget=3000.0,
            mission="构建稳定高效的 AI 产品平台"
        ),
    ]
    
    # 定义公司
    company = CompanyConfig(
        id="scarlett_corp",
        name="丝佳丽智能科技",
        ceo_role="ceo_ai",
        departments=["marketing_dept", "tech_dept"],
        company_vision="成为全球领先的 AI 助手服务提供商",
        annual_budget=100000.0,
        risk_tolerance="balanced"
    )
    
    # 组装企业
    enterprise = AIEnterprise(company)
    
    for role in roles:
        enterprise.add_role(role)
    
    for team in teams:
        enterprise.add_team(team)
    
    for dept in departments:
        enterprise.add_department(dept)
    
    return enterprise


if __name__ == "__main__":
    # 演示
    print("🏗️  正在构建 AI 企业组织架构...\n")
    
    company = create_sample_company()
    
    print(company.get_performance_report())
    
    # 模拟任务分配
    print("\n🎯 测试任务路由:")
    
    tasks = [
        ("帮我写个小红书美妆推广文案", TaskPriority.P2),
        ("制定明年 Q1 的市场战略", TaskPriority.P1),
        ("修复支付系统的 bug", TaskPriority.P0),
        ("优化官网 SEO 排名", TaskPriority.P3),
    ]
    
    for desc, priority in tasks:
        task = company.route_task(desc, priority)
        role = company.roles.get(task.assigned_to)
        print(f"\n【{priority.value.upper()}】{desc[:30]}...")
        print(f"  → 分配给：{role.name} ({role.job_title})")
        print(f"  → 使用模型：{role.model_name}")
        print(f"  → 层级：{task.target_level.value}")
