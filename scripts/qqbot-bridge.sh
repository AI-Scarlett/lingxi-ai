#!/bin/bash
# 灵犀 QQ Bot 桥接器 - Shell 包装器
# 供 QQ Bot Gateway 调用

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_SCRIPT="$SCRIPT_DIR/qqbot_bridge.py"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：需要 Python3" >&2
    exit 1
fi

# 显示帮助
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "用法：qqbot-bridge.sh --user-id <openid> --message <消息> [--channel qqbot]"
    echo "      qqbot-bridge.sh --user-id <openid> --query [--task-id <任务 ID>]"
    echo ""
    echo "选项:"
    echo "  --user-id    用户 ID (QQ openid)"
    echo "  --message    消息内容"
    echo "  --channel    渠道 (默认 qqbot)"
    echo "  --query      查询任务状态"
    echo "  --task-id    任务 ID（查询时指定）"
    echo "  --json       输出 JSON 格式"
    exit 0
fi

# 执行 Python 脚本
python3 "$BRIDGE_SCRIPT" "$@"
