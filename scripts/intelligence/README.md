# 🧠 灵犀智能学习系统

> **灵犀 2.3.0 核心功能** - 让灵犀越用越聪明 ✨

---

## 🎯 核心功能

### 1. 任务日志记录 (TaskLogger)
- 结构化存储任务执行数据
- 按日期分文件（JSONL 格式）
- 支持查询和统计
- 内存缓存（最近 100 条）

### 2. 模式学习 (PatternLearner)
- 频率分析（次/天）
- 时间模式识别（偏好小时段）
- 模型偏好学习
- 成本模式分析
- 优化建议生成

### 3. 自动优化 (Optimizer)
- 模型推荐（根据任务复杂度）
- Token 成本预估
- 执行耗时预估
- 并行/串行建议
- 缓存策略建议
- 成本优化报告

### 4. 预测调度 (Predictor)
- 时间模式预测
- 资源预加载
- 智能提醒
- 自动优化

---

## 📁 文件结构

```
scripts/intelligence/
├── __init__.py           # 主入口，IntelligenceEngine
├── task_logger.py        # 任务日志记录器
├── pattern_learner.py    # 模式学习器
├── optimizer.py          # 优化器
└── predictor.py          # 预测调度器
```

---

## 🚀 快速开始

### 1. 初始化

```python
from intelligence import IntelligenceEngine

engine = IntelligenceEngine()

# 初始化（分析最近 7 天数据）
engine.initialize(analyze_days=7)
```

### 2. 记录任务

```python
task_id = engine.log_task(
    task_type="content_creation",
    user_id="user123",
    input_text="帮我写个小红书文案",
    output_text="文案内容...",
    model_used="qwen-plus",
    token_cost=500,
    duration_ms=1200,
    success=True
)
```

### 3. 获取优化建议

```python
optimization = engine.get_optimization(
    task_type="content_creation",
    input_text="帮我写个小红书文案，关于 AI 助手的"
)

print(f"推荐模型：{optimization['suggested_model']}")
print(f"预估成本：{optimization['estimated_cost']} token")
print(f"预估耗时：{optimization['estimated_duration_ms']/1000:.1f}s")
```

### 4. 预测下一个任务

```python
prediction = engine.predict_next_task("user123")

if prediction:
    print(f"最可能任务：{prediction['task_type']}")
    print(f"概率：{prediction['probability']:.1%}")
    print(f"预计时间：{prediction['estimated_time']}")
    print(f"置信度：{prediction['confidence']}")
```

### 5. 生成报告

```python
report = engine.generate_report(days=7)
print(report)
```

---

## 📊 使用示例

### 完整流程

```python
from intelligence import IntelligenceEngine
from datetime import datetime

# 创建引擎
engine = IntelligenceEngine()

# 初始化
engine.initialize(analyze_days=7)

# 记录任务
task_id = engine.log_task(
    task_type="content_creation",
    user_id="user123",
    input_text="帮我写个小红书文案",
    output_text="文案内容...",
    model_used="qwen-plus",
    token_cost=500,
    duration_ms=1200,
    success=True
)

# 获取优化建议
optimization = engine.get_optimization(
    task_type="content_creation",
    input_text="帮我写个小红书文案"
)

# 预测下一个任务
prediction = engine.predict_next_task("user123")

# 生成报告
report = engine.generate_report(days=7)
print(report)
```

---

## 🎯 任务类型

支持的任务类型：

| 类型 | 说明 | 示例 |
|------|------|------|
| `content_creation` | 内容创作 | 写文案、写文章 |
| `image_generation` | 图片生成 | 生成图片、自拍 |
| `social_publish` | 社交发布 | 发小红书、发公众号 |
| `coding` | 编程开发 | 写代码、脚本 |
| `data_analysis` | 数据分析 | 报表、统计 |
| `search` | 搜索查询 | 搜索信息 |
| `translation` | 翻译 | 中英文翻译 |
| `reminder` | 提醒 | 定时提醒 |
| `chat` | 聊天 | 日常对话 |

---

