#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 错误日志管理器 (JSON 格式) v2.8.6

目标：使用结构化 JSON 格式存储错误日志，提高解析可靠性
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import deque

# ==================== 配置 ====================

LEARNINGS_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
ERRORS_JSON_FILE = LEARNINGS_DIR / "errors.json"
ERRORS_MD_FILE = LEARNINGS_DIR / "ERRORS.md"  # 保留 Markdown 用于人工阅读

# ==================== 数据模型 ====================

@dataclass
class ErrorLog:
    """错误日志（JSON 格式）"""
    error_id: str
    timestamp: str
    error_type: str
    error_message: str
    context: Dict[str, Any]
    suggestion: str
    tags: List[str]
    pattern_key: str
    resolved: bool = False
    resolved_at: Optional[str] = None
    related_logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'ErrorLog':
        """从字典创建"""
        return ErrorLog(**data)
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式（用于人工阅读）"""
        tags_str = ", ".join(self.tags) if self.tags else "未分类"
        status = "✅ 已解决" if self.resolved else "❌ 未解决"
        
        return f"""
## [{self.error_id}] {self.error_type} - {status}

**时间**: {self.timestamp}  
**标签**: {tags_str}  
**Pattern-Key**: `{self.pattern_key}`

### 错误信息
```
{self.error_message}
```

### 上下文
```json
{json.dumps(self.context, ensure_ascii=False, indent=2)}
```

### 建议修复
{self.suggestion}

---
"""

# ==================== 错误日志管理器 ====================

class ErrorLogManager:
    """错误日志管理器（JSON 格式）"""
    
    def __init__(self, max_history: int = 10000):
        """初始化
        
        Args:
            max_history: 最大保留错误数（默认 10000）
        """
        self.errors_file = ERRORS_JSON_FILE
        self.md_file = ERRORS_MD_FILE
        self.max_history = max_history
        
        # 使用 deque 加载现有错误
        self.errors = deque(self._load_errors(), maxlen=max_history)
        
        # 确保目录存在
        LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_errors(self) -> List[ErrorLog]:
        """加载现有错误日志"""
        if not self.errors_file.exists():
            return []
        
        try:
            content = self.errors_file.read_text(encoding='utf-8')
            data = json.loads(content)
            return [ErrorLog.from_dict(e) for e in data.get("errors", [])]
        except Exception as e:
            print(f"⚠️  加载错误日志失败：{e}")
            return []
    
    def _save_errors(self):
        """保存错误日志到 JSON 文件"""
        try:
            self.errors_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "version": "2.8.6",
                "last_updated": datetime.now().isoformat(),
                "total_count": len(self.errors),
                "errors": [e.to_dict() for e in self.errors]
            }
            
            self.errors_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            # 同时更新 Markdown 文件（用于人工阅读）
            self._update_markdown()
            
        except Exception as e:
            print(f"⚠️  保存错误日志失败：{e}")
    
    def _update_markdown(self):
        """更新 Markdown 文件（用于人工阅读）"""
        try:
            content = "# 📝 错误日志\n\n> 自动生成 - 灵犀 Learning Layer v2.8.6\n\n"
            
            # 按时间倒序
            for error in sorted(self.errors, key=lambda e: e.timestamp, reverse=True):
                content += error.to_markdown()
            
            self.md_file.write_text(content, encoding='utf-8')
            
        except Exception as e:
            print(f"⚠️  更新 Markdown 失败：{e}")
    
    def add_error(self, error_type: str, error_message: str, context: Dict = None, 
                  suggestion: str = "", tags: List[str] = None) -> ErrorLog:
        """添加错误日志
        
        Args:
            error_type: 错误类型
            error_message: 错误信息
            context: 上下文信息
            suggestion: 修复建议
            tags: 标签列表
        
        Returns:
            ErrorLog: 创建的错误日志对象
        """
        # 生成错误 ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        error_id = f"ERR-{timestamp}"
        
        # 创建错误日志
        error = ErrorLog(
            error_id=error_id,
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_message,
            context=context or {},
            suggestion=suggestion,
            tags=tags or [],
            pattern_key=self._extract_pattern_key(error_message)
        )
        
        # 添加到队列
        self.errors.append(error)
        
        # 保存到文件
        self._save_errors()
        
        print(f"📝 错误日志已记录：{error_id}")
        return error
    
    def _extract_pattern_key(self, error_message: str) -> str:
        """提取错误模式关键词"""
        # 简单实现：提取前 50 个字符
        return error_message[:50].replace("\n", " ")
    
    def get_recent_errors(self, days: int = 7, limit: int = 100) -> List[ErrorLog]:
        """获取最近的错误日志
        
        Args:
            days: 最近 N 天
            limit: 最大返回数量
        
        Returns:
            List[ErrorLog]: 错误日志列表
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        recent = []
        for error in self.errors:
            try:
                ts = datetime.fromisoformat(error.timestamp).timestamp()
                if ts >= cutoff:
                    recent.append(error)
            except:
                continue
            
            if len(recent) >= limit:
                break
        
        return recent
    
    def get_errors_by_pattern(self, pattern_key: str) -> List[ErrorLog]:
        """根据 Pattern-Key 获取错误"""
        return [e for e in self.errors if pattern_key in e.pattern_key]
    
    def mark_as_resolved(self, error_id: str) -> bool:
        """标记错误为已解决
        
        Args:
            error_id: 错误 ID
        
        Returns:
            bool: 是否成功
        """
        for error in self.errors:
            if error.error_id == error_id:
                error.resolved = True
                error.resolved_at = datetime.now().isoformat()
                self._save_errors()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.errors)
        resolved = sum(1 for e in self.errors if e.resolved)
        
        # 按类型统计
        type_counts = {}
        for error in self.errors:
            type_counts[error.error_type] = type_counts.get(error.error_type, 0) + 1
        
        return {
            "total_errors": total,
            "resolved_errors": resolved,
            "unresolved_errors": total - resolved,
            "resolution_rate": f"{(resolved / total * 100) if total > 0 else 0:.1f}%",
            "by_type": type_counts
        }

# ==================== 全局实例 ====================

_error_log_manager: Optional[ErrorLogManager] = None

def get_error_log_manager() -> ErrorLogManager:
    """获取错误日志管理器实例"""
    global _error_log_manager
    if _error_log_manager is None:
        _error_log_manager = ErrorLogManager()
    return _error_log_manager

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📝 灵犀错误日志管理器测试 (JSON 格式)")
    print("=" * 60)
    
    manager = get_error_log_manager()
    
    # 添加测试错误
    print("\n1️⃣ 添加测试错误...")
    error = manager.add_error(
        error_type="Connection Timeout",
        error_message="连接超时：API 服务在 30 秒内未响应",
        context={"url": "https://api.example.com", "timeout": 30},
        suggestion="增加超时时间或检查网络连接",
        tags=["timeout", "network"]
    )
    print(f"   错误 ID: {error.error_id}")
    
    # 获取统计
    print("\n2️⃣ 获取统计信息...")
    stats = manager.get_statistics()
    print(f"   总错误数：{stats['total_errors']}")
    print(f"   已解决：{stats['resolved_errors']}")
    print(f"   解决率：{stats['resolution_rate']}")
    
    # 获取最近错误
    print("\n3️⃣ 获取最近错误...")
    recent = manager.get_recent_errors(days=7)
    print(f"   最近 7 天错误：{len(recent)} 个")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
