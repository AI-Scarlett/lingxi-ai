#!/bin/bash
# 自动推送脚本 - 循环尝试直到成功

REPO_DIR="$HOME/.openclaw/skills/lingxi"
MAX_ATTEMPTS=100
DELAY=30  # 每次尝试间隔 30 秒

cd "$REPO_DIR"

echo "🚀 启动自动推送任务..."
echo "   最大尝试次数：$MAX_ATTEMPTS"
echo "   间隔时间：${DELAY}秒"
echo ""

for i in $(seq 1 $MAX_ATTEMPTS); do
    echo "[$i/$MAX_ATTEMPTS] 尝试推送..."
    
    # 尝试使用 gitclone 代理
    git remote set-url origin https://gitclone.com/github.com/AI-Scarlett/lingxi-ai.git
    if timeout 120 git push origin main 2>&1; then
        echo "✅ 推送成功！"
        exit 0
    fi
    
    # 尝试直接推送到 GitHub
    git remote set-url origin https://github.com/AI-Scarlett/lingxi-ai.git
    if timeout 120 git push origin main 2>&1; then
        echo "✅ 推送成功！"
        exit 0
    fi
    
    echo "❌ 失败，${DELAY}秒后重试..."
    sleep $DELAY
done

echo "❌ 达到最大尝试次数，推送失败"
exit 1
