#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 记忆持久化存储系统

核心特性：
1. JSONL 格式存储 - 通用、易读、易迁移
2. 用户级隔离 - 每个用户独立记忆文件
3. 导出/导入 - 支持迁移到不同设备/智能体
4. 自动备份 - 定期备份防丢失
5. 压缩打包 - 一键打包所有记忆

文件结构：
```
memory_storage/
├── users/
│   ├── user_123/
│   │   ├── memories.jsonl      # 主记忆文件
│   │   ├── preferences.jsonl   # 偏好记忆
│   │   ├── relationships.jsonl # 关系记忆
│   │   └── knowledge.jsonl     # 知识记忆
│   └── user_456/
│       └── ...
├── backups/
│   └── user_123_20260304_112000.zip
└── exports/
    └── user_123_memories_20260304.json
```
"""

import os
import json
import gzip
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, asdict
import zipfile

# ==================== 数据模型 ====================

@dataclass
class Memory:
    """记忆数据模型"""
    id: str
    user_id: str
    content: str
    category: str  # preferences, relationships, knowledge, context
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = None
    tags: List[str] = None
    confidence: float = 1.0
    access_count: int = 0
    last_accessed: str = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        return cls(**data)
    
    def to_jsonl(self) -> str:
        """转为 JSONL 格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_jsonl(cls, line: str) -> 'Memory':
        """从 JSONL 解析"""
        return cls.from_dict(json.loads(line))

# ==================== 持久化存储引擎 ====================

