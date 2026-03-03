#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号推送工具 v2 - 深度调试版
研究所有可能的推送方式
"""

import requests
import json
from pathlib import Path


class WeChatPublisherV2:
    """微信公众号发布器 v2"""
    
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
            print(f"✅ Access Token: {self.access_token[:30]}...")
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败：{result}")
    
    def check_api_permissions(self):
        """检查 API 权限"""
        if not self.access_token:
            self.get_access_token()
        
        print("\n🔍 检查 API 权限...")
        
        # 尝试获取素材列表
        url = f"{self.base_url}/material/batchget_material?access_token={self.access_token}"
        data = {
            "type": "image",
            "offset": 0,
            "count": 1
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"素材列表 API: {result}")
        
        # 尝试获取已保存的草稿
        url = f"{self.base_url}/draft/batchget?access_token={self.access_token}"
        data = {
            "offset": 0,
            "count": 1,
            "no_content": 1
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"草稿箱 API: {result}")
        
        return result
    
    def upload_image(self, image_path: str) -> dict:
        """上传图片"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/material/add_material?access_token={self.access_token}&type=image"
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
        
        result = response.json()
        
        if "media_id" in result:
            print(f"✅ 图片上传成功：{result['media_id']}")
            return result
        else:
            print(f"❌ 图片上传失败：{result}")
            return None
    
    def test_draft_with_minimal_content(self, thumb_media_id: str):
        """用最小化内容测试草稿箱 API"""
        if not self.access_token:
            self.get_access_token()
        
        print("\n🧪 测试 1: 最小化内容...")
        
        url = f"{self.base_url}/draft/add?access_token={self.access_token}"
        
        # 最简单的 HTML
        content = "<p>测试</p>"
        
        data = {
            "article": {
                "title": "测试",
                "content": content,
                "thumb_media_id": thumb_media_id
            }
        }
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
        result = response.json()
        
        print(f"最小化测试结果：{result}")
        
        if result.get("errcode") == 0:
            print("✅ 最小化测试成功！")
            return True
        else:
            print(f"❌ 错误码：{result.get('errcode')}, 错误信息：{result.get('errmsg')}")
            return False
    
    def test_with_free_draft_api(self, thumb_media_id: str):
        """尝试用 free_publish 接口"""
        if not self.access_token:
            self.get_access_token()
        
        print("\n🧪 测试 2: free_publish 接口...")
        
        url = f"{self.base_url}/freepublish/add?access_token={self.access_token}"
        
        data = {
            "articles": [
                {
                    "title": "测试",
                    "thumb_media_id": thumb_media_id,
                    "author": "测试",
                    "digest": "测试",
                    "show_cover_pic": 1,
                    "content": "<p>测试内容</p>",
                    "content_source_url": ""
                }
            ]
        }
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
        result = response.json()
        
        print(f"free_publish 测试结果：{result}")
        return result
    
    def test_update_news(self, thumb_media_id: str):
        """尝试用 update_news 接口"""
        if not self.access_token:
            self.get_access_token()
        
        print("\n🧪 测试 3: 先创建临时素材...")
        
        # 临时素材接口
        url = f"{self.base_url}/media/upload?access_token={self.access_token}&type=image"
        
        with open('/tmp/org_chart.png', 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
        
        temp_result = response.json()
        print(f"临时上传结果：{temp_result}")
        
        if "media_id" in temp_result:
            temp_media_id = temp_result["media_id"]
            
            # 尝试用图文消息接口
            print("\n尝试 mpnews 接口...")
            url = f"{self.base_url}/media/uploadnews?access_token={self.access_token}"
            
            data = {
                "articles": [
                    {
                        "title": "灵犀 AI 测试",
                        "thumb_media_id": temp_media_id,
                        "author": "丝嘉丽",
                        "digest": "测试",
                        "show_cover_pic": "1",
                        "content": "<p>测试内容</p>",
                        "content_source_url": ""
                    }
                ]
            }
            
            headers = {"Content-Type": "application/json; charset=utf-8"}
            response = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
            news_result = response.json()
            
            print(f"mpnews 结果：{news_result}")
            return news_result
        
        return None
    
    def full_test(self):
        """完整测试流程"""
        print("="*70)
        print("🔬 微信公众号 API 深度测试")
        print("="*70)
        
        # 获取 token
        self.get_access_token()
        
        # 检查权限
        self.check_api_permissions()
        
        # 上传封面图
        print("\n📤 上传封面图...")
        cover_result = self.upload_image('/tmp/org_chart.png')
        
        if not cover_result:
            print("❌ 封面图上传失败，终止测试")
            return
        
        thumb_media_id = cover_result["media_id"]
        
        # 测试 1: 最小化内容
        test1 = self.test_draft_with_minimal_content(thumb_media_id)
        
        if not test1:
            # 测试 2: free_publish
            test2 = self.test_with_free_draft_api(thumb_media_id)
            
            # 测试 3: mpnews
            test3 = self.test_update_news(thumb_media_id)
        
        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)


if __name__ == "__main__":
    APPID = "wxd04bcd7faf50af4b"
    APPSECRET = "8d2d876ea7e1f6d07bd26653aac74697"
    
    publisher = WeChatPublisherV2(APPID, APPSECRET)
    publisher.full_test()
