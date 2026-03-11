# 🌐 灵犀 Dashboard 外网访问指南

**适用版本：** v3.3.3+  
**目标：** 让所有用户都能方便地外网访问 Dashboard

**特点：**
- ✅ 无需域名
- ✅ 无需备案
- ✅ 纯 IP+token
- ✅ 零配置

---

## 🎯 问题场景

**问题：** 灵犀 Dashboard 默认只在本地运行（localhost:8765），用户在外无法访问。

**解决方案：** 提供 2 种访问方案。

---

## 🚀 快速开始（小白专用）

**最简单的方式：**

```bash
cd /root/.openclaw/skills/lingxi/dashboard
python3 start_dashboard.py
```

**自动显示：**
- ✅ 内网访问地址（IP+ 端口）
- ✅ 外网访问地址（公网 IP+token）
- ✅ 移动端访问地址
- ✅ 二维码

**零配置！有手就会！**

---

## 📋 访问方案

### 方案一：内网访问（推荐 ⭐⭐⭐⭐⭐）

**适用场景：** 
- ✅ 手机和电脑在同一 WiFi
- ✅ 零配置
- ✅ 最快速度

**配置方式：**
```bash
python3 start_dashboard.py
# 自动显示内网地址
```

**优点：**
- ✅ 零配置
- ✅ 速度快
- ✅ 免费使用

**缺点：**
- ❌ 只能在同一 WiFi 使用

---

### 方案二：外网访问（推荐 ⭐⭐⭐⭐⭐）

**适用场景：** 
- ✅ 任何地方（4G/5G/ 其他 WiFi）
- ✅ 无需域名
- ✅ 无需备案

**配置方式：**
```bash
# 1. 配置路由器端口映射（5 分钟）
# 查看教程：NAT_PORT_FORWARDING.md

# 2. 启动 Dashboard
python3 start_dashboard.py

# 3. 访问显示的公网 IP 地址
http://公网 IP:8766/mobile?token=xxx
```

**优点：**
- ✅ 任何地方都能访问
- ✅ 无需域名
- ✅ 无需备案
- ✅ Token 认证，安全
- ✅ 免费使用

**缺点：**
- ❌ 需要配置端口映射（5 分钟）
- ❌ 需要公网 IP（可联系运营商获取）

---

### 方案二：自有域名 + 反向代理（推荐 ⭐⭐⭐⭐）

**适用场景：**
- ✅ 有自有域名
- ✅ 长期稳定使用
- ✅ 需要完全控制

**配置方式：**

**1. DNS 配置**
```bash
# 添加 A 记录
lingxi.your-domain.com → 你的服务器 IP
```

**2. Nginx 配置**
```nginx
server {
    listen 80;
    server_name lingxi.your-domain.com;
    
    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**3. HTTPS 配置（Let's Encrypt）**
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx -y

# 获取证书
certbot --nginx -d lingxi.your-domain.com
```

**4. 启动远程访问**
```bash
cd /root/.openclaw/skills/lingxi/dashboard
python3 remote_access.py --host lingxi.your-domain.com
```

**优点：**
- ✅ 完全控制
- ✅ 自定义域名
- ✅ 稳定可靠

**缺点：**
- ❌ 需要自有域名
- ❌ 需要配置 Nginx

---

### 方案三：内网穿透工具（推荐 ⭐⭐⭐）

**适用场景：**
- ✅ 无公网 IP
- ✅ 临时使用
- ✅ 开发测试

#### 3.1 Cloudflare Tunnel（免费）

**步骤：**

**1. 安装 cloudflared**
```bash
# Ubuntu/Debian
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# macOS
brew install cloudflared
```

**2. 登录 Cloudflare**
```bash
cloudflared tunnel login
```

**3. 创建 Tunnel**
```bash
cloudflared tunnel create lingxi
```

**4. 配置 Tunnel**
```yaml
# ~/.cloudflared/lingxi.yml
tunnel: lingxi
credentials-file: /root/.cloudflared/lingxi.json

ingress:
  - hostname: lingxi.your-domain.com
    service: http://localhost:8765
  - service: http_status:404
```

**5. 运行 Tunnel**
```bash
cloudflared tunnel run lingxi
```

**6. 配置 DNS（Cloudflare Dashboard）**
```
Type: CNAME
Name: lingxi
Target: <tunnel-id>.cfargotunnel.com
```

**优点：**
- ✅ 免费
- ✅ 无需公网 IP
- ✅ 自动 HTTPS

**缺点：**
- ❌ 需要 Cloudflare 账号
- ❌ 配置稍复杂

---

#### 3.2 ngrok（免费/付费）

**步骤：**

