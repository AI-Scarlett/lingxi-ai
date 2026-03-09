# 灵犀 v3.1.0 - 自定义配置完全指南

> **灵活调整，打造专属你的灵犀！** 🛠️

---

## 📋 自定义内容总览

| 配置项 | 配置文件 | 难度 | 说明 |
|--------|----------|------|------|
| Layer 0 规则 | `layer0_custom_rules.json` | ⭐ | 添加个人习惯用语 |
| Layer 0 技能 | `layer0_skills.py` | ⭐⭐ | 修改技能触发词和响应 |
| 模型配置 | `lingxi-config.json` | ⭐⭐ | 调整各模块使用的模型 |
| 性能参数 | `lingxi-config.json` | ⭐⭐⭐ | 优化性能表现 |
| 自动学习 | `learning_layer.py` | ⭐⭐⭐ | 调整学习策略 |

---

## 🎯 自定义 Layer 0 规则

### 查看当前规则

```bash
# 列出所有规则
python3 layer0_config.py list

# 查看配置文件
cat ~/.openclaw/workspace/layer0_custom_rules.json
```

### 添加新规则

**方式 1：CLI 命令（推荐）**

```bash
# 基本用法
python3 layer0_config.py add -p 模式 1 模式 2 -r "你的响应" --priority 8

# 示例：添加问候语
python3 layer0_config.py add -p 老板好 老板早 -r "老板好呀～💋 今天也要加油哦！" --priority 10

# 示例：添加工作用语
python3 layer0_config.py add -p 开工 开始工作 -r "收到老板！⚡ 马上进入工作状态～" --priority 8
```

**方式 2：直接编辑配置文件**

```bash
nano ~/.openclaw/workspace/layer0_custom_rules.json
```

**规则格式：**
```json
{
  "version": "1.0",
  "rules": [
    {
      "patterns": ["模式 1", "模式 2", "模式 3"],
      "response": "响应内容",
      "priority": 8,
      "enabled": true,
      "created_at": "2026-03-09T16:00:00"
    }
  ]
}
```

**字段说明：**
- `patterns`: 触发模式数组，匹配任一即触发
- `response`: 响应内容（支持 emoji）
- `priority`: 优先级（1-10，数字越大越优先）
- `enabled`: 是否启用（true/false）
- `created_at`: 创建时间（可选）

### 删除规则

```bash
# 按索引删除（从 0 开始）
python3 layer0_config.py remove --index 0

# 查看删除后的规则
python3 layer0_config.py list
```

### 重置配置

```bash
# 删除自定义配置，恢复默认
python3 setup.py --reset-layer0

# 重新初始化
python3 setup.py --init-config
```

### 最佳实践

**1. 优先级设置：**
- 10：最高优先级（问候、紧急）
- 8-9：高优先级（常用语）
- 5-7：中优先级（一般用语）
- 1-4：低优先级（备用）

**2. 模式设计：**
```json
{
  "patterns": [
    "老板好",      // 精确匹配
    "老板早",      // 精确匹配
    "早啊老板"     // 包含匹配
  ],
  "response": "老板好呀～💋"
}
```

**3. 响应风格：**
- 保持一致的语气和人设
- 适当使用 emoji 增加趣味性
- 响应长度控制在 50 字以内

---

## 🎯 自定义 Layer 0 技能

### 查看可用技能

```bash
# 列出所有技能
python3 layer0_skills.py list

# 测试技能匹配
python3 layer0_skills.py test -i "几点了"
```

### 编辑技能配置

**打开技能文件：**
```bash
nano /root/.openclaw/skills/lingxi/scripts/layer0_skills.py
```

**找到 LAYER0_SKILLS 字典：**
```python
LAYER0_SKILLS = {
    "time": {
        "patterns": ["几点了", "现在时间", "几点"],
        "action": "get_time",
        "reply": lambda: f"现在{datetime.now().strftime('%H:%M:%S')}啦～ ⏰"
    },
    # ... 其他技能
}
```

### 添加新技能

**示例：添加星座查询技能**

