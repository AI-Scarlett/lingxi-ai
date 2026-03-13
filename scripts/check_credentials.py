#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀凭证和安全检查脚本

功能：
- 检查必要的配置文件是否存在
- 检查凭证文件权限是否正确
- 检查是否有未声明的凭证使用
- 提供安全配置建议

使用：
python3 scripts/check_credentials.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_check(passed, message, suggestion=None):
    if passed:
        print(f"{Colors.GREEN}✅{Colors.END} {message}")
    else:
        print(f"{Colors.RED}❌{Colors.END} {message}")
        if suggestion:
            print(f"   {Colors.YELLOW}建议：{suggestion}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {Colors.END}{message}")

def check_file_exists(path, required=False, description=""):
    """检查文件是否存在"""
    exists = Path(path).exists()
    if required:
        print_check(exists, f"{description}: {path}", 
                   f"创建文件：touch {path}")
    else:
        if exists:
            print_check(True, f"{description}: {path}")
        else:
            print_warning(f"{description}: {path} (可选，未配置)")
    return exists

def check_file_permissions(path, expected_perms="600"):
    """检查文件权限"""
    if not Path(path).exists():
        return True
    
    try:
        import stat
        current_perms = oct(os.stat(path).st_mode)[-3:]
        passed = current_perms == expected_perms
        print_check(passed, f"文件权限 {path}: {current_perms}",
                   f"修改权限：chmod {expected_perms} {path}")
        return passed
    except Exception as e:
        print_warning(f"无法检查 {path} 权限：{e}")
        return False

def check_directory_writable(path):
    """检查目录是否可写"""
    try:
        test_file = Path(path) / ".write_test"
        test_file.touch()
        test_file.unlink()
        print_check(True, f"目录可写：{path}")
        return True
    except Exception as e:
        print_check(False, f"目录不可写：{path}",
                   f"修改权限：chmod 755 {path}")
        return False

def check_env_variable(name, required=False):
    """检查环境变量"""
    value = os.environ.get(name)
    if value:
        masked = value[:4] + "..." if len(value) > 4 else "***"
        print_check(True, f"环境变量 {name}: {masked}")
        return True
    else:
        if required:
            print_check(False, f"环境变量 {name}: 未设置",
                       f"设置：export {name}=your_value")
        else:
            print_warning(f"环境变量 {name}: 未设置 (可选)")
        return False

def check_git_credentials_in_history():
    """检查 Git 历史中是否有凭证泄露"""
    print_header("Git 历史凭证检查")
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "-p", "--all", "-S", "ghp_", "--oneline"],
            capture_output=True, text=True, timeout=10,
            cwd="/root/lingxi-ai-latest"
        )
        
        if result.stdout.strip():
            print_check(False, "发现 Git 历史中包含 'ghp_' 的提交")
            print_warning("建议：使用 git filter-branch 或 BFG 清理历史")
            return False
        else:
            print_check(True, "Git 历史中未发现明显凭证泄露")
            return True
    except Exception as e:
        print_warning(f"Git 历史检查失败：{e}")
        return True

def check_dashboard_token():
    """检查 Dashboard Token 配置"""
    print_header("Dashboard 配置检查")
    
    token_file = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "dashboard_token.txt"
    check_file_exists(token_file, required=False, description="Dashboard Token")
    
    if token_file.exists():
        check_file_permissions(token_file, "600")
        
        # 检查 Token 格式
        try:
            token = token_file.read_text().strip()
            if len(token) >= 20:
                print_check(True, "Token 格式：有效")
            else:
                print_check(False, "Token 格式：过短",
                           "生成新 Token: openssl rand -hex 32")
        except Exception as e:
            print_check(False, f"Token 读取失败：{e}")

def check_database():
    """检查数据库配置"""
    print_header("数据库配置检查")
    
    db_path = Path("/root/lingxi-ai-latest/data/dashboard_v3.db")
    check_file_exists(db_path, required=True, description="Dashboard 数据库")
    
    if db_path.exists():
        check_file_permissions(db_path, "644")
    
    # 检查数据库目录
    check_directory_writable(Path("/root/lingxi-ai-latest/data"))

def check_openclaw_integration():
    """检查 OpenClaw 集成"""
    print_header("OpenClaw 集成检查")
    
    config_file = Path.home() / ".openclaw" / "openclaw.json"
    check_file_exists(config_file, required=True, description="OpenClaw 配置")
    
    # 检查任务记录器
    recorder_path = Path("/root/lingxi-ai-latest/scripts/openclaw_task_recorder.py")
    check_file_exists(recorder_path, required=False, description="任务记录器")
    
    startup_path = Path.home() / ".openclaw" / "workspace" / "lingxi_startup.py"
    check_file_exists(startup_path, required=False, description="启动脚本")

def check_logs():
    """检查日志配置"""
    print_header("日志配置检查")
    
    log_dir = Path("/tmp/lingxi-ai-latest/logs")
    if log_dir.exists():
        check_directory_writable(log_dir)
        
        # 检查日志文件大小
        try:
            total_size = sum(f.stat().st_size for f in log_dir.glob("*.log"))
            size_mb = total_size / 1024 / 1024
            if size_mb > 100:
                print_warning(f"日志文件过大：{size_mb:.1f} MB，建议清理")
            else:
                print_check(True, f"日志文件大小：{size_mb:.1f} MB")
        except:
            pass
    else:
        print_warning(f"日志目录不存在：{log_dir}")

def check_security_best_practices():
    """检查安全最佳实践"""
    print_header("安全最佳实践检查")
    
    # 检查 .gitignore
    gitignore_path = Path("/root/lingxi-ai-latest/.gitignore")
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        required_entries = [".git_token", "dashboard_token.txt", "*.key", "*.secret"]
        missing = [e for e in required_entries if e not in content]
        
        if missing:
            print_warning(f".gitignore 缺少条目：{', '.join(missing)}")
        else:
            print_check(True, ".gitignore 包含必要的忽略规则")
    else:
        print_warning(".gitignore 文件不存在")
    
    # 检查是否有凭证提交到 Git
    check_git_credentials_in_history()

def generate_report():
    """生成检查报告"""
    print_header("安全检查报告")
    
    report_path = Path("/root/lingxi-ai-latest/security_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"灵犀安全配置检查报告\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"版本：v3.3.6\n\n")
        
        f.write("已检查项目：\n")
        f.write("- Dashboard Token 配置\n")
        f.write("- 数据库配置\n")
        f.write("- OpenClaw 集成\n")
        f.write("- 文件权限\n")
        f.write("- Git 历史凭证\n")
        f.write("- 日志配置\n")
        f.write("- 安全最佳实践\n\n")
        
        f.write("详细文档：SECURITY_AND_CONFIG.md\n")
    
    print_check(True, f"检查报告已生成：{report_path}")

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}🦞 灵犀凭证和安全检查 v3.3.6{Colors.END}")
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行所有检查
    check_dashboard_token()
    check_database()
    check_openclaw_integration()
    check_logs()
    check_security_best_practices()
    
    # 生成报告
    generate_report()
    
    print_header("检查完成")
    print(f"\n{Colors.BOLD}详细文档：{Colors.END}SECURITY_AND_CONFIG.md")
    print(f"{Colors.BOLD}问题反馈：{Colors.END}https://github.com/AI-Scarlett/lingxi-ai/issues\n")

if __name__ == "__main__":
    main()
