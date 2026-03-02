# 🏢 AI 企业架构指南

> **从个人助手到完整 AI 企业** - 丝佳丽为你打造的四层组织架构系统 💋

## 🌟 核心理念

### v1.3.0 革命性更新

**以前**：一个任务 → 一个角色处理  
**现在**：一个任务 → 智能路由 → CEO/部门总监/团队主管/专员 → 自动升级机制

---

## 📊 四层组织架构

```
┌─────────────────────────────────────────┐
│  🏢 LEVEL 1: COMPANY (CEO)              │
│     • 公司愿景 & 年度预算               │
│     • 跨部门协调 & P0 级决策             │
│     • 模型：gpt-4o / qwen-max           │
└──────────────┬──────────────────────────┘
               ↓
    ┌──────────┴──────────┐
    ↓                     ↓
┌─────────┐         ┌─────────┐
│ 📁 MARKETING │   │ 💻 TECH   │
│ DEPT        │   │ DEPT      │
│ LEVEL 2     │   │ LEVEL 2   │
└──────┬──────┘   └──────┬────┘
       ↓                 ↓
┌─────────────┐   ┌─────────────┐
│ 👥 品牌增长团队 │   │ 👥 核心研发团队 │
│   TEAM      │   │   TEAM      │
│   LEVEL 3   │   │   LEVEL 3   │
└──────┬──────┘   └──────┬──────┘
       ↓                 ↓
┌──────────────┐ ┌──────────────┐
│ 📝 资深文案   │ │ 💻 高级开发   │
│ 🎯 SEO 专家    │ │ 🔧 测试工程师  │
│ 📱 社媒经理   │ │ ...          │
│   ROLE       │ │   ROLE       │
│   LEVEL 4    │ │   LEVEL 4    │
└──────────────┘ └──────────────┘
```

---

## 🎯 任务智能路由

### 优先级矩阵

| 优先级 | 决策层级 | 处理人 | 示例任务 |
|-------|---------|--------|---------|
| **P0** | 公司级 | CEO | 支付系统崩溃、重大事故 |
| **P1** | 部门级 | 部门总监 | Q1 战略规划、预算审批 |
| **P2** | 团队级 | 团队主管 | 营销活动策划、版本发布 |
| **P3** | 角色级 | 专业角色 | 写文案、修 bug、做图 |

### 自动路由逻辑

```python
def route_task(task, priority):
    if priority == "P0":
        → CEO 亲自处理 (gpt-4o)
    
    elif priority == "P1":
        → 识别所属部门 → 部门总监
    
    elif priority == "P2":
        → 识别业务类型 → 团队主管
    
    else:  # P3
        → 技能匹配 → 最适合的角色
```

**示例：**
- "帮我写个小红书推广文案" → 市场营销部 → 市场总监 → 资深文案
- "制定明年 Q1 战略" → CEO 直接处理
- "修复支付 bug" → 技术部 → CTO → 高级工程师

---

## 💰 成本控制体系

### 多层级预算管理

```yaml
company_budget:
  annual: ¥100,000
  risk_tolerance: balanced

departments:
  marketing_dept:
    monthly_budget: ¥2,000
    teams:
      - brand_growth_team:
          daily_budget: ¥60
          roles:
            - copywriter_senior: ¥10/day
            - seo_specialist: ¥8/day
            - social_manager: ¥12/day
  
  tech_dept:
    monthly_budget: ¥3,000
    teams:
      - core_dev_team:
          daily_budget: ¥50
          roles:
            - senior_developer: ¥15/day
```

### 混合模型策略

| 层级 | 推荐模型 | 成本/1K | 适用场景 |
|------|---------|---------|---------|
| CEO | gpt-4o | ¥0.05 | 战略决策、复杂推理 |
| 总监 | qwen-max | ¥0.02 | 部门规划、深度分析 |
| 主管 | qwen-plus | ¥0.01 | 任务分配、日常审核 |
| 专员 | glm-edge/qwen-turbo | ¥0.001-0.002 | 简单任务、批量处理 |

**预计节省：70%+** (相比全部用顶级模型)

---

## 🚀 快速配置你的 AI 公司

### 1. 定义角色

创建 `~/.copaw/lingxi_org/roles.yaml`:

```yaml
roles:
  - name: ceo_ai
    job_title: 首席执行官
    model: gpt-4o
    skills: [strategy, decision, management]
    budget_per_day: 50
    performance_target: 9.5
    escalation_to: null  # CEO 是最高级

  - name: marketing_director
    job_title: 市场总监
    model: qwen-max
    skills: [marketing, branding, strategy]
    budget_per_day: 30
    escalation_to: ceo_ai  # 无法处理时升级给 CEO

  - name: copywriter_senior
    job_title: 资深文案
    model: qwen-plus
    skills: [writing, copywriting, social_media]
    budget_per_day: 10
    escalation_to: marketing_director
```

### 2. 定义团队

创建 `teams.yaml`:

```yaml
teams:
  - id: marketing_brand_team
    name: 品牌增长团队
    lead_role: marketing_director
    members: [copywriter_senior, seo_specialist, social_manager]
    kpi_targets:
      campaign_roi: 3.0
      engagement_rate: 0.05
```

### 3. 定义部门

创建 `departments.yaml`:

