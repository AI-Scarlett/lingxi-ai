#!/bin/bash

# 🦞 灵犀 Dashboard systemd 守护进程配置脚本

set -e

INSTALL_DIR="$HOME/.lingxi/lingxi-ai"
SERVICE_FILE="/etc/systemd/system/lingxi-dashboard.service"

echo "🦞 ======================================="
echo "🦞 灵犀 Dashboard systemd 配置"
echo "🦞 ======================================="
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    echo "   sudo bash $0"
    exit 1
fi

# 创建 systemd 服务文件
echo "📝 创建 systemd 服务文件..."

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=灵犀 Dashboard
After=network.target

[Service]
Type=simple
User=$SUDO_USER
Group=$SUDO_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/dashboard/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lingxi-dashboard

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ 服务文件已创建：$SERVICE_FILE${NC}"

# 重新加载 systemd
echo "🔄 重新加载 systemd 配置..."
systemctl daemon-reload

# 启用服务
echo "⚙️  启用服务..."
systemctl enable lingxi-dashboard

# 启动服务
echo "🚀 启动服务..."
systemctl start lingxi-dashboard

# 显示状态
echo ""
echo "📊 服务状态："
systemctl status lingxi-dashboard --no-pager

echo ""
echo "💡 常用命令："
echo "   systemctl status lingxi-dashboard   # 查看状态"
echo "   systemctl stop lingxi-dashboard     # 停止服务"
echo "   systemctl restart lingxi-dashboard  # 重启服务"
echo "   journalctl -u lingxi-dashboard -f   # 查看日志"
echo ""
echo "✅ 配置完成！Dashboard 已作为守护进程运行"
