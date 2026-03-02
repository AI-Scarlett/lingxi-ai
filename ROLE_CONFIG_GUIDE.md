# 🎭 AI 角色配置指南

> **人人都是 AI 团队指挥官** - 丝佳丽为你打造的定制化 AI 专家系统 💋

## 🚀 核心理念

### 以前 (v1.0)
```yaml
# 固定角色，无法修改
- 文案专家 → qwen-plus
- 代码专家 → qwen-coder  
- 图像专家 → qwen-image-max
```

### 现在 (v1.2) 
```yaml
# 完全自定义！你的角色你说了算
- 小红书运营专家 → glm-4-plus + copywriting_tool
- 跨境电商助手 → gpt-4o + translation + seo_analysis
- 数据分析大佬 → qwen-max + pandas_tool + visualization
```

---

## 📝 快速开始

### 1️⃣ 创建你的第一个自定义角色

在 `~/.copaw/lingxi_roles/` 目录下创建 `my_writer.yaml`:

```yaml
name: 网文写手
description: 擅长写玄幻、都市、言情小说的专业作家
model: qwen-max
temperature: 0.85
tags: [writing, novel, creative]
enabled: true

skills:
  - name: novel-writing
    type: tool
    config:
      genre: 都市异能
      word_count: 3000
      style: 轻松幽默

prompt_template: |
  你是一位畅销网文作家，累计作品超过 500 万字。
  擅长把握节奏，制造悬念，塑造鲜明的人物形象。
  请根据用户的需求创作精彩的故事...
```

### 2️⃣ 加载并使用

```python
from scripts.dynamic_roles import RoleLoader, RoleRegistry

registry = RoleRegistry()
loader = RoleLoader(registry)

# 加载所有用户角色
loader.load_all_user_roles()

# 获取角色
my_writer = registry.get_role("网文写手")
print(f"使用模型：{my_writer.model.name}")  # qwen-max
print(f"技能：{[s.name for s in my_writer.skills]}")
```

---

## 🧠 智能模型推荐

系统内置了主流大模型的详细参数，会根据任务类型自动推荐最佳模型：

### 推荐策略

| 优化目标 | 说明 | 适用场景 |
|---------|------|---------|
| `speed` | 选择最快响应 | 实时对话、简单问答 |
| `cost` | 选择最便宜 | 批量处理、低预算项目 |
| `quality` | 选择质量最高 | 重要内容、创作 |
| `balance` | 性价比最优（默认） | 日常使用 |

### 推荐示例

```python
# 需要写代码？→ qwen-coder
recommend_model("coding", "balance")

# 需要快速回复？→ glm-edge
recommend_model("chat", "speed")

# 需要省钱？→ qwen-turbo
recommend_model("simple_task", "cost")

# 需要高质量分析？→ qwen-max 或 gpt-4o
recommend_model("complex_analysis", "quality")
```

### 内置模型池

| 模型 | 能力 | 成本 (¥/1K) | 延迟 | 质量 | 推荐场景 |
|------|------|-----------|------|------|---------|
| qwen-turbo | 文本 | 0.002 | 200ms | 7.5 | 简单对话 |
| qwen-plus | 文本 | 0.01 | 500ms | 8.5 | 通用任务 |
| qwen-max | 文本 | 0.02 | 800ms | 9.2 | 深度分析 |
| qwen-coder | 代码 | 0.02 | 1000ms | 9.0 | 编程 |
| glm-edge | 文本 | 0.001 | 150ms | 7.0 | 快速响应 |
| glm-4-plus | 文本 | 0.015 | 600ms | 8.8 | 长上下文 |
| gpt-4o-mini | 文本 | 0.008 | 400ms | 8.5 | 通用 |
| gpt-4o | 多模态 | 0.05 | 1200ms | 9.5 | 复杂推理 |

---

## 🛠️ 技能配置

### 可用技能类型

1. **tool** - 调用本地技能（如文件读写、Excel 处理）
2. **function** - 调用函数接口
3. **http** - 调用外部 API

### 技能配置示例

```yaml
skills:
  # 文件操作技能
  - name: file-reader
    type: tool
    config:
      supported_formats: [txt, md, json, yaml]
      max_size_mb: 10
  
  # Excel 处理技能
  - name: excel-analyzer
    type: tool
    config:
      operations: [read, write, pivot, chart]
  
  # 网络搜索技能
  - name: web-search
    type: http
    config:
      engine: google
      max_results: 5
  
  # 翻译技能
  - name: translator
    type: function
    config:
      languages: [zh, en, jp, kr]
```

---

## 📦 预设场景模板

