#!/bin/bash

# 环境设置和测试运行脚本
# 该脚本合并了setup.sh和run_tests.sh的功能
# 可以一步完成环境设置、激活虚拟环境和运行测试
#
# 重要：此脚本必须使用source命令运行才能正确激活虚拟环境
# 正确用法: source ./setup_and_run.sh 或 . ./setup_and_run.sh

# 显示帮助信息的函数
show_help() {
    echo "用法: source ./setup_and_run.sh [选项]  或  . ./setup_and_run.sh [选项]"
    echo ""
    echo "注意: 必须使用source命令运行此脚本，才能正确激活虚拟环境"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --test, -t     运行测试"
    echo "                 可选参数: 测试文件路径"
    echo "                 不提供参数则运行所有测试"
    echo ""
    echo "示例:"
    echo "  source ./setup_and_run.sh             # 设置环境并激活虚拟环境"
    echo "  source ./setup_and_run.sh --test      # 设置环境并运行所有测试"
    echo "  source ./setup_and_run.sh -t tests/your_test_file.py  # 运行特定测试"
    echo ""
    echo "错误用法(虚拟环境不会生效):"
    echo "  ./setup_and_run.sh  # 不要这样运行！"
    return 0
}

echo "=== 开始设置爬虫项目环境 ==="

# 检查uv是否已安装
if ! command -v uv &> /dev/null; then
    echo "uv未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 检查安装结果
    if ! command -v uv &> /dev/null; then
        echo "uv安装失败，请手动安装: https://github.com/astral-sh/uv"
        echo "脚本终止"
        return 1
    fi
    echo "uv安装成功！"
else
    echo "uv已安装: $(uv --version)"
fi

# 一步创建虚拟环境并安装所有依赖
echo "\n创建虚拟环境并安装依赖..."
uv sync

# 检查.env文件是否存在，如果不存在则提示创建
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "\n提示：未找到.env文件，但发现.env.example文件"
    echo "建议复制.env.example为.env并填入您的敏感信息："
    echo "cp .env.example .env"
    echo "然后编辑.env文件填入您的实际值"
fi

echo "\n=== 环境设置完成! ==="

# 激活虚拟环境
echo "\n正在激活虚拟环境..."
source .venv/bin/activate

# 验证Python环境
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python -V)

echo "使用的Python解释器: $PYTHON_PATH"
echo "Python版本: $PYTHON_VERSION"

# 检查是否使用了虚拟环境的Python
if [[ $PYTHON_PATH != *".venv/bin/python"* ]]; then
    echo "警告：未使用虚拟环境的Python解释器！"
    echo "当前使用: $PYTHON_PATH"
    echo "应该使用: $(pwd)/.venv/bin/python"
    echo "请确保正确激活了虚拟环境"
    echo "脚本终止"
    return 1
fi

# 处理命令行参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
fi

# 询问是否运行测试
if [ "$1" = "--test" ] || [ "$1" = "-t" ]; then
    # 运行测试
    echo "\n开始运行测试..."
    
    # 如果提供了特定测试文件，则运行该文件，否则运行所有测试
    if [ -n "$2" ]; then
        echo "运行测试: $2"
        python "$2"
    else
        echo "运行所有测试"
        python -m unittest discover tests
        
        # 提示：已删除测试文件
        echo "\n注意：以下测试文件已移除，因为examples目录中已有完整示例："
        echo "1. GitHub上传测试文件"
        echo "   如需测试GitHub上传功能，请参考 examples/github_image_example.py 和 examples/github_image_example.sh"
        echo "2. 博客生成测试文件"
        echo "   如需测试博客生成功能，请参考 examples/generate_blog_example.sh"
    fi
    
    echo "\n测试完成"
else
    echo "\n环境已准备就绪！您现在可以："
    echo "1. 运行测试: ./setup_and_run.sh --test [可选的测试文件路径]"
    echo "2. 运行爬虫: python crawler.py [参数]"
    echo "3. 生成博客: python generate_blog.py [参数]"
    echo "4. 运行示例: 查看examples目录中的示例脚本"
fi

# 关于虚拟环境激活的重要说明
echo "\n重要提示：虚拟环境激活只在当前shell会话中有效"
echo "如果您是通过 ./setup_and_run.sh 方式运行此脚本，虚拟环境可能不会在您的终端中生效"
echo "请使用以下方式运行此脚本以确保虚拟环境正确激活："
echo "  source ./setup_and_run.sh 或 . ./setup_and_run.sh"
echo ""
echo "当前虚拟环境状态："
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "  已激活: $VIRTUAL_ENV"
else
    echo "  未激活，请使用上述命令重新运行脚本"
fi
echo ""
echo "退出终端或运行 'deactivate' 命令可以退出虚拟环境"