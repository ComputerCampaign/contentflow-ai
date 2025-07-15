#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from .image_downloader import ImageDownloader
from .storage_manager import StorageManager

logger = logging.getLogger(__name__)

class BatchDownloader:
    """批量图片下载器，负责管理多个图片的下载任务"""
    
    def __init__(self, storage_manager, timeout=10, retry=3, max_workers=5):
        """初始化批量下载器
        
        Args:
            storage_manager (StorageManager): 存储管理器实例
            timeout (int): 请求超时时间（秒）
            retry (int): 失败重试次数
            max_workers (int): 最大并发下载数
        """
        self.storage_manager = storage_manager
        self.downloader = ImageDownloader(timeout, retry)
        self.max_workers = max_workers
    
    def download_images(self, images_data, page_url, task_dir):
        """批量下载图片
        
        Args:
            images_data (list): 图片数据列表，每个元素是包含url字段的字典
            page_url (str): 页面URL，用作引用页面
            task_dir (str): 任务目录路径
            
        Returns:
            list: 下载成功的图片信息列表
        """
        if not images_data:
            logger.warning("没有图片需要下载")
            return []
        
        logger.info(f"开始下载 {len(images_data)} 张图片")
        
        # 准备下载任务
        download_tasks = []
        for index, img_data in enumerate(images_data):
            img_url = img_data['url']
            
            # 处理相对URL
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(page_url, img_url)
                img_data['url'] = img_url  # 更新为完整URL
            
            # 获取图片保存路径
            save_path = self.storage_manager.get_image_path(
                task_dir, page_url, img_url, index=index+1
            )
            
            # 添加到下载任务
            download_tasks.append({
                'img_data': img_data,
                'img_url': img_url,
                'save_path': save_path,
                'index': index+1
            })
        
        # 执行下载任务
        successful_downloads = []
        failed_downloads = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务
            future_to_task = {}
            for task in download_tasks:
                future = executor.submit(
                    self.downloader.download,
                    task['img_url'],
                    task['save_path'],
                    page_url,  # 引用页面
                    True  # 跳过已存在的文件
                )
                future_to_task[future] = task
            
            # 处理下载结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    success = future.result()
                    if success:
                        # 添加本地文件路径到图片数据
                        task['img_data']['local_path'] = task['save_path']
                        successful_downloads.append(task['img_data'])
                    else:
                        failed_downloads.append(task['img_data'])
                except Exception as e:
                    logger.error(f"下载任务异常: {str(e)}")
                    failed_downloads.append(task['img_data'])
        
        # 统计下载结果
        logger.info(f"图片下载完成: 成功 {len(successful_downloads)} 张，失败 {len(failed_downloads)} 张")
        
        return successful_downloads