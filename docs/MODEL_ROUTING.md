# 灵犀 v3.0.1 - 智能模型路由配置指南

## 📊 阿里云百炼模型矩阵

| 模型 | 擅长领域 | 成本 | 速度 | 上下文 | 推荐场景 |
|------|---------|------|------|--------|---------|
| **qwen3.5-plus** | 通用任务、日常对话 | ⭐⭐ | ⚡⚡ | 32K | 日常对话、简单查询、一般文案 |
| **qwen3-max-2026-01-23** | 复杂推理、高质量创作 | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | 65K | 重要决策、复杂分析、专业建议 |
| **qwen3-coder-next** | 代码生成、快速编程 | ⭐⭐ | ⚡⚡ | 32K | 代码生成、Debug、脚本编写 |
| **qwen3-coder-plus** | 复杂编程、架构设计 | ⭐⭐⭐⭐ | ⚡⚡⚡ | 65K | 大型项目、架构设计、系统重构 |
| **glm-5** | 中文理解、长文本 | ⭐⭐⭐ | ⚡⚡ | 128K | 中文任务、知识查询、文档理解 |
| **glm-4.7** | 性价比中文任务 | ⭐ | ⚡⚡⚡⚡⚡ | 32K | 简单问答、日常聊天、低成本任务 |
| **kimi-k2.5** | 超长文本、文件处理 | ⭐⭐⭐ | ⚡⚡⚡ | 200K | 长文档、多文件分析、资料汇总 |
| **MiniMax-M2.5** | 创意内容、角色扮演 | ⭐⭐ | ⚡⚡ | 32K | 创意写作、角色扮演、营销文案 |

---

## 🎯 智能路由策略

### 1. 优先级模式

```python
# 平衡模式（默认）- 综合考虑质量、速度、成本
result = route_model(user_input, priority="balanced")

# 质量优先 - 不惜成本追求最佳效果
result = route_model(user_input, priority="quality")

# 速度优先 - 快速响应优先
result = route_model(user_input, priority="speed")

# 经济优先 - 成本敏感场景
result = route_model(user_input, priority="economy")
```

### 2. 场景化配置

#### 场景 1: 日常对话 (QQ/微信)
```yaml
channel: qqbot
priority: speed
max_cost: 2
require_speed: true
推荐模型：glm-4.7, qwen3.5-plus
```

#### 场景 2: 内容创作 (小红书/公众号)
```yaml
channel: xiaohongshu
priority: quality
max_cost: 4
require_speed: false
推荐模型：MiniMax-M2.5, qwen3-max-2026-01-23
```

#### 场景 3: 代码开发
```yaml
channel: discord
priority: quality
task_type: code
推荐模型：qwen3-coder-plus, qwen3-coder-next
```

#### 场景 4: 文档分析
```yaml
channel: feishu
priority: balanced
task_type: document
推荐模型：kimi-k2.5, glm-5
```

#### 场景 5: 专业咨询
```yaml
channel: wechat
priority: quality
max_cost: 5
task_type: professional
推荐模型：qwen3-max-2026-01-23, glm-5
```

---

## 🔧 代码示例

### 基础使用

```python
from scripts.model_router import get_model_router, route_model

router = get_model_router()

# 自动路由
result = route_model("帮我写个 Python 脚本")
print(f"推荐模型：{result.model_name}")
print(f"任务类型：{result.task_type.value}")
print(f"置信度：{result.confidence:.1%}")
print(f"理由：{result.reason}")
```

### 集成到 Orchestrator

```python
from scripts.orchestrator_v2 import get_orchestrator

orchestrator = get_orchestrator()

# 使用不同优先级执行
await orchestrator.execute("写一个小红书文案", model_priority="quality")
await orchestrator.execute("在吗", model_priority="economy")
await orchestrator.execute("帮我 debug 这段代码", model_priority="speed")
```

### 自定义路由规则

```python
from scripts.model_router import MODEL_REGISTRY, ModelTier

# 查看模型配置
for model_id, config in MODEL_REGISTRY.items():
    print(f"{config.name}:")
    print(f"  擅长：{', '.join(config.strengths)}")
    print(f"  成本：{'⭐' * config.cost_level}")
    print(f"  速度：{'⚡' * config.speed_level}")
```

---

## 📈 路由决策流程

```
用户输入
    ↓
意图识别 (TaskType Detection)
    ↓
匹配任务模式 (GREETING/CODE/CREATIVE/...)
    ↓
获取推荐模型列表
    ↓
应用优先级策略 (balanced/quality/speed/economy)
    ↓
应用约束 (max_cost/require_speed)
    ↓
输出最优模型 + 备选模型
```

---

## 🎛️ 渠道配置示例

