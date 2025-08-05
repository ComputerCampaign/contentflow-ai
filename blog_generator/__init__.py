#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块
独立的博客生成功能模块，与爬虫和后端API服务分离
"""

from blog_generator.blog_generator import BlogGenerator, blog_generator
from blog_generator.config import blog_config
from blog_generator.utils import load_metadata, list_available_templates

__all__ = [
    'BlogGenerator',
    'blog_generator',
    'blog_config',
    'load_metadata',
    'list_available_templates'
]

__version__ = '1.0.0'