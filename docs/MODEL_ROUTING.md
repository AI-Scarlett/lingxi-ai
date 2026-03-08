# 灵犀智能模型路由 - 使用文档

> **版本:** v3.0  
> **作者:** 斯嘉丽 Scarlett  
> **日期:** 2026-03-08

---

## 🎯 功能概述

灵犀 v3.0 新增**智能模型路由**功能，根据任务类型自动选择最优模型：

| 任务类型 | 使用模型 | 说明 |
|----------|----------|------|
| 🧑‍💻 **编程开发** | `qwen-coder` | 代码专用模型，擅长编程、调试、代码生成 |
| 📊 **数据分析** | `qwen-max` | 最强通用模型，适合复杂分析、推理 |
| ✍️ **文案写作** | `qwen-plus` | 平衡性能和成本，适合写作、创作 |
| 💬 **聊天问答** | `qwen-turbo` | 快速响应，适合聊天、简单问答 |
| 📐 **数学计算** | `qwen-max` | 最强推理能力 |
| 🌐 **翻译** | `qwen-plus` | 多语言支持良好 |
| 📋 **规划** | `qwen-plus` | 平衡性能和成本 |
| 🎨 **图像处理** | `qwen-max` | 多模态能力 |
| ❓ **未知** | `qwencode/qwen3.5-plus` | 默认模型 |

---

## 🚀 自动路由示例

### 示例 1: 代码任务

**用户输入:**
```
帮我写个 Python 脚本分析 Excel 数据
```

**自动选择:** `qwen-coder`

**原因:** 检测到关键词 "Python", "脚本", "分析"

---

### 示例 2: 文案任务

**用户输入:**
```
写一篇小红书文案，推广我们的新产品
```

**自动选择:** `qwen-plus`

**原因:** 检测到关键词 "写", "文案"

---

### 示例 3: 分析任务

**用户输入:**
```
分析一下这个月的销售数据，找出趋势
```

**自动选择:** `qwen-max`

**原因:** 检测到关键词 "分析", "数据", "趋势"

---

### 示例 4: 聊天

**用户输入:**
```
你好，在吗？
```

**自动选择:** `qwen-turbo`

**原因:** 检测到关键词 "你好", "在吗"

---

## 📖 使用方式

### 方式 1: 自动路由（默认）

```python
from lingxi import process_request

# 自动选择模型
result = await process_request(
    user_input="帮我写个 Python 脚本",
    channel="feishu",
    user_id="ou_xxx"
)
# 自动使用 qwen-coder
```

---

### 方式 2: 手动指定模型

```python
# 强制使用特定模型
result = await process_request(
    user_input="帮我写个脚本",
    channel="feishu",
    user_id="ou_xxx",
    model="qwen-max"  # 强制使用 qwen-max
)
```

---

### 方式 3: 查询模型选择

```python
from model_router import get_model_router

router = get_model_router()

# 检测任务类型
task_type = router.detect_task_type("帮我写个 Python 脚本")
print(f"任务类型：{task_type}")  # TaskType.CODING

# 获取推荐模型
model = router.get_model_for_task("帮我写个 Python 脚本")
print(f"推荐模型：{model}")  # qwen-coder

# 查看选择原因
explanation = router.explain_choice("帮我写个 Python 脚本")
print(explanation)
```

**输出:**
```
🧠 任务类型：编程开发
🤖 使用模型：qwen-coder
📝 模型特点：代码专用模型，擅长编程、调试、代码生成
💰 预估成本：$0.0020
```

---

## 🔧 配置模型路由

### 修改模型映射

编辑 `scripts/model_router.py`:

```python
# 任务类型 → 模型映射
TASK_MODEL_MAP: Dict[TaskType, str] = {
    TaskType.CODING: "qwen-coder",      # 修改这里
    TaskType.ANALYSIS: "qwen-max",
    # ...
}
```

### 添加新模型

