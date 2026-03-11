#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - Scrapling 爬虫技能测试

🕷️ 测试 Scrapling 爬虫功能
"""

import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools/executors"))

async def test_crawler():
    """测试爬虫功能"""
    print("="*60)
    print("🕷️ 灵犀 Scrapling 爬虫测试")
    print("="*60)
    
    # 测试 1：导入测试
    print("\n📦 测试 1: 模块导入")
    try:
        # 添加工具路径
        tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools/executors")
        sys.path.insert(0, tools_path)
        
        from scrapling_crawler import get_crawler, ScraplingExecutor
        print("✅ 模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败：{e}")
        return False
    
    # 测试 2：爬虫初始化
    print("\n🔧 测试 2: 爬虫初始化")
    try:
        crawler = get_crawler()
        if crawler:
            print("✅ 爬虫初始化成功")
        else:
            print("❌ 爬虫初始化失败")
            return False
    except Exception as e:
        print(f"❌ 爬虫初始化失败：{e}")
        return False
    
    # 测试 3：抓取测试（使用简单网站）
    print("\n🌐 测试 3: 网页抓取测试")
    test_urls = [
        "https://httpbin.org/html",  # 测试网站
        "https://example.com",       # 简单网站
    ]
    
    for url in test_urls:
        print(f"\n   测试 URL: {url}")
        try:
            result = await crawler.fetch(url)
            if result["success"]:
                print(f"   ✅ 抓取成功")
                print(f"      标题：{result.get('title', 'N/A')[:50]}")
                print(f"      状态：{result.get('status', 'N/A')}")
                print(f"      链接数：{len(result.get('links', []))}")
                print(f"      内容长度：{len(result.get('text', ''))} 字符")
            else:
                print(f"   ❌ 抓取失败：{result.get('error', '未知错误')}")
        except Exception as e:
            print(f"   ❌ 异常：{e}")
    
    # 测试 4：执行器测试
    print("\n⚙️ 测试 4: 执行器测试")
    try:
        from scrapling_crawler import get_executor
        executor = get_executor()
        print("✅ 执行器创建成功")
        
        # 测试执行
        result = await executor.execute({
            "url": "https://example.com",
            "extract_type": "all"
        })
        
        if result["success"]:
            print(f"✅ 执行成功：{result.get('message', '')}")
        else:
            print(f"❌ 执行失败：{result.get('error', '')}")
    except Exception as e:
        print(f"❌ 执行器测试失败：{e}")
    
    # 测试 5：Layer 0 技能匹配
    print("\n🎯 测试 5: Layer 0 技能匹配")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from layer0_skills import match_layer0_skill
        
        test_queries = [
            "抓取网页",
            "爬取数据",
            "提取内容",
        ]
        
        for query in test_queries:
            matched, skill = match_layer0_skill(query)
            if matched:
                print(f"   ✅ \"{query}\" → {skill['skill_name']}")
            else:
                print(f"   ❌ \"{query}\" → 未匹配")
    except Exception as e:
        print(f"❌ 技能匹配测试失败：{e}")
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_crawler())
    sys.exit(0 if success else 1)
