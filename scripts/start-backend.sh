#!/bin/bash

# 后端服务启动脚本
# 提供后端服务的一键启动功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

log_info "项目根目录: $PROJECT_ROOT"
log_info "后端目录: $BACKEND_DIR"

# 检查后端目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    log_error "后端目录不存在: $BACKEND_DIR"
    exit 1
fi

# 切换到后端目录
cd "$BACKEND_DIR"
log_info "切换到后端目录: $(pwd)"

# 检查Python环境
log_info "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装，请先安装Python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
log_success "Python版本: $PYTHON_VERSION"

# 检查虚拟环境
log_info "检查虚拟环境..."
if [ ! -d "../.venv" ]; then
    log_warning "虚拟环境不存在，正在创建..."
    cd "$PROJECT_ROOT"
    python3 -m venv .venv
    log_success "虚拟环境创建完成"
    cd "$BACKEND_DIR"
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source "$PROJECT_ROOT/.venv/bin/activate"
log_success "虚拟环境已激活"

# 检查并安装依赖
log_info "检查项目依赖..."
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    log_info "使用uv安装依赖..."
    if command -v uv &> /dev/null; then
        cd "$PROJECT_ROOT"
        uv sync
        cd "$BACKEND_DIR"
        log_success "依赖安装完成"
    else
        log_warning "uv未安装，使用pip安装依赖..."
        pip install -e "$PROJECT_ROOT"
        log_success "依赖安装完成"
    fi
else
    log_error "未找到pyproject.toml文件"
    exit 1
fi

# 检查.env文件
log_info "检查环境配置文件..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        log_warning ".env文件不存在，正在从.env.example创建..."
        cp .env.example .env
        log_success ".env文件创建完成"
        log_warning "请根据实际情况修改.env文件中的配置"
    else
        log_error ".env.example文件不存在，无法创建.env文件"
        exit 1
    fi
else
    log_success ".env文件已存在"
fi

# 检查端口占用
log_info "检查端口占用情况..."
PORT=$(grep -E '^PORT=' .env | cut -d'=' -f2 | tr -d ' ' || echo "5001")
if lsof -i :$PORT &> /dev/null; then
    log_warning "端口 $PORT 已被占用"
    log_info "占用端口的进程:"
    lsof -i :$PORT
    read -p "是否继续启动？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "启动已取消"
        exit 0
    fi
else
    log_success "端口 $PORT 可用"
fi

# 数据库初始化检查
log_info "检查数据库连接..."
if python -c "from app import create_app; app = create_app(); print('数据库连接正常')" 2>/dev/null; then
    log_success "数据库连接正常"
else
    log_warning "数据库连接失败，请检查数据库配置"
    log_info "尝试初始化数据库..."
    if python run.py init-db 2>/dev/null; then
        log_success "数据库初始化完成"
    else
        log_warning "数据库初始化失败，请手动检查数据库配置"
    fi
fi

# 创建管理员用户（如果不存在）
log_info "检查管理员用户..."
if python run.py create-admin 2>/dev/null; then
    log_success "管理员用户检查/创建完成"
else
    log_info "管理员用户可能已存在或创建失败"
fi

# 启动后端服务
log_info "启动后端服务..."
log_info "服务将运行在: http://localhost:$PORT"
log_info "按 Ctrl+C 停止服务"
echo

# 启动服务
python run.py run