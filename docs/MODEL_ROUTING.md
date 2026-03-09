# 灵犀 v3.0.1 - 智能模型路由配置指南

## 📊 阿里云百炼模型矩阵 (官方特性)

| 模型 | 文本生成 | 深度思考 | 视觉理解 | 成本 | 速度 | 上下文 | 推荐场景 |
|------|---------|---------|---------|------|------|--------|---------|
| **qwen3.5-plus** | ✓ | ✓ | ✓ | ⭐⭐ | ⚡⚡ | 32K | 🎯 全能均衡，图像理解 |
| **qwen3-max-2026-01-23** | ✓ | ✓ | ✗ | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | 65K | 🧠 复杂推理，重要决策 |
| **qwen3-coder-next** | ✓ | ✗ | ✗ | ⭐⭐ | ⚡⚡⚡⚡⚡ | 32K | 💻 轻量代码，快速生成 |
| **qwen3-coder-plus** | ✓ | ✗ | ✗ | ⭐⭐⭐⭐ | ⚡⚡⚡ | 65K | 💻 专业代码，架构设计 |
| **glm-5** | ✓ | ✓ | ✗ | ⭐⭐⭐ | ⚡⚡ | 128K | 📚 中文深度，长文本 |
| **glm-4.7** | ✓ | ✓ | ✗ | ⭐ | ⚡⚡⚡⚡⚡ | 32K | 💰 性价比，高频调用 |
| **kimi-k2.5** | ✓ | ✓ | ✓ | ⭐⭐⭐ | ⚡⚡⚡ | 200K | 📄 超长文本，图像理解 |
| **MiniMax-M2.5** | ✓ | ✓ | ✗ | ⭐⭐ | ⚡⚡ | 32K | 🎭 创意对话，角色扮演 |

---

## 🎯 智能路由策略

### 1. 根据任务特性选择

#### 需要深度思考的任务
```
✅ 推荐：qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5
❌ 避免：qwen3-coder-next, qwen3-coder-plus

场景：复杂分析、专业咨询、逻辑推理、决策建议
```

#### 需要视觉理解的任务
```
✅ 推荐：qwen3.5-plus, kimi-k2.5
❌ 避免：其他模型（不支持视觉）

场景：图片分析、图像识别、截图理解、视觉问答
```

#### 代码生成任务
```
✅ 轻量快速：qwen3-coder-next
✅ 专业复杂：qwen3-coder-plus
⚠️ 架构设计：qwen3-max (需要深度思考)

场景：脚本编写、代码补全、系统开发、架构设计
```

#### 性价比优先任务
```
✅ 首选：glm-4.7 (最便宜 + 最快)
✅ 均衡：qwen3.5-plus

场景：日常对话、简单问答、高频调用
```

#### 长文本处理
```
✅ 超长文档：kimi-k2.5 (200K 上下文)
✅ 长文本：glm-5 (128K 上下文)

场景：论文阅读、合同审查、多文档分析
```

---

### 2. 优先级模式

```python
# 平衡模式（默认）- 综合考虑质量、速度、成本
result = route_model(user_input, priority="balanced")

# 质量优先 - 不惜成本追求最佳效果
result = route_model(user_input, priority="quality")
# → 优先选择：qwen3-max, qwen3-coder-plus

# 速度优先 - 快速响应优先
result = route_model(user_input, priority="speed")
# → 优先选择：glm-4.7, qwen3-coder-next

# 经济优先 - 成本敏感场景
result = route_model(user_input, priority="economy")
# → 优先选择：glm-4.7
```

---

### 3. 场景化配置

#### 场景 1: 日常对话 (QQ/微信)
```yaml
channel: qqbot
priority: speed
max_cost: 2
require_speed: true
推荐模型：glm-4.7 (首选), qwen3.5-plus
理由：快速 + 便宜，支持深度思考
```

#### 场景 2: 内容创作 (小红书/公众号)
```yaml
channel: xiaohongshu
priority: quality
max_cost: 4
require_speed: false
推荐模型：MiniMax-M2.5 (首选), qwen3-max
理由：创意写作强，支持深度思考
```

#### 场景 3: 代码开发
```yaml
channel: discord
priority: balanced
task_type: code

# 轻量代码
- qwen3-coder-next (简单脚本、快速原型)

# 专业代码
- qwen3-coder-plus (复杂项目、架构设计)
```

#### 场景 4: 文档分析
```yaml
channel: feishu
priority: balanced
task_type: document
推荐模型：kimi-k2.5 (首选), glm-5
理由：超长上下文，支持深度思考 + 视觉理解
```

