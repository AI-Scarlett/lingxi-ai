# OpenClaw 启动配置
# 在 OpenClaw 启动时自动加载此文件

import sys
from pathlib import Path

# 添加灵犀脚本路径
LINGXI_PATH = Path("/root/lingxi-ai-latest")
if LINGXI_PATH.exists():
    sys.path.insert(0, str(LINGXI_PATH / "scripts"))
    print("✅ 灵犀路径已添加到 Python path")

# ⚠️ 自动加载任务记录器（已禁用，避免干扰 OpenClaw 记忆系统）
# 原因：注入导致 OpenClaw embedded agent 超时（10 分钟）
# 替代方案：使用定时同步脚本（scripts/sync_openclaw_tasks.py）
# try:
#     from openclaw_task_recorder import inject_openclaw, on_message_completed, record_task
#     print("✅ 灵犀任务记录器已加载")
#     
#     # 自动注入到 OpenClaw
#     inject_openclaw()
#     
# except ImportError as e:
#     print(f"⚠️ 任务记录器加载失败：{e}")

# 示例：手动记录函数（可在自定义代码中调用）
def log_task(user_input, user_id, channel, response, model="qwen3.5-plus"):
    """便捷函数：记录任务到 Dashboard"""
    import time
    start = time.time()
    # 这里会被 OpenClaw 实际处理逻辑覆盖
    # 实际响应时间会在 inject_openclaw 中计算
    record_task(
        user_input=user_input,
        user_id=user_id,
        channel=channel,
        final_output=response,
        llm_model=model
    )

print("🦞 灵犀 - OpenClaw 集成完成")
