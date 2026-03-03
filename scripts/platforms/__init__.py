#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台集成管理器 - Multi-Platform Manager
统一管理飞书、钉钉、企业微信等平台 💋

支持平台：
- 飞书 (Feishu)
- 钉钉 (DingTalk)
- 企业微信 (WeCom)
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

from .feishu_bot import FeishuPlatform
from .dingtalk_bot import DingTalkPlatform
from .wecom_bot import WeComPlatform


@dataclass
class PlatformMessage:
    """统一消息格式"""
    platform: str
    chat_id: str
    user_id: str
    text: str
    msg_type: str
    timestamp: str
    metadata: Optional[Dict] = None


class MultiPlatformManager:
    """多平台管理器"""
    
    def __init__(self, config_path: str = "~/.openclaw/workspace/platform-config.json"):
        self.config_path = Path(config_path).expanduser()
        self.platforms: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
                # 初始化各平台
                if "feishu" in config:
                    self.platforms["feishu"] = FeishuPlatform(config["feishu"])
                
                if "dingtalk" in config:
                    self.platforms["dingtalk"] = DingTalkPlatform(config["dingtalk"])
                
                if "wecom" in config:
                    self.platforms["wecom"] = WeComPlatform(config["wecom"])
    
    def get_platform(self, platform_name: str) -> Optional[Any]:
        """获取平台实例"""
        return self.platforms.get(platform_name)
    
    def list_platforms(self) -> List[Dict[str, str]]:
        """列出所有平台"""
        result = []
        for name, platform in self.platforms.items():
            info = platform.get_platform_info()
            result.append(info)
        return result
    
    def send_message(self,
                     platform_name: str,
                     text: str,
                     msg_type: str = "text",
                     **kwargs) -> bool:
        """
        发送消息到指定平台
        
        Args:
            platform_name: 平台名称 (feishu/dingtalk/wecom)
            text: 消息内容
            msg_type: 消息类型 (text/markdown/link/card 等)
            **kwargs: 其他参数
            
        Returns:
            是否发送成功
        """
        platform = self.get_platform(platform_name)
        if not platform:
            return False
        
        return platform.send_message(text, msg_type=msg_type, **kwargs)
    
    def broadcast(self, text: str, msg_type: str = "text", **kwargs) -> Dict[str, bool]:
        """
        广播消息到所有平台
        
        Args:
            text: 消息内容
            msg_type: 消息类型
            **kwargs: 其他参数
            
        Returns:
            各平台发送结果
        """
        results = {}
        
        for platform_name in self.platforms.keys():
            success = self.send_message(platform_name, text, msg_type, **kwargs)
            results[platform_name] = success
        
        return results
    
    def send_to_all(self, 
                    text: str,
                    platforms: Optional[List[str]] = None,
                    **kwargs) -> Dict[str, bool]:
        """
        发送到指定平台列表
        
        Args:
            text: 消息内容
            platforms: 平台列表，None 表示所有平台
            **kwargs: 其他参数
            
        Returns:
            各平台发送结果
        """
        results = {}
        target_platforms = platforms or list(self.platforms.keys())
        
        for platform_name in target_platforms:
            success = self.send_message(platform_name, text, **kwargs)
            results[platform_name] = success
        
        return results


# 全局单例
_manager = None

def get_platform_manager() -> MultiPlatformManager:
    """获取全局多平台管理器实例"""
    global _manager
    if _manager is None:
        _manager = MultiPlatformManager()
    return _manager


# 使用示例
if __name__ == "__main__":
    manager = MultiPlatformManager()
    
    # 列出所有平台
    platforms = manager.list_platforms()
    print("📱 可用平台:")
    for p in platforms:
        print(f"  • {p['display_name']} ({p['name']}) - {p['bot_count']} 个机器人")
    
    # 发送到单个平台
    manager.send_message(
        platform_name="feishu",
        text="你好，我是灵犀 AI 助手！💋",
        msg_type="text"
    )
    
    # 广播到所有平台
    results = manager.broadcast(
        text="任务完成通知！✅",
        msg_type="text"
    )
    print(f"\n广播结果：{results}")
    
    # 发送到指定平台
    results = manager.send_to_all(
        text="灵犀 AI 已上线",
        platforms=["feishu", "dingtalk"],
        msg_type="markdown"
    )
    print(f"定向发送结果：{results}")
