#!/bin/bash

# Airflow快速启动脚本
# 提供一键部署Airflow服务的功能

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
                                                                                    
                           Airflow 工作流调度平台                                    

EOF
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux 系统"
    else
        log_warn "未知操作系统: $OSTYPE"
    fi
    
    # 检查内存
    if [[ "$OSTYPE" == "darwin"* ]]; then
        total_mem=$(sysctl -n hw.memsize)
        total_mem_gb=$((total_mem / 1024 / 1024 / 1024))
    else
        total_mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    fi
    
    if [ "$total_mem_gb" -lt 4 ]; then
        log_warn "系统内存不足4GB，可能影响性能"
    else
        log_info "系统内存: ${total_mem_gb}GB ✓"
    fi
    
    # 检查磁盘空间
    available_space=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    # 提取数字部分进行比较
    space_num=$(echo "$available_space" | sed 's/[^0-9.]//g')
    if [ -n "$space_num" ] && [ "${space_num%.*}" -lt 5 ] 2>/dev/null; then
        log_warn "可用磁盘空间不足5GB，可能影响运行"
    else
        log_info "可用磁盘空间: ${available_space} ✓"
    fi
}

# 检查Docker环境
check_docker_environment() {
    log_info "检查Docker环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        echo "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查Docker版本
    docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    log_info "Docker版本: $docker_version ✓"
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        echo "安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    log_info "Docker Compose版本: $compose_version ✓"
}

# 生成安全密钥
generate_security_keys() {
    log_info "生成安全密钥..."
    
    # 生成Fernet Key
    if command -v python3 &> /dev/null; then
        fernet_key=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
        if [ -n "$fernet_key" ]; then
            log_info "已生成Fernet Key ✓"
        else
            log_warn "无法生成Fernet Key，将使用默认值"
            fernet_key="ZmDfcTF7_60GrrY167zsiPd67pEvs0aGqv7oRpKrHkw="
        fi
    else
        log_warn "Python3未安装，使用默认Fernet Key"
        fernet_key="ZmDfcTF7_60GrrY167zsiPd67pEvs0aGqv7oRpKrHkw="
    fi
    
    # 生成Secret Key
    secret_key=$(openssl rand -base64 32 2>/dev/null || echo "your-secret-key-change-in-production")
    
    # 更新环境变量文件
    env_file="$PROJECT_ROOT/deploy/envs/.env"
    if [ -f "$env_file" ]; then
        sed -i.bak "s|AIRFLOW_FERNET_KEY=.*|AIRFLOW_FERNET_KEY=$fernet_key|" "$env_file"
        sed -i.bak "s|AIRFLOW_SECRET_KEY=.*|AIRFLOW_SECRET_KEY=$secret_key|" "$env_file"
        rm -f "$env_file.bak"
        log_info "已更新安全密钥到环境变量文件 ✓"
    fi
}

# 检查端口占用
check_port_availability() {
    log_info "检查端口可用性..."
    
    local ports=("8080" "8306")
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -i :"$port" &> /dev/null; then
            occupied_ports+=("$port")
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        log_warn "以下端口已被占用: ${occupied_ports[*]}"
        echo "请确保以下端口可用:"
        echo "  - 8080: Airflow Web UI"
        echo "  - 8306: MySQL数据库"
        
        if [ "$FORCE_REBUILD" != "true" ]; then
            read -p "是否继续部署？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "部署已取消"
                save_cancellation_log "${occupied_ports[*]}"
                exit 0
            fi
        else
            log_warn "强制模式下继续部署"
        fi
    else
        log_info "端口检查通过 ✓"
    fi
}

