#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 自学习层 (Learning Layer) v2.8.5

心有灵犀，越用越聪明 🧠

核心功能:
1. 错误自动捕获 - 监听执行结果，检测错误
2. 学习日志自动生成 - ERRORS.md / LEARNINGS.md / FEATURES.md
3. 经验自动提炼 - 定期 Review，更新核心记忆
4. Hook 机制 - 启动提醒 + 后置检测
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import asyncio
from collections import deque

# ==================== 配置 ====================

LEARNINGS_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
BACKUP_DIR = LEARNINGS_DIR / "backups"

# 错误关键词
ERROR_KEYWORDS = [
    "error", "failed", "failure", "exception", "traceback",
    "错误", "失败", "异常", "报错", "崩溃"
]

# 学习日志 ID 格式
def generate_log_id(prefix: str = "LRN") -> str:
    """生成学习日志 ID"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{timestamp}"

# ==================== 数据模型 ====================

@dataclass
class ErrorLog:
    """错误日志"""
    id: str = field(default_factory=lambda: generate_log_id("ERR"))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_type: str = ""
    error_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    suggestion: str = ""
    tags: List[str] = field(default_factory=list)
    pattern_key: str = ""  # 用于追踪重复问题
    resolved: bool = False
    resolved_at: Optional[str] = None
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        tags_str = ", ".join(self.tags) if self.tags else "未分类"
        status = "✅ 已解决" if self.resolved else "❌ 未解决"
        
        return f"""
## [{self.id}] {self.error_type} - {status}

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

@dataclass
class LearningLog:
    """学习经验日志"""
    id: str = field(default_factory=lambda: generate_log_id("LRN"))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    title: str = ""
    lesson: str = ""
    knowledge_gap: str = ""
    action_taken: str = ""
    tags: List[str] = field(default_factory=list)
    related_logs: List[str] = field(default_factory=list)  # 关联的错误日志 ID
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        tags_str = ", ".join(self.tags) if self.tags else "未分类"
        related = ", ".join(self.related_logs) if self.related_logs else "无"
        
        return f"""
## [{self.id}] {self.title}

**时间**: {self.timestamp}  
**标签**: {tags_str}  
**关联日志**: {related}

### 学习内容
{self.lesson}

### 知识缺口
{self.knowledge_gap}

### 采取的行动
{self.action_taken}

---
"""

@dataclass
class FeatureRequest:
    """功能需求日志"""
    id: str = field(default_factory=lambda: generate_log_id("FEAT"))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    title: str = ""
    description: str = ""
    priority: str = "medium"  # low, medium, high, critical
    complexity: str = "medium"  # easy, medium, hard, unknown
    status: str = "pending"  # pending, reviewing, planned, done
    tags: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        tags_str = ", ".join(self.tags) if self.tags else "未分类"
        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(self.priority, "⚪")
        complexity_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🟠", "unknown": "⚪"}.get(self.complexity, "⚪")
        
        return f"""
## [{self.id}] {self.title} {priority_emoji}

**时间**: {self.timestamp}  
**优先级**: {self.priority} {priority_emoji}  
**复杂度**: {self.complexity} {complexity_emoji}  
**标签**: {tags_str}

### 需求描述
{self.description}

---
"""

# ==================== 学习日志管理器 ====================

