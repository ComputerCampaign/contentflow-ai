#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容生成模块
支持多平台文案生成和图片转视频功能
"""

# 导入生成器模块
from .generators import MultiPlatformGenerator, VideoGenerator

# 导入管理器模块
from .managers import ConfigManager, FileManager, PromptManager

# 导入工作流模块
from .workflows import WorkflowOrchestrator

__version__ = "2.0.0"

__all__ = [
    'ConfigManager',
    'FileManager',
    'MultiPlatformGenerator',
    'PromptManager',
    'VideoGenerator',
    'WorkflowOrchestrator'
]