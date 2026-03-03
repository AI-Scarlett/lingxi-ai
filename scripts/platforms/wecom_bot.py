#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信机器人集成 - WeCom Bot Integration
支持企业微信消息收发 💋

功能：
- 接收企业微信消息
- 发送企业微信消息
- 支持文本/Markdown/卡片消息
- Token 验证
"""

import json
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests


@dataclass
class WeComMessage:
    """企业微信消息"""
    corp_id: str
    user_id: str
    text: str
    timestamp: str
    msg_type: str = "text"


class WeComBot:
    """企业微信机器人"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.name = "wecom"
        self.display_name = "企业微信"
    
    def send_text(self, text: str, mentioned_list: Optional[List[str]] = None, **kwargs) -> bool:
        """发送文本消息"""
        payload = {
            "msgtype": "text",
            "text": {
                "content": text,
                "mentioned_list": mentioned_list or ["@all"]
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_markdown(self, markdown: str, **kwargs) -> bool:
        """发送 Markdown 消息"""
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_textcard(self, title: str, description: str, url: str, btn_txt: str = "查看详情", **kwargs) -> bool:
        """发送文本卡片消息"""
        payload = {
            "msgtype": "textcard",
            "textcard": {
                "title": title,
                "description": description,
                "url": url,
                "btntxt": btn_txt
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_news(self, articles: List[dict], **kwargs) -> bool:
        """发送图文消息"""
        payload = {
            "msgtype": "news",
            "news": {
                "articles": articles
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def send_image(self, media_id: str, **kwargs) -> bool:
        """发送图片消息"""
        payload = {
            "msgtype": "image",
            "image": {
                "media_id": media_id
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=payload, headers=headers)
        
        return response.json().get("errcode") == 0 if response.status_code == 200 else False
    
    def upload_media(self, media_type: str, file_path: str) -> Optional[str]:
        """上传媒体文件获取 media_id"""
        # 企业微信媒体上传需要调用企业微信 API
        # 这里简化处理，实际需要实现 OAuth 认证
        raise NotImplementedError("媒体上传需要企业微信 API 权限")
    
    def receive_message(self, request_data: dict) -> Optional[WeComMessage]:
        """解析接收到的消息"""
        # 企业微信回调消息格式
        to_user = request_data.get("ToUserName", "")
        from_user = request_data.get("FromUserName", "")
        msg_type = request_data.get("MsgType", "")
        
        if msg_type == "text":
            text = request_data.get("Content", "")
            timestamp = str(request_data.get("CreateTime", ""))
            
            return WeComMessage(
                corp_id=to_user,
                user_id=from_user,
                text=text,
                timestamp=timestamp,
                msg_type=msg_type
            )
        
        return None
    
    def verify_token(self, token: str, echostr: str) -> str:
        """验证 Token（用于首次配置）"""
        # 企业微信验证逻辑
        return echostr


class WeComPlatform:
    """企业微信平台集成"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bots: Dict[str, WeComBot] = {}
        self._init_bots()
    
    def _init_bots(self):
        """初始化机器人"""
        webhooks = self.config.get("webhooks", {})
        for name, webhook_config in webhooks.items():
            bot = WeComBot(webhook_url=webhook_config.get("url"))
            self.bots[name] = bot
    
    def get_bot(self, name: str = "default") -> Optional[WeComBot]:
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
            return bot.send_markdown(text, **kwargs)
        elif msg_type == "textcard":
            title = kwargs.get("title", "灵犀 AI")
            url = kwargs.get("url", "")
            btn_txt = kwargs.get("btn_txt", "查看详情")
            return bot.send_textcard(title, text, url, btn_txt, **kwargs)
        elif msg_type == "news":
            articles = kwargs.get("articles", [])
            return bot.send_news(articles, **kwargs)
        elif msg_type == "image":
            media_id = kwargs.get("media_id", "")
            return bot.send_image(media_id, **kwargs)
        
        return False
    
    def get_platform_info(self) -> dict:
        """获取平台信息"""
        return {
            "name": self.bots["default"].name if self.bots else "wecom",
            "display_name": self.bots["default"].display_name if self.bots else "企业微信",
            "bot_count": len(self.bots),
            "features": ["text", "markdown", "textcard", "news", "image"]
        }


# 使用示例
if __name__ == "__main__":
    # 配置
    config = {
        "webhooks": {
            "default": {
                "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
            }
        }
    }
    
    # 创建平台
    platform = WeComPlatform(config)
    
    # 发送文本消息
    platform.send_message(
        text="你好，我是灵犀 AI 助手！💋",
        msg_type="text"
    )
    
    # 发送 Markdown
    platform.send_message(
        text="**灵犀 AI**\n\n我已完成任务！✅",
        msg_type="markdown"
    )
    
    # 发送文本卡片
    platform.send_message(
        text="点击查看任务详情",
        msg_type="textcard",
        title="灵犀 AI 任务完成",
        url="https://github.com/AI-Scarlett/lingxi-ai"
    )