class LearningLogger:
    """学习日志管理器"""
    
    def __init__(self):
        self.errors_file = LEARNINGS_DIR / "ERRORS.md"
        self.learnings_file = LEARNINGS_DIR / "LEARNINGS.md"
        self.features_file = LEARNINGS_DIR / "FEATURE_REQUESTS.md"
        
        # 确保目录存在
        LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        # 初始化文件
        self._init_files()
    
    def _init_files(self):
        """初始化日志文件"""
        if not self.errors_file.exists():
            self.errors_file.write_text(self._get_header("错误日志"))
        
        if not self.learnings_file.exists():
            self.learnings_file.write_text(self._get_header("学习经验"))
        
        if not self.features_file.exists():
            self.features_file.write_text(self._get_header("功能需求"))
    
    def _get_header(self, title: str) -> str:
        """获取文件头"""
        return f"""# {title}

> 自动生成 - 灵犀 Learning Layer v2.8.5  
> 最后更新：{datetime.now().isoformat()}

---

"""
    
    def _append_to_file(self, file_path: Path, content: str):
        """追加内容到文件"""
        # 读取现有内容
        if file_path.exists():
            existing = file_path.read_text(encoding='utf-8')
        else:
            existing = self._get_header(file_path.stem)
        
        # 追加新内容
        new_content = existing + "\n" + content
        
        # 写入文件
        file_path.write_text(new_content, encoding='utf-8')
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None, suggestion: str = "") -> ErrorLog:
        """记录错误日志"""
        log = ErrorLog(
            error_type=error_type,
            error_message=error_message,
            context=context or {},
            suggestion=suggestion,
            tags=self._auto_tag_error(error_message),
            pattern_key=self._extract_pattern_key(error_message)
        )
        
        self._append_to_file(self.errors_file, log.to_markdown())
        print(f"📝 错误日志已记录：{log.id}")
        
        return log
    
    def log_learning(self, title: str, lesson: str, knowledge_gap: str = "", action_taken: str = "", tags: List[str] = None) -> LearningLog:
        """记录学习经验"""
        log = LearningLog(
            title=title,
            lesson=lesson,
            knowledge_gap=knowledge_gap,
            action_taken=action_taken,
            tags=tags or []
        )
        
        self._append_to_file(self.learnings_file, log.to_markdown())
        print(f"📝 学习日志已记录：{log.id}")
        
        return log
    
    def log_feature_request(self, title: str, description: str, priority: str = "medium", complexity: str = "medium", tags: List[str] = None) -> FeatureRequest:
        """记录功能需求"""
        req = FeatureRequest(
            title=title,
            description=description,
            priority=priority,
            complexity=complexity,
            tags=tags or []
        )
        
        self._append_to_file(self.features_file, req.to_markdown())
        print(f"📝 功能需求已记录：{req.id}")
        
        return req
    
    def _auto_tag_error(self, error_message: str) -> List[str]:
        """自动标记错误类型"""
        tags = []
        error_lower = error_message.lower()
        
        if "timeout" in error_lower or "超时" in error_lower:
            tags.append("timeout")
        
        if "connection" in error_lower or "连接" in error_lower:
            tags.append("network")
        
        if "permission" in error_lower or "权限" in error_lower:
            tags.append("permission")
        
        if "memory" in error_lower or "内存" in error_lower:
            tags.append("memory")
        
        if "file" in error_lower or "文件" in error_lower:
            tags.append("file")
        
        if not tags:
            tags.append("general")
        
        return tags
    
    def _extract_pattern_key(self, error_message: str) -> str:
        """提取 Pattern-Key (用于追踪重复问题)"""
        # 提取错误类型的关键词
        words = re.findall(r'\b\w+\b', error_message.lower())
        
        # 过滤常见词
        common_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
        keywords = [w for w in words if w not in common_words and len(w) > 3][:5]
        
        return "_".join(keywords) if keywords else "unknown"
    
    def get_recent_errors(self, days: int = 7) -> List[ErrorLog]:
        """获取最近的错误日志"""
        # 简化实现：读取文件并解析
        # 实际应该用数据库或更高效的存储
        return []
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "errors_file": str(self.errors_file),
            "learnings_file": str(self.learnings_file),
            "features_file": str(self.features_file),
            "directory": str(LEARNINGS_DIR)
        }

# ==================== 错误检测器 ====================

