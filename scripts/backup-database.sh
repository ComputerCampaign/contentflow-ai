#!/bin/bash

# 数据库备份脚本
# 使用方法: ./backup-database.sh

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

if ! command -v mysqldump &> /dev/null; then
    log_error "mysqldump 命令未找到，请安装MySQL客户端"
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

# 执行备份
perform_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/backup_$timestamp.sql"
    
    log_info "开始备份数据库: $MYSQL_DATABASE"
    log_info "备份文件: $backup_file"
    
    mkdir -p "$BACKUP_DIR"
    
    expect -c "
        spawn mysqldump -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p --single-transaction $MYSQL_DATABASE
        expect \"Enter password:\"
        send \"$MYSQL_PASSWORD\\r\"
        expect eof
    " > "$backup_file"
    
    if [[ $? -eq 0 && -s "$backup_file" ]]; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        log_info "备份完成！文件大小: $file_size"
        
        # 压缩备份文件
        if gzip "$backup_file"; then
            log_info "备份文件已压缩: ${backup_file}.gz"
        fi
    else
        log_error "备份失败"
        rm -f "$backup_file"
        exit 1
    fi
}

# 主函数
main() {
    log_info "开始数据库备份"
    test_connection
    perform_backup
    log_info "备份完成"
}

main "$@"