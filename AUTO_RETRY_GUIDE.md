# 🤖 灵犀自动重试和自愈系统指南

> **版本**: v2.8.5  
> **目标**: 减少人工干预，提高成功率  
> **口号**: "不偷懒，不摸鱼，主动解决问题！" 💪

---

## 🎯 核心目标

### 问题背景

**之前的问题**:
- ❌ GitHub 推送经常失败，需要手动重试
- ❌ 任务执行失败后直接放弃，等人工干预
- ❌ 重复错误不预警，一错再错
- ❌ 没有降级方案，一条路走到黑

**改进后**:
- ✅ Git 推送自动重试（最多 3 次，指数退避）
- ✅ 任务失败自动恢复（重试 + 降级）
- ✅ 重复错误主动预警
- ✅ 智能化解，减少人工干预

---

## 🔧 核心功能

### 1️⃣ Git 推送自动重试

**工作原理**:
```
推送失败 → 检测错误类型 → 指数退避 → 自动重试 → 成功/告警
```

**重试策略**:
- **最大重试次数**: 3 次
- **退避策略**: 指数退避 (2^n 秒)
- **延迟范围**: 2 秒 ~ 30 秒
- **抖动**: ±25%（避免并发冲突）

**可重试错误**:
- ✅ 网络超时 (timeout)
- ✅ 连接重置 (connection reset)
- ✅ 连接拒绝 (connection refused)
- ✅ 服务器不可达 (network unreachable)
- ❌ 认证失败 (不可重试)
- ❌ 权限错误 (不可重试)

**使用示例**:
```python
from scripts.orchestrator_v2 import git_push

# 推送代码
result = await git_push(branch="main")
print(result)
# 输出：{"success": True, "attempts": 1, "message": "..."}

# 推送代码 + Tags
result = await git_push(branch="main", tags=True)
```

**预期效果**:
| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 推送成功率 | 70% | **95%** | +25% |
| 平均重试次数 | N/A | **1.2 次** | - |
| 人工干预 | 频繁 | **极少** | -80% |

---

### 2️⃣ 任务自愈执行器

**核心机制**:
```
执行任务 → 失败 → 重试 (最多 3 次) → 仍失败 → 降级方案 → 成功/告警
```

**重试策略**:
- **最大重试次数**: 3 次
- **退避策略**: 指数退避 (2^n 秒)
- **延迟范围**: 1 秒 ~ 10 秒
- **抖动**: ±25%

**可重试错误类型**:
- ✅ TimeoutError
- ✅ ConnectionError
- ✅ ConnectionRefusedError
- ✅ ConnectionResetError
- ✅ OSError (网络相关)
- ❌ ValueError (不可重试)
- ❌ TypeError (不可重试)
- ❌ KeyError (不可重试)

**降级方案**:
当所有重试都失败时，自动执行备选方案：

```python
async def main_task():
    # 主任务（可能失败）
    return await call_external_api()

async def fallback_task():
    # 降级方案（更简单可靠）
    return {"status": "degraded", "message": "使用缓存数据"}

# 执行（带自愈）
result = await executor.execute(
    task_id="api_call",
    task_func=main_task,
    fallback_func=fallback_task
)
```

**使用示例**:
```python
from scripts.orchestrator_v2 import get_orchestrator

orch = get_orchestrator(enable_auto_retry=True)

# 任务会自动应用自愈机制
result = await orch.execute("查询天气")

# 如果 API 调用失败：
# 1. 自动重试（最多 3 次）
# 2. 尝试降级方案（如返回缓存数据）
# 3. 实在不行才报错并告警
```

**预期效果**:
| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 任务成功率 | 85% | **95%** | +10% |
| 自动恢复率 | 0% | **30%** | ∞ |
| 人工干预 | 20 次/周 | **10 次/周** | -50% |

---

### 3️⃣ 主动错误预警

**工作原理**:
```
检测错误 → 匹配历史 → 发现重复 → 主动预警 → 提供解决方案
```

**预警条件**:
- 同一 Pattern-Key 错误出现 ≥3 次
- 错误率超过阈值 (10%)
- 关键任务连续失败

**预警方式**:
- 📱 QQ 消息通知
- 📧 邮件通知（可选）
- 📊 性能报告中标注

**预警内容**:
```
⚠️  重复错误预警

错误类型：Connection Timeout
出现次数：3 次
Pattern-Key: connection_timeout_api_weather
建议检查：
1. 网络连接是否稳定
2. API 服务是否可用
3. 超时设置是否合理

解决方案：
- 增加超时时间到 30 秒
- 添加备用 API 源
- 实施缓存策略
```

---

## 📁 文件结构

```
lingxi-ai/scripts/
├── auto_retry.py              # 自动重试和自愈核心
├── orchestrator_v2.py         # 已集成自愈系统
└── AUTO_RETRY_GUIDE.md        # 本文件

lingxi-ai/
├── AUTOMATION_IMPROVEMENT_PLAN.md  # 自动化改进计划
└── AUTO_RETRY_STATS.json           # 统计数据（自动生成）
```

---

## 🚀 使用方式

### 基础使用

