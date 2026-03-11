# 灵犀 Dashboard 公网部署指南

**目标:** 让 Dashboard 可以从外网访问  
**公网 IP:** 106.52.101.202  
**端口:** 8765

---

## 🔍 当前状态

- ✅ Dashboard 服务运行中（监听 0.0.0.0:8765）
- ✅ 本地访问正常：http://localhost:8765
- ❌ 外网访问失败（防火墙/安全组阻挡）

---

## 🚀 解决方案

### 方案一：云服务器安全组配置（推荐）

如果你使用的是**腾讯云/阿里云/华为云**等云服务器：

#### 1. 登录云控制台

- **腾讯云:** https://console.cloud.tencent.com/cvm/security
- **阿里云:** https://ecs.console.aliyun.com/
- **华为云:** https://console.huaweicloud.com/ecs/

#### 2. 添加入站规则

| 配置项 | 值 |
|--------|-----|
| 协议 | TCP |
| 端口 | 8765 |
| 源 IP | 0.0.0.0/0（允许所有）或 你的 IP |
| 策略 | 允许 |

#### 3. 测试访问

```bash
# 从外网测试
curl http://106.52.101.202:8765/api/health
```

访问地址：
```
http://106.52.101.202:8765/?token=iOtZIA7A8DX7CJoQ50jMXEqVjZXlAVBo8THgJ1fZ-iY
```

---

### 方案二：Nginx 反向代理（生产环境推荐）

如果需要域名访问 + HTTPS：

#### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nginx -y

# CentOS/OpenCloudOS
sudo yum install nginx -y
```

#### 2. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/lingxi-dashboard
```

```nginx
server {
    listen 80;
    server_name dashboard.yourdomain.com;  # 你的域名
    
    location / {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_read_timeout 86400;
    }
}
```

#### 3. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/lingxi-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. 配置 HTTPS（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d dashboard.yourdomain.com
```

---

### 方案三：Cloudflare Tunnel（最简单，无需公网 IP）

如果云服务器没有公网 IP 或不想开放端口：

#### 1. 安装 cloudflared

```bash
# Linux
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

#### 2. 创建 Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create lingxi-dashboard
```

#### 3. 配置 config.yml

```yaml
tunnel: lingxi-dashboard
credentials-file: /root/.cloudflared/lingxi-dashboard.json

ingress:
  - hostname: dashboard.yourdomain.com
    service: http://localhost:8765
  - service: http_status:404
```

#### 4. 运行 Tunnel

```bash
cloudflared tunnel run lingxi-dashboard
```

---

## 🔐 安全建议

### 1. 使用强 Token

当前 Token 已自动生成，如需重置：

```bash
rm /root/.openclaw/workspace/.lingxi/dashboard_token.txt
# 重启 Dashboard 服务
pkill -f "python3 server.py"
cd /root/.openclaw/skills/lingxi/dashboard && python3 server.py &
```

### 2. 限制访问 IP

如果只允许特定 IP 访问，在云控制台安全组设置：
- 源 IP: `你的办公 IP/32`

### 3. 启用 HTTPS

生产环境**必须**启用 HTTPS，防止 Token 被窃听。

### 4. 使用域名访问

配置域名 + HTTPS，避免直接暴露 IP。

---

## 📊 快速测试脚本

```bash
#!/bin/bash
# test_public_access.sh

TOKEN=$(cat /root/.openclaw/workspace/.lingxi/dashboard_token.txt)
PUBLIC_IP="106.52.101.202"

echo "📊 测试 Dashboard 公网访问"
echo "================================"

# 本地测试
echo -n "1. 本地访问... "
if curl -s "http://localhost:8765/api/health" > /dev/null; then
    echo "✅ 成功"
else
    echo "❌ 失败"
fi

# 公网 IP 测试
echo -n "2. 公网 IP 访问... "
if curl -s --connect-timeout 3 "http://${PUBLIC_IP}:8765/api/health" > /dev/null; then
    echo "✅ 成功"
else
    echo "❌ 失败（检查安全组/防火墙）"
fi

# 显示访问地址
echo ""
echo "📱 访问地址:"
echo "  本地：http://localhost:8765/?token=${TOKEN}"
echo "  公网：http://${PUBLIC_IP}:8765/?token=${TOKEN}"
```

---

## 🎯 推荐方案

**立即可用:** 方案一（配置云安全组）  
**生产环境:** 方案二（Nginx + HTTPS）  
**无公网 IP:** 方案三（Cloudflare Tunnel）

---

## 📞 需要帮助？

检查步骤：

1. ✅ Dashboard 服务运行：`ps aux | grep server.py`
2. ✅ 端口监听：`netstat -tlnp | grep 8765`
3. ✅ 本地访问：`curl http://localhost:8765/api/health`
4. ❌ 外网访问：检查云安全组
5. ❌ 域名访问：配置 Nginx + HTTPS

---

**作者:** 丝嘉丽 Scarlett  
**日期:** 2026-03-10  
**版本:** v1.0
