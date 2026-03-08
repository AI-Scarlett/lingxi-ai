"""
灵犀共享记忆库 - 跨渠道记忆同步与查询
Shared Memory Library for Lingxi - Cross-Channel Memory Sync & Query

作者：斯嘉丽 Scarlett
日期：2026-03-08

功能：
1. 按渠道 + 用户 ID 组织记忆存储
2. 凌晨 2 点定时同步各渠道记忆到共享库
3. 支持用户手动绑定多渠道
4. 跨渠道记忆查询
"""

import asyncio
import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timedelta
import aiofiles
import aiofiles.os


@dataclass
class ChannelLink:
    """多渠道绑定关系"""
    link_id: str
    user_note: str                   # 用户备注（可选）
    channels: Dict[str, str]         # channel_name -> channel_user_id
    created_at: float
    verified_by_user: bool = True    # 是否经用户确认
    active: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ChannelLink":
        return cls(**data)
    
    def get_channel_id(self, channel: str) -> Optional[str]:
        """获取指定渠道的 ID"""
        return self.channels.get(channel)
    
    def get_all_channel_ids(self) -> Dict[str, str]:
        """获取所有绑定的渠道 ID"""
        return self.channels.copy()
    
    def add_channel(self, channel: str, user_id: str):
        """添加渠道绑定"""
        self.channels[channel] = user_id
    
    def remove_channel(self, channel: str):
        """移除渠道绑定"""
        if channel in self.channels:
            del self.channels[channel]


@dataclass
class SyncLog:
    """同步日志记录"""
    sync_id: str
    scheduled_time: str              # 计划同步时间（如 "02:00"）
    started_at: float
    completed_at: Optional[float] = None
    status: str = "running"          # running/success/failed/partial
    channels_synced: List[str] = field(default_factory=list)
    memories_synced: int = 0
    errors: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SyncLog":
        return cls(**data)


