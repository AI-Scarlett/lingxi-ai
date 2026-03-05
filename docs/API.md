# 灵犀 (Lingxi) API 文档

> 自动生成 - 最后更新：2026-03-05T14:18:08.497534

---

## 📦 模块概览

| 模块 | 版本 | 描述 |
|------|------|------|
| orchestrator_v2.py | v2.0 | 灵犀 (Lingxi) - 智慧调度系统核心 v2.0
心有灵犀，一点就通

🚀 v2.0 优化重点... |
| auto_retry.py | v2.8.5 | 灵犀 - 自动重试和自愈系统 v2.8.5

目标：减少人工干预，提高成功率
1. GitHub 推... |
| fast_response_layer_v2.py | v2.0 | 灵犀 - 超高速预响应层 v2.0 (扩展版)

目标：实现三大核心目标
1. ⚡ 快速反应 - 响... |
| performance_monitor.py | v2.8.5 | 灵犀 - 性能主动监控系统 v2.8.5

目标：主动发现性能问题，提前预警
1. 实时监控关键指标... |
| learning_layer.py | v2.8.5 | 灵犀 - 自学习层 (Learning Layer) v2.8.5

心有灵犀，越用越聪明 🧠

核... |

---

## 📄 orchestrator_v2.py

### 模块说明

灵犀 (Lingxi) - 智慧调度系统核心 v2.0
心有灵犀，一点就通

🚀 v2.0 优化重点:
1. 集成快速响应层 - 简单问题<5ms 秒回
2. 懒加载组件 - 启动更快
3. LRU 缓存 - 重复问题秒回
4. 正确的执行器路径 - 并行执行正常工作
5. 性能监控 - 每次显示耗时

### 类

#### SubTask

子任务

#### TaskResult

任务结果

#### SmartOrchestrator

灵犀 - 智慧调度系统主控制器 v2.9

### 函数

#### parse_intent()

快速意图识别（带缓存）

#### decompose_task()

根据意图拆解任务

#### execute_once()

执行单次任务（不含重试）

#### fallback_execute()

降级执行方案

#### execute_subtask()

执行子任务（带重试和降级）

Args:
    subtask: 子任务对象
    max_concurrent: 最大并发数（未使用，保留兼容性）
    max_retries: 最大重试次数（默认 3 次）

Returns:
    SubTask: 执行结果

#### score_subtask()

评分

#### aggregate_results()

汇总结果

#### get_orchestrator()

获取全局实例

#### git_push()

便捷 Git 推送函数

#### main()

测试

#### _default_stats()

默认统计

#### _load_stats()

加载统计信息

#### _save_stats()

保存统计信息

#### execute()

执行用户任务（带全局异常处理）

#### get_stats()

获取统计信息

---

## 📄 auto_retry.py

### 模块说明

灵犀 - 自动重试和自愈系统 v2.8.5

目标：减少人工干预，提高成功率
1. GitHub 推送自动重试（指数退避）
2. 任务执行自愈机制（重试 + 降级）
3. 主动错误提醒（重复错误预警）

### 类

#### RetryConfig

重试配置

#### GitPushManager

Git 推送管理器（带自动重试）

#### SelfHealingExecutor

自愈执行器

### 函数

#### calculate_delay()

计算重试延迟（指数退避 + 抖动）

#### get_git_push_manager()

获取 Git 推送管理器实例

#### get_self_healing_executor()

获取自愈执行器实例

#### main()

测试入口

#### push()

推送到 GitHub（自动重试，带 5 分钟超时）

#### _is_retryable_error()

判断是否是可重试的错误

#### _record_push()

记录推送历史

#### _send_push_failure_alert()

发送推送失败警报

#### get_statistics()

获取执行统计

#### execute()

执行任务（带自愈机制）

#### _record_execution()

记录执行历史

#### _send_failure_alert()

发送失败警报

---

## 📄 fast_response_layer_v2.py

### 模块说明

灵犀 - 超高速预响应层 v2.0 (扩展版)

目标：实现三大核心目标
1. ⚡ 快速反应 - 响应速度极致快
2. 💰 Tokens 消耗极限降低 - 能省则省
3. 🧠 记忆永不丢失 - 持久化存储

