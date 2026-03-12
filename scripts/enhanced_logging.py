#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 增强日志系统
统一使用 loguru 进行日志记录
"""

from loguru import logger
import sys
from pathlib import Path

# 日志目录
LOG_DIR = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 移除默认处理器
logger.remove()

# 添加控制台输出（彩色）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# 添加文件输出（INFO 级别）
logger.add(
    LOG_DIR / "lingxi_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    encoding="utf-8",
    compression="zip"
)

# 添加错误文件输出（ERROR 级别）
logger.add(
    LOG_DIR / "lingxi_errors_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="90 days",
    level="ERROR",
    encoding="utf-8",
    compression="zip"
)

# 添加调试文件输出（DEBUG 级别，可选）
# logger.add(
#     LOG_DIR / "lingxi_debug_{time:YYYY-MM-DD}.log",
#     rotation="50 MB",
#     retention="7 days",
#     level="DEBUG",
#     encoding="utf-8"
# )


def get_logger(name: str = "lingxi"):
    """获取命名日志器"""
    return logger.bind(name=name)


# 装饰器：自动记录函数执行
def log_execution(func):
    """记录函数执行日志的装饰器"""
    from functools import wraps
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger.info(f"开始执行：{func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.success(f"执行完成：{func.__name__}")
            return result
        except Exception as e:
            logger.error(f"执行失败：{func.__name__} - {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger.info(f"开始执行：{func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.success(f"执行完成：{func.__name__}")
            return result
        except Exception as e:
            logger.error(f"执行失败：{func.__name__} - {str(e)}")
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# 全局日志实例
lingxi_logger = get_logger()

if __name__ == "__main__":
    # 测试日志
    lingxi_logger.debug("调试消息")
    lingxi_logger.info("信息消息")
    lingxi_logger.warning("警告消息")
    lingxi_logger.error("错误消息")
    lingxi_logger.success("成功消息")