## 📈 性能指标

### 预期效果

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 任务执行速度 | 100% | 150% | +50% |
| Token 成本 | 100% | 70% | -30% |
| 预测准确率 | 0% | 80% | +80% |

### 实际效果（需要数据积累）

- **7 天后：** 初步模式识别
- **14 天后：** 准确预测偏好
- **30 天后：** 高度个性化优化

---

## 🔧 配置选项

### 日志存储路径

```python
# 默认：~/.openclaw/workspace/task-logs/
logger = TaskLogger(log_path="~/.openclaw/workspace/task-logs/")
```

### 模式存储路径

```python
# 默认：~/.openclaw/workspace/patterns/
learner = PatternLearner(pattern_path="~/.openclaw/workspace/patterns/")
```

### 分析天数

```python
# 默认：7 天
engine.initialize(analyze_days=14)  # 分析 14 天
```

---

## 💡 最佳实践

### 1. 持续记录

每次任务执行后都记录日志，数据越多越准确。

```python
# 在任务完成后立即记录
task_id = engine.log_task(...)
```

### 2. 定期分析

每天或每周分析一次模式。

```python
# 每天分析
engine.learner.analyze_patterns(days=1)
```

### 3. 实时优化

在执行任务前获取优化建议。

```python
# 执行前优化
optimization = engine.get_optimization(task_type, input_text)
# 使用推荐模型
model = optimization['suggested_model']
```

### 4. 智能提醒

利用预测功能提前准备。

```python
# 检查是否需要提醒
reminder = engine.should_remind(advance_minutes=30)
if reminder:
    send_notification(reminder)
```

---

## 📝 数据存储

### 任务日志

**位置：** `~/.openclaw/workspace/task-logs/YYYY-MM-DD.jsonl`

**格式：** JSONL（每行一个 JSON 对象）

```json
{
  "task_id": "abc123",
  "task_type": "content_creation",
  "user_id": "user123",
  "input_text": "帮我写个小红书文案",
  "output_text": "文案内容...",
  "model_used": "qwen-plus",
  "token_cost": 500,
  "duration_ms": 1200,
  "success": true,
  "timestamp": "2026-03-03T16:00:00",
  "feedback": null
}
```

### 模式数据

**位置：** `~/.openclaw/workspace/patterns/patterns.json`

**格式：** JSON

```json
{
  "content_creation": {
    "task_type": "content_creation",
    "frequency": 2.5,
    "preferred_hours": [14, 15, 16],
    "preferred_model": "qwen-plus",
    "avg_token_cost": 450,
    "avg_duration_ms": 1100,
    "success_rate": 0.95,
    "last_executed": "2026-03-03T16:00:00",
    "total_executions": 35
  }
}
```

---

## 🚨 注意事项

### 1. 隐私保护

- 任务日志包含用户输入和输出
- 确保存储路径安全
- 不要上传到公开仓库

### 2. 数据清理

定期清理旧日志，避免占用过多空间。

```bash
# 清理 30 天前的日志
find ~/.openclaw/workspace/task-logs/ -name "*.jsonl" -mtime +30 -delete
```

### 3. 性能影响

- 日志记录异步执行，不影响主流程
- 模式分析耗时，建议后台执行
- 缓存机制减少重复计算

---

## 🔮 未来计划

### v2.3.0-alpha (已完成)
- ✅ 任务日志记录
- ✅ 模式学习
- ✅ 自动优化
- ✅ 预测调度

### v2.3.0-beta (计划中)
- [ ] 集成到主编排器
- [ ] 实时优化策略
- [ ] 智能提醒系统

### v2.3.0-release (计划中)
- [ ] 完整测试
- [ ] 性能优化
- [ ] 文档完善

---

## 🙏 致谢

灵犀智能学习系统是灵犀 2.3.0 的核心功能，让灵犀越用越聪明！

**座右铭：** 用最少的资源，做最多的事。✨

---

**GitHub:** https://github.com/AI-Scarlett/lingxi-ai
**版本：** v2.3.0-alpha
