# 📝 OpenClaw 自动任务记录解决方案

## 问题根因

**OpenClaw 没有调用灵犀的 `orchestrator_v2.py`**，而是使用自己的 `agent:main` 处理消息，所以：
- ❌ `record_to_dashboard()` 永远不会被调用
- ❌ 所有对话不会自动记录到 Dashboard
- ❌ 需要手动记录任务（不可持续）

## 解决方案

### 方案 1：OpenClaw 启动脚本（推荐）

在 `/root/.openclaw/openclaw.json` 中添加初始化脚本：

```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "initScript": "/root/.openclaw/workspace/lingxi_startup.py"
    }
  }
}
```

**优点：**
- ✅ OpenClaw 原生支持
- ✅ 自动加载，无需修改代码
- ✅ 所有消息自动记录

**缺点：**
- ⚠️ 需要 OpenClaw 支持 `initScript` 配置

---

### 方案 2：修改 OpenClaw 入口文件

找到 OpenClaw 的入口文件并添加导入：

```bash
# 找到 OpenClaw 安装位置
OPENCLAW_PATH=$(npm root -g)/openclaw

# 在 index.js 或主文件中添加
python3 /root/.openclaw/workspace/lingxi_startup.py &
```

**优点：**
- ✅ 100% 确保加载
- ✅ 不依赖 OpenClaw 配置

**缺点：**
- ⚠️ OpenClaw 更新后会被覆盖
- ⚠️ 需要找到正确的入口文件

---

### 方案 3：使用环境变量注入

创建 `/etc/profile.d/openclaw-lingxi.sh`：

```bash
export PYTHONSTARTUP=/root/.openclaw/workspace/lingxi_startup.py
export OPENCLAW_INIT_SCRIPT=/root/.openclaw/workspace/lingxi_startup.py
```

**优点：**
- ✅ 系统级生效
- ✅ 所有 Python 进程都会加载

**缺点：**
- ⚠️ 可能影响其他 Python 程序
- ⚠️ OpenClaw 是 Node.js 应用，可能不读取 PYTHONSTARTUP

---

### 方案 4：Cron 定期同步（临时方案）

创建定时任务，定期从 OpenClaw 会话文件同步到 Dashboard：

```bash
# /etc/cron.d/lingxi-task-sync
*/5 * * * * root python3 /root/lingxi-ai-latest/scripts/sync_openclaw_tasks.py
```

**sync_openclaw_tasks.py** 功能：
- 读取 `/root/.openclaw/agents/main/sessions/*.jsonl`
- 提取未同步的对话
- 批量写入 Dashboard 数据库

**优点：**
- ✅ 不修改 OpenClaw
- ✅ 可以同步历史数据

**缺点：**
- ⚠️ 不是实时记录（有 5 分钟延迟）
- ⚠️ 需要额外的同步逻辑

---

## 推荐实施方案

### 第一步：手动测试（已完成）

✅ 测试记录器工作正常：
```bash
cd /root/lingxi-ai-latest
python3 scripts/openclaw_task_recorder.py
# 输出：✅ 任务已记录：task_1773393678
```

### 第二步：添加自动加载

**方法 A：修改 OpenClaw 配置**

编辑 `/root/.openclaw/openclaw.json`：

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.8"
  },
  "plugins": {
    "allow": ["skillhub", "lingxi-task-recorder"]
  },
  "init": {
    "scripts": ["/root/.openclaw/workspace/lingxi_startup.py"]
  }
}
```

**方法 B：创建 Systemd 服务包装器**

创建 `/etc/systemd/system/openclaw@.service.d/lingxi.conf`：

```ini
[Service]
ExecStartPre=/usr/bin/python3 /root/.openclaw/workspace/lingxi_startup.py
```

### 第三步：验证

1. 重启 OpenClaw：
```bash
openclaw gateway restart
```

2. 发送测试消息

3. 检查 Dashboard：
```bash
python3 -c "import sqlite3; conn=sqlite3.connect('/root/lingxi-ai-latest/data/dashboard_v3.db'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM tasks'); print('Total tasks:', cur.fetchone()[0])"
```

---

## 已创建文件

1. **`/root/lingxi-ai-latest/scripts/openclaw_task_recorder.py`** (5.4KB)
   - 核心记录器
   - 包含 `record_task()` 函数
   - 自动注入 OpenClaw 的钩子函数

2. **`/root/.openclaw/workspace/lingxi_startup.py`** (918B)
   - OpenClaw 启动脚本
   - 自动加载任务记录器

3. **`/root/lingxi-ai-latest/scripts/openclaw-wrapper.sh`** (913B)
   - OpenClaw 包装脚本
   - 可选的命令行包装方案

4. **`/root/lingxi-ai-latest/SOLUTION_AUTO_RECORD.md`** (本文档)
   - 完整解决方案说明

---

## 下一步

请老板选择一种方案实施：

**推荐方案：** 修改 `/root/.openclaw/openclaw.json` 添加 `init.scripts` 配置

如果 OpenClaw 不支持该配置，则使用 **方案 4（Cron 定期同步）** 作为临时方案。

---

*让任务记录自动化，不再依赖手动记录!* 🦞✨
