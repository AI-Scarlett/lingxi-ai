# 灵犀 v3.0 性能优化方案

**基于 OpenClaw 2026.3.7 版本分析**

---

## 🔍 当前问题诊断

### 1. sessions_spawn 使用不当

**问题:**
```python
# ❌ 当前代码 (orchestrator.py)
from sessions_spawn import sessions_spawn  # 导入方式错误
result = await sessions_spawn(
    agentId=agent_id,
    task=subtask.description,
    mode="run",
    cleanup="delete",
    timeoutSeconds=300
)
```

**OpenClaw 2026.3.7 正确用法:**
- `sessions_spawn` 是 **内置工具**，不是 Python 模块，不能直接 import
- 应该通过 OpenClaw 工具系统调用
- 参数 `cleanup` 默认是 `keep`，不是 `delete`

**影响:** 子任务执行可能失败或行为不符合预期

---

### 2. 没有利用 Thread-Bound Sessions

**OpenClaw 新特性:**
```yaml
# Discord 渠道支持 thread-bound subagent sessions
sessions_spawn(
    thread: true,      # 绑定到线程
    mode: "session",   # 持久会话模式
)
```

**灵犀现状:** 所有子任务都是 one-shot (`mode: "run"`)，无法保持上下文

**优化建议:**
- 对于复杂多轮任务，启用 `thread: true`
- 子 Agent 可以记住之前的对话历史
- 减少重复上下文传递

---

### 3. 没有利用 Nested Sub-Agents (Orchestrator Pattern)

**OpenClaw 支持:**
```json5
agents: {
  defaults: {
    subagents: {
      maxSpawnDepth: 2  // 允许子 Agent 再 spawn 子 Agent
    }
  }
}
```

**灵犀现状:** 单层架构 (灵犀 → 角色 Agent)

**优化建议:**
```
灵犀 (主控)
  ↓
编排子 Agent (depth=1)
  ↓
工作子 Agent (depth=2)
```

适用场景：
- 复杂任务需要进一步拆解
- 大规模并行处理

---

### 4. 模型路由过度复杂

**当前问题:**
```python
# 每个子任务都要经过完整模型路由分析
def get_model_for_role(role: RoleType, user_input: str, priority: str) -> str:
    # 复杂的路由逻辑...
```

**OpenClaw 推荐做法:**
```yaml
# 配置级别模型继承
agents:
  defaults:
    subagents:
      model: "qwen3.5-plus"  # 默认子 Agent 模型
      thinking: "off"        # 默认思考级别
```

**优化建议:**
- 简单任务：直接使用默认模型，跳过路由
- 复杂任务：才启用智能路由
- 配置级别覆盖 > 代码级别路由

---

### 5. 清理策略不当

**当前问题:**
```python
cleanup="delete"  # 立即删除会话
```

**OpenClaw 行为:**
- `cleanup: "delete"` → 立即归档会话 (transcript 重命名为 `*.deleted.<timestamp>`)
- `cleanup: "keep"` → 等待 auto-archive (默认 60 分钟)

**优化建议:**
- 调试模式：`cleanup: "keep"` (保留日志)
- 生产模式：`cleanup: "delete"` (节省存储)
- 重要任务：`cleanup: "keep"` + 手动归档

---

### 6. 三位一体系统 I/O 开销

**当前问题:**
```python
# 每次任务都同步读写状态文件
self.state = self._load_state()  # 磁盘 I/O
self._save_state()               # 磁盘 I/O
```

**优化建议:**
```python
# 懒加载 + 异步批量保存
class TrinityStateManager:
    def __init__(self):
        self._state = None  # 懒加载
        self._save_timer = None
    
    async def async_save(self, interval=60):
        # 批量保存，减少 I/O
        pass
```

---

### 7. 学习层频繁写入

**当前问题:**
```python
# 每个子任务完成都写磁盘
self.learning_layer.on_task_complete(...)  # 同步写入
```

