# ⚡ Layer 0 技能调用配置指南

> 心有灵犀，一点就通 - 零思考直接调用技能 🚀

---

## 📖 什么是 Layer 0 技能？

Layer 0 技能是灵犀的**零思考直接调用**功能，用户说出指令后：

1. **不调 LLM** - 直接匹配预定义技能
2. **自动提取参数** - 智能解析用户需求
3. **立即执行** - 后台调用对应 API
4. **预定义回复** - 先回复"好的老板～"再执行

**响应时间**: <5ms  
**Tokens 消耗**: 0  
**成本**: ¥0

---

## 🎯 已配置技能（5 个）

### 1️⃣ 查找/搜索新闻 🔍

**触发词**: "查找新闻", "搜索新闻", "查一下新闻", "百度一下新闻"

**Action**: `browser_search`

**回复**: "好的老板～ 马上打开百度搜索～🔍"

**示例**:
```
用户：查找 AI 新闻
灵犀：好的老板～ 马上打开百度搜索～🔍
Action: 打开百度搜索"AI 新闻"
```

---

### 2️⃣ 写公众号内容 📝

**触发词**: "写公众号", "公众号文章", "写公众号内容", "同步到公众号"

**Action**: `wechat_create_draft`

**回复**: "好的老板～ 马上为您撰写并发布到公众号草稿箱～📝"

**示例**:
```
用户：写公众号文章
灵犀：好的老板～ 马上为您撰写并发布到公众号草稿箱～📝
Action: 调用 wechat_publisher 创建草稿
```

---

### 3️⃣ 来张自拍/照片 📸

**触发词**: "来张自拍", "自拍", "发张自拍", "拍张照", "你的照片"

**Action**: `clawra_selfie`

**回复**: "好的老板～ 马上就来～💋"

**示例**:
```
用户：来张自拍
灵犀：好的老板～ 马上就来～💋
Action: 调用 clawra_selfie API 生图
```

**参数提取**:
- "镜子自拍" → mode="mirror"
- "穿西装自拍" → outfit="西装"

---

### 4️⃣ 发微博（自拍 + 文案） 📱

**触发词**: "发微博", "微博发布", "发个自拍到微博", "配文案发微博"

**Action**: `weibo_post_with_image`

**回复**: "好的老板～ 马上生成自拍并发布到微博～📱"

**示例**:
```
用户：发个自拍到微博
灵犀：好的老板～ 马上生成自拍并发布到微博～📱
Action: clawra_selfie + weibo_publisher
```

---

### 5️⃣ 检查任务执行情况 📋

**触发词**: "检查任务", "任务执行情况", "查看任务", "HEARTBEAT 任务"

**Action**: `heartbeat_get_status`

**回复**: "好的老板～ 马上整理任务执行情况～📋"

**示例**:
```
用户：检查任务执行情况
灵犀：好的老板～ 马上整理任务执行情况～📋
Action: 读取 HEARTBEAT.md 生成报告
```

---

## 🔧 配置文件

**位置**: `~/.openclaw/workspace/.learnings/layer0_skills.json`

**格式**:
```json
{
  "version": "1.0",
  "custom_skills": [
    {
      "id": "custom_skill_id",
      "patterns": ["触发词 1", "触发词 2"],
      "skill_name": "技能名称",
      "action": "对应 action",
      "params_template": {"param1": "value1"},
      "reply_template": "回复模板",
      "enabled": true,
      "priority": 100,
      "param_extractors": {
        "param1": "正则表达式"
      }
    }
  ]
}
```

---

## 📝 添加自定义技能

### 方式一：编辑 JSON 文件

直接编辑 `layer0_skills.json`，添加新技能：

```json
{
  "id": "custom_weather",
  "patterns": ["天气", "天气预报"],
  "skill_name": "weather",
  "action": "weather_get",
  "params_template": {"city": "auto"},
  "reply_template": "好的老板～ 马上查询天气～🌤️",
  "priority": 100
}
```

