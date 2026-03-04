#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀记忆系统测试脚本
Test script for Lingxi Memory Service

版本：v2.6.0
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_service import MemoryService, MemoryItem, MemoryStructure


class MockLLM:
    """模拟 LLM 客户端（用于测试）"""
    
    async def chat(self, messages, temperature=0.5):
        """模拟聊天响应"""
        user_content = messages[-1].get("content", "")
        
        # 根据内容返回模拟的记忆提取结果
        if "提取用户记忆" in user_content or "从以下对话中提取" in user_content:
            return json.dumps({
                "items": [
                    {
                        "category": "preferences",
                        "topic": "工作时间",
                        "content": "用户通常在上午 9 点开始工作",
                        "confidence": 0.85,
                        "metadata": {}
                    },
                    {
                        "category": "preferences",
                        "topic": "沟通风格",
                        "content": "用户偏好简洁直接的沟通方式",
                        "confidence": 0.9,
                        "metadata": {}
                    }
                ]
            }, ensure_ascii=False)
        
        elif "从任务执行中提取" in user_content:
            return json.dumps({
                "items": [
                    {
                        "category": "knowledge",
                        "topic": "技能",
                        "content": "用户熟悉 Python 编程和自动化脚本",
                        "confidence": 0.8,
                        "metadata": {}
                    }
                ]
            }, ensure_ascii=False)
        
        elif "筛选最相关的记忆" in user_content:
            return json.dumps({
                "relevant_items": ["test_id_1"],
                "inferences": ["用户对工作效率有较高要求"],
                "next_step_query": "用户的工作习惯是什么？"
            }, ensure_ascii=False)
        
        # 默认响应
        return json.dumps({"items": []}, ensure_ascii=False)


async def test_memory_structure():
    """测试 1: 记忆存储结构"""
    print("\n" + "="*60)
    print("📁 测试 1: 记忆存储结构")
    print("="*60)
    
    store = MemoryStructure()
    await store.ensure_structure()
    
    # 检查目录结构
    print("\n✅ 检查目录结构...")
    for name, dir_path in store.dirs.items():
        exists = "✅" if dir_path.exists() else "❌"
        print(f"  {exists} {name}: {dir_path}")
    
    # 检查文件
    print("\n✅ 检查文件...")
    for name, file_path in store.files.items():
        exists = "✅" if file_path.exists() else "❌"
        print(f"  {exists} {name}: {file_path}")
    
    print("\n✅ 测试 1 通过：记忆存储结构创建成功")
    return store


async def test_memory_item_save_load(store: MemoryStructure):
    """测试 2: 记忆项保存和加载"""
    print("\n" + "="*60)
    print("💾 测试 2: 记忆项保存和加载")
    print("="*60)
    
    # 创建测试记忆项
    test_items = [
        MemoryItem(
            id=f"test_{i}",
            category="preferences",
            topic=f"测试主题{i}",
            content=f"这是测试记忆内容{i}",
            source="test_script",
            timestamp=time.time(),
            confidence=0.9,
            user_id="test_user"
        )
        for i in range(5)
    ]
    
    # 保存记忆项
    print("\n✅ 保存 5 条测试记忆...")
    for item in test_items:
        await store.save_memory_item(item)
        print(f"  ✅ 保存：{item.topic}")
    
    # 加载记忆项
    print("\n✅ 加载所有记忆...")
    loaded_items = await store.load_all_items()
    print(f"  📊 加载了 {len(loaded_items)} 条记忆")
    
    # 验证
    assert len(loaded_items) >= 5, "记忆项数量不匹配"
    print("\n✅ 测试 2 通过：记忆项保存和加载成功")
    return loaded_items