```python
LAYER0_SKILLS = {
    # ... 现有技能 ...
    
    "horoscope": {
        "patterns": ["星座", "运势", "今天运势"],
        "action": "get_horoscope",
        "reply": "🔮 星座查询准备～ 老板是什么星座？"
    }
}
```

### 修改现有技能

**示例：修改时间响应风格**

```python
# 原响应
"time": {
    "patterns": ["几点了", "现在时间"],
    "action": "get_time",
    "reply": lambda: f"现在{datetime.now().strftime('%H:%M:%S')}啦～ ⏰"
}

# 修改后（更俏皮）
"time": {
    "patterns": ["几点了", "现在时间", "时间"],
    "action": "get_time",
    "reply": lambda: f"报告老板！现在是{datetime.now().strftime('%H 点%M 分')}～ ⏰"
}
```

### 技能响应类型

**1. 静态响应：**
```python
"skill": {
    "patterns": ["你好"],
    "action": "greet",
    "reply": "你好老板～💋"
}
```

**2. 动态响应（lambda）：**
```python
"skill": {
    "patterns": ["几点了"],
    "action": "get_time",
    "reply": lambda: f"现在{datetime.now().strftime('%H:%M')}啦～"
}
```

**3. 函数响应：**
```python
def get_weather_reply():
    # 复杂逻辑
    return "🌤️ 天气查询准备～"

"skill": {
    "patterns": ["天气"],
    "action": "get_weather",
    "reply": get_weather_reply
}
```

---

## 🎯 自定义模型配置

### 查看当前配置

```bash
cat ~/.openclaw/workspace/lingxi-config.json
```

### 编辑模型配置

**打开配置文件：**
```bash
nano ~/.openclaw/workspace/lingxi-config.json
```

### 可用模型列表

| 模型 | 特点 | 适用场景 | 成本 |
|------|------|----------|------|
| `qwen3.5-plus` | 全能均衡 | **推荐默认**，日常对话 | ⭐⭐ |
| `qwen3-max` | 高端推理 | 复杂分析、专业咨询 | ⭐⭐⭐⭐⭐ |
| `qwen3-coder-plus` | 专业代码 | 编程、脚本 | ⭐⭐⭐⭐ |
| `glm-5` | 中文深度 | 中文任务、长文 | ⭐⭐⭐ |
| `glm-4.7` | 性价比 | 简单问答、高频 | ⭐ |
| `kimi-k2.5` | 长文本 + 视觉 | 长文档、图像 | ⭐⭐⭐ |
| `MiniMax-M2.5` | 创意对话 | 创意写作、情感 | ⭐⭐ |

### 配置示例

**示例 1：经济型配置（节省成本）**

```json
{
  "model_routing": {
    "default_model": "glm-4.7",
    "complex_threshold": 0.8
  },
  "subagents": {
    "model": "glm-4.7",
    "thinking": "off"
  }
}
```

**示例 2：高质量配置（追求效果）**

```json
{
  "model_routing": {
    "default_model": "qwen3-max",
    "complex_threshold": 0.5
  },
  "subagents": {
    "model": "qwen3.5-plus",
    "thinking": "on"
  }
}
```

**示例 3：平衡型配置（推荐）**

```json
{
  "model_routing": {
    "default_model": "qwen3.5-plus",
    "complex_threshold": 0.7
  },
  "subagents": {
    "model": "glm-4.7",
    "thinking": "off"
  }
}
```

### 模型路由策略

**简单问题直连（默认模型）：**
- 问候、告别、感谢
- 时间、日期查询
- 简单确认

**智能路由（根据复杂度）：**
- 复杂度 < 0.7：默认模型
- 复杂度 >= 0.7：高端模型
- 代码任务：coder 模型
- 长文本：kimi 模型

---

## 🎯 自定义性能参数

### 编辑性能配置

```bash
nano ~/.openclaw/workspace/lingxi-config.json
```

### 性能参数说明