系统提供常见场景的预设模板，一键生成完整团队：

### 电商运营团队
```yaml
name: 电商全栈运营
roles:
  - 标题优化师 (qwen-plus)
  - 产品摄影师 (qwen-image-max)
  - 客服机器人 (glm-edge)
  - 数据分析师 (qwen-max)
```

### 内容创作者团队
```yaml
name: 自媒体达人组合
roles:
  - 文案专家 (qwen-max)
  - 视频脚本师 (gpt-4o-mini)
  - 封面设计师 (qwen-image-max)
  - 多语言翻译 (qwen-plus)
```

### 开发团队
```yaml
name: 全栈开发组
roles:
  - Python 专家 (qwen-coder)
  - 前端工程师 (gpt-4o)
  - 测试工程师 (qwen-plus)
  - 文档撰写员 (qwen-turbo)
```

---

## 💰 成本优化技巧

### 1. 混合模型策略
```yaml
# 简单任务用便宜模型
quick_replies: glm-edge     # ¥0.001/1K

# 核心任务用高质量模型
main_content: qwen-max      # ¥0.02/1K

# 图片任务专用模型
image_gen: qwen-image-max   # ¥0.08/张
```

### 2. 按优先级降级
```yaml
fallback_chain:
  primary: gpt-4o          # 首选
  backup: qwen-max         # 备用
  emergency: qwen-turbo    # 保底
```

### 3. 批量处理省钱
```bash
# 使用 qwen-turbo 做预处理
批量分类 → ¥0.002/条

# 再精选后用 qwen-max 深加工
深度改写 → ¥0.02/条

总成本降低 70%！
```

---

## 🔧 高级配置

### 1. 条件触发器
```yaml
triggers:
  - condition: "input_length > 1000"
    action: "switch_model_to_long_context"
  
  - condition: "urgency == high"
    action: "use_fastest_model"
  
  - condition: "cost_budget < 0.1"
    action: "fallback_to_cheapest"
```

### 2. 学习反馈机制
```yaml
learning:
  enabled: true
  feedback_weight: 0.3
  auto_adjust:
    - metric: "user_satisfaction"
      threshold: 4.0
      action: "upgrade_model_if_below"
```

### 3. A/B 测试
```yaml
ab_test:
  enabled: true
  variants:
    - name: "qwen_max_version"
      model: qwen-max
      weight: 0.5
    - name: "gpt4o_version"
      model: gpt-4o
      weight: 0.5
```

---

## 📊 监控与统计

```python
from scripts.monitoring import RoleMonitor

monitor = RoleMonitor()

# 查看各角色使用情况
stats = monitor.get_usage_stats()
print(stats)
"""
📊 角色使用统计 (最近 7 天)
┌─────────────────┬──────┬───────┬───────┐
│ 角色名         │ 调用 │ 平均分 │ 成本   │
├─────────────────┼──────┼───────┼───────┤
│ 网文写手        │ 234  │ 9.2   │ ¥4.68 │
│ Python 工程师    │ 156  │ 9.5   │ ¥3.12 │
│ 数据分析师      │ 89   │ 8.8   │ ¥2.24 │
└─────────────────┴──────┴───────┴───────┘
"""

# 成本分析报告
monitor.generate_cost_report()
"""
💰 成本控制建议
• 将"简单客服"从 qwen-plus 切换到 glm-edge
  预计节省：¥12.5/月
  
• 批量任务使用 qwen-turbo 预处理
  预计节省：¥8.3/月
  
总计可节省：¥20.8/月 (42%)
"""
```

---

## 🆘 常见问题

**Q: 如何知道该选哪个模型？**  
A: 让系统智能推荐！`recommend_model(task_type, "balance")`

**Q: 自定义角色后原版的还能用吗？**  
A: 当然！新角色和旧角色共存，互不影响

**Q: 如何分享我的角色配置给其他人？**  
A: 直接分享 `~/.copaw/lingxi_roles/*.yaml` 文件即可

**Q: 角色配置错误会怎样？**  
A: 系统会自动校验并提供友好的错误提示

---

## 🎯 下一步计划

- [ ] 图形化角色配置界面
- [ ] 角色市场（下载他人分享的配置）
- [ ] AI 辅助生成角色配置
- [ ] 性能基准测试工具
- [ ] 团队协作共享配置

---

## 💋 写在最后

老板～这个版本让你真正成为**AI 团队的 CEO**！每个使用者都能根据自己的业务场景，定制专属的专家团队。

需要我帮你创建一个适合你业务的角色配置吗？告诉我你在用什么场景，我给你量身打造！😘