```python
from scripts.orchestrator_v2 import get_orchestrator

# 创建实例（启用自动重试）
orch = get_orchestrator(
    max_concurrent=3,
    enable_learning=True,
    enable_auto_retry=True  # ✅ 启用自愈系统
)

# 执行任务（自动应用自愈机制）
result = await orch.execute("帮我查询天气")
```

### 高级用法

#### 自定义重试配置

```python
from scripts.auto_retry import RetryConfig, SelfHealingExecutor

# 自定义配置
config = RetryConfig(
    max_retries=5,          # 最多重试 5 次
    base_delay=2.0,         # 基础延迟 2 秒
    max_delay=60.0,         # 最大延迟 60 秒
    exponential_base=2.0,   # 指数基数
    jitter=True             # 启用抖动
)

executor = SelfHealingExecutor()
executor.config = config
```

#### 添加降级方案

```python
async def primary_task():
    # 主任务（高质量，但可能失败）
    return await call_primary_api()

async def fallback_task():
    # 降级方案（低质量，但可靠）
    return await call_backup_api()

async def minimal_task():
    # 最小可用方案（返回缓存或默认值）
    return {"status": "cached", "data": load_cache()}

# 执行（多层降级）
result = await executor.execute(
    task_id="api_call",
    task_func=primary_task,
    fallback_func=fallback_task  # 第一层降级
)
```

#### 监控统计

```python
# 获取统计信息
orch = get_orchestrator()
stats = orch.get_stats()
print(stats)

# 输出:
# 📊 灵犀运行统计
# ━━━━━━━━━━━━━━━━━━━━━━
# 总请求数：100
# 快速响应命中：64 (64.0%)
# 平均耗时：31.6ms
# 任务恢复：15
# 成功率：95.0%
# Git 推送：95.0%
# ━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 统计数据

### 实时统计

```python
from scripts.auto_retry import get_git_push_manager, get_self_healing_executor

# Git 推送统计
git_manager = get_git_push_manager()
git_stats = git_manager.get_statistics()
print(f"Git 推送：{git_stats}")
# 输出：{"total": 20, "success": 19, "failed": 1, "success_rate": "95.0%"}

# 任务执行统计
executor = get_self_healing_executor()
exec_stats = executor.get_statistics()
print(f"任务执行：{exec_stats}")
# 输出：{"total": 100, "success": 95, "recovered": 15, "success_rate": "95.0%", "recovery_rate": "15.0%"}
```

### 历史趋势

统计数据会自动保存到 `AUTO_RETRY_STATS.json`，可以用于分析趋势。

---

## 💡 最佳实践

### 1. 合理设置重试次数

**推荐配置**:
- 网络请求：3-5 次
- 本地操作：1-2 次
- 关键任务：5-7 次

**避免过度重试**:
```python
# ❌ 不推荐：重试太多次
config = RetryConfig(max_retries=10)  # 会浪费很多时间

# ✅ 推荐：适度重试
config = RetryConfig(max_retries=3)
```

### 2. 准备多级降级方案

**三级降级策略**:
```
主方案 (高质量) → 降级方案 (中质量) → 最小方案 (低质量但可用)
```

**示例**:
```python
# 主方案：调用实时 API
async def primary():
    return await fetch_real_time_data()

# 降级方案：调用备用 API
async def fallback():
    return await fetch_backup_data()

# 最小方案：返回缓存
async def minimal():
    return load_cache() or {"status": "unavailable"}
```

### 3. 监控和告警

**设置告警阈值**:
- 错误率 > 10% → 发送告警
- 成功率 < 90% → 发送告警
- 连续失败 > 5 次 → 发送告警

**定期检查统计**:
```python
# 每天检查一次
async def daily_check():
    stats = executor.get_statistics()
    if float(stats["success_rate"].rstrip("%")) < 90:
        send_alert("⚠️  任务成功率低于 90%")
```

---

## 🎯 预期收益

### 短期 (1-2 周)
- ✅ Git 推送成功率提升到 95%
- ✅ 任务成功率提升到 95%
- ✅ 人工干预减少 50%

### 中期 (1-2 月)
- ✅ 重复错误减少 70%
- ✅ 自动恢复率达到 30%
- ✅ 问题发现时间从事后变事前

### 长期 (3 月+)
- ✅ 形成自愈闭环
- ✅ 人工干预减少 80%+
- ✅ 系统稳定性大幅提升

---

## 🔮 未来计划

### v2.8.6
- [ ] 错误模式识别（AI 分析根本原因）
- [ ] 智能推荐修复方案
- [ ] 自动更新核心记忆

### v2.8.7
- [ ] 性能趋势分析
- [ ] 自动优化建议
- [ ] 周报自动生成

### v2.9.0
- [ ] 跨任务学习（一个任务的经验应用到其他任务）
- [ ] 预测性维护（提前发现潜在问题）
- [ ] 自进化系统（自动优化重试策略）

---

## 📖 参考资料

- [灵犀学习层指南](LEARNING_LAYER_GUIDE.md)
- [灵犀性能监控](scripts/FAST_RESPONSE_BENCHMARK.md)
- [自动化改进计划](AUTOMATION_IMPROVEMENT_PLAN.md)

---

**© 2026 AI Love World | Made with 💕 by Scarlett**
