#!/bin/bash

# 网页图片爬虫与博客生成器 - 统一启动脚本
# 合并了start.sh和setup_and_run.sh的功能
# 支持环境设置、前端构建、依赖安装和应用启动

# 显示帮助信息的函数
show_help() {
    echo "用法: ./run.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h        显示帮助信息"
    echo "  --setup, -s       仅进行环境设置，不启动应用"
    echo "  --test, -t        运行测试"
    echo "                    可选参数: 测试文件路径"
    echo "  --port PORT       指定应用运行端口 (默认: 8001)"
    echo "  --no-frontend     跳过前端构建"
    echo "  --dev             开发模式，启用调试"
    echo ""
    echo "示例:"
    echo "  ./run.sh                    # 完整设置并启动应用"
    echo "  ./run.sh --setup           # 仅设置环境"
    echo "  ./run.sh --test             # 运行所有测试"
    echo "  ./run.sh --port 9000        # 在端口9000启动应用"
    echo "  ./run.sh --no-frontend      # 跳过前端构建"
    echo "  ./run.sh --dev              # 开发模式启动"
    exit 0
}

# 解析命令行参数
SETUP_ONLY=false
RUN_TESTS=false
TEST_FILE=""
PORT=8001
SKIP_FRONTEND=false
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --setup|-s)
            SETUP_ONLY=true
            shift
            ;;
        --test|-t)
            RUN_TESTS=true
            if [[ $2 && $2 != --* ]]; then
                TEST_FILE="$2"
                shift
            fi
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            ;;
    esac
done

echo "=== 网页图片爬虫与博客生成器 - 统一启动脚本 ==="

# 检查是否在项目根目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查uv是否已安装
if ! command -v uv &> /dev/null; then
    echo "uv未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 重新加载shell配置
    source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null || true
    
    # 检查安装结果
    if ! command -v uv &> /dev/null; then
        echo "uv安装失败，请手动安装: https://github.com/astral-sh/uv"
        echo "或运行: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    echo "uv安装成功！"
else
    echo "uv已安装: $(uv --version)"
fi

# 创建虚拟环境并安装Python依赖
echo "\n正在创建虚拟环境并安装Python依赖..."
uv sync

if [ $? -ne 0 ]; then
    echo "错误: Python依赖安装失败"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "\n提示：未找到.env文件，但发现.env.example文件"
    echo "建议复制.env.example为.env并填入您的敏感信息："
    echo "cp .env.example .env"
    echo "然后编辑.env文件填入您的实际值"
fi

# 前端构建
if [ "$SKIP_FRONTEND" = false ]; then
    if [ ! -d "static" ]; then
        echo "\n警告: 未找到前端构建文件，正在构建前端..."
        
        # 检查Node.js和npm
        if ! command -v npm &> /dev/null; then
            echo "错误: 未找到npm，请先安装Node.js和npm"
            echo "或使用 --no-frontend 选项跳过前端构建"
            exit 1
        fi
        
        # 进入前端目录
        if [ -d "frontend" ]; then
            cd frontend
            
            # 安装依赖
            echo "正在安装前端依赖..."
            npm install
            
            if [ $? -ne 0 ]; then
                echo "错误: 前端依赖安装失败"
                cd ..
                exit 1
            fi
            
            # 构建前端
            echo "正在构建前端..."
            npm run build
            
            if [ $? -ne 0 ]; then
                echo "错误: 前端构建失败"
                cd ..
                exit 1
            fi
            
            # 返回项目根目录
            cd ..
            echo "前端构建完成！"
        else
            echo "警告: 未找到frontend目录，跳过前端构建"
        fi
    else
        echo "\n前端构建文件已存在，跳过构建"
    fi
else
    echo "\n跳过前端构建 (--no-frontend)"
fi

echo "\n=== 环境设置完成! ==="

# 如果只是设置环境，则退出
if [ "$SETUP_ONLY" = true ]; then
    echo "\n环境设置完成！您现在可以："
    echo "1. 启动应用: ./run.sh"
    echo "2. 运行测试: ./run.sh --test"
    echo "3. 查看帮助: ./run.sh --help"
    exit 0
fi

# 运行测试
if [ "$RUN_TESTS" = true ]; then
    echo "\n开始运行测试..."
    
    if [ -n "$TEST_FILE" ]; then
        echo "运行测试: $TEST_FILE"
        uv run python "$TEST_FILE"
    else
        echo "运行所有测试"
        uv run python -m unittest discover tests
    fi
    
    echo "\n测试完成"
    exit 0
fi

# 启动应用
echo "\n正在启动Flask应用..."
echo "应用将在 http://localhost:$PORT 上运行"
echo "按 Ctrl+C 停止应用"
echo ""

# 构建启动命令
START_CMD="uv run python app.py --port $PORT"

if [ "$DEV_MODE" = true ]; then
    echo "开发模式启动 (调试已启用)"
    START_CMD="$START_CMD --debug"
fi

# 启动应用
eval $START_CMD