class MemoryPersistence:
    """记忆持久化存储引擎"""
    
    def __init__(self, base_path: str = "~/.openclaw/workspace/memory_storage"):
        self.base_path = Path(base_path).expanduser()
        self.users_path = self.base_path / "users"
        self.backups_path = self.base_path / "backups"
        self.exports_path = self.base_path / "exports"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 内存缓存（加速访问）
        self._cache: Dict[str, Dict[str, Memory]] = {}
        self._load_all_to_cache()
    
    def _ensure_directories(self):
        """确保所有目录存在"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.users_path.mkdir(parents=True, exist_ok=True)
        self.backups_path.mkdir(parents=True, exist_ok=True)
        self.exports_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_path(self, user_id: str) -> Path:
        """获取用户目录"""
        user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
        return self.users_path / f"user_{user_hash}"
    
    def _get_memory_file(self, user_id: str, category: str = "memories") -> Path:
        """获取记忆文件路径"""
        user_path = self._get_user_path(user_id)
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path / f"{category}.jsonl"
    
    def _load_all_to_cache(self):
        """启动时加载所有记忆到缓存"""
        if not self.users_path.exists():
            return
        
        for user_dir in self.users_path.iterdir():
            if not user_dir.is_dir():
                continue
            
            user_id = user_dir.name  # user_xxx
            self._cache[user_id] = {}
            
            for memory_file in user_dir.glob("*.jsonl"):
                category = memory_file.stem
                self._load_category_to_cache(user_id, category)
    
    def _load_category_to_cache(self, user_id: str, category: str):
        """加载单个分类到缓存"""
        file_path = self._get_memory_file(user_id, category)
        if not file_path.exists():
            return
        
        key_prefix = f"{category}:"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    memory = Memory.from_jsonl(line)
                    key = f"{key_prefix}{memory.id}"
                    self._cache[user_id][key] = memory
                except Exception as e:
                    print(f"⚠️ 加载记忆失败：{e}")
    
    # ==================== 基础 CRUD ====================
    
    def add(self, memory: Memory) -> bool:
        """添加记忆"""
        user_id = memory.user_id
        category = memory.category
        
        # 确保用户缓存存在
        if user_id not in self._cache:
            self._cache[user_id] = {}
        
        # 添加到缓存
        key = f"{category}:{memory.id}"
        if key in self._cache[user_id]:
            return False  # 已存在
        
        self._cache[user_id][key] = memory
        
        # 追加到文件
        file_path = self._get_memory_file(user_id, category)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(memory.to_jsonl() + '\n')
        
        return True
    
    def get(self, user_id: str, memory_id: str, category: str = "memories") -> Optional[Memory]:
        """获取记忆"""
        key = f"{category}:{memory_id}"
        
        if user_id not in self._cache:
            return None
        
        memory = self._cache[user_id].get(key)
        
        # 更新访问统计
        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now().isoformat()
            self._update_memory(memory)
        
        return memory
    
    def update(self, memory: Memory) -> bool:
        """更新记忆"""
        memory.updated_at = datetime.now().isoformat()
        return self._update_memory(memory)
    
    def _update_memory(self, memory: Memory) -> bool:
        """内部更新方法"""
        user_id = memory.user_id
        category = memory.category
        key = f"{category}:{memory.id}"
        
        if user_id not in self._cache or key not in self._cache[user_id]:
            return False
        
        # 更新缓存
        self._cache[user_id][key] = memory
        
        # 重写整个文件（简单但低效，后续可优化）
        self._rewrite_file(user_id, category)
        
        return True
    
    def delete(self, user_id: str, memory_id: str, category: str = "memories") -> bool:
        """删除记忆"""
        key = f"{category}:{memory_id}"
        
        if user_id not in self._cache or key not in self._cache[user_id]:
            return False
        
        del self._cache[user_id][key]
        
        # 重写文件
        self._rewrite_file(user_id, category)
        
        return True
    
    def _rewrite_file(self, user_id: str, category: str):
        """重写文件（删除后重建）"""
        file_path = self._get_memory_file(user_id, category)
        
        # 获取该分类所有记忆
        key_prefix = f"{category}:"
        memories = [
            m for k, m in self._cache.get(user_id, {}).items()
            if k.startswith(key_prefix)
        ]
        
        # 重写文件
        with open(file_path, 'w', encoding='utf-8') as f:
            for memory in memories:
                f.write(memory.to_jsonl() + '\n')
    
    def list(self, user_id: str, category: str = "memories", 
             limit: int = 100, offset: int = 0) -> List[Memory]:
        """列出记忆"""
        key_prefix = f"{category}:"
        
        if user_id not in self._cache:
            return []
        
        memories = [
            m for k, m in self._cache[user_id].items()
            if k.startswith(key_prefix)
        ]
        
        # 按创建时间排序
        memories.sort(key=lambda m: m.created_at, reverse=True)
        
        return memories[offset:offset+limit]
    
    def search(self, user_id: str, query: str, 
               category: str = None) -> List[Memory]:
        """搜索记忆（关键词匹配）"""
        results = []
        query_lower = query.lower()
        
        user_cache = self._cache.get(user_id, {})
        
        for key, memory in user_cache.items():
            # 分类过滤
            if category and not key.startswith(f"{category}:"):
                continue
            
            # 关键词匹配
            if (query_lower in memory.content.lower() or
                query_lower in ' '.join(memory.tags or []).lower()):
                results.append(memory)
        
        # 按相关性排序（访问次数 + 置信度）
        results.sort(key=lambda m: m.access_count + m.confidence, reverse=True)
        
        return results
    
    # ==================== 统计信息 ====================
    
    def get_stats(self, user_id: str = None) -> Dict:
        """获取统计信息"""
        if user_id:
            user_cache = self._cache.get(user_id, {})
            total = len(user_cache)
            
            # 按分类统计
            categories = {}
            for key in user_cache:
                cat = key.split(':')[0]
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "user_id": user_id,
                "total_memories": total,
                "by_category": categories
            }
        else:
            # 所有用户
            total_users = len(self._cache)
            total_memories = sum(len(c) for c in self._cache.values())
            
            return {
                "total_users": total_users,
                "total_memories": total_memories,
                "storage_path": str(self.base_path)
            }
    
    # ==================== 导出/导入 ====================
    
    def export_user(self, user_id: str, output_path: str = None) -> str:
        """导出用户所有记忆为 JSON 文件"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.exports_path / f"user_{user_id}_memories_{timestamp}.json"
        else:
            output_path = Path(output_path)
        
        user_cache = self._cache.get(user_id, {})
        
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "user_id": user_id,
            "memories": [m.to_dict() for m in user_cache.values()]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def import_user(self, import_path: str, user_id: str = None) -> Dict:
        """从 JSON 文件导入记忆"""
        import_path = Path(import_path)
        
        if not import_path.exists():
            raise FileNotFoundError(f"导入文件不存在：{import_path}")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证格式
        if "version" not in data or "memories" not in data:
            raise ValueError("无效的导入文件格式")
        
        # 使用新 user_id（如果提供）
        new_user_id = user_id or data.get("user_id")
        if not new_user_id:
            raise ValueError("必须提供 user_id")
        
        # 导入记忆
        imported_count = 0
        failed_count = 0
        
        for mem_dict in data["memories"]:
            try:
                # 更新 user_id
                mem_dict["user_id"] = new_user_id
                memory = Memory.from_dict(mem_dict)
                
                # 添加到存储
                if self.add(memory):
                    imported_count += 1
                else:
                    failed_count += 1  # 已存在
            except Exception as e:
                print(f"⚠️ 导入失败：{e}")
                failed_count += 1
        
        return {
            "imported": imported_count,
            "failed": failed_count,
            "user_id": new_user_id
        }
    
    # ==================== 备份/恢复 ====================
    
    def backup_user(self, user_id: str, backup_path: str = None) -> str:
        """备份用户记忆（压缩打包）"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backups_path / f"user_{user_id}_{timestamp}.zip"
        else:
            backup_path = Path(backup_path)
        
        user_path = self._get_user_path(user_id)
        
        if not user_path.exists():
            raise FileNotFoundError(f"用户记忆不存在：{user_id}")
        
        # 创建 ZIP 压缩包
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in user_path.glob("*.jsonl"):
                arcname = f"memories/{file_path.name}"
                zipf.write(file_path, arcname)
            
            # 添加元数据
            metadata = {
                "user_id": user_id,
                "backed_up_at": datetime.now().isoformat(),
                "file_count": len(list(user_path.glob("*.jsonl")))
            }
            
            zipf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
        
        return str(backup_path)
    
    def restore_user(self, backup_path: str, user_id: str = None) -> Dict:
        """从备份恢复用户记忆"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在：{backup_path}")
        
        # 解压备份
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(tmpdir)
            
            # 读取元数据
            metadata_path = Path(tmpdir) / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                original_user_id = metadata.get("user_id")
            else:
                original_user_id = None
            
            # 使用新 user_id（如果提供）
            new_user_id = user_id or original_user_id
            if not new_user_id:
                raise ValueError("无法确定 user_id")
            
            # 导入记忆文件
            restored_count = 0
            memories_dir = Path(tmpdir) / "memories"
            
            if memories_dir.exists():
                for jsonl_file in memories_dir.glob("*.jsonl"):
                    category = jsonl_file.stem
                    
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                memory = Memory.from_jsonl(line)
                                memory.user_id = new_user_id
                                
                                if self.add(memory):
                                    restored_count += 1
                            except Exception as e:
                                print(f"⚠️ 恢复失败：{e}")
        
        return {
            "restored": restored_count,
            "user_id": new_user_id,
            "original_user_id": original_user_id
        }
    
    # ==================== 迁移工具 ====================
    
    def create_migration_package(self, user_id: str, output_path: str = None) -> str:
        """创建迁移包（包含所有记忆 + 元数据）"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.exports_path / f"migration_{user_id}_{timestamp}.zip"
        else:
            output_path = Path(output_path)
        
        user_path = self._get_user_path(user_id)
        
        if not user_path.exists():
            raise FileNotFoundError(f"用户记忆不存在：{user_id}")
        
        # 创建迁移包
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有记忆文件
            for file_path in user_path.glob("*.jsonl"):
                arcname = f"memories/{file_path.name}"
                zipf.write(file_path, arcname)
            
            # 添加迁移说明
            readme = f"""# 灵犀记忆迁移包

