#!/bin/bash

# GitHub图床示例脚本
# 此脚本展示如何使用GitHub图床功能上传图片并获取URL

# 确保示例图片存在
mkdir -p examples/images

# 创建示例图片（如果不存在）
if [ ! -f examples/images/image1.jpg ]; then
  echo "创建示例图片..."
  touch examples/images/image1.jpg
  touch examples/images/image2.jpg
  touch examples/images/image3.jpg
fi

# 设置GitHub仓库信息
REPO_OWNER="your-github-username"
REPO_NAME="your-image-repo"
BRANCH="main"

# 请在此处设置您的GitHub访问令牌
# 注意：不要在实际使用中将令牌硬编码在脚本中，这里仅作为示例
GITHUB_TOKEN="your-github-token"

echo "上传图片到GitHub仓库: ${REPO_OWNER}/${REPO_NAME}"

# 上传图片
python examples/github_image_example.py \
  --images examples/images/image1.jpg examples/images/image2.jpg examples/images/image3.jpg \
  --owner "${REPO_OWNER}" \
  --repo "${REPO_NAME}" \
  --branch "${BRANCH}" \
  --token "${GITHUB_TOKEN}"

echo "\n注意：请确保已设置正确的GitHub仓库信息和访问令牌"
echo "您可以在config/config.json文件中配置GitHub图床，或使用命令行参数"