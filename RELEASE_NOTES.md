# 灵犀 AI 助手 v3.3.7 发布说明

**发布日期**: 2026-03-14  
**版本**: v3.3.7  
**代号**: 稳如泰山

---

## 🎉 重大更新

### 1. systemd 守护进程 🔧

**永久稳定运行，彻底解决服务崩溃问题**：

- **自动启动**: 开机自动启动 Dashboard
- **自动重启**: 崩溃后 5 秒自动重启
- **日志记录**: journalctl 统一查看日志
- **资源限制**: 65535 文件描述符
- **安全加固**: PrivateTmp, NoNewPrivileges

**配置方式**:
```bash
systemctl enable lingxi-dashboard
systemctl start lingxi-dashboard
```

### 2. Layer0 渠道多选 📱

**支持自由选择多个渠道配置万能回复**：

- **渠道选项**: 飞书/钉钉/QQ/企业微信/WebChat/其他
- **多选模式**: 可勾选任意组合（1-6 个渠道）
- **万能回复**: 任何消息立即响应，无需等待 AI 处理
- **API 接口**: 新增 `/api/layer0/channel-config`

**使用场景**:
```
渠道：☑️ 飞书 ☑️ 钉钉
模式：^紧急.*
响应：收到，马上处理！
万能回复：✅ 勾选
```

### 3. 显示优化 🎨

**修复任务列表和记忆列表显示问题**：

- **任务列表**: 优先显示 summary，过滤系统上下文
- **记忆列表**: 智能提取用户实际指令
- **过滤内容**: Skills store policy/Conversation info 等
- **性能优化**: 每页 50 条数据，支持分页

**修复前**:
```
任务内容：Skills store policy (operator configured):
1. For skills discovery/install/update...
```

**修复后**:
```
任务内容：帮我查一下今天的天气
```

### 4. Q&A 文档 📚

**新增常见问题解答文档**：

- **7 大分类**: 安装部署/Dashboard 访问/Layer0 规则/任务管理/记忆系统/安全配置/故障排查
- **18 个常见问题**: 覆盖用户使用场景
- **详细解答**: 包含命令示例和截图说明
- **持续更新**: 根据用户反馈持续补充

**文档位置**: [QA.md](QA.md)

**等级详情**:
| 等级 | 积分 | CPU | GPU | Token/天 | 优先级 |
|------|------|-----|-----|----------|--------|
| 王牌 | 500+ | 8 核 | 独占 | 100,000 | 1.5x |
| 钻石 | 300-499 | 4 核 | 优先 | 50,000 | 1.3x |
| 金牌 | 200-299 | 2 核 | 正常 | 20,000 | 1.1x |
| 银牌 | 100-199 | 2 核 | 正常 | 10,000 | 1.0x |
| 普通 | 50-99 | 1 核 | 空闲 | 5,000 | 0.8x |
| 观察 | 0-49 | 0.5 核 | 禁止 | 1,000 | 0.5x |
| 隔离 | <0 | 0.5 核 | 禁止 | 500 | 0.0x |

### 2. 主动巡察系统 🔍

每 30 分钟自动执行全面检查：

**服务健康检查**:
- ✅ Dashboard 服务 HTTP 可访问性
- ✅ 每小时汇报日志检查
- ✅ 定时任务 Cron 状态
- ✅ OpenClaw Gateway 运行状态

**安全检查** (新增):
- 🔒 敏感信息泄露检测（CREDENTIALS.md、硬编码密钥、日志脱敏）
- 🔒 外网 IP 暴露检查（Dashboard 绑定、防火墙状态、端口暴露）
- 🔒 API 密钥安全检查（.env 权限、明文密钥、Git 历史）
- 🔒 文件权限检查（关键文件权限、脚本可执行权限）

**告警机制**: 发现高风险问题时自动飞书推送告警

### 3. 设备绑定认证系统 🔐

彻底解决端口暴露安全风险：

**核心功能**:
- 设备注册：首次访问自动注册，生成唯一设备 ID
- 设备指纹：基于 UserAgent + IP + 屏幕分辨率
- 管理员审批：新设备需要管理员审批后才能访问
- 设备管理：Dashboard 可查看/审批/撤销所有设备
- Token 认证：审批通过后 30 天有效，自动续期

