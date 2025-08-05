#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
独立爬虫模块
"""

from crawler.core import CrawlerCore
from crawler.utils.storage_manager import StorageManager
from crawler.utils.batch_downloader import BatchDownloader
from crawler.utils.html_parser import HtmlParser
from crawler.utils.xpath_manager import XPathManager
from crawler.utils.image_downloader import ImageDownloader
from crawler.utils.github_image_uploader import GitHubImageUploader
from crawler.utils.selenium_renderer import SeleniumRenderer
from crawler.config import crawler_config

__all__ = [
    'CrawlerCore',
    'StorageManager',
    'BatchDownloader',
    'HtmlParser',
    'XPathManager',
    'ImageDownloader',
    'GitHubImageUploader',
    'SeleniumRenderer',
    'crawler_config'
]

__version__ = '1.0.0'