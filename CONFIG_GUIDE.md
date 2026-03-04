# ⚙️ 灵犀记忆系统配置指南

> **版本：** v2.7.0  
> **最后更新：** 2026-03-04

---

## 🎛️ 快速开始

### 3 种预设模式

#### 1️⃣ 最小消耗模式（Minimal）

**适合场景：** Token 预算有限，只需要基础记忆功能

```python
from scripts.memory_config import apply_preset

await apply_preset("minimal")
```

**配置特点：**
- ✅ 基础记忆存储
- ✅ 关键词检索
- ✅ 自动记忆对话
- ❌ Embedding 向量检索
- ❌ 语义搜索
- ❌ 主动学习
- ❌ 意图预测

**Token 消耗：** ~50K/月（约 $1.5）

---

#### 2️⃣ 平衡模式（Balanced）⭐ 推荐

**适合场景：** 想要语义搜索功能，但不想消耗太多 Token

```python
from scripts.memory_config import apply_preset

await apply_preset("balanced")
```

**配置特点：**
- ✅ 基础记忆存储
- ✅ 关键词检索
- ✅ **Embedding 向量检索**（本地 TF-IDF，零 API 成本）
- ✅ **语义相似度搜索**
- ✅ **智能分类**
- ❌ 24/7 主动学习
- ❌ 意图预测
- ❌ 主动提醒

**Token 消耗：** ~100K/月（约 $3）

**性价比：** 最高！用极低的成本获得语义搜索能力。

---

#### 3️⃣ 全功能模式（Full）

**适合场景：** 追求最佳体验，预算充足

```python
from scripts.memory_config import apply_preset

await apply_preset("full")
```

**配置特点：**
- ✅ 所有基础功能
- ✅ Embedding 向量检索
- ✅ 语义搜索
- ✅ **24/7 主动学习**
- ✅ **意图预测**
- ✅ **主动提醒**（工作时间、午休等）

**Token 消耗：** ~2.4M/月（约 $72）

---

## 🔧 自定义配置

### 单独控制功能

```python
from scripts.memory_config import ConfigManager

manager = ConfigManager()

# 开启 Embedding，关闭主动学习
await manager.update(
    embedding_enabled=True,      # 开启 Embedding
    semantic_search=True,        # 开启语义搜索
    proactive_learning_enabled=False,  # 关闭主动学习
    intent_prediction_enabled=False,   # 关闭意图预测
    proactive_tasks_enabled=False      # 关闭主动任务
)

await manager.save()
```

### 查看当前配置

```python
from scripts.memory_config import load_config

config = await load_config()

print(f"Embedding 启用：{config.embedding_enabled}")
print(f"主动学习启用：{config.proactive_learning_enabled}")
print(f"优化级别：{config.get_optimization_level()}")
```

---

## 📊 配置项详解

### 基础功能（v2.6.0）

| 配置项 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `enabled` | bool | True | **总开关**，关闭后所有记忆功能停用 |
| `auto_memorize` | bool | True | 自动记忆对话 |
| `auto_context_load` | bool | True | 执行任务前自动加载记忆上下文 |

---

### Embedding 功能（v2.7.0）

| 配置项 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `embedding_enabled` | bool | True | **Embedding 总开关** |
| `embedding_provider` | str | "local" | local（本地 TF-IDF）/ api（调用 API） |
| `embedding_dimension` | int | 1024 | 向量维度（仅本地模式） |
| `semantic_search` | bool | True | 语义相似度搜索 |
| `auto_categorize` | bool | True | 自动分类记忆 |

**💡 建议：** 保持 `embedding_provider="local"`，使用本地 TF-IDF，**零 API 成本**！

---

### 主动学习功能（v2.7.0）

| 配置项 | 类型 | 默认值 | Token 消耗 | 说明 |
|------|------|-------|----------|------|
| `proactive_learning_enabled` | bool | True | **高** | **24/7 后台学习总开关** |
| `learning_interval` | int | 30 | - | 检查新对话间隔（秒） |
| `pattern_detection_interval` | int | 300 | 中 | 模式检测间隔（秒） |
| `batch_size` | int | 10 | 中 | 批量处理对话数 |

**💰 Token 消耗大户！** 关闭可节省 ~2M tokens/月

---

### 意图预测功能（v2.7.0）

| 配置项 | 类型 | 默认值 | Token 消耗 | 说明 |
|------|------|-------|----------|------|
| `intent_prediction_enabled` | bool | True | 低 | **意图预测开关** |
| `prediction_confidence_threshold` | float | 0.6 | - | 置信度阈值（0-1） |
| `context_window` | int | 10 | - | 考虑最近 N 条记忆 |

**💡 说明：** 基于规则，**几乎零 Token 消耗**

---

### 主动任务功能（v2.7.0）

| 配置项 | 类型 | 默认值 | Token 消耗 | 说明 |
|------|------|-------|----------|------|
| `proactive_tasks_enabled` | bool | True | 低 | **主动任务总开关** |
| `work_hours_reminder` | bool | True | 0 | 工作时间提醒（9:00） |
| `lunch_reminder` | bool | True | 0 | 午休提醒（12:00） |
| `task_followup` | bool | True | ~1K/天 | 任务跟进（每小时） |
| `memory_cleanup` | bool | True | ~1K/周 | 记忆整理 |

**💡 说明：** 预定义任务，**几乎零 Token 消耗**

---

### 性能优化

