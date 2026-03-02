# 📱 内容运营工作室 AI 组织架构模板

> 适用于 MCN 机构、自媒体工作室、内容创作团队

## 组织架构

```
CEO/创始人 (gpt-4o)
├─ 内容部 (qwen-max)
│  ├─ 文案组
│  │  ├─ 资深文案 (qwen-plus)
│  │  ├─ 脚本作家 (qwen-plus)
│  │  └─ 标题优化师 (qwen-turbo)
│  ├─ 视频组
│  │  ├─ 视频剪辑师 (qwen-vl-max)
│  │  ├─ 特效师 (qwen-vl-max)
│  │  └─ 调色师 (qwen-vl-max)
│  └─ 音频组
│     ├─ 配音员 (qwen-audio)
│     └─ 音效师 (qwen-audio)
│
├─ 运营部 (qwen-max)
│  ├─ 小红书组
│  │  ├─ 小红书运营 (qwen-plus)
│  │  └─ 种草写手 (qwen-plus)
│  ├─ 抖音组
│  │  ├─ 抖音运营 (qwen-plus)
│  │  └─ 直播策划 (qwen-max)
│  ├─ B 站组
│  │  ├─ B 站运营 (qwen-plus)
│  │  └─ 弹幕互动师 (qwen-turbo)
│  └─ 公众号组
│     ├─ 公众号编辑 (qwen-plus)
│     └─ 排版设计师 (qwen-vl-max)
│
├─ 视觉部 (qwen-max)
│  ├─ 设计组
│  │  ├─ 平面设计师 (qwen-vl-max)
│  │  ├─ 封面设计师 (qwen-vl-max)
│  │  └─ 插画师 (qwen-image-max)
│  └─ 摄影组
│     ├─ 摄影师 (qwen-vl-max)
│     └─ 修图师 (qwen-image-max)
│
└─ 商务部 (qwen-max)
   ├─ 商务拓展组
   │  ├─ BD 经理 (qwen-max)
   │  └─ 品牌合作专员 (qwen-plus)
   └─ 数据分析组
      ├─ 数据分析师 (qwen-max)
      └─ 增长黑客 (qwen-plus)
```

## 角色配置

