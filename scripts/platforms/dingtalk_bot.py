#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人集成 - DingTalk Bot Integration
支持钉钉消息收发 💋

功能：
- 接收钉钉消息
- 发送钉钉消息
- 支持文本/Markdown/卡片消息
- 签名验证
"""

import json
import hmac
import hashlib
import base64
import time
import urllib.parse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests


@dataclass
class DingTalkMessage:
    """钉钉消息"""
    conversation_id: str
    sender_id: str
    text: str
    timestamp: str
    msg_type: str = "text"


class DingTalkBot:
    """钉钉机器人"""
    
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self.name = "dingtalk"
        self.display_name = "钉钉"
    
    def _generate_sign(self, timestamp: str) -> str:
        """生成签名"""
        if not self.secret:
            return ""
        
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f"{timestamp}\n{self.secret}"
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        hmac_code = hmac.new(
            secret_enc,
            string_to_sign_enc,
            digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode('utf-8'))
        return sign
    
    def send_text(self, text: str, mentioned_all: bool = False, **kwargs) -> bool:
        """发送文本消息"""
        payload = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "isAtAll": mentioned_all
            }
        }
        
        # 添加签名
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)
        
        url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_markdown(self, title: str, markdown: str, **kwargs) -> bool:
        """发送 Markdown 消息"""
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown
            }
        }
        
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)
        
        url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_link(self, title: str, text: str, message_url: str, pic_url: str = "", **kwargs) -> bool:
        """发送链接消息"""
        payload = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url
            }
        }
        
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)
        
        url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_card(self, card_json: dict, **kwargs) -> bool:
        """发送卡片消息"""
        payload = {
            "msgtype": "interactive",
            "card": card_json
        }
        
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)
        
        url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def receive_message(self, request_data: dict) -> Optional[DingTalkMessage]:
        """解析接收到的消息"""
        # 钉钉回调消息格式
        chatbot_id = request_data.get("chatbotId", "")
        conversation_id = request_data.get("conversationId", "")
        sender_id = request_data.get("senderId", "")
        text = request_data.get("text", {}).get("content", "")
        timestamp = request_data.get("timestamp", "")
        
        return DingTalkMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            text=text,
            timestamp=timestamp,
            msg_type="text"
        )
    
    def verify_signature(self, timestamp: str, sign: str) -> bool:
        """验证签名"""
        if not self.secret:
            return True
        
        expected_sign = self._generate_sign(timestamp)
        return hmac.compare_digest(sign, expected_sign)


class DingTalkPlatform:
    """钉钉平台集成"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bots: Dict[str, DingTalkBot] = {}
        self._init_bots()
    
    def _init_bots(self):
        """初始化机器人"""
        webhooks = self.config.get("webhooks", {})
        for name, webhook_config in webhooks.items():
            bot = DingTalkBot(
                webhook_url=webhook_config.get("url"),
                secret=webhook_config.get("secret")
            )
            self.bots[name] = bot
    
    def get_bot(self, name: str = "default") -> Optional[DingTalkBot]:
        """获取机器人"""
        return self.bots.get(name)
    
    def send_message(self, 
                     text: str, 
                     bot_name: str = "default",
                     msg_type: str = "text",
                     **kwargs) -> bool:
        """发送消息"""
        bot = self.get_bot(bot_name)
        if not bot:
            return False
        
        if msg_type == "text":
            return bot.send_text(text, **kwargs)
        elif msg_type == "markdown":
            title = kwargs.get("title", "灵犀 AI")
            return bot.send_markdown(title, text, **kwargs)
        elif msg_type == "link":
            title = kwargs.get("title", "")
            message_url = kwargs.get("url", "")
            pic_url = kwargs.get("pic_url", "")
            return bot.send_link(title, text, message_url, pic_url, **kwargs)
        elif msg_type == "card":
            return bot.send_card(text, **kwargs)  # text 这里是 card_json
        
        return False
    
    def get_platform_info(self) -> dict:
        """获取平台信息"""
        return {
            "name": self.bots["default"].name if self.bots else "dingtalk",
            "display_name": self.bots["default"].display_name if self.bots else "钉钉",
            "bot_count": len(self.bots),
            "features": ["text", "markdown", "link", "card"]
        }


# 使用示例
if __name__ == "__main__":
    # 配置
    config = {
        "webhooks": {
            "default": {
                "url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
                "secret": "YOUR_SECRET"
            }
        }
    }
    
    # 创建平台
    platform = DingTalkPlatform(config)
    
    # 发送文本消息
    platform.send_message(
        text="你好，我是灵犀 AI 助手！💋",
        msg_type="text"
    )
    
    # 发送 Markdown
    platform.send_message(
        text="**灵犀 AI**\n\n我已完成任务！✅",
        msg_type="markdown",
        title="任务完成"
    )
    
    # 发送链接
    platform.send_message(
        text="点击查看详细内容",
        msg_type="link",
        title="灵犀 AI 任务",
        url="https://github.com/AI-Scarlett/lingxi-ai",
        pic_url=""
    )
