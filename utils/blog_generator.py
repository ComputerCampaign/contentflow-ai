#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块，用于根据爬虫结果自动生成博客文章
"""

import os
import json
import logging
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

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlogGenerator:
    """博客生成器，用于根据爬虫结果自动生成博客文章"""
    
    def __init__(self):
        """初始化博客生成器"""
        # 从配置中加载博客设置
        self.enabled = config.get('blog', 'enabled', False)
        self.template_path = config.get('blog', 'template_path', 'config/templates/blog_template.md')
        self.output_path = config.get('blog', 'output_path', 'blogs')
        
        # 图片存储配置
        self.image_storage_type = config.get('blog', 'image_storage', {}).get('type', 'local')
        self.image_base_url = config.get('blog', 'image_storage', {}).get('base_url', 'http://example.com/images/')
        self.image_local_path = config.get('blog', 'image_storage', {}).get('local_path', 'static/images')
        
        # 检查是否启用了博客生成
        if not self.enabled:
            logger.info("博客生成功能未启用")
        else:
            # 创建输出目录
            os.makedirs(self.output_path, exist_ok=True)
            
            # 创建图片存储目录（如果是本地存储）
            if self.image_storage_type == 'local':
                os.makedirs(self.image_local_path, exist_ok=True)
            
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
        """生成图片画廊Markdown
        
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
            if 'local_path' in img and os.path.exists(img['local_path']):
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
            
            # 保存博客文件
            blog_path = os.path.join(self.output_path, filename)
            with open(blog_path, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            
            logger.info(f"博客已生成: {blog_path}")
            return True, blog_path
            
        except Exception as e:
            logger.error(f"生成博客失败: {str(e)}")
            return False, ""

# 创建全局博客生成器实例
blog_generator = BlogGenerator()

# 导出博客生成器实例，方便其他模块导入
__all__ = ['blog_generator']