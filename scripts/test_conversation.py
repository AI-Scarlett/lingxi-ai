#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对话管理器

验证对话是否正确保存和加载
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.conversation_manager import ConversationManager

def test_conversation_manager():
    """测试对话管理器"""
    
    print("=" * 60)
    print("🧠 测试对话管理器")
    print("=" * 60)
    
    # 创建管理器
    manager = ConversationManager()
    
    # 测试用户 ID
    test_user_id = "DE5BA2C531B102AD9989F5E04935BCA6"
    
    print(f"\n1️⃣ 检查用户 {test_user_id} 的对话...")
    conv = manager.get_current(test_user_id)
    
    if conv:
        print(f"   ✅ 找到当前对话：{conv.id}")
        print(f"   - 消息数：{conv.message_count}")
        print(f"   - Tokens: {conv.total_tokens}")
        print(f"   - 状态：{conv.status}")
        print(f"   - 创建时间：{conv.created_at}")
    else:
        print(f"   ❌ 未找到当前对话，创建新的...")
        conv = manager.create_conversation(test_user_id)
        print(f"   ✅ 创建成功：{conv.id}")
    
    # 模拟添加消息
    print(f"\n2️⃣ 模拟添加 5 条消息...")
    for i in range(5):
        result = manager.add_message(test_user_id, conv.id, tokens=1000)
        print(f"   消息 {i+1}: {result['message_count']}/{result['max_messages']} ({result['usage_percent']}%)")
    
    # 检查结果
    print(f"\n3️⃣ 检查对话状态...")
    conv = manager.get_current(test_user_id)
    print(f"   - 消息数：{conv.message_count}")
    print(f"   - Tokens: {conv.total_tokens}")
    print(f"   - 状态：{conv.status}")
    
    # 测试阈值警告
    print(f"\n4️⃣ 测试阈值警告...")
    while conv.message_count < 85:
        result = manager.add_message(test_user_id, conv.id, tokens=500)
        if result.get("status") == "warning":
            print(f"   ⚠️ 触发警告：{result['suggestion']}")
            break
        if result.get("status") == "exceeded":
            print(f"   ❌ 已超限：{result['suggestion']}")
            break
    
    # 显示存储文件
    print(f"\n5️⃣ 存储文件位置...")
    import pathlib
    storage_path = pathlib.Path("~/.openclaw/workspace/conversations").expanduser()
    print(f"   📁 目录：{storage_path}")
    
    for file in storage_path.glob("*.jsonl"):
        print(f"   - {file.name} ({file.stat().st_size} bytes)")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_conversation_manager()
