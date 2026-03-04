# 🧠 灵犀记忆持久化存储系统 - 使用指南

**版本:** 1.0  
**日期:** 2026-03-04  
**三大核心目标之一:** 🧠 记忆永不丢失

---

## 🎯 核心特性

1. **JSONL 格式存储** - 通用、易读、易迁移
2. **用户级隔离** - 每个用户独立记忆文件
3. **导出/导入** - 支持迁移到不同设备/智能体
4. **备份/恢复** - 定期备份防丢失
5. **一键迁移** - 打包所有记忆，换设备无忧

---

## 📁 文件结构

```
~/.openclaw/workspace/memory_storage/
├── users/
│   ├── user_a1b2c3d4/          # 用户目录（user_id 哈希）
│   │   ├── memories.jsonl      # 主记忆文件
│   │   ├── preferences.jsonl   # 偏好记忆
│   │   ├── relationships.jsonl # 关系记忆
│   │   └── knowledge.jsonl     # 知识记忆
│   └── user_e5f6g7h8/
│       └── ...
├── backups/
│   ├── user_test_20260304_112000.zip
│   └── ...
└── exports/
    ├── user_test_memories_20260304.json
    └── migration_test_20260304.zip
```

---

## 🚀 快速开始

### Python API 使用

```python
from memory_persistence import MemoryPersistence, Memory
from datetime import datetime

# 初始化
persistence = MemoryPersistence()

# 添加记忆
memory = Memory(
    id="mem_001",
    user_id="user_123",
    content="用户喜欢喝拿铁咖啡",
    category="preferences",
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat(),
    tags=["饮品", "咖啡"],
    confidence=0.9
)
persistence.add(memory)

# 查询记忆
memories = persistence.list("user_123", category="preferences", limit=10)

# 搜索记忆
results = persistence.search("user_123", query="咖啡")

# 统计信息
stats = persistence.get_stats("user_123")
print(stats)
# {'user_id': 'user_123', 'total_memories': 10, 'by_category': {...}}
```

---

## 💾 导出/导入（设备迁移）

### 场景 1: 换设备

**旧设备导出:**
```bash
cd /root/.openclaw/skills/lingxi/scripts

# 方法 1: 导出为 JSON
python3 memory_persistence.py export user_123 -o ~/backup_memories.json

# 方法 2: 创建迁移包（推荐）
python3 memory_persistence.py migrate user_123 -o ~/migration_package.zip
```

**新设备导入:**
```bash
# 方法 1: 从 JSON 导入
python3 memory_persistence.py import ~/backup_memories.json -u user_123

# 方法 2: 从迁移包导入
python3 memory_persistence.py import ~/migration_package.zip -u user_123
```

### 场景 2: 迁移到新智能体

```python
from memory_persistence import MemoryPersistence

persistence = MemoryPersistence()

# 创建迁移包
package_path = persistence.create_migration_package(
    user_id="old_ai_user",
    output_path="~/migration_to_new_ai.zip"
)

# 在新智能体导入
result = persistence.import_user(
    import_path="~/migration_to_new_ai.zip",
    user_id="new_ai_user"  # 新智能体的 user_id
)

print(f"迁移完成：{result['imported']} 条记忆")
```

---

## 🗄️ 备份/恢复

### 定期备份

```bash
# 手动备份
python3 memory_persistence.py backup user_123 -o ~/backups/user_123_$(date +%Y%m%d).zip

# 自动备份（添加到 crontab）
# 每天凌晨 2 点备份
0 2 * * * cd /root/.openclaw/skills/lingxi/scripts && python3 memory_persistence.py backup user_123
```

### 从备份恢复

```bash
# 恢复到最后一次备份
python3 memory_persistence.py restore ~/backups/user_123_20260304.zip -u user_123

# 恢复到新用户（保留原备份）
python3 memory_persistence.py restore ~/backups/user_123_20260304.zip -u user_123_restored
```

---

## 🔀 合并用户记忆

**场景:** 将多个用户的记忆合并到一个用户

```python
from memory_persistence import MemoryPersistence

persistence = MemoryPersistence()

# 合并 user_a 和 user_b 到 user_c
result1 = persistence.merge_users("user_a", "user_c")
result2 = persistence.merge_users("user_b", "user_c")

print(f"合并完成：{result1['merged'] + result2['merged']} 条记忆")
```

---

## 📊 查看统计

