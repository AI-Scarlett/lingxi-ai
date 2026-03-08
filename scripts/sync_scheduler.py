"""
灵犀记忆同步调度器 - 凌晨 2 点定时同步
Memory Sync Scheduler for Lingxi - Daily 2AM Sync

作者：斯嘉丽 Scarlett
日期：2026-03-08

功能：
1. 定时扫描各渠道记忆
2. 过滤/脱敏处理
3. 语义去重
4. 写入共享记忆库
5. 记录同步日志
"""

import asyncio
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import aiofiles
import aiofiles.os

from shared_memory import (
    SharedMemoryStructure, 
    SharedMemoryService,
    SyncLog
)


class MemorySyncScheduler:
    """
    记忆同步调度器
    
    定时任务：每天凌晨 2 点执行
    cron: "0 2 * * *"
    """
    
    def __init__(self, workspace_path: str = "~/.openclaw/workspace"):
        self.workspace = Path(workspace_path).expanduser()
        self.memory_dir = self.workspace / "memory"
        self.shared_store = SharedMemoryStructure()
        self.shared_service = SharedMemoryService()
        
        # 渠道列表（可扩展）
        self.channels = ["feishu", "qqbot", "wechat", "whatsapp", "telegram", "dingtalk", "wecom"]
        
        # 同步配置
        self.sync_config = {
            "dedup_threshold": 0.8,  # 去重相似度阈值
            "privacy_keywords": [     # 隐私关键词（需要脱敏）
                "密码", "password", "token", "密钥", "secret",
                "身份证", "银行卡", "手机号", "邮箱"
            ],
            "retain_days": 30,  # 保留天数
        }
    
    async def initialize(self):
        """初始化"""
        await self.shared_store.ensure_structure()
    
    async def run_sync(self, force: bool = False) -> SyncLog:
        """
        执行同步任务
        
        Args:
            force: 是否强制执行（忽略时间检查）
        
        Returns:
            同步日志
        """
        await self.initialize()
        
        sync_log = SyncLog(
            sync_id=f"sync-{int(time.time())}",
            scheduled_time="02:00",
            started_at=time.time(),
            status="running"
        )
        
        try:
            # 1. 扫描各渠道记忆
            channel_memories = await self._scan_all_channels()
            sync_log.channels_synced = list(channel_memories.keys())
            
            # 2. 处理每个渠道的记忆
            total_synced = 0
            for channel, memories in channel_memories.items():
                for user_id, user_memories in memories.items():
                    # 3. 过滤和脱敏
                    processed = await self._process_memories(user_memories)
                    
                    # 4. 语义去重
                    deduped = await self._deduplicate_memories(processed)
                    
                    # 5. 写入共享记忆库
                    for date, content in deduped.items():
                        await self.shared_service.save_memory(
                            channel=channel,
                            user_id=user_id,
                            content=content,
                            date=date,
                            metadata={
                                "timestamp": time.time(),
                                "topic": "每日同步",
                                "sync_id": sync_log.sync_id
                            }
                        )
                        total_synced += 1
            
            sync_log.memories_synced = total_synced
            sync_log.status = "success"
            
        except Exception as e:
            sync_log.status = "failed"
            sync_log.errors.append({
                "error": str(e),
                "timestamp": time.time()
            })
            raise
        
        finally:
            sync_log.completed_at = time.time()
            
            # 6. 记录同步日志
            await self.shared_store.save_sync_log(sync_log)
        
        return sync_log
    
    async def _scan_all_channels(self) -> Dict[str, Dict[str, List[Dict]]]:
        """
        扫描所有渠道的记忆
        
        Returns:
            {channel: {user_id: [memories]}}
        """
        channel_memories = {}
        
        # 扫描共享记忆库中的用户目录
        if await aiofiles.os.path.exists(self.shared_store.users_dir):
            for channel_dir in self.shared_store.users_dir.iterdir():
                if not channel_dir.is_dir():
                    continue
                
                channel = channel_dir.name
                
                # 跳过特殊目录
                if channel.startswith('.'):
                    continue
                
                channel_memories[channel] = {}
                
                # 扫描该渠道下的所有用户
                for user_dir in channel_dir.iterdir():
                    if not user_dir.is_dir():
                        continue
                    
                    # 从路径反推 user_id（简化处理，实际应该从 profile 读取）
                    user_id = user_dir.name
                    
                    # 读取记忆文件
                    memories = await self._read_user_memories(user_dir)
                    if memories:
                        channel_memories[channel][user_id] = memories
        
        return channel_memories
    
    async def _read_user_memories(self, user_dir: Path) -> List[Dict]:
        """读取用户记忆文件"""
        memories = []
        memories_dir = user_dir / "memories"
        
        if not await aiofiles.os.path.exists(memories_dir):
            return memories
        
        # 读取最近 N 天的记忆
        cutoff_date = datetime.now() - timedelta(days=self.sync_config["retain_days"])
        
        # glob 不是异步的，需要同步调用
        for file_path in memories_dir.glob("*.md"):
            try:
                # 从文件名提取日期
                date_str = file_path.stem  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    continue
                
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    memories.append({
                        "date": date_str,
                        "content": content,
                        "path": str(file_path)
                    })
            except Exception as e:
                print(f"读取记忆文件失败 {file_path}: {e}")
        
        return memories
    
    async def _process_memories(self, memories: List[Dict]) -> Dict[str, str]:
        """
        处理记忆：过滤和脱敏
        
        Args:
            memories: 记忆列表
        
        Returns:
            {date: processed_content}
        """
        processed = {}
        
        for memory in memories:
            content = memory["content"]
            date = memory["date"]
            
            # 1. 脱敏处理
            sanitized = self._sanitize_content(content)
            
            # 2. 添加同步标记
            marked = f"""
> 🔄 **同步时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 📦 **同步 ID:** {memory.get('sync_id', 'manual')}

{sanitized}
"""
            processed[date] = marked
        
        return processed
    
    def _sanitize_content(self, content: str) -> str:
        """
        脱敏处理：移除或替换敏感信息
        
        Args:
            content: 原始内容
        
        Returns:
            脱敏后的内容
        """
        sanitized = content
        
        # 简单关键词替换（实际应该用更智能的 NLP 方法）
        for keyword in self.sync_config["privacy_keywords"]:
            if keyword.lower() in sanitized.lower():
                # 替换为 [已脱敏]
                import re
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                sanitized = pattern.sub("[已脱敏]", sanitized)
        
        return sanitized
    
    async def _deduplicate_memories(self, memories: Dict[str, str]) -> Dict[str, str]:
        """
        语义去重
        
        Args:
            memories: {date: content}
        
        Returns:
            去重后的记忆
        """
        # 简单版本：基于内容哈希去重
        # 实际应该用 embedding 相似度
        
        seen_hashes: Set[str] = set()
        deduped = {}
        
        for date, content in memories.items():
            # 计算内容哈希（忽略空白字符）
            normalized = ''.join(content.split()).encode('utf-8')
            content_hash = hashlib.md5(normalized).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduped[date] = content
        
        return deduped
    
    async def get_next_sync_time(self) -> datetime:
        """获取下次同步时间（下一个凌晨 2 点）"""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        next_sync = tomorrow.replace(hour=2, minute=0, second=0, microsecond=0)
        return next_sync
    
    async def should_sync(self) -> bool:
        """检查是否应该执行同步"""
        # 检查当前时间是否接近凌晨 2 点
        now = datetime.now()
        
        # 允许在 2:00-2:59 之间执行
        if now.hour == 2:
            # 检查今天是否已同步
            today = now.strftime("%Y-%m-%d")
            logs = await self.shared_store.get_sync_logs(today[:7], today[:7])
            
            # 过滤今天的日志
            today_logs = [
                log for log in logs
                if datetime.fromtimestamp(log.started_at).strftime("%Y-%m-%d") == today
            ]
            
            # 如果今天没有成功同步过，则执行
            return not any(log.status == "success" for log in today_logs)
        
        return False


