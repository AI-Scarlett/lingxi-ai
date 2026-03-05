#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - 文档自动更新脚本

功能:
1. 从代码自动提取注释生成文档
2. 检测代码变更自动更新 README
3. 生成 API 文档
4. 更新更新日志

运行方式:
    python scripts/update_docs.py
    # 或添加到 pre-commit hook
"""

import os
import re
import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

# ==================== 配置 ====================

DOCS_DIR = Path(__file__).parent.parent / "docs"
SCRIPTS_DIR = Path(__file__).parent
README_FILE = Path(__file__).parent.parent / "README.md"
CHANGELOG_FILE = DOCS_DIR / "CHANGELOG.md"
API_DOCS_FILE = DOCS_DIR / "API.md"

# 需要文档化的文件
TARGET_FILES = [
    "orchestrator_v2.py",
    "auto_retry.py",
    "fast_response_layer_v2.py",
    "performance_monitor.py",
    "learning_layer.py",
]

# ==================== 工具函数 ====================

def compute_file_hash(file_path: Path) -> str:
    """计算文件哈希值"""
    if not file_path.exists():
        return ""
    content = file_path.read_text(encoding='utf-8')
    return hashlib.md5(content.encode()).hexdigest()

def load_hash_cache() -> Dict[str, str]:
    """加载哈希缓存"""
    cache_file = DOCS_DIR / ".doc_hash_cache.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding='utf-8'))
        except:
            return {}
    return {}

def save_hash_cache(cache: Dict[str, str]):
    """保存哈希缓存"""
    cache_file = DOCS_DIR / ".doc_hash_cache.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache, indent=2), encoding='utf-8')

def extract_docstring(code: str) -> Dict[str, str]:
    """提取代码中的文档字符串"""
    docstrings = {}
    
    try:
        tree = ast.parse(code)
        
        # 提取模块级文档
        if ast.get_docstring(tree):
            docstrings["module"] = ast.get_docstring(tree)
        
        # 提取类和函数的文档
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    key = f"{node.__class__.__name__}:{node.name}"
                    docstrings[key] = docstring
    
    except SyntaxError:
        pass
    
    return docstrings

def extract_version(code: str) -> Optional[str]:
    """提取版本号"""
    # 匹配 v2.0, v2.8.5 等版本格式
    match = re.search(r'v(\d+\.\d+(?:\.\d+)?)', code)
    if match:
        return f"v{match.group(1)}"
    return None

def extract_features(code: str) -> List[str]:
    """提取功能特性列表"""
    features = []
    
    # 匹配注释中的功能描述
    feature_patterns = [
        r'[#"]\s*(?:功能 | 特性 | 目标 | 优化)[:：]?\s*(.+)',
        r'[#"]\s*(?:\d+[.)]\s*)?(支持 | 实现 | 添加 | 优化)\s+(.+?)(?:\n|$)',
    ]
    
    for pattern in feature_patterns:
        matches = re.findall(pattern, code, re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                features.append(match[-1].strip())
            else:
                features.append(match.strip())
    
    return features[:10]  # 限制最多 10 个特性

# ==================== 文档生成器 ====================

class DocGenerator:
    """文档生成器"""
    
    def __init__(self):
        self.docstrings = {}
        self.versions = {}
        self.features = {}
        self.last_update = datetime.now().isoformat()
    
    def scan_files(self):
        """扫描所有目标文件"""
        print("📝 扫描代码文件...")
        
        for file_name in TARGET_FILES:
            file_path = SCRIPTS_DIR / file_name
            if file_path.exists():
                code = file_path.read_text(encoding='utf-8')
                self.docstrings[file_name] = extract_docstring(code)
                self.versions[file_name] = extract_version(code)
                self.features[file_name] = extract_features(code)
                print(f"   ✅ {file_name}")
            else:
                print(f"   ⚠️  {file_name} 不存在")
    
    def check_readme_versions(self) -> bool:
        """检查 README 版本顺序是否正确"""
        if not README_FILE.exists():
            return True
        
        readme = README_FILE.read_text(encoding='utf-8')
        
        # 提取所有版本号
        version_pattern = r'v(\d+)\.(\d+)\.(\d+)'
        versions = re.findall(version_pattern, readme)
        
        if len(versions) < 2:
            return True
        
        # 检查版本是否按倒序排列
        for i in range(len(versions) - 1):
            current = tuple(map(int, versions[i]))
            next_v = tuple(map(int, versions[i + 1]))
            
            # 如果当前版本小于下一个版本，说明顺序错误
            if current < next_v:
                print(f"   ❌ 版本顺序错误：v{'.'.join(map(str, next_v))} 应该在 v{'.'.join(map(str, current))} 前面")
                return False
        
        print(f"   ✅ 版本顺序正确")
        return True
    
    def generate_api_docs(self) -> str:
        """生成 API 文档"""
        content = f"""# 灵犀 (Lingxi) API 文档

> 自动生成 - 最后更新：{self.last_update}

---

## 📦 模块概览

