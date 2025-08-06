#!/bin/bash

# 全平台停止脚本
# 提供整个平台的一键停止功能

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AIRFLOW_MANAGER="$PROJECT_ROOT/airflow/scripts/airflow-manager.sh"

# 颜色输出函数
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# 日志函数
log_info() { green "[INFO] $1"; }
log_warn() { yellow "[WARN] $1"; }
log_error() { red "[ERROR] $1"; }

# 显示横幅
show_banner() {
    cat << 'EOF'

   ____                    _              ____  _       _    __                     
  / ___|_ __ __ ___      _| | ___ _ __   |  _ \| | __ _| |_ / _| ___  _ __ _ __ ___  
 | |   | '__/ _` \ \ /\ / / |/ _ \ '__|  | |_) | |/ _` | __| |_ / _ \| '__| '_ ` _ \ 
 | |___| | | (_| |\ V  V /| |  __/ |     |  __/| | (_| | |_|  _| (_) | |  | | | | | |
  \____|_|  \__,_| \_/\_/ |_|\___|_|     |_|   |_|\__,_|\__|_|  \___/|_|  |_| |_| |_|
                                                                                    
                           全平台服务停止                                    

EOF
}

# 停止Airflow服务
stop_airflow() {
    log_info "停止Airflow服务..."
    
    if [ -f "$AIRFLOW_MANAGER" ]; then
        "$AIRFLOW_MANAGER" stop
        log_info "Airflow服务已停止"
    else
        log_warn "Airflow管理脚本不存在: $AIRFLOW_MANAGER"
    fi
}

# 停止后端服务
stop_backend() {
    log_info "停止后端服务..."
    # TODO: 实现后端服务停止逻辑
    log_warn "后端服务停止功能待实现"
}

# 停止前端服务
stop_frontend() {
    log_info "停止前端服务..."
    # TODO: 实现前端服务停止逻辑
    log_warn "前端服务停止功能待实现"
}

# 主函数
main() {
    show_banner
    
    log_info "开始停止所有服务..."
    
    # 停止各个服务
    stop_airflow
    stop_backend
    stop_frontend
    
    echo
    green "🛑 所有服务已停止！"
    echo
}

# 执行主函数
main "$@"