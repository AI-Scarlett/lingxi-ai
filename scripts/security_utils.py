#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 安全工具函数 v2.8.5

目标：增强系统安全性，防止注入和未授权访问
1. 输入清洗 - 防止注入攻击
2. 路径白名单 - 限制文件访问范围
3. 安全日志 - 记录敏感操作
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import asyncio

# ==================== 配置 ====================

import os

# 安全文件路径白名单（从环境变量读取，支持自定义）
SAFE_PATHS_ENV = os.getenv(
    "LINGXI_SAFE_PATHS",
    f"{Path.home()}/.openclaw/workspace,{Path.home()}/.openclaw/skills,{Path.home()}/.openclaw/extensions"
)
SAFE_PATHS = [Path(p.strip()) for p in SAFE_PATHS_ENV.split(",")]

# 禁止访问的路径
FORBIDDEN_PATHS_ENV = os.getenv(
    "LINGXI_FORBIDDEN_PATHS",
    "/etc,/root/.ssh,/proc,/sys,/dev,/boot,/var/log"
)
FORBIDDEN_PATHS = [p.strip() for p in FORBIDDEN_PATHS_ENV.split(",")]

# 危险命令关键词
DANGEROUS_COMMANDS = [
    "rm -rf",
    "rm -fr",
    "dd if=",
    "mkfs",
    "chmod 777",
    "chown root",
    "sudo",
    "su -",
    "wget",
    "curl",
    "nc ",
    "netcat",
    "python -c",
    "python3 -c",
    "perl -e",
    "ruby -e",
    "eval(",
    "exec(",
    "__import__",
]

# 日志文件
SECURITY_LOG = Path.home() / ".openclaw" / "workspace" / ".learnings" / "security.log"

# ==================== 输入清洗 ====================