**1. 安装 ngrok**
```bash
# 下载
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**2. 配置认证**
```bash
ngrok config add-authtoken <your-token>
```

**3. 启动**
```bash
ngrok http 8765 --subdomain=lingxi
```

**优点：**
- ✅ 简单快速
- ✅ 无需域名

**缺点：**
- ❌ 免费版随机域名
- ❌ 付费版较贵

---

#### 3.3 frp（自建）

**步骤：**

**1. 准备公网服务器**
- 需要一台有公网 IP 的服务器
- 安装 frps（frp server）

**2. 配置 frps（服务器端）**
```ini
# frps.ini
[common]
bind_port = 7000
token = your_secret_token
```

**3. 配置 frpc（客户端）**
```ini
# frpc.ini
[common]
server_addr = <your-server-ip>
server_port = 7000
token = your_secret_token

[lingxi]
type = http
local_port = 8765
custom_domains = lingxi.your-domain.com
```

**4. 启动**
```bash
# 服务器端
./frps -c frps.ini

# 客户端
./frpc -c frpc.ini
```

**优点：**
- ✅ 完全自控
- ✅ 免费

**缺点：**
- ❌ 需要公网服务器
- ❌ 配置复杂

---

## 🚀 快速选择指南

| 需求 | 推荐方案 | 配置难度 | 成本 |
|------|----------|----------|------|
| **快速测试** | 官方域名 | ⭐ | 免费 |
| **长期使用** | 自有域名 + Nginx | ⭐⭐⭐ | 域名费 |
| **无公网 IP** | Cloudflare Tunnel | ⭐⭐ | 免费 |
| **临时使用** | ngrok | ⭐ | 免费/付费 |
| **完全自控** | frp 自建 | ⭐⭐⭐⭐ | 服务器费 |

---

## 📱 用户使用指南

### 普通用户（快速上手）

**步骤：**
1. 安装灵犀系统
2. 自动使用官方域名
3. 访问 https://lingxi.me-ai.help

**配置：** 零配置

---

### 高级用户（自有域名）

**步骤：**
1. 准备域名（如：your-domain.com）
2. 配置 DNS A 记录
3. 配置 Nginx 反向代理
4. 申请 HTTPS 证书
5. 启动远程访问

**配置：**
```bash
# 1. DNS 配置
lingxi.your-domain.com → 服务器 IP

# 2. Nginx 配置
server {
    listen 80;
    server_name lingxi.your-domain.com;
    location / { proxy_pass http://localhost:8765; }
}

# 3. HTTPS
certbot --nginx -d lingxi.your-domain.com

# 4. 启动
python3 remote_access.py --host lingxi.your-domain.com
```

---

### 企业用户（高可用）

**步骤：**
1. 负载均衡配置
2. 多实例部署
3. 数据库主从
4. 监控告警

**架构：**
```
                    ┌─────────────┐
                    │   Nginx LB  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
   │ Instance 1│   │ Instance 2│   │ Instance 3│
   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                   ┌─────▼─────┐
                   │   Redis   │
                   └───────────┘
```

---

## 🔧 配置示例

### 完整 Nginx 配置

```nginx
server {
    listen 80;
    server_name lingxi.me-ai.help;
    
    # 强制 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lingxi.me-ai.help;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/lingxi.me-ai.help/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lingxi.me-ai.help/privkey.pem;
    
    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 代理到 Dashboard
    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 访问日志
    access_log /var/log/nginx/lingxi_access.log;
    error_log /var/log/nginx/lingxi_error.log;
}
```

---

## 📊 方案对比

| 方案 | 难度 | 成本 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| **官方域名** | ⭐ | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **自有域名** | ⭐⭐⭐ | 域名费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cloudflare** | ⭐⭐ | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **ngrok** | ⭐ | 免费/付费 | ⭐⭐⭐ | ⭐⭐⭐ |
| **frp 自建** | ⭐⭐⭐⭐ | 服务器费 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🙋 常见问题

### Q: 我没有域名怎么办？

**A:** 使用官方域名 `lingxi.me-ai.help`，零配置直接使用！

### Q: 官方域名收费吗？

**A:** 完全免费！老板提供给大家用的。

### Q: 可以自定义子域名吗？

**A:** 可以！使用自有域名方案，配置 Nginx 反向代理即可。

### Q: 多个用户会冲突吗？

**A:** 不会！每个用户独立部署，互不影响。

### Q: 安全性如何保障？

**A:** 
- ✅ Token 认证
- ✅ HTTPS 加密
- ✅ 访问控制
- ✅ IP 白名单（可选）

---

## 📞 技术支持

**问题反馈：** 飞书联系 Scarlett  
**文档：** `/root/.openclaw/skills/lingxi/dashboard/EXTERNAL_ACCESS.md`  
**Dashboard：** http://localhost:8765

---

**灵犀系统 v3.3.3 - 让外网访问如此简单！** 💋

**Scarlett**  
2026-03-11