**用户 ID:** {user_id}
**创建时间:** {datetime.now().isoformat()}
**版本:** 1.0

## 使用方法

### 方法 1: 在新设备导入
1. 将迁移包复制到新设备
2. 使用 import_user() 或命令行工具导入

### 方法 2: 直接解压
1. 解压到 ~/.openclaw/workspace/memory_storage/users/
2. 重启灵犀系统

## 文件说明
- memories.jsonl - 主记忆
- preferences.jsonl - 偏好设置
- relationships.jsonl - 关系网络
- knowledge.jsonl - 知识库
"""
            zipf.writestr("README.md", readme)
            
            # 添加导入脚本
            import_script = f"""#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from memory_persistence import MemoryPersistence

persistence = MemoryPersistence()
result = persistence.import_user("{output_path.name}", "{user_id}")
print(f"导入完成：{{result['imported']}} 条记忆")
"""
            zipf.writestr("import.py", import_script)
        
        return str(output_path)
    
    def merge_users(self, source_user_id: str, target_user_id: str) -> Dict:
        """合并两个用户的记忆（用于迁移到新智能体）"""
        source_cache = self._cache.get(source_user_id, {})
        
        merged_count = 0
        skipped_count = 0
        
        for key, memory in source_cache.items():
            # 复制记忆，更新 user_id
            new_memory = Memory(
                id=memory.id,
                user_id=target_user_id,
                content=memory.content,
                category=memory.category,
                created_at=memory.created_at,
                updated_at=datetime.now().isoformat(),
                metadata=memory.metadata,
                tags=memory.tags,
                confidence=memory.confidence,
                access_count=memory.access_count,
                last_accessed=memory.last_accessed
            )
            
            if self.add(new_memory):
                merged_count += 1
            else:
                skipped_count += 1  # 已存在
        
        return {
            "merged": merged_count,
            "skipped": skipped_count,
            "source_user": source_user_id,
            "target_user": target_user_id
        }
    
    # ==================== 清理工具 ====================
    
    def cleanup_old_memories(self, user_id: str, days: int = 365) -> int:
        """清理超过指定天数的记忆"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        deleted_count = 0
        
        for category in ["memories", "preferences", "relationships", "knowledge"]:
            memories = self.list(user_id, category, limit=10000)
            
            for memory in memories:
                try:
                    created = datetime.fromisoformat(memory.created_at).timestamp()
                    if created < cutoff:
                        self.delete(user_id, memory.id, category)
                        deleted_count += 1
                except Exception as e:
                    pass
        
        return deleted_count
    
    def compact_storage(self, user_id: str) -> Dict:
        """压缩存储（去重 + 清理）"""
        # TODO: 实现智能去重
        return {
            "status": "not_implemented",
            "message": "压缩功能开发中"
        }

