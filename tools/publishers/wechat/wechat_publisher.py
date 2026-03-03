#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号推送工具
集成到灵犀 AI 系统 - 用于推送文章到公众号草稿箱
"""

import requests
import json
from pathlib import Path


class WeChatPublisher:
    """微信公众号发布器"""
    
    def __init__(self, appid: str, appsecret: str):
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
    
    def get_access_token(self) -> str:
        """获取 access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        response = requests.get(url)
        result = response.json()
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败：{result}")
    
    def upload_image(self, image_path: str) -> dict:
        """上传图片到素材库"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/material/add_material?access_token={self.access_token}&type=image"
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
        
        result = response.json()
        
        if "media_id" in result:
            print(f"✅ 图片上传成功：{result['media_id']}")
            return {
                "media_id": result["media_id"],
                "url": result.get("url", "")
            }
        else:
            print(f"❌ 图片上传失败：{result}")
            return None
    
    def upload_images(self, image_paths: list) -> list:
        """批量上传图片"""
        results = []
        for path in image_paths:
            if Path(path).exists():
                result = self.upload_image(path)
                if result:
                    results.append(result)
        return results
    
    def add_to_draft(self, title: str, content: str, thumb_media_id: str, 
                     author: str = "", digest: str = "") -> dict:
        """
        添加到草稿箱
        
        Args:
            title: 文章标题
            content: HTML 内容
            thumb_media_id: 封面图片 media_id
            author: 作者
            digest: 摘要
        
        Returns:
            dict: 包含 media_id 的结果
        """
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/draft/add?access_token={self.access_token}"
        
        data = {
            "article": {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 0,
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }
        }
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
        result = response.json()
        
        if "errcode" in result:
            if result["errcode"] == 0:
                print(f"✅ 推送成功！草稿箱 media_id: {result.get('media_id', 'N/A')}")
                return {"success": True, "media_id": result.get("media_id")}
            else:
                print(f"❌ 推送失败：{result}")
                return {"success": False, "error": result}
        else:
            print(f"❌ 推送失败：{result}")
            return {"success": False, "error": result}
    
    def publish_article(self, title: str, content: str, image_paths: list = None,
                        author: str = "", digest: str = "") -> dict:
        """
        完整发布流程：上传图片 → 推送草稿箱
        
        Args:
            title: 文章标题
            content: HTML 内容（图片用 media_id 或 URL）
            image_paths: 本地图片路径列表（可选）
            author: 作者
            digest: 摘要
        
        Returns:
            dict: 发布结果
        """
        print(f"📝 开始发布：{title}")
        
        # 上传封面图（如果有）
        thumb_media_id = None
        if image_paths and len(image_paths) > 0:
            first_image = image_paths[0]
            if Path(first_image).exists():
                result = self.upload_image(first_image)
                if result:
                    thumb_media_id = result["media_id"]
        
        if not thumb_media_id:
            print("⚠️ 警告：没有封面图，推送可能失败")
            return {"success": False, "error": "No cover image"}
        
        # 推送到草稿箱
        return self.add_to_draft(title, content, thumb_media_id, author, digest)


# 使用示例
if __name__ == "__main__":
    # 配置
    APPID = "wxd04bcd7faf50af4b"
    APPSECRET = "8d2d876ea7e1f6d07bd26653aac74697"
    
    # 创建发布器
    publisher = WeChatPublisher(APPID, APPSECRET)
    
    # 读取 HTML 内容
    with open("/tmp/lingxi_wechat_final.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 发布文章
    result = publisher.publish_article(
        title="灵犀 AI：一个人的公司如何靠 AI 调度系统实现高效运营",
        content=content,
        image_paths=["/tmp/org_chart.png"],
        author="丝嘉丽 AI 实验室",
        digest="在 OpenClaw 生态中，用 AI 组建你的专属企业帝国"
    )
    
    print(f"\n最终结果：{result}")
