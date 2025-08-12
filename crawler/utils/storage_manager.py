#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import hashlib
import shutil
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, List, Optional, Any

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class StorageManager:
    """存储管理器，负责管理爬虫数据的存储结构"""
    
    def __init__(self, base_dir: str = 'data'):
        """初始化存储管理器
        
        Args:
            base_dir: 基础数据目录
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def create_task_dir(self, task_id: Optional[str] = None, page_url: Optional[str] = None) -> str:
        """创建任务目录
        
        Args:
            task_id: 任务ID，如果不提供则自动生成
            page_url: 页面URL
            
        Returns:
            任务目录路径
        """
        # 如果没有提供任务ID，则自动生成
        if not task_id:
            # 使用时间戳或UUID生成任务ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # 可以选择使用UUID增加唯一性
            import uuid
            random_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
            task_id = f"task_{timestamp}_{random_id}"
        
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
        return task_dir
    
    def get_image_path(self, task_dir: str, page_url: str, img_url: str, index: Optional[int] = None) -> str:
        """获取图片保存路径
        
        Args:
            task_dir: 任务目录路径
            page_url: 页面URL
            img_url: 图片URL
            index: 图片索引
            
        Returns:
            图片保存路径
        """
        # 获取任务ID（从任务目录路径中提取）
        task_id = os.path.basename(task_dir)
        
        # 从图片URL中提取扩展名
        img_parsed = urlparse(img_url)
        img_path = img_parsed.path
        _, ext = os.path.splitext(img_path)
        
        # 如果没有扩展名，使用默认扩展名
        if not ext:
            ext = '.jpg'
        
        # 生成图片文件名，使用task_id加索引的形式
        if index is not None:
            filename = f"{task_id}_{index}{ext}"
        else:
            # 使用图片URL的哈希值作为索引
            hash_obj = hashlib.md5(img_url.encode('utf-8'))
            filename = f"{task_id}_{hash_obj.hexdigest()[:8]}{ext}"
        
        # 返回完整路径
        return os.path.join(task_dir, 'images', filename)
    
    def save_page_html(self, task_dir: str, page_url: str, html_content: str) -> Optional[str]:
        """保存页面HTML内容
        
        Args:
            task_dir: 任务目录路径
            page_url: 页面URL
            html_content: HTML内容
            
        Returns:
            HTML文件保存路径
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
    
    def save_metadata(self, metadata: Dict[str, Any], task_dir: str) -> Optional[str]:
        """保存元数据
        
        Args:
            metadata: 元数据字典
            task_dir: 任务目录路径
            
        Returns:
            元数据文件保存路径
        """
        # 生成元数据文件名，保存到metadata子目录中
        metadata_dir = os.path.join(task_dir, 'metadata')
        os.makedirs(metadata_dir, exist_ok=True)  # 确保metadata目录存在
        filename = 'metadata.json'
        file_path = os.path.join(metadata_dir, filename)
        
        # 保存元数据
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            logger.info(f"元数据已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存元数据失败: {str(e)}")
            return None
    
    def load_metadata(self, task_dir: str) -> Optional[Dict[str, Any]]:
        """加载元数据
        
        Args:
            task_dir: 任务目录路径
            
        Returns:
            元数据字典
        """
        # 从metadata子目录中读取元数据文件
        metadata_dir = os.path.join(task_dir, 'metadata')
        filename = 'metadata.json'
        file_path = os.path.join(metadata_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"加载元数据失败: {str(e)}")
            return None
    
    def save_page_info(self, task_dir: str, page_info: Dict[str, Any]) -> Optional[str]:
        """保存页面信息
        
        Args:
            task_dir: 任务目录路径
            page_info: 页面信息
            
        Returns:
            页面信息文件保存路径
        """
        # 生成页面信息文件名
        filename = 'page_info.json'
        file_path = os.path.join(task_dir, 'metadata', filename)
        
        # 确保metadata目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存页面信息
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_info, f, indent=4, ensure_ascii=False)
            logger.info(f"页面信息已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存页面信息失败: {str(e)}")
            return None
    
    def save_images_csv(self, task_dir: str, images_data: List[Dict[str, Any]]) -> Optional[str]:
        """保存图片数据到CSV
        
        Args:
            task_dir: 任务目录路径
            images_data: 图片数据列表
            
        Returns:
            CSV文件保存路径
        """
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas未安装，无法保存CSV文件")
            return None
        
        # 生成CSV文件名
        filename = 'images.csv'
        file_path = os.path.join(task_dir, 'metadata', filename)
        
        # 确保metadata目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存CSV
        try:
            df = pd.DataFrame(images_data)
            df.to_csv(file_path, index=False, encoding='utf-8')
            logger.info(f"图片数据已保存到CSV: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存图片数据到CSV失败: {str(e)}")
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名，移除非法字符
        
        Args:
            name: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除非法字符
        name = re.sub(r'[\\/*?:"<>|]', '', name)
        # 将空格替换为下划线
        name = re.sub(r'\s+', '_', name)
        # 限制长度
        if len(name) > 50:
            name = name[:50]
        return name.lower()
        
    def upload_to_github(self, image_path: str) -> str:
        """上传图片到GitHub
        
        Args:
            image_path: 图片本地路径
            
        Returns:
            GitHub图片URL，上传失败则返回空字符串
        """
        logger.info(f"StorageManager: 开始处理GitHub图床上传请求")
        logger.debug(f"  - 图片路径: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"StorageManager: 图片文件不存在，无法上传")
            logger.error(f"  - 路径: {image_path}")
            return ""
        
        # 获取文件信息
        try:
            file_size = os.path.getsize(image_path)
            logger.debug(f"StorageManager: 图片文件信息 - 大小: {file_size} bytes ({file_size/1024:.2f} KB)")
        except Exception as e:
            logger.warning(f"StorageManager: 无法获取文件大小: {str(e)}")
        
        try:
            # 导入GitHub图床上传器
            logger.debug("StorageManager: 导入GitHub图床上传器")
            from crawler.utils.github_image_uploader import GitHubImageUploader
            
            # 创建GitHub图床上传器实例
            logger.debug("StorageManager: 创建GitHub图床上传器实例")
            github_uploader = GitHubImageUploader()
            
            # 检查是否配置正确
            logger.debug("StorageManager: 检查GitHub图床配置")
            if not github_uploader.is_configured():
                logger.error("StorageManager: GitHub图床未正确配置，无法上传图片")
                logger.error("  - 请检查以下配置项:")
                logger.error(f"    * enabled: {getattr(github_uploader, 'enabled', 'N/A')}")
                logger.error(f"    * token: {'已设置' if getattr(github_uploader, 'token', '') else '未设置'}")
                logger.error(f"    * repo_owner: {getattr(github_uploader, 'repo_owner', 'N/A')}")
                logger.error(f"    * repo_name: {getattr(github_uploader, 'repo_name', 'N/A')}")
                return ""
            
            logger.info("StorageManager: GitHub图床配置检查通过，开始上传")
            
            # 上传图片
            github_url = github_uploader.upload_image(image_path)
            if github_url:
                logger.info(f"StorageManager: 图片已成功上传到GitHub图床")
                logger.info(f"  - 本地路径: {image_path}")
                logger.info(f"  - GitHub URL: {github_url}")
                return github_url
            else:
                logger.error("StorageManager: GitHub图床上传失败")
                logger.error(f"  - 本地路径: {image_path}")
                logger.error("  - 可能原因: 网络问题、权限问题或GitHub服务异常")
                logger.error("  - 建议: 检查网络连接、GitHub token权限和仓库访问权限")
                return ""
        except ImportError as e:
            logger.error(f"StorageManager: 导入GitHub图床上传器失败: {str(e)}")
            logger.error("  - 请检查crawler.utils.github_image_uploader模块是否存在")
            return ""
        except Exception as e:
            logger.error(f"StorageManager: 上传图片到GitHub时发生未知错误")
            logger.error(f"  - 本地路径: {image_path}")
            logger.error(f"  - 错误信息: {str(e)}")
            logger.error(f"  - 错误类型: {type(e).__name__}")
            import traceback
            logger.debug(f"  - 错误堆栈: {traceback.format_exc()}")
            return ""