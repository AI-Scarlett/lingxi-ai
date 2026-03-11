#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 Dashboard 访问地址查看工具

功能：
- 显示所有访问地址
- 生成可保存的访问卡片
- 强调安全注意事项
- 支持导出为文本文件
"""

from quick_access import QuickAccessGenerator
from pathlib import Path
import time


def generate_access_card(generator: QuickAccessGenerator) -> str:
    """生成访问卡片（可保存）"""
    
    inner_url = generator.get_inner_url()
    token = list(generator.tokens.keys())[-1] if generator.tokens else generator.generate_access_token()
    outer_url = generator.get_outer_url(token)
    mobile_url = generator.get_mobile_url(token)
    public_ip = generator.get_public_ip()
    
    card = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🚀 灵犀 Dashboard 访问地址卡                         ║
║                                                                  ║
║  生成时间：{time.strftime("%Y-%m-%d %H:%M:%S")}
║  有效期：30 天
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📡 内网访问（同一 WiFi）                                         ║
║  ────────────────────────────────────────────────────────────    ║
║  💻 电脑：{inner_url:<50} ║
║  📱 手机：{inner_url + "/mobile":<50} ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
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
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ⚠️⚠️⚠️  重要安全提示  ⚠️⚠️⚠️                                     ║
║  ────────────────────────────────────────────────────────────    ║
║                                                                  ║
║  🔒 以上访问地址包含你的专属 Token，请勿泄露！                    ║
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
╚══════════════════════════════════════════════════════════════════╝
"""
    
    return card


def print_access_info():
    """打印访问信息"""
    generator = QuickAccessGenerator()
    
    # 生成新 token
    token = generator.generate_access_token()
    
    # 获取访问地址
    inner_url = generator.get_inner_url()
    outer_url = generator.get_outer_url(token)
    mobile_url = generator.get_mobile_url(token)
    public_ip = generator.get_public_ip()
    
    print()
    print("=" * 70)
    print("📩 灵犀 Dashboard 访问地址")
    print("=" * 70)
    print()
    
    print("📡 内网访问（同一 WiFi）:")
    print(f"   💻 电脑：{inner_url}")
    print(f"   📱 手机：{mobile_url}")
    print()
    
    print("🌐 外网访问（任何地方）:")
    print(f"   💻 电脑：{outer_url}")
    print(f"   📱 手机：{mobile_url}")
    print()
    
    print(f"🌍 你的公网 IP: {public_ip}")
    print()
    
    print("🔑 访问 Token:")
    print(f"   {token}")
    print(f"   有效期：30 天")
    print()
    
    print("-" * 70)
    print()
    
    # 安全警告
    print("⚠️⚠️⚠️  重要安全提示  ⚠️⚠️⚠️")
    print()
    print("🔒 以上访问地址包含你的专属 Token，")
    print("🔒 请勿泄露给任何人！")
    print()
    print("❌ 不要发给陌生人")
    print("❌ 不要发到公开群聊")
    print("❌ 不要发到社交媒体")
    print("❌ 不要截图分享")
    print()
    print("✅ 仅限自己使用")
    print("✅ 如已泄露，请立即撤销并重新生成")
    print()
    print("撤销命令：python3 quick_access.py --revoke {token}")
    print("生成新的：python3 quick_access.py --generate-token")
    print()
    print("=" * 70)
    print()
    
    # 询问是否保存
    save = input("💾 是否保存访问地址到文件？(y/n): ").strip().lower()
    if save == 'y':
        save_access_card(generator)


def save_access_card(generator: QuickAccessGenerator):
    """保存访问卡片到文件"""
    
    card = generate_access_card(generator)
    
    # 生成文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = Path.home() / ".openclaw" / "workspace" / ".lingxi" / f"access_card_{timestamp}.txt"
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存
    filename.write_text(card, encoding='utf-8')
    
    print()
    print(f"✅ 访问地址已保存到：{filename}")
    print()
    print("💡 提示：可以将此文件保存到安全的地方，")
    print("   但不要分享给他人！")
    print()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--save":
            # 直接保存
            generator = QuickAccessGenerator()
            generator.generate_access_token()
            save_access_card(generator)
        elif sys.argv[1] == "--help":
            print("""
📩 灵犀 Dashboard 访问地址查看工具

用法:
  python3 show_access.py              # 显示访问地址
  python3 show_access.py --save       # 显示并保存到文件
  python3 show_access.py --help       # 显示帮助
""")
        else:
            print(f"❌ 未知参数：{sys.argv[1]}")
            print("使用 --help 查看帮助")
    else:
        print_access_info()


if __name__ == "__main__":
    main()
