#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成器模块
包含多平台文案生成器和视频生成器
"""

from .multi_platform_generator import MultiPlatformGenerator
from .video_generator import VideoGenerator

__all__ = [
    'MultiPlatformGenerator',
    'VideoGenerator'
]