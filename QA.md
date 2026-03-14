# 灵犀 AI 助手 - 常见问题解答

> 收集用户常见问题和解决方案，帮助快速上手

## 📋 目录

1. [安装部署](#安装部署)
2. [Dashboard 访问](#dashboard 访问)
3. [Layer0 规则](#layer0 规则)
4. [任务管理](#任务管理)
5. [记忆系统](#记忆系统)
6. [安全配置](#安全配置)
7. [故障排查](#故障排查)

---

## 安装部署

### Q1: 如何安装灵犀 AI 助手？

**A**: 按照以下步骤安装：

```bash
# 1. 克隆项目
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
vim .env  # 填写 API 密钥

# 4. 启动 Dashboard
cd dashboard/v3
python3 server.py

# 5. 配置定时任务（可选）
crontab -e
# 添加 HEARTBEAT.md 中的定时任务
```

**参考文档**: [README.md](README.md)

---

### Q2: 如何配置 systemd 守护进程？

**A**: 创建 systemd 服务文件：

```bash
# 创建服务文件
sudo tee /etc/systemd/system/lingxi-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Lingxi Dashboard Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/lingxi-ai-latest/dashboard/v3
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable lingxi-dashboard
sudo systemctl start lingxi-dashboard
```

**验证状态**:
```bash
systemctl status lingxi-dashboard
journalctl -u lingxi-dashboard -f
```

---

## Dashboard 访问

### Q3: 如何访问 Dashboard？

**A**: 使用以下 URL 访问：

```
http://<服务器 IP>:8765/?token=<你的 token>
```

**示例**:
```
http://49.232.250.180:8765/?token=1e4c2a9af43cd7001d00ce08b1a16d1a3d32b9de7d0e08ae4b63082fe1ff7bf6
```

**获取 token**:
```bash
cat /root/.openclaw/workspace/.lingxi/dashboard_token.txt
```

---

### Q4: Dashboard 无法访问怎么办？

**A**: 按以下步骤排查：

1. **检查服务状态**:
   ```bash
   systemctl status lingxi-dashboard
   ```

2. **检查端口监听**:
   ```bash
   ss -tlnp | grep 8765
   ```

3. **检查防火墙**:
   ```bash
   ufw status
   ufw allow 8765
   ```

4. **重启服务**:
   ```bash
   systemctl restart lingxi-dashboard
   ```

5. **查看日志**:
   ```bash
   journalctl -u lingxi-dashboard -n 50
   ```

---

### Q5: Dashboard 加载很慢怎么办？

**A**: 已优化分页加载，每页显示 50 条数据：

- **任务列表**: 每页 50 条，支持分页
- **记忆列表**: 每页 50 条，支持分页
- **技能列表**: 全部显示（通常较少）

**优化建议**:
- 使用筛选功能快速定位
- 使用搜索功能精确查找
- 避免一次性加载全部数据

---

## Layer0 规则

### Q6: 如何配置 Layer0 规则？

**A**: 在 Dashboard 中配置：

1. 打开 Dashboard → Layer0 规则
2. 点击"新建规则"
3. 填写规则信息：
   - **模式**: 正则表达式（如 `^你好.*`）
   - **响应**: 匹配时的回复
   - **分类**: 规则分类
   - **优先级**: 1-10（数字越大优先级越高）
   - **渠道**: 可多选（飞书/钉钉/QQ/等）
   - **万能回复**: 勾选后任何消息立即响应
4. 保存

**示例规则**:
```
模式：^紧急.*
响应：收到，马上处理！
渠道：飞书 + 钉钉
万能回复：✅ 勾选
```

---

### Q7: 什么是万能回复？

**A**: 万能回复是 Layer0 级别的即时响应功能：

- **触发条件**: 任何消息
- **响应速度**: Layer0 级别（毫秒级）
- **用途**: 避免用户等待，提升体验
- **配置**: 在 Layer0 规则中勾选"万能回复"

**示例**:
```
用户：帮我查天气
→ 立即回复：收到，正在处理...（Layer0）
→ AI 继续处理实际任务
```

---

### Q8: 如何为不同渠道配置不同回复？

**A**: Layer0 规则支持渠道多选：

1. 创建规则时选择渠道
2. 可勾选多个渠道（飞书 + 钉钉 + QQ 等）
3. 该规则只对选中的渠道生效

**示例**:
```
渠道：☑️ 飞书 ☑️ 钉钉
模式：^日报.*
响应：日报已收到，正在分析...
```

---

## 任务管理

### Q9: 任务列表显示异常怎么办？

**A**: 已修复显示逻辑，现在优先显示用户实际指令：

**修复前**:
```
任务内容：Skills store policy (operator configured):
1. For skills discovery/install/update...
```

**修复后**:
```
任务内容：帮我查一下今天的天气
```

**如果仍显示异常**:
1. 刷新页面（Ctrl+F5）
2. 清除浏览器缓存
3. 检查任务数据源

---

### Q10: 如何查看任务详情？

**A**: 在 Dashboard 任务列表中：

1. 点击任务卡片查看摘要
2. 使用筛选功能：
   - **渠道**: 飞书/钉钉/QQ/等
   - **类型**: 定时/实时
   - **时间**: 当日/7 天/30 天/全部
3. 使用搜索功能查找特定任务

---

## 记忆系统

### Q11: 记忆列表显示系统上下文怎么办？

**A**: 已修复显示逻辑，自动过滤系统上下文：

**过滤内容**:
- ❌ `Skills store policy...`
- ❌ `Conversation info...`
- ❌ `Sender (untrusted metadata)...`
- ❌ `[message_id: ...]`

**保留内容**:
- ✅ 用户实际消息
- ✅ 对话内容
- ✅ 记忆摘要

**如果仍显示异常**:
1. 刷新页面
2. 清除浏览器缓存

---

### Q12: 记忆是如何存储的？

**A**: 记忆存储在多个位置：

1. **每日记忆文件**: `memory/YYYY-MM-DD.md`
2. **会话文件**: `sessions/*.jsonl`
3. **长期记忆**: `MEMORY.md`

**记忆分层**:
- **STM** (短期记忆): < 200 字
- **MTM** (中期记忆): 200-500 字
- **LTM** (长期记忆): > 500 字

---

## 安全配置

### Q13: 如何保护 Dashboard 安全？

**A**: 采用 Token 认证机制：

1. **强制 Token 验证**: 所有 API 接口必须验证 token
2. **Token 存储**: 保存在 `.lingxi/dashboard_token.txt`
3. **访问方式**: URL 中带 token 参数

**安全建议**:
- 不要泄露 token
- 定期更换 token
- 配置防火墙白名单（可选）

---

### Q14: 如何配置防火墙？

**A**: 使用 ufw 配置防火墙：

```bash
# 启用防火墙
sudo ufw enable

# 允许 Dashboard 端口
sudo ufw allow 8765

# 允许特定 IP（推荐）
sudo ufw allow from 你的 IP to any port 8765

# 允许 SSH
sudo ufw allow 22

# 查看状态
sudo ufw status
```

---

## 故障排查

### Q15: Dashboard 服务崩溃怎么办？

**A**: systemd 会自动重启服务：

1. **查看状态**:
   ```bash
   systemctl status lingxi-dashboard
   ```

2. **查看日志**:
   ```bash
   journalctl -u lingxi-dashboard -n 50
   ```

3. **手动重启**:
   ```bash
   systemctl restart lingxi-dashboard
   ```

**自动重启配置**:
```ini
Restart=always        # 总是自动重启
RestartSec=5          # 5 秒后重启
```

---

### Q16: API 接口返回 401 错误怎么办？

**A**: 401 表示 token 无效或缺失：

1. **检查 URL 是否带 token**:
   ```
   http://IP:8765/?token=你的 token
   ```

2. **检查 token 是否正确**:
   ```bash
   cat /root/.openclaw/workspace/.lingxi/dashboard_token.txt
   ```

3. **清除浏览器缓存**:
   - Ctrl+Shift+Delete
   - 清除缓存和 Cookie

4. **重新登录**:
   - 访问 `/login.html`
   - 输入正确的 token

---

### Q17: 如何查看系统日志？

**A**: 使用 journalctl 查看日志：

```bash
# Dashboard 实时日志
journalctl -u lingxi-dashboard -f

# 最近 100 条日志
journalctl -u lingxi-dashboard -n 100

# 指定时间范围
journalctl -u lingxi-dashboard --since "2026-03-14 10:00" --until "2026-03-14 12:00"

# 导出日志
journalctl -u lingxi-dashboard > /tmp/dashboard.log
```

---

### Q18: 如何备份数据？

**A**: 定期备份重要数据：

```bash
# 备份记忆文件
tar -czf memory_backup_$(date +%Y%m%d).tar.gz \
    /root/.openclaw/workspace/memory/ \
    /root/.openclaw/workspace/MEMORY.md

# 备份 Dashboard 数据
tar -czf dashboard_data_$(date +%Y%m%d).tar.gz \
    /root/lingxi-ai-latest/dashboard/v3/data/

# 备份到远程服务器
scp memory_backup_*.tar.gz user@backup-server:/backups/
```

---

## 版本信息

**当前版本**: v3.3.7  
**发布日期**: 2026-03-14  
**GitHub**: https://github.com/AI-Scarlett/lingxi-ai

---

## 获取帮助

- **GitHub Issues**: https://github.com/AI-Scarlett/lingxi-ai/issues
- **技术文档**: [TECHNICAL.md](TECHNICAL.md)
- **更新日志**: [RELEASE_NOTES.md](RELEASE_NOTES.md)

---

**灵犀 · 心有灵犀，一点就通** ✨
