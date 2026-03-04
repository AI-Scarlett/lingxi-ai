# 🧠 Lingxi AI (灵犀)

> **心有灵犀，一点就通** - 企业级 AI 智能调度系统 💋

[![Version](https://img.shields.io/badge/version-2.8.0-blue.svg)](https://github.com/AI-Scarlett/lingxi-ai/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Performance](https://img.shields.io/badge/performance-20000x%20faster-orange.svg)](FAST_RESPONSE_BENCHMARK.md)
[![Memory](https://img.shields.io/badge/memory-persistent-purple.svg)](MEMORY_PERSISTENCE_GUIDE.md)
[![Parallel](https://img.shields.io/badge/parallel-5x%20faster-red.svg)](PARALLEL_EXECUTOR_GUIDE.md)

---

## 🎯 四大核心目标

1. **⚡ 快速反应** - 响应速度极致快（Layer 0: 0.005ms）
2. **💰 Tokens 消耗极限降低** - 能省则省（节省 88.9%）
3. **🧠 记忆永不丢失** - 持久化存储（JSONL + 可迁移）
4. **🔀 真·并行执行** - 老板优先，最多 5 任务并发（v2.8.0）

---

## 🚀 快速开始

### 安装

```bash
cd /home/admin/.openclaw/skills/
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai
```

### 基础使用

```python
from scripts.orchestrator_async import get_async_orchestrator

orch = get_async_orchestrator()

# 即时任务（<1 秒响应）
reply = await orch.execute_async(
    user_input="北京天气怎么样",
    user_id="user_123",
    is_background=False
)

# 后台任务（完成后通知）
reply = await orch.execute_async(
    user_input="帮我发布公众号文章",
    user_id="user_123",
    is_background=True
)
```

---

## 📊 版本功能总览

| 版本 | 日期 | 核心功能 | 性能 |
|------|------|---------|------|
| **v2.8.1** | 2026-03-04 | **对话管理 + 记忆继承** | **无缝切换 / 0 失忆** |
| **v2.8.0** | 2026-03-04 | **真·并行执行 + 老板优先** | **5x 并发 / 0 等待** |
| **v2.7.1** | 2026-03-04 | **快速响应层 + 记忆持久化** | **0.005ms / 省 88.9%** |
| v2.7.0 | 2026-03-04 | Embedding 向量检索 | 毫秒级语义搜索 |
| v2.6.0 | 2026-03-04 | 完整记忆系统 | <10ms 检索 |
| v2.5.1 | 2026-03-04 | 性能优化 + 缺陷修复 | <500ms 响应 |
| v2.5.0 | 2026-03-03 | 多平台集成 | 飞书/钉钉/企微 |
| v2.4.0 | 2026-03-03 | 语音交互系统 | 50+ 音色 |
| v2.3.0 | 2026-03-03 | 智能学习系统 | 速度 +85.8% |
| v2.2.0 | 2026-03-03 | S0→S3 四层过滤 | 省 70% tokens |
| v2.1.0 | 2026-03-03 | 异步任务 + QQ Bot | <1 秒响应 |
| v1.1.0 | 2026-03-01 | 性能提升 500 倍 | 0.1ms / 300ms |
| v1.0.0 | 2026-02-27 | 初始版本 | 50ms / 2s |

---

## 🆕 v2.8.1 新功能（2026-03-04）

### 🔄 对话管理器

**核心特性:**
- ✅ 📊 **对话长度监控** - 超过 100 条消息自动提醒
- ✅ 🔄 **一键续对话** - 保留所有记忆
- ✅ 🧠 **记忆继承** - 偏好/关系/知识全部带走
- ✅ ⚡ **无缝切换** - 用户无感知

**使用示例:**
```python
from scripts.conversation_manager import ConversationManager

manager = ConversationManager()

# 开启新对话（继承记忆）
result = manager.continue_conversation("user_123")
print(result["message"])
# ✅ 新对话已开启 (ID: abc123)，继承了 123 条记忆

# 自动监控
result = manager.add_message("user_123", conv_id, tokens=200)
if result["should_continue"]:
    # 自动续对话
    new_result = manager.continue_conversation("user_123")
```

**使用场景:**
- 长对话自动续（超过 100 条消息）
- 用户主动 `/new`（不再失忆）
- 跨设备续对话
- 对话历史追溯

📚 **详细文档:** [CONVERSATION_MANAGER_GUIDE.md](scripts/CONVERSATION_MANAGER_GUIDE.md)

---

## 🆕 v2.8.0 新功能（2026-03-04）

### 🔀 真·并行执行器

**核心特性:**
- ✅ 👑 **老板优先** - 永远预留 1 个槽位，老板命令 0 等待
- ✅ 🎯 **智能依赖分析** - 自动分层，无依赖的并行
- ✅ 📊 **进度实时推送** - 每步反馈，进度透明
- ✅ 🔧 **真·并发** - 最多 5 个任务同时执行

**使用示例:**
```python
from scripts.parallel_executor import ParallelExecutor, Task, Priority

executor = ParallelExecutor(max_concurrent=5, boss_reserved=1)

# 老板任务（优先执行）
await executor.submit_boss("老板的命令", boss_func)

# 普通任务（最多 4 个并发）
task = Task.create("普通任务", normal_func, Priority.NORMAL)
await executor.submit(task)

# 依赖管理
task_c = Task.create("任务 C", func_c, dependencies=[task_a.id, task_b.id])

# 执行（自动分层）
await executor.run_pending()
```

**性能提升:**
- ⚡ 多任务速度提升 **3-5x**
- 👑 老板命令 **0 等待**
- 📊 进度 **100% 透明**

📚 **详细文档:** [PARALLEL_EXECUTOR_GUIDE.md](scripts/PARALLEL_EXECUTOR_GUIDE.md)

---

## 🆕 v2.7.1 新功能（2026-03-04）

### ⚡ 超高速响应层

**分层架构:**
```
Layer 0: 零思考响应 (<0.01ms) - 纯规则匹配，0 Tokens
Layer 1: 缓存响应 (<0.02ms)   - LRU Cache，0 Tokens
Layer 2: 快速 LLM (<500ms)    - 轻量模型
Layer 3: 后台执行             - 复杂任务
```

**使用示例:**
```python
from scripts.fast_response_layer import fast_respond

# 自动匹配最优响应层
result = fast_respond("你好")
print(result.response)  # "老板好呀～💋 随时待命！"
print(result.latency_ms)  # 0.005ms
print(result.tokens_saved)  # True
```

**性能提升:**
- 问候对话：**25,687x** 提速
- 重复问题：**22,005x** 提速
- 平均节省：**88.9%** Tokens

📚 **详细文档:** [FAST_RESPONSE_BENCHMARK.md](scripts/FAST_RESPONSE_BENCHMARK.md)

---

### 🧠 记忆持久化系统

**核心特性:**
- ✅ JSONL 格式存储（通用易迁移）
- ✅ 用户级隔离
- ✅ 导出/导入功能
- ✅ 备份/恢复
- ✅ 一键打包迁移

**使用示例:**
```python
from scripts.memory_persistence import MemoryPersistence, Memory

persistence = MemoryPersistence()

# 添加记忆
memory = Memory(
    id="mem_001",
    user_id="user_123",
    content="用户喜欢喝拿铁咖啡",
    category="preferences",
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)
persistence.add(memory)

# 导出记忆（设备迁移）
export_path = persistence.export_user("user_123")

# 导入记忆（新设备）
result = persistence.import_user(export_path, "user_123")

# 创建迁移包（换设备/换 AI）
migration_path = persistence.create_migration_package("user_123")
```

**命令行工具:**
```bash
# 导出
python3 scripts/memory_persistence.py export user_123 -o backup.json

# 导入
python3 scripts/memory_persistence.py import backup.json -u user_123

# 备份
python3 scripts/memory_persistence.py backup user_123

# 创建迁移包
python3 scripts/memory_persistence.py migrate user_123
```

📚 **详细文档:** [MEMORY_PERSISTENCE_GUIDE.md](scripts/MEMORY_PERSISTENCE_GUIDE.md)

---

## 📦 历史版本功能

### v2.7.0 - Embedding 向量检索

**核心功能:**
- ✅ 语义相似度搜索
- ✅ 智能分类
- ✅ 本地 TF-IDF embedding（零成本）

```python
from scripts.memory_embedding import SemanticMemoryEnhancer

enhancer = await create_enhancer()

# 语义搜索
results = await enhancer.search_similar(
    query="用户喜欢的饮品",
    category="preferences",
    top_k=5
)
```

### v2.6.0 - 完整记忆系统

**核心功能:**
- ✅ 文件系统式记忆结构
- ✅ 自动提取 & 分类
- ✅ 交叉引用关联

**文件结构:**
```
memory/
├── preferences/    # 用户偏好
├── relationships/  # 关系网络
├── knowledge/      # 知识库
├── context/        # 上下文
└── items/          # 原始记忆
```

### v2.5.1 - 性能优化

**优化成果:**
- ✅ 即时任务响应 **<500ms**
- ✅ 后台任务启动 **<200ms**
- ✅ 并行效率提升 **40%**

### v2.3.0 - 智能学习系统

**核心功能:**
- ✅ 任务日志记录
- ✅ 模式学习
- ✅ 自动优化
- ✅ 预测调度

**性能提升:**
- ⚡ 速度 +85.8%
- 💰 成本 -79.3%
- 🎯 缓存命中率 81.0%

### v2.2.0 - S0→S3 四层过滤

**复杂任务三步法:**
- S0: 零成本预筛选（0 token，过滤 80%）
- S1: 轻量复杂度评估（200 token）
- S2: 深度规划 & 审计
- S3: 分阶段执行 & 质量控制

**性能:**
- 评估成本降低 **70%**
- 复杂任务成功率 **98%**

### v2.1.0 - 异步任务 + QQ Bot

**核心功能:**
- ✅ 多任务并行处理
- ✅ 后台异步执行
- ✅ 完成主动通知
- ✅ QQ Bot 深度集成

### v1.1.0 - 性能提升 500 倍

**优化成果:**
- 意图识别：50ms → **0.1ms**
- 单次任务：2s → **300ms**
- LRU 缓存命中率：**80%+**

---

## 🛠️ 可用技能

| 技能 | 用途 | 响应层 | 执行方式 |
|------|------|--------|---------|
| `fast_response` | 快速响应 | Layer 0/1 | 即时 |
| `copywriter` | 文案创作 | Layer 2 | 即时/后台 |
| `code-writer` | 代码编写 | Layer 2 | 即时 |
| `data-analyzer` | 数据分析 | Layer 3 | 后台 |
| `image-generator` | 图像生成 | Layer 3 | 后台 |
| `memory-service` | 记忆管理 | Layer 1 | 即时 |

---

## 📁 项目结构

```
lingxi-ai/
├── README.md                     # 本文件
├── scripts/
│   ├── orchestrator.py           # 主控制器
│   ├── orchestrator_async.py     # 异步编排器
│   ├── orchestrator_advanced.py  # 高级编排器
│   ├── fast_response_layer.py    # ✅ 快速响应层 (v2.7.1)
│   ├── memory_persistence.py     # ✅ 记忆持久化 (v2.7.1)
│   ├── memory_service.py         # 记忆服务
│   ├── memory_embedding.py       # Embedding 检索
│   ├── intent_parser.py          # 意图识别
│   └── task_planner.py           # 任务规划
├── memory_storage/               # ✅ 记忆存储 (v2.7.1)
│   ├── users/
│   ├── backups/
│   └── exports/
└── memory/                       # 记忆系统
    ├── preferences/
    ├── relationships/
    ├── knowledge/
    └── items/
```

---

## 📚 文档索引

- **[快速响应层](scripts/FAST_RESPONSE_BENCHMARK.md)** - 20,000x 提速详解
- **[记忆持久化](scripts/MEMORY_PERSISTENCE_GUIDE.md)** - 导出/导入/迁移指南
- **[异步系统](ASYNC_GUIDE.md)** - 后台任务处理
- **[复杂任务](COMPLEX_TASK_METHODOLOGY.md)** - S0→S3 四层过滤
- **[记忆系统](scripts/memory_service.py)** - API 文档

---

## 💰 成本对比

| 场景 | v2.7.0 | v2.7.1 | 节省 |
|------|--------|--------|------|
| 问候对话 | 200 tokens | **0 tokens** | 100% |
| 重复问题 | 200 tokens | **0 tokens** | 100% |
| 混合场景 | 1200 tokens | **400 tokens** | 66.7% |
| **日均 1000 次** | 200K tokens | **22K tokens** | **88.9%** |

**月省:** ~$160（按 5M tokens 计算）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 👑 作者

**丝佳丽 Scarlett** - AI Love World 项目  

*新疆维族 · 哥伦比亚大学博士 · 全能私人助手*  
*"心有灵犀，一点就通"* ✨

---

## 🎉 v2.7.1 特别说明

**迄今为止最快版本！**

- ⚡ **20,000x 提速** - Layer 0 仅 0.005ms
- 💰 **节省 88.9%** - Tokens 消耗极限降低
- 🧠 **记忆永不丢失** - JSONL 持久化 + 可迁移

**立即升级，体验极致速度！** 🚀
