# 🔒 灵犀 Dashboard 安全指南

**版本：** v3.3.3  
**重要性：** ⭐⭐⭐⭐⭐（非常重要）

---

## ⚠️ 重要安全提示

**你的访问地址包含专属 Token，请勿泄露！**

---

## 🚫 绝对不要做的事

### ❌ 不要发给陌生人
- 陌生人可能恶意使用你的 Dashboard
- 可能查看你的隐私数据
- 可能消耗你的资源

### ❌ 不要发到公开群聊
- 群聊里可能有坏人
- 一旦泄露无法收回
- 可能被截图传播

### ❌ 不要发到社交媒体
- 朋友圈/QQ 空间/微博都不行
- 截图会暴露 Token
- 可能被陌生人看到

### ❌ 不要截图分享
- 截图包含完整 Token
- 截图可能被传播
- 无法控制谁能看到

---

## ✅ 正确的做法

### ✅ 仅限自己使用
- 只在自己设备上访问
- 不要分享给他人
- 定期更换 Token

### ✅ 妥善保管访问地址
- 保存到安全的地方
- 不要明文存储
- 使用密码管理器

### ✅ 定期检查 Token
```bash
# 查看所有有效 tokens
python3 quick_access.py --list-tokens

# 撤销可疑的 tokens
python3 quick_access.py --revoke <token>
```

### ✅ 如已泄露，立即处理
```bash
# 1. 撤销已泄露的 token
python3 quick_access.py --revoke <泄露的 token>

# 2. 生成新的 token
python3 quick_access.py --generate-token

# 3. 更新所有访问地址
```

---

## 🔐 Token 管理最佳实践

### 定期更换
```bash
# 建议每 30 天更换一次
python3 quick_access.py --generate-token

# 撤销旧的
python3 quick_access.py --revoke <旧 token>
```

### 分类管理
```bash
# 为不同设备生成不同 token
python3 quick_access.py --generate-token  # 手机用
python3 quick_access.py --generate-token  # 电脑用
python3 quick_access.py --generate-token  # 平板用

# 查看
python3 quick_access.py --list-tokens
```

### 权限控制
```bash
# 为不同用途生成 token
python3 quick_access.py --generate-token  # 日常使用
python3 quick_access.py --generate-token  # 临时分享（短期有效期）
```

---

## 🛡️ 安全配置建议

### 1. 使用内网访问（最安全）
```
内网访问只在同一 WiFi 内有效
外部无法访问
最安全！
```

### 2. 配置防火墙
```bash
# Linux
sudo ufw allow from 192.168.1.0/24 to any port 8766

# Windows
控制面板 → 防火墙 → 高级设置 → 入站规则
→ 只允许内网 IP 访问
```

### 3. 定期审查访问记录
```bash
# 查看 token 访问记录
python3 quick_access.py --list-tokens

# 检查异常访问
# 如有异常，立即撤销
```

---

## 🚨 安全事件响应

### 发现泄露怎么办？

**步骤 1：立即撤销**
```bash
python3 quick_access.py --revoke <泄露的 token>
```

**步骤 2：生成新的**
```bash
python3 quick_access.py --generate-token
```

**步骤 3：更新访问地址**
```bash
python3 show_access.py
```

**步骤 4：检查访问记录**
```bash
python3 quick_access.py --list-tokens
# 查看是否有异常访问
```

### 怀疑被入侵怎么办？

**步骤 1：撤销所有 tokens**
```bash
# 手动删除 token 文件
rm ~/.openclaw/workspace/.lingxi/access_tokens.json
```

**步骤 2：生成全新的 tokens**
```bash
python3 quick_access.py --generate-token
```

**步骤 3：检查系统日志**
```bash
# 查看 Dashboard 日志
tail -f /tmp/dashboard.log
```

---

## 📋 安全检查清单

### 每周检查
- [ ] 查看 token 列表
- [ ] 检查访问记录
- [ ] 撤销不用的 tokens

### 每月检查
- [ ] 更换所有 tokens
- [ ] 检查防火墙配置
- [ ] 审查访问日志

### 每季度检查
- [ ] 全面安全审计
- [ ] 更新所有配置
- [ ] 检查系统更新

---

## 💡 常见问题

### Q: Token 有效期多久？

**A:** 默认 30 天，可以自定义。

### Q: 可以设置永久的 token 吗？

**A:** 不建议！为了安全，建议定期更换。

### Q: 忘记 token 怎么办？

**A:** 
```bash
python3 quick_access.py --list-tokens
```

### Q: 可以同时使用多个 token 吗？

**A:** 可以！每个设备一个 token，便于管理。

### Q: token 被暴力破解怎么办？

**A:** 不可能！token 是随机生成的，比密码安全得多。

---

## 📞 需要帮助？

**文档：** 本文档  
**技术支持：** 飞书联系 Scarlett  
**紧急联系：** 立即撤销所有 tokens

---

**记住：安全无小事，保护你的访问地址！** 🔒

**灵犀系统 v3.3.3**  
2026-03-11
