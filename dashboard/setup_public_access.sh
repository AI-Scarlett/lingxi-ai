#!/bin/bash
# 灵犀 Dashboard 公网访问一键配置脚本
# Lingxi Dashboard Public Access Setup Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
DASHBOARD_PORT=8765
PUBLIC_IP="106.52.101.202"
TOKEN_FILE="/root/.openclaw/workspace/.lingxi/dashboard_token.txt"

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   灵犀 Dashboard 公网访问配置脚本                  ║${NC}"
echo -e "${BLUE}║   Lingxi Dashboard Public Access Setup             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查 Dashboard 服务
echo -e "${YELLOW}[1/5] 检查 Dashboard 服务状态...${NC}"
if pgrep -f "python3.*server.py" > /dev/null; then
    echo -e "${GREEN}✅ Dashboard 服务运行中${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard 服务未运行，正在启动...${NC}"
    cd /root/.openclaw/skills/lingxi/dashboard
    nohup python3 server.py > /tmp/dashboard.log 2>&1 &
    sleep 3
    if pgrep -f "python3.*server.py" > /dev/null; then
        echo -e "${GREEN}✅ Dashboard 服务已启动${NC}"
    else
        echo -e "${RED}❌ Dashboard 服务启动失败${NC}"
        exit 1
    fi
fi

# 检查端口监听
echo -e "${YELLOW}[2/5] 检查端口监听状态...${NC}"
if netstat -tlnp 2>/dev/null | grep -q ":${DASHBOARD_PORT}" || ss -tlnp 2>/dev/null | grep -q ":${DASHBOARD_PORT}"; then
    echo -e "${GREEN}✅ 端口 ${DASHBOARD_PORT} 正在监听${NC}"
else
    echo -e "${RED}❌ 端口 ${DASHBOARD_PORT} 未监听${NC}"
    exit 1
fi

# 本地访问测试
echo -e "${YELLOW}[3/5] 测试本地访问...${NC}"
if curl -s "http://localhost:${DASHBOARD_PORT}/api/health" > /dev/null; then
    echo -e "${GREEN}✅ 本地访问正常${NC}"
else
    echo -e "${RED}❌ 本地访问失败${NC}"
    exit 1
fi

# 外网访问测试
echo -e "${YELLOW}[4/5] 测试外网访问...${NC}"
if curl -s --connect-timeout 3 "http://${PUBLIC_IP}:${DASHBOARD_PORT}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 外网访问正常${NC}"
    echo -e "${YELLOW}ℹ️  云服务器安全组已开放${NC}"
else
    echo -e "${YELLOW}⚠️  外网访问失败${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}需要配置云服务器安全组！${NC}"
    echo ""
    echo -e "${BLUE}请按以下步骤操作：${NC}"
    echo ""
    echo "1️⃣  登录云控制台"
    echo "   腾讯云：https://console.cloud.tencent.com/cvm/security"
    echo "   阿里云：https://ecs.console.aliyun.com/"
    echo ""
    echo "2️⃣  添加入站规则"
    echo "   - 协议：TCP"
    echo "   - 端口：${DASHBOARD_PORT}"
    echo "   - 源 IP: 0.0.0.0/0（或你的 IP）"
    echo "   - 策略：允许"
    echo ""
    echo "3️⃣  保存后再次运行此脚本"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

# 显示访问信息
echo -e "${YELLOW}[5/5] 访问信息${NC}"
echo ""
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    echo -e "${GREEN}🔑 Token:${NC} ${TOKEN}"
    echo ""
    echo -e "${GREEN}📱 访问地址:${NC}"
    echo "   本地访问：http://localhost:${DASHBOARD_PORT}/?token=${TOKEN}"
    echo "   公网访问：http://${PUBLIC_IP}:${DASHBOARD_PORT}/?token=${TOKEN}"
    echo ""
    echo -e "${YELLOW}⚠️  安全提示:${NC}"
    echo "   - 请妥善保管 Token，不要泄露给他人"
    echo "   - 生产环境建议使用 HTTPS"
    echo "   - 可配置 Nginx 反向代理 + 域名访问"
else
    echo -e "${RED}❌ Token 文件不存在${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 配置完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 生成访问卡片
echo ""
echo "┌──────────────────────────────────────────────┐"
echo "│  🚀 灵犀 Dashboard 已就绪                    │"
echo "├──────────────────────────────────────────────┤"
echo "│  📊 状态：运行中                             │"
echo "│  🌐 公网 IP: ${PUBLIC_IP}"
echo "│  🔌 端口：${DASHBOARD_PORT}"
echo "│  🔑 Token: ${TOKEN:0:20}..."
echo "│                                              │"
echo "│  访问：http://${PUBLIC_IP}:${DASHBOARD_PORT}/?token=${TOKEN}"
echo "└──────────────────────────────────────────────┘"

echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 如果外网无法访问，请检查云安全组配置"
echo "   - 查看详细说明：cat /root/.openclaw/skills/lingxi/dashboard/DEPLOY_PUBLIC.md"
echo ""