#### 场景 5: 专业咨询
```yaml
channel: wechat
priority: quality
max_cost: 5
task_type: professional
推荐模型：qwen3-max (首选), glm-5
理由：深度思考能力强，输出质量高
```

#### 场景 6: 图像理解
```yaml
channel: qqbot
task_type: vision
推荐模型：qwen3.5-plus (首选), kimi-k2.5
理由：仅这两个模型支持视觉理解
```

---

## 🔧 代码示例

### 基础使用

```python
from scripts.model_router import get_model_router, route_model

router = get_model_router()

# 自动路由
result = route_model("帮我写个 Python 脚本")
print(f"推荐模型：{result.model_name}")  # → qwen3-coder-next
print(f"任务类型：{result.task_type.value}")  # → code_generation
print(f"置信度：{result.confidence:.1%}")
print(f"理由：{result.reason}")
```

### 不同优先级对比

```python
# 同一任务，不同优先级
user_input = "分析一下这个财务报表"

# 平衡模式
result = route_model(user_input, priority="balanced")
# → glm-5 (成本适中，深度思考强)

# 质量优先
result = route_model(user_input, priority="quality")
# → qwen3-max (最高质量)

# 速度优先
result = route_model(user_input, priority="speed")
# → glm-4.7 (最快响应)

# 经济优先
result = route_model(user_input, priority="economy")
# → glm-4.7 (最便宜)
```

### 视觉理解任务

```python
# 图片分析任务
result = route_model("帮我看看这张图片里有什么")
# → qwen3.5-plus (支持视觉理解)

result = route_model("分析这张截图的内容")
# → kimi-k2.5 (支持视觉理解 + 长上下文)
```

---

## 📈 路由决策流程

```
用户输入
    ↓
意图识别 (TaskType Detection)
    ↓
匹配任务模式 (GREETING/CODE/CREATIVE/VISION/...)
    ↓
检查特殊需求:
  - 需要视觉理解？→ qwen3.5-plus, kimi-k2.5
  - 需要深度思考？→ qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5
  - 代码任务？→ qwen3-coder-next/plus
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
QQ_CONFIG = {
    "priority": "speed",
    "max_cost": 2,
    "require_speed": True,
    "default_model": "glm-4.7",  # 最便宜 + 最快
}
```

### 小红书 (高质量创作)
```python
XHS_CONFIG = {
    "priority": "quality",
    "max_cost": 4,
    "require_speed": False,
    "default_model": "MiniMax-M2.5",  # 创意写作强
}
```

### 飞书文档 (专业分析)
```python
FEISHU_CONFIG = {
    "priority": "balanced",
    "max_cost": 5,
    "require_speed": False,
    "default_model": "qwen3-max-2026-01-23",  # 深度思考强
}
```

### 代码助手
```python
CODER_CONFIG = {
    "priority": "balanced",
    "task_type": "code",
    "lightweight_model": "qwen3-coder-next",  # 简单代码
    "professional_model": "qwen3-coder-plus",  # 复杂代码
}
```

### 视觉助手
```python
VISION_CONFIG = {
    "priority": "balanced",
    "task_type": "vision",
    "default_model": "qwen3.5-plus",  # 视觉理解 + 均衡
    "long_context_model": "kimi-k2.5",  # 视觉 + 长文本
}
```

---

## 📊 性能对比

### 响应时间 (平均值)

| 模型 | Layer 0 | Layer 1 | Layer 2/3 |
|------|---------|---------|-----------|
| glm-4.7 | <5ms | <10ms | ~200ms |
| qwen3-coder-next | <5ms | <10ms | ~250ms |
| qwen3.5-plus | <5ms | <10ms | ~300ms |
| MiniMax-M2.5 | <5ms | <10ms | ~400ms |
| glm-5 | <5ms | <10ms | ~450ms |
| qwen3-coder-plus | <5ms | <10ms | ~500ms |
| kimi-k2.5 | <5ms | <10ms | ~600ms |
| qwen3-max | <5ms | <10ms | ~800ms |

### 成本对比 (相对值，1K tokens)

| 模型 | 成本 | 推荐用法 |
|------|------|---------|
| glm-4.7 | ¥0.001 | 日常对话、简单问答、高频调用 |
| qwen3.5-plus | ¥0.002 | 通用任务、图像理解、多模态 |
| qwen3-coder-next | ¥0.002 | 轻量代码、快速原型 |
| MiniMax-M2.5 | ¥0.002 | 创意写作、角色扮演 |
| glm-5 | ¥0.003 | 长文本、中文深度任务 |
| kimi-k2.5 | ¥0.003 | 超长文档、图像理解 |
| qwen3-coder-plus | ¥0.004 | 专业代码、架构设计 |
| qwen3-max | ¥0.005 | 重要决策、专业咨询 |

