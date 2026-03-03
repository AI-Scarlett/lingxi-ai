#!/usr/bin/env python3
"""
通过 GitHub API 推送代码
需要设置 GITHUB_TOKEN 环境变量
"""

import os
import sys
import subprocess
import base64
import requests

REPO_OWNER = "AI-Scarlett"
REPO_NAME = "lingxi-ai"
BRANCH = "main"

def get_github_token():
    """获取 GitHub Token"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # 尝试从文件读取
        token_file = os.path.expanduser("~/.github_token")
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
    
    if not token:
        print("❌ 未找到 GITHUB_TOKEN")
        print("\n获取 Token 步骤:")
        print("1. 访问 https://github.com/settings/tokens")
        print("2. 点击 'Generate new token (classic)'")
        print("3. 选择权限：repo (Full control of private repositories)")
        print("4. 生成后复制 token")
        print("5. 设置环境变量：export GITHUB_TOKEN=<your_token>")
        print("   或保存到文件：echo '<your_token>' > ~/.github_token")
        sys.exit(1)
    
    return token

def get_current_commit():
    """获取当前最新提交"""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return result.stdout.strip()

def list_changed_files():
    """列出需要推送的文件"""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 获取最近一次提交的变更文件
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        capture_output=True,
        text=True,
        cwd=repo_dir
    )
    
    files = result.stdout.strip().split('\n')
    return [f for f in files if f]

def main():
    print("🚀 通过 GitHub API 推送代码...\n")
    
    token = get_github_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取当前提交
    commit_hash = get_current_commit()
    print(f"📦 当前提交：{commit_hash}")
    
    # 获取变更文件
    files = list_changed_files()
    print(f"📝 变更文件：{len(files)} 个\n")
    
    for file in files[:10]:  # 限制显示前 10 个
        print(f"  - {file}")
    
    if len(files) > 10:
        print(f"  ... 还有 {len(files) - 10} 个文件")
    
    print("\n💡 由于 GitHub API 限制，建议使用以下方式推送:")
    print("\n方式 1 - 使用 Git 命令行（推荐）:")
    print("  cd ~/.openclaw/skills/lingxi")
    print("  git remote set-url origin https://<TOKEN>@github.com/AI-Scarlett/lingxi-ai.git")
    print("  git push origin main")
    print("\n方式 2 - 使用 SSH:")
    print("  cd ~/.openclaw/skills/lingxi")
    print("  git remote set-url origin git@github.com:AI-Scarlett/lingxi-ai.git")
    print("  git push origin main")
    print("\n方式 3 - 手动上传:")
    print("  1. 访问 https://github.com/AI-Scarlett/lingxi-ai")
    print("  2. 点击 'Add file' → 'Upload files'")
    print("  3. 拖拽文件上传")
    print("  4. 提交更改")

if __name__ == "__main__":
    main()
