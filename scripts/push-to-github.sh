#!/bin/bash
# 灵犀异步任务系统 - GitHub 推送脚本
# 自动尝试多种推送方式

set -e

REPO_DIR="$HOME/.openclaw/skills/lingxi"
cd "$REPO_DIR"

echo "🚀 开始推送到 GitHub..."
echo ""

# 方式 1: 尝试 gitclone 代理
echo "📦 方式 1: 使用 gitclone 代理..."
if git push origin main 2>&1; then
    echo "✅ 推送成功！"
    exit 0
fi

echo "❌ 代理推送失败，尝试其他方式..."
echo ""

# 方式 2: 尝试 SSH
echo "📦 方式 2: 使用 SSH..."
git remote set-url origin git@github.com:AI-Scarlett/lingxi-ai.git 2>/dev/null || true

if ssh-add -l >/dev/null 2>&1 || ssh-add ~/.ssh/id_ed25519 2>/dev/null; then
    if git push origin main 2>&1; then
        echo "✅ SSH 推送成功！"
        exit 0
    fi
fi

echo "❌ SSH 推送失败"
echo ""

# 恢复远程地址
git remote set-url origin https://gitclone.com/github.com/AI-Scarlett/lingxi-ai.git 2>/dev/null || true

# 显示手动推送指南
echo "⚠️  自动推送失败，请手动执行以下命令之一："
echo ""
echo "方式 1 - SSH 推送（推荐）："
echo "  cd $REPO_DIR"
echo "  git remote set-url origin git@github.com:AI-Scarlett/lingxi-ai.git"
echo "  git push origin main"
echo ""
echo "方式 2 - Personal Access Token："
echo "  cd $REPO_DIR"
echo "  git remote set-url origin https://<YOUR_TOKEN>@github.com/AI-Scarlett/lingxi-ai.git"
echo "  git push origin main"
echo ""
echo "📋 提交信息："
git log --oneline -1
echo ""
echo "💡 推送成功后访问：https://github.com/AI-Scarlett/lingxi-ai"
