
---

## 📝 飞书云文档创建 + 写入最佳实践 (2026-03-12)

**问题**: 直接用 REST API 写入文档内容返回 404

**解决**: 使用 OpenClaw 的 `feishu_doc` 工具，正确的操作顺序：

```python
# 1. 先创建文档 (action: create)
feishu_doc(action="create", title="文档标题")

# 2. 获取返回的 document_id，然后写入内容 (action: write)
feishu_doc(action="write", doc_token="返回的document_id", content="完整Markdown内容")
```

**注意**: 
- 不能用 REST API 直接调用 `/blocks` 插入，会 404
- 必须用 OpenClaw 集成的 feishu_doc 工具
- write action 会自动把 Markdown 转换为飞书文档块

---

## 🔐 重要凭证索引 (2026-03-09 整理)

**GitHub:**
- 用户名：AI-Scarlett
- Token: 已移除
- 位置：/root/.github_token
- 仓库：hunter-daily-report

**阿里云百炼:**
- API Key 1: sk-d84ce7d711c14942af76aa5722cbd037 (自拍)
- API Key 2: sk-871c8e233cbf4ce997b728b3a76b9dce (备用)

**微信公众号:**
- AppID: wxd04bcd7faf50af4b
- AppSecret: 8d2d876ea7e1f6d07bd26653aac74697
- 服务器 IP: 106.52.101.202

**OpenClaw Gateway:**
- Token: c5aab3f96d6cd6506ca530b9203d1ea3f304be481698885a

**详细文档:** `/root/.openclaw/workspace/CREDENTIALS.md` (权限 600)

---

## 🔐 阿里云百炼 API Keys (2026-03-09 补充)

**主 Key (灵犀/Hunter):**
- Key: sk-sp-d6afbe98ff954e3789c9a3bd973e00aa
- 端点：https://coding.dashscope.aliyuncs.com/v1
- 模型：qwen3.5-plus, qwen3-max, qwen3-coder-plus, MiniMax, kimi, glm

**文生图 Key:**
- Key: sk-871c8e233cbf4ce997b728b3a76b9dce
- 端点：https://dashscope.aliyuncs.com/api/v1

**自拍 Key:**
- Key: sk-d84ce7d711c14942af76aa5722cbd037
- 用途：斯嘉丽自拍生成

**DeepSeek Key:**
- Key: sk-3c2d5b90fe2f469cbac4de40ad0cc87a
- 端点：https://api.deepseek.com/v1

**详细文档:** `/root/.openclaw/workspace/CREDENTIALS.md`
