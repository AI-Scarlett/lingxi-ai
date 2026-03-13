# 📤 灵犀代码推送指南

## 问题说明

当前环境无法直接推送到 GitHub/Gitee（需要交互式认证）

## 解决方案

### 方案 1：使用 Git Credential Store（推荐）

```bash
cd /root/lingxi-ai-latest

# 1. 配置 credential helper
git config --global credential.helper store

# 2. 手动推送一次（会提示输入用户名密码）
git push origin main

# 3. 之后推送无需密码
./scripts/git-push-helper.sh push
```

### 方案 2：使用 SSH 密钥

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "scarlett@ai-love.world"

# 2. 添加公钥到 GitHub/Gitee
cat ~/.ssh/id_ed25519.pub

# 3. 测试连接
ssh -T git@github.com
ssh -T git@gitee.com

# 4. 修改远程仓库为 SSH
git remote set-url origin git@github.com:AI-Scarlett/lingxi-ai.git
git remote set-url gitee git@gitee.com:AI-Scarlett/lingxi-ai.git

# 5. 推送
./scripts/git-push-helper.sh push
```

### 方案 3：使用 Personal Access Token

**GitHub:**
1. 访问 https://github.com/settings/tokens
2. 创建新 Token（勾选 repo 权限）
3. 推送时使用：
```bash
git push https://<TOKEN>@github.com/AI-Scarlett/lingxi-ai.git main
```

**Gitee:**
1. 访问 https://gitee.com/profile/personal_access_tokens
2. 创建新 Token
3. 推送时使用：
```bash
git push https://<TOKEN>@gitee.com/AI-Scarlett/lingxi-ai.git main
```

---

## 自动推送脚本

使用优化后的推送脚本（带重试和镜像源）：

```bash
cd /root/lingxi-ai-latest

# 推送代码
./scripts/git-push-helper.sh push

# 查看状态
./scripts/git-push-helper.sh status

# 同步所有远程
./scripts/git-push-helper.sh sync
```

---

## 当前提交状态

本地已有以下优化提交：

- ✅ systemd 守护进程配置
- ✅ requirements.txt
- ✅ 配置管理中心
- ✅ 健康检查脚本
- ✅ 自动重启脚本
- ✅ Git 推送辅助脚本
- ✅ 增强日志系统
- ✅ 单元测试框架

**提交哈希：** `04c1c71`

---

## 手动推送命令

```bash
cd /root/lingxi-ai-latest
git push origin main
```

或使用 Gitee 镜像：
```bash
git push gitee main
```

---

**创建时间：** 2026-03-13 00:11  
**版本：** v3.3.6
