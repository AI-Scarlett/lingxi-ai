#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 v3.3.3 配置常量

所有魔法数字和阈值定义在这里
"""

# ========== 时间阈值（毫秒）==========

RESPONSE_TIME_WARNING_THRESHOLD = 500  # 慢响应警告阈值
RESPONSE_TIME_CRITICAL_THRESHOLD = 1000  # 严重延迟阈值
TASK_TIMEOUT_DEFAULT = 30000  # 默认任务超时（30 秒）
TASK_TIMEOUT_LONG = 60000  # 长任务超时（60 秒）

# ========== 记忆系统 ==========

MEMORY_STM_CAPACITY = 100  # STM 容量（条数）
MEMORY_STM_TTL_HOURS = 24  # STM 过期时间（小时）
MEMORY_MTM_DAYS = 7  # MTM 保留天数
MEMORY_COMPRESS_THRESHOLD_CHARS = 500  # 压缩阈值（字符数）
MEMORY_IMPORTANCE_HIGH = 9.0  # 高重要性阈值
MEMORY_IMPORTANCE_MEDIUM = 7.0  # 中等重要性阈值

# ========== 任务系统 ==========

TASK_MAX_CONCURRENT = 100  # 最大并发任务数
TASK_QUEUE_SIZE = 1000  # 任务队列大小
TASK_RETRY_MAX = 3  # 最大重试次数

# ========== 学习系统 ==========

LEARNING_FREQUENCY_THRESHOLD = 3  # 高频问题阈值（次/天）
LEARNING_RULE_AUTO_APPLY = True  # 自动应用学习规则
LEARNING_REVIEW_INTERVAL_DAYS = 7  # 复习间隔（天）

# ========== 抓取系统 ==========

FETCH_TIMEOUT_DEFAULT = 30  # 默认超时（秒）
FETCH_MAX_RETRIES = 3  # 最大重试次数
FETCH_JINA_TIMEOUT = 10  # Jina 超时（秒）
FETCH_SCRAPLING_TIMEOUT = 60  # Scrapling 超时（秒）

# ========== API 限制 ==========

API_RATE_LIMIT_PER_MINUTE = 60  # 每分钟 API 调用限制
API_BATCH_SIZE = 10  # 批量处理大小

# ========== Dashboard ==========

DASHBOARD_DEFAULT_PORT = 8765  # 默认端口
DASHBOARD_TOKEN_EXPIRY_DAYS = 7  # Token 有效期（天）

# ========== 日志 ==========

LOG_LEVEL_DEFAULT = "INFO"
LOG_MAX_SIZE_MB = 10  # 日志文件最大大小（MB）
LOG_BACKUP_COUNT = 5  # 日志备份数量
