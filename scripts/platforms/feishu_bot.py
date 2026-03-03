#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人集成 - Feishu Bot Integration
支持飞书消息收发 💋

功能：
- 接收飞书消息
- 发送飞书消息
- 支持文本/图片/卡片消息
- 自动回复
"""

import json
import hmac
import hashlib
import base64
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import requests


@dataclass
class FeishuMessage:
    """飞书消息"""
    chat_id: str
    user_id: str
    text: str
    timestamp: str
    message_id: str
    msg_type: str = "text"


class FeishuBot:
    """飞书机器人"""
    
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self.name = "feishu"
        self.display_name = "飞书"
    
    def _generate_sign(self, timestamp: str) -> str:
        """生成签名"""
        if not self.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    def send_text(self, chat_id: str, text: str, **kwargs) -> bool:
        """发送文本消息"""
        payload = {
            "chat_id": chat_id,
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        
        # 添加签名
        timestamp = str(int(time.time()))
        sign = self._generate_sign(timestamp)
        
        headers = {"Content-Type": "application/json"}
        if sign:
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers=headers
        )
        
        return response.status_code == 200
    
    def send_markdown(self, chat_id: str, markdown: str, **kwargs) -> bool:
        """发送 Markdown 消息"""
        payload = {
            "chat_id": chat_id,
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "灵犀 AI"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown
                    }
                ]
            }
        }
        
        timestamp = str(int(time.time()))
        sign = self._generate_sign(timestamp)
        
        headers = {"Content-Type": "application/json"}
        if sign:
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers=headers
        )
        
        return response.status_code == 200
    
    def send_image(self, chat_id: str, image_key: str, **kwargs) -> bool:
        """发送图片消息"""
        payload = {
            "chat_id": chat_id,
            "msg_type": "image",
            "content": {
                "image_key": image_key
            }
        }
        
        timestamp = str(int(time.time()))
        sign = self._generate_sign(timestamp)
        
        headers = {"Content-Type": "application/json"}
        if sign:
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers=headers
        )
        
        return response.status_code == 200
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片获取 image_key"""
        # 飞书图片上传需要调用飞书开放平台 API
        # 这里简化处理，实际需要实现 OAuth 认证
        raise NotImplementedError("图片上传需要飞书开放平台 API 权限")
    
    def receive_message(self, request_data: dict) -> FeishuMessage:
        """解析接收到的消息"""
        # 飞书回调消息格式
        challenge = request_data.get("challenge")
        if challenge:
            # 验证回调
            return None
        
        event = request_data.get("event", {})
        message = event.get("message", {})
        
        return FeishuMessage(
            chat_id=message.get("chat_id", ""),
            user_id=message.get("sender", {}).get("sender_id", {}).get("user_id", ""),
            text=message.get("content", "{}"),
            timestamp=message.get("create_time", ""),
            message_id=message.get("message_id", ""),
            msg_type=message.get("message_type", "text")
        )
    
    def verify_signature(self, timestamp: str, sign: str) -> bool:
        """验证签名"""
        if not self.secret:
            return True
        
        expected_sign = self._generate_sign(timestamp)
        return hmac.compare_digest(sign, expected_sign)


class FeishuPlatform:
    """飞书平台集成"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bots: Dict[str, FeishuBot] = {}
        self._init_bots()
    
    def _init_bots(self):
        """初始化机器人"""
        webhooks = self.config.get("webhooks", {})
        for name, webhook_config in webhooks.items():
            bot = FeishuBot(
                webhook_url=webhook_config.get("url"),
                secret=webhook_config.get("secret")
            )
            self.bots[name] = bot
    
    def get_bot(self, name: str = "default") -> Optional[FeishuBot]:
        """获取机器人"""
        return self.bots.get(name)
    
    def send_message(self, 
                     chat_id: str, 
                     text: str, 
                     bot_name: str = "default",
                     msg_type: str = "text",
                     **kwargs) -> bool:
        """发送消息"""
        bot = self.get_bot(bot_name)
        if not bot:
            return False
        
        if msg_type == "text":
            return bot.send_text(chat_id, text, **kwargs)
        elif msg_type == "markdown":
            return bot.send_markdown(chat_id, text, **kwargs)
        elif msg_type == "image":
            return bot.send_image(chat_id, text, **kwargs)  # text 这里是 image_key
        
        return False
    
    def get_platform_info(self) -> dict:
        """获取平台信息"""
        return {
            "name": self.bots["default"].name if self.bots else "feishu",
            "display_name": self.bots["default"].display_name if self.bots else "飞书",
            "bot_count": len(self.bots),
            "features": ["text", "markdown", "image", "card"]
        }


# 使用示例
if __name__ == "__main__":
    # 配置
    config = {
        "webhooks": {
            "default": {
                "url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK",
                "secret": "YOUR_SECRET"
            }
        }
    }
    
    # 创建平台
    platform = FeishuPlatform(config)
    
    # 发送消息
    platform.send_message(
        chat_id="oc_abc123",
        text="你好，我是灵犀 AI 助手！💋",
        msg_type="text"
    )
    
    # 发送 Markdown
    platform.send_message(
        chat_id="oc_abc123",
        text="**灵犀 AI**\n\n我已完成任务！✅",
        msg_type="markdown"
    )
