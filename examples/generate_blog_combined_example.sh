#!/bin/bash

# 博客生成综合示例脚本
# 此脚本展示了generate_blog.py的两种生成模式的使用方法

# 确保当前目录是项目根目录
cd "$(dirname "$0")/.." || exit

# 创建示例图片目录
mkdir -p examples/images

# 如果没有示例图片，创建一些示例图片（这里只是创建空文件作为示例）
if [ ! -f examples/images/image1.jpg ]; then
    echo "创建示例图片..."
    touch examples/images/image1.jpg
    touch examples/images/image2.jpg
    touch examples/images/image3.jpg
fi

# 创建输出目录
mkdir -p examples/output

# 列出可用的模板
echo "列出可用的模板"
echo "==================================================="
python generate_blog.py --list-templates

echo "\n\n"
echo "模式1：从自定义数据生成博客"
echo "==================================================="

# 使用自定义数据生成博客
echo "从自定义数据生成博客"
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg \
    --metadata examples/metadata_example.json \
    --template simple_template \
    --output examples/output/custom_data_blog.md

echo "\n\n"
echo "模式2：从爬虫数据生成博客"
echo "==================================================="

# 检查是否提供了任务目录参数
if [ $# -eq 0 ]; then
    echo "注意: 未提供爬虫任务目录路径，无法展示从爬虫数据生成博客的示例"
    echo "用法: $0 <爬虫任务目录路径>"
    echo "\n所有博客已生成到 examples/output/ 目录"
    exit 0
fi

# 获取任务目录路径
TASK_DIR="$1"

# 检查任务目录是否存在
if [ ! -d "$TASK_DIR" ]; then
    echo "错误: 任务目录不存在: $TASK_DIR"
    echo "\n所有博客已生成到 examples/output/ 目录"
    exit 1
fi

# 从爬虫数据生成博客
echo "从爬虫数据生成博客"
python generate_blog.py \
    --task-dir "$TASK_DIR" \
    --template simple_template \
    --output examples/output/crawler_data_blog.md

echo "\n所有博客已生成到 examples/output/ 目录"