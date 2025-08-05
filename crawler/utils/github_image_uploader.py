#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub图床模块，用于将图片上传到GitHub仓库并获取URL
"""

import os
import base64
import hashlib
import requests
from datetime import datetime
from urllib.parse import quote

# 导入配置
from crawler.config import crawler_config

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class GitHubImageUploader:
    """GitHub图床上传器，用于将图片上传到GitHub仓库并获取URL"""
    
    def __init__(self):
        """初始化GitHub图床上传器"""
        # 从配置中加载GitHub图床设置
        self.github_config = crawler_config.get('github', {})
        self.enabled = self.github_config.get('enabled', False)
        self.repo_owner = self.github_config.get('repo_owner', '')
        self.repo_name = self.github_config.get('repo_name', '')
        self.branch = self.github_config.get('branch', 'main')
        self.token = self.github_config.get('token', '')
        self.image_path = self.github_config.get('image_path', 'images')
        self.base_url = self.github_config.get('base_url', '')
        
        # 如果base_url未设置，则自动构建
        if not self.base_url and self.repo_owner and self.repo_name:
            # 确保image_path不以斜杠结尾，以避免URL中出现双斜杠
            image_path_clean = self.image_path.rstrip('/')
            self.base_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{image_path_clean}/"
        
        # 检查是否启用了GitHub图床
        if not self.enabled:
            logger.info("GitHub图床功能未启用")
        elif not self.token:
            logger.warning("GitHub图床功能已启用，但未设置访问令牌")
        elif not self.repo_owner or not self.repo_name:
            logger.warning("GitHub图床功能已启用，但未设置仓库信息")
    
    def upload_image(self, image_path):
        """上传图片到GitHub仓库
        
        Args:
            image_path (str): 图片本地路径
            
        Returns:
            str: 图片URL，上传失败则返回空字符串
        """
        if not self.enabled:
            logger.warning("GitHub图床功能未启用，无法上传图片")
            return ""
        
        if not self.token:
            logger.error("GitHub图床功能已启用，但未设置访问令牌(token)，无法上传图片")
            return ""
            
        if not self.repo_owner or not self.repo_name:
            logger.error("GitHub图床功能已启用，但未设置仓库信息(repo_owner/repo_name)，无法上传图片")
            return ""
        
        if not os.path.exists(image_path):
            logger.warning(f"图片不存在: {image_path}")
            return ""
        
        try:
            # 读取图片文件
            with open(image_path, 'rb') as f:
                file_content = f.read()
            
            # 生成唯一文件名，保持与storage_manager.py中的命名一致
            file_name = os.path.basename(image_path)
            file_ext = os.path.splitext(file_name)[1]
            
            # 从图片路径中提取任务ID
            # 假设图片路径格式为 .../data/task_id/images/filename
            path_parts = image_path.split(os.sep)
            task_id = None
            for i, part in enumerate(path_parts):
                if part == 'data' and i+1 < len(path_parts):
                    task_id = path_parts[i+1]
                    break
            
            # 如果找不到任务ID，则使用日期作为前缀
            if not task_id:
                date_prefix = datetime.now().strftime('%Y%m%d')
                file_hash = hashlib.md5(file_content).hexdigest()[:8]
                new_file_name = f"{date_prefix}_{file_hash}{file_ext}"
            else:
                # 使用任务ID作为文件名前缀
                file_hash = hashlib.md5(file_content).hexdigest()[:8]
                new_file_name = f"{task_id}_{file_hash}{file_ext}"
            
            # 构建API URL
            # 确保image_path不以斜杠开头或结尾，以避免URL中出现双斜杠
            image_path_clean = self.image_path.strip('/')
            github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{image_path_clean}/{new_file_name}"
            
            # 准备请求头和数据
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # 将图片内容编码为base64
            content_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # 准备请求数据
            data = {
                'message': f'Upload image {new_file_name}',
                'content': content_base64,
                'branch': self.branch
            }
            
            # 发送请求
            response = requests.put(github_api_url, headers=headers, json=data)
            
            # 检查响应
            if response.status_code in [201, 200]:
                # 上传成功，返回图片URL
                # 确保base_url以斜杠结尾，避免URL格式错误
                base_url = self.base_url if self.base_url.endswith('/') else f"{self.base_url}/"
                image_url = f"{base_url}{quote(new_file_name)}"
                logger.info(f"图片已上传到GitHub: {image_url}")
                return image_url
            else:
                # 上传失败
                logger.error(f"上传图片到GitHub失败: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"上传图片到GitHub时发生错误: {str(e)}")
            return ""
    
    def is_configured(self):
        """检查GitHub图床是否已正确配置
        
        Returns:
            bool: 是否已正确配置
        """
        return self.enabled and self.token and self.repo_owner and self.repo_name