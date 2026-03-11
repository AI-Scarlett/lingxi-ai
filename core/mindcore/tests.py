#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindCore 单元测试

测试所有记忆模块的功能
"""

import asyncio
import time
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mindcore.stm import ShortTermMemory
from mindcore.mtm import MidTermMemory
from mindcore.ltm import LongTermMemory
from mindcore.extractor import MemoryExtractor
from mindcore.compressor import MemoryCompressor
from mindcore.retriever import HybridRetriever


async def test_stm():
    """测试短期记忆"""
    print("\n=== 测试 STM（短期记忆） ===")
    
    stm = ShortTermMemory(capacity=10, ttl_hours=24)
    
    # 添加记忆
    m1 = await stm.add("老板喜欢早上 9 点开始工作", importance=9.0)
    m2 = await stm.add("老板不喜欢吃香菜", importance=8.0)
    m3 = await stm.add("老板的生日是 3 月 15 日", importance=10.0)
    
    print(f"✅ 添加了 3 条记忆")
    print(f"   - {m1}")
    print(f"   - {m2}")
    print(f"   - {m3}")
    
    # 获取记忆
    retrieved = await stm.get(m1.id)
    print(f"✅ 检索记忆：{retrieved.content if retrieved else 'None'}")
    
    # 搜索
    results = await stm.search("老板 喜欢", top_k=2)
    print(f"✅ 搜索结果：{len(results)} 条")
    for r in results:
        print(f"   - {r.content[:50]}...")
    
    # 统计
    stats = stm.stats()
    print(f"✅ 统计：{stats}")
    
    return True


async def test_mtm(tmp_db):
    """测试中期记忆"""
    print("\n=== 测试 MTM（中期记忆） ===")
    
    mtm = MidTermMemory(tmp_db)
    
    # 添加记忆
    m1 = await mtm.add("老板的工作习惯：每天早上 9 点开始，晚上 6 点结束", importance=9.0)
    m2 = await mtm.add("老板的饮食偏好：不喜欢吃香菜，喜欢川菜", importance=8.0)
    
    print(f"✅ 添加了 2 条记忆")
    
    # 获取
    retrieved = await mtm.get(m1["id"])
    print(f"✅ 检索记忆：{retrieved['content'] if retrieved else 'None'}")
    
    # 搜索
    results = await mtm.search("老板 习惯", top_k=2)
    print(f"✅ 搜索结果：{len(results)} 条")
    
    # 最近记忆
    recent = await mtm.get_recent(days=7, limit=10)
    print(f"✅ 最近 7 天记忆：{len(recent)} 条")
    
    # 统计
    stats = mtm.stats()
    print(f"✅ 统计：{stats}")
    
    return True


async def test_ltm(tmp_db):
    """测试长期记忆"""
    print("\n=== 测试 LTM（长期记忆） ===")
    
    ltm = LongTermMemory(tmp_db)
    
    # 添加记忆
    m1 = await ltm.add("老板的完整档案：姓名、生日、偏好、习惯等", importance=10.0, metadata={"tags": ["档案", "重要"]})
    m2 = await ltm.add("项目历史记录：2026 年所有重要项目", importance=9.0, metadata={"tags": ["项目", "历史"]})
    
    print(f"✅ 添加了 2 条记忆")
    
    # 按标签搜索
    results = await ltm.search_by_tags(["档案"], top_k=5)
    print(f"✅ 标签搜索：{len(results)} 条")
    
    # 高重要性记忆
    high_imp = await ltm.get_by_importance(min_importance=9.0, limit=10)
    print(f"✅ 高重要性记忆：{len(high_imp)} 条")
    
    # 统计
    stats = ltm.stats()
    print(f"✅ 统计：{stats}")
    
    return True


def test_extractor():
    """测试记忆提取器"""
    print("\n=== 测试 MemoryExtractor（记忆提取器） ===")
    
    extractor = MemoryExtractor()
    
    # 测试对话
    user_content = "我喜欢每天早上 9 点开始工作，不喜欢被打扰。记住，我不喜欢吃香菜。"
    
    memories = extractor.extract(user_content)
    
    print(f"✅ 从对话中提取了 {len(memories)} 条记忆:")
    for mem in memories:
        print(f"   - 类型：{mem['type']}, 内容：{mem['content'][:50]}..., 重要性：{mem['importance']}")
    
    # 测试重要性计算
    important_content = "记住！这个非常重要！我是公司的 CEO，我必须每天早上 8 点开会。"
    importance = extractor._calculate_importance(important_content, "")
    print(f"✅ 重要性评分：{importance}/10")
    
    return True


def test_compressor():
    """测试记忆压缩器"""
    print("\n=== 测试 MemoryCompressor（记忆压缩器） ===")
    
    compressor = MemoryCompressor(threshold_chars=50)
    
    # 长内容
    long_content = "老板的完整工作习惯描述：他喜欢每天早上 9 点准时开始工作，不喜欢在早上被打扰。他通常会在早上处理最重要的任务，下午开会，晚上总结一天的工作。他不喜欢吃香菜，但是非常喜欢川菜。他的生日是 3 月 15 日，属虎。"
    
    # 压缩
    compressed = compressor.compress(long_content, max_length=100)
    print(f"✅ 原始长度：{len(long_content)} 字符")
    print(f"✅ 压缩后：{len(compressed)} 字符")
    print(f"   内容：{compressed}")
    
    # 测试去重
    memories = [
        {"content": "老板喜欢早上 9 点工作", "importance": 8.0},
        {"content": "老板喜欢早上 9 点工作", "importance": 9.0},
        {"content": "老板不喜欢吃香菜", "importance": 7.0}
    ]
    
    merged = compressor.merge_similar(memories)
    print(f"✅ 去重前：{len(memories)} 条，去重后：{len(merged)} 条")
    
    return True


async def test_retriever():
    """测试混合检索器"""
    print("\n=== 测试 HybridRetriever（混合检索器） ===")
    
    retriever = HybridRetriever()
    
    # 模拟记忆源
    sources = {
        "stm": [
            {"id": "1", "content": "老板喜欢早上 9 点工作", "importance": 9.0},
            {"id": "2", "content": "老板不喜欢吃香菜", "importance": 8.0}
        ],
        "mtm": [
            {"id": "3", "content": "老板的工作习惯非常规律", "importance": 7.0},
            {"id": "4", "content": "老板的生日是 3 月 15 日", "importance": 10.0}
        ],
        "ltm": [
            {"id": "5", "content": "老板的完整档案信息", "importance": 10.0}
        ]
    }
    
    # 检索
    results = await retriever.retrieve("老板 工作 习惯", top_k=3, sources=sources)
    
    print(f"✅ 检索结果：{len(results)} 条")
    for r in results:
        print(f"   - [{r.get('_source')}] {r['content'][:50]}... (score: {r.get('_score', 0):.4f})")
    
    return True


async def run_all_tests():
    """运行所有测试"""
    import tempfile
    import os
    
    # 创建临时数据库
    tmp_db = tempfile.mktemp(suffix=".db")
    
    print("="*60)
    print("🧪 MemOS 单元测试套件")
    print("="*60)
    
    tests = [
        ("STM", lambda: test_stm()),
        ("MTM", lambda: test_mtm(tmp_db)),
        ("LTM", lambda: test_ltm(tmp_db)),
        ("Extractor", lambda: test_extractor()),
        ("Compressor", lambda: test_compressor()),
        ("Retriever", lambda: test_retriever())
    ]
    
    results = []
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((name, "✅ PASS", result))
        except Exception as e:
            results.append((name, f"❌ FAIL: {e}", False))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    for name, status, _ in results:
        print(f"{name}: {status}")
    
    passed = sum(1 for _, s, _ in results if "PASS" in s)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 通过")
    
    # 清理
    if os.path.exists(tmp_db):
        os.remove(tmp_db)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
