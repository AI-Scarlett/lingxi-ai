#!/bin/bash
# 灵犀数据看板 - 外网访问配置
# Expose Dashboard to Internet

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "🌐 灵犀看板 - 外网访问配置"
echo "=========================================="
echo ""

# 选择隧道工具
echo "请选择隧道工具:"
echo "1. ngrok (需要账号)"
echo "2. Cloudflare Tunnel (推荐，免费)"
echo "3. localtunnel (简单，临时使用)"
echo ""
read -p "请选择 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📦 使用 ngrok..."
        if ! command -v ngrok &> /dev/null; then
            echo "⚠️  ngrok 未安装，请先安装："
            echo "   brew install ngrok (macOS)"
            echo "   或访问 https://ngrok.com/download"
            exit 1
        fi
        
        echo "🔗 启动 ngrok 隧道..."
        ngrok http 8765
        ;;
    
    2)
        echo ""
        echo "📦 使用 Cloudflare Tunnel..."
        
        if ! command -v cloudflared &> /dev/null; then
            echo "⚠️  cloudflared 未安装，正在安装..."
            
            # 根据系统安装
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
                sudo dpkg -i cloudflared.deb
                rm cloudflared.deb
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                brew install cloudflared
            fi
        fi
        
        echo ""
        echo "🔗 启动 Cloudflare Tunnel..."
        echo "⚠️  首次使用需要登录 Cloudflare 账号"
        echo ""
        cloudflared tunnel --url http://localhost:8765
        ;;
    
    3)
        echo ""
        echo "📦 使用 localtunnel..."
        
        if ! command -v lt &> /dev/null; then
            echo "⚠️  安装 localtunnel..."
            npm install -g localtunnel
        fi
        
        echo "🔗 启动 localtunnel..."
        lt --port 8765
        ;;
    
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
