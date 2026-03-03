# 上传代码到 GitHub - 完整指南

> **本地代码已准备好，选择一种方式上传到 GitHub** 💋

---

## 📦 本地提交状态

✅ **已完成 2 个提交：**

1. `feat: 异步任务系统 - 多任务并行处理支持`
2. `docs: 添加 GitHub 推送指南和自动化脚本`

**新增 22 个文件：**
- 6 个核心模块
- 3 个测试/工具脚本
- 7 个文档
- 4 个微信发布工具
- 2 个配置文件更新

---

## 🚀 推送方式

### 方式 1：使用 Git + Token（最可靠）⭐

#### Step 1: 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. 填写备注：`lingxi-ai-deploy`
4. 选择权限：✅ **repo** (Full control of private repositories)
5. 点击 **"Generate token"**
6. **复制 Token**（只显示一次，保存好！）

#### Step 2: 设置 Token

```bash
# 方式 A: 临时使用（推荐）
export GITHUB_TOKEN=<你的 token>

# 方式 B: 保存到文件
echo "<你的 token>" > ~/.github_token
chmod 600 ~/.github_token
```

#### Step 3: 推送代码

```bash
cd ~/.openclaw/skills/lingxi

# 使用 Token 推送
git remote set-url origin https://${GITHUB_TOKEN}@github.com/AI-Scarlett/lingxi-ai.git
git push origin main
```

**成功输出示例：**
```
Enumerating objects: 150, done.
Counting objects: 100% (150/150), done.
Delta compression using up to 8 threads
Compressing objects: 100% (120/120), done.
Writing objects: 100% (125/125), 45.20 KiB | 5.02 MiB/s, done.
Total 125 (delta 85), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (85/85), completed with 15 local objects.
To https://github.com/AI-Scarlett/lingxi-ai.git
   d098f4f..a0847e5  main -> main
```

---

### 方式 2：使用 SSH

#### Step 1: 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "scarlett@ailoveworld.com"
# 一路回车即可
```

#### Step 2: 添加公钥到 GitHub

```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

复制输出内容，然后：
1. 访问 https://github.com/settings/keys
2. 点击 **"New SSH key"**
3. 标题：`lingxi-ai-deploy`
4. 粘贴公钥内容
5. 点击 **"Add SSH key"**

#### Step 3: 推送代码

```bash
cd ~/.openclaw/skills/lingxi

# 切换到 SSH 远程
git remote set-url origin git@github.com:AI-Scarlett/lingxi-ai.git

# 推送
git push origin main
```

---

### 方式 3：使用 GitHub Desktop（图形界面）

1. 下载 GitHub Desktop: https://desktop.github.com
2. 登录 GitHub 账号
3. Clone 仓库：`AI-Scarlett/lingxi-ai`
4. 复制本地代码到 Clone 的目录
5. 在 GitHub Desktop 中 Commit & Push

---

### 方式 4：手动上传文件（最后的选择）

1. 访问 https://github.com/AI-Scarlett/lingxi-ai
2. 点击 **"Add file"** → **"Upload files"**
3. 拖拽以下文件上传：

**核心模块（6 个）：**
- `scripts/task_manager.py`
- `scripts/async_executor.py`
- `scripts/orchestrator_async.py`
- `scripts/lingxi_qqbot.py`
- `scripts/qqbot_bridge.py`
- `scripts/qqbot-bridge.sh`

**测试工具（3 个）：**
- `scripts/test_async_system.py`
- `scripts/demo.py`
- `scripts/push-to-github.sh`

**文档（7 个）：**
- `README_QQBOT.md`
- `QQBOT_INTEGRATION.md`
- `ASYNC_GUIDE.md`
- `IMPLEMENTATION_SUMMARY.md`
- `INTEGRATION_COMPLETE.md`
- `FINAL_SUMMARY.md`
- `PUSH_TO_GITHUB.md`

**微信工具（4 个）：**
- `tools/publishers/wechat/wechat_debug.py`
- `tools/publishers/wechat/wechat_publisher.py`
- `tools/publishers/wechat/wechat_simple.py`
- `tools/publishers/wechat/wechat_v3.py`

**其他（2 个）：**
- `.gitignore`
- `scripts/orchestrator.py` (已修改)

4. 填写提交信息：`feat: 异步任务系统 - 多任务并行处理支持`
5. 点击 **"Commit changes"**

---

## ✅ 验证上传

上传成功后，访问：
https://github.com/AI-Scarlett/lingxi-ai

检查以下内容：
- ✅ 最新提交是 "docs: 添加 GitHub 推送指南和自动化脚本"
- ✅ 文件列表包含所有新增文件
- ✅ 文档完整可读

---

## 🐛 故障排查

### 问题 1：Token 无效

**解决：**
- 确认 Token 权限包含 `repo`
- 重新生成 Token
- 确认 Token 没有过期

### 问题 2：SSH 密钥验证失败

**解决：**
```bash
# 测试 SSH 连接
ssh -T git@github.com

# 添加密钥到 ssh-agent
ssh-add ~/.ssh/id_ed25519
```

### 问题 3：权限不足

**解决：**
- 确认 GitHub 账号是仓库所有者或有写入权限
- 联系仓库管理员添加权限

### 问题 4：网络超时

**解决：**
- 使用代理服务器
- 尝试多次推送
- 使用 GitHub Desktop

---

## 📊 快速检查清单

```bash
# 1. 检查本地提交
cd ~/.openclaw/skills/lingxi
git log --oneline -3

# 2. 检查变更文件
git diff HEAD~2 --name-only

# 3. 检查远程地址
git remote -v

# 4. 推送
git push origin main
```

---

## 💋 推荐方案

**最推荐：方式 1（Git + Token）**
- ✅ 简单快速
- ✅ 不需要配置 SSH
- ✅ 适合一次性推送

**长期开发：方式 2（SSH）**
- ✅ 无需每次输入 Token
- ✅ 更安全
- ✅ 适合频繁推送

---

## 🎉 完成后的样子

推送成功后，仓库页面会显示：

```
📦 AI-Scarlett/lingxi-ai
✨ 心有灵犀，一点就通

Latest commit: a0847e5 docs: 添加 GitHub 推送指南和自动化脚本
2 hours ago

📁 Files:
  ├── scripts/
  │   ├── task_manager.py          ✅ 新增
  │   ├── async_executor.py        ✅ 新增
  │   ├── orchestrator_async.py    ✅ 新增
  │   ├── lingxi_qqbot.py          ✅ 新增
  │   └── ...
  ├── README_QQBOT.md              ✅ 新增
  ├── QQBOT_INTEGRATION.md         ✅ 新增
  └── ...
```

---

## 💡 需要帮助？

如果遇到问题，告诉我具体错误信息，我会帮你解决！💋

---

**灵犀团队** | 心有灵犀，一点就通 ✨