# 显示部署信息
show_deployment_info() {
    cat << EOF

$(blue "=== 部署信息 ===")

服务组件:
  • MySQL 8.0.39 数据库
  • Airflow 2.8.1 工作流平台
  • Python 3.11 运行环境

网络端口:
  • Airflow Web UI: http://localhost:8080
  • MySQL数据库: localhost:8306

默认账户:
  • 用户名: admin
  • 密码: admin123
  • 邮箱: admin@crawler-platform.com

数据目录:
  • MySQL数据: ./data/db/mysql
  • Airflow日志: ./airflow/logs
  • DAG文件: ./airflow/dags

EOF
}

# 确认部署
confirm_deployment() {
    echo
    read -p "$(yellow "确认开始部署Airflow平台？(y/N): ")" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
}

# 检查镜像是否存在
check_image_exists() {
    local image_name="crawler-airflow:latest"
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^$image_name$"; then
        return 0  # 镜像存在
    else
        return 1  # 镜像不存在
    fi
}

# 执行部署
perform_deployment() {
    if [ "$QUIET_MODE" = "true" ]; then
        echo "🚀 正在部署Airflow平台..."
    else
        log_info "开始部署Airflow平台..."
    fi
    
    # 检查管理脚本
    if [ ! -f "$AIRFLOW_MANAGER" ]; then
        log_error "Airflow管理脚本不存在: $AIRFLOW_MANAGER"
        exit 1
    fi
    
    # 初始化环境
    if [ "$QUIET_MODE" = "false" ]; then
        log_info "初始化环境..."
    fi
    "$AIRFLOW_MANAGER" init >/dev/null 2>&1
    
    # 智能构建镜像
    if [ "$FORCE_REBUILD" = "true" ]; then
        if [ "$QUIET_MODE" = "true" ]; then
            echo "🔨 重新构建镜像..."
            if ! "$AIRFLOW_MANAGER" build --no-cache >/dev/null 2>&1; then
                echo "❌ 镜像构建失败！请检查错误信息:"
                "$AIRFLOW_MANAGER" build --no-cache
                exit 1
            fi
        else
            log_info "强制重新构建镜像..."
            if ! "$AIRFLOW_MANAGER" build --no-cache; then
                log_error "镜像构建失败！"
                exit 1
            fi
        fi
    elif check_image_exists; then
        if [ "$QUIET_MODE" = "true" ]; then
            echo "✅ 使用现有镜像"
        else
            log_info "检测到已存在的Airflow镜像，跳过构建步骤"
            log_warn "如需重新构建镜像，请使用 --rebuild 选项或手动执行: $AIRFLOW_MANAGER build"
        fi
    else
        if [ "$QUIET_MODE" = "true" ]; then
            echo "🔨 构建Airflow镜像..."
            if ! "$AIRFLOW_MANAGER" build >/dev/null 2>&1; then
                echo "❌ 镜像构建失败！请检查错误信息:"
                "$AIRFLOW_MANAGER" build
                exit 1
            fi
        else
            log_info "未检测到Airflow镜像，开始构建..."
            if ! "$AIRFLOW_MANAGER" build; then
                log_error "镜像构建失败！"
                exit 1
            fi
        fi
    fi
    
    # 启动服务
    if [ "$QUIET_MODE" = "true" ]; then
        echo "🚀 启动服务..."
    else
        log_info "启动服务..."
    fi
    "$AIRFLOW_MANAGER" start -d >/dev/null 2>&1
    
    # 等待服务启动
    if [ "$QUIET_MODE" = "true" ]; then
        echo "⏳ 等待服务启动..."
        sleep 30
        echo "✅ 服务启动完成"
    else
        log_info "等待服务启动..."
        for i in {1..30}; do
            printf "."
            sleep 1
        done
        echo
    fi
    
    # 检查服务状态
    if [ "$QUIET_MODE" = "false" ]; then
        log_info "检查服务状态..."
        "$AIRFLOW_MANAGER" status
    fi
}

