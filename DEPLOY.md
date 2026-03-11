# 🦞 灵犀 v3.3.3 部署说明

## 📦 安装方式

### 方式 1：一键安装（推荐）

```bash
curl -Ls https://raw.githubusercontent.com/AI-Scarlett/lingxi-ai/main/scripts/install.sh | bash
```

**功能：**
- ✅ 自动检查 Python 环境
- ✅ 自动创建虚拟环境（venv）
- ✅ 自动克隆仓库
- ✅ 自动安装依赖
- ✅ 自动启动服务

### 方式 2：手动安装

```bash
# 克隆仓库
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## ⚙️ 配置

### 1. 环境变量配置

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

**必需配置：**
```bash
# 阿里云 DashScope API 密钥
DASHSCOPE_API_KEY=sk-your-actual-key-here

# 通义千问 API 密钥
QWEN_API_KEY=sk-your-actual-key-here
```

**可选配置：**
```bash
# 搜索 API
PERPLEXITY_API_KEY=your-key-here

# 远程访问
NGROK_AUTH_TOKEN=your-token-here
```

### 2. 获取 API 密钥

**阿里云 DashScope：**
1. 访问：https://dashscope.console.aliyun.com/apiKey
2. 登录/注册阿里云账号
3. 创建 API Key
4. 复制到 .env 文件

**⚠️ 重要：**
- API 密钥必须填写真实值
- 不要使用示例值（sk-your-xxx）
- 启动时会强制检查 API 密钥

---

## 🚀 启动方式

### 方式 1：快速启动（开发环境）

```bash
cd lingxi-ai
python3 scripts/quick_start.py
```

**特点：**
- ✅ 自动检查 API 密钥
- ✅ 前台运行，方便调试
- ❌ 不适合生产环境

### 方式 2：systemd 守护进程（生产环境）

```bash
# 配置 systemd 服务
sudo bash scripts/setup_systemd.sh

# 查看状态
systemctl status lingxi-dashboard

# 重启服务
sudo systemctl restart lingxi-dashboard

# 查看日志
journalctl -u lingxi-dashboard -f
```

**特点：**
- ✅ 后台守护进程
- ✅ 开机自启动
- ✅ 崩溃自动重启
- ✅ 日志集中管理

### 方式 3：手动启动

```bash
cd lingxi-ai
source venv/bin/activate
python3 dashboard/server.py
```

---

## 🔐 安全提示

### 1. API 密钥安全

- ✅ 使用环境变量存储
- ✅ .env 文件已加入 .gitignore
- ❌ 不要提交到 Git
- ❌ 不要分享给他人

### 2. Dashboard 访问

- ✅ Token 认证保护
- ✅ 7 天有效期
- ⚠️ 建议配置防火墙
- ⚠️ 定期更换 Token

### 3. 服务器安全

```bash
# 配置防火墙（仅允许必要端口）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8765/tcp  # Dashboard
sudo ufw enable

# 查看开放端口
sudo ufw status
```

---

## 📊 访问 Dashboard

### 本地访问
```
http://localhost:8765/?token=YOUR_TOKEN
```

### 外网访问
```
http://YOUR_SERVER_IP:8765/?token=YOUR_TOKEN
```

### 获取 Token
```bash
cat ~/.openclaw/workspace/.lingxi/dashboard_token.txt
```

---

## 🔧 常用命令

### 虚拟环境
```bash
# 激活虚拟环境
source venv/bin/activate

# 退出虚拟环境
deactivate
```

### systemd 服务
```bash
# 查看状态
systemctl status lingxi-dashboard

# 停止服务
sudo systemctl stop lingxi-dashboard

# 启动服务
sudo systemctl start lingxi-dashboard

# 重启服务
sudo systemctl restart lingxi-dashboard

# 查看日志
journalctl -u lingxi-dashboard -f
```

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip install -r requirements.txt --upgrade

# 导出依赖
pip freeze > requirements.txt
```

---

## ⚠️ 故障排查

### 问题 1：Dashboard 无法启动

**检查日志：**
```bash
journalctl -u lingxi-dashboard -f
```

**常见原因：**
- 端口被占用：`lsof -ti:8765 | xargs kill -9`
- API 密钥未配置：检查 .env 文件
- 虚拟环境未激活：`source venv/bin/activate`

### 问题 2：API 调用失败

**检查 API 密钥：**
```bash
cat .env | grep API_KEY
```

**确保：**
- 密钥格式正确（sk-开头）
- 密钥未过期
- 账户有足够额度

### 问题 3：Token 验证失败

**重置 Token：**
```bash
echo "new_token_$(date +%s)" > ~/.openclaw/workspace/.lingxi/dashboard_token.txt
```

**重启服务：**
```bash
sudo systemctl restart lingxi-dashboard
```

---

## 📞 技术支持

- **GitHub:** https://github.com/AI-Scarlett/lingxi-ai
- **Issues:** https://github.com/AI-Scarlett/lingxi-ai/issues
- **文档：** docs/ 目录

---

**灵犀 v3.3.3 - 养龙虾的最佳助手！** 🦞✨
