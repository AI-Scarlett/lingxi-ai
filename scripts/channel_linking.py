"""
灵犀多渠道绑定管理工具
Channel Linking Manager for Lingxi

作者：斯嘉丽 Scarlett
日期：2026-03-08

功能：
1. 创建多渠道绑定
2. 查询绑定关系
3. 解除绑定
4. 验证绑定状态
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from shared_memory import SharedMemoryService, ChannelLink


class ChannelLinkingManager:
    """
    多渠道绑定管理器
    
    提供用户友好的绑定管理接口
    """
    
    def __init__(self):
        self.service = SharedMemoryService()
        self._initialized = False
    
    async def initialize(self):
        """初始化"""
        if not self._initialized:
            await self.service.initialize()
            self._initialized = True
    
    async def create_binding(self, channels: Dict[str, str], 
                            user_note: str = "", 
                            require_confirmation: bool = True) -> Dict:
        """
        创建多渠道绑定
        
        Args:
            channels: 渠道映射 {channel_name: user_id}
                     示例：{"feishu": "ou_xxx", "qqbot": "7941xxx"}
            user_note: 用户备注
            require_confirmation: 是否需要用户确认
        
        Returns:
            绑定结果
        """
        await self.initialize()
        
        # 验证输入
        if not channels or len(channels) < 2:
            return {
                "success": False,
                "error": "至少需要绑定 2 个渠道"
            }
        
        # 检查是否已有绑定
        for channel, user_id in channels.items():
            existing = await self.service.store.find_link_by_channel_id(channel, user_id)
            if existing:
                return {
                    "success": False,
                    "error": f"渠道 {channel} 的用户 {user_id} 已存在绑定关系",
                    "existing_link": existing.to_dict()
                }
        
        # 创建绑定
        link = await self.service.bind_channels(channels, user_note)
        
        return {
            "success": True,
            "link_id": link.link_id,
            "channels": link.channels,
            "created_at": datetime.fromtimestamp(link.created_at).isoformat(),
            "message": f"✅ 成功绑定 {len(channels)} 个渠道"
        }
    
    async def get_binding(self, channel: str, user_id: str) -> Optional[Dict]:
        """
        查询当前渠道的绑定关系
        
        Args:
            channel: 渠道名称
            user_id: 用户 ID
        
        Returns:
            绑定关系详情，无绑定返回 None
        """
        await self.initialize()
        
        link = await self.service.store.find_link_by_channel_id(channel, user_id)
        
        if not link:
            return None
        
        return {
            "link_id": link.link_id,
            "channels": link.channels,
            "user_note": link.user_note,
            "created_at": datetime.fromtimestamp(link.created_at).isoformat(),
            "verified": link.verified_by_user,
            "active": link.active,
            "current_channel": channel,
            "linked_channels": {
                k: v for k, v in link.channels.items() if k != channel
            }
        }
    
    async def list_all_bindings(self) -> List[Dict]:
        """
        列出所有绑定关系
        
        Returns:
            绑定关系列表
        """
        await self.initialize()
        return await self.service.list_bindings()
    
    async def remove_binding(self, link_id: str, 
                            channel: str = None, 
                            user_id: str = None) -> Dict:
        """
        解除绑定
        
        Args:
            link_id: 绑定关系 ID
            channel: 可选，只解除指定渠道
            user_id: 可选，配合 channel 使用
        
        Returns:
            操作结果
        """
        await self.initialize()
        
        link = await self.service.store.get_channel_link(link_id)
        
        if not link:
            return {
                "success": False,
                "error": "绑定关系不存在"
            }
        
        if channel and user_id:
            # 只解除指定渠道
            if channel in link.channels:
                del link.channels[channel]
                
                if len(link.channels) < 2:
                    # 剩余渠道不足 2 个，删除整个绑定
                    link.active = False
                    # 实际删除逻辑：从索引中移除
                    await self.service.store._update_links_index(link_id, "remove")
                    return {
                        "success": True,
                        "message": "绑定关系已删除（剩余渠道不足 2 个）"
                    }
                else:
                    # 更新绑定
                    # 保存更新：重写绑定文件
                    link_file = self.service.store.links_detail_dir / f"{link_id}.json"
                    import json
                    import aiofiles
                    async with aiofiles.open(link_file, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(link.to_dict(), ensure_ascii=False, indent=2))
                    return {
                        "success": True,
                        "message": f"已解除渠道 {channel} 的绑定",
                        "remaining_channels": list(link.channels.keys())
                    }
            else:
                return {
                    "success": False,
                    "error": f"渠道 {channel} 不在绑定关系中"
                }
        else:
            # 删除整个绑定
            link.active = False
            # 实际删除逻辑：从索引中移除并删除文件
            await self.service.store._update_links_index(link_id, "remove")
            link_file = self.service.store.links_detail_dir / f"{link_id}.json"
            if os.path.exists(link_file):
                os.remove(link_file)
            return {
                "success": True,
                "message": "绑定关系已删除"
            }
    
    async def verify_binding(self, link_id: str, 
                            verification_code: str = None) -> Dict:
        """
        验证绑定关系（用户确认）
        
        Args:
            link_id: 绑定关系 ID
            verification_code: 验证码（可选）
        
        Returns:
            验证结果
        """
        await self.initialize()
        
        link = await self.service.store.get_channel_link(link_id)
        
        if not link:
            return {
                "success": False,
                "error": "绑定关系不存在"
            }
        
        # 更新验证状态
        link.verified_by_user = True
        
        # 保存更新：重写绑定文件
        import json
        import aiofiles
        link_file = self.service.store.links_detail_dir / f"{link_id}.json"
        async with aiofiles.open(link_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(link.to_dict(), ensure_ascii=False, indent=2))
        
        return {
            "success": True,
            "message": "✅ 绑定关系已验证",
            "link": link.to_dict()
        }
    
    async def get_cross_channel_memories(self, channel: str, user_id: str,
                                        days: int = 7) -> Dict:
        """
        获取跨渠道记忆（包括所有绑定渠道）
        
        Args:
            channel: 当前渠道
            user_id: 当前渠道用户 ID
            days: 查询天数
        
        Returns:
            跨渠道记忆汇总
        """
        await self.initialize()
        
        # 查询记忆
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        memories = await self.service.query_memories(
            channel=channel,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            cross_channel=True
        )
        
        # 按渠道分组
        grouped = {}
        for key, content in memories.items():
            ch = key.split(":")[0]
            if ch not in grouped:
                grouped[ch] = []
            grouped[ch].append({
                "date": key.split(":")[1] if ":" in key else key,
                "content": content
            })
        
        return {
            "channel": channel,
            "user_id": user_id,
            "days": days,
            "memories_by_channel": grouped,
            "total_entries": len(memories)
        }


# 命令行交互工具
async def interactive_bind():
    """交互式绑定工具"""
    print("\n" + "="*60)
    print("🔗 灵犀多渠道绑定工具")
    print("="*60 + "\n")
    
    manager = ChannelLinkingManager()
    
    print("请选择操作:")
    print("1. 创建新绑定")
    print("2. 查询我的绑定")
    print("3. 列出所有绑定")
    print("4. 解除绑定")
    print("5. 查看跨渠道记忆")
    print("0. 退出\n")
    
    choice = input("请输入选项 (0-5): ").strip()
    
    if choice == "1":
        # 创建绑定
        print("\n📝 创建多渠道绑定")
        print("请输入要绑定的渠道（格式：渠道名：用户 ID）")
        print("示例：feishu:ou_xxx 或 qqbot:7941xxx")
        print("输入 'done' 结束\n")
        
        channels = {}
        while True:
            line = input("渠道绑定 > ").strip()
            if line.lower() == "done":
                break
            
            if ":" in line:
                channel, user_id = line.split(":", 1)
                channels[channel.strip()] = user_id.strip()
                print(f"  ✓ 已添加：{channel} -> {user_id}")
            else:
                print("  ✗ 格式错误，请使用 渠道名：用户 ID")
        
        if len(channels) >= 2:
            note = input("\n备注（可选，直接回车跳过）: ").strip()
            result = await manager.create_binding(channels, note)
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n✗ 至少需要绑定 2 个渠道")
    
    elif choice == "2":
        # 查询绑定
        print("\n🔍 查询绑定关系")
        channel = input("渠道名称: ").strip()
        user_id = input("用户 ID: ").strip()
        
        binding = await manager.get_binding(channel, user_id)
        
        if binding:
            print("\n✅ 找到绑定关系:")
            print(json.dumps(binding, ensure_ascii=False, indent=2))
        else:
            print("\n❌ 未找到绑定关系")
    
    elif choice == "3":
        # 列出所有绑定
        print("\n📋 所有绑定关系")
        bindings = await manager.list_all_bindings()
        
        if bindings:
            for i, binding in enumerate(bindings, 1):
                print(f"\n[{i}] {binding['link_id']}")
                print(f"    渠道：{', '.join(binding['channels'].keys())}")
                print(f"    创建时间：{binding['created_at']}")
                if binding.get('user_note'):
                    print(f"    备注：{binding['user_note']}")
        else:
            print("\n暂无绑定关系")
    
    elif choice == "4":
        # 解除绑定
        print("\n❌ 解除绑定")
        link_id = input("绑定关系 ID: ").strip()
        
        confirm = input("确认删除？(y/n): ").strip().lower()
        if confirm == "y":
            result = await manager.remove_binding(link_id)
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("已取消")
    
    elif choice == "5":
        # 查看跨渠道记忆
        print("\n📖 查看跨渠道记忆")
        channel = input("渠道名称: ").strip()
        user_id = input("用户 ID: ").strip()
        days = input("查询天数 (默认 7): ").strip() or "7"
        
        memories = await manager.get_cross_channel_memories(
            channel, user_id, int(days)
        )
        
        print("\n" + json.dumps(memories, ensure_ascii=False, indent=2))
    
    elif choice == "0":
        print("\n👋 再见!")
        return
    
    else:
        print("\n✗ 无效选项")
    
    # 递归调用，继续操作
    await interactive_bind()


# CLI 入口
async def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀多渠道绑定管理工具")
    parser.add_argument("--bind", action="store_true", help="交互式绑定")
    parser.add_argument("--query", nargs=2, metavar=("CHANNEL", "USER_ID"), 
                       help="查询绑定关系")
    parser.add_argument("--list", action="store_true", help="列出所有绑定")
    parser.add_argument("--memories", nargs=2, metavar=("CHANNEL", "USER_ID"),
                       help="查看跨渠道记忆")
    parser.add_argument("--days", type=int, default=7, help="查询记忆的天数")
    
    args = parser.parse_args()
    
    manager = ChannelLinkingManager()
    
    if args.bind:
        await interactive_bind()
    
    elif args.query:
        channel, user_id = args.query
        binding = await manager.get_binding(channel, user_id)
        if binding:
            print(json.dumps(binding, ensure_ascii=False, indent=2))
        else:
            print("未找到绑定关系")
    
    elif args.list:
        bindings = await manager.list_all_bindings()
        print(json.dumps(bindings, ensure_ascii=False, indent=2))
    
    elif args.memories:
        channel, user_id = args.memories
        memories = await manager.get_cross_channel_memories(channel, user_id, args.days)
        print(json.dumps(memories, ensure_ascii=False, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
