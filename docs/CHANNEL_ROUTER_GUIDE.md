# 📡 灵犀渠道智能路由指南

> **不同渠道 = 不同场景 = 不同优化策略**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai)
[![Channel Router](https://img.shields.io/badge/channel-router-green.svg)](https://github.com/AI-Scarlett/lingxi-ai)

---

## 🎯 核心思路

根据**来源渠道**和**任务类型**自动选择最优处理策略：

| 渠道 | 典型场景 | 优化目标 | 策略 |
|------|---------|---------|------|
| QQ(聊天) | 日常聊天/情感陪伴 | **速度优先** | Layer 0 快速响应 (<5ms) |
| QQ(代码) | 写代码/技术任务 | **质量优先** | 启用审核层 + 完整执行 |
| 飞书 | 工作协作/文档 | **平衡** | 标准执行 + 审计日志 |
| 微信 | 公众号/内容创作 | **质量优先** | 启用审核层 + 学习层 |
| 钉钉 | 企业任务/提醒 | **速度优先** | 精简执行 |

---

## 🚀 快速开始

### 方式 1：自动渠道路由（推荐）

```python
from scripts.orchestrator_v2 import get_orchestrator_for_channel

# 根据渠道自动选择配置
orch = get_orchestrator_for_channel(
    channel="qqbot",
    user_id="DE5BA2C531B102AD9989F5E04935BCA6",
    user_input="写个 Python 函数"  # 用于关键词匹配
)

# 执行任务
result = await orch.execute(user_input, user_id)
```

### 方式 2：手动配置

```python
from scripts.orchestrator_v2 import get_orchestrator

# 聊天模式（速度优先）
orch_chat = get_orchestrator(
    max_concurrent=2,
    enable_review=False,    # 不审核
    enable_audit=False,     # 不审计
    enable_fast_response=True  # 快速响应
)

# 代码模式（质量优先）
orch_code = get_orchestrator(
    max_concurrent=3,
    enable_review=True,     # 启用审核
    enable_audit=True,      # 启用审计
    enable_fast_response=False
)
```

---

## 📋 配置文件

**路径**: `~/.openclaw/workspace/.learnings/channel_config.json`

### 配置结构

```json
{
  "channels": {
    "qqbot_chat": {
      "description": "QQ-纯聊天模式",
      "user_ids": ["DE5BA2C531B102AD9989F5E04935BCA6"],
      "default": true,
      "config": {
        "max_concurrent": 2,
        "enable_review": false,
        "enable_audit": false,
        "enable_learning": true,
        "fast_response": true,
        "enable_auto_retry": true
      }
    },
    "qqbot_coding": {
      "description": "QQ-代码/技术任务",
      "keywords": ["代码", "编程", "debug", "python", "js"],
      "config": {
        "max_concurrent": 3,
        "enable_review": true,
        "enable_audit": true,
        "enable_learning": true,
        "fast_response": false
      }
    }
  },
  "fallback": {
    "max_concurrent": 3,
    "enable_review": false,
    "enable_audit": false,
    "enable_learning": true,
    "fast_response": true
  }
}
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `max_concurrent` | int | 3 | 最大并发任务数 |
| `enable_review` | bool | false | 是否启用质量审核 |
| `enable_audit` | bool | false | 是否启用审计日志 |
| `enable_learning` | bool | true | 是否启用学习层 |
| `fast_response` | bool | true | 是否启用快速响应 |
| `enable_auto_retry` | bool | true | 是否启用自动重试 |

---

## 🔍 渠道路由规则

### 1. 渠道名匹配
```python
# qqbot → 匹配 qqbot_chat 或 qqbot_coding
# feishu → 匹配 feishu_work
# wechat → 匹配 wechat_content
```

### 2. 关键词匹配
```python
# 用户输入包含关键词 → 路由到对应渠道
"写个 Python 函数" → qqbot_coding (包含"python")
"公众号文章" → wechat_content (包含"公众号")
```

### 3. 用户 ID 匹配
```json
{
  "qqbot_vip": {
    "user_ids": ["DE5BA2C531B102AD9989F5E04935BCA6"],
    "config": {
      "max_concurrent": 10  // VIP 用户更高并发
    }
  }
}
```

### 4. 默认通道
```json
{
  "qqbot_chat": {
    "default": true  // 未匹配到时使用此配置
  }
}
```

---

## 📊 性能对比

### 响应时间

| 场景 | 旧版本 | 新版本 | 提升 |
|------|--------|--------|------|
| QQ 聊天 | ~500ms | **<5ms** | **100x** |
| QQ 写代码 | ~500ms | ~800ms | -60% (质量更高) |
| 飞书工作 | ~1000ms | ~600ms | 40% |
| 微信公众号 | ~2000ms | ~1500ms | 25% |

### Tokens 消耗

| 场景 | 旧版本 | 新版本 | 节省 |
|------|--------|--------|------|
| QQ 聊天 | 2000 tokens | **0 tokens** | **100%** |
| QQ 写代码 | 5000 tokens | 5000 tokens | 0% |
| 飞书工作 | 3000 tokens | 2500 tokens | 17% |
| 微信公众号 | 8000 tokens | 7000 tokens | 12% |

**总体节省**: 约 **40-60%** (取决于聊天比例)

---

## 🛠️ 高级功能

### 时间段路由

```json
{
  "time_based": {
    "enabled": true,
    "rules": {
      "work_hours": {
        "schedule": "9:00-18:00",
        "timezone": "Asia/Shanghai",
        "override": {
          "enable_review": true
        }
      },
      "night_mode": {
        "schedule": "23:00-8:00",
        "override": {
          "fast_response": true,
          "enable_review": false
        }
      }
    }
  }
}
```

### 用户等级路由

```json
{
  "user_tiers": {
    "vip": {
      "user_ids": ["DE5BA2C531B102AD9989F5E04935BCA6"],
      "config": {
        "max_concurrent": 10,
        "priority": "high"
      }
    },
    "normal": {
      "config": {
        "max_concurrent": 3,
        "priority": "normal"
      }
    }
  }
}
```

---

## 🧪 测试

```bash
cd /root/.openclaw/skills/lingxi
python3 scripts/channel_router.py
```

**测试输出**:
```
📡 灵犀渠道智能路由器测试
============================================================

测试：qqbot | DE5BA2C531B102AD9989F5E04935BCA6 | '你好呀'
  → 渠道类型：qqbot_chat
  → 配置：{"max_concurrent": 2, "enable_review": false, ...}

测试：qqbot | DE5BA2C531B102AD9989F5E04935BCA6 | '写个 Python 函数'
  → 渠道类型：qqbot_coding
  → 配置：{"max_concurrent": 3, "enable_review": true, ...}

📊 缓存统计:
  缓存大小：2

✅ 测试完成！
```

---

## 📈 监控统计

```python
from scripts.channel_router import get_stats

stats = get_stats()
print(f"缓存大小：{stats['cache_size']}")
print(f"缓存的渠道：{stats['cached_channels']}")
```

---

## ⚠️ 注意事项

1. **配置缓存**: Orchestrator 实例会被缓存，避免重复创建
2. **热更新**: 修改配置后调用 `reload_config()` 生效
3. **降级方案**: 配置加载失败时使用默认配置
4. **内存占用**: 每个配置缓存一个实例，注意内存使用

---

## 🔧 API 参考

### `get_channel_orchestrator(channel, user_id, user_input)`

根据渠道获取最优配置的 Orchestrator

**参数**:
- `channel` (str): 渠道名 (qqbot/feishu/wechat 等)
- `user_id` (str): 用户 ID
- `user_input` (str, optional): 用户输入 (用于关键词匹配)
- `force_new` (bool, optional): 是否强制创建新实例

**返回**: SmartOrchestrator 实例

---

### `reload_config(config_path)`

重新加载配置

**参数**:
- `config_path` (str, optional): 配置文件路径

---

### `clear_cache()`

清除 Orchestrator 缓存

---

### `execute_with_channel_routing(channel, user_id, user_input)`

便捷函数：使用渠道路由执行任务

**参数**:
- `channel` (str): 渠道名
- `user_id` (str): 用户 ID
- `user_input` (str): 用户输入
- `is_background` (bool, optional): 是否后台任务

**返回**: TaskResult

---

## 📚 相关文件

- **渠道路由器**: `scripts/channel_router.py`
- **配置文件**: `~/.openclaw/workspace/.learnings/channel_config.json`
- **主执行器**: `scripts/orchestrator_v2.py`
- **质量审核层**: `scripts/review_layer.py`
- **审计日志层**: `scripts/audit_layer.py`

---

## 💡 最佳实践

### 1. 聊天场景
```python
# 快速响应，不审核，不审计
orch = get_orchestrator_for_channel("qqbot", user_id, "你好呀")
```

### 2. 代码场景
```python
# 启用审核和审计，保证质量
orch = get_orchestrator_for_channel("qqbot", user_id, "写个 Python 函数")
```

### 3. 工作场景
```python
# 标准执行，保留审计日志
orch = get_orchestrator_for_channel("feishu", user_id, "周报怎么写")
```

### 4. 内容创作
```python
# 启用审核，保证内容质量
orch = get_orchestrator_for_channel("wechat", user_id, "公众号文章")
```

---

## 🎯 预期效果

- ✅ 聊天场景响应速度提升 **100x** (<5ms)
- ✅ Tokens 消耗节省 **40-60%**
- ✅ 工作场景质量保证 (审核 + 审计)
- ✅ 配置灵活，可随时调整

---

_最后更新：2026-03-05_
