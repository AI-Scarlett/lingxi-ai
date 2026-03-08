#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 修复剩余 TODO 事项

作者：斯嘉丽 Scarlett
日期：2026-03-08
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_active_memory():
    """修复 active_memory.py 中的 TODO"""
    filepath = os.path.join(SCRIPT_DIR, "active_memory.py")
    
    if not os.path.exists(filepath):
        print("⚠️  active_memory.py 不存在")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TODO 1: 实现对话历史检索 (line 194)
    old1 = '        # TODO: 实现对话历史检索'
    new1 = '''        # 实现对话历史检索（简化版：返回最近 10 条）
        recent = self.conversation_history[-10:] if self.conversation_history else []
        return recent'''
    
    # TODO 2: 实现对话记录保存 (line 353)
    old2 = '        # TODO: 实现对话记录保存'
    new2 = '''        # 实现对话记录保存（简化版：添加到内存列表）
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近 100 条
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]'''
    
    count = 0
    if old1 in content:
        content = content.replace(old1, new1)
        count += 1
    if old2 in content:
        content = content.replace(old2, new2)
        count += 1
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复 active_memory.py ({count} 个 TODO)")
        return True
    else:
        print(f"⚠️  active_memory.py 未找到目标 TODO")
        return False


def fix_channel_linking():
    """修复 channel_linking.py 中的 TODO"""
    filepath = os.path.join(SCRIPT_DIR, "channel_linking.py")
    
    if not os.path.exists(filepath):
        print("⚠️  channel_linking.py 不存在")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TODO 1: 实际删除逻辑 (line 160)
    old1 = '''                if len(link.channels) < 2:
                    # 剩余渠道不足 2 个，删除整个绑定
                    link.active = False
                    # TODO: 实际删除逻辑'''
    
    new1 = '''                if len(link.channels) < 2:
                    # 剩余渠道不足 2 个，删除整个绑定
                    link.active = False
                    # 实际删除逻辑：从索引中移除
                    await self.service.store._update_links_index(link_id, "remove")'''
    
    # TODO 2: 保存更新 (line 167)
    old2 = '''                else:
                    # 更新绑定
                    # TODO: 保存更新'''
    
    new2 = '''                else:
                    # 更新绑定
                    # 保存更新：重写绑定文件
                    link_file = self.service.store.links_detail_dir / f"{link_id}.json"
                    import json
                    import aiofiles
                    async with aiofiles.open(link_file, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(link.to_dict(), ensure_ascii=False, indent=2))'''
    
    # TODO 3: 实际删除逻辑 (line 181)
    old3 = '''            # 删除整个绑定
            link.active = False
            # TODO: 实际删除逻辑'''
    
    new3 = '''            # 删除整个绑定
            link.active = False
            # 实际删除逻辑：从索引中移除并删除文件
            await self.service.store._update_links_index(link_id, "remove")
            link_file = self.service.store.links_detail_dir / f"{link_id}.json"
            if os.path.exists(link_file):
                os.remove(link_file)'''
    
    # TODO 4: 保存更新 (line 212)
    old4 = '''        # 更新验证状态
        link.verified_by_user = True
        
        # TODO: 保存更新'''
    
    new4 = '''        # 更新验证状态
        link.verified_by_user = True
        
        # 保存更新：重写绑定文件
        import json
        import aiofiles
        link_file = self.service.store.links_detail_dir / f"{link_id}.json"
        async with aiofiles.open(link_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(link.to_dict(), ensure_ascii=False, indent=2))'''
    
    count = 0
    for old, new in [(old1, new1), (old2, new2), (old3, new3), (old4, new4)]:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复 channel_linking.py ({count} 个 TODO)")
        return True
    else:
        print(f"⚠️  channel_linking.py 未找到目标 TODO")
        return False


def main():
    print("=" * 60)
    print("🔧 灵犀 - 修复剩余 TODO 事项")
    print("=" * 60)
    
    fixes = [
        fix_active_memory,
        fix_channel_linking,
    ]
    
    success = 0
    for fix in fixes:
        try:
            if fix():
                success += 1
        except Exception as e:
            print(f"❌ {fix.__name__} 失败：{e}")
    
    print("=" * 60)
    print(f"✅ 完成：{success}/{len(fixes)} 个文件已修复")
    print("=" * 60)


if __name__ == "__main__":
    main()
