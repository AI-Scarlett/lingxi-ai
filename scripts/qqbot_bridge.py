#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 - QQ Bot 桥接器
作为 QQ Bot Gateway 和灵犀异步系统之间的桥梁

用法:
    python3 qqbot_bridge.py --user-id <openid> --message "消息内容" --channel qqbot
"""

import asyncio
import argparse
import json
import sys
import os

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lingxi_qqbot import handle_qq_message, query_task_status

async def process_message(user_id: str, message: str, channel: str = "qqbot") -> dict:
    """处理消息并返回结果
    
    Args:
        user_id: 用户 ID (QQ openid)
        message: 消息内容
        channel: 渠道
        
    Returns:
        JSON 格式的结果
    """
    try:
        print(f"[桥接器] 收到消息 - 用户：{user_id}", file=sys.stderr)
        print(f"[桥接器] 消息：{message[:100]}", file=sys.stderr)
        
        # 调用灵犀处理
        reply = await handle_qq_message(user_id, message, channel)
        
        print(f"[桥接器] 回复：{reply[:200]}", file=sys.stderr)
        
        return {
            "success": True,
            "reply": reply,
            "user_id": user_id,
            "message": message
        }
    
    except Exception as e:
        print(f"[桥接器] 错误：{e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        return {
            "success": False,
            "error": str(e),
            "reply": f"抱歉，处理出问题了：{str(e)[:100]}"
        }

async def query_status(user_id: str, task_id: str = None) -> dict:
    """查询任务状态
    
    Args:
        user_id: 用户 ID
        task_id: 任务 ID（可选）
        
    Returns:
        JSON 格式的状态
    """
    try:
        status = await query_task_status(user_id, task_id)
        
        return {
            "success": True,
            "status": status
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="灵犀 QQ Bot 桥接器")
    parser.add_argument("--user-id", required=True, help="用户 ID (QQ openid)")
    parser.add_argument("--message", help="消息内容")
    parser.add_argument("--channel", default="qqbot", help="渠道 (默认 qqbot)")
    parser.add_argument("--query", action="store_true", help="查询任务状态")
    parser.add_argument("--task-id", help="任务 ID（查询时指定）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    if args.query:
        # 查询模式
        result = asyncio.run(query_status(args.user_id, args.task_id))
    else:
        # 消息处理模式
        if not args.message:
            print("错误：需要指定 --message", file=sys.stderr)
            sys.exit(1)
        
        result = asyncio.run(process_message(args.user_id, args.message, args.channel))
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        if result.get("success"):
            print(result.get("reply", ""))
        else:
            print(f"错误：{result.get('error', '未知错误')}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
