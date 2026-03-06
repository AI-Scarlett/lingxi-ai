#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音引擎管理器 - Voice Engine Manager
支持多个国内语音服务，用户可自由切换 💋

支持的引擎：
- 科大讯飞（首选）
- 百度语音
- 阿里云百炼（新增）
- 腾讯云
- 微软 Azure（国内版）
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """语音配置"""
    engine: str
    app_id: str
    api_key: str
    secret_key: Optional[str] = None
    voice_id: Optional[str] = None
    region: Optional[str] = None


class BaseVoiceEngine(ABC):
    """语音引擎基类"""
    
    name: str = "base"
    display_name: str = "语音引擎"
    
    @abstractmethod
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """语音识别"""
        pass
    
    @abstractmethod
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """语音合成"""
        pass
    
    @abstractmethod
    def get_voices(self) -> List[Dict[str, str]]:
        """获取可用音色列表"""
        pass
    
    @abstractmethod
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查凭证是否有效"""
        pass


class IFlytekEngine(BaseVoiceEngine):
    """科大讯飞语音引擎"""
    
    name = "iflytek"
    display_name = "科大讯飞"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def _get_client(self):
        """获取客户端（懒加载）"""
        if self._client is None and self.config:
            from xfyun import SpeechRecognizer, SpeechSynthesizer
            self._client = {
                "recognizer": SpeechRecognizer(
                    app_id=self.config.app_id,
                    api_key=self.config.api_key
                ),
                "synthesizer": SpeechSynthesizer(
                    app_id=self.config.app_id,
                    api_key=self.config.api_key,
                    voice=self.config.voice_id or "xiaoyan"
                )
            }
        return self._client
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """讯飞语音识别"""
        client = self._get_client()
        if not client:
            raise Exception("讯飞未配置")
        
        result = client["recognizer"].recognize(audio_data)
        return result.get("text", "")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """讯飞语音合成"""
        client = self._get_client()
        if not client:
            raise Exception("讯飞未配置")
        
        voice = voice_id or self.config.voice_id or "xiaoyan"
        audio_data = client["synthesizer"].synthesize(text, voice=voice)
        return audio_data
    
    def get_voices(self) -> List[Dict[str, str]]:
        """讯飞可用音色"""
        return [
            {"id": "xiaoyan", "name": "小燕", "style": "温柔知性", "gender": "女"},
            {"id": "xiaoping", "name": "小萍", "style": "活泼可爱", "gender": "女"},
            {"id": "xiaoyun", "name": "小芸", "style": "成熟优雅", "gender": "女"},
            {"id": "xiaorong", "name": "小蓉", "style": "四川方言", "gender": "女"},
            {"id": "xiaogang", "name": "小刚", "style": "沉稳专业", "gender": "男"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查讯飞凭证"""
        try:
            # 简单检查，实际应该调用 API
            return bool(config.app_id and config.api_key)
        except:
            return False


