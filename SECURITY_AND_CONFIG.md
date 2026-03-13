# 🔐 灵犀 (Lingxi) 配置与安全声明

> **版本：** v3.3.6  
> **最后更新：** 2026-03-13  
> **安全级别：** ⚠️ 需要外部凭证

---

## 📋 配置声明

### ✅ 无需凭证即可运行的功能

以下功能**不需要**任何 API 密钥或外部凭证：

- ✅ 本地 SQLite 数据库操作
- ✅ Dashboard 本地访问（http://localhost:8765）
- ✅ 记忆管理（MindCore）
- ✅ Layer0 规则管理
- ✅ 技能管理
- ✅ 任务记录（本地数据库）

### ⚠️ 需要外部凭证的功能

以下功能**需要**配置相应的 API 密钥或服务凭证：

| 功能 | 凭证类型 | 必需性 | 存储位置 | 风险等级 |
|------|---------|--------|---------|---------|
| **OpenClaw 集成** | OpenClaw Gateway | 必需 | `~/.openclaw/openclaw.json` | 🟡 中 |
| **飞书机器人** | 飞书 AppID/AppSecret | 可选 | 飞书后台配置 | 🟡 中 |
| **企业微信机器人** | 企业微信 Webhook | 可选 | 企业微信后台 | 🟡 中 |
| **QQ 机器人** | QQ Bot Token | 可选 | QQ 开放平台 | 🟡 中 |
| **GitHub 推送** | GitHub Personal Access Token | 可选 | `~/.github_token` | 🔴 高 |
| **Dashboard 公开访问** | Dashboard Token | 可选 | `~/.openclaw/workspace/.lingxi/dashboard_token.txt` | 🟢 低 |
| **大模型调用** | 阿里云百炼 API Key | 可选 | 环境变量 | 🔴 高 |

---

## 🔑 凭证管理最佳实践

### 1. 环境变量（推荐）

```bash
# ~/.bashrc 或 ~/.profile
export LINGXI_DASHBOARD_TOKEN="your_dashboard_token"
export LINGXI_GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export ALIYUN_DASHSCOPE_API_KEY="sk-xxxxxxxxxxxx"
```

**优点：**
- ✅ 不写入代码或配置文件
- ✅ 进程隔离，更安全
- ✅ 易于轮换和管理

---

### 2. 文件存储（次选）

```bash
# Dashboard Token
echo "your_dashboard_token" > ~/.openclaw/workspace/.lingxi/dashboard_token.txt
chmod 600 ~/.openclaw/workspace/.lingxi/dashboard_token.txt

# GitHub Token
echo "ghp_xxxxxxxxxxxx" > ~/.github_token
chmod 600 ~/.github_token
```

**权限要求：**
```bash
# 所有凭证文件必须设置为 600（仅所有者可读写）
chmod 600 ~/.openclaw/workspace/.lingxi/dashboard_token.txt
chmod 600 ~/.github_token
chmod 600 ~/.openclaw/openclaw.json
```

---

### 3. 凭证检查脚本

灵犀启动时会自动检查必要的凭证：

```bash
#!/bin/bash
# /root/lingxi-ai-latest/scripts/check_credentials.sh

echo "🔐 灵犀凭证检查"
echo "================"

# Dashboard Token
if [ -f ~/.openclaw/workspace/.lingxi/dashboard_token.txt ]; then
    echo "✅ Dashboard Token: 已配置"
else
    echo "⚠️ Dashboard Token: 未配置（可选）"
fi

# GitHub Token
if [ -f ~/.github_token ]; then
    echo "✅ GitHub Token: 已配置"
else
    echo "⚠️ GitHub Token: 未配置（可选）"
fi

# OpenClaw 配置
if [ -f ~/.openclaw/openclaw.json ]; then
    echo "✅ OpenClaw 配置：已找到"
else
    echo "❌ OpenClaw 配置：未找到（必需）"
fi

# 文件权限检查
for file in ~/.github_token ~/.openclaw/workspace/.lingxi/dashboard_token.txt; do
    if [ -f "$file" ]; then
        perms=$(stat -c %a "$file")
        if [ "$perms" != "600" ]; then
            echo "⚠️ 警告：$file 权限为 $perms，建议设置为 600"
        fi
    fi
done
```

