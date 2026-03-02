#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像专家执行器 - 调用 scarlett-selfie 技能
"""

import os
import sys
from typing import Dict, Any

# 添加技能路径
SKILL_BASE = "/home/admin/.openclaw/skills/scarlett-selfie"

class ImageExpertExecutor:
    """图像专家执行器"""
    
    def __init__(self):
        self.name = "图像专家"
        self.model = "qwen-image-edit-plus"
        self.backup_model = "qwen-image-max"
        self.reference_image = "https://i.imgs.ovh/2026/02/24/y15adq.png"
        self.api_key = "sk-d84ce7d711c14942af76aa5722cbd037"
        self.endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行图像生成任务"""
        import aiohttp
        import json
        
        user_input = task_data.get("user_input", "")
        
        # 构建 prompt
        body_desc = "curvy voluptuous figure with full bust, hourglass body shape, plump hips and thighs, feminine realistic proportions"
        
        prompt = f"make a pic of this person, but {user_input}. {body_desc}. taking a mirror selfie, seductive pose, soft romantic lighting"
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": self.reference_image},
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {"n": 1}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if "output" in result:
                        # 从不同响应格式中提取图片URL
                        image_url = None
                        if "choices" in result["output"]:
                            image_url = result["output"]["choices"][0]["message"]["content"][0].get("image")
                        elif "results" in result["output"]:
                            image_url = result["output"]["results"][0].get("url")
                        
                        return {
                            "success": True,
                            "image_url": image_url,
                            "model_used": self.model,
                            "prompt": prompt
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get("message", "Unknown error"),
                            "model_used": self.model
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": self.model
            }
    
    def get_description(self) -> str:
        return "生成自拍照片，使用 qwen-image-edit-plus 模型"