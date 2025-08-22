#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型包
"""

from backend.models.user import User
from backend.models.task import Task, TaskExecution
from backend.models.crawler import CrawlerConfig, CrawlerResult
from backend.models.xpath import XPathConfig
from backend.models.ai_content import AIContentConfig
from backend.models.ai_model import AIModelConfig
from backend.models.dashboard import Dashboard

__all__ = ['User', 'Task', 'TaskExecution', 'CrawlerConfig', 'CrawlerResult', 'XPathConfig', 'AIContentConfig', 'AIModelConfig', 'Dashboard']