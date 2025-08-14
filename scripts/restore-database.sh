#!/bin/bash

# 数据库恢复脚本
# 使用方法: ./restore-database.sh <backup_file>

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/data/backups"

# 默认数据库配置
MYSQL_HOST="localhost"
MYSQL_PORT="8306"
MYSQL_USER="crawler_usage"
MYSQL_DATABASE="crawler_platform"
MYSQL_PASSWORD=""

# 加载环境变量
if [[ -f "$PROJECT_ROOT/backend/.env" ]]; then
    while IFS='=' read -r key value; do
        # 跳过注释和空行
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z $key ]] && continue
        # 移除引号并导出变量
        value=$(echo "$value" | sed 's/^["'\'']//' | sed 's/["'\'']*$//')
        export "$key"="$value"
    done < <(grep -E '^[A-Z_]+=.*' "$PROJECT_ROOT/backend/.env")
fi

# 检查必要工具
if ! command -v mysql &> /dev/null; then
    log_error "mysql 命令未找到，请安装MySQL客户端"
    exit 1
fi

if ! command -v expect &> /dev/null; then
    log_error "expect 命令未找到，请安装expect工具"
    log_info "macOS安装: brew install expect"
    exit 1
fi

# 测试数据库连接
test_connection() {
    log_info "测试数据库连接..."
    
    expect -c "
        spawn mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p -e 'SELECT 1;'
        expect \"Enter password:\"
        send \"$MYSQL_PASSWORD\\r\"
        expect eof
    " > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_info "数据库连接成功"
    else
        log_error "数据库连接失败，请检查配置"
        exit 1
    fi
}

# 检查数据库是否存在
check_database_exists() {
    log_info "检查数据库是否存在: $MYSQL_DATABASE"
    
    local result
    result=$(expect -c "
        spawn mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p -e \"SHOW DATABASES LIKE '$MYSQL_DATABASE';\"
        expect \"Enter password:\"
        send \"$MYSQL_PASSWORD\\r\"
        expect eof
    " 2>/dev/null | grep -c "$MYSQL_DATABASE" || echo "0")
    
    if [[ "$result" -gt 0 ]]; then
        log_info "数据库 $MYSQL_DATABASE 已存在"
        return 0
    else
        log_info "数据库 $MYSQL_DATABASE 不存在"
        return 1
    fi
}

# 创建数据库
create_database() {
    log_info "创建数据库: $MYSQL_DATABASE"
    
    expect -c "
        spawn mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p -e \"CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"
        expect \"Enter password:\"
        send \"$MYSQL_PASSWORD\\r\"
        expect eof
    " > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_info "数据库创建成功"
    else
        log_error "数据库创建失败"
        exit 1
    fi
}

# 执行恢复
perform_restore() {
    local backup_file="$1"
    
    log_info "开始恢复数据库: $MYSQL_DATABASE"
    log_info "备份文件: $backup_file"
    
    # 检查备份文件
    if [[ ! -f "$backup_file" ]]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    # 处理压缩文件
    local restore_cmd
    if [[ "$backup_file" == *.gz ]]; then
        restore_cmd="zcat '$backup_file' | expect -c '
            spawn mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p $MYSQL_DATABASE
            expect \"Enter password:\"
            send \"$MYSQL_PASSWORD\\r\"
            interact
        '"
    else
        restore_cmd="expect -c '
            spawn mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p $MYSQL_DATABASE
            expect \"Enter password:\"
            send \"$MYSQL_PASSWORD\\r\"
            interact
        ' < '$backup_file'"
    fi
    
    # 执行恢复
    if eval "$restore_cmd" > /dev/null 2>&1; then
        log_info "数据库恢复成功"
    else
        log_error "数据库恢复失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "数据库恢复脚本"
    echo ""
    echo "用法: $0 <backup_file>"
    echo ""
    echo "参数:"
    echo "  backup_file    备份文件路径（支持.sql和.sql.gz格式）"
    echo ""
    echo "示例:"
    echo "  $0 backup_20240101_120000.sql.gz"
    echo "  $0 /path/to/backup.sql"
}

# 主函数
main() {
    if [[ $# -eq 0 ]]; then
        log_error "请指定备份文件"
        show_help
        exit 1
    fi
    
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    local backup_file="$1"
    
    # 如果是相对路径，尝试在备份目录中查找
    if [[ ! -f "$backup_file" && ! "$backup_file" =~ ^/ ]]; then
        local full_path="$BACKUP_DIR/$backup_file"
        if [[ -f "$full_path" ]]; then
            backup_file="$full_path"
        fi
    fi
    
    log_info "开始数据库恢复"
    test_connection
    
    if ! check_database_exists; then
        create_database
    fi
    
    perform_restore "$backup_file"
    log_info "恢复完成"
}

main "$@"