### 方式二：Python 代码添加

```python
from layer0_skills import add_custom_skill

add_custom_skill(
    patterns=["天气", "天气预报"],
    skill_name="weather",
    action="weather_get",
    params_template={"city": "auto"},
    reply_template="好的老板～ 马上查询天气～🌤️",
    priority=100
)
```

---

## 🎯 参数提取器

支持正则表达式提取参数：

```json
{
  "param_extractors": {
    "minutes": "(\\d+) (分钟 | 分钟后)",
    "outfit": "(穿 | 穿着) (.*?) (裙子 | 西装)",
    "topic": "(关于 | 主题) (.*)$"
  }
}
```

**示例**:
- "5 分钟后提醒我" → minutes="5"
- "穿西装自拍" → outfit="西装"
- "关于 AI 的文章" → topic="AI"

---

## 📊 优先级设置

| 优先级 | 场景 | 示例 |
|--------|------|------|
| 100 | 高频技能 | 自拍、天气、搜索 |
| 90-99 | 中频技能 | 新闻、提醒 |
| 80-89 | 低频技能 | 音乐、电影 |
| 0-79 | 特殊技能 | 自定义功能 |

**注意**: 数字越大越优先匹配！

---

## 🔍 测试技能配置

```bash
cd /root/.openclaw/skills/lingxi
python3 scripts/layer0_skills.py
```

输出示例:
```
✅ '来张自拍'
   技能：clawra_selfie
   Action: clawra_selfie
   参数：{'mode': 'direct', 'outfit': 'default'}
   回复：好的老板～ 马上就来～💋
```

---

## 📋 当前配置清单

| 技能 | 触发词 | Action | 状态 |
|------|--------|--------|------|
| 🔍 搜索新闻 | "查找新闻", "搜索新闻" | browser_search | ✅ |
| 📝 公众号 | "写公众号", "公众号文章" | wechat_create_draft | ✅ |
| 📸 自拍 | "来张自拍", "自拍" | clawra_selfie | ✅ |
| 📱 微博 | "发微博", "微博发布" | weibo_post_with_image | ✅ |
| 📋 任务检查 | "检查任务", "任务执行情况" | heartbeat_get_status | ✅ |

---

## 🎉 使用示例

### 示例 1: 搜索新闻
```
用户：查找 AI 新闻
灵犀：好的老板～ 马上打开百度搜索～🔍
→ 打开百度搜索"AI 新闻"
```

### 示例 2: 写公众号
```
用户：写公众号文章
灵犀：好的老板～ 马上为您撰写并发布到公众号草稿箱～📝
→ 调用 wechat_publisher 创建草稿
```

### 示例 3: 自拍
```
用户：来张自拍
灵犀：好的老板～ 马上就来～💋
→ 调用 clawra_selfie API 生图并发送
```

### 示例 4: 微博发布
```
用户：发个自拍到微博
灵犀：好的老板～ 马上生成自拍并发布到微博～📱
→ clawra_selfie + weibo_publisher
```

### 示例 5: 检查任务
```
用户：检查任务执行情况
灵犀：好的老板～ 马上整理任务执行情况～📋
→ 读取 HEARTBEAT.md 生成报告
```

---

## ⚠️ 注意事项

1. **优先级冲突**: 如果多个技能触发词重叠，优先级高的先匹配
2. **参数提取**: 确保正则表达式正确，否则参数可能提取失败
3. **技能依赖**: 确保对应的技能已安装并可用
4. **回复模板**: 保持简洁友好，符合灵犀风格

---

## 🔗 相关文档

- [Layer 0 自定义配置指南](LAYER0_CUSTOM_GUIDE.md)
- [HEARTBEAT 任务同步器](HEARTBEAT_SYNC_GUIDE.md)
- [灵犀技能列表](SKILLS_LIST.md)

---

*本指南由灵犀 Learning Layer 自动生成*
