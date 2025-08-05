#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块工具包
"""

from blog_generator.utils.generate_blog import BlogGenerator, load_metadata, list_available_templates

__all__ = [
    'BlogGenerator',
    'load_metadata',
    'list_available_templates'
]

__version__ = '1.0.0'