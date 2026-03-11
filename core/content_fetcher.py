#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀智能内容获取器 - 基于 Scrapling

特性：
- 自适应解析（网站变化后自动重新定位）
- 绕过反爬（Cloudflare Turnstile 等）
- 智能缓存（避免重复请求）
- 多种 Fetcher（HTTP/Stealth/Dynamic）
- 支持微信文章等特殊页面

Usage:
    from core.content_fetcher import SmartContentFetcher
    
    fetcher = SmartContentFetcher()
    content = await fetcher.fetch_url("https://mp.weixin.qq.com/s/xxx")
"""

import time
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Scrapling 导入
try:
    from scrapling.fetchers import (
        Fetcher,
        AsyncFetcher,
        StealthyFetcher,
        DynamicFetcher
    )
    from scrapling.parser import Selector
    SCRAPPING_AVAILABLE = True
except ImportError:
    SCRAPPING_AVAILABLE = False
    print("⚠️ Scrapling 未安装，部分功能受限")


class SmartContentFetcher:
    """智能内容获取器"""
    
    def __init__(self, workspace_path: str = None):
        """
        初始化内容获取器
        
        Args:
            workspace_path: 工作目录路径（用于缓存）
        """
        self.workspace = Path(workspace_path) if workspace_path else Path.home() / ".openclaw" / "workspace"
        self.cache_dir = self.workspace / ".lingxi" / "content_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Scrapling 状态
        if SCRAPPING_AVAILABLE:
            # 启用自适应模式
            StealthyFetcher.adaptive = True
            
            # 初始化 Fetchers
            self.stealth_fetcher = StealthyFetcher()
            self.async_fetcher = AsyncFetcher()
            self.dynamic_fetcher = DynamicFetcher()
            print("✅ Scrapling 已就绪 - 自适应模式已启用")
        else:
            self.stealth_fetcher = None
            self.async_fetcher = None
            self.dynamic_fetcher = None
        
        # 缓存管理
        self.cache_ttl = 3600  # 缓存有效期 1 小时
        self.max_cache_size = 100  # 最多缓存 100 个页面
    
    async def fetch_url(self, url: str, 
                       adaptive: bool = True,
                       bypass_bot: bool = True,
                       use_cache: bool = True,
                       timeout: int = 30) -> Dict[str, Any]:
        """
        智能获取网页内容
        
        Args:
            url: 目标 URL
            adaptive: 自适应模式（网站变化后自动重新定位）
            bypass_bot: 绕过反爬虫（Cloudflare 等）
            use_cache: 使用缓存（避免重复请求）
            timeout: 超时时间（秒）
        
        Returns:
            {
                "success": True/False,
                "content": "页面文本内容",
                "html": "页面 HTML",
                "title": "页面标题",
                "url": "最终 URL（可能有重定向）",
                "from_cache": True/False,
                "error": "错误信息（如果有）"
            }
        """
        # 检查缓存
        if use_cache:
            cached = self._get_from_cache(url)
            if cached:
                return {
                    "success": True,
                    "content": cached["content"],
                    "html": cached.get("html", ""),
                    "title": cached.get("title", ""),
                    "url": url,
                    "from_cache": True,
                    "cached_at": cached.get("cached_at")
                }
        
        # Scrapling 不可用时降级到基础请求
        if not SCRAPPING_AVAILABLE:
            return await self._fallback_fetch(url)
        
        try:
            # 根据 URL 类型选择 Fetcher
            if "weixin.qq.com" in url or "mp.weixin.qq.com" in url:
                # 微信文章需要特殊处理
                page = await self._fetch_wechat(url, timeout)
            elif bypass_bot:
                # 有反爬的网站使用 StealthyFetcher
                page = await self.stealth_fetcher.fetch_async(
                    url,
                    headless=True,
                    network_idle=True,
                    timeout=timeout * 1000
                )
            else:
                # 普通网站使用 AsyncFetcher
                page = await self.async_fetcher.fetch_async(
                    url,
                    timeout=timeout * 1000
                )
            
            # 提取内容
            result = {
                "success": True,
                "content": page.get_all_text(ignore_tags=('script', 'style')),
                "html": page.html_content,
                "title": page.find('title').text if page.find('title') else "",
                "url": url,
                "from_cache": False
            }
            
            # 保存到缓存
            if use_cache:
                self._save_to_cache(url, result)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "html": "",
                "title": "",
                "url": url,
                "from_cache": False,
                "error": str(e)
            }
    
    async def _fetch_wechat(self, url: str, timeout: int = 30) -> Any:
        """
        特殊处理微信文章（可能需要绕过反爬）
        
        Args:
            url: 微信文章 URL
            timeout: 超时时间
        
        Returns:
            Scrapling page 对象
        """
        # 尝试使用 StealthyFetcher
        try:
            page = await self.stealth_fetcher.fetch_async(
                url,
                headless=True,
                network_idle=True,
                timeout=timeout * 1000
            )
            return page
        except Exception as e:
            # 如果失败，尝试 DynamicFetcher（完整浏览器）
            print(f"⚠️ StealthyFetcher 失败，尝试 DynamicFetcher: {e}")
            page = await self.dynamic_fetcher.fetch_async(
                url,
                headless=True,
                timeout=timeout * 1000
            )
            return page
    
    async def _fallback_fetch(self, url: str) -> Dict[str, Any]:
        """
        Scrapling 不可用时的降级方案
        
        Args:
            url: 目标 URL
        
        Returns:
            基础内容字典
        """
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    html = await response.text()
                    
                    # 简单提取标题
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    title = title_match.group(1) if title_match else ""
                    
                    # 提取纯文本（去除 HTML 标签）
                    content = re.sub(r'<[^>]+>', '', html)
                    
                    return {
                        "success": True,
                        "content": content,
                        "html": html,
                        "title": title,
                        "url": url,
                        "from_cache": False
                    }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "html": "",
                "title": "",
                "url": url,
                "from_cache": False,
                "error": str(e)
            }
    
    def extract_with_selector(self, html: str, selector: str, 
                             selector_type: str = "css",
                             adaptive: bool = True) -> list:
        """
        使用选择器提取内容
        
        Args:
            html: HTML 内容
            selector: CSS 或 XPath 选择器
            selector_type: "css" 或 "xpath"
            adaptive: 自适应模式（找不到时尝试相似元素）
        
        Returns:
            提取的内容列表
        """
        if not SCRAPPING_AVAILABLE:
            return []
        
        page = Selector(html)
        
        try:
            if selector_type == "css":
                elements = page.css(selector)
            elif selector_type == "xpath":
                elements = page.xpath(selector)
            else:
                elements = page.css(selector)
            
            # 提取文本
            results = [el.get_all_text() for el in elements]
            
            # 自适应模式：如果没找到，尝试找相似元素
            if adaptive and not results:
                # 尝试找相似元素
                target = page.find_by_regex(selector.split('.')[-1] if '.' in selector else selector)
                if target:
                    similar = target.find_similar()
                    results = [el.get_all_text() for el in similar]
            
            return results
            
        except Exception as e:
            print(f"⚠️ 选择器提取失败：{e}")
            return []
    
    def _get_cache_key(self, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_from_cache(self, url: str) -> Optional[Dict]:
        """从缓存获取"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            cached = json.loads(cache_file.read_text(encoding='utf-8'))
            
            # 检查是否过期
            if time.time() - cached.get("timestamp", 0) > self.cache_ttl:
                cache_file.unlink()
                return None
            
            return cached
            
        except Exception:
            return None
    
    def _save_to_cache(self, url: str, result: Dict):
        """保存到缓存"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            "url": url,
            "content": result.get("content", ""),
            "html": result.get("html", ""),
            "title": result.get("title", ""),
            "timestamp": time.time(),
            "cached_at": datetime.now().isoformat()
        }
        
        cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # 清理过期缓存
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            # 按时间排序，删除最旧的
            if len(cache_files) > self.max_cache_size:
                cache_files.sort(key=lambda f: f.stat().st_mtime)
                for old_file in cache_files[:len(cache_files) - self.max_cache_size]:
                    old_file.unlink()
        except Exception:
            pass
    
    def clear_cache(self):
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print(f"✅ 已清空缓存：{self.cache_dir}")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "count": len(cache_files),
            "size_bytes": total_size,
            "size_mb": round(total_size / 1024 / 1024, 2),
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl
        }


# 全局实例
_fetcher = None

def get_content_fetcher(workspace_path: str = None) -> SmartContentFetcher:
    """获取内容获取器实例"""
    global _fetcher
    
    if _fetcher is None:
        workspace = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        _fetcher = SmartContentFetcher(workspace)
    
    return _fetcher
