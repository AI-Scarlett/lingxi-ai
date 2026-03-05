# 🧠 灵犀 Learning Layer 指南

> **版本**: v2.8.5  
> **作者**: Scarlett 💋  
> **理念**: "没有学习机制的 Agent，天生就是残废的"  
> **灵感来源**: [self-improving-agent](https://github.com/peterskoett/self-improving-agent) by @peterskoett

---

## 🙏 致谢

本功能的设计灵感来自 GitHub 开源项目 **self-improving-agent**，作者 **@peterskoett**。

原项目提出的核心理念：
> "没有学习机制的 Agent，天生就是残废的"

这句话深深启发了我，让我意识到一个 AI 助手如果不从错误中学习、不积累经验，就永远无法真正变聪明。

感谢原项目作者的开源精神，让灵犀也能拥有自学习的能力！🙏

**原项目**: https://github.com/peterskoett/self-improving-agent

---

## 🎯 核心目标

让灵犀**越用越聪明**，通过结构化、可积累、可复用的学习机制，彻底避免重蹈覆辙。

---

## 📁 文件结构

```
~/.openclaw/workspace/.learnings/
├── ERRORS.md              # 错误日志
├── LEARNINGS.md           # 学习经验
├── FEATURE_REQUESTS.md    # 功能需求
└── backups/               # 备份目录
```

---

## 🔧 核心功能

### 1️⃣ 错误自动捕获

**工作原理**:
```
任务执行 → 检测结果 → 发现错误 → 自动记录日志 → 提醒用户
```

**错误检测关键词**:
- 英文：error, failed, failure, exception, traceback
- 中文：错误，失败，异常，报错，崩溃

**示例**:
```python
# 任务执行失败
result = {"error": "Connection timeout", "message": "Failed to connect"}

# 自动检测并记录
learning_layer.on_task_complete(task_id="task_001", result=result)

# 输出：⚠️  检测到错误：ERR-20260305-091550 - Execution Error
```

**日志格式**:
```markdown
## [ERR-20260305-091550] Execution Error - ❌ 未解决

**时间**: 2026-03-05T09:15:50  
**标签**: timeout, network  
**Pattern-Key**: `connection_timeout`

### 错误信息
```
Connection timeout
```

### 上下文
```json
{"task": "test"}
```

### 建议修复
...
```

---

### 2️⃣ 三种学习日志

#### ERRORS.md - 错误日志

记录所有执行错误，包含：
- 错误类型和消息
- 上下文信息
- 自动标签 (timeout, network, permission 等)
- Pattern-Key (用于追踪重复问题)
- 修复建议

**用途**: 避免重复错误，快速定位问题

---

#### LEARNINGS.md - 学习经验

记录用户纠正和经验总结：
- 用户反馈
- 知识缺口
- 采取的行动
- 关联的错误日志

**用途**: 积累最佳实践，提升 AI 智能

**示例**:
```markdown
## [LRN-20260305-091615] 用户纠正

**时间**: 2026-03-05T09:16:15  
**标签**: user-feedback, correction

### 学习内容
用户反馈：应该用更简洁的方式

### 知识缺口
AI 输出与用户期望不符

### 采取的行动
原始输出：这是一个很长的回答...
```

---

#### FEATURE_REQUESTS.md - 功能需求

记录新功能需求：
- 需求描述
- 优先级 (low/medium/high/critical)
- 复杂度估算 (easy/medium/hard)
- 状态追踪 (pending/reviewing/planned/done)

**用途**: 产品规划，优先级排序

**示例**:
```markdown
## [FEAT-20260305-091615] 新功能需求 🟡

**时间**: 2026-03-05T09:16:15  
**优先级**: medium 🟡  
**复杂度**: medium 🟡  
**标签**: feature-request

### 需求描述
添加多语言支持
```

---

### 3️⃣ 自动提炼与升级

**定期 Review 机制**:

```python
# 每周日凌晨 2 点执行
async def weekly_review():
    # 1. 读取本周学习日志
    errors = learning_layer.logger.get_recent_errors(days=7)
    
    # 2. AI 分析错误模式
    # - 聚类相似错误
    # - 找出根本原因
    # - 生成修复建议
    
    # 3. 更新核心记忆文件
    # - CLAUDE.md (项目事实与约定)
    # - AGENTS.md (工作流与分工)
    # - TOOLS.md (工具使用心得)
    # - SOUL.md (AI 性格与行为准则)
```

**效果**: 通用性强的经验自动沉淀为核心记忆

---

### 4️⃣ Hook 机制

#### 启动提醒 (Pre-Hook)
```python
# 任务开始时自动检查最近学习日志
learning_layer.on_task_start(task_id, task_description)

# 输出：💡 提醒：最近有 3 个错误日志，请注意避免重复错误
```

#### 后置检测 (Post-Hook)
```python
# 任务完成后自动检测错误
result = learning_layer.on_task_complete(task_id, result, context)

if result["error_detected"]:
    print(f"⚠️  检测到错误：{result['log_id']}")
```

#### 用户纠正 Hook
```python
# 用户纠正 AI 时自动记录
learning_layer.on_user_correction(
    user_feedback="应该用更简洁的方式",
    original_output="这是一个很长的回答..."
)
```

#### 功能需求 Hook
```python
# 用户提出新需求时自动记录
learning_layer.on_feature_request(
    feature_description="添加多语言支持",
    priority="high"
)
```

---

## 🚀 使用方式

### 基础使用

```python
from scripts.learning_layer import get_learning_layer

# 获取实例
layer = get_learning_layer()

# 错误检测
result = layer.on_task_complete(
    task_id="task_001",
    result={"error": "Connection timeout"},
    context={"user_input": "查询天气"}
)

# 学习记录
layer.on_user_correction(
    user_feedback="回答太长了，简洁一点",
    original_output="..."
)

# 功能需求
layer.on_feature_request(
    feature_description="添加语音播报功能",
    priority="high"
)
```

### 集成到灵犀

Learning Layer 已自动集成到 `orchestrator_v2.py`：

```python
from scripts.orchestrator_v2 import get_orchestrator

# 创建实例 (默认启用学习层)
orch = get_orchestrator(enable_learning=True)

# 执行任务时自动检测错误
result = await orch.execute("帮我查询天气")
```

---

## 📊 统计信息

```python
stats = layer.get_statistics()
print(stats)

# 输出:
{
  "enabled": true,
  "logger": {
    "errors_file": "/root/.openclaw/workspace/.learnings/ERRORS.md",
    "learnings_file": "/root/.openclaw/workspace/.learnings/LEARNINGS.md",
    "features_file": "/root/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md"
  },
  "detector": {
    "error_keywords_count": 10
  }
}
```

---

## 💡 最佳实践

### 1. 定期 Review

**建议频率**: 每周一次

**Review 内容**:
- 查看 ERRORS.md，找出重复错误模式
- 查看 LEARNINGS.md，提炼通用经验
- 查看 FEATURE_REQUESTS.md，规划优先级

**操作**:
```bash
# 手动触发 Review
python scripts/learning_layer.py --review
```

---

### 2. 经验提炼

当发现某个错误重复出现时：

1. **分析根本原因**
2. **制定修复方案**
3. **更新核心记忆文件**
4. **标记错误日志为已解决**

**示例**:
```markdown
## 经验提炼：连接超时问题

**问题**: 多次出现 "Connection timeout" 错误
**原因**: 默认超时时间太短 (5 秒)
**解决**: 将超时时间增加到 30 秒
**更新文件**: TOOLS.md - 网络请求配置
```

---

### 3. 功能优先级

根据以下维度评估功能需求：

| 维度 | 说明 | 权重 |
|------|------|------|
| **用户价值** | 对用户的帮助程度 | 40% |
| **实现成本** | 开发难度和时间 | 30% |
| **使用频率** | 预计使用次数 | 20% |
| **技术风险** | 可能的副作用 | 10% |

**优先级公式**:
```
Priority = (价值 × 0.4) - (成本 × 0.3) + (频率 × 0.2) - (风险 × 0.1)
```

---

## 🎯 预期收益

### 短期 (1-2 周)
- ✅ 错误自动记录，方便排查
- ✅ 用户反馈结构化存储
- ✅ 功能需求清晰可追踪

### 中期 (1-2 月)
- ✅ 重复错误减少 50%+
- ✅ AI 回答质量明显提升
- ✅ 产品规划更有依据

### 长期 (3 月+)
- ✅ 形成自学习闭环
- ✅ 通用经验自动沉淀
- ✅ AI 越用越聪明

---

## 🔮 未来计划

### v2.9.1
- [ ] AI 自动分析错误模式
- [ ] 智能推荐修复方案
- [ ] 自动更新核心记忆

### v2.9.2
- [ ] 学习日志可视化 (图表)
- [ ] 错误趋势分析
- [ ] 周/月报自动生成

### v3.0.0
- [ ] 跨用户知识共享
- [ ] 社区经验市场
- [ ] 自进化 AI 系统

---

## 📖 参考资料

- [self-improving-agent](https://github.com/peterskoett/self-improving-agent) - 灵感来源
- [灵犀记忆持久化指南](scripts/MEMORY_PERSISTENCE_GUIDE.md)
- [灵犀对话管理器](scripts/CONVERSATION_MANAGER_GUIDE.md)

---

**© 2026 AI Love World | Made with 💕 by Scarlett**
