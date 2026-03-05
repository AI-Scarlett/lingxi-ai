#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 (Lingxi) - 性能基准测试

使用 pytest-benchmark 进行性能测试
确保每次修改不影响核心性能指标

运行方式:
    pip install pytest-benchmark
    pytest tests/benchmarks.py --benchmark-only
    pytest tests/benchmarks.py --benchmark-compare  # 对比上一次结果
"""

import pytest
import time
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# ==================== 导入测试目标 ====================

from fast_response_layer_v2 import fast_respond, cache_response, LRUCache
from learning_layer import ErrorDetector, LearningLogger, ERROR_KEYWORDS
from performance_monitor import PerformanceMonitor, PerformanceMetrics
from orchestrator_v2 import parse_intent, decompose_task

# ==================== Layer 0: 快速响应基准测试 ====================

class TestFastResponse:
    """快速响应层基准测试"""
    
    @pytest.fixture
    def warm_cache(self):
        """预热缓存"""
        cache_response("你好", "老板好呀～💋")
        cache_response("在吗", "在呢老板～😊")
        return
    
    def test_layer0_greeting(self, benchmark):
        """测试 Layer 0 问候响应 (<5ms)"""
        result = benchmark(fast_respond, "你好")
        assert result.layer == "layer0"
        assert result.tokens_saved is True
    
    def test_layer0_thanks(self, benchmark):
        """测试 Layer 0 感谢响应"""
        result = benchmark(fast_respond, "谢谢")
        assert result.layer == "layer0"
        assert result.latency_ms < 10  # 应该 <5ms
    
    def test_layer0_time(self, benchmark):
        """测试 Layer 0 时间查询 (动态响应)"""
        result = benchmark(fast_respond, "几点了")
        assert result.layer == "layer0"
        assert result.response is not None
    
    def test_layer1_cached(self, benchmark, warm_cache):
        """测试 Layer 1 缓存命中 (<10ms)"""
        result = benchmark(fast_respond, "你好")
        assert result.cache_hit is True or result.layer == "layer0"
    
    def test_layer3_passthrough(self, benchmark):
        """测试 Layer 3 直通 (复杂问题)"""
        result = benchmark(fast_respond, "帮我写一个复杂的 Python 脚本，需要实现...")
        assert result.layer == "passthrough"
        assert result.tokens_saved is False

# ==================== LRU 缓存基准测试 ====================

class TestLRUCache:
    """LRU 缓存基准测试"""
    
    @pytest.fixture
    def cache(self):
        return LRUCache(capacity=1000, default_ttl=3600)
    
    def test_cache_put(self, benchmark, cache):
        """测试缓存写入"""
        benchmark(cache.put, "test_key", "test_value")
        assert cache.get("test_key") == "test_value"
    
    def test_cache_get_hit(self, benchmark, cache):
        """测试缓存命中读取"""
        cache.put("key1", "value1")
        result = benchmark(cache.get, "key1")
        assert result == "value1"
    
    def test_cache_get_miss(self, benchmark, cache):
        """测试缓存未命中"""
        result = benchmark(cache.get, "nonexistent")
        assert result is None
    
    def test_cache_ttl_expiration(self, benchmark, cache):
        """测试 TTL 过期 (短 TTL)"""
        cache.put("temp", "value", ttl=1)  # 1 秒过期
        time.sleep(1.1)
        result = benchmark(cache.get, "temp")
        assert result is None  # 已过期
    
    def test_cache_clear_expired(self, benchmark, cache):
        """测试清理过期条目"""
        # 添加一些短 TTL 条目
        for i in range(10):
            cache.put(f"temp_{i}", f"value_{i}", ttl=1)
        time.sleep(1.1)
        cleared = benchmark(cache.clear_expired)
        assert cleared == 10

# ==================== 错误检测基准测试 ====================

class TestErrorDetection:
    """错误检测基准测试"""
    
    @pytest.fixture
    def detector(self):
        return ErrorDetector()
    
    def test_detect_english_error(self, benchmark, detector):
        """测试英文错误检测"""
        result = benchmark(detector.detect, {"error": "Connection timeout"})
        assert result is True
    
    def test_detect_chinese_error(self, benchmark, detector):
        """测试中文错误检测"""
        result = benchmark(detector.detect, {"message": "连接超时失败"})
        assert result is True
    
    def test_detect_no_error(self, benchmark, detector):
        """测试无错误情况"""
        result = benchmark(detector.detect, {"success": True, "data": "ok"})
        assert result is False
    
    def test_detect_all_keywords(self, benchmark, detector):
        """测试所有错误关键词"""
        for keyword in ERROR_KEYWORDS:
            result = detector.detect(f"Test {keyword} message")
            assert result is True, f"关键词 '{keyword}' 未检测到"

# ==================== 意图识别基准测试 ====================

class TestIntentRecognition:
    """意图识别基准测试"""
    
    def test_intent_content_creation(self, benchmark):
        """测试内容创作意图识别"""
        result = benchmark(parse_intent, "帮我写一篇小红书文案")
        assert "content_creation" in result["types"]
    
    def test_intent_image_generation(self, benchmark):
        """测试图片生成意图识别"""
        result = benchmark(parse_intent, "生成一张封面图")
        assert "image_generation" in result["types"]
    
    def test_intent_social_publish(self, benchmark):
        """测试社交发布意图识别"""
        result = benchmark(parse_intent, "发到小红书")
        assert "social_publish" in result["types"]
        assert result["platform"] == "小红书"
    
    def test_intent_mixed(self, benchmark):
        """测试混合意图识别"""
        result = benchmark(parse_intent, "写个小红书文案并发到朋友圈")
        assert len(result["types"]) >= 2

# ==================== 任务拆解基准测试 ====================

class TestTaskDecomposition:
    """任务拆解基准测试"""
    
    def test_decompose_simple(self, benchmark):
        """测试简单任务拆解"""
        intent = parse_intent("你好")
        subtasks = benchmark(decompose_task, "你好", intent)
        assert len(subtasks) >= 1
    
    def test_decompose_complex(self, benchmark):
        """测试复杂任务拆解"""
        user_input = "帮我写一篇小红书文案，生成封面图，然后发布"
        intent = parse_intent(user_input)
        subtasks = benchmark(decompose_task, user_input, intent)
        assert len(subtasks) >= 3  # 至少 3 个子任务
    
    def test_decompose_with_platform(self, benchmark):
        """测试带平台的任务拆解"""
        intent = {"types": ["social_publish"], "platform": "小红书"}
        subtasks = benchmark(decompose_task, "发小红书", intent)
        assert len(subtasks) >= 1

# ==================== 性能监控基准测试 ====================

class TestPerformanceMonitor:
    """性能监控基准测试"""
    
    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()
    
    def test_record_metrics(self, benchmark, monitor):
        """测试指标记录"""
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            avg_latency_ms=50.0,
            p95_latency_ms=100.0,
            p99_latency_ms=200.0,
            request_count=100,
            error_count=2,
            error_rate=0.02,
            fast_response_rate=0.65,
            cache_hit_rate=0.30
        )
        benchmark(monitor.record_metrics, metrics)
    
    def test_calculate_baseline_simple(self, benchmark, monitor):
        """测试简单基线计算"""
        # 先添加一些测试数据
        for i in range(10):
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                avg_latency_ms=50.0 + i,
                p95_latency_ms=100.0,
                p99_latency_ms=200.0,
                request_count=100,
                error_count=2,
                error_rate=0.02,
                fast_response_rate=0.65,
                cache_hit_rate=0.30
            )
            monitor.record_metrics(metrics)
        
        baseline = benchmark(monitor.calculate_baseline, 1, False)
        assert "avg_latency_ms" in baseline
    
    def test_calculate_baseline_ewma(self, benchmark, monitor):
        """测试 EWMA 基线计算"""
        # 先添加一些测试数据
        for i in range(10):
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                avg_latency_ms=50.0 + i,
                p95_latency_ms=100.0,
                p99_latency_ms=200.0,
                request_count=100,
                error_count=2,
                error_rate=0.02,
                fast_response_rate=0.65,
                cache_hit_rate=0.30
            )
            monitor.record_metrics(metrics)
        
        baseline = benchmark(monitor.calculate_baseline, 1, True)
        assert "avg_latency_ms" in baseline
        assert baseline.get("method") == "ewma"

# ==================== 端到端基准测试 ====================

class TestEndToEnd:
    """端到端基准测试"""
    
    def test_simple_greeting(self, benchmark):
        """测试简单问候端到端延迟"""
        result = benchmark(fast_respond, "你好")
        assert result.latency_ms < 10  # 应该 <10ms
    
    def test_complex_query(self, benchmark):
        """测试复杂查询端到端延迟"""
        result = benchmark(fast_respond, "帮我分析一下最近的数据并生成报告")
        # 复杂问题应该直通到 LLM
        assert result.layer == "passthrough"

# ==================== 性能要求 (CI 检查) ====================

class TestPerformanceRequirements:
    """性能要求测试 (CI 自动检查)"""
    
    def test_layer0_latency(self):
        """Layer 0 响应时间 <5ms"""
        result = fast_respond("你好")
        assert result.latency_ms < 5, f"Layer 0 延迟 {result.latency_ms:.2f}ms > 5ms"
    
    def test_layer1_latency(self):
        """Layer 1 缓存响应 <10ms"""
        cache_response("test", "response")
        result = fast_respond("test")
        assert result.latency_ms < 10, f"Layer 1 延迟 {result.latency_ms:.2f}ms > 10ms"
    
    def test_error_detection_coverage(self):
        """错误检测覆盖率 >95%"""
        detector = ErrorDetector()
        detected = 0
        total = len(ERROR_KEYWORDS)
        
        for keyword in ERROR_KEYWORDS:
            if detector.detect(f"Test {keyword} message"):
                detected += 1
        
        coverage = detected / total * 100
        assert coverage >= 95, f"错误检测覆盖率 {coverage:.1f}% < 95%"
    
    def test_cache_ttl_works(self):
        """缓存 TTL 必须正常工作"""
        cache = LRUCache(capacity=100, default_ttl=3600)
        cache.put("temp", "value", ttl=1)
        time.sleep(1.1)
        assert cache.get("temp") is None, "缓存 TTL 未生效"

# ==================== 运行基准测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 灵犀性能基准测试")
    print("=" * 60)
    print("\n运行方式:")
    print("  pytest tests/benchmarks.py --benchmark-only")
    print("  pytest tests/benchmarks.py --benchmark-compare")
    print("\n性能要求:")
    print("  - Layer 0: <5ms")
    print("  - Layer 1: <10ms")
    print("  - 错误检测：>95% 覆盖率")
    print("  - 缓存 TTL: 必须正常工作")
    print("=" * 60)