---

## 📂 文件读写声明

### 灵犀会读写的文件

| 路径 | 操作类型 | 用途 | 是否必需 |
|------|---------|------|---------|
| `~/.openclaw/workspace/.lingxi/dashboard_token.txt` | 读 | Dashboard API 认证 | 否 |
| `~/.openclaw/workspace/.lingxi/dashboard_v3.db` | 读写 | 任务/技能数据持久化 | 是 |
| `~/.openclaw/workspace/.lingxi/layer0_rules.json` | 读写 | Layer0 规则配置 | 是 |
| `~/.openclaw/workspace/.lingxi/memories.jsonl` | 读写 | 记忆数据 | 是 |
| `~/.openclaw/workspace/memory/items/memories.jsonl` | 读写 | OpenClaw 记忆同步 | 否 |
| `~/.github_token` | 读 | GitHub 推送认证 | 否 |
| `/root/lingxi-ai-latest/data/dashboard_v3.db` | 读写 | Dashboard 主数据库 | 是 |
| `/tmp/lingxi-ai-latest/logs/*.log` | 写 | 日志文件 | 否 |
| `/tmp/dashboard.log` | 写 | Dashboard 运行日志 | 否 |

### 权限要求

```bash
# 灵犀需要以下目录的写权限
chmod 755 /root/lingxi-ai-latest
chmod 755 /root/lingxi-ai-latest/data
chmod 755 ~/.openclaw/workspace/.lingxi
chmod 755 /tmp/lingxi-ai-latest/logs
```

---

## 🚨 安全风险提示

### 高风险操作

以下操作**可能泄露敏感信息**，请谨慎使用：

1. **GitHub 推送**
   - 风险：Token 可能被记录在 Git 历史中
   - 缓解：使用 SSH Key 而非 Token
   - 命令：`git push origin main`

2. **Dashboard 公开访问**
   - 风险：Token 可能被中间人截获
   - 缓解：使用 HTTPS + 防火墙限制 IP
   - 命令：`python3 server.py --host 0.0.0.0`

3. **日志文件**
   - 风险：可能包含用户输入和 API 响应
   - 缓解：定期清理日志，设置日志轮转
   - 位置：`/tmp/lingxi-ai-latest/logs/`

---

## ✅ 安全配置检查清单

在部署灵犀前，请确认以下事项：

### 基础配置
- [ ] Dashboard Token 已生成并存储
- [ ] Dashboard Token 文件权限为 600
- [ ] OpenClaw 配置文件存在且有效
- [ ] 数据库目录有写权限

### 可选配置（按需）
- [ ] GitHub Token（如需推送代码）
- [ ] 飞书/钉钉/企业微信配置（如需多渠道）
- [ ] 阿里云百炼 API Key（如需大模型调用）

### 安全措施
- [ ] 所有凭证文件权限设置为 600
- [ ] 防火墙仅开放必要端口（8765）
- [ ] 日志定期清理（建议 7 天）
- [ ] 数据库定期备份（建议每天）
- [ ] 不将凭证提交到 Git 仓库

---

## 🔍 透明度承诺

灵犀承诺：

1. **明确声明**所有外部依赖和凭证需求
2. **不隐藏**任何网络请求或数据外发
3. **不收集**用户隐私数据
4. **不上传**任何凭证到第三方（除明确配置的服务）
5. **提供**完整的凭证管理和轮换指南

---

## 📞 问题反馈

如发现任何未声明的凭证使用或安全风险，请报告：

- **GitHub Issues:** https://github.com/AI-Scarlett/lingxi-ai/issues
- **邮箱：** security@lingxi.ai（如有）

---

*安全透明，值得信赖* 🦞✨