**使用流程**:
1. 新设备访问 → 自动跳转到设备注册页面
2. 填写设备名称（可选）→ 提交申请
3. 等待管理员审批
4. 审批通过 → 无感访问 Dashboard

**设备管理页面**:
```
http://localhost:8765/pages/devices.html?token=<your_token>
```

### 4. EvoMind 自改进 🔄

真正的自动化改进机制：

**分析维度**:
- 任务失败原因分析
- 汇报延迟统计
- 资源使用优化建议

**执行周期**: 每 6 小时自动执行

**输出**:
- 改进建议（JSON 格式，保存到 `data/evomind_history.json`）
- HEARTBEAT.md 自动更新
- Dashboard API 实时数据

---

## 🔧 功能优化

### MindCore 记忆管理
- ✅ 修复记忆时间显示问题（从硬编码 23:59 改为文件实际修改时间）
- ✅ 从会话文件自动提取记忆（补充 memory 文件不足）
- ✅ 记忆总数突破 164 条

### Dashboard 可视化
- ✅ Agent 监控页面（Tab 切换模式）
- ✅ Agent 积分排行榜页面（Tab 切换模式）
- ✅ 设备管理页面（管理员专用）
- ✅ 导航优化（从新标签页打开改为 Tab 切换）

### 定时任务
- ✅ 主动巡察：`*/30 * * * *`
- ✅ EvoMind 分析：`0 */6 * * *`
- ✅ 每小时汇报：`0 * * * *`
- ✅ 健康检查：`*/5 * * * *`
- ✅ 每日简报：`0 8,12,21 * * *`
- ✅ 商机报告：`0 0 * * *`

---

## 📊 统计数据

### 代码统计
- **核心模块**: 3 个（agent_credit.py, evomind.py, device_auth.py）
- **脚本工具**: 2 个（active_inspection.py, hourly_progress_report.py）
- **Dashboard 页面**: 4 个（agents.html, agent_credit.html, devices.html, device_register.html）
- **代码行数**: ~3000 行
- **API 接口**: 20+ 个

### 功能统计
- **记忆总数**: 164 条
- **Layer0 规则**: 191 条
- **已安装技能**: 10 个
- **定时任务**: 6 个
- **设备认证**: 已启用

---

## 🚀 安装升级

### 新安装

```bash
# 克隆项目
git clone https://github.com/AI-Scarlett/lingxi-ai.git
cd lingxi-ai

# 安装依赖
pip install -r requirements.txt

# 启动 Dashboard
cd dashboard/v3
python3 server.py
```

### 升级

```bash
# 拉取最新代码
git pull origin master

# 安装新依赖
pip install -r requirements.txt --upgrade

# 重启 Dashboard
pkill -f server.py
cd dashboard/v3 && python3 server.py &
```

---

## ⚠️ 重要说明

### 安全建议

1. **Dashboard 绑定限制**
   ```bash
   # 修改为只监听本地
   uvicorn server:app --host 127.0.0.1 --port 8765
   ```

2. **配置防火墙**
   ```bash
   ufw allow from 信任 IP to any port 8765
   ufw deny 8765
   ```

3. **文件权限**
   ```bash
   chmod 600 CREDENTIALS.md
   chmod 600 .env
   chmod +x scripts/*.py
   ```

### 已知问题

- 设备认证系统首次使用需要手动审批
- Agent 积分初始值为 100 分，需要时间积累
- Dashboard 首次加载可能较慢（建议启用缓存）

---

## 📝 更新计划

### v3.3.7 (计划 2026-03-21)
- [ ] 记忆语义搜索优化
- [ ] 技能自动更新机制
- [ ] Dashboard 性能优化
- [ ] 移动端适配

### v3.4.0 (计划 2026-03-28)
- [ ] 多 Agent 协作系统
- [ ] 任务依赖关系管理
- [ ] 高级数据分析报表
- [ ] Webhook 集成

---

## 🙏 致谢

感谢所有贡献者和用户！

特别感谢：
- OpenClaw 团队提供基础框架
- MemOS 项目提供记忆管理灵感
- 社区用户提供宝贵建议

---

## 📞 联系方式

- **GitHub**: https://github.com/AI-Scarlett/lingxi-ai
- **Issues**: https://github.com/AI-Scarlett/lingxi-ai/issues
- **Discussions**: https://github.com/AI-Scarlett/lingxi-ai/discussions

---

**灵犀 · 心有灵犀，一点就通** ✨