class ErrorDetector:
    """错误检测器"""
    
    def __init__(self, logger: LearningLogger = None):
        self.logger = logger or LearningLogger()
        self.error_keywords = ERROR_KEYWORDS
    
    def detect(self, result: Any) -> bool:
        """检测是否包含错误"""
        if result is None:
            return False
        
        # 检查字典
        if isinstance(result, dict):
            return self._check_dict(result)
        
        # 检查字符串
        if isinstance(result, str):
            return self._check_string(result)
        
        # 检查异常
        if isinstance(result, Exception):
            return True
        
        return False
    
    def _check_dict(self, data: Dict) -> bool:
        """检查字典是否包含错误"""
        # 检查常见错误字段
        if "error" in data or "errors" in data:
            return True
        
        if "status" in data and data["status"] in ["failed", "failure", "error"]:
            return True
        
        # 递归检查
        for key, value in data.items():
            if isinstance(value, dict):
                if self._check_dict(value):
                    return True
            elif isinstance(value, str):
                if self._check_string(value):
                    return True
        
        return False
    
    def _check_string(self, text: str) -> bool:
        """检查字符串是否包含错误关键词"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.error_keywords)
    
    def analyze_and_log(self, result: Any, context: Dict = None) -> Optional[ErrorLog]:
        """分析结果并记录错误日志"""
        if not self.detect(result):
            return None
        
        # 提取错误信息
        error_type = "Unknown Error"
        error_message = ""
        suggestion = ""
        
        if isinstance(result, dict):
            error_message = result.get("error", result.get("message", str(result)))
            error_type = result.get("error_type", "Execution Error")
            suggestion = result.get("suggestion", "")
        elif isinstance(result, str):
            error_message = result
            error_type = "String Error"
        elif isinstance(result, Exception):
            error_message = str(result)
            error_type = type(result).__name__
        
        # 记录日志
        log = self.logger.log_error(
            error_type=error_type,
            error_message=error_message,
            context=context or {"result": str(result)},
            suggestion=suggestion
        )
        
        return log

# ==================== 学习层主控制器 ====================

class LearningLayer:
    """学习层主控制器"""
    
    def __init__(self, max_history: int = 1000):
        """初始化学习层
        
        Args:
            max_history: 历史记录最大条数（默认 1000，防止内存泄漏）
        """
        self.logger = LearningLogger()
        self.detector = ErrorDetector(self.logger)
        self.enabled = True
        
        # 使用 deque 限制大小，防止内存泄漏
        self.execution_history = deque(maxlen=max_history)
        self.error_history = deque(maxlen=max_history)
        self.learning_logs = deque(maxlen=max_history)
    
    def on_task_start(self, task_id: str, task_description: str):
        """任务开始时的 Hook"""
        if not self.enabled:
            return
        
        # 检查最近的学习日志，避免重复错误
        recent_logs = self.logger.get_recent_errors(days=7)
        if recent_logs:
            print(f"💡 提醒：最近有 {len(recent_logs)} 个错误日志，请注意避免重复错误")
    
    def on_task_complete(self, task_id: str, result: Any, context: Dict = None):
        """任务完成时的 Hook"""
        if not self.enabled:
            return
        
        # 检测错误
        if self.detector.detect(result):
            log = self.detector.analyze_and_log(result, context)
            if log:
                print(f"⚠️  检测到错误：{log.id} - {log.error_type}")
                return {"error_detected": True, "log_id": log.id}
        
        return {"error_detected": False}
    
    def on_user_correction(self, user_feedback: str, original_output: str):
        """用户纠正时的 Hook"""
        if not self.enabled:
            return
        
        # 记录学习经验
        self.logger.log_learning(
            title="用户纠正",
            lesson=f"用户反馈：{user_feedback}",
            knowledge_gap="AI 输出与用户期望不符",
            action_taken=f"原始输出：{original_output[:200]}...",
            tags=["user-feedback", "correction"]
        )
    
    def on_feature_request(self, feature_description: str, priority: str = "medium"):
        """功能需求记录"""
        if not self.enabled:
            return
        
        # 估算复杂度
        complexity = self._estimate_complexity(feature_description)
        
        self.logger.log_feature_request(
            title="新功能需求",
            description=feature_description,
            priority=priority,
            complexity=complexity,
            tags=["feature-request"]
        )
    
    def _estimate_complexity(self, description: str) -> str:
        """估算功能复杂度"""
        desc_lower = description.lower()
        
        # 简单关键词
        simple_keywords = ["添加", "修改", "调整", "优化", "bug", "fix"]
        if any(kw in desc_lower for kw in simple_keywords) and len(description) < 50:
            return "easy"
        
        # 复杂关键词
        complex_keywords = ["重构", "架构", "集成", "多平台", "AI", "机器学习"]
        if any(kw in desc_lower for kw in complex_keywords):
            return "hard"
        
        return "medium"
    
    def weekly_review(self):
        """每周 Review (调用 AI 提炼经验)"""
        print("🧠 开始每周 Review...")
        
        # 获取本周错误日志
        errors = self.logger.get_recent_errors(days=7)
        
        if not errors:
            print("✅ 本周没有错误日志")
            return
        
        # TODO: 调用 AI 分析错误模式，提炼通用经验
        # 1. 聚类相似错误
        # 2. 找出根本原因
        # 3. 生成修复建议
        # 4. 更新核心记忆文件
        
        print(f"📊 本周共 {len(errors)} 个错误，需要人工 Review")
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "execution_history_size": len(self.execution_history),
            "error_history_size": len(self.error_history),
            "learning_logs_size": len(self.learning_logs),
            "logger": self.logger.get_statistics(),
            "detector": {"error_keywords_count": len(ERROR_KEYWORDS)}
        }

# ==================== 全局实例 ====================

_learning_layer: Optional[LearningLayer] = None

def get_learning_layer() -> LearningLayer:
    """获取学习层实例"""
    global _learning_layer
    if _learning_layer is None:
        _learning_layer = LearningLayer()
    return _learning_layer

# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("🧠 灵犀 Learning Layer v2.8.5 测试")
    print("=" * 60)
    
    layer = get_learning_layer()
    
    # 测试错误检测
    print("\n1️⃣ 测试错误检测")
    result = layer.on_task_complete(
        task_id="test_001",
        result={"error": "Connection timeout", "message": "Failed to connect"},
        context={"task": "test"}
    )
    print(f"   结果：{result}")
    
    # 测试学习记录
    print("\n2️⃣ 测试学习记录")
    layer.on_user_correction(
        user_feedback="应该用更简洁的方式",
        original_output="这是一个很长的回答..."
    )
    
    # 测试功能需求
    print("\n3️⃣ 测试功能需求")
    layer.on_feature_request(
        feature_description="添加多语言支持",
        priority="high"
    )
    
    # 显示统计
    print("\n4️⃣ 统计信息")
    stats = layer.get_statistics()
    print(f"   {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！学习日志已保存到：~/.openclaw/workspace/.learnings/")
