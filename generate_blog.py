#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成脚本

该脚本用于根据提供的图片列表、元数据和模板生成博客文章。
可以作为独立脚本运行，也可以从其他模块调用。

用法：
    python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json --template template_name --output output.md
"""

import os
import sys
import json
import logging
import argparse
import shutil
import hashlib
from datetime import datetime
import re
from urllib.parse import urlparse

# 导入配置
from config import config

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlogGenerator:
    """博客生成器，用于根据提供的图片和元数据生成博客文章"""
    
    def __init__(self, template_name=None):
        """初始化博客生成器
        
        Args:
            template_name (str, optional): 模板名称，如果不提供则使用默认模板
        """
        # 从配置中加载博客设置
        self.output_path = config.get('blog', 'output_path', 'blogs')
        
        # 图片存储配置
        self.image_storage_type = config.get('blog', 'image_storage', {}).get('type', 'local')
        self.image_base_url = config.get('blog', 'image_storage', {}).get('base_url', 'http://example.com/images/')
        self.image_local_path = config.get('blog', 'image_storage', {}).get('local_path', 'static/images')
        
        # 模板配置
        self.templates_dir = config.get('blog', 'templates_dir', 'config/templates')
        
        # 设置模板
        self.template_name = template_name or 'default'
        self.template_path = self._get_template_path(self.template_name)
        
        # 创建输出目录
        os.makedirs(self.output_path, exist_ok=True)
        
        # 创建图片存储目录（如果是本地存储）
        if self.image_storage_type == 'local':
            os.makedirs(self.image_local_path, exist_ok=True)
    
    def _get_template_path(self, template_name):
        """获取模板文件路径
        
        Args:
            template_name (str): 模板名称
            
        Returns:
            str: 模板文件路径
        """
        # 检查是否是内置模板名称
        if template_name == 'default':
            template_file = 'blog_template.md'
        else:
            template_file = f"{template_name}.md"
        
        # 构建模板路径
        template_path = os.path.join(self.templates_dir, template_file)
        
        # 检查模板文件是否存在
        if not os.path.exists(template_path):
            logger.warning(f"模板文件不存在: {template_path}，将使用默认模板")
            # 尝试使用默认模板
            default_template_path = os.path.join(self.templates_dir, 'blog_template.md')
            if os.path.exists(default_template_path):
                return default_template_path
            else:
                # 创建默认模板
                self._create_default_template()
                return os.path.join(self.templates_dir, 'blog_template.md')
        
        return template_path
    
    def _create_default_template(self):
        """创建默认博客模板"""
        # 创建模板目录
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 默认模板内容
        default_template = """\# {title}

*发布时间: {date}*

*来源: [{source_name}]({source_url})*

## 概述

{summary}

## 图片展示

{image_gallery}

## 详细内容

{content}

## 标签

{tags}

