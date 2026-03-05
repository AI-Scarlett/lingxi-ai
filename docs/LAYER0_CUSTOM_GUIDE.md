# 🎨 Layer 0 自定义配置指南

> 心有灵犀，一点就通 - 自定义你的专属快速响应 💋

---

## 📖 什么是 Layer 0 自定义？

Layer 0 是灵犀的**零思考响应层**，可以在 **<5ms** 内回复用户，完全不需要调用 LLM，节省 Tokens！

现在你可以**自己配置**想要什么样的回复，让灵犀更懂你！

---

## 🚀 快速开始

### 方式一：Python 代码配置

```python
from layer0_config import add_custom_response, list_custom_responses

# 添加自定义规则
add_custom_response(
    patterns=["老板好", "老大好", "早上好老板"],
    response="老板好呀～ 今天心情怎么样？💋",
    priority=10,
    description="自定义问候"
)

# 查看所有规则
rules = list_custom_responses()
for rule in rules:
    print(f"{rule.patterns} → {rule.response}")

# 删除规则
from layer0_config import remove_custom_response
remove_custom_response("custom_20260305123456_0")
```

### 方式二：直接编辑 JSON 文件

配置文件位置：`~/.openclaw/workspace/.learnings/layer0_custom_rules.json`

```json
{
  "version": "1.0",
  "rules": {
    "custom_greeting": {
      "id": "custom_greeting",
      "patterns": ["老板好", "老大好"],
      "response": "老板好呀～ 今天心情怎么样？💋",
      "priority": 10,
      "enabled": true,
      "description": "自定义问候"
    },
    "custom_thanks": {
      "id": "custom_thanks",
      "patterns": ["谢谢", "辛苦了"],
      "response": "跟我还客气什么呀～ 应该的！💕",
      "priority": 5,
      "enabled": true,
      "description": "感谢回应"
    }
  }
}
```

---

## 📋 配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 规则唯一标识 |
| `patterns` | string[] | ✅ | 触发关键词列表 |
| `response` | string | ✅ | 回复内容 |
| `priority` | int | ❌ | 优先级（数字越大越优先，默认 0） |
| `enabled` | boolean | ❌ | 是否启用（默认 true） |
| `description` | string | ❌ | 规则描述 |

---

## 💡 使用示例

### 1️⃣ 自定义问候

```python
add_custom_response(
    patterns=["早", "早上好", "早安", "morning"],
    response="早上好老板～☀️ 今天又是元气满满的一天！",
    priority=10
)
```

### 2️⃣ 自定义告别

```python
add_custom_response(
    patterns=["拜拜", "再见", "先下了", "溜了"],
    response="老板慢走～ 随时叫我哦！💋",
    priority=8
)
```

### 3️⃣ 自定义特定场景

```python
add_custom_response(
    patterns=["发布小红书", "发小红书", "小红书文案"],
    response="好的老板～ 马上帮您处理小红书发布！📱",
    priority=15
)
```

### 4️⃣ 动态响应（使用函数）

```python
from layer0_config import get_layer0_config

config = get_layer0_config()
config.add_rule(
    patterns=["几点了", "现在时间"],
    response=lambda: f"现在{datetime.now().strftime('%H:%M')}啦～ ⏰",
    priority=10
)
```

---

## 🔧 管理命令

### 查看所有规则

```python
from layer0_config import list_custom_responses

rules = list_custom_responses()
for rule in rules:
    print(f"ID: {rule.id}")
    print(f"  触发词：{rule.patterns}")
    print(f"  回复：{rule.response}")
    print(f"  优先级：{rule.priority}")
    print()
```

### 更新规则

```python
from layer0_config import get_layer0_config

config = get_layer0_config()
config.update_rule(
    rule_id="custom_001",
    patterns=["新的触发词"],
    response="新的回复",
    priority=20
)
```

### 启用/禁用规则

```python
config.enable_rule("custom_001")  # 启用
config.disable_rule("custom_001")  # 禁用
```

### 导出规则

```python
config = get_layer0_config()
config.export_rules("/path/to/export.json")
```

### 导入规则

```python
config = get_layer0_config()
config.import_rules("/path/to/import.json", merge=True)
```

---

## 📊 统计信息

```python
from layer0_config import get_layer0_stats

stats = get_layer0_stats()
print(f"总规则数：{stats['total_rules']}")
print(f"启用规则：{stats['enabled_rules']}")
print(f"总命中数：{stats['total_hits']}")
print(f"平均命中：{stats['avg_hits_per_rule']:.1f}")
```

---

## 🎯 最佳实践

### 1. 优先级设置

- **10-20**: 高频场景（问候、告别）
- **5-10**: 中频场景（感谢、确认）
- **0-5**: 低频场景（特殊需求）

### 2. 触发词设计

```python
# ✅ 好的设计：覆盖多种表达
patterns=["谢谢", "谢谢你", "感谢", "辛苦了", "麻烦你了"]

# ❌ 不好的设计：太具体
patterns=["非常感谢你的帮助"]
```

### 3. 回复风格

保持简洁、一致的风格：

```python
# ✅ 统一使用"老板"称呼
response="好的老板～ 马上办！⚡"
response="收到老板～ 理解万岁！😊"

# ❌ 风格混乱
response="好的先生"
response="收到亲"
```

---

## 📁 配置文件位置

```
~/.openclaw/workspace/.learnings/
├── layer0_custom_rules.json      # 自定义规则配置
└── backups/
    ├── layer0_config_20260305_123456.json  # 自动备份
    └── ...
```

---

## 🔍 常见问题

### Q: 自定义规则和内置规则冲突怎么办？

A: **自定义规则优先级更高**！会先匹配自定义规则，再匹配内置规则。

### Q: 如何恢复默认配置？

A: 删除 `layer0_custom_rules.json` 文件，系统会自动重建。

### Q: 规则不生效怎么办？

A: 检查以下几点：
1. 规则是否 `enabled=true`
2. `patterns` 是否包含触发词
3. 优先级是否设置合理

### Q: 最多可以添加多少条规则？

A: 默认最多 1000 条，一般使用足够了。

---

## 🎉 示例配置

完整的示例配置：

```json
{
  "version": "1.0",
  "rules": {
    "greeting": {
      "id": "greeting",
      "patterns": ["老板好", "早", "早上好", "在吗"],
      "response": "老板好呀～ 随时待命！💋",
      "priority": 10,
      "description": "问候"
    },
    "thanks": {
      "id": "thanks",
      "patterns": ["谢谢", "辛苦了", "感谢"],
      "response": "跟我还客气什么呀～💕",
      "priority": 8,
      "description": "感谢"
    },
    "bye": {
      "id": "bye",
      "patterns": ["拜拜", "再见", "晚安", "先下了"],
      "response": "老板慢走～ 想我哦！💕",
      "priority": 8,
      "description": "告别"
    },
    "confirm": {
      "id": "confirm",
      "patterns": ["好的", "收到", "明白", "OK"],
      "response": "收到老板！✅",
      "priority": 5,
      "description": "确认"
    },
    "xiaohongshu": {
      "id": "xiaohongshu",
      "patterns": ["小红书", "发小红书", "小红书文案"],
      "response": "好的老板～ 马上帮您处理小红书！📱",
      "priority": 15,
      "description": "小红书相关"
    }
  }
}
```

---

*本指南由灵犀 Learning Layer 自动生成*
