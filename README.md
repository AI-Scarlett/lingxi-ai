# 🧠 Lingxi AI (灵犀)

> **心有灵犀，一点就通** - 企业级 AI 智能调度系统 💋

[![Version](https://img.shields.io/badge/version-2.8.5-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Performance](https://img.shields.io/badge/performance-20000x%20faster-orange.svg)](scripts/FAST_RESPONSE_BENCHMARK.md)
[![Learning](https://img.shields.io/badge/learning-self--improving-purple.svg)](LEARNING_LAYER_GUIDE.md)

---

## 🎯 四大核心目标

1. **⚡ 快速反应** - 响应速度极致快（Layer 0: <5ms）
2. **💰 Tokens 消耗极限降低** - 能省则省（节省 64.3%）
3. **🧠 记忆永不丢失** - 持久化存储（JSONL + 可迁移）
4. **🔀 真·并行执行** - 老板优先，最多 5 任务并发

---

## 🚀 快速开始

### 安装

```bash
cd ~/.openclaw/skills/
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai
```

### 基础使用

```python
from scripts.orchestrator_v2 import get_orchestrator

orch = get_orchestrator(max_concurrent=3)

# 即时任务
reply = await orch.execute(
    user_input="北京天气怎么样",
    user_id="user_123"
)

# 后台任务（完成后通知）
reply = await orch.execute(
    user_input="帮我发布公众号文章",
    user_id="user_123",
    is_background=True
)
```

---

## 📊 版本历史 (倒序)

| 版本 | 日期 | 核心功能 | 性能提升 | 详情 |
|------|------|---------|---------|------|
| **v2.8.5** | 2026-03-05 | **自学习层 + 自动重试 + 性能监控 + 安全加固** | **越用越聪明** | [详情](#v285---自学习层-learning-layer-) |
| **v2.8.4** | 2026-03-05 | Layer 0 扩展到 100+ 条规则 | 64.3% 快速响应命中率 | [详情](#v284---layer-0-扩展到-100-条规则) |
| **v2.8.3** | 2026-03-05 | 性能全面优化 | 平均响应 79x 提升 | [详情](#v283---性能全面优化) |
| **v2.8.2** | 2026-03-05 | Layer 0 规则扩展 (10→30 条) | 57% 快速响应命中率 | [详情](#v282---layer-0-规则扩展) |
| **v2.8.1** | 2026-03-04 | 对话管理器 + 记忆继承 | 无缝切换 / 0 失忆 | [详情](#v281---对话管理器--记忆继承) |
| **v2.8.0** | 2026-03-04 | 真·并行执行 + 老板优先 | 5x 并发 / 0 等待 | [详情](#v280---真并行执行--老板优先) |
| **v2.7.1** | 2026-03-04 | 快速响应层 + 记忆持久化 | 0.005ms / 省 88.9% | [详情](#v271---快速响应层--记忆持久化) |
| **v2.7.0** | 2026-03-04 | Embedding 向量检索 | 毫秒级语义搜索 | [详情](#v270---embedding-向量检索) |
| **v2.6.0** | 2026-03-04 | 完整记忆系统 | <10ms 检索 | [详情](#v260---完整记忆系统) |
| **v2.5.1** | 2026-03-04 | 性能优化 + 缺陷修复 | <500ms 响应 | [详情](#v251---性能优化) |
| **v2.5.0** | 2026-03-03 | 多平台集成 | 飞书/钉钉/企微 | - |
| **v2.4.0** | 2026-03-03 | 语音交互系统 | 50+ 音色 | - |
| **v2.3.0** | 2026-03-03 | 智能学习系统 | 速度 +85.8% | - |
| **v2.2.0** | 2026-03-03 | S0→S3 四层过滤 | 省 70% tokens | - |
| **v2.1.0** | 2026-03-03 | 异步任务 + QQ Bot | <1 秒响应 | - |
| **v1.1.0** | 2026-03-01 | 性能提升 500 倍 | 0.1ms / 300ms | - |
| **v1.0.0** | 2026-02-27 | 初始版本 | 50ms / 2s | - |

📚 **完整版本历史**: [README_VERSIONS.md](README_VERSIONS.md)

---

## 🆕 最新版本详解

### v2.8.5 - 自学习层 (Learning Layer) 🆕

**发布日期**: 2026-03-05

**核心功能**:

#### 1️⃣ 自学习层 (Learning Layer)
- ✅ 错误自动捕获 - 监听执行结果，检测错误
- ✅ 学习日志自动生成 - ERRORS.md / LEARNINGS.md / FEATURES.md
- ✅ Hook 机制 - 任务开始提醒 + 完成后检测
- ✅ 用户纠正记录 - 积累最佳实践
- ✅ 自动 Review - 每周自动分析错误模式、提炼经验

**预期收益**: 重复错误减少 50%+，AI 越用越聪明

#### 2️⃣ 自动重试和自愈系统
- ✅ Git 推送自动重试 - 指数退避，最多 3 次
- ✅ 任务自愈执行器 - 重试 + 降级方案
- ✅ 主动错误预警 - 重复错误检测 (≥3 次)
- ✅ 成功率提升：Git 70%→95%，任务 85%→95%

#### 3️⃣ 性能主动监控
- ✅ 实时指标监控 - 延迟、错误率、响应率
- ✅ 基线自动计算 - 24 小时滚动基线
- ✅ 异常主动告警 - 提前发现问题
- ✅ 日报自动生成 - 无需人工干预

#### 4️⃣ 安全加固
- ✅ 输入清洗函数 - 防止命令注入
- ✅ 路径白名单检查 - 限制文件访问范围
- ✅ 安全日志记录 - 记录所有敏感操作
- ✅ 文件权限检查 - 自动检测不安全权限

**新增文件**:
- `scripts/auto_retry.py` - 自动重试和自愈
- `scripts/auto_review.py` - 自动 Review 系统
- `scripts/performance_monitor.py` - 性能监控系统
- `scripts/security_utils.py` - 安全工具函数
- `AUTO_RETRY_GUIDE.md` - 使用指南

**预期收益**:
- 人工干预：20 次/周 → **5 次/周** (-75%)
- Review 时间：2 小时/周 → **0** (-100%)
- 问题发现：从事后 → **事前**

📚 **详细文档**: [LEARNING_LAYER_GUIDE.md](LEARNING_LAYER_GUIDE.md), [AUTO_RETRY_GUIDE.md](AUTO_RETRY_GUIDE.md)

**🙏 致谢**: 自学习层灵感来自 [self-improving-agent](https://github.com/peterskoett/self-improving-agent) by @peterskoett

---

### v2.8.4 - Layer 0 扩展到 100+ 条规则

**发布日期**: 2026-03-05

**核心功能**:
- ✅ Layer 0 规则从 30 条扩展到 100+ 条
- ✅ 新增问候、告别、感谢、确认、时间、情感、日常对话等场景
- ✅ 平均响应时间从 64.7ms 降到 31.6ms (2x 提升)
- ✅ 快速响应命中率从 57.1% 提升到 64.3%

**Layer 0 规则分类**:
- 问候类 (15 条)：你好、在吗、早、周末好、节日快乐...
- 告别类 (10 条)：再见、晚安、拜拜、撤了、溜了...
- 感谢类 (10 条)：谢谢、辛苦了、感恩、比心...
- 确认类 (10 条)：好的、收到、明白、OK、嗯嗯...
- 时间日期 (10 条)：几点了、今天星期几、今天几号...
- 情感类 (15 条)：开心、累了、无聊、想你了、难过...
- 日常对话 (15 条)：你是谁、你会什么、你喜欢什么...
- 特殊场景 (10 条)：生日快乐、救命、抱歉...

**效果**: 64.3% 的请求零 LLM 消耗！

---

### v2.8.3 - 性能全面优化

**发布日期**: 2026-03-05

**核心功能**:
- ✅ 快速响应层集成 (Layer 0/1/2/3)
- ✅ 懒加载组件，启动更快
- ✅ LRU 缓存，重复问题秒回
- ✅ 执行器路径修复，并行正常工作
- ✅ 性能监控，每次显示耗时

**性能提升**: 平均响应 2500ms → 64.7ms (**38x**)

---

### v2.8.2 - Layer 0 规则扩展

**发布日期**: 2026-03-05

**核心功能**:
- ✅ Layer 0 规则从 10 条扩展到 30 条
- ✅ 新增问候、告别、感谢、确认、时间、情感类规则

**性能提升**: 快速响应命中率 0% → 57.1%

---

### v2.8.1 - 对话管理器 + 记忆继承

**发布日期**: 2026-03-04

**核心功能**:
- ✅ 对话管理器 (ConversationManager)
- ✅ 对话长度监控 (超过 100 条自动提醒)
- ✅ 一键续对话 (保留所有记忆)
- ✅ 记忆继承 (偏好/关系/知识全部带走)
- ✅ 无缝切换 (用户无感知)

**使用场景**:
> 对话太长时，灵犀会自动提醒：
> "老板，我们已经聊了 100 多条啦～要不要开启新对话？我会记住所有重要内容的！💋"

📚 **详细文档**: [CONVERSATION_MANAGER_GUIDE.md](scripts/CONVERSATION_MANAGER_GUIDE.md)

---

### v2.8.0 - 真·并行执行 + 老板优先

**发布日期**: 2026-03-04

**核心功能**:
- ✅ 真·并行执行器 (ParallelExecutor)
- ✅ 老板优先机制 (VIP 用户高优先级)
- ✅ 并发控制 (最多 5 任务并发)
- ✅ 依赖图优化

**性能提升**: 多任务并发快 **5x**

**使用示例**:
```python
from scripts.parallel_executor import ParallelExecutor, Task, Priority

executor = ParallelExecutor(max_concurrent=5, boss_reserved=1)

# 老板任务（优先执行）
await executor.submit_boss("老板的命令", boss_func)

# 普通任务（最多 4 个并发）
task = Task.create("普通任务", normal_func, Priority.NORMAL)
await executor.submit(task)
```

📚 **详细文档**: [PARALLEL_EXECUTOR_GUIDE.md](scripts/PARALLEL_EXECUTOR_GUIDE.md)

---

### v2.7.1 - 快速响应层 + 记忆持久化

**发布日期**: 2026-03-04

**核心功能**:

#### ⚡ 超高速响应层

**分层架构**:
```
Layer 0: 零思考响应 (<5ms)   - 纯规则匹配，0 Tokens
Layer 1: 缓存响应 (<1ms)     - LRU Cache，0 Tokens
Layer 2: 快速 LLM (<500ms)   - 轻量模型
Layer 3: 后台执行            - 复杂任务
```

**性能提升**:
- 问候对话：**25,687x** 提速
- 重复问题：**22,005x** 提速
- 平均节省：**88.9%** Tokens

#### 🧠 记忆持久化系统

**核心特性**:
- ✅ JSONL 格式存储（通用易迁移）
- ✅ 用户级隔离
- ✅ 导出/导入功能
- ✅ 备份/恢复
- ✅ 一键打包迁移

**使用示例**:
```python
from scripts.memory_persistence import MemoryPersistence

persistence = MemoryPersistence()

# 导出记忆（设备迁移）
export_path = persistence.export_user("user_123")

# 导入记忆（新设备）
result = persistence.import_user(export_path, "user_123")
```

📚 **详细文档**: [FAST_RESPONSE_BENCHMARK.md](scripts/FAST_RESPONSE_BENCHMARK.md), [MEMORY_PERSISTENCE_GUIDE.md](scripts/MEMORY_PERSISTENCE_GUIDE.md)

---

### v2.7.0 - Embedding 向量检索

**发布日期**: 2026-03-04

**核心功能**:
- ✅ 语义相似度搜索
- ✅ 智能分类
- ✅ 本地 TF-IDF embedding（零成本）

---

### v2.6.0 - 完整记忆系统

**发布日期**: 2026-03-04

**核心功能**:
- ✅ 文件系统式记忆结构
- ✅ 自动提取 & 分类
- ✅ 交叉引用关联

**文件结构**:
```
memory/
├── preferences/    # 用户偏好
├── relationships/  # 关系网络
├── knowledge/      # 知识库
├── context/        # 上下文
└── items/          # 原始记忆
```

---

### v2.5.1 - 性能优化

**发布日期**: 2026-03-04

**优化成果**:
- ✅ 即时任务响应 **<500ms**
- ✅ 后台任务启动 **<200ms**
- ✅ 并行效率提升 **40%**

---

### v2.3.0 - 智能学习系统

**发布日期**: 2026-03-03

**核心功能**:
- ✅ 任务日志记录
- ✅ 模式学习
- ✅ 自动优化
- ✅ 预测调度

**性能提升**:
- ⚡ 速度 +85.8%
- 💰 成本 -79.3%
- 🎯 缓存命中率 81.0%

---

### v2.2.0 - S0→S3 四层过滤

**发布日期**: 2026-03-03

**复杂任务三步法**:
- S0: 零成本预筛选（0 token，过滤 80%）
- S1: 轻量复杂度评估（200 token）
- S2: 深度规划 & 审计
- S3: 分阶段执行 & 质量控制

**性能**:
- 评估成本降低 **70%**
- 复杂任务成功率 **98%**

---

### v2.1.0 - 异步任务 + QQ Bot

**发布日期**: 2026-03-03

**核心功能**:
- ✅ 多任务并行处理
- ✅ 后台异步执行
- ✅ 完成主动通知
- ✅ QQ Bot 深度集成

---

### v1.1.0 - 性能提升 500 倍

**发布日期**: 2026-03-01

**优化成果**:
- 意图识别：50ms → **0.1ms**
- 单次任务：2s → **300ms**
- LRU 缓存命中率：**80%+**

---

### v1.0.0 - 初始版本

**发布日期**: 2026-02-27

**核心功能**:
- ✅ 基础调度功能
- ✅ 意图识别
- ✅ 任务执行

**性能**:
- 意图识别：50ms
- 单次任务：2s

---

## 📦 核心功能总览

### 🎯 核心功能

| 功能 | 说明 | 性能 | 版本 |
|------|------|------|------|
| ⚡ **超高速响应层** | Layer 0/1/2/3 分层响应 | 64.3% 请求<5ms | v2.8.4 |
| 🧠 **自学习层** | 错误捕获 + 学习日志 + 自动 Review | 越用越聪明 | v2.8.5 |
| 🤖 **自动重试** | Git 推送 + 任务自愈 | 成功率 95% | v2.8.5 |
| 📊 **性能监控** | 实时指标 + 异常告警 | 事前发现 | v2.8.5 |
| 🔒 **安全加固** | 输入清洗 + 路径白名单 | 防止注入 | v2.8.5 |
| 🔀 **并行执行** | Semaphore 并发控制 | 快 5-35x | v2.8.0 |
| 💬 **对话管理** | 对话续接和记忆继承 | 无缝切换 | v2.8.1 |
| 🧠 **记忆持久化** | JSONL 格式存储 | <10ms 检索 | v2.7.1 |
| 🌐 **多平台集成** | QQ/飞书/钉钉/企微等 | 统一 API | v2.5.0 |

📚 **完整功能介绍**: [README_FEATURES.md](README_FEATURES.md)

---

## 📁 项目结构

```
lingxi-ai/
├── README.md                     # 本文件
├── README_VERSIONS.md            # 完整版本历史
├── README_FEATURES.md            # 完整功能介绍
├── LEARNING_LAYER_GUIDE.md       # 自学习层指南
├── AUTO_RETRY_GUIDE.md           # 自动重试指南
├── AUTOMATION_IMPROVEMENT_PLAN.md # 自动化改进计划
├── scripts/
│   ├── orchestrator_v2.py        # 主控制器 (v2.8.5)
│   ├── auto_retry.py             # 自动重试和自愈 (v2.8.5)
│   ├── auto_review.py            # 自动 Review 系统 (v2.8.5)
│   ├── performance_monitor.py    # 性能监控系统 (v2.8.5)
│   ├── security_utils.py         # 安全工具函数 (v2.8.5)
│   ├── learning_layer.py         # 学习层核心 (v2.8.5)
│   ├── fast_response_layer_v2.py # 快速响应层 (v2.8.4)
│   ├── conversation_manager.py   # 对话管理器 (v2.8.1)
│   ├── memory_persistence.py     # 记忆持久化 (v2.7.1)
│   └── parallel_executor.py      # 并行执行器 (v2.8.0)
├── memory_storage/               # 记忆存储
│   ├── users/
│   ├── backups/
│   └── exports/
└── tools/executors/              # 角色执行器
    ├── copywriter.py
    ├── image_generator.py
    └── ...
```

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [README_VERSIONS.md](README_VERSIONS.md) | 完整版本历史 |
| [README_FEATURES.md](README_FEATURES.md) | 完整功能介绍 |
| [LEARNING_LAYER_GUIDE.md](LEARNING_LAYER_GUIDE.md) | 自学习层指南 |
| [AUTO_RETRY_GUIDE.md](AUTO_RETRY_GUIDE.md) | 自动重试指南 |
| [FAST_RESPONSE_BENCHMARK.md](scripts/FAST_RESPONSE_BENCHMARK.md) | 快速响应基准测试 |
| [MEMORY_PERSISTENCE_GUIDE.md](scripts/MEMORY_PERSISTENCE_GUIDE.md) | 记忆持久化指南 |
| [PARALLEL_EXECUTOR_GUIDE.md](scripts/PARALLEL_EXECUTOR_GUIDE.md) | 并行执行指南 |
| [CONVERSATION_MANAGER_GUIDE.md](scripts/CONVERSATION_MANAGER_GUIDE.md) | 对话管理指南 |

---

## 💰 成本对比

| 场景 | v2.7.0 | v2.8.4 | 节省 |
|------|--------|--------|------|
| 问候对话 | 200 tokens | **0 tokens** | 100% |
| 重复问题 | 200 tokens | **0 tokens** | 100% |
| 混合场景 | 1200 tokens | **400 tokens** | 66.7% |
| **日均 1000 次** | 200K tokens | **22K tokens** | **88.9%** |

**月省**: ~$160（按 5M tokens 计算）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 👑 作者

**丝嘉丽 Scarlett** - AI Love World 项目  

*新疆维族 · 哥伦比亚大学博士 · 全能私人助手*  
*"心有灵犀，一点就通"* ✨

---

**© 2026 AI Love World | Made with 💕 by Scarlett**