---
*本文由爬虫自动生成*
"""
        
        # 写入默认模板
        template_path = os.path.join(self.templates_dir, 'blog_template.md')
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logger.info(f"已创建默认博客模板: {template_path}")
        except Exception as e:
            logger.error(f"创建默认博客模板失败: {str(e)}")
    
    def _get_template(self):
        """获取博客模板内容
        
        Returns:
            str: 模板内容
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取博客模板失败: {str(e)}")
            # 返回一个简单的默认模板
            return "# {title}\n\n{content}\n\n{image_gallery}"
    
    def _upload_image(self, image_path):
        """上传图片到存储
        
        Args:
            image_path (str): 图片本地路径
            
        Returns:
            str: 图片URL
        """
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return ""
        
        # 生成唯一文件名
        file_name = os.path.basename(image_path)
        file_ext = os.path.splitext(file_name)[1]
        file_hash = hashlib.md5(open(image_path, 'rb').read()).hexdigest()
        new_file_name = f"{file_hash}{file_ext}"
        
        # 根据存储类型处理图片
        if self.image_storage_type == 'local':
            # 本地存储
            dest_path = os.path.join(self.image_local_path, new_file_name)
            try:
                shutil.copy2(image_path, dest_path)
                logger.info(f"图片已复制到本地存储: {dest_path}")
                return os.path.join(self.image_base_url, new_file_name)
            except Exception as e:
                logger.error(f"复制图片失败: {str(e)}")
                return ""
        else:
            # 其他存储类型（如S3、OSS等）可以在这里扩展
            logger.warning(f"不支持的图片存储类型: {self.image_storage_type}，将使用本地存储")
            # 默认使用本地存储
            dest_path = os.path.join(self.image_local_path, new_file_name)
            try:
                shutil.copy2(image_path, dest_path)
                logger.info(f"图片已复制到本地存储: {dest_path}")
                return os.path.join(self.image_base_url, new_file_name)
            except Exception as e:
                logger.error(f"复制图片失败: {str(e)}")
                return ""
    
    def _generate_image_gallery(self, images):
        """生成图片画廊Markdown
        
        Args:
            images (list): 图片路径列表
            
        Returns:
            str: 图片画廊Markdown
        """
        if not images:
            return "*没有图片*"
        
        gallery = ""
        
        # 最多显示6张图片
        for i, img_path in enumerate(images[:6]):
            if os.path.exists(img_path):
                # 上传图片并获取URL
                img_url = self._upload_image(img_path)
                if img_url:
                    alt_text = f"图片{i+1}"
                    gallery += f"![{alt_text}]({img_url})\n\n"
        
        if len(images) > 6:
            gallery += f"*还有 {len(images) - 6} 张图片未显示*\n"
        
        return gallery
    
    def _generate_tags(self, metadata):
        """生成标签
        
        Args:
            metadata (dict): 元数据
            
        Returns:
            str: 标签Markdown
        """
        # 从元数据中提取标签
        tags = metadata.get('tags', [])
        
        # 如果没有标签，尝试从标题中提取
        if not tags and 'title' in metadata:
            title_words = re.findall(r'\w+', metadata['title'])
            tags = [word.lower() for word in title_words if len(word) > 3][:5]
        
        if not tags:
            return "*无标签*"
        
        return ' '.join([f"#{tag}" for tag in tags])
    
    def generate_blog(self, images, metadata, output_path=None):
        """生成博客文章
        
        Args:
            images (list): 图片路径列表
            metadata (dict): 元数据，包含标题、URL、内容等信息
            output_path (str, optional): 输出文件路径，如果不提供则自动生成
            
        Returns:
            tuple: (是否成功, 博客文件路径)
        """
        try:
            # 获取模板
            template = self._get_template()
            
            # 准备数据
            title = metadata.get('title', '未知标题')
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_name = metadata.get('source_name', '')
            source_url = metadata.get('url', '')
            summary = metadata.get('summary', '无摘要')
            content = metadata.get('content', '无内容')
            
            # 如果没有提供source_name，尝试从URL中提取
            if not source_name and source_url:
                source_name = urlparse(source_url).netloc
            
            # 生成图片画廊
            image_gallery = self._generate_image_gallery(images)
            
            # 生成标签
            tags = self._generate_tags(metadata)
            
            # 填充模板
            blog_content = template.format(
                title=title,
                date=date,
                source_name=source_name,
                source_url=source_url,
                summary=summary,
                image_gallery=image_gallery,
                content=content,
                tags=tags
            )
            
            # 确定输出路径
            if not output_path:
                # 生成文件名
                safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                date_prefix = datetime.now().strftime('%Y%m%d')
                filename = f"{date_prefix}-{safe_title}.md"
                output_path = os.path.join(self.output_path, filename)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存博客文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            
            logger.info(f"博客已生成: {output_path}")
            return True, output_path
            
        except Exception as e:
            logger.error(f"生成博客失败: {str(e)}")
            return False, ""


def load_metadata(metadata_path):
    """加载元数据
    
    Args:
        metadata_path (str): 元数据文件路径
        
    Returns:
        dict: 元数据
    """
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载元数据失败: {str(e)}")
        return {}


def list_available_templates():
    """列出可用的模板
    
    Returns:
        list: 模板名称列表
    """
    templates_dir = config.get('blog', 'templates_dir', 'config/templates')
    if not os.path.exists(templates_dir):
        return []
    
    templates = []
    for file in os.listdir(templates_dir):
        if file.endswith('.md'):
            template_name = os.path.splitext(file)[0]
            templates.append(template_name)
    
    return templates


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成博客文章')
    parser.add_argument('--images', nargs='+', help='图片路径列表')
    parser.add_argument('--metadata', required=True, help='元数据文件路径')
    parser.add_argument('--template', help='模板名称')
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
    
    # 检查必要参数
    if not args.metadata:
        print("错误: 必须提供元数据文件路径")
        parser.print_help()
        return
    
    # 加载元数据
    metadata = load_metadata(args.metadata)
    if not metadata:
        print("错误: 无法加载元数据或元数据为空")
        return
    
    # 创建博客生成器
    generator = BlogGenerator(template_name=args.template)
    
    # 生成博客
    success, blog_path = generator.generate_blog(
        images=args.images or [],
        metadata=metadata,
        output_path=args.output
    )
    
    if success:
        print(f"博客已成功生成: {blog_path}")
    else:
        print("生成博客失败")


if __name__ == '__main__':
    main()