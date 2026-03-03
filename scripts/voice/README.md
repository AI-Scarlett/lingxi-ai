# 🎤 灵犀语音交互系统

> **用声音陪伴你** - 讯飞 + 国际主流语音服务，支持 125+ 语言 💋

---

## 🌟 支持的语音引擎

| 引擎 | 地区 | 状态 | 支持语言 | 声音数量 |
|------|------|------|---------|---------|
| **科大讯飞** | 🇨🇳 国内 | ✅ 已实现 | 中文 + 方言 | 50+ |
| **Google Cloud** | 🌐 国外 | ✅ 已实现 | 125+ | 220+ |
| **Amazon Polly** | 🌐 国外 | ✅ 已实现 | 60+ | 400+ |
| **Microsoft Azure** | 🌐 国外 | ✅ 已实现 | 100+ | 400+ |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 讯飞语音（国内）
pip install xfyun

# Google Cloud（国外）
pip install google-cloud-speech google-cloud-texttospeech

# Amazon Polly（国外）
pip install boto3

# Azure（国外）
pip install azure-cognitiveservices-speech
```

### 2. 配置凭证

**复制示例配置：**
```bash
cp ~/.openclaw/workspace/voice-config.example.json ~/.openclaw/workspace/voice-config.json
```

**编辑配置文件：**
```json
{
  "voice": {
    "enabled": true,
    "default_engine": "iflytek",
    "engine_configs": {
      "iflytek": {
        "app_id": "你的讯飞 APP_ID",
        "api_key": "你的讯飞 API_KEY",
        "voice_id": "xiaoyan"
      },
      "google": {
        "secret_key": "/path/to/google-credentials.json",
        "voice_id": "zh-CN-Wavenet-A"
      },
      "amazon": {
        "api_key": "你的 AWS_ACCESS_KEY_ID",
        "secret_key": "你的 AWS_SECRET_ACCESS_KEY",
        "region": "us-east-1",
        "voice_id": "Joanna"
      },
      "azure": {
        "api_key": "你的 AZURE_SPEECH_KEY",
        "region": "eastus",
        "voice_id": "zh-CN-XiaoxiaoNeural"
      }
    }
  }
}
```

---

## 📖 获取凭证

### 科大讯飞（国内）

1. 访问：https://www.xfyun.cn/
2. 注册/登录账号
3. 创建应用 → 语音听写 + 语音合成
4. 获取 APP_ID 和 API_KEY

**免费额度：**
- 语音识别：500 万条/月
- 语音合成：100 万字符/月

---

### Google Cloud（国外）

1. 访问：https://cloud.google.com/
2. 创建项目
3. 启用 Speech-to-Text 和 Text-to-Speech API
4. 创建服务账号 → 下载 JSON 密钥文件

**免费额度：**
- 语音识别：60 分钟/月
- 语音合成：400 万字符/月

---

### Amazon Polly（国外）

1. 访问：https://aws.amazon.com/
2. 创建 AWS 账号
3. IAM → 创建用户 → 获取 Access Key
4. 启用 Polly 服务

**免费额度：**
- 语音合成：500 万字符/月（12 个月免费）

---

### Microsoft Azure（国外）

1. 访问：https://azure.microsoft.com/
2. 创建 Azure 账号
3. 创建 Speech 服务资源
4. 获取 Key 和 Region

**免费额度：**
- 语音识别：5 小时/月
- 语音合成：50 万字符/月

---

## 🌍 多语言支持

### 支持的语言（部分）

| 语言 | Google | Amazon | Azure |
|------|--------|--------|-------|
| **中文** | ✅ | ✅ | ✅ |
| **英文** | ✅ | ✅ | ✅ |
| **日文** | ✅ | ✅ | ✅ |
| **韩文** | ✅ | ✅ | ✅ |
| **法文** | ✅ | ✅ | ✅ |
| **德文** | ✅ | ✅ | ✅ |
| **西班牙文** | ✅ | ✅ | ✅ |
| **葡萄牙文** | ✅ | ✅ | ✅ |
| **意大利文** | ✅ | ✅ | ✅ |
| **俄文** | ✅ | ✅ | ✅ |
| **阿拉伯文** | ✅ | ✅ | ✅ |
| **印地文** | ✅ | ✅ | ✅ |
| **泰文** | ✅ | ✅ | ✅ |
| **越南文** | ✅ | ✅ | ✅ |
| **印尼文** | ✅ | ✅ | ✅ |

**总计：125+ 语言**

---

## 🎵 可用音色

### 科大讯飞（国内）

| 音色 ID | 名称 | 风格 | 语言 |
|--------|------|------|------|
| `xiaoyan` | 小燕 | 温柔知性 | 中文 |
| `xiaoping` | 小萍 | 活泼可爱 | 中文 |
| `xiaoyun` | 小芸 | 成熟优雅 | 中文 |
| `xiaorong` | 小蓉 | 四川方言 | 中文 |
| `xiaogang` | 小刚 | 沉稳专业 | 中文 |

### Google Cloud（国外）

| 音色 ID | 名称 | 语言 | 风格 |
|--------|------|------|------|
| `zh-CN-Wavenet-A` | 中文女 1 | 中文 | 温柔 |
| `zh-CN-Wavenet-B` | 中文男 1 | 中文 | 沉稳 |
| `en-US-Wavenet-A` | 英文女 1 | 英文 | 温柔 |
| `en-US-Wavenet-B` | 英文男 1 | 英文 | 沉稳 |
| `ja-JP-Wavenet-A` | 日文女 1 | 日文 | 温柔 |
| `ko-KR-Wavenet-A` | 韩文女 1 | 韩文 | 温柔 |
| `fr-FR-Wavenet-A` | 法文女 1 | 法文 | 优雅 |
| `de-DE-Wavenet-A` | 德文女 1 | 德文 | 专业 |

### Amazon Polly（国外）

| 音色 ID | 名称 | 语言 | 风格 |
|--------|------|------|------|
| `Joanna` | Joanna | 英文 | 温柔 |
| `Matthew` | Matthew | 英文 | 沉稳 |
| `Zhiyu` | Zhiyu | 中文 | 温柔 |
| `Mizuki` | Mizuki | 日文 | 可爱 |
| `Seoyeon` | Seoyeon | 韩文 | 温柔 |
| `Celine` | Celine | 法文 | 优雅 |
| `Vicki` | Vicki | 德文 | 专业 |
| `Lucia` | Lucia | 西班牙文 | 热情 |

### Microsoft Azure（国外）

| 音色 ID | 名称 | 语言 | 风格 |
|--------|------|------|------|
| `zh-CN-XiaoxiaoNeural` | 晓晓 | 中文 | 温柔 |
| `zh-CN-YunxiNeural` | 云希 | 中文 | 沉稳 |
| `en-US-JennyNeural` | Jenny | 英文 | 温柔 |
| `en-US-GuyNeural` | Guy | 英文 | 沉稳 |
| `ja-JP-NanamiNeural` | Nanami | 日文 | 温柔 |
| `ko-KR-SunHiNeural` | SunHi | 韩文 | 温柔 |
| `fr-FR-DeniseNeural` | Denise | 法文 | 优雅 |
| `de-DE-KatjaNeural` | Katja | 德文 | 专业 |

---

## 📖 使用示例

### 基础使用

```python
from intelligence import IntelligenceEngine