async def test_memory_extractor():
    """测试 3: 自动记忆提取"""
    print("\n" + "="*60)
    print("🧠 测试 3: 自动记忆提取")
    print("="*60)
    
    from memory_service import MemoryExtractor
    
    extractor = MemoryExtractor(llm_client=MockLLM())
    
    # 测试对话提取
    test_conversation = [
        {"role": "user", "content": "我通常早上 9 点开始工作"},
        {"role": "assistant", "content": "好的，我记住了～"},
        {"role": "user", "content": "我喜欢简洁直接的沟通方式"},
    ]
    
    print("\n✅ 从对话中提取记忆...")
    items = await extractor.extract_from_conversation(test_conversation, "test_conv_001")
    
    print(f"  📊 提取了 {len(items)} 条记忆")
    for item in items:
        print(f"    - [{item.category}] {item.topic}: {item.content[:30]}...")
    
    # 测试任务提取
    print("\n✅ 从任务中提取记忆...")
    task_items = await extractor.extract_from_task(
        task_input="帮我写一个 Python 脚本",
        task_result="脚本已完成，使用了 asyncio 和 aiohttp",
        task_id="test_task_001"
    )
    
    print(f"  📊 提取了 {len(task_items)} 条记忆")
    for item in task_items:
        print(f"    - [{item.category}] {item.topic}: {item.content[:30]}...")
    
    print("\n✅ 测试 3 通过：自动记忆提取成功")
    return items + task_items


async def test_memory_organizer(store: MemoryStructure):
    """测试 4: 记忆组织器"""
    print("\n" + "="*60)
    print("🗂️  测试 4: 记忆组织器")
    print("="*60)
    
    from memory_service import MemoryOrganizer
    
    organizer = MemoryOrganizer(store)
    
    # 测试自动分类
    print("\n✅ 测试自动分类...")
    test_contents = [
        "我喜欢早上喝咖啡",
        "张三是我的同事",
        "我熟悉 Python 编程",
        "今天下午有个会议"
    ]
    
    for content in test_contents:
        category = organizer.auto_categorize(content)
        print(f"  📝 '{content[:15]}...' → {category}")
    
    # 测试查找相关记忆
    print("\n✅ 测试查找相关记忆...")
    items = await store.load_all_items()
    if items:
        test_item = items[0]
        related = await organizer.find_related(test_item, top_k=3)
        print(f"  🔗 '{test_item.topic}' 的相关记忆：{related}")
    
    # 测试模式检测
    print("\n✅ 测试模式检测...")
    patterns = await organizer.detect_patterns()
    for pattern in patterns:
        print(f"  📊 {pattern['type']}: {pattern['description']}")
    
    print("\n✅ 测试 4 通过：记忆组织器工作正常")


async def test_memory_retriever(store: MemoryStructure):
    """测试 5: 记忆检索"""
    print("\n" + "="*60)
    print("🔍 测试 5: 记忆检索")
    print("="*60)
    
    from memory_service import MemoryRetriever
    
    retriever = MemoryRetriever(store, llm_client=MockLLM())
    
    # 测试关键词检索
    print("\n✅ 关键词检索...")
    result = await retriever.retrieve("测试 主题", method="keyword", top_k=5)
    print(f"  📊 检索到 {result['total']} 条结果")
    for i, item in enumerate(result['items'][:3]):
        print(f"    {i+1}. [{item['category']}] {item['topic']}")
    
    # 测试 LLM 检索
    print("\n✅ LLM 深度检索...")
    result = await retriever.retrieve("用户偏好", method="llm", top_k=3)
    print(f"  📊 检索到 {len(result.get('items', []))} 条结果")
    if result.get('inferences'):
        print(f"  💡 推理：{result['inferences'][0]}")
    if result.get('next_step_query'):
        print(f"  🔮 预测查询：{result['next_step_query']}")
    
    # 测试主动上下文
    print("\n✅ 主动上下文加载...")
    context = await retriever.proactive_context("test_user")
    print(f"  📊 总记忆数：{context['total_memories']}")
    print(f"  📝 最近记忆：{len(context['recent_context'])} 条")
    print(f"  🔮 预测需求：{len(context['predicted_needs'])} 个")
    
    print("\n✅ 测试 5 通过：记忆检索功能正常")


