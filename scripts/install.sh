#!/bin/bash

# 🦞 灵犀 v3.3.3 一键安装脚本
# 专为养龙虾新手小白设计！

set -e

echo "🦞 ======================================="
echo "🦞 灵犀 v3.3.3 - 养龙虾的最佳助手"
echo "🦞 ======================================="
echo ""
echo "✨ 专为新手小白设计，一键安装启动！"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo "📦 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python3${NC}"
    echo "请先安装 Python 3.8+"
    exit 1
fi
echo -e "${GREEN}✅ Python3 已安装：$(python3 --version)${NC}"

# 检查 pip
echo "📦 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 pip3${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 已安装${NC}"

# 创建安装目录
INSTALL_DIR="$HOME/.lingxi"
echo "📁 创建安装目录：$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# 克隆仓库（如果不存在）
if [ ! -d "$INSTALL_DIR/lingxi-ai" ]; then
    echo "📥 克隆仓库..."
    git clone https://github.com/AI-Scarlett/lingxi-ai.git "$INSTALL_DIR/lingxi-ai"
else
    echo "📥 更新仓库..."
    cd "$INSTALL_DIR/lingxi-ai" && git pull
fi

cd "$INSTALL_DIR/lingxi-ai"

# 创建虚拟环境
echo "📦 创建 Python 虚拟环境..."
if [ ! -d "$INSTALL_DIR/lingxi-ai/venv" ]; then
    python3 -m venv "$INSTALL_DIR/lingxi-ai/venv"
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
source "$INSTALL_DIR/lingxi-ai/venv/bin/activate"
echo -e "${GREEN}✅ 虚拟环境已激活${NC}"

# 安装依赖
echo "📦 安装依赖（虚拟环境中）..."
pip install -r requirements.txt -q
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo "⚙️  创建环境变量配置..."
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}⚠️  请编辑 .env 文件，填写你的 API 密钥：${NC}"
    echo "   nano .env"
    echo ""
    echo "必须配置："
    echo "  - DASHSCOPE_API_KEY（图像生成）"
    echo "  - QWEN_API_KEY（LLM 调用）"
    echo ""
    read -p "按回车键继续..."
fi

# 启动 Dashboard
echo ""
echo "🚀 启动 Dashboard..."
python3 dashboard/server.py &
DASHBOARD_PID=$!

# 等待启动
sleep 3

# 生成访问令牌
TOKEN_FILE="$HOME/.openclaw/workspace/.lingxi/dashboard_token.txt"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE" | head -1)
else
    TOKEN="demo_token_$(date +%s)"
    mkdir -p "$(dirname "$TOKEN_FILE")"
    echo "$TOKEN" > "$TOKEN_FILE"
fi

# 获取本机 IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🦞 ======================================="
echo "🦞 ✅ 安装完成！"
echo "🦞 ======================================="
echo ""
echo "📊 Dashboard 访问方式："
echo ""
echo "   本地访问："
echo "   http://localhost:8765/?token=$TOKEN"
echo ""
echo "   局域网访问："
echo "   http://$LOCAL_IP:8765/?token=$TOKEN"
echo ""
echo "📱 手机扫码访问（推荐）："
echo "   使用微信扫描下方二维码"
echo ""
echo "   [二维码生成中...]"
echo ""

# 生成二维码（如果 qrcode 可用）
if command -v qrencode &> /dev/null; then
    echo "http://$LOCAL_IP:8765/?token=$TOKEN" | qrencode -t ANSIUTF8
fi

echo ""
echo "💡 提示："
echo "   - 按 Ctrl+C 停止 Dashboard"
echo "   - 访问地址已保存到：$TOKEN_FILE"
echo "   - 配置文档：$INSTALL_DIR/lingxi-ai/docs/"
echo ""
echo "🦞 祝你养龙虾愉快！✨"
echo ""

# 保持运行
wait $DASHBOARD_PID
