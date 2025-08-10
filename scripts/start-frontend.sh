#!/bin/bash

# 前端服务启动脚本
# 提供前端服务的一键启动功能

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
FRONTEND_DIR="$PROJECT_ROOT/frontend"

log_info "项目根目录: $PROJECT_ROOT"
log_info "前端目录: $FRONTEND_DIR"

# 检查前端目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    log_error "前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# 切换到前端目录
cd "$FRONTEND_DIR"
log_info "切换到前端目录: $(pwd)"

# 检查Node.js环境
log_info "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    log_error "Node.js 未安装，请先安装Node.js"
    log_info "推荐使用Node.js 16+版本"
    exit 1
fi

NODE_VERSION=$(node --version)
log_success "Node.js版本: $NODE_VERSION"

# 检查npm
if ! command -v npm &> /dev/null; then
    log_error "npm 未安装，请先安装npm"
    exit 1
fi

NPM_VERSION=$(npm --version)
log_success "npm版本: $NPM_VERSION"

# 检查package.json文件
log_info "检查项目配置..."
if [ ! -f "package.json" ]; then
    log_error "package.json文件不存在"
    exit 1
fi
log_success "package.json文件存在"

# 检查环境配置文件
log_info "检查环境配置文件..."
if [ ! -f ".env.development" ]; then
    log_warning ".env.development文件不存在，创建默认配置..."
    cat > .env.development << EOF
# 开发环境配置
VITE_API_BASE_URL=http://localhost:5001/api/v1
VITE_APP_TITLE=智能爬虫内容管理系统
VITE_APP_VERSION=1.0.0
VITE_NODE_ENV=development
EOF
    log_success ".env.development文件创建完成"
else
    log_success ".env.development文件已存在"
fi

# 检查API地址配置
log_info "检查API配置..."
API_URL=$(grep -E '^VITE_API_BASE_URL=' .env.development | cut -d'=' -f2 | tr -d ' ' || echo "")
if [ -z "$API_URL" ]; then
    log_warning "API地址未配置，使用默认地址"
    echo "VITE_API_BASE_URL=http://localhost:5001/api/v1" >> .env.development
else
    log_success "API地址: $API_URL"
fi

# 检查端口占用
log_info "检查端口占用情况..."
FRONTEND_PORT=3000
if lsof -i :$FRONTEND_PORT &> /dev/null; then
    log_warning "端口 $FRONTEND_PORT 已被占用"
    log_info "占用端口的进程:"
    lsof -i :$FRONTEND_PORT
    read -p "是否继续启动？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "启动已取消"
        exit 0
    fi
else
    log_success "端口 $FRONTEND_PORT 可用"
fi

# 检查node_modules目录
log_info "检查依赖安装状态..."
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
    log_warning "依赖未安装或不完整，正在安装依赖..."
    
    # 清理可能存在的问题文件
    if [ -d "node_modules" ]; then
        log_info "清理现有node_modules目录..."
        rm -rf node_modules
    fi
    
    if [ -f "package-lock.json" ]; then
        log_info "清理现有package-lock.json文件..."
        rm -f package-lock.json
    fi
    
    # 使用临时缓存目录避免权限问题
    log_info "安装项目依赖..."
    if npm install --cache /tmp/.npm; then
        log_success "依赖安装完成"
    else
        log_error "依赖安装失败"
        log_info "尝试使用其他方法安装..."
        if npm install --no-optional --legacy-peer-deps --cache /tmp/.npm; then
            log_success "依赖安装完成（使用兼容模式）"
        else
            log_error "依赖安装失败，请手动解决"
            exit 1
        fi
    fi
else
    log_success "依赖已安装"
fi

# 检查关键依赖
log_info "检查关键依赖..."
if [ ! -d "node_modules/vite" ]; then
    log_error "Vite未安装，请检查依赖安装"
    exit 1
fi
log_success "关键依赖检查通过"

# 检查后端服务状态
log_info "检查后端服务状态..."
BACKEND_URL=$(echo "$API_URL" | sed 's|/api/v1||')
if curl -s "$BACKEND_URL" > /dev/null 2>&1; then
    log_success "后端服务运行正常: $BACKEND_URL"
else
    log_warning "后端服务未运行或无法访问: $BACKEND_URL"
    log_info "请确保后端服务已启动"
fi

# 启动前端服务
log_info "启动前端开发服务器..."
log_info "服务将运行在: http://localhost:$FRONTEND_PORT"
log_info "按 Ctrl+C 停止服务"
echo

# 启动服务
npm run dev