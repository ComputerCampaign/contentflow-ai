#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫模块配置
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class CrawlerConfig:
    """
    爬虫配置管理类
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 'config.json'
        )
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        # 加载.env文件中的环境变量
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        load_dotenv(env_path)
        default_config = {
            "crawler": {
                "timeout": 30,
                "retry": 3,
                "max_workers": 4,
                "use_selenium": False,
                "enable_xpath": True,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "storage": {
                "base_dir": "data",
                "output_dir": "output",
                "logs_dir": "logs"
            },

            "selenium": {
                "headless": True,
                "disable_gpu": True,
                "disable_dev_shm_usage": True,
                "window_size": "1920,1080",
                "page_load_timeout": 30,
                "implicit_wait": 10
            },
            "xpath": {
                "enabled": True,
                "rules_path": "crawler/config/xpath/xpath_rules.json",
                "default_rule_id": "general_article"
            },
            "scripts": {
                "stealth_path": "crawler/config/scripts/stealth.min.js"
            },
            "image_storage": {
                "type": "github",
                "github": {
                    "enabled": True,
                    "repo_owner": "ComputerCampaign",
                    "repo_name": "material_warehouse",
                    "branch": "main",
                    "token": "",
                    "image_path": "images",
                    "base_url": "https://raw.githubusercontent.com/ComputerCampaign/material_warehouse/main/images/"
                }
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # 合并配置
                    self._merge_config(default_config, file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")
        
        # 从环境变量加载配置，覆盖空值
        self._load_env_config(default_config)
        
        return default_config
    
    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]):
        """
        递归合并配置
        
        Args:
            default: 默认配置
            override: 覆盖配置
        """
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def _load_env_config(self, config: Dict[str, Any]):
        """
        从环境变量加载配置，覆盖空值
        
        Args:
            config: 配置字典
        """
        # 加载GitHub token
        github_token = os.getenv('CRAWLER_GITHUB_TOKEN')
        if github_token:
            # 覆盖image_storage.github.token配置
            if 'image_storage' in config and 'github' in config['image_storage']:
                if not config['image_storage']['github'].get('token'):
                    config['image_storage']['github']['token'] = github_token
                    print(f"Info: GitHub token loaded from environment variable (token: {github_token[:8]}...)")
                else:
                    print(f"Info: GitHub token already set in config file, skipping environment variable")
        else:
            print("Warning: CRAWLER_GITHUB_TOKEN environment variable not found")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """
        保存配置到文件
        """
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def crawler(self) -> Dict[str, Any]:
        """爬虫配置"""
        return self._config.get('crawler', {})
    
    @property
    def storage(self) -> Dict[str, Any]:
        """存储配置"""
        return self._config.get('storage', {})
    

    
    @property
    def selenium(self) -> Dict[str, Any]:
        """Selenium配置"""
        return self._config.get('selenium', {})
    
    @property
    def xpath(self) -> Dict[str, Any]:
        """XPath配置"""
        return self._config.get('xpath', {})
    
    @property
    def scripts(self) -> Dict[str, Any]:
        """脚本配置"""
        return self._config.get('scripts', {})
    
    @property
    def image_storage(self) -> Dict[str, Any]:
        """图片存储配置"""
        return self._config.get('image_storage', {})

# 全局配置实例
crawler_config = CrawlerConfig()