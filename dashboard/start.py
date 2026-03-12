#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard v4.0 启动脚本

使用方法:
    python start.py              # 默认模式
    python start.py --host 0.0.0.0 --port 8765
    python start.py --dev        # 开发模式（热重载）
"""

import argparse
import sys
from pathlib import Path

# 添加 backend 到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def main():
    parser = argparse.ArgumentParser(description="灵犀 Dashboard v4.0")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="监听端口 (默认: 8765)")
    parser.add_argument("--dev", action="store_true", help="开发模式")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 灵犀 Dashboard v4.0                                     ║
║                                                              ║
║   现代化 AI 助手数据看板                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        import uvicorn
        
        reload = args.dev and not args.no_reload
        
        print(f"📡 启动服务器: http://{args.host}:{args.port}")
        print(f"📁 数据目录: ~/.openclaw/workspace/.lingxi/")
        print(f"🔧 开发模式: {'开启' if reload else '关闭'}")
        print("")
        
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        print("❌ 请先安装依赖:")
        print("   pip install fastapi uvicorn aiosqlite")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 再见!")

if __name__ == "__main__":
    main()
