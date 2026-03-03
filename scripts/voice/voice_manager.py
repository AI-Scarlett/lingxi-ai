#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音引擎管理器 - Voice Engine Manager
支持多个国内语音服务，用户可自由切换 💋

支持的引擎：
- 科大讯飞（首选）
- 百度语音
- 阿里云
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


class AliyunEngine(BaseVoiceEngine):
    """阿里云语音引擎"""
    
    name = "aliyun"
    display_name = "阿里云"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """阿里云语音识别"""
        # TODO: 实现阿里云 API 调用
        raise NotImplementedError("阿里云语音识别暂未实现")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """阿里云语音合成"""
        # TODO: 实现阿里云 API 调用
        raise NotImplementedError("阿里云语音合成暂未实现")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """阿里云可用音色"""
        return [
            {"id": "xiaoyun", "name": "小云", "style": "温柔", "gender": "女"},
            {"id": "yuer", "name": "悦儿", "style": "可爱", "gender": "女"},
            {"id": "ruoxi", "name": "若兮", "style": "情感", "gender": "女"},
            {"id": "siqi", "name": "思琪", "style": "知性", "gender": "女"},
            {"id": "aiqi", "name": "艾琪", "style": "AI 感", "gender": "女"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查阿里云凭证"""
        try:
            return bool(config.app_id and config.api_key and config.secret_key)
        except:
            return False


class TencentEngine(BaseVoiceEngine):
    """腾讯云语音引擎"""
    
    name = "tencent"
    display_name = "腾讯云"
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """腾讯云语音识别"""
        # TODO: 实现腾讯云 API 调用
        raise NotImplementedError("腾讯云语音识别暂未实现")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """腾讯云语音合成"""
        # TODO: 实现腾讯云 API 调用
        raise NotImplementedError("腾讯云语音合成暂未实现")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """腾讯云可用音色"""
        return [
            {"id": "1001", "name": "女声", "style": "温柔", "gender": "女"},
            {"id": "1002", "name": "男声", "style": "沉稳", "gender": "男"},
            {"id": "1003", "name": "女声", "style": "活泼", "gender": "女"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查腾讯云凭证"""
        try:
            return bool(config.app_id and config.api_key and config.secret_key)
        except:
            return False


class AzureEngine(BaseVoiceEngine):
    """微软 Azure 语音引擎（国内版）"""
    
    name = "azure"
    display_name = "微软 Azure"
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config
        self._client = None
    
    def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """Azure 语音识别"""
        # TODO: 实现 Azure API 调用
        raise NotImplementedError("Azure 语音识别暂未实现")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """Azure 语音合成"""
        # TODO: 实现 Azure API 调用
        raise NotImplementedError("Azure 语音合成暂未实现")
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Azure 可用音色"""
        return [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "style": "温柔", "gender": "女"},
            {"id": "zh-CN-YunxiNeural", "name": "云希", "style": "沉稳", "gender": "男"},
            {"id": "zh-CN-YunjianNeural", "name": "云健", "style": "专业", "gender": "男"},
        ]
    
    def check_credentials(self, config: VoiceConfig) -> bool:
        """检查 Azure 凭证"""
        try:
            return bool(config.app_id and config.api_key)
        except:
            return False


class VoiceEngineManager:
    """语音引擎管理器"""
    
    def __init__(self, config_path: str = "~/.openclaw/workspace/voice-config.json"):
        self.config_path = Path(config_path).expanduser()
        self.engines: Dict[str, BaseVoiceEngine] = {}
        self.default_engine = "iflytek"
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
        elif engine_name == "baidu":
            self.engines[engine_name] = BaiduEngine(voice_config)
        elif engine_name == "aliyun":
            self.engines[engine_name] = AliyunEngine(voice_config)
        elif engine_name == "tencent":
            self.engines[engine_name] = TencentEngine(voice_config)
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