# 保存部署日志
save_deployment_log() {
    local log_dir="$PROJECT_ROOT/logs"
    local log_file="$log_dir/airflow-deployment.log"
    
    # 确保日志目录存在
    mkdir -p "$log_dir"
    
    # 生成部署日志内容
    cat > "$log_file" << EOF
=== Airflow 部署日志 ===
部署时间: $(date '+%Y-%m-%d %H:%M:%S')
部署用户: $(whoami)
项目路径: $PROJECT_ROOT

=== 系统信息 ===
操作系统: $OSTYPE
内存信息: $(if [[ "$OSTYPE" == "darwin"* ]]; then sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)"GB"}'; else free -h | awk '/^Mem:/{print $2}'; fi)
磁盘空间: $(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
Docker版本: $(docker --version)
Docker Compose版本: $(docker-compose --version)

=== 部署配置 ===
强制重建: $FORCE_REBUILD
静默模式: $QUIET_MODE

=== 服务信息 ===
Airflow Web UI: http://localhost:8080
MySQL数据库: localhost:8306
默认用户名: admin
默认密码: admin123

=== 数据目录 ===
MySQL数据: $PROJECT_ROOT/data/db/mysql
Airflow日志: $PROJECT_ROOT/airflow/logs
DAG文件: $PROJECT_ROOT/airflow/dags

=== 管理命令 ===
查看状态: ./airflow/scripts/airflow-manager.sh status
查看日志: ./airflow/scripts/airflow-manager.sh logs
停止服务: ./airflow/scripts/airflow-manager.sh stop
重启服务: ./airflow/scripts/airflow-manager.sh restart

=== 部署完成 ===
部署状态: 成功
完成时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF
}

# 显示部署结果
show_deployment_result() {
    echo
    green "🎉 Airflow平台部署完成！"
    echo
    
    cat << EOF
$(blue "=== 访问信息 ===")

🌐 Web界面: $(green "http://localhost:8080")
👤 用户名: $(green "admin")
🔑 密码: $(green "admin123")

$(blue "=== 管理命令 ===")

# 查看服务状态
./airflow/scripts/airflow-manager.sh status

# 查看日志
./airflow/scripts/airflow-manager.sh logs

# 停止服务
./airflow/scripts/airflow-manager.sh stop

# 重启服务
./airflow/scripts/airflow-manager.sh restart

$(blue "=== 下一步 ===")

1. 访问Web界面并登录
2. 查看示例DAG: example_crawler_workflow
3. 创建自己的DAG文件
4. 阅读文档: ./airflow/README.md

EOF
    
    # 保存部署日志
    save_deployment_log
    
    log_info "部署日志已保存到: $PROJECT_ROOT/logs/airflow-deployment.log"
}

# 错误处理
handle_error() {
    local exit_code=$?
    log_error "部署过程中发生错误 (退出码: $exit_code)"
    
    echo
    echo "$(yellow "故障排除建议:")"
    echo "1. 检查Docker服务是否正常运行"
    echo "2. 确保端口8080和8306未被占用"
    echo "3. 检查系统资源是否充足"
    echo "4. 查看详细日志: ./airflow/scripts/airflow-manager.sh logs"
    echo "5. 重新运行部署脚本"
    
    # 保存错误日志
    save_error_log "$exit_code"
    
    exit $exit_code
}

# 保存取消部署日志
save_cancellation_log() {
    local occupied_ports=$1
    local log_dir="$PROJECT_ROOT/logs"
    local log_file="$log_dir/airflow-deployment.log"
    
    # 确保日志目录存在
    mkdir -p "$log_dir"
    
    # 生成取消部署日志内容
    cat > "$log_file" << EOF
=== Airflow 部署日志 ===
部署时间: $(date '+%Y-%m-%d %H:%M:%S')
部署用户: $(whoami)
项目路径: $PROJECT_ROOT

=== 系统信息 ===
操作系统: $OSTYPE
内存信息: $(if [[ "$OSTYPE" == "darwin"* ]]; then sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)"GB"}'; else free -h | awk '/^Mem:/{print $2}'; fi)
磁盘空间: $(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
Docker版本: $(docker --version 2>/dev/null || echo "未安装")
Docker Compose版本: $(docker-compose --version 2>/dev/null || echo "未安装")

=== 部署配置 ===
强制重建: ${FORCE_REBUILD:-false}
静默模式: ${QUIET_MODE:-false}

=== 取消原因 ===
取消时间: $(date '+%Y-%m-%d %H:%M:%S')
取消原因: 端口冲突
占用端口: $occupied_ports

=== 解决建议 ===
1. 停止占用端口的服务:
   - 端口8080: 可能是其他Web服务
   - 端口8306: 可能是MySQL或其他数据库服务
2. 使用以下命令查看端口占用:
   lsof -i :8080
   lsof -i :8306
3. 停止相关服务后重新运行部署脚本
4. 或者使用 --force 参数强制部署

=== 部署结果 ===
部署状态: 已取消
完成时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF
}

