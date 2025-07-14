#!/bin/bash

# 这个脚本展示了如何使用generate_blog.py脚本生成博客

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

# 列出可用的模板
echo "列出可用的模板:"
python generate_blog.py --list-templates

echo "\n使用默认模板生成博客:"
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --output examples/output/default_blog.md

echo "\n使用简单模板生成博客:"
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --template simple_template \
    --output examples/output/simple_blog.md

echo "\n使用详细模板生成博客:"
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --template detailed_template \
    --output examples/output/detailed_blog.md

echo "\n所有博客已生成到 examples/output/ 目录"