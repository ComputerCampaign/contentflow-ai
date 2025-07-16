#!/bin/bash

# 博客生成示例脚本
# 此脚本展示了generate_blog.py的自定义数据生成模式的各种使用方式和功能

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

# 示例1：列出可用的模板
echo "示例1：列出可用的模板"
echo "==================================================="
python generate_blog.py --list-templates

# 示例2：使用默认模板生成博客
echo "\n\n示例2：使用默认模板生成博客"
echo "==================================================="
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --output examples/output/default_blog.md

# 示例3：使用简单模板生成博客
echo "\n\n示例3：使用简单模板生成博客"
echo "==================================================="
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --template simple_template \
    --output examples/output/simple_blog.md

# 示例4：使用详细模板生成博客
echo "\n\n示例4：使用详细模板生成博客"
echo "==================================================="
python generate_blog.py \
    --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
    --metadata examples/metadata_example.json \
    --template detailed_template \
    --output examples/output/detailed_blog.md

# 示例5：不指定图片，仅使用元数据生成博客
echo "\n\n示例5：不指定图片，仅使用元数据生成博客"
echo "==================================================="
python generate_blog.py \
    --metadata examples/metadata_example.json \
    --output examples/output/no_images_blog.md

# 示例6：不指定输出路径，使用默认输出目录
echo "\n\n示例6：不指定输出路径，使用默认输出目录"
echo "==================================================="
python generate_blog.py \
    --images examples/images/image1.jpg \
    --metadata examples/metadata_example.json \
    --template simple_template

echo "\n所有博客已生成到 examples/output/ 目录"