class InputSanitizer:
    """输入清洗器"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 10000) -> str:
        """清洗字符串输入"""
        if not input_str:
            return ""
        
        # 限制长度
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # 移除控制字符（保留换行和制表符）
        input_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_str)
        
        # 移除潜在的注入模式
        dangerous_patterns = [
            r'\$\([^)]+\)',      # 命令替换 $()
            r'`[^`]+`',          # 反引号命令替换
            r'\|\|',             # 管道
            r'&&',               # 逻辑与
            r';\s*\w+',          # 分号分隔命令
            r'>\s*/',            # 重定向到根目录
            r'<\s*/',            # 从根目录读取
        ]
        
        for pattern in dangerous_patterns:
            input_str = re.sub(pattern, '', input_str)
        
        return input_str.strip()
    
    @staticmethod
    def sanitize_file_path(file_path: str) -> Optional[str]:
        """清洗文件路径"""
        if not file_path:
            return None
        
        # 清洗路径
        file_path = InputSanitizer.sanitize_string(file_path, max_length=1000)
        
        # 解析路径
        try:
            path = Path(file_path).resolve()
        except Exception as e:
            # 容错处理
            return None
        
        # 检查是否在白名单内
        if not InputSanitizer.is_path_allowed(path):
            return None
        
        return str(path)
    
    @staticmethod
    def sanitize_command(command: str) -> Optional[str]:
        """清洗命令"""
        if not command:
            return None
        
        # 清洗命令
        command = InputSanitizer.sanitize_string(command, max_length=5000)
        
        # 检查危险命令
        command_lower = command.lower()
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                log_security_event("dangerous_command", {
                    "command": command[:200],
                    "dangerous_keyword": dangerous
                })
                return None
        
        return command
    
    @staticmethod
    def sanitize_json(json_str: str) -> Optional[Dict]:
        """清洗并解析 JSON"""
        if not json_str:
            return None
        
        try:
            # 限制长度
            if len(json_str) > 100000:
                json_str = json_str[:100000]
            
            # 解析 JSON
            data = json.loads(json_str)
            
            # 递归清洗字符串值
            return InputSanitizer._sanitize_json_data(data)
        
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def _sanitize_json_data(data: Any) -> Any:
        """递归清洗 JSON 数据"""
        if isinstance(data, str):
            return InputSanitizer.sanitize_string(data)
        elif isinstance(data, dict):
            return {k: InputSanitizer._sanitize_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer._sanitize_json_data(item) for item in data]
        else:
            return data

# ==================== 路径白名单检查 ====================

class PathWhitelist:
    """路径白名单检查器"""
    
    def __init__(self, allowed_paths: List[Path] = None):
        self.allowed_paths = allowed_paths or SAFE_PATHS.copy()
        self.forbidden_paths = FORBIDDEN_PATHS.copy()
    
    def add_allowed_path(self, path: str):
        """添加允许的路径"""
        try:
            resolved = Path(path).resolve()
            if resolved not in self.allowed_paths:
                self.allowed_paths.append(resolved)
                log_security_event("path_whitelist_updated", {
                    "action": "add",
                    "path": str(resolved)
                })
        except Exception as e:
            log_security_event("path_whitelist_error", {
                "action": "add",
                "path": path,
                "error": str(e)
            })
    
    def remove_allowed_path(self, path: str):
        """移除允许的路径"""
        try:
            resolved = Path(path).resolve()
            if resolved in self.allowed_paths:
                self.allowed_paths.remove(resolved)
                log_security_event("path_whitelist_updated", {
                    "action": "remove",
                    "path": str(resolved)
                })
        except Exception as e:
            log_security_event("path_whitelist_error", {
                "action": "remove",
                "path": path,
                "error": str(e)
            })
    
    def is_path_allowed(self, path: str) -> bool:
        """检查路径是否允许访问"""
        if not path:
            return False
        
        try:
            # 解析并规范化路径
            resolved = Path(path).resolve()
            path_str = str(resolved)
            
            # 检查是否在禁止列表中
            for forbidden in self.forbidden_paths:
                if path_str.startswith(forbidden):
                    log_security_event("forbidden_path_access", {
                        "path": path_str,
                        "forbidden_prefix": forbidden
                    })
                    return False
            
            # 检查是否在允许列表中
            for allowed in self.allowed_paths:
                try:
                    # 检查路径是否在允许路径的子目录中
                    resolved.relative_to(allowed)
                    return True
                except ValueError:
                    continue
            
            # 不在任何允许路径中
            log_security_event("path_not_allowed", {
                "path": path_str,
                "allowed_paths": [str(p) for p in self.allowed_paths]
            })
            return False
        
        except Exception as e:
            log_security_event("path_check_error", {
                "path": path,
                "error": str(e)
            })
            return False
    
    def safe_open(self, path: str, mode: str = 'r', **kwargs):
        """安全地打开文件"""
        if not self.is_path_allowed(path):
            raise PermissionError(f"Path not allowed: {path}")
        
        # 额外的安全检查
        if 'w' in mode and Path(path).exists():
            # 写操作时检查文件权限
            stat_info = Path(path).stat()
            if stat_info.st_mode & 0o002:  # 检查是否 world-writable
                log_security_event("insecure_file_permission", {
                    "path": path,
                    "mode": oct(stat_info.st_mode)
                })
        
        return open(path, mode, **kwargs)

# ==================== 安全日志 ====================

def log_security_event(event_type: str, details: Dict):
    """记录安全事件"""
    try:
        SECURITY_LOG.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        with open(SECURITY_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    except Exception as e:
        # 日志记录失败时打印到控制台
        print(f"⚠️  安全日志记录失败：{e}")

def get_security_logs(hours: int = 24) -> List[Dict]:
    """获取最近的安全日志"""
    if not SECURITY_LOG.exists():
        return []
    
    logs = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    try:
        with open(SECURITY_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(log_entry["timestamp"])
                    if timestamp >= cutoff:
                        logs.append(log_entry)
                except Exception as e:
                    # 容错处理
                    continue
    
    except Exception as e:
        print(f"⚠️  读取安全日志失败：{e}")
    
    return logs

# ==================== 文件权限检查 ====================

class FilePermissionChecker:
    """文件权限检查器"""
    
    @staticmethod
    def check_file_permissions(path: str) -> Dict[str, Any]:
        """检查文件权限"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"exists": False}
            
            stat_info = file_path.stat()
            
            return {
                "exists": True,
                "is_file": file_path.is_file(),
                "is_dir": file_path.is_dir(),
                "mode": oct(stat_info.st_mode)[-3:],
                "owner_uid": stat_info.st_uid,
                "group_gid": stat_info.st_gid,
                "is_world_writable": bool(stat_info.st_mode & 0o002),
                "is_world_readable": bool(stat_info.st_mode & 0o004),
                "is_executable": bool(stat_info.st_mode & 0o001),
                "recommendations": FilePermissionChecker._get_recommendations(stat_info.st_mode, file_path)
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_recommendations(mode: int, path: Path) -> List[str]:
        """获取权限建议"""
        recommendations = []
        
        # 检查是否 world-writable
        if mode & 0o002:
            recommendations.append(f"⚠️  文件 {path} 对所有用户可写，建议：chmod o-w {path}")
        
        # 检查敏感文件是否权限过大
        sensitive_patterns = ['.env', '.key', '.pem', '.secret', 'password', 'credential']
        if any(pattern in path.name.lower() for pattern in sensitive_patterns):
            if mode & 0o044:  # 其他人可读
                recommendations.append(f"🔒 敏感文件 {path} 建议：chmod 600 {path}")
        
        # 检查脚本文件是否可执行
        if path.suffix in ['.sh', '.py', '.bash'] and not (mode & 0o001):
            recommendations.append(f"💡 脚本文件 {path} 可能需要执行权限：chmod +x {path}")
        
        return recommendations

# ==================== 全局实例 ====================

_input_sanitizer = InputSanitizer()
_path_whitelist = PathWhitelist()
_permission_checker = FilePermissionChecker()

def get_input_sanitizer() -> InputSanitizer:
    """获取输入清洗器实例"""
    return _input_sanitizer

def get_path_whitelist() -> PathWhitelist:
    """获取路径白名单检查器实例"""
    return _path_whitelist

def get_permission_checker() -> FilePermissionChecker:
    """获取权限检查器实例"""
    return _permission_checker

# ==================== 测试入口 ====================

async def main():
    """测试入口"""
    print("=" * 60)
    print("🔒 灵犀安全工具测试")
    print("=" * 60)
    
    # 测试输入清洗
    print("\n1️⃣ 测试输入清洗")
    sanitizer = get_input_sanitizer()
    
    test_cases = [
        ("正常字符串", "Hello World"),
        ("命令注入", "ls && rm -rf /"),
        ("命令替换", "$(whoami)"),
        ("超长字符串", "A" * 20000),
    ]
    
    for name, test_input in test_cases:
        result = sanitizer.sanitize_string(test_input)
        print(f"   {name}: {len(result)} 字符 (原：{len(test_input)} 字符)")
    
    # 测试路径白名单
    print("\n2️⃣ 测试路径白名单")
    whitelist = get_path_whitelist()
    
    test_paths = [
        ("/root/.openclaw/workspace/test.txt", True),
        ("/etc/passwd", False),
        ("/root/.ssh/id_rsa", False),
    ]
    
    for path, expected in test_paths:
        result = whitelist.is_path_allowed(path)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {path}: {'允许' if result else '拒绝'}")
    
    # 测试权限检查
    print("\n3️⃣ 测试权限检查")
    checker = get_permission_checker()
    
    result = checker.check_file_permissions("/root/.openclaw/workspace")
    if "error" not in result:
        print(f"   路径：{result.get('mode', 'N/A')}")
        if result.get('recommendations'):
            print(f"   建议：{len(result['recommendations'])} 条")
    
    # 查看安全日志
    print("\n4️⃣ 安全日志")
    logs = get_security_logs(hours=1)
    print(f"   最近 1 小时事件：{len(logs)} 条")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    from datetime import timedelta
    asyncio.run(main())
