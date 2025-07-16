#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块，用于根据爬虫结果自动生成博客文章
"""

import os
import json
import pandas as pd
from datetime import datetime
import shutil
import re
import hashlib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# 导入配置
from config import config

# 导入GitHub图床上传器
from crawler_utils.github_image_uploader import GitHubImageUploader

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class BlogGenerator:
    """博客生成器，用于根据爬虫结果自动生成博客文章"""
    
    def __init__(self):
        """初始化博客生成器"""
        # 从配置中加载博客设置
        self.enabled = config.get('blog', 'enabled', False)
        self.template_path = config.get('blog', 'template_path', 'config/templates/blog_template.md')
        self.output_path = config.get('blog', 'output_path', 'blogs')
        
        # 图片存储配置 - 强制使用GitHub
        self.image_storage_type = 'github'
        
        # 检查是否使用爬虫的图片存储配置
        self.use_crawler_image_storage = config.get('blog', 'use_crawler_image_storage', True)
        
        # 初始化GitHub图床上传器
        self.github_uploader = GitHubImageUploader()
        
        # 检查是否启用了博客生成
        if not self.enabled:
            logger.info("博客生成功能未启用")
        else:
            # 创建输出目录结构
            os.makedirs(os.path.join(self.output_path, 'published'), exist_ok=True)
            os.makedirs(os.path.join(self.output_path, 'drafts'), exist_ok=True)
            
            # 检查模板文件
            if not os.path.exists(self.template_path):
                logger.warning(f"博客模板文件不存在: {self.template_path}，将使用默认模板")
                self._create_default_template()
    
    def _create_default_template(self):
        """创建默认博客模板"""
        # 创建模板目录
        os.makedirs(os.path.dirname(self.template_path), exist_ok=True)
        
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
        try:
            with open(self.template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logger.info(f"已创建默认博客模板: {self.template_path}")
        except Exception as e:
            logger.error(f"创建默认博客模板失败: {str(e)}")
    
    def _get_template(self):
        """获取博客模板
        
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
        """上传图片到GitHub图床或获取已上传的URL
        
        Args:
            image_path (str): 图片本地路径
            
        Returns:
            str: 图片URL
        """
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return ""
            
        # 优先使用已存在的GitHub URL（在元数据中）
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
                from crawler_utils.storage_manager import StorageManager
                storage_manager = StorageManager()
                github_url = storage_manager.upload_to_github(image_path)
                if github_url:
                    logger.info(f"使用爬虫的GitHub图床上传图片成功: {github_url}")
                    return github_url
            except Exception as e:
                logger.warning(f"使用爬虫的GitHub图床上传图片失败: {str(e)}")
        
        # 使用博客模块自己的GitHub图床上传器
        image_url = self.github_uploader.upload_image(image_path)
        if image_url:
            logger.info(f"图片已上传到GitHub: {image_url}")
            return image_url
        else:
            logger.error(f"上传图片到GitHub失败: {image_path}")
            # 不考虑上传失败的情况，直接返回空字符串
            return ""
    
    def _extract_summary(self, html_content, max_length=200):
        """从HTML内容中提取摘要
        
        Args:
            html_content (str): HTML内容
            max_length (int): 最大摘要长度
            
        Returns:
            str: 摘要文本
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.extract()
            
            # 获取文本
            text = soup.get_text(separator=' ', strip=True)
            
            # 清理文本
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 截取摘要
            if len(text) > max_length:
                text = text[:max_length] + '...'
            
            return text
        except Exception as e:
            logger.error(f"提取摘要失败: {str(e)}")
            return ""
    
    def _generate_image_gallery(self, images):
        """生成图片画廊Markdown，使用GitHub图床地址
        
        Args:
            images (list): 图片信息列表，每个元素为包含url和local_path的字典
            
        Returns:
            str: 图片画廊Markdown
        """
        if not images:
            return "*没有图片*"
        
        gallery = ""
        
        # 最多显示6张图片
        for i, img in enumerate(images[:6]):
            # 优先使用GitHub图片URL
            if 'github_url' in img and img['github_url']:
                alt_text = img.get('alt', '') or f"图片{i+1}"
                gallery += f"![{alt_text}]({img['github_url']})\n\n"
            elif 'local_path' in img and os.path.exists(img['local_path']):
                # 上传图片并获取URL
                img_url = self._upload_image(img['local_path'])
                if img_url:
                    alt_text = img.get('alt', '') or f"图片{i+1}"
                    gallery += f"![{alt_text}]({img_url})\n\n"
        
        if len(images) > 6:
            gallery += f"*还有 {len(images) - 6} 张图片未显示*\n"
        
        return gallery
    
    def _generate_tags(self, parsed_data):
        """生成标签
        
        Args:
            parsed_data (dict): 解析结果
            
        Returns:
            str: 标签Markdown
        """
        # 从标题中提取可能的标签
        tags = set()
        
        # 从页面标题中提取
        if 'page_title' in parsed_data:
            title_words = re.findall(r'\w+', parsed_data['page_title'])
            for word in title_words:
                if len(word) > 3:  # 只使用长度大于3的词作为标签
                    tags.add(word.lower())
        
        # 从标题中提取
        if 'headings' in parsed_data:
            for heading in parsed_data['headings']:
                heading_words = re.findall(r'\w+', heading.get('text', ''))
                for word in heading_words:
                    if len(word) > 3:
                        tags.add(word.lower())
        
        # 最多使用5个标签
        tags = list(tags)[:5]
        
        if not tags:
            return "*无标签*"
        
        return ' '.join([f"#{tag}" for tag in tags])
    
    def generate_blog(self, url, html_content, parsed_data, data_dir):
        """生成博客文章
        
        Args:
            url (str): 爬取的URL
            html_content (str): HTML内容
            parsed_data (dict): 解析结果
            data_dir (str): 数据目录
            
        Returns:
            tuple: (是否成功, 博客文件路径)
        """
        if not self.enabled:
            logger.info("博客生成功能未启用，跳过生成")
            return False, ""
        
        try:
            # 获取模板
            template = self._get_template()
            
            # 准备数据
            title = parsed_data.get('page_title', '未知标题')
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_name = urlparse(url).netloc
            source_url = url
            summary = self._extract_summary(html_content)
            
            # 处理图片
            images = []
            
            # 首先尝试从page_info.json获取图片信息（包含GitHub URL）
            page_info_path = os.path.join(data_dir, 'metadata', 'page_info.json')
            if os.path.exists(page_info_path):
                try:
                    with open(page_info_path, 'r', encoding='utf-8') as f:
                        page_info = json.load(f)
                    
                    if 'images' in page_info:
                        for img in page_info['images']:
                            img_data = {
                                'url': img['url'],
                                'alt': img.get('alt', '')
                            }
                            
                            # 添加本地路径
                            if 'local_path' in img and os.path.exists(img['local_path']):
                                img_data['local_path'] = img['local_path']
                            
                            # 添加GitHub URL
                            if 'github_url' in img and img['github_url']:
                                img_data['github_url'] = img['github_url']
                            
                            images.append(img_data)
                except Exception as e:
                    logger.error(f"从page_info.json读取图片信息失败: {str(e)}")
            
            # 如果从page_info.json获取失败，则尝试从CSV文件获取
            if not images:
                csv_path = os.path.join(data_dir, 'images.csv')
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        for _, row in df.iterrows():
                            img_url = row['url']
                            img_alt = row.get('alt', '')
                            
                            # 查找本地图片路径
                            img_filename = os.path.basename(urlparse(img_url).path)
                            if not img_filename or '.' not in img_filename:
                                img_filename = f"{hash(img_url) & 0xffffffff}.jpg"
                            
                            local_path = os.path.join(data_dir, 'images', img_filename)
                            
                            if os.path.exists(local_path):
                                images.append({
                                    'url': img_url,
                                    'alt': img_alt,
                                    'local_path': local_path
                                })
                    except Exception as e:
                        logger.error(f"处理图片CSV文件失败: {str(e)}")
            
            # 生成图片画廊
            image_gallery = self._generate_image_gallery(images)
            
            # 生成标签
            tags = self._generate_tags(parsed_data)
            
            # 生成内容
            content = ""
            if 'headings' in parsed_data and parsed_data['headings']:
                for heading in parsed_data['headings']:
                    level = heading.get('level', 1)
                    text = heading.get('text', '')
                    content += f"{'#' * (level + 1)} {text}\n\n"
                    content += "这里是内容段落。\n\n"
            else:
                content = "这里是默认内容。\n\n"
            
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
            
            # 生成文件名
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            date_prefix = datetime.now().strftime('%Y%m%d')
            filename = f"{date_prefix}-{safe_title}.md"
            
            # 保存博客文件到草稿目录
            draft_path = os.path.join(self.output_path, 'drafts', filename)
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            
            logger.info(f"博客草稿已生成: {draft_path}")
            return True, draft_path
            
        except Exception as e:
            logger.error(f"生成博客失败: {str(e)}")
            return False, ""

# 创建全局博客生成器实例
blog_generator = BlogGenerator()

# 导出博客生成器实例，方便其他模块导入
__all__ = ['blog_generator']