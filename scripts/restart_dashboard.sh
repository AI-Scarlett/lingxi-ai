#!/bin/bash
# 灵犀 Dashboard 自动重启脚本
# 用法：./restart_dashboard.sh [start|stop|restart|status]

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$SCRIPT_DIR/../dashboard"
LOG_DIR="$HOME/.openclaw/workspace/.lingxi/logs"
PID_FILE="/var/run/lingxi/dashboard.pid"
LOG_FILE="$LOG_DIR/dashboard_restart.log"

# 确保目录存在
mkdir -p "$LOG_DIR"
mkdir -p "$(dirname $PID_FILE)"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# 检查进程状态
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "✅ Dashboard 运行中 (PID: $PID)"
            return 0
        else
            log "⚠️  PID 文件存在但进程已停止"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        log "❌ Dashboard 未运行"
        return 1
    fi
}

# 启动 Dashboard
start() {
    if check_status; then
        log "Dashboard 已经在运行"
        return 0
    fi
    
    log "🚀 启动 Dashboard..."
    
    cd "$DASHBOARD_DIR"
    nohup /usr/bin/python3 backend/main.py > "$LOG_DIR/dashboard_stdout.log" 2>&1 &
    PID=$!
    
    echo $PID > "$PID_FILE"
    
    # 等待启动
    sleep 3
    
    if ps -p "$PID" > /dev/null 2>&1; then
        log "✅ Dashboard 启动成功 (PID: $PID)"
        
        # 验证 HTTP 服务
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/api/health | grep -q "200"; then
            log "✅ Dashboard HTTP 服务正常"
        else
            log "⚠️  Dashboard HTTP 服务可能未完全启动"
        fi
        
        return 0
    else
        log "❌ Dashboard 启动失败"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止 Dashboard
stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "🛑 停止 Dashboard (PID: $PID)..."
            kill "$PID"
            
            # 等待进程结束
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # 如果还在运行，强制终止
            if ps -p "$PID" > /dev/null 2>&1; then
                log "⚠️  进程未响应，强制终止..."
                kill -9 "$PID"
            fi
            
            log "✅ Dashboard 已停止"
        else
            log "⚠️  进程已停止"
        fi
        rm -f "$PID_FILE"
    else
        log "ℹ️  PID 文件不存在"
    fi
    
    # 清理可能的僵尸进程
    pkill -f "python3.*backend/main.py" 2>/dev/null || true
    log "✅ 清理完成"
}

# 重启 Dashboard
restart() {
    log "🔄 重启 Dashboard..."
    stop
    sleep 2
    start
}

# 主函数
case "${1:-status}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        check_status
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status}"
        exit 1
        ;;
esac
