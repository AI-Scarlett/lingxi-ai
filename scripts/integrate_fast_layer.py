#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - 快速响应层集成示例

展示如何将 FastResponseLayer 集成到现有 Orchestrator 中
"""

from fast_response_layer import fast_respond, cache_response

# ==================== 集成到 Orchestrator ====================

class OptimizedOrchestrator:
    """优化后的编排器 - 集成快速响应层"""
    
    def __init__(self):
        self.fast_layer_enabled = True
        self.stats = {
            "layer0_hits": 0,
            "layer1_hits": 0,
            "llm_calls": 0,
            "total_requests": 0
        }
    
    async def execute(self, user_input: str, user_id: str = "default"):
        """
        执行任务 - 带快速响应层
        
        流程：
        1. Layer 0: 零思考响应（<5ms）
        2. Layer 1: 缓存响应（<10ms）
        3. Layer 2: 快速 LLM（<500ms）
        4. Layer 3: 后台执行（复杂任务）
        """
        self.stats["total_requests"] += 1
        
        # ===== Layer 0 & 1: 快速响应 =====
        if self.fast_layer_enabled:
            result = fast_respond(user_input)
            
            if result.layer in ["layer0", "layer1"]:
                # 记录统计
                if result.layer == "layer0":
                    self.stats["layer0_hits"] += 1
                else:
                    self.stats["layer1_hits"] += 1
                
                # 缓存响应（如果是 Layer 2 下来的）
                if result.layer == "layer2" and result.response:
                    cache_response(user_input, result.response)
                
                # 直接返回，不调用 LLM
                return {
                    "response": result.response,
                    "latency_ms": result.latency_ms,
                    "layer": result.layer,
                    "tokens_saved": result.tokens_saved,
                    "source": "fast_layer"
                }
        
        # ===== Layer 2/3: 需要 LLM =====
        self.stats["llm_calls"] += 1
        
        # 这里是原有的 LLM 调用逻辑
        # ...
        
        # 模拟 LLM 响应
        response = f"老板，我正在处理：{user_input}"
        
        # 缓存结果（供下次使用）
        cache_response(user_input, response)
        
        return {
            "response": response,
            "latency_ms": 300,  # 模拟
            "layer": "layer2",
            "tokens_saved": False,
            "source": "llm"
        }
    
    def get_stats(self):
        """获取统计信息"""
        total = self.stats["total_requests"]
        return {
            **self.stats,
            "fast_layer_rate": f"{(self.stats['layer0_hits'] + self.stats['layer1_hits']) / total * 100:.1f}%" if total > 0 else "0%",
            "tokens_saved_count": (self.stats["layer0_hits"] + self.stats["layer1_hits"]) * 200
        }

# ==================== 使用示例 ====================

async def demo():
    """演示使用"""
    orch = OptimizedOrchestrator()
    
    test_inputs = [
        "你好",
        "在吗",
        "帮我写个文案",
        "谢谢",
        "帮我写个文案",  # 重复，应该走缓存
        "几点了",
        "开发一个系统"
    ]
    
    print("🚀 集成演示开始...\n")
    
    for inp in test_inputs:
        result = await orch.execute(inp)
        print(f"输入：{inp}")
        print(f"  响应：{result['response']}")
        print(f"  延迟：{result['latency_ms']:.3f}ms")
        print(f"  来源：{result['layer']} ({result['source']})")
        print(f"  Tokens 节省：{'✅' if result['tokens_saved'] else '❌'}")
        print()
    
    # 统计
    stats = orch.get_stats()
    print("📊 统计信息:")
    print(f"  总请求：{stats['total_requests']}")
    print(f"  Layer 0 命中：{stats['layer0_hits']}")
    print(f"  Layer 1 命中：{stats['layer1_hits']}")
    print(f"  LLM 调用：{stats['llm_calls']}")
    print(f"  快速层命中率：{stats['fast_layer_rate']}")
    print(f"  节省 Tokens: {stats['tokens_saved_count']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
