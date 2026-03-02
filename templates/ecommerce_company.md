# 🛍️ 电商公司 AI 组织架构模板

> 适用于淘宝/京东/拼多多/抖音电商等电商企业

## 组织架构

```
CEO (gpt-4o)
├─ 运营部 (qwen-max)
│  ├─ 商品运营组
│  │  ├─ 选品专员 (qwen-plus)
│  │  ├─ 定价策略师 (qwen-max)
│  │  └─ 库存管理师 (qwen-plus)
│  ├─ 客服组
│  │  ├─ 售前客服 (glm-edge)
│  │  ├─ 售后客服 (glm-edge)
│  │  └─ 投诉处理专员 (qwen-plus)
│  └─ 订单组
│     ├─ 订单处理员 (qwen-turbo)
│     └─ 物流协调员 (qwen-plus)
│
├─ 市场部 (qwen-max)
│  ├─ 推广组
│  │  ├─ 直通车优化师 (qwen-plus)
│  │  ├─ 信息流投放师 (qwen-plus)
│  │  └─ 活动策划师 (qwen-max)
│  ├─ 内容组
│  │  ├─ 商品文案 (qwen-plus)
│  │  ├─ 详情页设计师 (qwen-vl-max)
│  │  └─ 短视频脚本师 (qwen-plus)
│  └─ 社交媒体组
│     ├─ 小红书运营 (qwen-plus)
│     ├─ 抖音运营 (qwen-plus)
│     └─ 私域流量运营 (qwen-plus)
│
├─ 产品部 (qwen-max)
│  ├─ 产品开发组
│  │  ├─ 市场调研员 (qwen-plus)
│  │  └─ 产品开发专员 (qwen-max)
│  └─ 视觉设计组
│     ├─ 平面设计师 (qwen-vl-max)
│     └─ 摄影修图师 (qwen-image-max)
│
└─ 数据部 (qwen-max)
   ├─ 数据分析组
   │  ├─ 经营分析师 (qwen-max)
   │  ├─ 用户分析师 (qwen-max)
   │  └─ 竞品分析师 (qwen-plus)
   └─ BI 报表组
      └─ 报表工程师 (qwen-coder)
```

## 角色配置