**优化建议:**
```python
# 批量异步写入
class LearningLayer:
    def __init__(self):
        self.batch_buffer = []
        self.write_interval = 30  # 秒
    
    async def batch_write(self):
        # 每 30 秒批量写入一次
        pass
```

---

## 🚀 优化实施计划

### Phase 1: 修复关键 Bug (立即)

1. **修复 sessions_spawn 调用**
   - 移除错误的 import
   - 使用正确的工具调用方式
   - 添加错误处理和降级逻辑

2. **优化清理策略**
   - 添加配置开关
   - 调试模式保留日志
   - 生产模式自动清理

**预期收益:** 稳定性提升 30%

---

### Phase 2: 性能优化 (本周)

1. **三位一体懒加载**
   - 首次访问时才加载状态
   - 异步批量保存 (60 秒间隔)
   - 内存缓存 + 磁盘持久化

2. **学习层批量写入**
   - 缓冲 10 条记录或 30 秒触发
   - 异步写入，不阻塞主流程
   - 失败重试机制

3. **模型路由简化**
   - 简单问题直连默认模型
   - 复杂问题才启用智能路由
   - 配置级别模型继承

**预期收益:** 响应速度提升 50%

---

### Phase 3: 架构升级 (下周)

1. **启用 Thread-Bound Sessions**
   - Discord 渠道优先
   - 复杂任务绑定线程
   - 保持对话上下文

2. **Nested Sub-Agents**
   - 配置 `maxSpawnDepth: 2`
   - 编排器模式实现
   - 大规模并行处理

3. **性能监控仪表板**
   - 实时延迟监控
   - 缓存命中率
   - 错误率告警

**预期收益:** 复杂任务处理能力提升 3x

---

## 📊 性能目标

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 简单问题响应 | ~200ms | <50ms | 75%↓ |
| 复杂任务执行 | ~5s | ~3s | 40%↓ |
| 快速响应率 | 65% | 80% | 23%↑ |
| 缓存命中率 | 30% | 60% | 100%↑ |
| 错误率 | 2% | <0.5% | 75%↓ |

---

## 🔧 配置建议

### OpenClaw Gateway 配置

```yaml
# ~/.openclaw/config.yaml 或 gateway config

agents:
  defaults:
    subagents:
      model: "qwen3.5-plus"      # 子 Agent 默认模型
      thinking: "off"            # 关闭思考（加快速度）
      runTimeoutSeconds: 300     # 5 分钟超时
      archiveAfterMinutes: 60    # 60 分钟后自动归档
      maxSpawnDepth: 2           # 允许嵌套子 Agent

session:
  threadBindings:
    enabled: true                # 启用线程绑定
    idleHours: 2                 # 2 小时空闲后自动解绑
    maxAgeHours: 24              # 24 小时后强制解绑

channels:
  discord:
    threadBindings:
      enabled: true
      spawnSubagentSessions: true  # 自动绑定子 Agent 到线程
```

### 灵犀配置

```json
// ~/.openclaw/workspace/lingxi-config.json

{
  "performance": {
    "lazy_load_trinity": true,
    "async_save_interval_seconds": 60,
    "learning_batch_size": 10,
    "learning_write_interval_seconds": 30,
    "model_routing": {
      "simple_passthrough": true,
      "default_model": "qwen3.5-plus",
      "complex_threshold": 0.7
    }
  },
  "subagents": {
    "cleanup_mode": "keep",  // 调试模式用 keep，生产用 delete
    "thread_binding": {
      "enabled": true,
      "channels": ["discord"]
    },
    "nested_depth": 2
  }
}
```

---

## 📝 待办事项

- [ ] 修复 sessions_spawn 调用方式
- [ ] 实现三位一体懒加载
- [ ] 实现学习层批量异步写入
- [ ] 简化模型路由逻辑
- [ ] 添加性能监控
- [ ] 配置 Thread-Bound Sessions
- [ ] 测试 Nested Sub-Agents
- [ ] 更新文档

---

**创建时间:** 2026-03-09 15:25 UTC  
**作者:** 斯嘉丽 (Scarlett)  
**版本:** v1.0
