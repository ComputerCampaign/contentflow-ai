#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成工具模块

该模块用于根据提供的图片列表、元数据和模板生成博客文章。
可以作为独立模块被其他脚本调用。
"""

import os
import sys
import json
import argparse
import shutil
import hashlib
from datetime import datetime
import re
from urllib.parse import urlparse

# 导入配置
from blog_generator.config import blog_config

# 导入日志配置
from blog_generator.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class BlogGenerator:
    """博客生成器，用于根据提供的图片和元数据生成博客文章"""
    
    def __init__(self, template_name=None):
        """初始化博客生成器
        
        Args:
            template_name (str, optional): 模板名称，如果不提供则使用默认模板
        """
        # 从配置中加载博客设置
        self.output_path = blog_config.get('blog', 'output_dir', 'blogs')
        
        # 图片存储配置 - 强制使用GitHub
        self.image_storage_type = 'github'
        
        # 是否使用爬虫的图片存储设置
        self.use_crawler_image_storage = blog_config.get('blog', 'use_crawler_image_storage', True)
        
        # 模板配置
        self.templates_dir = blog_config.get('blog', 'templates_dir', 'config/templates')
        
        # 设置模板
        self.template_name = template_name or 'default'
        self.template_path = self._get_template_path(self.template_name)
        
        # 创建输出目录结构
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'published'), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'drafts'), exist_ok=True)
    
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
        default_template = """\
# {title}

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
        """上传图片到GitHub图床
        
        Args:
            image_path (str): 图片本地路径
            
        Returns:
            str: 图片URL
        """
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return ""
            
        # 检查图片是否已经有GitHub URL（在元数据中）
        try:
            # 从图片路径推断任务目录
            task_dir = os.path.dirname(os.path.dirname(image_path))
            metadata_file = os.path.join(task_dir, 'metadata', 'page_info.json')
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    page_info = json.load(f)
                    
                # 查找图片在元数据中的记录
                for img in page_info.get('images', []):
                    if img.get('local_path') == image_path and img.get('github_url'):
                        logger.info(f"使用已存在的GitHub URL: {img['github_url']}")
                        return img['github_url']
        except Exception as e:
            logger.warning(f"检查已存在的GitHub URL时出错: {str(e)}")
        
        # 如果配置为使用爬虫的图片存储，则尝试使用StorageManager上传
        if self.use_crawler_image_storage:
            try:
                from crawler.utils.storage_manager import StorageManager
                storage_manager = StorageManager()
                github_url = storage_manager.upload_to_github(image_path)
                if github_url:
                    logger.info(f"使用爬虫的GitHub图床上传图片成功: {github_url}")
                    return github_url
            except Exception as e:
                logger.warning(f"使用爬虫的GitHub图床上传图片失败: {str(e)}")
        
        # 导入GitHub图床上传器
        from crawler.utils.github_image_uploader import GitHubImageUploader
        
        # 创建GitHub图床上传器实例
        github_uploader = GitHubImageUploader()
        
        # 上传图片到GitHub
        github_url = github_uploader.upload_image(image_path)
        if github_url:
            logger.info(f"图片已上传到GitHub: {github_url}")
            return github_url
        else:
            logger.error(f"上传图片到GitHub失败: {image_path}")
            # 不考虑上传失败的情况，直接返回空字符串
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
                # 保存到drafts目录
                output_path = os.path.join(self.output_path, 'drafts', filename)
            
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
    from blog_generator.config import blog_config
    templates_dir = blog_config.get('blog', 'templates_dir', 'config/templates')
    if not os.path.exists(templates_dir):
        return []
    
    templates = []
    for file in os.listdir(templates_dir):
        if file.endswith('.md'):
            template_name = os.path.splitext(file)[0]
            templates.append(template_name)
    
    return templates


# 导出类和函数，方便其他模块导入
__all__ = ['BlogGenerator', 'load_metadata', 'list_available_templates']