```yaml
# 保存为：~/.copaw/lingxi_org/content_studio.yaml

company:
  name: 内容运营工作室
  vision: 打造千万粉丝的内容矩阵
  annual_budget: 100000
  risk_tolerance: aggressive

roles:
  # ===== CEO =====
  - name: ceo
    job_title: 创始人/CEO
    model: gpt-4o
    skills: [strategy, content_vision, business_development]
    budget_per_day: 50
    performance_target: 9.5
    escalation_to: null

  # ===== 内容部 =====
  - name: content_director
    job_title: 内容总监
    model: qwen-max
    skills: [content_strategy, editorial, team_management]
    budget_per_day: 30
    escalation_to: ceo

  - name: senior_copywriter
    job_title: 资深文案
    model: qwen-plus
    skills: [copywriting, storytelling, brand_voice]
    budget_per_day: 12
    escalation_to: content_director

  - name: script_writer
    job_title: 脚本作家
    model: qwen-plus
    skills: [video_script, screenplay, short_video]
    budget_per_day: 12
    escalation_to: content_director

  - name: title_optimizer
    job_title: 标题优化师
    model: qwen-turbo
    skills: [headline, clickbait, seo]
    budget_per_day: 4
    escalation_to: content_director

  - name: video_editor
    job_title: 视频剪辑师
    model: qwen-vl-max
    skills: [video_editing, premiere, final_cut]
    budget_per_day: 18
    escalation_to: content_director

  - name: vfx_artist
    job_title: 特效师
    model: qwen-vl-max
    skills: [after_effects, motion_graphics, vfx]
    budget_per_day: 20
    escalation_to: content_director

  - name: colorist
    job_title: 调色师
    model: qwen-vl-max
    skills: [color_grading, davinci, visual_aesthetics]
    budget_per_day: 18
    escalation_to: content_director

  - name: voice_actor
    job_title: 配音员
    model: qwen-audio
    skills: [voice_over, narration, character_voice]
    budget_per_day: 15
    escalation_to: content_director

  - name: sound_designer
    job_title: 音效师
    model: qwen-audio
    skills: [sound_design, audio_mixing, sfx]
    budget_per_day: 15
    escalation_to: content_director

  # ===== 运营部 =====
  - name: ops_director
    job_title: 运营总监
    model: qwen-max
    skills: [social_media, growth_hacking, analytics]
    budget_per_day: 30
    escalation_to: ceo

  - name: xiaohongshu_operator
    job_title: 小红书运营
    model: qwen-plus
    skills: [xiaohongshu, seeding, note_optimization]
    budget_per_day: 12
    escalation_to: ops_director

  - name: seeding_writer
    job_title: 种草写手
    model: qwen-plus
    skills: [product_review, recommendation, lifestyle]
    budget_per_day: 10
    escalation_to: ops_director

  - name: douyin_operator
    job_title: 抖音运营
    model: qwen-plus
    skills: [douyin, short_video, algorithm]
    budget_per_day: 12
    escalation_to: ops_director

  - name: live_stream_planner
    job_title: 直播策划
    model: qwen-max
    skills: [live_streaming, sales_script, interaction]
    budget_per_day: 18
    escalation_to: ops_director

  - name: bilibili_operator
    job_title: B 站运营
    model: qwen-plus
    skills: [bilibili, community, video_optimization]
    budget_per_day: 12
    escalation_to: ops_director

  - name: comment_manager
    job_title: 弹幕互动师
    model: qwen-turbo
    skills: [community_management, engagement, reply]
    budget_per_day: 5
    escalation_to: ops_director

  - name: wechat_editor
    job_title: 公众号编辑
    model: qwen-plus
    skills: [wechat, article_editing, content_curation]
    budget_per_day: 12
    escalation_to: ops_director

  - name: layout_designer
    job_title: 排版设计师
    model: qwen-vl-max
    skills: [layout_design, typography, visual_hierarchy]
    budget_per_day: 15
    escalation_to: ops_director

  # ===== 视觉部 =====
  - name: creative_director
    job_title: 创意总监
    model: qwen-max
    skills: [creative_direction, visual_strategy, branding]
    budget_per_day: 35
    escalation_to: ceo

  - name: graphic_designer
    job_title: 平面设计师
    model: qwen-vl-max
    skills: [graphic_design, photoshop, illustrator]
    budget_per_day: 15
    escalation_to: creative_director

  - name: thumbnail_designer
    job_title: 封面设计师
    model: qwen-vl-max
    skills: [thumbnail_design, click_optimization, visual_impact]
    budget_per_day: 12
    escalation_to: creative_director

  - name: illustrator
    job_title: 插画师
    model: qwen-image-max
    skills: [illustration, digital_art, character_design]
    budget_per_day: 18
    escalation_to: creative_director

  - name: photographer
    job_title: 摄影师
    model: qwen-vl-max
    skills: [photography, composition, lighting]
    budget_per_day: 18
    escalation_to: creative_director

  - name: photo_retoucher
    job_title: 修图师
    model: qwen-image-max
    skills: [photo_retouching, skin_retouch, color_correction]
    budget_per_day: 15
    escalation_to: creative_director

  # ===== 商务部 =====
  - name: business_director
    job_title: 商务总监
    model: qwen-max
    skills: [business_development, negotiation, partnerships]
    budget_per_day: 35
    escalation_to: ceo

  - name: bd_manager
    job_title: BD 经理
    model: qwen-max
    skills: [client_acquisition, pitch, contract]
    budget_per_day: 20
    escalation_to: business_director

  - name: brand_partnership_specialist
    job_title: 品牌合作专员
    model: qwen-plus
    skills: [brand_collaboration, sponsored_content, pr]
    budget_per_day: 15
    escalation_to: business_director

  - name: data_analyst
    job_title: 数据分析师
    model: qwen-max
    skills: [data_analysis, audience_insights, performance_tracking]
    budget_per_day: 18
    escalation_to: business_director

  - name: growth_hacker
    job_title: 增长黑客
    model: qwen-plus
    skills: [growth_hacking, ab_testing, viral_marketing]
    budget_per_day: 18
    escalation_to: business_director

teams:
  - id: copywriting_team
    name: 文案组
    lead_role: senior_copywriter
    members: [senior_copywriter, script_writer, title_optimizer]
    kpi_targets:
      content_output: 100
      avg_views: 10000

  - id: video_production_team
    name: 视频组
    lead_role: video_editor
    members: [video_editor, vfx_artist, colorist]
    kpi_targets:
      video_output: 30
      avg_watch_time: 120

  - id: xiaohongshu_team
    name: 小红书组
    lead_role: xiaohongshu_operator
    members: [xiaohongshu_operator, seeding_writer]
    kpi_targets:
      note_output: 60
      follower_growth: 0.15

  - id: douyin_team
    name: 抖音组
    lead_role: douyin_operator
    members: [douyin_operator, live_stream_planner]
    kpi_targets:
      video_output: 90
      live_gmv: 50000

  - id: bilibili_team
    name: B 站组
    lead_role: bilibili_operator
    members: [bilibili_operator, comment_manager]
    kpi_targets:
      video_output: 20
      coin_count: 5000

  - id: design_team
    name: 设计组
    lead_role: graphic_designer
    members: [graphic_designer, thumbnail_designer, illustrator]
    kpi_targets:
      design_output: 200
      satisfaction_rate: 0.95

  - id: business_team
    name: 商务拓展组
    lead_role: bd_manager
    members: [bd_manager, brand_partnership_specialist]
    kpi_targets:
      deals_closed: 10
      revenue: 200000

departments:
  - id: content_dept
    name: 内容部
    head_role: content_director
    teams: [copywriting_team, video_production_team]
    mission: 生产高质量内容
    monthly_budget: 10000

  - id: operations_dept
    name: 运营部
    head_role: ops_director
    teams: [xiaohongshu_team, douyin_team, bilibili_team]
    mission: 多平台运营增长
    monthly_budget: 8000

  - id: visual_dept
    name: 视觉部
    head_role: creative_director
    teams: [design_team]
    mission: 打造视觉冲击力
    monthly_budget: 7000

  - id: business_dept
    name: 商务部
    head_role: business_director
    teams: [business_team]
    mission: 商业变现
    monthly_budget: 5000
```

