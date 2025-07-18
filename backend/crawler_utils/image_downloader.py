#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import hashlib
import requests
from urllib.parse import urljoin, urlparse
from tqdm import tqdm

# 导入日志配置
import os
import sys
# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class ImageDownloader:
    """图片下载器，负责下载单个图片"""
    
    def __init__(self, timeout=10, retry=3):
        """初始化图片下载器
        
        Args:
            timeout (int): 请求超时时间（秒）
            retry (int): 失败重试次数
        """
        self.timeout = timeout
        self.retry = retry
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def download(self, url, save_path, referer=None, skip_existing=True):
        """下载单个图片
        
        Args:
            url (str): 图片URL
            save_path (str): 保存路径
            referer (str, optional): 引用页面URL
            skip_existing (bool): 是否跳过已存在的文件
            
        Returns:
            bool: 是否下载成功
        """
        # 检查文件是否已存在
        if skip_existing and os.path.exists(save_path):
            logger.info(f"文件已存在，跳过下载: {save_path}")
            return True
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 设置引用页面
        headers = {}
        if referer:
            headers['Referer'] = referer
        
        # 下载图片
        for attempt in range(self.retry + 1):
            try:
                response = self.session.get(url, timeout=self.timeout, headers=headers, stream=True)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"非图片内容类型: {content_type}, URL: {url}")
                
                # 获取文件大小
                total_size = int(response.headers.get('Content-Length', 0))
                
                # 下载文件
                with open(save_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(save_path)) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                logger.info(f"图片下载成功: {save_path}")
                return True
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retry:
                    logger.warning(f"下载失败，重试 {attempt+1}/{self.retry}: {url}")
                else:
                    logger.error(f"下载失败: {url}, 错误: {str(e)}")
                    return False
        
        return False