class SharedMemoryStructure:
    """
    共享记忆库文件系统结构
    
    memory/shared/
    ├── users/                       # 按渠道 + 用户 ID 组织
    │   ├── feishu/
    │   │   └── ou_4192609eb71f18ae82f9163f02bef144/
    │   │       ├── profile.md       # 用户画像
    │   │       ├── preferences.md   # 偏好设置
    │   │       └── memories/        # 记忆文件（按日期）
    │   │           └── 2026-03-08.md
    │   ├── qqbot/
    │   │   └── 7941E72A6252ADA08CC281AC26D9920B/
    │   │       └── ...
    │   └── whatsapp/
    │       └── +8613800138000/
    │           └── ...
    ├── cross-channel-links/         # 多渠道绑定关系
    │   ├── index.json               # 绑定关系索引
    │   └── links/                   # 详细绑定信息
    │       └── link-001.json
    ├── sync-logs/                   # 同步日志
    │   └── 2026-03/
    │       └── 2026-03-08.json
    └── config.json                  # 共享记忆库配置
    """
    
    def __init__(self, base_path: str = "~/.openclaw/workspace/memory/shared"):
        self.base = Path(base_path).expanduser()
        
        # 定义目录结构
        self.users_dir = self.base / "users"
        self.links_dir = self.base / "cross-channel-links"
        self.links_index = self.links_dir / "index.json"
        self.links_detail_dir = self.links_dir / "links"
        self.sync_logs_dir = self.base / "sync-logs"
        self.config_file = self.base / "config.json"
        
        # 渠道映射（用于路径规范化）
        self.channel_aliases = {
            "feishu": "feishu",
            "qqbot": "qqbot",
            "wechat": "wechat",
            "whatsapp": "whatsapp",
            "telegram": "telegram",
            "dingtalk": "dingtalk",
            "wecom": "wecom",
        }
    
    async def ensure_structure(self):
        """确保目录结构存在"""
        await aiofiles.os.makedirs(self.users_dir, exist_ok=True)
        await aiofiles.os.makedirs(self.links_detail_dir, exist_ok=True)
        await aiofiles.os.makedirs(self.sync_logs_dir, exist_ok=True)
        
        # 初始化索引文件
        if not await aiofiles.os.path.exists(self.links_index):
            async with aiofiles.open(self.links_index, 'w', encoding='utf-8') as f:
                await f.write(json.dumps({
                    "links": [],
                    "last_updated": time.time()
                }, ensure_ascii=False, indent=2))
        
        # 初始化配置文件
        if not await aiofiles.os.path.exists(self.config_file):
            async with aiofiles.open(self.config_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps({
                    "version": "1.0",
                    "created_at": time.time(),
                    "sync_schedule": "0 2 * * *",  # 凌晨 2 点
                    "cross_channel_enabled": True,
                    "privacy_mode": "opt-in"  # opt-in: 用户确认后才共享
                }, ensure_ascii=False, indent=2))
    
    def _get_user_path(self, channel: str, user_id: str) -> Path:
        """获取用户记忆存储路径"""
        channel = self.channel_aliases.get(channel.lower(), channel.lower())
        # 对 user_id 进行哈希，避免特殊字符问题
        safe_user_id = hashlib.md5(user_id.encode()).hexdigest()[:16]
        return self.users_dir / channel / safe_user_id
    
    async def get_user_dir(self, channel: str, user_id: str) -> Path:
        """获取并确保用户目录存在"""
        user_path = self._get_user_path(channel, user_id)
        await aiofiles.os.makedirs(user_path, exist_ok=True)
        await aiofiles.os.makedirs(user_path / "memories", exist_ok=True)
        return user_path
    
    async def save_user_profile(self, channel: str, user_id: str, profile: Dict):
        """保存用户画像"""
        user_path = await self.get_user_dir(channel, user_id)
        profile_file = user_path / "profile.md"
        
        content = f"""# 用户画像

**渠道:** {channel}  
**用户 ID:** {user_id}  
**更新时间:** {datetime.now().isoformat()}

## 基本信息
{json.dumps(profile, ensure_ascii=False, indent=2)}
"""
        async with aiofiles.open(profile_file, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def load_user_profile(self, channel: str, user_id: str) -> Optional[Dict]:
        """加载用户画像"""
        user_path = self._get_user_path(channel, user_id)
        profile_file = user_path / "profile.md"
        
        if not await aiofiles.os.path.exists(profile_file):
            return None
        
        async with aiofiles.open(profile_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            # 提取 JSON 部分
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(content[json_start:json_end])
            except Exception as e:
                pass
            return None
    
    async def save_memory(self, channel: str, user_id: str, date: str, memory_content: str):
        """保存记忆（按日期分文件）"""
        user_path = await self.get_user_dir(channel, user_id)
        memory_file = user_path / "memories" / f"{date}.md"
        
        # 如果文件存在，追加内容；否则创建新文件
        mode = 'a' if await aiofiles.os.path.exists(memory_file) else 'w'
        async with aiofiles.open(memory_file, mode, encoding='utf-8') as f:
            if mode == 'w':
                await f.write(f"# 记忆记录 - {date}\n\n")
            await f.write(memory_content + "\n\n")
    
    async def load_memory(self, channel: str, user_id: str, date: str) -> Optional[str]:
        """加载指定日期的记忆"""
        user_path = self._get_user_path(channel, user_id)
        memory_file = user_path / "memories" / f"{date}.md"
        
        if not await aiofiles.os.path.exists(memory_file):
            return None
        
        async with aiofiles.open(memory_file, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def load_memories_by_date_range(self, channel: str, user_id: str, 
                                          start_date: str, end_date: str) -> Dict[str, str]:
        """加载日期范围内的记忆"""
        user_path = self._get_user_path(channel, user_id)
        memories_dir = user_path / "memories"
        
        if not await aiofiles.os.path.exists(memories_dir):
            return {}
        
        memories = {}
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            memory_file = memories_dir / f"{date_str}.md"
            
            if await aiofiles.os.path.exists(memory_file):
                async with aiofiles.open(memory_file, 'r', encoding='utf-8') as f:
                    memories[date_str] = await f.read()
            
            current += timedelta(days=1)
        
        return memories
    
    # ========== 多渠道绑定管理 ==========
    
    async def create_channel_link(self, channels: Dict[str, str], user_note: str = "") -> ChannelLink:
        """创建多渠道绑定关系"""
        link_id = f"link-{int(time.time())}"
        link = ChannelLink(
            link_id=link_id,
            user_note=user_note,
            channels=channels,
            created_at=time.time(),
            verified_by_user=True
        )
        
        # 保存到详细文件
        link_file = self.links_detail_dir / f"{link_id}.json"
        async with aiofiles.open(link_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(link.to_dict(), ensure_ascii=False, indent=2))
        
        # 更新索引
        await self._update_links_index(link_id, "add")
        
        return link
    
    async def _update_links_index(self, link_id: str, action: str = "add"):
        """更新绑定关系索引"""
        index_data = {"links": [], "last_updated": time.time()}
        
        if await aiofiles.os.path.exists(self.links_index):
            async with aiofiles.open(self.links_index, 'r', encoding='utf-8') as f:
                try:
                    index_data = json.loads(await f.read())
                except Exception as e:
                    pass
        
        if action == "add":
            if link_id not in index_data["links"]:
                index_data["links"].append(link_id)
        elif action == "remove":
            if link_id in index_data["links"]:
                index_data["links"].remove(link_id)
        
        index_data["last_updated"] = time.time()
        
        async with aiofiles.open(self.links_index, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(index_data, ensure_ascii=False, indent=2))
    
    async def get_channel_link(self, link_id: str) -> Optional[ChannelLink]:
        """获取绑定关系"""
        link_file = self.links_detail_dir / f"{link_id}.json"
        
        if not await aiofiles.os.path.exists(link_file):
            return None
        
        async with aiofiles.open(link_file, 'r', encoding='utf-8') as f:
            data = json.loads(await f.read())
            return ChannelLink.from_dict(data)
    
    async def find_link_by_channel_id(self, channel: str, user_id: str) -> Optional[ChannelLink]:
        """通过渠道 ID 查找绑定关系"""
        if not await aiofiles.os.path.exists(self.links_index):
            return None
        
        async with aiofiles.open(self.links_index, 'r', encoding='utf-8') as f:
            index_data = json.loads(await f.read())
        
        for link_id in index_data["links"]:
            link = await self.get_channel_link(link_id)
            if link and link.active:
                if link.get_channel_id(channel) == user_id:
                    return link
        
        return None
    
    async def list_all_links(self) -> List[ChannelLink]:
        """列出所有绑定关系"""
        if not await aiofiles.os.path.exists(self.links_index):
            return []
        
        async with aiofiles.open(self.links_index, 'r', encoding='utf-8') as f:
            index_data = json.loads(await f.read())
        
        links = []
        for link_id in index_data["links"]:
            link = await self.get_channel_link(link_id)
            if link:
                links.append(link)
        
        return links
    
    # ========== 同步日志管理 ==========
    
    async def save_sync_log(self, log: SyncLog):
        """保存同步日志"""
        date = datetime.fromtimestamp(log.started_at).strftime("%Y-%m")
        log_dir = self.sync_logs_dir / date
        await aiofiles.os.makedirs(log_dir, exist_ok=True)
        
        log_file = log_dir / f"{datetime.fromtimestamp(log.started_at).strftime('%Y-%m-%d')}.json"
        
        # 如果文件存在，读取现有日志列表
        logs = []
        if await aiofiles.os.path.exists(log_file):
            async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.loads(await f.read())
                except Exception as e:
                    # 容错处理
                    logs = []
        
        logs.append(log.to_dict())
        
        async with aiofiles.open(log_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(logs, ensure_ascii=False, indent=2))
    
    async def get_sync_logs(self, start_date: str, end_date: str) -> List[SyncLog]:
        """获取日期范围内的同步日志"""
        logs = []
        
        start = datetime.strptime(start_date, "%Y-%m")
        end = datetime.strptime(end_date, "%Y-%m")
        
        current = start
        while current <= end:
            month_str = current.strftime("%Y-%m")
            log_dir = self.sync_logs_dir / month_str
            
            if await aiofiles.os.path.exists(log_dir):
                # glob 不是异步的，需要同步调用
                for file_path in log_dir.glob("*.json"):
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.loads(await f.read())
                            if isinstance(data, list):
                                logs.extend([SyncLog.from_dict(item) for item in data])
                            else:
                                logs.append(SyncLog.from_dict(data))
                        except Exception as e:
                            pass
            
            # 移动到下一月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return logs


class SharedMemoryService:
    """
    共享记忆库服务 - 统一接口
    
    提供：
    1. 跨渠道记忆查询
    2. 多渠道绑定管理
    3. 同步日志查询
    """
    
    def __init__(self):
        self.store = SharedMemoryStructure()
        self._initialized = False
    
    async def initialize(self):
        """初始化共享记忆库"""
        if not self._initialized:
            await self.store.ensure_structure()
            self._initialized = True
    
    # ========== 记忆存储与查询 ==========
    
    async def save_memory(self, channel: str, user_id: str, content: str, 
                         date: str = None, metadata: Dict = None):
        """
        保存记忆到共享记忆库
        
        Args:
            channel: 来源渠道
            user_id: 渠道用户 ID
            content: 记忆内容
            date: 日期（YYYY-MM-DD，默认今天）
            metadata: 元数据
        """
        await self.initialize()
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if metadata is None:
            metadata = {}
        
        # 格式化记忆内容
        memory_entry = f"""## [{metadata.get('timestamp', datetime.now().isoformat())}] {metadata.get('topic', '记忆')}

**渠道:** {channel}  
**用户 ID:** {user_id}

{content}

---
"""
        await self.store.save_memory(channel, user_id, date, memory_entry)
    
    async def query_memories(self, channel: str, user_id: str, 
                            start_date: str = None, end_date: str = None,
                            cross_channel: bool = True) -> Dict[str, str]:
        """
        查询记忆
        
        Args:
            channel: 当前渠道
            user_id: 当前渠道用户 ID
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            cross_channel: 是否跨渠道查询（默认 True）
        
        Returns:
            记忆字典 {date: content}
        """
        await self.initialize()
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        all_memories = {}
        
        # 查询当前渠道记忆
        current_memories = await self.store.load_memories_by_date_range(
            channel, user_id, start_date, end_date
        )
        all_memories.update({f"{channel}:{k}": v for k, v in current_memories.items()})
        
        # 如果启用跨渠道查询，查找绑定的其他渠道
        if cross_channel:
            link = await self.store.find_link_by_channel_id(channel, user_id)
            if link:
                for linked_channel, linked_user_id in link.channels.items():
                    if linked_channel != channel:
                        linked_memories = await self.store.load_memories_by_date_range(
                            linked_channel, linked_user_id, start_date, end_date
                        )
                        all_memories.update({f"{linked_channel}:{k}": v for k, v in linked_memories.items()})
        
        return all_memories
    
    # ========== 多渠道绑定管理 ==========
    
    async def bind_channels(self, channels: Dict[str, str], user_note: str = "") -> ChannelLink:
        """
        绑定多个渠道
        
        Args:
            channels: 渠道映射 {channel_name: user_id}
            user_note: 用户备注
        
        Returns:
            创建的绑定关系
        """
        await self.initialize()
        return await self.store.create_channel_link(channels, user_note)
    
    async def get_linked_channels(self, channel: str, user_id: str) -> Optional[Dict[str, str]]:
        """
        获取与当前渠道绑定的其他渠道
        
        Args:
            channel: 当前渠道
            user_id: 当前渠道用户 ID
        
        Returns:
            所有绑定的渠道映射，无绑定则返回 None
        """
        await self.initialize()
        link = await self.store.find_link_by_channel_id(channel, user_id)
        return link.get_all_channel_ids() if link else None
    
    async def list_bindings(self) -> List[Dict]:
        """列出所有渠道绑定"""
        await self.initialize()
        links = await self.store.list_all_links()
        return [link.to_dict() for link in links]
    
    # ========== 同步日志查询 ==========
    
    async def get_sync_history(self, days: int = 7) -> List[Dict]:
        """
        获取同步历史
        
        Args:
            days: 查询天数
        
        Returns:
            同步日志列表
        """
        await self.initialize()
        
        end = datetime.now()
        start = end - timedelta(days=days)
        
        logs = await self.store.get_sync_logs(
            start.strftime("%Y-%m"),
            end.strftime("%Y-%m")
        )
        
        # 过滤日期范围
        filtered = [
            log for log in logs
            if start <= datetime.fromtimestamp(log.started_at) <= end
        ]
        
        return [log.to_dict() for log in filtered]


# 便捷函数
async def save_memory(channel: str, user_id: str, content: str, **kwargs):
    """便捷函数：保存记忆"""
    service = SharedMemoryService()
    await service.save_memory(channel, user_id, content, **kwargs)


async def query_memories(channel: str, user_id: str, **kwargs) -> Dict[str, str]:
    """便捷函数：查询记忆"""
    service = SharedMemoryService()
    return await service.query_memories(channel, user_id, **kwargs)


async def bind_channels(channels: Dict[str, str], **kwargs) -> ChannelLink:
    """便捷函数：绑定渠道"""
    service = SharedMemoryService()
    return await service.bind_channels(channels, **kwargs)