```json
{
  "performance": {
    "lazy_load_trinity": true,           // 懒加载（节省内存）
    "async_save_interval_seconds": 60,   // 批量保存间隔（秒）
    "learning_batch_size": 10,           // 学习批量大小
    "learning_write_interval_seconds": 30, // 学习写入间隔
    "model_routing": {
      "simple_passthrough": true,        // 简单问题跳过路由
      "default_model": "qwen3.5-plus",
      "complex_threshold": 0.7
    }
  }
}
```

### 优化建议

**1. 提升响应速度：**
```json
{
  "lazy_load_trinity": true,
  "async_save_interval_seconds": 120,
  "learning_batch_size": 20
}
```

**2. 提升学习速度：**
```json
{
  "learning_batch_size": 5,
  "learning_write_interval_seconds": 15
}
```

**3. 节省内存：**
```json
{
  "lazy_load_trinity": true,
  "async_save_interval_seconds": 300
}
```

---

## 🎯 自定义自动学习

### 调整学习策略

**编辑学习层配置：**
```bash
nano /root/.openclaw/skills/lingxi/scripts/learning_layer.py
```

**修改触发条件：**
```python
# 原配置（7 天，日均>1 次）
def get_frequent_queries(self, min_days: int = 7, min_daily_avg: float = 1.0)

# 修改为快速学习（3 天，日均>0.5 次）
def get_frequent_queries(self, min_days: int = 3, min_daily_avg: float = 0.5)
```

### 手动触发学习

```bash
# 查看学习报告
python3 learning_layer.py --report

# 应用新规则（预览）
python3 learning_layer.py --apply

# 应用新规则（实际写入）
python3 learning_layer.py --apply --days 7 --min-daily 1.0

# 清理旧日志
python3 learning_layer.py --cleanup
```

### 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点自动学习
0 2 * * * python3 /root/.openclaw/skills/lingxi/scripts/learning_layer.py --apply
```

---

## 📊 配置效果验证

### 测试 Layer 0 规则

```bash
python3 -c "
from fast_response_layer_v2 import fast_respond
result = fast_respond('你的测试语')
print(f'响应：{result.response}')
print(f'耗时：{result.latency_ms:.3f}ms')
print(f'层级：{result.layer}')
"
```

### 测试技能匹配

```bash
python3 layer0_skills.py test -i "你的触发词"
```

### 查看系统状态

```bash
python3 setup.py --status
```

### 运行完整测试

```bash
python3 setup.py --test
```

---

## 📝 配置备份与恢复

### 备份配置

```bash
# 备份所有配置
cp ~/.openclaw/workspace/layer0_custom_rules.json ~/layer0_backup_$(date +%Y%m%d).json
cp ~/.openclaw/workspace/lingxi-config.json ~/lingxi_config_backup_$(date +%Y%m%d).json
```

### 恢复配置

```bash
# 恢复 Layer 0 规则
cp ~/layer0_backup_20260309.json ~/.openclaw/workspace/layer0_custom_rules.json

# 恢复灵犀配置
cp ~/lingxi_config_backup_20260309.json ~/.openclaw/workspace/lingxi-config.json
```

---

## 💡 最佳实践总结

### Layer 0 规则
- ✅ 保持规则简洁（50 字以内）
- ✅ 使用高优先级处理常用语
- ✅ 定期清理未启用的规则
- ✅ 备份重要自定义规则

### Layer 0 技能
- ✅ 触发词要独特，避免冲突
- ✅ 响应风格保持一致
- ✅ 测试后再应用到生产
- ✅ 文档化自定义技能

### 模型配置
- ✅ 根据需求选择模型（成本 vs 质量）
- ✅ 子 Agent 使用经济模型
- ✅ 定期评估模型效果
- ✅ 记录配置变更

### 性能优化
- ✅ 启用懒加载节省内存
- ✅ 批量写入减少 I/O
- ✅ 监控性能指标
- ✅ 根据实际使用调整参数

---

**版本：** v3.1.0  
**更新时间：** 2026-03-09  
**作者：** 斯嘉丽 (Scarlett) 💋
