#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块配置
"""

import os
import json
from typing import Dict, Any

class BlogConfig:
    """博客生成配置管理器"""
    
    def __init__(self, config_file: str = None):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), '..', 'config', 'blog_config.json'
        )
        self._config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            'blog': {
                'output_dir': 'blogs',
                'drafts_dir': 'blogs/drafts',
                'published_dir': 'blogs/published',
                'template_file': 'config/templates/blog_template.md',
                'default_author': 'AI Assistant',
                'default_language': 'zh-CN',
                'auto_publish': False,
                'image_processing': {
                    'enabled': True,
                    'max_width': 800,
                    'quality': 85
                }
            },
            'ai': {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'api_key': '',
                'base_url': '',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'content': {
                'min_length': 500,
                'max_length': 3000,
                'include_images': True,
                'include_metadata': True,
                'seo_optimization': True
            }
        }
    
    def _load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                self._merge_config(self._config, file_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]):
        """合并配置"""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get(self, *keys, default=None):
        """获取配置值
        
        Args:
            *keys: 配置键路径
            default: 默认值
            
        Returns:
            配置值
        """
        current = self._config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    def set(self, *keys, value):
        """设置配置值
        
        Args:
            *keys: 配置键路径
            value: 配置值
        """
        current = self._config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

# 创建全局配置实例
blog_config = BlogConfig()