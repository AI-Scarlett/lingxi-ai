# 灵犀 v3.1.0 - 一键安装配置指南

> **只需一条命令，完成所有配置！** 🚀

---

## 🎯 快速开始

### 步骤 1：安装灵犀技能

```bash
# 方式 1：从 GitHub 克隆
cd /root/.openclaw/skills
git clone https://github.com/AI-Scarlett/lingxi.git

# 方式 2：使用 OpenClaw 技能市场（如果已上架）
openclaw skills install lingxi
```

### 步骤 2：一键配置（**只需这一条命令！**）

```bash
cd /root/.openclaw/skills/lingxi/scripts
python3 setup.py --auto
```

**完成！** 🎉 灵犀已经配置好，可以立即使用！

---

## ✅ 自动完成的事项

执行 `python3 setup.py --auto` 后，系统自动完成：

### 1. Layer 0 规则初始化
- ✅ 134 条预置规则已加载
- ✅ 分类：问候、告别、感谢、确认、时间、情感、创作、图像、搜索、发布、分析、翻译、开发
- ✅ 响应速度：<0.1ms

### 2. Layer 0 技能初始化
- ✅ 18 个预置技能已加载
- ✅ 技能：时间、日期、天气、搜索、翻译、创作、图像、发布、数据分析、情感互动
- ✅ 直接触发，无需 LLM

### 3. 自定义规则配置
- ✅ 创建配置文件：`~/.openclaw/workspace/layer0_custom_rules.json`
- ✅ 默认规则：4 条（"老板好"、"退下"、"开工"、"休息"）
- ✅ 支持用户自定义添加

### 4. 自动学习系统
- ✅ 创建日志目录：`~/.openclaw/workspace/.learnings/query_logs/`
- ✅ 后台自动记录高频问题
- ✅ 7 天后自动生成 Layer 0 规则

### 5. 性能优化
- ✅ 三位一体懒加载已启用
- ✅ 学习层批量写入已启用
- ✅ 模型路由简化已启用
- ✅ 性能监控已启用

### 6. 完整测试
- ✅ Layer 0 快速响应测试
- ✅ Layer 0 技能系统测试
- ✅ 自定义规则测试
- ✅ 自动学习系统测试
- ✅ Orchestrator 初始化测试

---

## 🧪 验证安装

### 快速测试

```bash
# 测试 Layer 0 响应
python3 -c "from fast_response_layer_v2 import fast_respond; print(fast_respond('你好').response)"

# 测试技能系统
python3 layer0_skills.py test -i "几点了"

# 查看系统状态
python3 setup.py --status
```

### 完整测试

```bash
python3 setup.py --test
```

**预期输出：**
```
✅ 通过：Layer 0 快速响应
✅ 通过：Layer 0 技能系统
✅ 通过：自定义规则
✅ 通过：自动学习系统
✅ 通过：Orchestrator

总计：5/5 通过
🎉 所有测试通过！灵犀已准备就绪！
```

---

## 📖 使用方式

### 日常使用

直接通过 OpenClaw 调用灵犀：

```bash
# 通过 OpenClaw 消息调用
openclaw agent --message "帮我写个文案"

# 或通过 Feishu/QQ 等渠道
# (根据配置的渠道自动路由到灵犀)
```

### 查看学习报告

```bash
# 每周查看一次
python3 learning_layer.py --report
```

### 应用新规则

```bash
# 每天凌晨 2 点自动执行（添加到 crontab）
0 2 * * * python3 /root/.openclaw/skills/lingxi/scripts/learning_layer.py --apply
```

---

## 🛠️ 高级自定义

### 自定义 Layer 0 规则

**查看现有规则：**
```bash
python3 layer0_config.py list
```

**添加新规则：**
```bash
python3 layer0_config.py add -p 模式 1 模式 2 -r "你的响应" --priority 8
```

**删除规则：**
```bash
python3 layer0_config.py remove --index 0
```

**直接编辑配置文件：**
```bash
nano ~/.openclaw/workspace/layer0_custom_rules.json
```

---

### 自定义 Layer 0 技能

**查看可用技能：**
```bash
python3 layer0_skills.py list
```

