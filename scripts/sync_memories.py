#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 记忆文件同步脚本

功能：
- 扫描每日记忆文件（memory/*.md）
- 提取记忆内容
- 同步到 items/memories.jsonl
- 避免重复记录

使用：
python3 sync_memories.py
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
ITEMS_FILE = MEMORY_DIR / "items" / "memories.jsonl"
STATE_FILE = MEMORY_DIR / "items" / "sync_state.json"

def load_synced_ids() -> set:
    """加载已同步的记忆 ID"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return set(state.get('synced_ids', []))
    return set()

def save_synced_ids(synced_ids: set):
    """保存已同步的记忆 ID"""
    ITEMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump({'synced_ids': list(synced_ids)[-1000:]}, f, indent=2)  # 只保留最近 1000 条

def load_existing_memories() -> set:
    """加载已存在的记忆 ID"""
    synced_ids = set()
    if ITEMS_FILE.exists():
        with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    memory = json.loads(line.strip())
                    synced_ids.add(memory.get('id', ''))
                except:
                    continue
    return synced_ids

def parse_daily_memory(file_path: Path) -> list:
    """解析每日记忆文件"""
    memories = []
    content = file_path.read_text(encoding='utf-8')
    
    # 提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
    date_str = date_match.group(1) if date_match else file_path.stem
    
    # 提取章节标题和内容
    sections = re.split(r'\n##+\s+', content)
    for section in sections[1:]:  # 跳过第一个空章节
        lines = section.split('\n')
        title = lines[0].strip() if lines else '无标题'
        content_text = '\n'.join(lines[1:]).strip()
        
        if len(content_text) < 20:  # 跳过太短的内容
            continue
        
        # 生成唯一 ID
        memory_id = f"{date_str}_{hash(title) % 10000:04d}"
        
        memories.append({
            'id': memory_id,
            'category': 'context',
            'topic': title,
            'content': content_text[:2000],  # 限制长度
            'source': f'daily_{date_str}',
            'timestamp': time.time(),
            'confidence': 0.8,
            'related_ids': [],
            'user_id': 'default',
            'embeddings': None,
            'metadata': {
                'date': date_str,
                'file': file_path.name
            }
        })
    
    return memories

def sync_memories():
    """同步记忆文件"""
    print(f"🦞 灵犀记忆同步")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"记忆目录：{MEMORY_DIR}")
    print(f"目标文件：{ITEMS_FILE}")
    print()
    
    # 确保目录存在
    ITEMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载已同步的记忆 ID
    synced_ids = load_synced_ids() | load_existing_memories()
    print(f"已同步记忆数：{len(synced_ids)}")
    
    # 扫描每日记忆文件
    daily_files = sorted(MEMORY_DIR.glob("*.md"))
    print(f"发现 {len(daily_files)} 个每日记忆文件")
    
    new_memories = []
    for daily_file in daily_files:
        if 'HEARTBEAT' in daily_file.name or 'CREDENTIALS' in daily_file.name:
            continue
        
        memories = parse_daily_memory(daily_file)
        for memory in memories:
            if memory['id'] not in synced_ids:
                new_memories.append(memory)
                synced_ids.add(memory['id'])
    
    print(f"新记忆数：{len(new_memories)}")
    
    # 写入新记忆
    if new_memories:
        with open(ITEMS_FILE, 'a', encoding='utf-8') as f:
            for memory in new_memories:
                f.write(json.dumps(memory, ensure_ascii=False) + '\n')
        print(f"✅ 已写入 {len(new_memories)} 条新记忆")
    else:
        print(f"✅ 没有新记忆需要同步")
    
    # 保存状态
    save_synced_ids(synced_ids)
    
    # 统计
    total_memories = len(synced_ids)
    print(f"\n✨ 同步完成")
    print(f"总记忆数：{total_memories}")

if __name__ == "__main__":
    sync_memories()