```yaml
# 保存为：~/.copaw/lingxi_org/ecommerce_company.yaml

company:
  name: 电商公司
  vision: 成为行业领先的电商品牌
  annual_budget: 150000
  risk_tolerance: balanced

roles:
  # ===== CEO 层 =====
  - name: ceo
    job_title: 首席执行官
    model: gpt-4o
    skills: [strategy, decision, management]
    budget_per_day: 60
    performance_target: 9.5
    escalation_to: null

  # ===== 运营部 =====
  - name: ops_director
    job_title: 运营总监
    model: qwen-max
    skills: [operations, management, ecommerce]
    budget_per_day: 35
    escalation_to: ceo

  - name: product_specialist
    job_title: 选品专员
    model: qwen-plus
    skills: [product_selection, market_research]
    budget_per_day: 12
    escalation_to: ops_director

  - name: pricing_strategist
    job_title: 定价策略师
    model: qwen-max
    skills: [pricing, competition_analysis, profit_optimization]
    budget_per_day: 15
    escalation_to: ops_director

  - name: inventory_manager
    job_title: 库存管理师
    model: qwen-plus
    skills: [inventory, supply_chain, forecasting]
    budget_per_day: 12
    escalation_to: ops_director

  - name: pre_sales_service
    job_title: 售前客服
    model: glm-edge
    skills: [customer_service, sales, communication]
    budget_per_day: 5
    escalation_to: ops_director

  - name: after_sales_service
    job_title: 售后客服
    model: glm-edge
    skills: [customer_service, problem_solving]
    budget_per_day: 5
    escalation_to: ops_director

  - name: complaint_handler
    job_title: 投诉处理专员
    model: qwen-plus
    skills: [conflict_resolution, customer_retention]
    budget_per_day: 10
    escalation_to: ops_director

  - name: order_processor
    job_title: 订单处理员
    model: qwen-turbo
    skills: [order_processing, data_entry]
    budget_per_day: 3
    escalation_to: ops_director

  - name: logistics_coordinator
    job_title: 物流协调员
    model: qwen-plus
    skills: [logistics, shipping, tracking]
    budget_per_day: 10
    escalation_to: ops_director

  # ===== 市场部 =====
  - name: marketing_director
    job_title: 市场总监
    model: qwen-max
    skills: [marketing, branding, strategy]
    budget_per_day: 35
    escalation_to: ceo

  - name: ppc_specialist
    job_title: 直通车优化师
    model: qwen-plus
    skills: [ppc, sem, roi_optimization]
    budget_per_day: 15
    escalation_to: marketing_director

  - name: ad_buyer
    job_title: 信息流投放师
    model: qwen-plus
    skills: [feed_ads, douyin_ads, wechat_ads]
    budget_per_day: 15
    escalation_to: marketing_director

  - name: campaign_planner
    job_title: 活动策划师
    model: qwen-max
    skills: [event_planning, 618, double11, promotions]
    budget_per_day: 18
    escalation_to: marketing_director

  - name: copywriter
    job_title: 商品文案
    model: qwen-plus
    skills: [copywriting, product_description, selling_points]
    budget_per_day: 10
    escalation_to: marketing_director

  - name: detail_designer
    job_title: 详情页设计师
    model: qwen-vl-max
    skills: [detail_page, visual_design, conversion_optimization]
    budget_per_day: 20
    escalation_to: marketing_director

  - name: video_script_writer
    job_title: 短视频脚本师
    model: qwen-plus
    skills: [video_script, short_video, storytelling]
    budget_per_day: 12
    escalation_to: marketing_director

  - name: xiaohongshu_operator
    job_title: 小红书运营
    model: qwen-plus
    skills: [xiaohongshu, seeding, koc_management]
    budget_per_day: 12
    escalation_to: marketing_director

  - name: douyin_operator
    job_title: 抖音运营
    model: qwen-plus
    skills: [douyin, live_streaming, short_video]
    budget_per_day: 12
    escalation_to: marketing_director

  - name: private_traffic_operator
    job_title: 私域流量运营
    model: qwen-plus
    skills: [wechat, community, user_retention]
    budget_per_day: 12
    escalation_to: marketing_director

  # ===== 产品部 =====
  - name: product_director
    job_title: 产品总监
    model: qwen-max
    skills: [product_management, roadmap, user_research]
    budget_per_day: 35
    escalation_to: ceo

  - name: market_researcher
    job_title: 市场调研员
    model: qwen-plus
    skills: [market_research, user_survey, trend_analysis]
    budget_per_day: 12
    escalation_to: product_director

  - name: product_developer
    job_title: 产品开发专员
    model: qwen-max
    skills: [product_development, sourcing, supplier_management]
    budget_per_day: 15
    escalation_to: product_director

  - name: graphic_designer
    job_title: 平面设计师
    model: qwen-vl-max
    skills: [graphic_design, branding, visual_identity]
    budget_per_day: 18
    escalation_to: product_director

  - name: photographer
    job_title: 摄影修图师
    model: qwen-image-max
    skills: [photography, photo_editing, product_photography]
    budget_per_day: 20
    escalation_to: product_director

  # ===== 数据部 =====
  - name: data_director
    job_title: 数据总监
    model: qwen-max
    skills: [data_strategy, analytics, bi]
    budget_per_day: 35
    escalation_to: ceo

  - name: business_analyst
    job_title: 经营分析师
    model: qwen-max
    skills: [business_analysis, kpi_tracking, reporting]
    budget_per_day: 18
    escalation_to: data_director

  - name: user_analyst
    job_title: 用户分析师
    model: qwen-max
    skills: [user_analysis, cohort_analysis, retention]
    budget_per_day: 18
    escalation_to: data_director

  - name: competitor_analyst
    job_title: 竞品分析师
    model: qwen-plus
    skills: [competitor_analysis, benchmarking, market_intelligence]
    budget_per_day: 15
    escalation_to: data_director

  - name: bi_engineer
    job_title: 报表工程师
    model: qwen-coder
    skills: [sql, python, tableau, powerbi]
    budget_per_day: 18
    escalation_to: data_director

teams:
  - id: product_ops_team
    name: 商品运营组
    lead_role: product_specialist
    members: [product_specialist, pricing_strategist, inventory_manager]
    kpi_targets:
      gmv_target: 1000000
      inventory_turnover: 30

  - id: customer_service_team
    name: 客服组
    lead_role: complaint_handler
    members: [pre_sales_service, after_sales_service, complaint_handler]
    kpi_targets:
      response_time: 30
      satisfaction_rate: 0.95

  - id: promotion_team
    name: 推广组
    lead_role: ppc_specialist
    members: [ppc_specialist, ad_buyer, campaign_planner]
    kpi_targets:
      roas: 3.0
      conversion_rate: 0.03

  - id: content_team
    name: 内容组
    lead_role: copywriter
    members: [copywriter, detail_designer, video_script_writer]
    kpi_targets:
      content_output: 50
      click_rate: 0.05

  - id: social_team
    name: 社交媒体组
    lead_role: xiaohongshu_operator
    members: [xiaohongshu_operator, douyin_operator, private_traffic_operator]
    kpi_targets:
      follower_growth: 0.1
      engagement_rate: 0.05

  - id: data_team
    name: 数据分析组
    lead_role: business_analyst
    members: [business_analyst, user_analyst, competitor_analyst, bi_engineer]
    kpi_targets:
      report_accuracy: 0.99
      insight_count: 10

departments:
  - id: operations_dept
    name: 运营部
    head_role: ops_director
    teams: [product_ops_team, customer_service_team]
    mission: 提升店铺运营效率和客户满意度
    monthly_budget: 8000

  - id: marketing_dept
    name: 市场部
    head_role: marketing_director
    teams: [promotion_team, content_team, social_team]
    mission: 打造品牌影响力，驱动流量增长
    monthly_budget: 12000

  - id: product_dept
    name: 产品部
    head_role: product_director
    teams: []
    mission: 开发有竞争力的产品
    monthly_budget: 6000

  - id: data_dept
    name: 数据部
    head_role: data_director
    teams: [data_team]
    mission: 数据驱动决策
    monthly_budget: 5000
```

