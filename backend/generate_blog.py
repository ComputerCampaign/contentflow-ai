#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成脚本

该脚本用于生成博客文章，支持两种模式：
1. 从爬虫数据生成：从爬虫生成的数据目录中读取信息，并生成对应的博客文章
2. 从自定义数据生成：根据提供的图片列表、元数据和模板生成博客文章

用法：
    # 从爬虫数据生成
    python generate_blog.py --task-dir <爬虫任务目录> [--template <模板名称>] [--output <输出文件路径>]
    
    # 从自定义数据生成
    python generate_blog.py --images <图片路径> [<图片路径> ...] --metadata <元数据文件路径> [--template <模板名称>] [--output <输出文件路径>]
    
    # 列出可用模板
    python generate_blog.py --list-templates
"""

import os
import sys
import json
import argparse
import pandas as pd
from urllib.parse import urlparse

# 导入配置
from config import config

# 导入博客生成器
from .utils.generate_blog import BlogGenerator, list_available_templates

# 导入日志配置
from .utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)


def load_page_info(task_dir):
    """
    从任务目录加载页面信息
    
    Args:
        task_dir (str): 爬虫任务目录路径
        
    Returns:
        dict: 页面信息，包含图片数据
    """
    page_info_path = os.path.join(task_dir, 'metadata', 'page_info.json')
    if not os.path.exists(page_info_path):
        logger.error(f"页面信息文件不存在: {page_info_path}")
        return None
    
    try:
        with open(page_info_path, 'r', encoding='utf-8') as f:
            page_info = json.load(f)
        logger.info(f"已加载页面信息: {page_info_path}")
        return page_info
    except Exception as e:
        logger.error(f"加载页面信息失败: {str(e)}")
        return None


def load_images_data(task_dir):
    """
    从任务目录加载图片数据
    
    Args:
        task_dir (str): 爬虫任务目录路径
        
    Returns:
        list: 图片路径列表
    """
    # 首先尝试从page_info.json获取图片信息
    page_info = load_page_info(task_dir)
    if page_info and 'images' in page_info:
        image_paths = []
        for img in page_info['images']:
            if 'local_path' in img and os.path.exists(img['local_path']):
                image_paths.append(img['local_path'])
        
        if image_paths:
            logger.info(f"从页面信息中找到 {len(image_paths)} 张图片")
            return image_paths
    
    # 如果从page_info.json获取失败，则尝试从images.csv获取
    csv_path = os.path.join(task_dir, 'metadata', 'images.csv')
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            image_paths = []
            
            for _, row in df.iterrows():
                if 'local_path' in row and os.path.exists(row['local_path']):
                    image_paths.append(row['local_path'])
                else:
                    # 尝试从URL推断本地路径
                    img_url = row['url']
                    img_filename = os.path.basename(urlparse(img_url).path)
                    if not img_filename or '.' not in img_filename:
                        continue
                    
                    local_path = os.path.join(task_dir, 'images', img_filename)
                    if os.path.exists(local_path):
                        image_paths.append(local_path)
            
            if image_paths:
                logger.info(f"从CSV文件中找到 {len(image_paths)} 张图片")
                return image_paths
        except Exception as e:
            logger.error(f"处理图片CSV文件失败: {str(e)}")
    
    # 如果上述方法都失败，则直接扫描images目录
    images_dir = os.path.join(task_dir, 'images')
    if os.path.exists(images_dir) and os.path.isdir(images_dir):
        image_paths = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                image_paths.append(os.path.join(images_dir, filename))
        
        if image_paths:
            logger.info(f"从images目录中找到 {len(image_paths)} 张图片")
            return image_paths
    
    logger.warning("未找到任何图片")
    return []


def prepare_metadata(task_dir, page_info=None):
    """
    准备博客元数据
    
    Args:
        task_dir (str): 爬虫任务目录路径
        page_info (dict, optional): 页面信息
        
    Returns:
        dict: 博客元数据
    """
    if page_info is None:
        page_info = load_page_info(task_dir)
        if not page_info:
            logger.error("无法加载页面信息，无法准备元数据")
            return None
    
    # 准备元数据
    metadata = {
        'title': page_info.get('page_title', '未知标题'),
        'url': page_info.get('url', ''),
        'source_name': urlparse(page_info.get('url', '')).netloc,
        'summary': page_info.get('description', ''),
        'content': page_info.get('content', ''),
        'tags': page_info.get('tags', [])
    }
    
    return metadata


def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成博客文章')
    
    # 创建互斥参数组，用户只能选择一种模式
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--task-dir', help='爬虫任务目录路径（从爬虫数据生成模式）')
    mode_group.add_argument('--images', nargs='+', help='图片路径列表（从自定义数据生成模式）')
    
    # 其他参数
    parser.add_argument('--metadata', help='元数据文件路径（从自定义数据生成模式必需）')
    parser.add_argument('--template', help='博客模板名称')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--list-templates', action='store_true', help='列出可用的模板')
    
    args = parser.parse_args()
    
    # 列出可用模板
    if args.list_templates:
        templates = list_available_templates()
        if templates:
            print("可用的模板:")
            for template in templates:
                print(f"  - {template}")
        else:
            print("没有可用的模板")
        return
    
    # 创建博客生成器
    generator = BlogGenerator(template_name=args.template)
    
    # 根据模式选择处理方式
    if args.task_dir:  # 从爬虫数据生成模式
        # 检查任务目录
        if not os.path.exists(args.task_dir) or not os.path.isdir(args.task_dir):
            logger.error(f"任务目录不存在或不是目录: {args.task_dir}")
            sys.exit(1)
        
        # 加载页面信息
        page_info = load_page_info(args.task_dir)
        if not page_info:
            logger.error("无法加载页面信息，无法生成博客")
            sys.exit(1)
        
        # 加载图片数据
        image_paths = load_images_data(args.task_dir)
        
        # 准备元数据
        metadata = prepare_metadata(args.task_dir, page_info)
        if not metadata:
            logger.error("无法准备元数据，无法生成博客")
            sys.exit(1)
        
        # 生成博客
        success, blog_path = generator.generate_blog(
            images=image_paths,
            metadata=metadata,
            output_path=args.output
        )
    else:  # 从自定义数据生成模式
        # 检查必要参数
        if not args.metadata:
            logger.error("错误: 使用自定义数据生成模式时必须提供元数据文件路径")
            parser.print_help()
            sys.exit(1)
        
        # 加载元数据
        from .utils.generate_blog import load_metadata
        metadata = load_metadata(args.metadata)
        if not metadata:
            logger.error("错误: 无法加载元数据或元数据为空")
            sys.exit(1)
        
        # 生成博客
        success, blog_path = generator.generate_blog(
            images=args.images or [],
            metadata=metadata,
            output_path=args.output
        )
    
    # 输出结果
    if success:
        print(f"博客已成功生成: {blog_path}")
    else:
        print("生成博客失败")
        sys.exit(1)


if __name__ == '__main__':
    main()