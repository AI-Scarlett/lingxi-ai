#!/bin/bash
# 灵犀数据看板启动脚本
# Lingxi Dashboard Launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$SCRIPT_DIR/dashboard"

echo "=========================================="
echo "🚀 灵犀数据看板"
echo "=========================================="
echo ""

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  安装依赖..."
    pip3 install -q -r "$DASHBOARD_DIR/requirements.txt"
fi

echo "✅ 依赖检查完成"
echo ""

# 启动服务
echo "🌐 启动服务器..."
echo ""

cd "$DASHBOARD_DIR"
python3 server.py