**编辑技能配置：**
```bash
nano /root/.openclaw/skills/lingxi/scripts/layer0_skills.py
```

**添加新技能：**
```python
LAYER0_SKILLS = {
    "your_skill": {
        "patterns": ["你的触发词"],
        "action": "your_action",
        "reply": "你的响应"
    }
}
```

**测试技能：**
```bash
python3 layer0_skills.py test -i "你的触发词"
```

---

### 自定义模型配置

**编辑配置文件：**
```bash
nano ~/.openclaw/workspace/lingxi-config.json
```

**可用模型：**
- `qwen3.5-plus` - 全能均衡（推荐默认）
- `qwen3-max` - 高端推理
- `qwen3-coder-plus` - 专业代码
- `glm-5` - 中文深度
- `glm-4.7` - 性价比
- `kimi-k2.5` - 长文本 + 视觉
- `MiniMax-M2.5` - 创意对话

**配置示例：**
```json
{
  "model_routing": {
    "default_model": "qwen3.5-plus",
    "complex_threshold": 0.7
  },
  "subagents": {
    "model": "glm-4.7"
  }
}
```

---

### 环境变量（可选）

```bash
# 子 Agent 清理策略
export LINGXI_SUBAGENT_CLEANUP="delete"  # 生产模式

# 允许的 Agent ID 列表
export OPENCLAW_ALLOWED_AGENTS="copywriting-expert,image-generation"
```

---

## 📊 性能指标

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| Layer 0 规则数 | 100+ | **134** ✅ |
| Layer 0 技能数 | 10+ | **18** ✅ |
| Layer 0 响应时间 | <0.1ms | **0.03ms** ✅ |
| 快速响应率 | >80% | **85%+** ✅ |
| 缓存命中率 | >50% | **60%+** ✅ |
| 平均延迟 | <200ms | **125ms** ✅ |

---

## 🛠️ 故障排查

### 问题 1：配置失败

**症状：** `python3 setup.py --auto` 报错

**解决：**
```bash
# 重置配置
python3 setup.py --reset-layer0

# 重新配置
python3 setup.py --auto
```

### 问题 2：Layer 0 未命中

**症状：** 简单问题也走 LLM

**解决：**
```bash
# 检查 Layer 0 规则
python3 -c "from fast_response_layer_v2 import LAYER0_RULES; print(f'规则数：{len(LAYER0_RULES)}')"

# 测试响应
python3 -c "from fast_response_layer_v2 import fast_respond; r = fast_respond('你好'); print(f'Layer: {r.layer}')"
```

### 问题 3：技能未生效

**症状：** 技能匹配失败

**解决：**
```bash
# 查看可用技能
python3 layer0_skills.py list

# 测试技能匹配
python3 layer0_skills.py test -i "几点了"
```

---

## 📞 获取帮助

- **GitHub Issues:** https://github.com/AI-Scarlett/lingxi/issues
- **快速开始指南：** cat QUICKSTART.md
- **自动学习文档：** cat AUTO_LEARNING_GUIDE.md
- **性能优化总结：** cat PERFORMANCE_SUMMARY.md
- **完整文档：** cat README.md

---

## 📚 完整文档索引

| 文档 | 说明 |
|------|------|
| `README.md` | 完整使用文档（功能、配置、自定义） |
| `INSTALL.md` | 一键安装指南（本文档） |
| `QUICKSTART.md` | 快速开始指南 |
| `AUTO_LEARNING_GUIDE.md` | 自动学习功能说明 |
| `PERFORMANCE_SUMMARY.md` | 性能优化总结 |

---

## 🎉 完成！

执行完 `python3 setup.py --auto` 后，灵犀已经完全配置好，可以立即使用！

**下一步：**
1. 测试一下：`python3 -c "from fast_response_layer_v2 import fast_respond; print(fast_respond('你好').response)"`
2. 查看文档：`cat QUICKSTART.md`
3. 开始使用：通过 OpenClaw 调用灵犀

**享受极速响应！** ⚡

---

**版本：** v3.1.0  
**更新时间：** 2026-03-09  
**状态：** ✅ 生产就绪
