#!/bin/bash
# 灵犀 - Git 推送辅助脚本
# 自动重试 + 多镜像源支持

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."
MAX_RETRIES=3
TIMEOUT=60

# 远程仓库列表
REMOTES=(
    "origin:https://github.com/AI-Scarlett/lingxi-ai.git"
    "gitee:https://gitee.com/AI-Scarlett/lingxi-ai.git"
)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 推送到指定远程
push_to_remote() {
    local remote=$1
    local url=$2
    
    log "尝试推送到 $remote ($url)..."
    
    cd "$REPO_DIR"
    
    if timeout $TIMEOUT git push "$remote" main 2>&1; then
        log "✅ 推送到 $remote 成功"
        return 0
    else
        log "❌ 推送到 $remote 失败"
        return 1
    fi
}

# 主推送函数（带重试）
push_with_retry() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        log "第 $attempt 次尝试..."
        
        # 尝试所有远程仓库
        for remote_info in "${REMOTES[@]}"; do
            IFS=':' read -r remote url <<< "$remote_info"
            
            if push_to_remote "$remote" "$url"; then
                return 0
            fi
            
            sleep 2
        done
        
        log "等待 10 秒后重试..."
        sleep 10
        ((attempt++))
    done
    
    log "❌ 所有尝试都失败了"
    return 1
}

# 检查 Git 状态
check_status() {
    cd "$REPO_DIR"
    
    log "Git 状态:"
    git status --short
    
    log "未推送的提交:"
    git log --oneline HEAD..origin/main 2>/dev/null || echo "无未推送的提交"
}

# 主函数
case "${1:-push}" in
    push)
        log "🚀 开始推送代码..."
        push_with_retry
        ;;
    status)
        check_status
        ;;
    add-remote)
        # 添加备用远程
        cd "$REPO_DIR"
        git remote add gitee https://gitee.com/AI-Scarlett/lingxi-ai.git 2>/dev/null || true
        log "✅ Gitee 远程仓库已添加"
        ;;
    sync)
        # 同步所有远程
        cd "$REPO_DIR"
        git fetch --all
        git pull origin main
        push_with_retry
        ;;
    *)
        echo "用法：$0 {push|status|add-remote|sync}"
        exit 1
        ;;
esac