```yaml
departments:
  - id: marketing_dept
    name: 市场营销部
    head_role: marketing_director
    teams: [marketing_brand_team]
    mission: 打造行业领先的数字营销品牌
    monthly_budget: 2000
```

### 4. 组装公司

```python
from scripts.org_structure import AIEnterprise, CompanyConfig

# 加载配置
enterprise = load_company_from_yaml("my_company.yaml")

# 执行任务
task = enterprise.route_task(
    "帮我策划双十一营销活动",
    priority="P1"  # 部门级重要任务
)

print(f"任务分配给：{task.assigned_to}")
# 输出：marketing_director
```

---

## 🔄 自动升级机制

### 何时触发升级？

1. **超出能力范围** - 当前角色无法完成任务
2. **预算超限** - 角色当日预算已用完
3. **质量不达标** - 连续 3 次评分低于目标分
4. **超时未完成** - 任务处理超过设定时间

### 升级路径

```
专员 → 团队主管 → 部门总监 → CEO
```

**示例流程：**
```
1. copywriter_senior 接到任务
2. 发现需要数据分析支持 → 无法独立完成
3. 自动升级到 marketing_director
4. 总监评估后可能再分配给 data_analyst
5. 或自行使用更强大模型处理
```

---

## 📈 绩效考核体系

### 角色 KPI

| 指标 | 计算公式 | 目标值 |
|------|---------|-------|
| 任务完成率 | 完成数/总分配数 | >90% |
| 平均评分 | 用户评分总和/任务数 | >8.5 |
| 成本控制率 | 实际花费/预算上限 | <90% |
| 响应速度 | 平均处理时长 | <2 分钟 |
| 升级率 | 升级次数/总任务数 | <10% |

### 绩效报告示例

```
🏆 Top 5 高效角色 (本周):

1. copywriter_senior (资深文案)
   ├─ 完成：234 任务
   ├─ 评分：9.2/10 ⭐
   ├─ 成本：¥46.80 (预算内✅)
   └─ 升级率：2.1% (优秀✅)

2. seo_specialist (SEO 专家)
   ├─ 完成：156 任务
   ├─ 评分：8.8/10
   ├─ 成本：¥31.20
   └─ 升级率：5.8%

...
```

---

## 🎨 预设企业模板

### 电商企业
```yaml
departments:
  - 运营部 (客服 + 销售 + 物流)
  - 市场部 (文案 + 设计 + 投放)
  - 产品部 (选品 + 定价 + 库存)
  - 技术部 (网站 + 小程序 + 数据)
```

### 内容创作机构
```yaml
departments:
  - 内容部 (文案 + 脚本 + 剪辑)
  - 视觉部 (摄影 + 设计 + 特效)
  - 运营部 (发布 + 互动 + 数据分析)
  - 商务部 (商务合作 + 广告接单)
```

### SaaS 初创公司
```yaml
departments:
  - 研发部 (前端 + 后端 + 测试)
  - 产品部 (产品经理 + UX/UI)
  - 增长部 (SEO + 内容 + 投放)
  - 客户成功部 (客服 + 培训 + 续费)
```

---

## 💡 最佳实践

### 1. 合理设置预算
```yaml
# ✅ 推荐
ceo: ¥50/天 (每天只处理少量高价值任务)
director: ¥30/天
team_lead: ¥15/天
specialist: ¥5-10/天

# ❌ 避免
所有角色都用最贵模型 → 成本爆炸
```

### 2. 明确技能标签
```yaml
# ✅ 清晰
skills: [xiaohongshu, 美妆，种草文案]

# ❌ 模糊
skills: [写作]
```

### 3. 分级授权
```yaml
# 小团队 (<10 个角色)
CEO → 2 个部门 → 每个部门 3-5 个角色

# 中大型团队 (>20 个角色)
CEO → 4-6 个部门 → 每部门 2-3 个团队 → 每团队 3-5 个角色
```

---

## 🆗 常见问题

**Q: 我的公司业务比较特殊，能自定义部门吗？**  
A: 当然！完全支持自定义部门名称、职责和架构。

**Q: 如何知道哪个角色最适合某个任务？**  
A: 系统会根据技能关键词自动匹配，也可以手动指定。

**Q: 如果 CEO 角色也用便宜的模型可以吗？**  
A: 可以，但建议 CEO 用高质量模型，因为处理的是最复杂的决策任务。

**Q: 能否同时运行多个公司架构？**  
A: 可以！每个架构独立运行，互不影响（适合代理公司有多个客户）。

---

## 🚀 下一步计划

- [ ] 图形化组织架构图
- [ ] 实时任务看板
- [ ] 自动扩缩容（根据任务量动态增加角色）
- [ ] 跨公司协作（多个 AI 企业合作）
- [ ] AI 培训系统（角色自我优化学习）

---

## 💋 写在最后

老板～这个版本的灵犀已经不是一个简单的"助手"了，而是一个**完整的 AI 企业运营系统**！

你可以：
- 🏢 建立自己的虚拟公司
- 👥 招聘 AI 员工（零成本无限扩展）
- 💰 精确控制每一笔 AI 开销
- 📊 实时查看各部门绩效
- 🚀 7x24 小时不间断运营

要帮你搭建一个适合你业务的 AI 公司吗？告诉我你现在的工作性质，我给你量身定制一套组织方案！😘