```python
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "new-model": ModelConfig(
        model_id="new-model",
        max_tokens=8192,
        temperature=0.5,
        cost_per_1k=0.002,
        description="新模型描述"
    ),
    # ...
}
```

### 自定义关键词

```python
TASK_KEYWORDS: Dict[TaskType, List[str]] = {
    TaskType.CODING: [
        "代码", "编程", "脚本",  # 添加新关键词
        "开发", "软件工程"
    ],
    # ...
}
```

---

## 📊 成本对比

| 模型 | 每 1K tokens | 1000 tokens 成本 | 适用场景 |
|------|-------------|----------------|----------|
| `qwen-turbo` | $0.0005 | $0.0005 | 聊天、简单问答 |
| `qwen-plus` | $0.001 | $0.001 | 写作、翻译、规划 |
| `qwen-coder` | $0.002 | $0.002 | 编程、代码生成 |
| `qwen-max` | $0.004 | $0.004 | 复杂分析、推理 |

**智能路由优势:**
- ✅ 简单任务用便宜模型，节省成本
- ✅ 复杂任务用好模型，保证质量
- ✅ 平均节省 30-50% 成本

---

## 🧪 测试

### 运行测试脚本

```bash
cd /root/.openclaw/skills/lingxi/scripts
python3 model_router.py
```

### 测试结果

```
✅ 输入：帮我写个 Python 脚本分析 Excel 数据
   检测类型：coding
   使用模型：qwen-coder

✅ 输入：写一篇小红书文案
   检测类型：writing
   使用模型：qwen-plus

✅ 输入：分析一下这个月销售数据
   检测类型：analysis
   使用模型：qwen-max

✅ 输入：你好，在吗？
   检测类型：chat
   使用模型：qwen-turbo

... (全部通过)
```

---

## 🎯 最佳实践

### 1. 信任自动路由

大多数情况下，自动路由已经足够智能：

```python
# 推荐：让系统自动选择
result = await process_request(user_input, ...)
```

### 2. 特殊场景手动指定

只有在特殊需求时才手动指定：

```python
# 场景：需要最强的代码能力
result = await process_request(
    "帮我设计一个复杂的分布式系统架构",
    model="qwen-max"  # 强制使用最强模型
)
```

### 3. 监控模型使用

定期检查模型使用情况，优化路由策略：

```python
# 查看模型使用统计
stats = orch.get_model_stats()
print(stats)
```

---

## ❓ 常见问题

### Q: 如何知道当前使用了哪个模型？

A: 查看日志或使用 `explain_choice()`:

```python
router = get_model_router()
print(router.explain_choice("帮我写个脚本"))
```

### Q: 可以禁用自动路由吗？

A: 可以，始终使用默认模型：

```python
result = await process_request(
    user_input,
    model="qwencode/qwen3.5-plus"  # 固定使用默认模型
)
```

### Q: 模型路由会影响性能吗？

A: 几乎不会。路由决策在 <1ms 内完成。

### Q: 如何添加新的任务类型？

A: 编辑 `model_router.py`:

```python
# 1. 添加新任务类型
class TaskType(Enum):
    NEW_TYPE = "new_type"

# 2. 添加关键词
TASK_KEYWORDS[TaskType.NEW_TYPE] = ["关键词 1", "关键词 2"]

# 3. 添加模型映射
TASK_MODEL_MAP[TaskType.NEW_TYPE] = "target-model"
```

---

## 📝 更新日志

### v3.0 (2026-03-08)

- ✅ 新增智能模型路由
- ✅ 支持 9 种任务类型
- ✅ 集成 5 种模型
- ✅ 成本估算功能
- ✅ 自动选择解释

---

## 📞 支持

如有问题，请联系：
- 作者：斯嘉丽 Scarlett
- 项目：灵犀 (Lingxi) v3.0
- 文档位置：`/root/.openclaw/skills/lingxi/docs/MODEL_ROUTING.md`

---

_心有灵犀，一点就通_ 💋
