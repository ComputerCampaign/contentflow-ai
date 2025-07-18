#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件，存储项目的各种配置信息
"""

import os
import json
import logging
from os import environ

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(console_handler)

# 尝试加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    # 加载.env文件中的环境变量
    load_dotenv()
    logger.info("已加载.env文件中的环境变量")
except ImportError:
    logger.warning("未安装python-dotenv库，无法从.env文件加载环境变量。该库已包含在项目依赖中，请使用uv sync安装所有依赖")

class Config:
    """配置类，用于管理项目的各种配置"""
    
    # 默认配置文件路径
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    def __init__(self, config_path=None):
        """初始化配置
        
        Args:
            config_path (str, optional): 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件
        
        Returns:
            dict: 配置字典
        """
        # 默认配置
        default_config = {
            # 爬虫配置
            "crawler": {
                "output_dir": "output",
                "data_dir": "data",
                "timeout": 10,
                "retry": 3,
                "use_selenium": False,
                "selenium_config": {
                    "headless": True,
                    "proxy": None,
                    "page_load_wait": 6,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "disable_gpu": True,
                    "no_sandbox": True,
                    "disable_dev_shm_usage": True,
                    "window_size": "1920,1080"
                }
            },
            # 邮件配置
            "email": {
                "enabled": False,
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "sender_email": "your_email@example.com",
                "sender_password": "",  # 不建议在配置文件中存储密码，可以使用环境变量
                "receiver_emails": ["receiver@example.com"],
                "subject_prefix": "[爬虫通知] "
            },
            # 博客配置
            "blog": {
                "enabled": False,
                "template_path": "templates/blog_template.md",
                "output_path": "blogs",
                "image_storage": {
                    "type": "github"  # 只支持github图床
                }
            }
        }
        
        # 如果配置文件存在，则加载
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并用户配置和默认配置
                self._merge_config(default_config, user_config)
                logger.info(f"已加载配置文件: {self.config_path}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}，将使用默认配置")
        else:
            logger.warning(f"配置文件不存在: {self.config_path}，将使用默认配置")
            # 创建默认配置文件
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已创建默认配置文件: {self.config_path}")
            except Exception as e:
                logger.error(f"创建默认配置文件失败: {str(e)}")
        
        # 从环境变量加载敏感信息
        self._load_from_environment(default_config)
        
        return default_config
    
    def _merge_config(self, default_config, user_config):
        """递归合并配置
        
        Args:
            default_config (dict): 默认配置
            user_config (dict): 用户配置
        """
        for key, value in user_config.items():
            if key in default_config:
                if isinstance(value, dict) and isinstance(default_config[key], dict):
                    self._merge_config(default_config[key], value)
                else:
                    default_config[key] = value
            else:
                default_config[key] = value
    
    def _load_from_environment(self, config):
        """从环境变量加载敏感信息
        
        环境变量命名规则：
        - CRAWLER_EMAIL_PASSWORD: 邮件密码
        - CRAWLER_GITHUB_TOKEN: GitHub令牌
        
        Args:
            config (dict): 配置字典
        """
        # 加载邮件密码
        email_password = environ.get('CRAWLER_EMAIL_PASSWORD')
        if email_password:
            config['email']['sender_password'] = email_password
            logger.info("已从环境变量加载邮件密码")
        
        # 加载GitHub令牌
        github_token = environ.get('CRAWLER_GITHUB_TOKEN')
        if github_token and 'crawler' in config and 'image_storage' in config['crawler'] and 'github' in config['crawler']['image_storage']:
            config['crawler']['image_storage']['github']['token'] = github_token
            logger.info("已从环境变量加载GitHub令牌")
        
        # 可以根据需要添加更多敏感信息的加载
    
    def get(self, section, key=None, default=None):
        """获取配置值
        
        Args:
            section (str): 配置节
            key (str, optional): 配置键，如果为None则返回整个节
            default (any, optional): 默认值，如果配置不存在则返回此值
            
        Returns:
            any: 配置值
        """
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key, default)
    
    def set(self, section, key, sub_key=None, value=None):
        """设置配置值
        
        Args:
            section (str): 配置节
            key (str): 配置键
            sub_key (str, optional): 子配置键，用于嵌套配置
            value (any): 配置值，如果sub_key为None，则value为key对应的值
        """
        if section not in self.config:
            self.config[section] = {}
        
        if sub_key is None:
            self.config[section][key] = value
        else:
            if key not in self.config[section]:
                self.config[section][key] = {}
            self.config[section][key][sub_key] = value

# 创建全局配置实例
config = Config()

# 导出配置实例，方便其他模块导入
__all__ = ['config']