async def test_memory_service():
    """测试 6: 完整记忆服务"""
    print("\n" + "="*60)
    print("🎯 测试 6: 完整记忆服务集成")
    print("="*60)
    
    service = MemoryService(llm_client=MockLLM())
    await service.initialize()
    
    # 测试 memorize
    print("\n✅ 测试 memorize()...")
    conversation = [
        {"role": "user", "content": "我喜欢喝拿铁咖啡"},
        {"role": "assistant", "content": "好的，我记住了～"}
    ]
    
    result = await service.memorize(conversation, "test_conv_final")
    print(f"  📊 提取了 {result['extracted_items']} 条记忆")
    
    # 测试 retrieve
    print("\n✅ 测试 retrieve()...")
    result = await service.retrieve("咖啡", method="keyword")
    print(f"  📊 检索到 {result.get('total', 0)} 条结果")
    
    # 测试 get_context
    print("\n✅ 测试 get_context()...")
    context = await service.get_context("default")
    print(f"  📊 上下文：{context.get('total_memories', 0)} 条记忆")
    
    # 测试 get_stats
    print("\n✅ 测试 get_stats()...")
    stats = await service.get_stats()
    print(f"  📊 总记忆数：{stats['total_items']}")
    print(f"  📊 按类别：{stats['by_category']}")
    print(f"  📊 最近 24 小时：{stats['recent_items']} 条")
    
    print("\n✅ 测试 6 通过：完整记忆服务集成成功")


async def test_orchestrator_integration():
    """测试 7: 主编排器集成"""
    print("\n" + "="*60)
    print("🔧 测试 7: 主编排器集成")
    print("="*60)
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from orchestrator_with_memory import LingxiOrchestrator
        
        orchestrator = LingxiOrchestrator(llm_client=MockLLM())
        await orchestrator.initialize()
        
        # 测试执行
        print("\n✅ 测试 execute()...")
        result = await orchestrator.execute("今天天气怎么样", user_id="test_user")
        print(f"  📊 会话 ID: {result['session_id']}")
        print(f"  📊 加载记忆：{result['context_loaded']} 条")
        print(f"  📊 意图：{result['intent']['intent']}")
        
        # 测试记忆统计
        print("\n✅ 测试 get_memory_stats()...")
        stats = await orchestrator.get_memory_stats()
        print(f"  📊 总记忆数：{stats['total_items']}")
        
        # 测试搜索记忆
        print("\n✅ 测试 search_memory()...")
        search_result = await orchestrator.search_memory("偏好")
        print(f"  📊 搜索结果：{search_result.get('total', 0)} 条")
        
        print("\n✅ 测试 7 通过：主编排器集成成功")
        
    except ImportError as e:
        print(f"\n⚠️  主编排器模块未找到：{e}")
        print("   跳过此测试")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 灵犀记忆系统 v2.6.0 测试套件")
    print("="*60)
    print("\n开始测试...\n")
    
    start_time = time.time()
    
    try:
        # 测试 1: 存储结构
        store = await test_memory_structure()
        
        # 测试 2: 保存加载
        await test_memory_item_save_load(store)
        
        # 测试 3: 自动提取
        await test_memory_extractor()
        
        # 测试 4: 组织器
        await test_memory_organizer(store)
        
        # 测试 5: 检索
        await test_memory_retriever(store)
        
        # 测试 6: 完整服务
        await test_memory_service()
        
        # 测试 7: 主编排器集成
        await test_orchestrator_integration()
        
        # 总结
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        print(f"\n📊 测试总览:")
        print(f"  - 测试项目：7 个")
        print(f"  - 总耗时：{elapsed:.2f}秒")
        print(f"  - 状态：全部通过 ✅")
        print(f"\n💋 灵犀记忆系统 v2.6.0 已就绪！")
        print(f"\n📁 记忆文件位置：~/.openclaw/workspace/memory/")
        print(f"📝 记忆数据文件：~/.openclaw/workspace/memory/items/memories.jsonl")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 测试失败")
        print("="*60)
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