分层架构：
- Layer 0: 零思考响应 (<5ms) - 纯规则匹配，不调 LLM
- Layer 1: 缓存响应 (<10ms) - LRU Cache 命中
- Layer 2: 快速 LLM (<500ms) - 单轮对话，轻量模型
- Layer 3: 后台执行 - 复杂任务，先确认后执行

### 类

#### FastResponse

快速响应规则

#### CacheEntry

缓存条目（带时间戳）

#### LRUCache

LRU 缓存 - 带 TTL 过期机制

#### ResponseResult

响应结果

### 函数

#### normalize_text()

文本归一化 - 提高匹配率

#### match_layer0()

Layer 0: 零思考响应匹配（优化版）

优化点：
1. 按优先级排序匹配
2. 最长匹配优先
3. 提前返回

#### get_cached_response()

Layer 1: 缓存响应

#### cache_response()

缓存响应

#### fast_respond()

超高速响应入口 v2.0

Args:
    user_input: 用户输入
    skip_layers: 跳过的层（测试用）

Returns:
    ResponseResult

#### run_benchmark()

性能基准测试

#### is_expired()

检查是否过期

#### put()

添加缓存（支持自定义 TTL）

#### _remove()

移除缓存条目

#### clear_expired()

清理所有过期条目，返回清理数量

---

## 📄 performance_monitor.py

### 模块说明

灵犀 - 性能主动监控系统 v2.8.5

目标：主动发现性能问题，提前预警
1. 实时监控关键指标
2. 对比基线发现异常
3. 主动告警和推荐优化
4. 生成性能趋势报告

### 类

#### MonitorConfig

监控配置

#### PerformanceMetrics

性能指标

#### PerformanceMonitor

性能监控器

#### PerformanceReportGenerator

性能报告生成器

### 函数

#### get_performance_monitor()

获取性能监控器实例

#### get_report_generator()

获取报告生成器实例

#### main()

测试入口

#### record_metrics()

记录性能指标

#### _check_anomalies()

检查性能异常

#### _is_duplicate_alert()

检查是否是重复告警

#### _send_alert()

发送告警

#### calculate_baseline()

计算性能基线（支持 EWMA 指数加权移动平均）

#### get_current_status()

获取当前性能状态

#### _load_history()

加载历史记录

#### _save_history()

保存历史记录

#### get_statistics()

获取统计信息

#### generate_daily_report()

生成日报

#### save_report()

保存报告

---

## 📄 learning_layer.py

### 模块说明

灵犀 - 自学习层 (Learning Layer) v2.8.5

心有灵犀，越用越聪明 🧠

核心功能:
1. 错误自动捕获 - 监听执行结果，检测错误
2. 学习日志自动生成 - ERRORS.md / LEARNINGS.md / FEATURES.md
3. 经验自动提炼 - 定期 Review，更新核心记忆
4. Hook 机制 - 启动提醒 + 后置检测

### 类

#### ErrorLog

错误日志

#### LearningLog

学习经验日志

#### FeatureRequest

功能需求日志

#### LearningLogger

学习日志管理器

#### ErrorDetector

错误检测器

#### LearningLayer

学习层主控制器

### 函数

#### generate_log_id()

生成学习日志 ID

#### get_learning_layer()

获取学习层实例

#### to_markdown()

转换为 Markdown 格式

#### _init_files()

初始化日志文件

#### _get_header()

获取文件头

#### _append_to_file()

追加内容到文件

#### log_error()

记录错误日志

#### log_learning()

记录学习经验

#### log_feature_request()

记录功能需求

#### _auto_tag_error()

自动标记错误类型

#### _extract_pattern_key()

提取 Pattern-Key (用于追踪重复问题)

#### get_recent_errors()

获取最近的错误日志

#### get_statistics()

获取统计信息

#### detect()

检测是否包含错误

#### _check_dict()

检查字典是否包含错误

#### _check_string()

检查字符串是否包含错误关键词

#### analyze_and_log()

分析结果并记录错误日志

#### __init__()

初始化学习层

Args:
    max_history: 历史记录最大条数（默认 1000，防止内存泄漏）

#### on_task_start()

任务开始时的 Hook

#### on_task_complete()

任务完成时的 Hook

#### on_user_correction()

用户纠正时的 Hook

#### on_document_error()

文档错误检测 Hook（新增）

#### on_feature_request()

功能需求记录

#### _estimate_complexity()

估算功能复杂度

#### weekly_review()

每周 Review (调用 AI 提炼经验)

---