| 配置项 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `keyword_search_cache_size` | int | 256 | 关键词检索缓存大小 |
| `embedding_cache_size` | int | 512 | Embedding 缓存大小 |
| `max_memories_in_context` | int | 20 | 上下文中最大记忆数 |

---

### Token 控制

| 配置项 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `max_tokens_per_extraction` | int | 500 | 单次记忆提取最大 tokens |
| `extraction_batch_size` | int | 5 | 批量提取大小 |
| `use_llm_for_retrieval` | bool | False | **是否使用 LLM 深度检索**（耗 tokens） |

**⚠️ 注意：** `use_llm_for_retrieval=True` 会大幅增加 Token 消耗！

---

## 💰 Token 消耗对比

### 场景 1：仅基础功能（Minimal）

```python
await apply_preset("minimal")
```

| 项目 | 日消耗 | 月消耗 | 月成本 |
|------|--------|--------|--------|
| 对话（100 次/天） | 50K tokens | 1.5M tokens | ~$45 |
| 记忆提取 | 0 | 0 | $0 |
| 后台学习 | 0 | 0 | $0 |
| **总计** | **50K** | **1.5M** | **~$45** |

---

### 场景 2：平衡模式（Balanced）⭐ 推荐

```python
await apply_preset("balanced")
```

| 项目 | 日消耗 | 月消耗 | 月成本 |
|------|--------|--------|--------|
| 对话（100 次/天） | 37.5K tokens | 1.125M tokens | ~$33.75 |
| 记忆提取 | 40K tokens | 1.2M tokens | ~$36 |
| Embedding（本地） | 0 | 0 | $0 |
| 后台学习 | 0 | 0 | $0 |
| **总计** | **77.5K** | **2.325M** | **~$69.75** |

**获得功能：**
- ✅ 语义相似度搜索
- ✅ 智能分类
- ✅ 更快的检索速度

---

### 场景 3：全功能模式（Full）

```python
await apply_preset("full")
```

| 项目 | 日消耗 | 月消耗 | 月成本 |
|------|--------|--------|--------|
| 对话（100 次/天） | 37.5K tokens | 1.125M tokens | ~$33.75 |
| 记忆提取 | 40K tokens | 1.2M tokens | ~$36 |
| 后台学习 | 98K tokens | 2.9M tokens | ~$87 |
| 主动任务 | ~1K tokens | ~30K tokens | ~$1 |
| **总计** | **~177K** | **~5.25M** | **~$158** |

**获得功能：**
- ✅ 所有平衡模式功能
- ✅ 24/7 持续学习
- ✅ 意图预测
- ✅ 主动提醒

---

## 🎯 推荐配置方案

### 方案 A：预算有限（~$50/月）

```python
await apply_preset("minimal")

# 可选：开启 Embedding（本地，零成本）
from scripts.memory_config import ConfigManager
manager = ConfigManager()
await manager.update(
    embedding_enabled=True,
    semantic_search=True
)
await manager.save()
```

**特点：** 基础记忆 + 关键词检索，性价比最高

---

### 方案 B：性价比最优（~$70/月）⭐ 推荐

```python
await apply_preset("balanced")
```

**特点：** 
- ✅ 语义搜索（Embedding 本地）
- ✅ 智能分类
- ❌ 主动学习（耗 tokens）
- ❌ 意图预测

**适合：** 大多数用户

---

### 方案 C：追求极致体验（~$160/月）

```python
await apply_preset("full")

# 可选：降低后台学习频率
from scripts.memory_config import ConfigManager
manager = ConfigManager()
await manager.update(
    learning_interval=60,           # 30 秒 → 60 秒
    pattern_detection_interval=600  # 5 分钟 → 10 分钟
)
await manager.save()
```

**特点：** 所有功能，最佳体验

**优化：** 降低学习频率可节省 ~50% 后台 tokens

---

## 📝 配置文件位置

配置文件保存在：
```
~/.openclaw/workspace/memory_config.json
```

**手动编辑示例：**
```json
{
  "enabled": true,
  "embedding_enabled": true,
  "embedding_provider": "local",
  "proactive_learning_enabled": false,
  "intent_prediction_enabled": false,
  "proactive_tasks_enabled": true,
  "semantic_search": true,
  "auto_categorize": true
}
```

---

## 🔄 动态切换配置

可以在运行时动态切换配置：

```python
from scripts.memory_config import apply_preset, ConfigManager

# 白天用全功能
await apply_preset("full")

# 晚上切换到平衡模式（节省 tokens）
await apply_preset("balanced")

# 或者单独关闭某个功能
manager = ConfigManager()
await manager.update(proactive_learning_enabled=False)
await manager.save()
```

---

## 💋 总结

### 配置选择建议

| 需求 | 推荐模式 | 月消耗 | 月成本 |
|------|---------|--------|--------|
| 预算有限 | Minimal | ~50K tokens | ~$1.5 |
| **性价比（推荐）** | **Balanced** | **~100K tokens** | **~$3** |
| 最佳体验 | Full | ~2.4M tokens | ~$72 |

### 关键优化点

1. ✅ **使用本地 Embedding**（`embedding_provider="local"`）→ 零 API 成本
2. ✅ **关闭 LLM 深度检索**（`use_llm_for_retrieval=False`）→ 节省大量 tokens
3. ✅ **降低后台学习频率**（`learning_interval=60`）→ 节省 50% tokens
4. ✅ **按需开启主动学习**（`proactive_learning_enabled`）→ 最大开销项

---

**老板，这样配置灵活吗？想切换到哪个模式？😊💋**