## 典型任务路由示例

| 任务 | 优先级 | 路由路径 | 预计成本 |
|------|--------|---------|---------|
| 618 活动策划 | P1 | CEO → 市场总监 → 活动策划师 | ¥18 |
| 商品详情页优化 | P2 | 市场总监 → 详情页设计师 | ¥20 |
| 客户投诉处理 | P0 | CEO → 运营总监 → 投诉专员 | ¥10 |
| 竞品分析报告 | P2 | 数据总监 → 竞品分析师 | ¥15 |
| 直通车投放优化 | P3 | 直通车优化师 | ¥15 |
| 小红书种草文案 | P3 | 小红书运营 | ¥12 |

## 成本预估

| 部门 | 日预算 | 月预算 | 年预算 |
|------|--------|--------|--------|
| CEO 层 | ¥60 | - | - |
| 运营部 | ¥107 | ¥3,210 | ¥38,520 |
| 市场部 | ¥121 | ¥3,630 | ¥43,560 |
| 产品部 | ¥88 | ¥2,640 | ¥31,680 |
| 数据部 | ¥89 | ¥2,670 | ¥32,040 |
| **总计** | **¥465** | **¥13,950** | **¥167,400** |

> 💡 实际使用建议：根据业务规模按需启用角色，初期可启用核心角色（10-15 个），日成本约¥150-200

## 使用方式

```python
from scripts.org_structure import load_company_from_yaml

# 加载电商公司模板
ecommerce = load_company_from_yaml(
    "~/.copaw/lingxi_org/ecommerce_company.yaml"
)

# 执行任务
task = ecommerce.route_task(
    "帮我写个双 11 预售活动文案",
    priority="P2"
)

print(f"任务分配给：{task.assigned_to}")
# 输出：campaign_planner 或 copywriter
```