### QQ Bot (快速响应)
```python
# 渠道特定配置
QQ_CONFIG = {
    "priority": "speed",
    "max_cost": 2,
    "require_speed": True,
    "default_model": "glm-4.7",
}
```

### 小红书 (高质量创作)
```python
XHS_CONFIG = {
    "priority": "quality",
    "max_cost": 4,
    "require_speed": False,
    "default_model": "MiniMax-M2.5",
}
```

### 飞书文档 (专业分析)
```python
FEISHU_CONFIG = {
    "priority": "balanced",
    "max_cost": 5,
    "require_speed": False,
    "default_model": "qwen3-max-2026-01-23",
}
```

---

## 📊 性能对比

### 响应时间 (平均值)

| 模型 | Layer 0 | Layer 1 | Layer 2/3 |
|------|---------|---------|-----------|
| glm-4.7 | <5ms | <10ms | ~200ms |
| qwen3.5-plus | <5ms | <10ms | ~300ms |
| MiniMax-M2.5 | <5ms | <10ms | ~400ms |
| qwen3-max | <5ms | <10ms | ~800ms |
| kimi-k2.5 | <5ms | <10ms | ~600ms |

### 成本对比 (相对值)

| 模型 | 1K tokens | 推荐用法 |
|------|-----------|---------|
| glm-4.7 | ¥0.001 | 日常对话、简单问答 |
| qwen3.5-plus | ¥0.002 | 通用任务、多轮对话 |
| MiniMax-M2.5 | ¥0.002 | 创意写作、角色扮演 |
| qwen3-coder-next | ¥0.002 | 代码生成、Debug |
| glm-5 | ¥0.003 | 长文本、知识问答 |
| kimi-k2.5 | ¥0.003 | 超长文档、多文件 |
| qwen3-coder-plus | ¥0.004 | 复杂编程、架构 |
| qwen3-max | ¥0.005 | 重要决策、专业咨询 |

---

## 💡 最佳实践

### 1. 分层使用

- **Layer 0/1**: 使用规则匹配和缓存，零成本
- **Layer 2**: 简单任务使用经济型模型 (glm-4.7)
- **Layer 3**: 复杂任务使用高级模型 (qwen3-max)

### 2. 动态调整

```python
# 根据用户反馈调整优先级
if user_satisfaction < 0.8:
    priority = "quality"  # 降低满意度时提升质量
elif response_time > 1000:
    priority = "speed"    # 响应慢时提升速度
elif daily_budget_exceeded:
    priority = "economy"  # 预算超支时控制成本
```

### 3. 任务类型优化

| 任务类型 | 推荐模型 | 优先级 | 原因 |
|---------|---------|--------|------|
| 问候/告别 | glm-4.7 | speed | 简单、频繁、要求快 |
| 情感陪伴 | MiniMax-M2.5 | quality | 需要情感表达 |
| 代码生成 | qwen3-coder-next | quality | 专业性要求高 |
| 文案创作 | MiniMax-M2.5 | quality | 创意性要求高 |
| 文档总结 | kimi-k2.5 | balanced | 长文本处理强 |
| 专业咨询 | qwen3-max | quality | 准确性第一 |

---

## 🔍 调试与监控

### 查看路由日志

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 路由时会输出：
# 🎯 智能路由：通义千问 Coder Next (置信度：85.0%)
#    任务类型：code_generation
#    选择理由：平衡模式：qwen3-coder-next 在 code_generation 任务中表现优秀
```

### 统计信息

```python
from scripts.orchestrator_v2 import get_orchestrator

orchestrator = get_orchestrator()
print(orchestrator.get_stats())

# 输出：
# 📊 灵犀运行统计
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 总请求数：1000
# 快速响应命中：650 (65.0%)
# 平均耗时：245.3ms
# 模型分布：
#   - glm-4.7: 400 次
#   - qwen3.5-plus: 300 次
#   - MiniMax-M2.5: 150 次
#   - qwen3-coder-next: 100 次
#   - qwen3-max: 50 次
```

---

## ⚠️ 注意事项

1. **成本控制**: 设置 `max_cost` 避免意外超支
2. **速度要求**: 实时对话场景设置 `require_speed=True`
3. **质量保障**: 重要任务使用 `priority="quality"`
4. **模型降级**: 当首选模型不可用时自动降级到备选
5. **监控告警**: 定期检查模型使用分布和成本

---

## 📝 更新日志

### v3.0.1 (2026-03-09)
- ✨ 新增智能模型路由系统
- 🎯 支持 8 种阿里云百炼模型
- 📊 4 种优先级策略 (balanced/quality/speed/economy)
- 🔧 集成到 Orchestrator v2
- 📚 完善配置文档和示例

---

**🎯 灵犀 - 心有灵犀，一点就通**