| 模块 | 版本 | 描述 |
|------|------|------|
"""
        
        for file_name, version in self.versions.items():
            desc = self.docstrings.get(file_name, {}).get("module", "暂无描述")[:50]
            content += f"| {file_name} | {version or 'N/A'} | {desc}... |\n"
        
        content += "\n---\n\n"
        
        # 详细 API
        for file_name, docs in self.docstrings.items():
            content += f"## 📄 {file_name}\n\n"
            
            if "module" in docs:
                content += f"### 模块说明\n\n{docs['module']}\n\n"
            
            # 提取类和函数
            classes = [k for k in docs.keys() if k.startswith("ClassDef:")]
            functions = [k for k in docs.keys() if k.startswith("FunctionDef:") or k.startswith("AsyncFunctionDef:")]
            
            if classes:
                content += "### 类\n\n"
                for cls in classes:
                    name = cls.split(":")[1]
                    content += f"#### {name}\n\n{docs[cls]}\n\n"
            
            if functions:
                content += "### 函数\n\n"
                for func in functions:
                    name = func.split(":")[1]
                    content += f"#### {name}()\n\n{docs[func]}\n\n"
            
            content += "---\n\n"
        
        return content
    
    def generate_readme_update(self) -> str:
        """生成 README 更新内容"""
        content = f"""## 📊 系统架构

灵犀采用分层架构设计：

```
┌─────────────────────────────────────┐
│         用户输入 (User Input)        │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  Layer 0/1: 快速响应层 (<10ms)       │
│  - 规则匹配 (零思考)                 │
│  - LRU 缓存 (带 TTL)                  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  Layer 2/3: 完整执行层 (<500ms)      │
│  - 意图识别                          │
│  - 任务拆解                          │
│  - 并行执行                          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       学习层 (Learning Layer)        │
│  - 错误检测 (50+ 关键词)              │
│  - 自动日志                          │
│  - 经验提炼                          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       自愈系统 (Self-Healing)        │
│  - 自动重试 (指数退避)               │
│  - 降级方案                          │
│  - Git 推送超时保护                   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│       性能监控 (Performance)         │
│  - 实时指标                          │
│  - EWMA 基线计算                      │
│  - 异常告警                          │
└─────────────────────────────────────┘
```

## 🚀 核心模块

"""
        
        for file_name, version in self.versions.items():
            features = self.features.get(file_name, [])
            content += f"### {file_name} `{version or 'N/A'}`\n\n"
            
            if features:
                content += "**特性**:\n"
                for feature in features:
                    content += f"- {feature}\n"
            
            content += "\n"
        
        return content
    
    def generate_changelog_entry(self, changes: List[str]) -> str:
        """生成更新日志条目"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        content = f"""## {date} - v2.9.1

### 🎯 新增功能
"""
        
        for change in changes:
            content += f"- {change}\n"
        
        content += f"""
### 📝 文档
- 自动生成 API 文档
- 自动更新 README
- 添加文档哈希缓存

---

"""
        return content
    
    def save_all(self):
        """保存所有文档"""
        print("\n💾 保存文档...")
        
        # 确保目录存在
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 保存 API 文档
        api_content = self.generate_api_docs()
        API_DOCS_FILE.write_text(api_content, encoding='utf-8')
        print(f"   ✅ {API_DOCS_FILE}")
        
        # 更新 README
        readme_update = self.generate_readme_update()
        if README_FILE.exists():
            readme = README_FILE.read_text(encoding='utf-8')
            # 查找系统架构部分并替换
            if "## 📊 系统架构" in readme:
                # 简单替换（实际应该更智能）
                print(f"   ⚠️  README 需要手动更新架构部分")
            else:
                # 追加到末尾
                readme += "\n\n" + readme_update
                README_FILE.write_text(readme, encoding='utf-8')
                print(f"   ✅ {README_FILE}")
        
        # 保存哈希缓存
        cache = {}
        for file_name in TARGET_FILES:
            file_path = SCRIPTS_DIR / file_name
            if file_path.exists():
                cache[file_name] = compute_file_hash(file_path)
        save_hash_cache(cache)
        print(f"   ✅ 哈希缓存已保存")
        
        print("\n✅ 文档更新完成！")

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("📝 灵犀文档自动更新")
    print("=" * 60)
    
    generator = DocGenerator()
    
    # 扫描文件
    generator.scan_files()
    
    # 检查 README 版本顺序
    print("\n🔍 检查文档质量...")
    version_order_ok = generator.check_readme_versions()
    
    # 检查变更
    old_cache = load_hash_cache()
    changes = []
    
    for file_name in TARGET_FILES:
        file_path = SCRIPTS_DIR / file_name
        if file_path.exists():
            new_hash = compute_file_hash(file_path)
            old_hash = old_cache.get(file_name, "")
            
            if new_hash != old_hash:
                changes.append(f"更新 {file_name}")
                print(f"   🔄 {file_name} 有变更")
            else:
                print(f"   ✓ {file_name} 无变更")
    
    # 保存文档
    generator.save_all()
    
    # 生成更新日志（如果有变更）
    if changes:
        changelog_entry = generator.generate_changelog_entry(changes)
        if CHANGELOG_FILE.exists():
            existing = CHANGELOG_FILE.read_text(encoding='utf-8')
            CHANGELOG_FILE.write_text(changelog_entry + existing, encoding='utf-8')
        else:
            CHANGELOG_FILE.write_text(changelog_entry, encoding='utf-8')
        print(f"\n📝 更新日志已记录：{CHANGELOG_FILE}")
    
    print("\n" + "=" * 60)
    print("✅ 文档更新完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
