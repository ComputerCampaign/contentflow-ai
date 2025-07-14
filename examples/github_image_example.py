#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub图床示例脚本

此脚本展示如何使用GitHub图床功能上传图片并获取URL
"""

import os
import sys
import logging
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入GitHub图床上传器
from utils.github_image_uploader import GitHubImageUploader
from config import config

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_github_config(args):
    """根据命令行参数设置GitHub配置
    
    Args:
        args: 命令行参数
    """
    # 获取当前配置
    github_config = config.get('blog', 'image_storage', {}).get('github', {})
    
    # 更新配置
    github_config['enabled'] = True
    
    if args.owner:
        github_config['repo_owner'] = args.owner
    
    if args.repo:
        github_config['repo_name'] = args.repo
    
    if args.branch:
        github_config['branch'] = args.branch
    
    if args.token:
        github_config['token'] = args.token
    
    if args.path:
        github_config['image_path'] = args.path
    
    if args.base_url:
        github_config['base_url'] = args.base_url
    
    # 更新配置
    config.set('blog', 'image_storage', 'github', github_config)
    config.set('blog', 'image_storage', 'type', 'github')
    
    # 打印配置信息（不包含token）
    logger.info("GitHub图床配置:")
    logger.info(f"  仓库: {github_config['repo_owner']}/{github_config['repo_name']}")
    logger.info(f"  分支: {github_config['branch']}")
    logger.info(f"  图片路径: {github_config['image_path']}")
    if github_config['base_url']:
        logger.info(f"  基础URL: {github_config['base_url']}")
    else:
        logger.info(f"  基础URL: 自动生成")

def upload_images(args):
    """上传图片到GitHub仓库
    
    Args:
        args: 命令行参数
    """
    # 设置GitHub配置
    setup_github_config(args)
    
    # 初始化GitHub图床上传器
    uploader = GitHubImageUploader()
    
    # 检查配置
    if not uploader.is_configured():
        logger.error("GitHub图床未正确配置，请检查参数")
        return
    
    # 上传图片
    success_count = 0
    fail_count = 0
    
    for image_path in args.images:
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            fail_count += 1
            continue
        
        logger.info(f"正在上传图片: {image_path}")
        image_url = uploader.upload_image(image_path)
        
        if image_url:
            logger.info(f"上传成功: {image_url}")
            success_count += 1
        else:
            logger.error(f"上传失败: {image_path}")
            fail_count += 1
    
    logger.info(f"上传完成: 成功 {success_count} 张，失败 {fail_count} 张")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GitHub图床示例脚本')
    
    # 添加命令行参数
    parser.add_argument('--images', nargs='+', required=True, help='要上传的图片路径列表')
    parser.add_argument('--owner', help='GitHub仓库所有者')
    parser.add_argument('--repo', help='GitHub仓库名称')
    parser.add_argument('--branch', default='main', help='GitHub仓库分支')
    parser.add_argument('--token', help='GitHub访问令牌')
    parser.add_argument('--path', default='images', help='图片在仓库中的路径')
    parser.add_argument('--base-url', help='图片访问的基础URL')
    
    args = parser.parse_args()
    
    # 上传图片
    upload_images(args)

if __name__ == '__main__':
    main()