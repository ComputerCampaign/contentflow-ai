#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型包
"""

from backend.models.user import User
from backend.models.task import Task
from backend.models.crawler_configs import CrawlerConfig
from backend.models.crawler_result import CrawlerResult
from backend.models.xpath import XPathConfig
from backend.models.ai_content import AIContentConfig
from backend.models.ai_model import AIModelConfig
from backend.models.prompt import PromptConfig
from backend.models.dashboard import Dashboard

__all__ = ['User', 'Task', 'CrawlerConfig', 'CrawlerResult', 'XPathConfig', 'AIContentConfig', 'AIModelConfig', 'PromptConfig', 'Dashboard']