# ==================== 命令行工具 ====================

def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="灵犀记忆持久化存储工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # stats 命令
    subparsers.add_parser("stats", help="查看统计信息")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出用户记忆")
    export_parser.add_argument("user_id", help="用户 ID")
    export_parser.add_argument("-o", "--output", help="输出文件路径")
    
    # import 命令
    import_parser = subparsers.add_parser("import", help="导入用户记忆")
    import_parser.add_argument("input_path", help="输入文件路径")
    import_parser.add_argument("-u", "--user", dest="user_id", help="目标用户 ID")
    
    # backup 命令
    backup_parser = subparsers.add_parser("backup", help="备份用户记忆")
    backup_parser.add_argument("user_id", help="用户 ID")
    backup_parser.add_argument("-o", "--output", help="备份文件路径")
    
    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复用户记忆")
    restore_parser.add_argument("backup_path", help="备份文件路径")
    restore_parser.add_argument("-u", "--user", dest="user_id", help="目标用户 ID")
    
    # migrate 命令
    migrate_parser = subparsers.add_parser("migrate", help="创建迁移包")
    migrate_parser.add_argument("user_id", help="用户 ID")
    migrate_parser.add_argument("-o", "--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    persistence = MemoryPersistence()
    
    if args.command == "stats":
        stats = persistence.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.command == "export":
        output = persistence.export_user(args.user_id, args.output)
        print(f"✅ 导出完成：{output}")
    
    elif args.command == "import":
        result = persistence.import_user(args.input_path, args.user_id)
        print(f"✅ 导入完成：{result['imported']} 条记忆，失败 {result['failed']} 条")
    
    elif args.command == "backup":
        output = persistence.backup_user(args.user_id, args.output)
        print(f"✅ 备份完成：{output}")
    
    elif args.command == "restore":
        result = persistence.restore_user(args.backup_path, args.user_id)
        print(f"✅ 恢复完成：{result['restored']} 条记忆")
    
    elif args.command == "migrate":
        output = persistence.create_migration_package(args.user_id, args.output)
        print(f"✅ 迁移包创建完成：{output}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
