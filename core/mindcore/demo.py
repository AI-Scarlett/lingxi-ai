#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindCore 快速演示

展示 MindCore 核心功能
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mindcore import MindCore


async def demo():
    """演示 MindCore 功能"""
    
    print("="*60)
    print("🧠 灵犀 MindCore 记忆核心系统演示")
    print("="*60)
    
    # 获取实例
    mindcore = MindCore()
    
    # 1. 保存记忆
    print("\n📝 保存记忆...")
    
    m1 = await mindcore.save(
        "老板喜欢每天早上 9 点开始工作，不喜欢被打扰",
        importance=9.0,
        metadata={"tags": ["工作习惯", "偏好"]}
    )
    print(f"✅ 保存记忆 1: {m1.id}")
    
    m2 = await mindcore.save(
        "老板不喜欢吃香菜，但是非常喜欢川菜",
        importance=8.0,
        metadata={"tags": ["饮食偏好"]}
    )
    print(f"✅ 保存记忆 2: {m2.id}")
    
    m3 = await mindcore.save(
        "老板的生日是 3 月 15 日，属虎",
        importance=10.0,
        metadata={"tags": ["个人信息", "重要"]}
    )
    print(f"✅ 保存记忆 3: {m3.id}")
    
    # 2. 检索记忆
    print("\n🔍 检索记忆...")
    
    results = await mindcore.retrieve("老板 工作 习惯", top_k=3)
    print(f"✅ 检索到 {len(results)} 条记忆:")
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r.content[:60]}...")
    
    # 3. 查看统计
    print("\n📊 查看统计...")
    
    print(f"✅ STM 统计：{mindcore.stm.stats()}")
    print(f"✅ MTM 统计：{mindcore.mtm.stats()}")
    print(f"✅ LTM 统计：{mindcore.ltm.stats()}")
    
    # 4. 运行改进周期
    print("\n🔄 运行改进周期...")
    
    report = await mindcore.lifecycle.process(mindcore.stm, mindcore.mtm, mindcore.ltm)
    print(f"✅ 改进报告：{report}")
    
    print("\n" + "="*60)
    print("✨ 演示完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(demo())
