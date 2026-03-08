# 灵犀共享记忆库 - 使用文档

> **版本:** v1.0  
> **作者:** 斯嘉丽 Scarlett  
> **日期:** 2026-03-08

---

## 📚 概述

灵犀共享记忆库是一个**跨渠道记忆同步与查询系统**，支持：

1. ✅ **按渠道 + 用户 ID 组织记忆** - 无需统一 GlobalID，直接使用各渠道原生 ID
2. ✅ **凌晨 2 点定时同步** - 自动同步各渠道记忆到共享库
3. ✅ **用户手动绑定多渠道** - 用户确认后可跨渠道共享记忆
4. ✅ **跨渠道记忆查询** - 在任意渠道可查询绑定渠道的历史记忆

---

## 🏗️ 架构设计

### 存储结构

```
memory/shared/
├── users/                       # 按渠道 + 用户 ID 组织
│   ├── feishu/
│   │   └── <user_id_hash>/
│   │       ├── profile.md
│   │       └── memories/
│   │           └── 2026-03-08.md
│   ├── qqbot/
│   │   └── <user_id_hash>/
│   └── ...
├── cross-channel-links/         # 多渠道绑定关系
│   ├── index.json
│   └── links/
│       └── link-1772930067.json
├── sync-logs/                   # 同步日志
│   └── 2026-03/
│       └── 2026-03-08.json
└── config.json
```

### 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **共享记忆库** | `shared_memory.py` | 记忆存储、查询、绑定管理 |
| **同步调度器** | `sync_scheduler.py` | 凌晨 2 点定时同步 |
| **绑定管理** | `channel_linking.py` | 多渠道绑定交互工具 |

---

## 🚀 快速开始

### 1. 保存记忆

```python
from shared_memory import SharedMemoryService

service = SharedMemoryService()

# 保存记忆
await service.save_memory(
    channel="feishu",
    user_id="ou_4192609eb71f18ae82f9163f02bef144",
    content="用户喜欢简洁的回复风格",
    metadata={"topic": "用户偏好"}
)
```

### 2. 绑定多渠道

```python
from channel_linking import ChannelLinkingManager

manager = ChannelLinkingManager()

# 创建绑定
result = await manager.create_binding(
    channels={
        "feishu": "ou_xxx",
        "qqbot": "7941xxx"
    },
    user_note="老板的多渠道绑定"
)

print(result)
# {'success': True, 'link_id': 'link-1772930067', ...}
```

### 3. 查询跨渠道记忆

```python
# 从 qqbot 查询（能看到 feishu 的记忆）
memories = await manager.get_cross_channel_memories(
    channel="qqbot",
    user_id="7941xxx",
    days=7
)

print(memories)
# {'total_entries': 5, 'memories_by_channel': {'feishu': [...], 'qqbot': [...]}}
```

### 4. 立即执行同步

```python
from sync_scheduler import SyncSchedulerService

sync_service = SyncSchedulerService()

# 立即同步
result = await sync_service.sync_now()

print(result)
# {'status': 'success', 'memories_synced': 10, ...}
```

---

## 📖 CLI 命令

### 共享记忆库测试

```bash
cd /root/.openclaw/skills/lingxi/scripts

# 运行演示场景
python3 test_shared_memory.py --demo

# 运行所有测试
python3 test_shared_memory.py --all

# 只测试共享记忆库
python3 test_shared_memory.py --memory

# 只测试同步调度器
python3 test_shared_memory.py --sync

# 只测试渠道绑定
python3 test_shared_memory.py --link
```

### 同步调度器

```bash
# 立即执行同步
python3 sync_scheduler.py --sync-now

# 查看同步状态
python3 sync_scheduler.py --status

# 查看最近 7 天同步历史
python3 sync_scheduler.py --history 7

# 查看下次同步时间
python3 sync_scheduler.py --next
```

### 多渠道绑定管理

```bash
# 交互式绑定工具
python3 channel_linking.py --bind

# 查询绑定关系
python3 channel_linking.py --query feishu ou_xxx

# 列出所有绑定
python3 channel_linking.py --list

# 查看跨渠道记忆
python3 channel_linking.py --memories feishu ou_xxx --days 7
```

---

## 🔗 多渠道绑定流程

### 场景 1: 用户主动绑定

```
用户说："我的飞书和 QQ 是同一个账号，可以同步记忆"

→ 调用 create_binding()
→ 创建绑定关系
→ 用户确认后生效
```

### 场景 2: 系统建议绑定

```
系统检测到两个渠道的用户画像高度相似

→ 提示用户："检测到您的飞书和 QQ 使用习惯相似，是否绑定？"
→ 用户确认后调用 create_binding()
```

### 场景 3: 解除绑定

```
用户说："取消我的多渠道绑定"

→ 调用 remove_binding()
→ 删除或停用绑定关系
```

---

## ⏰ 定时同步配置

### Cron 配置

在系统的 crontab 中添加：

```bash
# 每天凌晨 2 点执行同步
0 2 * * * cd /root/.openclaw/skills/lingxi/scripts && python3 sync_scheduler.py --sync-now >> /var/log/lingxi_sync.log 2>&1
```

### OpenClaw 心跳任务

在 `HEARTBEAT.md` 中添加：

```markdown
## ⏰ 定时任务

- ⏰ **记忆同步**: 每天凌晨 2 点同步各渠道记忆到共享库
  - 周期：0 2 * * *
  - 命令：python3 /root/.openclaw/skills/lingxi/scripts/sync_scheduler.py --sync-now
```