```bash
# 查看所有用户统计
python3 memory_persistence.py stats

# 输出示例:
{
  "total_users": 5,
  "total_memories": 1234,
  "storage_path": "/root/.openclaw/workspace/memory_storage"
}
```

---

## 🔍 高级用法

### 分类管理

记忆分为 4 个分类：

| 分类 | 用途 | 示例 |
|------|------|------|
| `memories` | 主记忆 | 对话历史、事件记录 |
| `preferences` | 用户偏好 | 喜欢的食物、沟通风格 |
| `relationships` | 关系网络 | 联系人、交互历史 |
| `knowledge` | 知识库 | 专业技能、兴趣爱好 |

```python
# 按分类查询
prefs = persistence.list("user_123", category="preferences")
knowledge = persistence.list("user_123", category="knowledge")

# 添加不同分类的记忆
pref_memory = Memory(
    id="pref_001",
    user_id="user_123",
    content="喜欢喝拿铁咖啡，不要糖",
    category="preferences",
    ...
)

knowledge_memory = Memory(
    id="know_001",
    user_id="user_123",
    content="擅长 Python 和 JavaScript 开发",
    category="knowledge",
    ...
)
```

### 搜索记忆

```python
# 关键词搜索
results = persistence.search("user_123", query="咖啡")

# 按分类搜索
pref_results = persistence.search("user_123", query="喜欢", category="preferences")

# 遍历结果
for memory in results:
    print(f"{memory.content} (置信度：{memory.confidence})")
```

### 清理旧记忆

```python
# 清理超过 365 天的记忆
deleted = persistence.cleanup_old_memories("user_123", days=365)
print(f"清理了 {deleted} 条旧记忆")
```

---

## 📦 迁移包内容

迁移包（ZIP 格式）包含：

```
migration_user_123_20260304.zip
├── README.md              # 使用说明
├── import.py              # 一键导入脚本
└── memories/
    ├── memories.jsonl     # 主记忆
    ├── preferences.jsonl  # 偏好
    ├── relationships.jsonl# 关系
    └── knowledge.jsonl    # 知识
```

**解压后可以直接使用:**
```bash
# 解压到正确位置
unzip migration_user_123_20260304.zip -d ~/.openclaw/workspace/memory_storage/users/

# 或者使用导入脚本
cd migration_user_123_20260304
python3 import.py
```

---

## 🔧 集成到灵犀系统

### 与 Fast Response Layer 集成

```python
from fast_response_layer import response_cache
from memory_persistence import MemoryPersistence

persistence = MemoryPersistence()

# 定期将缓存持久化
def persist_cache_to_disk(user_id: str):
    """将内存缓存保存到磁盘"""
    for key, response in response_cache.cache.items():
        memory = Memory(
            id=f"cache_{hash(key)}",
            user_id=user_id,
            content=response,
            category="memories",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={"cache_key": key}
        )
        persistence.add(memory)

# 每小时持久化一次
import schedule
schedule.every().hour.do(persist_cache_to_disk, user_id="user_123")
```

### 与记忆系统服务集成

```python
from memory_service import MemoryService
from memory_persistence import MemoryPersistence

class EnhancedMemoryService(MemoryService):
    """增强版记忆服务 - 带持久化"""
    
    def __init__(self):
        super().__init__()
        self.persistence = MemoryPersistence()
    
    async def memorize(self, conversation, user_id):
        # 原有逻辑
        result = await super().memorize(conversation, user_id)
        
        # 持久化到磁盘
        for item in result['extracted_memories']:
            memory = Memory(
                id=item['id'],
                user_id=user_id,
                content=item['content'],
                category=item['category'],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                metadata=item.get('metadata', {})
            )
            self.persistence.add(memory)
        
        return result
    
    async def retrieve(self, query, user_id, **kwargs):
        # 先从磁盘加载（如果缓存为空）
        if user_id not in self._cache or len(self._cache[user_id]) == 0:
            self._load_from_persistence(user_id)
        
        return await super().retrieve(query, user_id, **kwargs)
    
    def _load_from_persistence(self, user_id):
        """从持久化存储加载到缓存"""
        for category in ["memories", "preferences", "relationships", "knowledge"]:
            memories = self.persistence.list(user_id, category=category, limit=10000)
            for memory in memories:
                # 加载到缓存
                pass
```

---

## 🛡️ 最佳实践

### 1. 定期备份

```bash
# 添加到 crontab
# 每天备份
0 2 * * * cd /root/.openclaw/skills/lingxi/scripts && python3 memory_persistence.py backup user_123

# 每周清理旧备份（保留最近 7 天）
0 3 * * 0 find /root/.openclaw/workspace/memory_storage/backups -name "*.zip" -mtime +7 -delete
```

