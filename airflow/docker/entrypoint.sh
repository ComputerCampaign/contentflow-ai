#!/bin/bash
set -e

# 颜色输出函数
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# 日志函数
log_info() { green "[INFO] $1"; }
log_warn() { yellow "[WARN] $1"; }
log_error() { red "[ERROR] $1"; }

# 等待数据库连接
wait_for_db() {
    log_info "等待数据库连接..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if airflow db check > /dev/null 2>&1; then
            log_info "数据库连接成功"
            return 0
        fi
        
        log_warn "数据库连接失败，重试 $attempt/$max_attempts"
        sleep 2
        ((attempt++))
    done
    
    log_error "数据库连接超时"
    exit 1
}

# 初始化数据库
init_db() {
    log_info "初始化Airflow数据库..."
    airflow db init
    
    if [ $? -eq 0 ]; then
        log_info "数据库初始化成功"
    else
        log_error "数据库初始化失败"
        exit 1
    fi
}

# 升级数据库
upgrade_db() {
    log_info "升级Airflow数据库..."
    airflow db upgrade
    
    if [ $? -eq 0 ]; then
        log_info "数据库升级成功"
    else
        log_error "数据库升级失败"
        exit 1
    fi
}

# 创建管理员用户
create_admin_user() {
    local username="${AIRFLOW_ADMIN_USERNAME:-admin}"
    local password="${AIRFLOW_ADMIN_PASSWORD:-admin123}"
    local firstname="${AIRFLOW_ADMIN_FIRSTNAME:-Admin}"
    local lastname="${AIRFLOW_ADMIN_LASTNAME:-User}"
    local email="${AIRFLOW_ADMIN_EMAIL:-admin@example.com}"
    
    log_info "创建管理员用户: $username"
    
    # 检查用户是否已存在
    if airflow users list | grep -q "$username"; then
        log_warn "用户 $username 已存在，跳过创建"
    else
        airflow users create \
            --username "$username" \
            --firstname "$firstname" \
            --lastname "$lastname" \
            --role Admin \
            --email "$email" \
            --password "$password"
        
        if [ $? -eq 0 ]; then
            log_info "管理员用户创建成功"
        else
            log_error "管理员用户创建失败"
            exit 1
        fi
    fi
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    
    # 确保日志目录存在并有正确权限
    mkdir -p /opt/airflow/logs
    chmod 755 /opt/airflow/logs
    
    # 确保DAGs目录存在并有正确权限
    mkdir -p /opt/airflow/dags
    chmod 755 /opt/airflow/dags
    
    # 确保插件目录存在并有正确权限
    mkdir -p /opt/airflow/plugins
    chmod 755 /opt/airflow/plugins
    
    log_info "权限设置完成"
}

# 验证配置
validate_config() {
    log_info "验证Airflow配置..."
    
    # 检查必要的环境变量
    local required_vars=("AIRFLOW_DB_HOST" "AIRFLOW_DB_USER" "AIRFLOW_DB_PASSWORD" "AIRFLOW_DB_NAME")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "缺少必要的环境变量: $var"
            exit 1
        fi
    done
    
    # 验证配置文件
    log_info "执行 airflow config list 命令..."
    if ! airflow config list 2>&1; then
        log_error "Airflow配置验证失败，详细错误信息见上方"
        exit 1
    fi
    
    log_info "配置验证通过"
}

# 主函数
main() {
    log_info "启动Airflow容器..."
    
    # 设置权限
    set_permissions
    
    # 验证配置
    validate_config
    
    # 等待数据库
    wait_for_db
    
    # 根据服务类型执行不同的初始化
    case "${AIRFLOW_SERVICE_TYPE:-webserver}" in
        "webserver")
            log_info "启动Webserver服务"
            
            # 初始化或升级数据库
            if [ "${AIRFLOW_INIT_DB:-true}" = "true" ]; then
                init_db
            else
                upgrade_db
            fi
            
            # 创建管理员用户
            if [ "${AIRFLOW_CREATE_ADMIN:-true}" = "true" ]; then
                create_admin_user
            fi
            
            # 启动webserver
            exec airflow webserver
            ;;
        "scheduler")
            log_info "启动Scheduler服务"
            
            # 等待webserver初始化完成
            sleep 10
            
            # 启动scheduler
            exec airflow scheduler
            ;;
        "worker")
            log_info "启动Worker服务"
            
            # 等待scheduler启动
            sleep 15
            
            # 启动worker
            exec airflow celery worker
            ;;
        "flower")
            log_info "启动Flower服务"
            
            # 启动flower
            exec airflow celery flower
            ;;
        *)
            log_error "未知的服务类型: ${AIRFLOW_SERVICE_TYPE}"
            exit 1
            ;;
    esac
}

# 信号处理
trap 'log_info "收到停止信号，正在关闭..."; exit 0' SIGTERM SIGINT

# 执行主函数
main "$@"