#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Loader Utility

This module provides functionality to load crawler data including metadata and images.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class CrawlerData:
    """爬虫数据结构"""
    title: str
    description: str
    comments: List[Dict[str, Any]]  # 支持嵌套的评论结构
    image_url: Optional[str] = None  # 图片URL地址
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'title': self.title,
            'description': self.description,
            'comments': self.comments,
            'image_url': self.image_url
        }


class DataLoader:
    """数据加载器"""
    
    def __init__(self, base_path: str = "crawler_data"):
        """初始化数据加载器
        
        Args:
            base_path: 爬虫数据基础路径
        """
        self.base_path = Path(base_path)
        
    def load_crawler_data(self, task_name: str) -> Optional[CrawlerData]:
        """加载指定task_name的爬虫数据
        
        Args:
            task_name: 任务名称 (如 'task_name_20240115_143022')
            
        Returns:
            CrawlerData对象，如果加载失败返回None
        """
        task_path = self.base_path / task_name
        
        if not task_path.exists():
            return None
            
        # 加载元数据
        metadata_file = task_path / "metadata" / "metadata.json"
        if not metadata_file.exists():
            return None
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
            
        # 从metadata中提取图片URL，优先使用github_url
        image_url = None
        images = metadata.get('images', [])
        if images and len(images) > 0:
            first_image = images[0]
            # 优先使用github_url，如果没有则使用原始url
            image_url = first_image.get('github_url') or first_image.get('url')
        
        return CrawlerData(
            title=metadata.get('title', ''),
            description=metadata.get('description', ''),
            comments=metadata.get('comments', []),
            image_url=image_url
        )
    

    
    def list_tasks(self) -> List[str]:
        """列出所有可用的任务ID
        
        Returns:
            任务ID列表
        """
        if not self.base_path.exists():
            return []
            
        tasks = []
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 检查是否包含任务相关文件来确认这是一个任务目录
                metadata_file = item / "metadata" / "metadata.json"
                if metadata_file.exists():
                    tasks.append(item.name)
                
        return sorted(tasks)
    
    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """获取指定任务的基本信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典，如果任务不存在返回None
        """
        task_path = self.base_path / task_id
        if not task_path.exists():
            return None
            
        metadata_file = task_path / "metadata" / "metadata.json"
        if not metadata_file.exists():
            return None
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return {
                    'task_id': task_id,
                    'title': metadata.get('title', ''),
                    'description': metadata.get('description', ''),
                    'url': metadata.get('url', ''),
                    'created_time': metadata.get('created_time', ''),
                    'has_images': len(metadata.get('images', [])) > 0
                }
        except (json.JSONDecodeError, IOError):
            return None
    
    def load_all_data(self) -> List[Tuple[str, CrawlerData]]:
        """加载所有可用的爬虫数据
        
        Returns:
            (task_id, crawler_data) 元组列表
        """
        all_data = []
        
        for task_id in self.list_tasks():
            data = self.load_crawler_data(task_id)
            if data:
                all_data.append((task_id, data))
                    
        return all_data