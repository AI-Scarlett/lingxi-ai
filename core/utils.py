#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共工具函数

提取重复代码，提供统一的工具函数
"""

import sys
import importlib
from typing import Optional, Any


def safe_import(module_name: str, package: Optional[str] = None) -> Any:
    """
    安全导入模块
    
    Args:
        module_name: 模块名
        package: 包名（可选）
    
    Returns:
        模块对象，导入失败返回 None
    """
    try:
        return importlib.import_module(module_name, package)
    except ImportError as e:
        print(f"⚠️  警告：无法导入 {module_name}: {e}")
        return None


def safe_get_env(key: str, default: str = None) -> Optional[str]:
    """
    安全获取环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
    
    Returns:
        环境变量值，不存在返回 default
    """
    import os
    value = os.environ.get(key)
    
    if not value and default:
        return default
    
    if not value:
        print(f"⚠️  警告：环境变量 {key} 未设置")
    
    return value


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
    
    Returns:
        格式化后的大小（KB/MB/GB）
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        是否有效
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_production() -> bool:
    """
    判断是否生产环境
    
    Returns:
        是否生产环境
    """
    import os
    return os.environ.get("ENVIRONMENT") == "production"


def get_python_version() -> str:
    """
    获取 Python 版本
    
    Returns:
        版本号字符串
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def check_python_version(min_version: str = "3.8.0") -> bool:
    """
    检查 Python 版本
    
    Args:
        min_version: 最低版本要求
    
    Returns:
        是否满足要求
    """
    from packaging import version
    
    current = get_python_version()
    return version.parse(current) >= version.parse(min_version)