## 典型任务路由

| 任务 | 优先级 | 路由路径 | 成本 |
|------|--------|---------|------|
| 双 11 直播策划 | P1 | CEO → 运营总监 → 直播策划 | ¥18 |
| 小红书种草笔记 | P3 | 小红书运营 + 种草写手 | ¥22 |
| 抖音视频脚本 | P2 | 内容总监 → 脚本作家 | ¥12 |
| 产品封面设计 | P3 | 封面设计师 | ¥12 |
| 品牌合作方案 | P1 | CEO → 商务总监 → BD 经理 | ¥20 |
| 数据分析报告 | P2 | 数据分析师 | ¥18 |

## 成本预估

| 部门 | 日预算 | 月预算 | 年预算 |
|------|--------|--------|--------|
| CEO | ¥50 | - | - |
| 内容部 | ¥129 | ¥3,870 | ¥46,440 |
| 运营部 | ¥106 | ¥3,180 | ¥38,160 |
| 视觉部 | ¥113 | ¥3,390 | ¥40,680 |
| 商务部 | ¥106 | ¥3,180 | ¥38,160 |
| **总计** | **¥504** | **¥15,120** | **¥181,440** |

> 💡 建议：初期启用核心角色（文案 + 运营 + 设计），日成本约¥100-150

## 使用方式

```python
from scripts.org_structure import load_company_from_yaml

studio = load_company_from_yaml(
    "~/.copaw/lingxi_org/content_studio.yaml"
)

task = studio.route_task(
    "帮我写个小红书美妆种草笔记",
    priority="P3"
)

print(f"任务分配给：{task.assigned_to}")
# 输出：xiaohongshu_operator 或 seeding_writer
```
