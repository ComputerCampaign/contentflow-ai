#!/bin/bash

# 网页图片爬虫与博客生成器 - 启动脚本

echo "=== 网页图片爬虫与博客生成器 ==="
echo "正在启动应用..."

# 检查是否在项目根目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python"
    exit 1
fi

# 检查前端构建文件
if [ ! -d "static" ]; then
    echo "警告: 未找到前端构建文件，正在构建前端..."
    
    # 检查Node.js和npm
    if ! command -v npm &> /dev/null; then
        echo "错误: 未找到npm，请先安装Node.js和npm"
        exit 1
    fi
    
    # 进入前端目录
    cd frontend
    
    # 安装依赖
    echo "正在安装前端依赖..."
    npm install
    
    # 构建前端
    echo "正在构建前端..."
    npm run build
    
    # 返回项目根目录
    cd ..
fi

# 检查uv
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到uv，请先安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 安装Python依赖
echo "正在安装Python依赖..."
uv sync

# 启动应用
echo "正在启动Flask应用..."
echo "应用将在 http://localhost:8000 上运行"
echo "按 Ctrl+C 停止应用"
echo ""

uv run python app.py