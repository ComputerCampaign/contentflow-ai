#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件，存储项目的各种配置信息
"""

import os
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
                "use_selenium": False
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
                    "type": "local",  # local, s3, oss等
                    "base_url": "http://example.com/images/",  # 图片访问的基础URL
                    "local_path": "static/images"  # 本地存储路径
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
    
    def set(self, section, key, value):
        """设置配置值
        
        Args:
            section (str): 配置节
            key (str): 配置键
            value (any): 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self):
        """保存配置到文件
        
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False

# 创建全局配置实例
config = Config()

# 导出配置实例，方便其他模块导入
__all__ = ['config']