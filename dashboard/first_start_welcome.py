#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 首次启动欢迎消息

功能：
- 检测是否首次启动
- 生成欢迎消息
- 显示访问地址
- 强调安全注意事项
- 提供快速入门指南
"""

from pathlib import Path
import time
from quick_access import QuickAccessGenerator


def check_first_start() -> bool:
    """检查是否首次启动"""
    marker_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / ".started_before"
    
    if not marker_file.exists():
        # 首次启动
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(str(time.time()))
        return True
    
    return False


def generate_welcome_message() -> str:
    """生成欢迎消息"""
    
    generator = QuickAccessGenerator()
    token = generator.generate_access_token()
    
    inner_url = generator.get_inner_url()
    outer_url = generator.get_outer_url(token)
    mobile_url = generator.get_mobile_url(token)
    public_ip = generator.get_public_ip()
    
    message = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🎉 欢迎使用灵犀 Dashboard v3.3.3 完全体！                  ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📩 你的专属访问地址（已自动生成）                                 ║
║                                                                  ║
╠──────────────────────────────────────────────────────────────────╣
║                                                                  ║
║  📡 内网访问（同一 WiFi）                                         ║
║  ────────────────────────────────────────────────────────────    ║
║  💻 电脑：{inner_url:<50} ║
║  📱 手机：{inner_url + "/mobile":<50} ║
║                                                                  ║
╠──────────────────────────────────────────────────────────────────╣
║                                                                  ║
║  🌐 外网访问（任何地方）                                          ║
║  ────────────────────────────────────────────────────────────    ║
║  💻 电脑：{outer_url:<50} ║
║  📱 手机：{mobile_url:<50} ║
║                                                                  ║
║  🌍 公网 IP: {public_ip:<53} ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🔑 访问 Token: {token:<50} ║
║     有效期：30 天                                                 ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ⚠️⚠️⚠️  重要安全提示  ⚠️⚠️⚠️                                     ║
║  ────────────────────────────────────────────────────────────    ║
║                                                                  ║
║  🔒 以上访问地址包含你的专属 Token，请勿泄露！                      ║
║                                                                  ║
║  ❌ 不要发给陌生人                                               ║
║  ❌ 不要发到公开群聊                                               ║
║  ❌ 不要发到社交媒体                                               ║
║  ❌ 不要截图分享                                                   ║
║                                                                  ║
║  ✅ 仅限自己使用                                                   ║
║  ✅ 如已泄露，请立即撤销并重新生成                                 ║
║                                                                  ║
║  撤销命令：python3 quick_access.py --revoke {token:<30} ║
║  生成新的：python3 quick_access.py --generate-token              ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🚀 快速入门                                                     ║
║  ────────────────────────────────────────────────────────────    ║
║                                                                  ║
║  1️⃣  内网访问（推荐）                                             ║
║     手机连接同一 WiFi，访问上面的内网地址                          ║
║                                                                  ║
║  2️⃣  外网访问（任何地方）                                         ║
║     需要配置路由器端口映射（5 分钟）                               ║
║     查看教程：dashboard/NAT_PORT_FORWARDING.md                   ║
║                                                                  ║
║  3️⃣  查看访问地址                                                ║
║     随时运行：python3 show_access.py                             ║
║                                                                  ║
║  4️⃣  保存访问地址                                                ║
║     运行：python3 show_access.py --save                          ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📚 帮助文档                                                     ║
║  ────────────────────────────────────────────────────────────    ║
║                                                                  ║
║  • 小白用户指南：dashboard/BEGINNER_GUIDE.md                    ║
║  • 外网访问配置：dashboard/NAT_PORT_FORWARDING.md               ║
║  • 完整功能文档：/root/.openclaw/workspace/                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

💡 提示：
   - 这是首次启动，已自动生成访问地址
   - 以后启动会直接显示，无需重新生成
   - Token 有效期 30 天，过期自动续期
   - 如有问题，请查看帮助文档

✅ Dashboard 正在启动，请稍候...

"""
    
    return message


def show_welcome():
    """显示欢迎消息"""
    
    if check_first_start():
        # 首次启动
        message = generate_welcome_message()
        print(message)
        
        # 保存访问卡片
        generator = QuickAccessGenerator()
        from show_access import save_access_card
        save_access_card(generator)
        
    else:
        # 非首次启动，显示简化版
        generator = QuickAccessGenerator()
        
        # 检查是否有有效 token
        tokens = generator.list_tokens()
        
        if not tokens:
            # 没有有效 token，生成新的
            generator.generate_access_token()
        
        # 显示访问地址
        from show_access import print_access_info
        print_access_info()


def main():
    """主函数"""
    show_welcome()


if __name__ == "__main__":
    main()
