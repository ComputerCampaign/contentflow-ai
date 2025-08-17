#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Generator Module

This module provides intelligent content generation based on the Doubao model.
It generates text content from crawler data including metadata and images.
"""

__version__ = "1.0.0"
__author__ = "AI Content Generator Team"

from ai_content_generator.generator import AIContentGenerator
from ai_content_generator.content_generator import ContentGenerator
from ai_content_generator.config import AIConfig
from ai_content_generator.utils.data_loader import DataLoader, CrawlerData

__all__ = ['AIContentGenerator', 'ContentGenerator', 'AIConfig', 'DataLoader', 'CrawlerData']