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
        # 从配置中加载GitHub图床设置，使用image_storage.github配置
        image_storage_config = crawler_config.get('image_storage', {})
        self.github_config = image_storage_config.get('github', {})
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
        logger.info(f"开始上传图片到GitHub: {image_path}")
        
        # 详细的配置检查日志
        logger.debug(f"GitHub图床配置检查:")
        logger.debug(f"  - enabled: {self.enabled}")
        logger.debug(f"  - repo_owner: {self.repo_owner}")
        logger.debug(f"  - repo_name: {self.repo_name}")
        logger.debug(f"  - branch: {self.branch}")
        logger.debug(f"  - image_path: {self.image_path}")
        logger.debug(f"  - base_url: {self.base_url}")
        logger.debug(f"  - token配置: {'已设置' if self.token else '未设置'}")
        
        if not self.enabled:
            logger.warning("GitHub图床功能未启用，无法上传图片")
            logger.debug("请在配置文件中设置 github.enabled = true")
            return ""
        
        if not self.token:
            logger.error("GitHub图床功能已启用，但未设置访问令牌(token)，无法上传图片")
            logger.error("请在配置文件中设置 github.token 或 image_storage.github.token")
            return ""
            
        if not self.repo_owner or not self.repo_name:
            logger.error("GitHub图床功能已启用，但未设置仓库信息(repo_owner/repo_name)，无法上传图片")
            logger.error(f"当前配置: repo_owner='{self.repo_owner}', repo_name='{self.repo_name}'")
            return ""
        
        if not os.path.exists(image_path):
            logger.warning(f"图片文件不存在: {image_path}")
            return ""
        
        try:
            # 读取图片文件
            logger.debug(f"开始读取图片文件: {image_path}")
            with open(image_path, 'rb') as f:
                file_content = f.read()
            
            file_size = len(file_content)
            logger.info(f"图片文件读取成功，大小: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            # 生成唯一文件名，保持与storage_manager.py中的命名一致
            file_name = os.path.basename(image_path)
            file_ext = os.path.splitext(file_name)[1]
            logger.debug(f"原始文件名: {file_name}, 扩展名: {file_ext}")
            
            # 从图片路径中提取任务ID
            # 假设图片路径格式为 .../data/task_id/images/filename
            path_parts = image_path.split(os.sep)
            task_id = None
            logger.debug(f"图片路径分析: {path_parts}")
            for i, part in enumerate(path_parts):
                if part == 'data' and i+1 < len(path_parts):
                    task_id = path_parts[i+1]
                    logger.debug(f"找到任务ID: {task_id}")
                    break
            
            # 如果找不到任务ID，则使用日期作为前缀
            if not task_id:
                date_prefix = datetime.now().strftime('%Y%m%d')
                file_hash = hashlib.md5(file_content).hexdigest()[:8]
                new_file_name = f"{date_prefix}_{file_hash}{file_ext}"
                logger.debug(f"未找到任务ID，使用日期前缀生成文件名: {new_file_name}")
            else:
                # 使用任务ID作为文件名前缀
                file_hash = hashlib.md5(file_content).hexdigest()[:8]
                new_file_name = f"{task_id}_{file_hash}{file_ext}"
                logger.debug(f"使用任务ID生成文件名: {new_file_name}")
            
            # 构建API URL
            # 确保image_path不以斜杠开头或结尾，以避免URL中出现双斜杠
            image_path_clean = self.image_path.strip('/')
            github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{image_path_clean}/{new_file_name}"
            logger.info(f"构建GitHub API URL: {github_api_url}")
            
            # 准备请求头和数据
            headers = {
                'Authorization': f'token {self.token[:8]}***',  # 只显示token前8位用于调试
                'Accept': 'application/vnd.github.v3+json'
            }
            logger.debug(f"请求头: {headers}")
            
            # 将图片内容编码为base64
            logger.debug("开始将图片内容编码为base64")
            content_base64 = base64.b64encode(file_content).decode('utf-8')
            base64_size = len(content_base64)
            logger.debug(f"base64编码完成，大小: {base64_size} 字符")
            
            # 准备请求数据
            commit_message = f'Upload image {new_file_name}'
            data = {
                'message': commit_message,
                'content': content_base64,
                'branch': self.branch
            }
            logger.debug(f"请求数据准备完成: message='{commit_message}', branch='{self.branch}', content_size={base64_size}")
            
            # 发送请求
            logger.info(f"发送PUT请求到GitHub API: {github_api_url}")
            # 准备实际请求头（包含完整token）
            actual_headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.put(github_api_url, headers=actual_headers, json=data, timeout=30)
            
            # 检查响应
            logger.info(f"收到GitHub API响应: 状态码 {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            
            if response.status_code in [201, 200]:
                # 上传成功，返回图片URL
                logger.info(f"图片上传成功! 状态码: {response.status_code}")
                
                # 解析响应内容
                try:
                    response_json = response.json()
                    logger.debug(f"响应JSON: {response_json.get('message', 'N/A')}")
                    if 'content' in response_json:
                        logger.debug(f"GitHub文件信息: sha={response_json['content'].get('sha', 'N/A')}")
                except Exception as json_error:
                    logger.warning(f"解析响应JSON失败: {json_error}")
                
                # 确保base_url以斜杠结尾，避免URL格式错误
                base_url = self.base_url if self.base_url.endswith('/') else f"{self.base_url}/"
                image_url = f"{base_url}{quote(new_file_name)}"
                logger.info(f"图片已上传到GitHub，访问URL: {image_url}")
                return image_url
            else:
                # 上传失败
                logger.error(f"上传图片到GitHub失败!")
                logger.error(f"  - 状态码: {response.status_code}")
                logger.error(f"  - 响应内容: {response.text}")
                
                # 尝试解析错误信息
                try:
                    error_json = response.json()
                    if 'message' in error_json:
                        logger.error(f"  - GitHub错误信息: {error_json['message']}")
                    if 'errors' in error_json:
                        for error in error_json['errors']:
                            logger.error(f"  - 详细错误: {error}")
                except Exception:
                    logger.error("  - 无法解析错误响应为JSON")
                
                return ""
                
        except requests.exceptions.Timeout as e:
            logger.error(f"上传图片到GitHub超时: {str(e)}")
            logger.error("请检查网络连接或增加超时时间")
            return ""
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接GitHub API失败: {str(e)}")
            logger.error("请检查网络连接和GitHub服务状态")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API请求异常: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"上传图片到GitHub时发生未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            return ""
    
    def is_configured(self):
        """检查GitHub图床是否已正确配置
        
        Returns:
            bool: 是否已正确配置
        """
        return self.enabled and self.token and self.repo_owner and self.repo_name