#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时推送调度器

功能：
- 定时推送审批通知（7:00/12:00/21:00）
- 飞书消息推送
- 审批结果处理
"""

import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json


class ApprovalScheduler:
    """审批调度器"""
    
    def __init__(self):
        self.approval_times = ["07:00", "12:00", "21:00"]  # 审批时间
        self.feishu_enabled = True
        self.feishu_user_id = "ou_4192609eb71f18ae82f9163f02bef144"
        self.max_proposals_per_notification = 10
        self.config_path = Path("~/.openclaw/workspace/.lingxi/improvement_config.json").expanduser()
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.approval_times = config.get("approval_times", self.approval_times)
                self.feishu_enabled = config.get("feishu_enabled", self.feishu_enabled)
                self.feishu_user_id = config.get("feishu_user_id", self.feishu_user_id)
                self.max_proposals_per_notification = config.get("max_proposals_per_notification", 10)
    
    def _save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "approval_times": self.approval_times,
            "feishu_enabled": self.feishu_enabled,
            "feishu_user_id": self.feishu_user_id,
            "max_proposals_per_notification": self.max_proposals_per_notification
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def get_next_approval_time(self) -> datetime:
        """获取下次审批时间"""
        now = datetime.now()
        
        for time_str in self.approval_times:
            hour, minute = map(int, time_str.split(":"))
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_time > now:
                return next_time
        
        # 如果今天的审批时间都过了，返回明天第一个
        hour, minute = map(int, self.approval_times[0].split(":"))
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def get_time_of_day(self) -> str:
        """获取当前时段"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 11:
            return "morning"
        elif 11 <= hour < 17:
            return "noon"
        elif 17 <= hour < 23:
            return "night"
        else:
            return "regular"
    
    async def send_approval_notification(self, proposals: List[dict]) -> bool:
        """发送审批通知"""
        if not proposals:
            print("ℹ️ 无待审批提案，跳过推送")
            return False
        
        if not self.feishu_enabled:
            print("ℹ️ 飞书推送已禁用")
            return False
        
        # 生成卡片
        from .approval import get_approval_manager
        
        manager = get_approval_manager()
        time_of_day = self.get_time_of_day()
        card = manager.generate_notification_card(proposals, time_of_day)
        
        # 发送飞书消息（简化实现，实际需调用飞书 API）
        print(f"📱 发送审批通知（{time_of_day}）：{len(proposals)} 个提案")
        print(f"   接收人：{self.feishu_user_id}")
        print(f"   卡片预览：{json.dumps(card, ensure_ascii=False)[:200]}...")
        
        # TODO: 实际调用飞书 API 发送消息
        # await self._send_feishu_message(card)
        
        return True
    
    async def _send_feishu_message(self, card: dict):
        """发送飞书消息（实际 API 调用）"""
        # TODO: 实现飞书 API 调用
        # 需要使用 feishu_doc 或 feishu_chat 工具
        pass
    
    async def process_user_approval(self, user_id: str, action: str, proposal_ids: List[str]) -> dict:
        """处理用户审批"""
        from .approval import get_approval_manager
        
        manager = get_approval_manager()
        results = await manager.process_approval(user_id, action, proposal_ids)
        
        print(f"✅ 处理审批：{action} {len(proposal_ids)} 个提案")
        print(f"   批准：{len(results['approved'])}")
        print(f"   拒绝：{len(results['rejected'])}")
        print(f"   推迟：{len(results['deferred'])}")
        
        return results
    
    def get_schedule_info(self) -> dict:
        """获取调度信息"""
        next_time = self.get_next_approval_time()
        now = datetime.now()
        
        return {
            "next_approval_time": next_time.isoformat(),
            "time_until_next": str(next_time - now),
            "approval_times": self.approval_times,
            "feishu_enabled": self.feishu_enabled,
            "feishu_user_id": self.feishu_user_id
        }
    
    async def run_scheduler(self):
        """运行调度器（后台任务）"""
        print("🕐 启动审批调度器...")
        
        while True:
            next_time = self.get_next_approval_time()
            now = datetime.now()
            
            # 计算等待时间
            wait_seconds = (next_time - now).total_seconds()
            
            print(f"⏰ 下次审批时间：{next_time.strftime('%H:%M:%S')}")
            print(f"   等待 {wait_seconds:.0f} 秒")
            
            # 等待到审批时间
            await asyncio.sleep(wait_seconds)
            
            # 获取待审批提案
            from .approval import get_approval_manager
            manager = get_approval_manager()
            proposals = await manager.get_pending_proposals(self.max_proposals_per_notification)
            
            # 发送通知
            if proposals:
                await self.send_approval_notification(proposals)
            else:
                print("ℹ️ 无待审批提案")
            
            # 等待 1 分钟，避免重复触发
            await asyncio.sleep(60)


# 全局实例
_scheduler = None


def get_scheduler() -> ApprovalScheduler:
    """获取调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ApprovalScheduler()
    return _scheduler


async def demo():
    """演示调度器"""
    print("="*60)
    print("🕐 审批调度器演示")
    print("="*60)
    
    scheduler = get_scheduler()
    
    # 显示调度信息
    info = scheduler.get_schedule_info()
    print(f"\n📅 下次审批：{info['next_approval_time']}")
    print(f"⏱️  剩余时间：{info['time_until_next']}")
    print(f"⏰ 审批时间：{info['approval_times']}")
    print(f"📱 飞书推送：{'✅ 启用' if info['feishu_enabled'] else '❌ 禁用'}")
    
    # 模拟添加提案
    from .approval import get_approval_manager
    manager = get_approval_manager()
    
    print("\n📝 添加测试提案...")
    await manager.add_proposal({
        "type": "save_memory",
        "title": "老板的工作习惯",
        "description": "从对话中提取：老板喜欢每天早上 9 点开始工作",
        "content": "老板喜欢每天早上 9 点开始工作，不喜欢被打扰",
        "importance": 9.0
    })
    
    # 获取待审批提案
    proposals = await manager.get_pending_proposals()
    print(f"✅ 待审批提案：{len(proposals)} 个")
    
    # 模拟发送通知
    if proposals:
        await scheduler.send_approval_notification(proposals)
    
    print("\n✨ 演示完成！")


if __name__ == "__main__":
    asyncio.run(demo())