---

## 💡 最佳实践

### 1. 分层使用策略

```
Layer 0/1: 规则匹配 + 缓存 → 零成本
Layer 2: 简单任务 → glm-4.7 (最便宜)
Layer 3: 复杂任务 → 根据类型选择
  - 代码：qwen3-coder-next/plus
  - 创作：MiniMax-M2.5
  - 分析：qwen3-max, glm-5
  - 文档：kimi-k2.5
  - 视觉：qwen3.5-plus, kimi-k2.5
```

### 2. 动态调整策略

```python
# 根据用户反馈调整优先级
if user_satisfaction < 0.8:
    priority = "quality"  # 降低满意度时提升质量
elif response_time > 1000:
    priority = "speed"    # 响应慢时提升速度
elif daily_budget_exceeded:
    priority = "economy"  # 预算超支时控制成本
```

### 3. 任务类型优化表

| 任务类型 | 推荐模型 | 优先级 | 原因 |
|---------|---------|--------|------|
| 问候/告别 | glm-4.7 | speed | 简单、频繁、要求快 |
| 情感陪伴 | MiniMax-M2.5 | quality | 情感表达强 |
| 代码生成 (简单) | qwen3-coder-next | speed | 快速生成 |
| 代码生成 (复杂) | qwen3-coder-plus | quality | 专业性强 |
| 文案创作 | MiniMax-M2.5 | quality | 创意性强 |
| 文档总结 | kimi-k2.5 | balanced | 超长上下文 |
| 图片分析 | qwen3.5-plus | balanced | 视觉理解 |
| 专业咨询 | qwen3-max | quality | 深度思考强 |
| 日常对话 | glm-4.7 | economy | 性价比最高 |

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
#    支持特性：文本生成
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
#   - glm-4.7: 400 次 (日常对话)
#   - qwen3.5-plus: 200 次 (通用任务 + 视觉)
#   - MiniMax-M2.5: 150 次 (创意写作)
#   - qwen3-coder-next: 100 次 (代码生成)
#   - qwen3-max: 100 次 (专业咨询)
#   - kimi-k2.5: 50 次 (长文档)
```

---

## ⚠️ 注意事项

### 1. 视觉理解限制
只有 **qwen3.5-plus** 和 **kimi-k2.5** 支持视觉理解，其他模型无法处理图片相关任务。

### 2. 深度思考能力
以下模型支持深度思考：
- ✅ qwen3.5-plus, qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5
- ❌ qwen3-coder-next, qwen3-coder-plus (专注代码生成)

### 3. 成本控制
设置 `max_cost` 避免意外超支：
```python
result = route_model(user_input, max_cost=3)  # 最多使用中等成本模型
```

### 4. 速度要求
实时对话场景设置 `require_speed=True`：
```python
result = route_model(user_input, require_speed=True)
```

### 5. 质量保障
重要任务使用 `priority="quality"`：
```python
result = route_model(user_input, priority="quality")
```

---

## 📝 更新日志

### v3.0.1 (2026-03-09)
- ✨ 新增智能模型路由系统
- 🎯 支持 8 种阿里云百炼模型
- 📊 基于官方特性配置 (文本生成/深度思考/视觉理解)
- 🔧 4 种优先级策略 (balanced/quality/speed/economy)
- 👁️ 新增视觉理解任务支持
- 💻 代码任务细分为轻量/专业两级
- 📚 完善配置文档和示例

---

## 🎯 快速参考卡

```
┌─────────────────────────────────────────────────────────────┐
│  任务类型          │  首选模型          │  备选模型        │
├─────────────────────────────────────────────────────────────┤
│  日常对话          │  glm-4.7          │  qwen3.5-plus    │
│  情感陪伴          │  MiniMax-M2.5     │  qwen3.5-plus    │
│  创意写作          │  MiniMax-M2.5     │  qwen3-max       │
│  代码生成 (轻)     │  qwen3-coder-next │  -               │
│  代码生成 (专)     │  qwen3-coder-plus │  qwen3-max       │
│  专业咨询          │  qwen3-max        │  glm-5           │
│  长文档分析        │  kimi-k2.5        │  glm-5           │
│  图片分析          │  qwen3.5-plus     │  kimi-k2.5       │
│  性价比优先        │  glm-4.7          │  -               │
│  质量优先          │  qwen3-max        │  qwen3-coder-plus│
└─────────────────────────────────────────────────────────────┘
```

---

**🎯 灵犀 - 心有灵犀，一点就通**