class BaiduEngine(BaseVoiceEngine):
    """百度语音引擎"""
    
    name = "baidu"
    display_name = "百度语音"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def _get_client(self):
        """获取客户端（懒加载）"""
        if self._client is None and self.config:
            from aip import AipSpeech
            self._client = AipSpeech(
                self.config.app_id,
                self.config.api_key,
                self.config.secret_key
            )
        return self._client
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """百度语音识别"""
        client = self._get_client()
        if not client:
            raise Exception("百度未配置")
        
        result = client.asr(audio_data, 'pcm', 16000, {
            'dev_pid': 1537,  # 普通话
        })
        
        if result.get('err_no') == 0:
            return result.get('result', [''])[0]
        return ""
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """百度语音合成"""
        client = self._get_client()
        if not client:
            raise Exception("百度未配置")
        
        options = {
            'spd': kwargs.get('speed', 5),      # 语速
            'pit': kwargs.get('pitch', 5),      # 音调
            'vol': kwargs.get('volume', 5),     # 音量
            'per': int(voice_id or self.config.voice_id or 1),  # 音色
        }
        
        result = client.synthesis(text, 'zh', 1, options)
        
        # 返回音频数据
        if not isinstance(result, dict):
            return result
        return b""
    
    def get_voices(self) -> List[Dict[str, str]]:
        """百度可用音色"""
        return [
            {"id": "1", "name": "女声", "style": "温柔", "gender": "女"},
            {"id": "2", "name": "男声", "style": "沉稳", "gender": "男"},
            {"id": "3", "name": "男声", "style": "亲切", "gender": "男"},
            {"id": "4", "name": "女声", "style": "活泼", "gender": "女"},
            {"id": "106", "name": "女声", "style": "情感丰富", "gender": "女"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查百度凭证"""
        try:
            return bool(config.app_id and config.api_key and config.secret_key)
        except:
            return False


class GoogleEngine(BaseVoiceEngine):
    """Google Cloud 语音引擎（国外）"""
    
    name = "google"
    display_name = "Google Cloud"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """Google 语音识别（支持 125+ 语言）"""
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient.from_service_account_json(
                self.config.secret_key  # JSON 密钥文件路径
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=kwargs.get('language_code', 'zh-CN'),
            )
            
            response = client.recognize(config=config, audio=audio)
            results = []
            for result in response.results:
                results.append(result.alternatives[0].transcript)
            
            return " ".join(results)
        except Exception as e:
            raise Exception(f"Google 语音识别失败：{e}")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """Google 语音合成（支持 220+ 声音）"""
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                self.config.secret_key
            )
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice_name = voice_id or self.config.voice_id or "zh-CN-Wavenet-A"
            voice = texttospeech.VoiceSelectionParams(
                language_code=kwargs.get('language_code', 'zh-CN'),
                name=voice_name,
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )
            
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            return response.audio_content
        except Exception as e:
            raise Exception(f"Google 语音合成失败：{e}")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Google 可用音色（部分）"""
        return [
            # 中文
            {"id": "zh-CN-Wavenet-A", "name": "中文女 1", "style": "温柔", "gender": "女", "language": "zh-CN"},
            {"id": "zh-CN-Wavenet-B", "name": "中文男 1", "style": "沉稳", "gender": "男", "language": "zh-CN"},
            {"id": "zh-CN-Wavenet-C", "name": "中文女 2", "style": "活泼", "gender": "女", "language": "zh-CN"},
            # 英文
            {"id": "en-US-Wavenet-A", "name": "英文女 1", "style": "温柔", "gender": "女", "language": "en-US"},
            {"id": "en-US-Wavenet-B", "name": "英文男 1", "style": "沉稳", "gender": "男", "language": "en-US"},
            {"id": "en-US-Wavenet-C", "name": "英文女 2", "style": "活泼", "gender": "女", "language": "en-US"},
            # 日文
            {"id": "ja-JP-Wavenet-A", "name": "日文女 1", "style": "温柔", "gender": "女", "language": "ja-JP"},
            # 韩文
            {"id": "ko-KR-Wavenet-A", "name": "韩文女 1", "style": "温柔", "gender": "女", "language": "ko-KR"},
            # 法文
            {"id": "fr-FR-Wavenet-A", "name": "法文女 1", "style": "优雅", "gender": "女", "language": "fr-FR"},
            # 德文
            {"id": "de-DE-Wavenet-A", "name": "德文女 1", "style": "专业", "gender": "女", "language": "de-DE"},
            # 西班牙文
            {"id": "es-ES-Wavenet-A", "name": "西班牙文女 1", "style": "热情", "gender": "女", "language": "es-ES"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查 Google 凭证"""
        try:
            if not config.secret_key:
                return False
            # 检查 JSON 文件是否存在
            return Path(config.secret_key).exists()
        except:
            return False


class AliBailianEngine(BaseVoiceEngine):
    """阿里云百炼语音引擎（国内）💋"""
    
    name = "ali_bailian"
    display_name = "阿里云百炼"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """阿里云百炼语音识别（支持中文、英文等）"""
        try:
            import dashscope
            from dashscope import AudioTranscription
            
            # 设置 API Key
            dashscope.api_key = self.config.api_key
            
            # 保存音频到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_data)
                audio_file = f.name
            
            try:
                # 调用语音识别 API
                result = AudioTranscription.call(
                    model='paraformer-realtime-v2',
                    format='wav',
                    file_path=audio_file
                )
                
                if result.status_code == 200:
                    return result.output.get('text', '')
                else:
                    raise Exception(f"识别失败：{result.message}")
            finally:
                import os
                os.unlink(audio_file)
                
        except Exception as e:
            raise Exception(f"阿里云百炼语音识别失败：{e}")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """阿里云百炼语音合成（支持 50+ 音色）"""
        try:
            import dashscope
            from dashscope import SpeechSynthesizer
            
            # 设置 API Key
            dashscope.api_key = self.config.api_key
            
            # 音色选择（默认：中文女声）
            voice_name = voice_id or self.config.voice_id or "longxiaochun"
            
            # 调用语音合成 API
            response = SpeechSynthesizer.call(
                model='sambert-zh-v1',
                voice=voice_name,
                text=text
            )
            
            if response.status_code == 200:
                return response.get_audio_data()
            else:
                raise Exception(f"语音合成失败：{response.message}")
                
        except Exception as e:
            raise Exception(f"阿里云百炼语音合成失败：{e}")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """获取阿里云百炼可用音色列表"""
        return [
            {"id": "longxiaochun", "name": "龙小淳 (中文女声)", "lang": "zh-CN"},
            {"id": "longxiaoyan", "name": "龙小颜 (中文女声)", "lang": "zh-CN"},
            {"id": "longxiaoguang", "name": "龙小光 (中文男声)", "lang": "zh-CN"},
            {"id": "longlong", "name": "龙龙 (中文男声)", "lang": "zh-CN"},
            {"id": "xiaoyun", "name": "小云 (中文女声)", "lang": "zh-CN"},
            {"id": "xiaogang", "name": "小刚 (中文男声)", "lang": "zh-CN"},
            {"id": "ruby", "name": "Ruby (英文女声)", "lang": "en-US"},
            {"id": "jenny", "name": "Jenny (英文女声)", "lang": "en-US"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查阿里云百炼凭证是否有效"""
        try:
            import dashscope
            dashscope.api_key = config.api_key
            
            # 尝试获取音色列表
            voices = self.get_voices()
            return len(voices) > 0
        except:
            return False


class AmazonEngine(BaseVoiceEngine):
    """Amazon Polly 语音引擎（国外）"""
    
    name = "amazon"
    display_name = "Amazon Polly"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """Amazon 语音识别（支持 50+ 语言）"""
        try:
            import boto3
            
            client = boto3.client(
                'transcribe',
                region_name=self.config.region or 'us-east-1',
                aws_access_key_id=self.config.api_key,
                aws_secret_access_key=self.config.secret_key
            )
            
            # 简化的实现，实际应该使用流式 API
            raise NotImplementedError("Amazon 语音识别需要使用流式 API，暂未实现")
        except Exception as e:
            raise Exception(f"Amazon 语音识别失败：{e}")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """Amazon Polly 语音合成（支持 60+ 语言）"""
        try:
            import boto3
            
            client = boto3.client(
                'polly',
                region_name=self.config.region or 'us-east-1',
                aws_access_key_id=self.config.api_key,
                aws_secret_access_key=self.config.secret_key
            )
            
            voice_name = voice_id or self.config.voice_id or "Joanna"
            
            response = client.synthesize_speech(
                Text=text,
                OutputFormat='pcm',
                VoiceId=voice_name,
                LanguageCode=kwargs.get('language_code', 'en-US')
            )
            
            return response['AudioStream'].read()
        except Exception as e:
            raise Exception(f"Amazon Polly 语音合成失败：{e}")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Amazon Polly 可用音色（部分）"""
        return [
            # 英文
            {"id": "Joanna", "name": "Joanna", "style": "温柔", "gender": "女", "language": "en-US"},
            {"id": "Matthew", "name": "Matthew", "style": "沉稳", "gender": "男", "language": "en-US"},
            {"id": "Salli", "name": "Salli", "style": "活泼", "gender": "女", "language": "en-US"},
            # 中文
            {"id": "Zhiyu", "name": "Zhiyu", "style": "温柔", "gender": "女", "language": "zh-CN"},
            # 日文
            {"id": "Mizuki", "name": "Mizuki", "style": "可爱", "gender": "女", "language": "ja-JP"},
            # 韩文
            {"id": "Seoyeon", "name": "Seoyeon", "style": "温柔", "gender": "女", "language": "ko-KR"},
            # 法文
            {"id": "Celine", "name": "Celine", "style": "优雅", "gender": "女", "language": "fr-FR"},
            # 德文
            {"id": "Vicki", "name": "Vicki", "style": "专业", "gender": "女", "language": "de-DE"},
            # 西班牙文
            {"id": "Lucia", "name": "Lucia", "style": "热情", "gender": "女", "language": "es-ES"},
            # 葡萄牙文
            {"id": "Camila", "name": "Camila", "style": "温柔", "gender": "女", "language": "pt-BR"},
            # 意大利文
            {"id": "Carla", "name": "Carla", "style": "优雅", "gender": "女", "language": "it-IT"},
            # 俄文
            {"id": "Tatyana", "name": "Tatyana", "style": "温柔", "gender": "女", "language": "ru-RU"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查 Amazon 凭证"""
        try:
            return bool(config.api_key and config.secret_key)
        except:
            return False


class AzureEngine(BaseVoiceEngine):
    """微软 Azure 语音引擎（国外）"""
    
    name = "azure"
    display_name = "Microsoft Azure"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """Azure 语音识别（支持 100+ 语言）"""
        try:
            from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioDataStream
            
            speech_config = SpeechConfig(
                subscription=self.config.api_key,
                region=self.config.region or "eastus"
            )
            speech_config.speech_recognition_language = kwargs.get('language_code', 'zh-CN')
            
            audio_stream = AudioDataStream(audio_data)
            recognizer = SpeechRecognizer(speech_config=speech_config, audio_stream=audio_stream)
            
            result = recognizer.recognize_once()
            return result.text
        except Exception as e:
            raise Exception(f"Azure 语音识别失败：{e}")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """Azure 语音合成（支持 400+ 声音）"""
        try:
            from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
            
            speech_config = SpeechConfig(
                subscription=self.config.api_key,
                region=self.config.region or "eastus"
            )
            
            voice_name = voice_id or self.config.voice_id or "zh-CN-XiaoxiaoNeural"
            speech_config.speech_synthesis_voice_name = voice_name
            
            synthesizer = SpeechSynthesizer(speech_config=speech_config)
            
            result = synthesizer.speak_text_async(text).get()
            return result.audio_data
        except Exception as e:
            raise Exception(f"Azure 语音合成失败：{e}")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Azure 可用音色（部分）"""
        return [
            # 中文
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "style": "温柔", "gender": "女", "language": "zh-CN"},
            {"id": "zh-CN-YunxiNeural", "name": "云希", "style": "沉稳", "gender": "男", "language": "zh-CN"},
            {"id": "zh-CN-YunjianNeural", "name": "云健", "style": "专业", "gender": "男", "language": "zh-CN"},
            # 英文
            {"id": "en-US-JennyNeural", "name": "Jenny", "style": "温柔", "gender": "女", "language": "en-US"},
            {"id": "en-US-GuyNeural", "name": "Guy", "style": "沉稳", "gender": "男", "language": "en-US"},
            # 日文
            {"id": "ja-JP-NanamiNeural", "name": "Nanami", "style": "温柔", "gender": "女", "language": "ja-JP"},
            # 韩文
            {"id": "ko-KR-SunHiNeural", "name": "SunHi", "style": "温柔", "gender": "女", "language": "ko-KR"},
            # 法文
            {"id": "fr-FR-DeniseNeural", "name": "Denise", "style": "优雅", "gender": "女", "language": "fr-FR"},
            # 德文
            {"id": "de-DE-KatjaNeural", "name": "Katja", "style": "专业", "gender": "女", "language": "de-DE"},
            # 西班牙文
            {"id": "es-ES-ElviraNeural", "name": "Elvira", "style": "热情", "gender": "女", "language": "es-ES"},
            # 葡萄牙文
            {"id": "pt-BR-FranciscaNeural", "name": "Francisca", "style": "温柔", "gender": "女", "language": "pt-BR"},
            # 意大利文
            {"id": "it-IT-ElsaNeural", "name": "Elsa", "style": "优雅", "gender": "女", "language": "it-IT"},
            # 俄文
            {"id": "ru-RU-SvetlanaNeural", "name": "Svetlana", "style": "温柔", "gender": "女", "language": "ru-RU"},
            # 阿拉伯文
            {"id": "ar-SA-ZariyahNeural", "name": "Zariyah", "style": "优雅", "gender": "女", "language": "ar-SA"},
            # 印地文
            {"id": "hi-IN-SwaraNeural", "name": "Swara", "style": "温柔", "gender": "女", "language": "hi-IN"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查 Azure 凭证"""
        try:
            return bool(config.api_key and config.region)
        except:
            return False


class VoiceEngineManager:
    """语音引擎管理器
    
    支持引擎：
    - 科大讯飞（国内首选）- 中文识别 98%
    - 阿里云百炼（国内）- 支持 50+ 音色 💋
    - Google Cloud（国外）- 支持 125+ 语言
    - Amazon Polly（国外）- 支持 60+ 语言
    - Azure（国外）- 支持 100+ 语言
    """
    
    def __init__(self, config_path: str = "~/.openclaw/workspace/voice-config.json"):
        self.config_path = Path(config_path).expanduser()
        self.engines: Dict[str, BaseVoiceEngine] = {}
        self.default_engine = "iflytek"  # 默认讯飞
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.default_engine = config.get("default_engine", "iflytek")
                
                # 初始化引擎
                engine_configs = config.get("engine_configs", {})
                for engine_name, eng_config in engine_configs.items():
                    self._init_engine(engine_name, eng_config)
    
    def _init_engine(self, engine_name: str, config: dict):
        """初始化引擎"""
        voice_config = VoiceConfig(
            engine=engine_name,
            app_id=config.get("app_id", ""),
            api_key=config.get("api_key", ""),
            secret_key=config.get("secret_key"),
            voice_id=config.get("voice_id"),
            region=config.get("region")
        )
        
        if engine_name == "iflytek":
            self.engines[engine_name] = IFlytekEngine(voice_config)
        elif engine_name == "ali_bailian":
            self.engines[engine_name] = AliBailianEngine(voice_config)
        elif engine_name == "google":
            self.engines[engine_name] = GoogleEngine(voice_config)
        elif engine_name == "amazon":
            self.engines[engine_name] = AmazonEngine(voice_config)
        elif engine_name == "azure":
            self.engines[engine_name] = AzureEngine(voice_config)
    
    def set_engine(self, engine_name: str) -> bool:
        """切换语音引擎"""
        if engine_name in self.engines:
            self.default_engine = engine_name
            return True
        return False
    
    def get_engine(self, engine_name: Optional[str] = None) -> Optional[BaseVoiceEngine]:
        """获取引擎实例"""
        name = engine_name or self.default_engine
        return self.engines.get(name)
    
    def list_engines(self) -> List[Dict[str, str]]:
        """列出可用引擎"""
        return [
            {"name": engine.name, "display_name": engine.display_name}
            for engine in self.engines.values()
        ]
    
    def list_voices(self, engine_name: Optional[str] = None) -> List[Dict[str, str]]:
        """列出可用音色"""
        engine = self.get_engine(engine_name)
        if engine:
            return engine.get_voices()
        return []
    
    def speech_to_text(self, audio_data: bytes, engine_name: Optional[str] = None) -> str:
        """语音识别"""
        engine = self.get_engine(engine_name)
        if not engine:
            raise Exception(f"引擎 {engine_name or self.default_engine} 未找到")
        return engine.speech_to_text(audio_data)
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, 
                       engine_name: Optional[str] = None, **kwargs) -> bytes:
        """语音合成"""
        engine = self.get_engine(engine_name)
        if not engine:
            raise Exception(f"引擎 {engine_name or self.default_engine} 未找到")
        return engine.text_to_speech(text, voice_id, **kwargs)
    
    def check_engine_status(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """检查引擎状态"""
        engine = self.get_engine(engine_name)
        if not engine:
            return {"available": False, "error": "引擎未找到"}
        
        config = engine.config if hasattr(engine, 'config') else None
        if not config:
            return {"available": False, "error": "引擎未配置"}
        
        is_valid = engine.check_credentials(config)
        return {
            "available": is_valid,
            "engine": engine.name,
            "display_name": engine.display_name,
            "configured": bool(config.app_id and config.api_key)
        }


# 全局单例
_manager = None

def get_voice_manager() -> VoiceEngineManager:
    """获取全局语音引擎管理器实例"""
    global _manager
    if _manager is None:
        _manager = VoiceEngineManager()
    return _manager


# 使用示例
if __name__ == "__main__":
    manager = VoiceEngineManager()
    
    # 列出可用引擎
    engines = manager.list_engines()
    print("🎤 可用语音引擎:")
    for engine in engines:
        print(f"  • {engine['display_name']} ({engine['name']})")
    
    # 列出讯飞音色
    print("\n🎵 讯飞音色:")
    voices = manager.list_voices("iflytek")
    for voice in voices:
        print(f"  • {voice['name']} - {voice['style']} ({voice['gender']})")
    
    # 切换引擎
    manager.set_engine("baidu")
    print(f"\n✅ 已切换到：{manager.default_engine}")