# 保存错误日志
save_error_log() {
    local exit_code=$1
    local log_dir="$PROJECT_ROOT/logs"
    local log_file="$log_dir/airflow-deployment.log"
    
    # 确保日志目录存在
    mkdir -p "$log_dir"
    
    # 生成错误日志内容
    cat > "$log_file" << EOF
=== Airflow 部署日志 ===
部署时间: $(date '+%Y-%m-%d %H:%M:%S')
部署用户: $(whoami)
项目路径: $PROJECT_ROOT

=== 系统信息 ===
操作系统: $OSTYPE
内存信息: $(if [[ "$OSTYPE" == "darwin"* ]]; then sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)"GB"}'; else free -h | awk '/^Mem:/{print $2}'; fi)
磁盘空间: $(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
Docker版本: $(docker --version 2>/dev/null || echo "未安装")
Docker Compose版本: $(docker-compose --version 2>/dev/null || echo "未安装")

=== 部署配置 ===
强制重建: ${FORCE_REBUILD:-false}
静默模式: ${QUIET_MODE:-false}

=== 错误信息 ===
错误时间: $(date '+%Y-%m-%d %H:%M:%S')
退出码: $exit_code
错误描述: 部署过程中发生错误

=== 故障排除建议 ===
1. 检查Docker服务是否正常运行
2. 确保端口8080和8306未被占用
3. 检查系统资源是否充足
4. 查看详细日志: ./airflow/scripts/airflow-manager.sh logs
5. 重新运行部署脚本

=== 部署结果 ===
部署状态: 失败
完成时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF
}

# 主函数
main() {
    # 设置错误处理
    trap handle_error ERR
    
    # 显示横幅
    show_banner
    
    # 系统检查
    check_system_requirements
    check_docker_environment
    check_port_availability
    
    # 生成安全密钥
    generate_security_keys
    
    # 显示部署信息
    show_deployment_info
    
    # 确认部署
    confirm_deployment
    
    # 执行部署
    perform_deployment
    
    # 显示结果
    show_deployment_result
}

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat << EOF
Airflow快速启动脚本

用法: $0 [选项]

选项:
  -h, --help    显示帮助信息
  --force       跳过确认直接部署
  --rebuild     强制重新构建镜像
  --quiet       静默模式（减少输出信息）
  --verbose     显示详细输出

示例:
  $0              # 交互式部署
  $0 --force      # 自动部署
  $0 --rebuild    # 强制重建镜像
  $0 --quiet      # 静默模式部署
  $0 --verbose    # 详细输出部署

EOF
    exit 0
fi

# 全局变量
FORCE_REBUILD=false
QUIET_MODE=false

# 处理参数
for arg in "$@"; do
    case $arg in
        --force)
            # 跳过确认
            confirm_deployment() { :; }
            ;;
        --rebuild)
            FORCE_REBUILD=true
            ;;
        --quiet)
            QUIET_MODE=true
            # 重定义日志函数为静默模式
            log_info() { :; }
            log_warn() { :; }
            ;;
        --verbose)
            set -x
            ;;
    esac
done

# 执行主函数
main "$@"