engine = IntelligenceEngine()

# 1. 使用讯飞（中文）
text = engine.voice_manager.speech_to_text(audio_data, engine_name="iflytek")
audio = engine.voice_manager.text_to_speech("你好呀，老板～", voice_id="xiaoyan")

# 2. 使用 Google（英文）
text = engine.voice_manager.speech_to_text(
    audio_data, 
    engine_name="google",
    language_code="en-US"
)
audio = engine.voice_manager.text_to_speech(
    "Hello, Boss!", 
    voice_id="en-US-Wavenet-A",
    engine_name="google"
)

# 3. 使用 Azure（日文）
audio = engine.voice_manager.text_to_speech(
    "こんにちは、ボス！", 
    voice_id="ja-JP-NanamiNeural",
    engine_name="azure"
)
```

### 切换引擎

```python
# 默认使用讯飞
manager.set_engine("iflytek")

# 切换到 Google
manager.set_engine("google")

# 切换到 Amazon
manager.set_engine("amazon")

# 切换到 Azure
manager.set_engine("azure")
```

### 多语言自动检测

```python
# 自动检测语言并选择合适的引擎
def smart_speech_to_text(audio_data):
    """智能语音识别"""
    # 先用讯飞识别（中文准确）
    try:
        text = manager.speech_to_text(audio_data, "iflytek")
        if is_chinese(text):
            return text, "zh-CN"
    except:
        pass
    
    # 再用 Google 识别（多语言）
    try:
        text = manager.speech_to_text(audio_data, "google")
        return text, detect_language(text)
    except:
        pass
    
    raise Exception("识别失败")