---

## 🔒 隐私与安全

### 默认行为

- ✅ **默认不跨渠道** - 除非用户主动绑定
- ✅ **用户确认机制** - 绑定需要用户明确确认
- ✅ **可逆操作** - 随时可以解除绑定

### 脱敏处理

同步时自动脱敏以下内容：
- 密码、token、密钥
- 身份证号、银行卡号
- 手机号、邮箱

### 数据保留

- 默认保留最近 **30 天** 的记忆
- 可配置 `retain_days` 参数调整

---

## 📊 查询触发场景

### 1. 会话启动时预加载

```python
# 新会话开始时自动加载最近记忆
context = await service.get_context(
    channel=current_channel,
    user_id=current_user_id,
    cross_channel=True
)
```

### 2. 语义匹配触发

```python
# 用户提到"昨天说的..."时
if "昨天" in user_input or "上次" in user_input:
    memories = await service.query_memories(
        channel=current_channel,
        user_id=current_user_id,
        start_date=(now - timedelta(days=7)).strftime("%Y-%m-%d"),
        cross_channel=True
    )
```

### 3. 定时心跳检查

```python
# Heartbeat 任务执行时
async def heartbeat_check():
    # 检查是否有新的跨渠道记忆
    memories = await service.query_memories(...)
    if memories:
        notify_user(f"您有其他渠道的新记忆：{len(memories)}条")
```

### 4. 任务完成回写

```python
# 子 Agent 完成任务后
if task_result.should_remember:
    await service.save_memory(
        channel=current_channel,
        user_id=current_user_id,
        content=task_result.summary,
        metadata={"topic": task_result.topic}
    )
```

### 5. 显式查询命令

```python
# 用户明确指令："查一下共享记忆里关于 XX 的内容"
if user_input.startswith("查一下") or "共享记忆" in user_input:
    query = extract_query(user_input)
    results = await service.retrieve(query, cross_channel=True)
```

---

## 🧪 测试示例

### 完整测试流程

```bash
# 1. 清理旧数据（可选）
rm -rf ~/.openclaw/workspace/memory/shared

# 2. 运行演示场景
python3 test_shared_memory.py --demo

# 3. 查看生成的文件
tree ~/.openclaw/workspace/memory/shared

# 4. 手动测试绑定
python3 channel_linking.py --bind

# 5. 测试同步
python3 sync_scheduler.py --sync-now

# 6. 查看同步历史
python3 sync_scheduler.py --history 7
```

---

## 📝 API 参考

### SharedMemoryService

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `save_memory()` | channel, user_id, content, date, metadata | None | 保存记忆 |
| `query_memories()` | channel, user_id, start_date, end_date, cross_channel | Dict[str, str] | 查询记忆 |
| `bind_channels()` | channels, user_note | ChannelLink | 绑定渠道 |
| `get_linked_channels()` | channel, user_id | Optional[Dict] | 获取绑定渠道 |
| `list_bindings()` | - | List[Dict] | 列出所有绑定 |
| `get_sync_history()` | days | List[Dict] | 获取同步历史 |

### ChannelLinkingManager

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create_binding()` | channels, user_note, require_confirmation | Dict | 创建绑定 |
| `get_binding()` | channel, user_id | Optional[Dict] | 查询绑定 |
| `remove_binding()` | link_id, channel, user_id | Dict | 解除绑定 |
| `get_cross_channel_memories()` | channel, user_id, days | Dict | 跨渠道记忆 |

### SyncSchedulerService

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `sync_now()` | - | Dict | 立即同步 |
| `get_sync_history()` | days | List[Dict] | 同步历史 |
| `get_next_sync_time()` | - | str | 下次同步时间 |
| `check_sync_status()` | - | Dict | 同步状态 |

---

## 🎯 最佳实践

### 1. 记忆内容规范

```markdown
## [时间戳] 主题

**渠道:** feishu  
**用户 ID:** ou_xxx

记忆内容...

---
```

### 2. 绑定命名规范

```python
# 好的命名
user_note = "老板的工作账号绑定"

# 避免的命名
user_note = "test"  # 太模糊
```

### 3. 同步日志监控

```python
# 定期检查同步状态
status = await sync_service.check_sync_status()
if status['last_sync']['status'] != 'success':
    alert_admin("同步失败，请检查日志")
```

### 4. 性能优化

- 使用日期范围查询，避免加载全部记忆
- 跨渠道查询时限制天数（建议 7-30 天）
- 定期清理旧同步日志

---

## ❓ 常见问题

### Q: 绑定后记忆会立即同步吗？
A: 不会。绑定只是建立渠道关联，记忆同步在凌晨 2 点执行。可以手动调用 `sync_now()` 立即同步。

### Q: 解除绑定后记忆会删除吗？
A: 不会。解除绑定只是断开渠道关联，各渠道的记忆仍然保留。

### Q: 可以绑定超过 2 个渠道吗？
A: 可以。支持绑定任意数量的渠道。

### Q: 同步失败怎么办？
A: 查看同步日志 `sync-logs/` 目录，根据错误信息排查。常见问题：权限不足、磁盘空间不足。

---

## 📞 支持

如有问题，请联系：
- 作者：斯嘉丽 Scarlett
- 项目：灵犀 (Lingxi) v3.0
- 文档位置：`/root/.openclaw/skills/lingxi/docs/SHARED_MEMORY.md`

---

_心有灵犀，一点就通_ 💋