class SyncSchedulerService:
    """
    同步调度服务 - 提供外部调用接口
    """
    
    def __init__(self):
        self.scheduler = MemorySyncScheduler()
        self.shared_service = SharedMemoryService()
        self._initialized = False
    
    async def initialize(self):
        """初始化"""
        if not self._initialized:
            await self.scheduler.initialize()
            self._initialized = True
    
    async def sync_now(self) -> Dict:
        """立即执行同步"""
        await self.initialize()
        log = await self.scheduler.run_sync(force=True)
        return {
            "status": log.status,
            "sync_id": log.sync_id,
            "channels_synced": log.channels_synced,
            "memories_synced": log.memories_synced,
            "started_at": datetime.fromtimestamp(log.started_at).isoformat(),
            "completed_at": datetime.fromtimestamp(log.completed_at).isoformat() if log.completed_at else None,
            "errors": log.errors
        }
    
    async def get_sync_history(self, days: int = 7) -> List[Dict]:
        """获取同步历史"""
        await self.initialize()
        return await self.shared_service.get_sync_history(days)
    
    async def get_next_sync_time(self) -> str:
        """获取下次同步时间"""
        await self.initialize()
        next_time = await self.scheduler.get_next_sync_time()
        return next_time.isoformat()
    
    async def check_sync_status(self) -> Dict:
        """检查同步状态"""
        await self.initialize()
        
        now = datetime.now()
        next_sync = await self.scheduler.get_next_sync_time()
        
        # 获取最近一次同步
        logs = await self.get_sync_history(1)
        last_sync = logs[0] if logs else None
        
        return {
            "current_time": now.isoformat(),
            "next_sync_time": next_sync.isoformat(),
            "hours_until_sync": (next_sync - now).total_seconds() / 3600,
            "last_sync": last_sync,
            "should_sync_now": await self.scheduler.should_sync()
        }


# CLI 入口
async def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀记忆同步调度器")
    parser.add_argument("--sync-now", action="store_true", help="立即执行同步")
    parser.add_argument("--status", action="store_true", help="查看同步状态")
    parser.add_argument("--history", type=int, default=0, help="查看历史同步记录（天数）")
    parser.add_argument("--next", action="store_true", help="查看下次同步时间")
    
    args = parser.parse_args()
    
    service = SyncSchedulerService()
    
    if args.sync_now:
        print("🔄 开始执行同步...")
        result = await service.sync_now()
        print(f"✅ 同步完成")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.status:
        print("📊 同步状态")
        status = await service.check_sync_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.history > 0:
        print(f"📜 最近 {args.history} 天的同步历史")
        history = await service.get_sync_history(args.history)
        print(json.dumps(history, ensure_ascii=False, indent=2))
    
    elif args.next:
        print("⏰ 下次同步时间")
        next_time = await service.get_next_sync_time()
        print(next_time)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