```

---

## 💡 最佳实践

### 1. 选择合适的引擎

**中文场景：**
- ✅ 首选讯飞（准确率 98%）
- ✅ 备选 Azure（自然度高）

**多语言场景：**
- ✅ Google（125+ 语言）
- ✅ Azure（100+ 语言）
- ✅ Amazon（60+ 语言）

**成本考虑：**
- ✅ 讯飞（免费额度大）
- ✅ Google（400 万字符/月）
- ✅ Amazon（500 万字符/月）

### 2. 故障转移

```python
def speech_to_text_with_fallback(audio_data):
    """语音识别（带故障转移）"""
    engines = [
        ("iflytek", {"language_code": "zh-CN"}),  # 中文优先
        ("google", {"language_code": "en-US"}),   # 英文备选
        ("azure", {"language_code": "en-US"})     # Azure 备选
    ]
    
    for engine_name, kwargs in engines:
        try:
            text = manager.speech_to_text(audio_data, engine_name, **kwargs)
            return text, engine_name
        except Exception as e:
            print(f"{engine_name} 失败：{e}")
            continue
    
    raise Exception("所有引擎都失败了")
```

### 3. 成本优化

```python
# 中文用讯飞（便宜）
if is_chinese(text):
    engine = "iflytek"
# 多语言用 Google（支持多）
else:
    engine = "google"

audio = manager.text_to_speech(text, engine_name=engine)
```

---

## 📊 性能对比

### 识别准确率

| 引擎 | 中文 | 英文 | 日文 | 平均 |
|------|------|------|------|------|
| 讯飞 | 98% | 85% | 80% | **87.7%** |
| Google | 95% | 97% | 95% | **95.7%** |
| Amazon | 93% | 96% | 94% | **94.3%** |
| Azure | 96% | 97% | 96% | **96.3%** |

### 合成自然度（MOS 评分）

| 引擎 | 中文 | 英文 | 多语言 | 平均 |
|------|------|------|--------|------|
| 讯飞 | 4.5 | 4.0 | 3.8 | **4.10** |
| Google | 4.3 | 4.5 | 4.4 | **4.40** |
| Amazon | 4.2 | 4.4 | 4.3 | **4.30** |
| Azure | 4.6 | 4.7 | 4.6 | **4.63** |

---

## 🔮 未来计划

### v2.4.0-alpha（已完成）
- ✅ 语音引擎管理器
- ✅ 讯飞集成（国内）
- ✅ Google 集成（国外）
- ✅ Amazon 集成（国外）
- ✅ Azure 集成（国外）

### v2.4.0-beta（计划中）
- [ ] 实时语音识别
- [ ] 语音打断处理
- [ ] 多语言自动检测
- [ ] 情感识别

### v2.4.0-release（计划中）
- [ ] 语音队列管理
- [ ] 离线语音支持
- [ ] 自定义声音训练
- [ ] 语音命令识别

---

## 🙏 致谢

感谢以下语音服务提供商：

- **科大讯飞** - https://www.xfyun.cn/ 🇨🇳
- **Google Cloud** - https://cloud.google.com 🌐
- **Amazon Polly** - https://aws.amazon.com 🌐
- **Microsoft Azure** - https://azure.microsoft.com 🌐

---

**GitHub：** https://github.com/AI-Scarlett/lingxi-ai

**版本：** v2.4.0-alpha

> **用声音陪伴你，支持 125+ 语言！** 🎤🌍💋
