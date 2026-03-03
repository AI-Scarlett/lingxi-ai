#!/bin/bash
# 创建上传包 - 用于手动上传到 GitHub

set -e

REPO_DIR="$HOME/.openclaw/skills/lingxi"
UPLOAD_DIR="/tmp/lingxi-upload-$(date +%Y%m%d-%H%M%S)"

echo "📦 创建 GitHub 上传包..."
echo ""

# 创建临时目录
mkdir -p "$UPLOAD_DIR"

# 复制需要上传的文件
echo "📋 复制文件..."

# 核心模块
cp "$REPO_DIR/scripts/task_manager.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/async_executor.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/orchestrator_async.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/lingxi_qqbot.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/qqbot_bridge.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/qqbot-bridge.sh" "$UPLOAD_DIR/"

# 测试和工具
cp "$REPO_DIR/scripts/test_async_system.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/demo.py" "$UPLOAD_DIR/"
cp "$REPO_DIR/scripts/push-to-github.sh" "$UPLOAD_DIR/"

# 文档
cp "$REPO_DIR/README_QQBOT.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/QQBOT_INTEGRATION.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/ASYNC_GUIDE.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/IMPLEMENTATION_SUMMARY.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/INTEGRATION_COMPLETE.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/FINAL_SUMMARY.md" "$UPLOAD_DIR/"
cp "$REPO_DIR/UPLOAD_TO_GITHUB.md" "$UPLOAD_DIR/"

# 微信工具
mkdir -p "$UPLOAD_DIR/tools/publishers/wechat"
cp "$REPO_DIR/tools/publishers/wechat/wechat_*.py" "$UPLOAD_DIR/tools/publishers/wechat/"

# .gitignore
cp "$REPO_DIR/.gitignore" "$UPLOAD_DIR/"

# 修改 orchestrator.py (如果有修改)
if [ -f "$REPO_DIR/scripts/orchestrator.py" ]; then
    cp "$REPO_DIR/scripts/orchestrator.py" "$UPLOAD_DIR/scripts/" 2>/dev/null || mkdir -p "$UPLOAD_DIR/scripts" && cp "$REPO_DIR/scripts/orchestrator.py" "$UPLOAD_DIR/scripts/"
fi

echo "✅ 已复制 $(find "$UPLOAD_DIR" -type f | wc -l) 个文件"
echo ""

# 创建压缩包
PACKAGE="$UPLOAD_DIR.tar.gz"
cd /tmp && tar -czf "$PACKAGE" "lingxi-upload-$(date +%Y%m%d-%H%M%S)"

echo "📦 上传包已创建："
echo "   $PACKAGE"
echo ""
echo "💡 上传步骤："
echo "   1. 访问 https://github.com/AI-Scarlett/lingxi-ai"
echo "   2. 点击 'Add file' → 'Upload files'"
echo "   3. 解压上传包，拖拽所有文件上传"
echo "   4. 提交信息：feat: 异步任务系统 - 多任务并行处理支持"
echo ""
echo "📋 或者使用 Git 推送（推荐）："
echo "   cd $REPO_DIR"
echo "   git push origin main"
