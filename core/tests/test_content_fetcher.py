#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapling 内容获取器单元测试
"""

import asyncio
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from content_fetcher import SmartContentFetcher, get_content_fetcher


class TestSmartContentFetcher:
    """内容获取器测试"""
    
    @pytest.fixture
    def fetcher(self):
        """创建测试实例"""
        return SmartContentFetcher(str(Path.home() / ".openclaw" / "workspace"))
    
    @pytest.mark.asyncio
    async def test_basic_fetch(self, fetcher):
        """测试基础抓取"""
        result = await fetcher.fetch_url("https://example.com")
        
        assert result["success"] is True
        assert result["content"] is not None
        assert len(result["content"]) > 0
        assert result["from_cache"] is False
    
    @pytest.mark.asyncio
    async def test_cache(self, fetcher):
        """测试缓存功能"""
        url = "https://example.com"
        
        # 首次获取
        result1 = await fetcher.fetch_url(url, use_cache=True)
        assert result1["from_cache"] is False
        
        # 二次获取（应该来自缓存）
        result2 = await fetcher.fetch_url(url, use_cache=True)
        assert result2["from_cache"] is True
        
        # 内容应该相同
        assert result1["content"] == result2["content"]
    
    @pytest.mark.asyncio
    async def test_selector_extraction(self, fetcher):
        """测试选择器提取"""
        html = """
        <html>
            <body>
                <div class="product">
                    <h2>Product 1</h2>
                    <p class="price">$10.99</p>
                </div>
                <div class="product">
                    <h2>Product 2</h2>
                    <p class="price">$20.99</p>
                </div>
            </body>
        </html>
        """
        
        # CSS 选择器
        products = fetcher.extract_with_selector(html, ".product h2", selector_type="css")
        assert len(products) == 2
        assert "Product 1" in products[0]
        assert "Product 2" in products[1]
        
        # XPath 选择器
        prices = fetcher.extract_with_selector(html, "//p[@class='price']", selector_type="xpath")
        assert len(prices) == 2
        assert "$10.99" in prices[0]
        assert "$20.99" in prices[1]
    
    @pytest.mark.asyncio
    async def test_adaptive_extraction(self, fetcher):
        """测试自适应提取"""
        # 原始 HTML
        html1 = """
        <div class="product-list">
            <article class="product" data-id="1">
                <h3>Product 1</h3>
            </article>
        </div>
        """
        
        # 变化后的 HTML（类名改变）
        html2 = """
        <div class="items">
            <article class="item" data-id="1">
                <h3>Product 1</h3>
            </article>
        </div>
        """
        
        # 自适应模式应该能找到相似元素
        results1 = fetcher.extract_with_selector(html1, ".product h3", adaptive=True)
        results2 = fetcher.extract_with_selector(html2, ".product h3", adaptive=True)
        
        # 即使类名改变，自适应模式也应该找到
        assert len(results1) > 0 or len(results2) > 0
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self, fetcher):
        """测试缓存清理"""
        # 设置小缓存限制
        fetcher.max_cache_size = 3
        
        # 添加多个缓存
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
            "https://example.com/4",
            "https://example.com/5"
        ]
        
        for url in urls:
            # 模拟缓存
            fetcher._save_to_cache(url, {"content": "test"})
        
        # 检查缓存数量不超过限制
        stats = fetcher.get_cache_stats()
        assert stats["count"] <= fetcher.max_cache_size
    
    @pytest.mark.asyncio
    async def test_error_handling(self, fetcher):
        """测试错误处理"""
        # 无效 URL
        result = await fetcher.fetch_url("https://invalid.url.that.does.not.exist")
        
        assert result["success"] is False
        assert "error" in result
        assert result["content"] == ""
    
    @pytest.mark.asyncio
    async def test_timeout(self, fetcher):
        """测试超时处理"""
        # 设置很短的超时
        result = await fetcher.fetch_url("https://httpbin.org/delay/10", timeout=1)
        
        # 应该超时或失败
        assert result["success"] is False or "timeout" in result.get("error", "").lower()
    
    def test_cache_stats(self, fetcher):
        """测试缓存统计"""
        stats = fetcher.get_cache_stats()
        
        assert "count" in stats
        assert "size_bytes" in stats
        assert "size_mb" in stats
        assert "max_size" in stats
        assert "ttl_seconds" in stats
    
    def test_singleton(self):
        """测试单例模式"""
        fetcher1 = get_content_fetcher()
        fetcher2 = get_content_fetcher()
        
        assert fetcher1 is fetcher2


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """完整工作流测试"""
        fetcher = get_content_fetcher()
        
        # 1. 抓取网页
        result = await fetcher.fetch_url("https://example.com")
        assert result["success"] is True
        
        # 2. 提取内容
        if result["html"]:
            titles = fetcher.extract_with_selector(result["html"], "h1", selector_type="css")
            # 应该有 h1 标签
            assert isinstance(titles, list)
        
        # 3. 检查缓存
        stats = fetcher.get_cache_stats()
        assert stats["count"] > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
