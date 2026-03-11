#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Scrapling 爬虫执行器

🕷️ 基于 Scrapling 的自适应网页爬虫
✅ 自动绕过反爬虫
✅ 智能提取正文
✅ 支持 JavaScript 渲染
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import json


class ScraplingCrawler:
    """Scrapling 爬虫类"""
    
    def __init__(self):
        self.crawler = None
        self._init_crawler()
    
    def _init_crawler(self):
        """初始化 Scrapling"""
        try:
            from scrapling import Fetcher
            self.crawler = Fetcher(
                stealth=True,           # 隐身模式
                disable_resources=True, # 禁用资源加载（加速）
                timeout=30,             # 超时时间
            )
            print("✅ Scrapling 爬虫已初始化")
        except ImportError as e:
            print(f"❌ Scrapling 导入失败：{e}")
            self.crawler = None
    
    async def fetch(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        抓取网页
        
        Args:
            url: 目标 URL
            options: 抓取选项
        
        Returns:
            Dict: 抓取结果
        """
        if not self.crawler:
            return {
                "success": False,
                "error": "Scrapling 未初始化",
                "url": url
            }
        
        try:
            # 同步执行（在异步中运行）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._fetch_sync(url, options or {})
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def _fetch_sync(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """同步抓取实现（Scrapling 原生 API）"""
        try:
            # 执行抓取
            page = self.crawler.get(url)
            
            # 检查状态
            status = page.status
            if status != 200:
                return {
                    "success": False,
                    "error": f"HTTP {status}",
                    "url": url,
                    "status": status
                }
            
            # Scrapling 本身就是选择器，直接使用
            # 提取标题
            title_elem = page.find('title')
            title = title_elem.text if title_elem else "无标题"
            
            # 提取内容
            result = {
                "success": True,
                "url": url,
                "status": status,
                "title": title,
                "text": page.get_all_text(strip=True),
                "html": page.html_content,
                "links": self._extract_links(page),
                "images": self._extract_images(page),
                "metadata": {
                    "content_type": page.headers.get('content-type', ''),
                    "encoding": page.encoding,
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def _extract_links(self, soup) -> list:
        """提取链接"""
        try:
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    "text": link.get_text(strip=True),
                    "href": link.get('href', '')
                })
            return links[:50]  # 限制数量
        except:
            return []
    
    def _extract_images(self, soup) -> list:
        """提取图片"""
        try:
            images = []
            for img in soup.find_all('img'):
                images.append({
                    "src": img.get('src', ''),
                    "alt": img.get('alt', '')
                })
            return images[:20]  # 限制数量
        except:
            return []
    
    def extract_content(self, html: str, selector: str = None) -> Dict[str, Any]:
        """
        从 HTML 提取内容
        
        Args:
            html: HTML 内容
            selector: CSS 选择器（可选）
        
        Returns:
            Dict: 提取的内容
        """
        try:
            from scrapling import Parser
            soup = Parser(html)
            
            if selector:
                # 使用 CSS 选择器
                elements = soup.select(selector)
                content = [el.text for el in elements]
            else:
                # 自动提取正文
                content = soup.text
            
            return {
                "success": True,
                "content": content,
                "type": "text"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 全局爬虫实例
_crawler = None

def get_crawler() -> ScraplingCrawler:
    """获取爬虫实例"""
    global _crawler
    if _crawler is None:
        _crawler = ScraplingCrawler()
    return _crawler


# ==================== 灵犀执行器接口 ====================

class ScraplingExecutor:
    """灵犀 Scrapling 执行器"""
    
    def __init__(self):
        self.crawler = get_crawler()
    
    async def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行爬虫任务
        
        Args:
            input_data: 输入数据
                - url: 目标 URL（必需）
                - selector: CSS 选择器（可选）
                - extract_type: 提取类型 (text/links/images/all)
        
        Returns:
            Dict: 执行结果
        """
        url = input_data.get("url")
        selector = input_data.get("selector")
        extract_type = input_data.get("extract_type", "all")
        
        if not url:
            return {
                "success": False,
                "error": "缺少必需参数：url"
            }
        
        print(f"🕷️ 开始抓取：{url}")
        
        # 抓取网页
        result = await self.crawler.fetch(url)
        
        if not result["success"]:
            return result
        
        # 根据类型提取内容
        output = {
            "url": url,
            "title": result.get("title", ""),
            "status": result.get("status", 200)
        }
        
        if extract_type == "text":
            output["content"] = result.get("text", "")
        elif extract_type == "links":
            output["links"] = result.get("links", [])
        elif extract_type == "images":
            output["images"] = result.get("images", [])
        else:  # all
            output["content"] = result.get("text", "")
            output["links"] = result.get("links", [])[:20]
            output["images"] = result.get("images", [])[:10]
        
        output["success"] = True
        output["message"] = f"✅ 成功抓取：{result.get('title', '无标题')}"
        
        return output


# 便捷函数
def get_executor() -> ScraplingExecutor:
    """获取执行器实例"""
    return ScraplingExecutor()


# ==================== CLI 测试 ====================

if __name__ == "__main__":
    import sys
    
    async def test():
        """测试爬虫"""
        if len(sys.argv) < 2:
            print("用法：python3 scrapling_crawler.py <URL> [selector]")
            sys.exit(1)
        
        url = sys.argv[1]
        selector = sys.argv[2] if len(sys.argv) > 2 else None
        
        executor = get_executor()
        result = await executor.execute({
            "url": url,
            "selector": selector,
            "extract_type": "all"
        })
        
        if result["success"]:
            print(f"\n✅ 抓取成功！")
            print(f"标题：{result['title']}")
            print(f"状态：{result['status']}")
            print(f"链接数：{len(result.get('links', []))}")
            print(f"图片数：{len(result.get('images', []))}")
            print(f"内容长度：{len(result.get('content', ''))} 字符")
        else:
            print(f"\n❌ 抓取失败：{result.get('error', '未知错误')}")
    
    asyncio.run(test())
