#!/bin/bash

# 简化的环境设置脚本
# 使用uv sync一步完成虚拟环境创建和依赖安装

echo "=== 开始设置爬虫项目环境 ==="

# 检查uv是否已安装
if ! command -v uv &> /dev/null; then
    echo "uv未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 检查安装结果
    if ! command -v uv &> /dev/null; then
        echo "uv安装失败，请手动安装: https://github.com/astral-sh/uv"
        exit 1
    fi
    echo "uv安装成功！"
else
    echo "uv已安装: $(uv --version)"
fi

# 一步创建虚拟环境并安装所有依赖
echo "\n创建虚拟环境并安装依赖..."
uv sync

# 显示激活命令
echo "\n环境设置完成！使用以下命令激活虚拟环境："
echo "source .venv/bin/activate"

echo "\n=== 环境设置完成! ==="