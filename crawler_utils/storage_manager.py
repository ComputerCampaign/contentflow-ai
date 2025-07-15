#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import hashlib
import logging
import shutil
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageManager:
    """存储管理器，负责管理爬虫数据的存储结构"""
    
    def __init__(self, base_dir='data'):
        """初始化存储管理器
        
        Args:
            base_dir (str): 基础数据目录
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def create_task_directory(self, task_id=None, page_url=None):
        """创建任务目录
        
        Args:
            task_id (str, optional): 任务ID，如果不提供则自动生成
            page_url (str, optional): 页面URL，用于生成任务ID
            
        Returns:
            tuple: (任务ID, 任务目录路径)
        """
        # 如果没有提供任务ID，则自动生成
        if not task_id:
            if page_url:
                # 从URL生成任务ID
                parsed_url = urlparse(page_url)
                path_parts = parsed_url.path.strip('/').split('/')
                if path_parts and path_parts[-1]:
                    # 使用URL最后一部分作为任务ID的一部分
                    task_id = self._sanitize_filename(path_parts[-1])
                else:
                    # 使用域名作为任务ID的一部分
                    task_id = self._sanitize_filename(parsed_url.netloc)
            
            # 添加时间戳确保唯一性
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_id = f"{task_id}_{timestamp}" if task_id else timestamp
        
        # 创建任务目录
        task_dir = os.path.join(self.base_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 创建图片目录
        images_dir = os.path.join(task_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # 创建元数据目录
        metadata_dir = os.path.join(task_dir, 'metadata')
        os.makedirs(metadata_dir, exist_ok=True)
        
        logger.info(f"创建任务目录: {task_dir}")
        return task_id, task_dir
    
    def get_image_path(self, task_dir, page_url, img_url, index=None):
        """获取图片保存路径
        
        Args:
            task_dir (str): 任务目录路径
            page_url (str): 页面URL
            img_url (str): 图片URL
            index (int, optional): 图片索引
            
        Returns:
            str: 图片保存路径
        """
        # 从页面URL中提取名称部分
        parsed_url = urlparse(page_url)
        path_parts = parsed_url.path.strip('/').split('/')
        page_name = ''
        
        # 尝试从URL路径中提取有意义的名称
        if path_parts and path_parts[-1]:
            page_name = self._sanitize_filename(path_parts[-1])
        elif len(path_parts) > 1 and path_parts[-2]:
            page_name = self._sanitize_filename(path_parts[-2])
        else:
            page_name = self._sanitize_filename(parsed_url.netloc)
        
        # 从图片URL中提取扩展名
        img_parsed = urlparse(img_url)
        img_path = img_parsed.path
        _, ext = os.path.splitext(img_path)
        
        # 如果没有扩展名，使用默认扩展名
        if not ext:
            ext = '.jpg'
        
        # 生成图片文件名
        if index is not None:
            filename = f"{page_name}_{index}{ext}"
        else:
            # 使用图片URL的哈希值作为文件名
            hash_obj = hashlib.md5(img_url.encode('utf-8'))
            filename = f"{page_name}_{hash_obj.hexdigest()[:8]}{ext}"
        
        # 返回完整路径
        return os.path.join(task_dir, 'images', filename)
    
    def save_page_html(self, task_dir, page_url, html_content):
        """保存页面HTML内容
        
        Args:
            task_dir (str): 任务目录路径
            page_url (str): 页面URL
            html_content (str): HTML内容
            
        Returns:
            str: HTML文件保存路径
        """
        # 生成HTML文件名
        filename = 'page.html'
        file_path = os.path.join(task_dir, filename)
        
        # 保存HTML内容
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"页面HTML已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存页面HTML失败: {str(e)}")
            return None
    
    def save_page_info(self, task_dir, page_info):
        """保存页面信息
        
        Args:
            task_dir (str): 任务目录路径
            page_info (dict): 页面信息
            
        Returns:
            str: 页面信息文件保存路径
        """
        # 生成页面信息文件名
        filename = 'page_info.json'
        file_path = os.path.join(task_dir, 'metadata', filename)
        
        # 保存页面信息
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_info, f, indent=4, ensure_ascii=False)
            logger.info(f"页面信息已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存页面信息失败: {str(e)}")
            return None
    
    def save_images_csv(self, task_dir, images_data):
        """保存图片数据到CSV
        
        Args:
            task_dir (str): 任务目录路径
            images_data (list): 图片数据列表
            
        Returns:
            str: CSV文件保存路径
        """
        import pandas as pd
        
        # 生成CSV文件名
        filename = 'images.csv'
        file_path = os.path.join(task_dir, 'metadata', filename)
        
        # 保存CSV
        try:
            df = pd.DataFrame(images_data)
            df.to_csv(file_path, index=False, encoding='utf-8')
            logger.info(f"图片数据已保存到CSV: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存图片数据到CSV失败: {str(e)}")
            return None
    
    def _sanitize_filename(self, name):
        """清理文件名，移除非法字符
        
        Args:
            name (str): 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除非法字符
        name = re.sub(r'[\\/*?:"<>|]', '', name)
        # 将空格替换为下划线
        name = re.sub(r'\s+', '_', name)
        # 限制长度
        if len(name) > 50:
            name = name[:50]
        return name.lower()