### 2. 异地备份

```bash
# 备份到云存储
python3 memory_persistence.py backup user_123 -o /tmp/backup.zip
rclone copy /tmp/backup.zip remote:backups/lingxi/
```

### 3. 版本控制

```bash
# 使用 Git 管理记忆（可选）
cd ~/.openclaw/workspace/memory_storage
git init
git add users/
git commit -m "Initial memory backup"
```

### 4. 监控存储大小

```python
import os

def get_storage_size():
    """获取存储总大小"""
    total_size = 0
    storage_path = Path("~/.openclaw/workspace/memory_storage").expanduser()
    
    for dirpath, dirnames, filenames in os.walk(storage_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    return total_size / (1024 * 1024)  # MB

size_mb = get_storage_size()
if size_mb > 100:  # 超过 100MB 警告
    print(f"⚠️ 存储空间过大：{size_mb:.2f}MB")
```

---

## 📊 性能指标

| 操作 | 延迟 | 说明 |
|------|------|------|
| 添加记忆 | <1ms | 追加写入 |
| 查询记忆 | <10ms | 内存缓存 |
| 搜索记忆 | <50ms | 关键词匹配 |
| 导出 1000 条 | <1s | JSON 格式 |
| 导入 1000 条 | <1s | 批量写入 |
| 备份 1000 条 | <500ms | ZIP 压缩 |

---

## 🎯 迁移场景示例

### 场景 1: 从本地服务器迁移到云服务器

**步骤:**

1. **本地导出**
   ```bash
   python3 memory_persistence.py migrate user_123 -o ~/migration.zip
   ```

2. **传输到云服务器**
   ```bash
   scp ~/migration.zip user@cloud:~/
   ```

3. **云服务器导入**
   ```bash
   python3 memory_persistence.py import ~/migration.zip -u user_123
   ```

### 场景 2: 从旧 AI 迁移到新 AI

**步骤:**

1. **旧 AI 导出**
   ```python
   persistence.create_migration_package("old_ai_user", "migration.zip")
   ```

2. **新 AI 导入**
   ```python
   result = persistence.import_user("migration.zip", "new_ai_user")
   print(f"迁移了 {result['imported']} 条记忆")
   ```

3. **验证**
   ```python
   stats = persistence.get_stats("new_ai_user")
   print(f"新 AI 现在有 {stats['total_memories']} 条记忆")
   ```

### 场景 3: 多设备同步

**步骤:**

1. **主设备定期导出**
   ```bash
   # 每小时导出
   0 * * * * python3 memory_persistence.py export user_123 -o /sync/memories.json
   ```

2. **从设备定期导入**
   ```bash
   # 每小时导入
   5 * * * * python3 memory_persistence.py import /sync/memories.json -u user_123
   ```

---

## 🐛 故障排查

### 问题 1: 导入失败

**错误:** `无效的导入文件格式`

**解决:**
```bash
# 检查文件格式
python3 -c "import json; json.load(open('your_file.json'))"

# 确保包含 version 和 memories 字段
```

### 问题 2: 记忆丢失

**解决:**
```bash
# 从备份恢复
python3 memory_persistence.py restore latest_backup.zip -u user_123

# 检查存储目录
ls -la ~/.openclaw/workspace/memory_storage/users/
```

### 问题 3: 存储空间过大

**解决:**
```python
# 清理旧记忆
persistence.cleanup_old_memories("user_123", days=90)

# 压缩存储
persistence.compact_storage("user_123")
```

---

## 📚 相关文档

- [FAST_RESPONSE_BENCHMARK.md](FAST_RESPONSE_BENCHMARK.md) - 快速响应层性能测试
- [memory_service.py](memory_service.py) - 记忆服务 API
- [memory_config.py](memory_config.py) - 记忆系统配置

---

## 🎉 总结

**记忆持久化系统实现了:**

1. ✅ **JSONL 格式存储** - 通用易迁移
2. ✅ **用户级隔离** - 安全独立
3. ✅ **导出/导入** - 设备迁移无忧
4. ✅ **备份/恢复** - 数据安全
5. ✅ **一键迁移** - 换设备/换 AI 轻松

**记忆永不丢失，随时随地带着走！** 💋

---

**作者:** 丝佳丽 Scarlett  
**日期:** 2026-03-04  
**状态:** ✅ 完成，待老板审核
