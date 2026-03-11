#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapling 内容获取器使用示例

演示如何使用 Scrapling 集成到灵犀中
"""

import asyncio
from pathlib import Path
import sys

# 添加核心模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from content_fetcher import SmartContentFetcher, get_content_fetcher


async def demo_basic_usage():
    """基础用法示例"""
    print("=" * 60)
    print("Scrapling 内容获取器 - 基础用法示例")
    print("=" * 60)
    
    # 获取实例
    fetcher = get_content_fetcher()
    
    # 示例 1: 普通网页抓取
    print("\n📄 示例 1: 抓取普通网页")
    result = await fetcher.fetch_url("https://example.com")
    
    if result["success"]:
        print(f"✅ 成功获取：{result['title']}")
        print(f"📊 内容长度：{len(result['content'])} 字符")
        print(f"💾 来自缓存：{result['from_cache']}")
        print(f"📝 前 200 字符：{result['content'][:200]}...")
    else:
        print(f"❌ 失败：{result['error']}")
    
    # 示例 2: 微信文章（特殊处理）
    print("\n📱 示例 2: 抓取微信文章")
    wechat_url = "https://mp.weixin.qq.com/s/LpaM683yzrzq_Nj63oH_RA"
    result = await fetcher.fetch_url(wechat_url, bypass_bot=True)
    
    if result["success"]:
        print(f"✅ 成功获取：{result['title']}")
        print(f"📊 内容长度：{len(result['content'])} 字符")
        print(f"📝 前 300 字符：{result['content'][:300]}...")
    else:
        print(f"❌ 失败：{result['error']}")
    
    # 示例 3: 使用选择器提取
    print("\n🎯 示例 3: 使用选择器提取内容")
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
    print(f"CSS 选择器提取：{products}")
    
    # 自适应模式（网站变化后自动重新定位）
    prices = fetcher.extract_with_selector(html, ".price", selector_type="css", adaptive=True)
    print(f"自适应提取：{prices}")
    
    # 示例 4: 缓存统计
    print("\n💾 示例 4: 缓存统计")
    stats = fetcher.get_cache_stats()
    print(f"缓存数量：{stats['count']}")
    print(f"缓存大小：{stats['size_mb']} MB")
    print(f"最大缓存：{stats['max_size']}")
    print(f"缓存有效期：{stats['ttl_seconds']} 秒")


async def demo_advanced_usage():
    """高级用法示例"""
    print("\n" + "=" * 60)
    print("Scrapling 内容获取器 - 高级用法示例")
    print("=" * 60)
    
    fetcher = SmartContentFetcher()
    
    # 示例 1: 批量抓取（带并发控制）
    print("\n🚀 示例 1: 批量抓取")
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://www.wikipedia.org"
    ]
    
    import asyncio
    tasks = [fetcher.fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            print(f"❌ {url}: {result}")
        elif result["success"]:
            print(f"✅ {url}: {len(result['content'])} 字符")
        else:
            print(f"❌ {url}: {result['error']}")
    
    # 示例 2: 带重试的抓取
    print("\n🔄 示例 2: 带重试的抓取")
    for attempt in range(3):
        result = await fetcher.fetch_url("https://example.com", timeout=10)
        if result["success"]:
            print(f"✅ 第 {attempt + 1} 次尝试成功")
            break
        else:
            print(f"⚠️ 第 {attempt + 1} 次尝试失败：{result['error']}")
            await asyncio.sleep(1)  # 等待 1 秒后重试
    
    # 示例 3: 自定义缓存策略
    print("\n💾 示例 3: 自定义缓存策略")
    fetcher.cache_ttl = 300  # 5 分钟有效期
    fetcher.max_cache_size = 50  # 最多 50 个页面
    
    result = await fetcher.fetch_url("https://example.com", use_cache=True)
    print(f"首次获取：来自缓存={result['from_cache']}")
    
    result = await fetcher.fetch_url("https://example.com", use_cache=True)
    print(f"二次获取：来自缓存={result['from_cache']}")


async def demo_integration_with_llm():
    """与 LLM 集成示例"""
    print("\n" + "=" * 60)
    print("Scrapling 与 LLM 集成示例")
    print("=" * 60)
    
    fetcher = get_content_fetcher()
    
    # 场景：用户发送了一个链接，需要提取内容并总结
    print("\n📋 场景：用户发送链接，提取内容并总结")
    
    url = "https://example.com"
    print(f"用户链接：{url}")
    
    # 1. 获取内容
    result = await fetcher.fetch_url(url)
    
    if result["success"]:
        content = result["content"]
        
        # 2. 智能截断（避免超出 token 限制）
        max_tokens = 2000
        if len(content) > max_tokens * 4:  # 粗略估计
            content = content[:max_tokens * 4] + "\n...（内容已截断）"
        
        # 3. 准备 LLM 输入
        llm_input = f"""
请总结以下内容：

{content[:500]}...
"""
        
        print(f"✅ 内容已准备好发送给 LLM")
        print(f"📊 原始长度：{len(result['content'])} 字符")
        print(f"📊 处理后长度：{len(content)} 字符")
        print(f"💡 节省 tokens: {(1 - len(content)/len(result['content'])) * 100:.1f}%")
    else:
        print(f"❌ 获取失败：{result['error']}")


async def main():
    """主函数"""
    print("\n🕷️ Scrapling 内容获取器演示\n")
    
    # 检查 Scrapling 是否可用
    try:
        from scrapling.fetchers import StealthyFetcher
        print("✅ Scrapling 已安装并可用")
    except ImportError:
        print("⚠️ Scrapling 未安装，部分功能受限")
        print("安装命令：pip install scrapling")
        return
    
    # 运行演示
    await demo_basic_usage()
    await demo_advanced_usage()
    await demo_integration_with_llm()
    
    print("\n" + "=" * 60)
    print("演示完毕！💋")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
