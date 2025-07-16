#!/bin/bash

# 从爬虫数据生成博客示例脚本
# 此脚本展示了如何在爬虫完成后使用generate_blog.py的爬虫数据生成模式生成博客

# 确保当前目录是项目根目录
cd "$(dirname "$0")/.." || exit

# 检查是否提供了任务目录参数
if [ $# -eq 0 ]; then
    echo "错误: 请提供爬虫任务目录路径"
    echo "用法: $0 <爬虫任务目录路径> [模板名称]"
    exit 1
fi

# 获取任务目录路径
TASK_DIR="$1"

# 检查任务目录是否存在
if [ ! -d "$TASK_DIR" ]; then
    echo "错误: 任务目录不存在: $TASK_DIR"
    exit 1
fi

# 获取可选的模板名称
TEMPLATE=""
if [ $# -ge 2 ]; then
    TEMPLATE="--template $2"
fi

# 示例1：列出可用的模板
echo "示例1：列出可用的模板"
echo "==================================================="
python generate_blog.py --list-templates

# 示例2：使用默认模板生成博客
echo "\n\n示例2：使用默认模板生成博客"
echo "==================================================="
python generate_blog.py --task-dir "$TASK_DIR" $TEMPLATE

# 示例3：使用指定输出路径生成博客
echo "\n\n示例3：使用指定输出路径生成博客"
echo "==================================================="
OUTPUT_PATH="examples/output/blog_from_crawler.md"
python generate_blog.py --task-dir "$TASK_DIR" $TEMPLATE --output "$OUTPUT_PATH"

echo "\n博客生成完成，请查看输出目录"