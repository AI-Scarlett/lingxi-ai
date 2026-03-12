#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 统一配置管理中心
从环境变量和 .env 文件读取配置
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional, List
import os


class Settings(BaseSettings):
    """灵犀统一配置"""
    
    # ========== API 配置 ==========
    DASHSCOPE_API_KEY: str = Field(
        default="",
        description="阿里云 DashScope API 密钥（图像生成）"
    )
    
    QWEN_API_KEY: str = Field(
        default="",
        description="通义千问 API 密钥（LLM 调用）"
    )
    
    PERPLEXITY_API_KEY: str = Field(
        default="",
        description="Perplexity API 密钥（搜索）"
    )
    
    # ========== 数据库配置 ==========
    DB_PATH: str = Field(
        default="~/.openclaw/workspace/.lingxi/dashboard_v3.db",
        description="SQLite 数据库路径"
    )
    
    # ========== Dashboard 配置 ==========
    DASHBOARD_PORT: int = Field(
        default=8765,
        ge=1024,
        le=65535,
        description="Dashboard 服务端口"
    )
    
    DASHBOARD_HOST: str = Field(
        default="0.0.0.0",
        description="Dashboard 监听地址"
    )
    
    DASHBOARD_TOKEN: Optional[str] = Field(
        default=None,
        description="Dashboard 访问令牌"
    )
    
    # ========== 日志配置 ==========
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别 (DEBUG/INFO/WARNING/ERROR)"
    )
    
    LOG_DIR: str = Field(
        default="~/.openclaw/workspace/.lingxi/logs",
        description="日志目录"
    )
    
    # ========== 性能配置 ==========
    MAX_CONCURRENT_TASKS: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="最大并发任务数"
    )
    
    CACHE_TTL: int = Field(
        default=60,
        ge=0,
        description="缓存过期时间（秒）"
    )
    
    # ========== OpenClaw 路径 ==========
    OPENCLAW_DIR: str = Field(
        default="~/.openclaw",
        description="OpenClaw 根目录"
    )
    
    # ========== Redis 配置 (可选) ==========
    REDIS_HOST: Optional[str] = Field(
        default=None,
        description="Redis 服务器地址"
    )
    
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis 端口"
    )
    
    REDIS_DB: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis 数据库编号"
    )
    
    # ========== 功能开关 ==========
    ENABLE_DASHBOARD: bool = Field(
        default=True,
        description="是否启用 Dashboard"
    )
    
    ENABLE_LOGGING: bool = Field(
        default=True,
        description="是否启用日志"
    )
    
    ENABLE_CACHE: bool = Field(
        default=True,
        description="是否启用缓存"
    )
    
    # ========== 版本信息 ==========
    VERSION: str = Field(
        default="v3.3.6",
        description="灵犀版本号"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = Settings()
    return _settings


# 便捷函数
def get_dashboard_url() -> str:
    """获取 Dashboard 访问地址"""
    settings = get_settings()
    return f"http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}"


def get_db_path() -> Path:
    """获取数据库文件路径"""
    settings = get_settings()
    return Path(settings.DB_PATH).expanduser()


def get_log_dir() -> Path:
    """获取日志目录"""
    settings = get_settings()
    log_dir = Path(settings.LOG_DIR).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


if __name__ == "__main__":
    # 测试配置加载
    settings = get_settings()
    
    print("灵犀配置中心 v" + settings.VERSION)
    print("=" * 50)
    print(f"Dashboard 端口：{settings.DASHBOARD_PORT}")
    print(f"日志级别：{settings.LOG_LEVEL}")
    print(f"最大并发：{settings.MAX_CONCURRENT_TASKS}")
    print(f"缓存 TTL: {settings.CACHE_TTL}s")
    print(f"数据库路径：{get_db_path()}")
    print(f"日志目录：{get_log_dir()}")
    print("=" * 50)
    
    # 检查必需配置
    if not settings.DASHSCOPE_API_KEY:
        print("⚠️  警告：DASHSCOPE_API_KEY 未配置")
    if not settings.QWEN_API_KEY:
        print("⚠️  警告：QWEN_API_KEY 未配置")
