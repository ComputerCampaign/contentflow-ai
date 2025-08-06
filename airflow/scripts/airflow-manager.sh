#!/bin/bash

# Airflow管理脚本
# 提供Airflow服务的启动、停止、重启、状态检查等功能

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/deploy/docker/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/deploy/envs/.env"
AIRFLOW_ENV_FILE="$PROJECT_ROOT/airflow/config/.env"

# 颜色输出函数
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# 日志函数
log_info() { green "[INFO] $1"; }
log_warn() { yellow "[WARN] $1"; }
log_error() { red "[ERROR] $1"; }
log_debug() { blue "[DEBUG] $1"; }

# 显示帮助信息
show_help() {
    cat << EOF
Airflow管理脚本

用法: $0 [命令] [选项]

命令:
  start           启动Airflow服务
  stop            停止Airflow服务
  restart         重启Airflow服务
  status          查看服务状态
  logs            查看服务日志
  build           构建Airflow镜像
  clean           清理资源
  init            初始化环境
  shell           进入Airflow容器
  db-init         初始化数据库
  db-upgrade      升级数据库
  create-user     创建用户
  list-dags       列出所有DAG
  test-dag        测试DAG
  backup          备份数据
  restore         恢复数据

选项:
  -h, --help      显示帮助信息
  -v, --verbose   详细输出
  -f, --force     强制执行
  -d, --detach    后台运行
  --no-cache      构建时不使用缓存

示例:
  $0 start                    # 启动所有服务
  $0 logs airflow_webserver   # 查看webserver日志
  $0 shell webserver          # 进入webserver容器
  $0 create-user admin        # 创建管理员用户
  $0 test-dag example_dag     # 测试指定DAG

EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装或不在PATH中"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装或不在PATH中"
        exit 1
    fi
    
    # 检查配置文件
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Docker Compose文件不存在: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 初始化环境
init_environment() {
    log_info "初始化Airflow环境..."
    
    # 创建必要的目录
    mkdir -p "$PROJECT_ROOT/airflow/logs"
    mkdir -p "$PROJECT_ROOT/airflow/plugins"
    mkdir -p "$PROJECT_ROOT/data/airflow"
    
    # 设置权限
    if [ "$(uname)" = "Linux" ]; then
        sudo chown -R 50000:0 "$PROJECT_ROOT/airflow/logs"
        sudo chown -R 50000:0 "$PROJECT_ROOT/airflow/plugins"
    fi
    
    # 复制环境变量文件
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_FILE.example" ]; then
            cp "$ENV_FILE.example" "$ENV_FILE"
            log_info "已创建环境变量文件: $ENV_FILE"
        else
            log_error "环境变量示例文件不存在: $ENV_FILE.example"
            exit 1
        fi
    fi
    
    # 复制Airflow环境变量文件
    if [ ! -f "$AIRFLOW_ENV_FILE" ]; then
        if [ -f "$AIRFLOW_ENV_FILE.example" ]; then
            cp "$AIRFLOW_ENV_FILE.example" "$AIRFLOW_ENV_FILE"
            log_info "已创建Airflow环境变量文件: $AIRFLOW_ENV_FILE"
        fi
    fi
    
    log_info "环境初始化完成"
}

# 构建镜像
build_images() {
    local no_cache="$1"
    
    log_info "构建Airflow镜像..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$no_cache" = "true" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --platform linux/amd64 --no-cache airflow_webserver
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --platform linux/amd64 airflow_webserver
    fi
    
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    local detach="$1"
    
    log_info "启动Airflow服务..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$detach" = "true" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" up
    fi
    
    if [ "$detach" = "true" ]; then
        log_info "服务已在后台启动"
        show_status
    fi
}

# 停止服务
stop_services() {
    log_info "停止Airflow服务..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    log_info "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启Airflow服务..."
    
    stop_services
    sleep 2
    start_services "true"
}

# 查看状态
show_status() {
    log_info "服务状态:"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    log_info "服务健康状态:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    log_info "访问地址:"
    echo "  Airflow Web UI: http://localhost:8080"
    echo "  MySQL: localhost:8306"
}

# 查看日志
show_logs() {
    local service="$1"
    local follow="$2"
    
    cd "$PROJECT_ROOT"
    
    if [ -z "$service" ]; then
        if [ "$follow" = "true" ]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        else
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs
        fi
    else
        if [ "$follow" = "true" ]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f "$service"
        else
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs "$service"
        fi
    fi
}

# 进入容器
enter_shell() {
    local service="${1:-airflow_webserver}"
    
    log_info "进入 $service 容器..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec "$service" bash
}

# 清理资源
clean_resources() {
    local force="$1"
    
    if [ "$force" != "true" ]; then
        read -p "确定要清理所有资源吗？这将删除容器、镜像和数据 (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "取消清理操作"
            return
        fi
    fi
    
    log_info "清理Airflow资源..."
    
    cd "$PROJECT_ROOT"
    
    # 停止并删除容器
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
    
    # 删除镜像
    docker images | grep airflow | awk '{print $3}' | xargs -r docker rmi -f
    
    # 清理未使用的资源
    docker system prune -f
    
    log_info "资源清理完成"
}

# 数据库操作
db_init() {
    log_info "初始化Airflow数据库..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec airflow_webserver airflow db init
    
    log_info "数据库初始化完成"
}

db_upgrade() {
    log_info "升级Airflow数据库..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec airflow_webserver airflow db upgrade
    
    log_info "数据库升级完成"
}

# 用户管理
create_user() {
    local username="$1"
    
    if [ -z "$username" ]; then
        read -p "请输入用户名: " username
    fi
    
    if [ -z "$username" ]; then
        log_error "用户名不能为空"
        exit 1
    fi
    
    log_info "创建用户: $username"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec airflow_webserver airflow users create \
        --username "$username" \
        --firstname "User" \
        --lastname "Name" \
        --role Admin \
        --email "$username@example.com"
}

# DAG管理
list_dags() {
    log_info "DAG列表:"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec airflow_webserver airflow dags list
}

test_dag() {
    local dag_id="$1"
    
    if [ -z "$dag_id" ]; then
        log_error "请指定DAG ID"
        exit 1
    fi
    
    log_info "测试DAG: $dag_id"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec airflow_webserver airflow dags test "$dag_id"
}

# 主函数
main() {
    local command="$1"
    shift
    
    # 解析选项
    local verbose=false
    local force=false
    local detach=false
    local no_cache=false
    local follow=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -d|--detach)
                detach=true
                shift
                ;;
            --no-cache)
                no_cache=true
                shift
                ;;
            --follow)
                follow=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    # 设置详细输出
    if [ "$verbose" = "true" ]; then
        set -x
    fi
    
    # 检查依赖
    check_dependencies
    
    # 执行命令
    case "$command" in
        start)
            init_environment
            start_services "$detach"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$1" "$follow"
            ;;
        build)
            build_images "$no_cache"
            ;;
        clean)
            clean_resources "$force"
            ;;
        init)
            init_environment
            ;;
        shell)
            enter_shell "$1"
            ;;
        db-init)
            db_init
            ;;
        db-upgrade)
            db_upgrade
            ;;
        create-user)
            create_user "$1"
            ;;
        list-dags)
            list_dags
            ;;
        test-dag)
            test_dag "$1"
            ;;
        backup)
            log_warn "备份功能待实现"
            ;;
        restore)
            log_warn "恢复功能待实现"
            ;;
        "")
            log_error "请指定命令"
            show_help
            exit 1
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"