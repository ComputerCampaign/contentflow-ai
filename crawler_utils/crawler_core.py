#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫核心模块，提供网页爬取的核心功能
"""

import os
import sys
import requests
import time
from urllib.parse import urlparse

# 导入自定义模块
from crawler_utils import StorageManager, BatchDownloader, HtmlParser, XPathManager
from crawler_utils.selenium_renderer import SeleniumRenderer

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class CrawlerCore:
    """网页爬虫核心类，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir=None, data_dir=None, timeout=None, retry=None, use_selenium=None, enable_xpath=None, max_workers=None, config=None):
        """初始化爬虫
        
        Args:
            output_dir (str, optional): 输出目录（用于临时文件和日志）
            data_dir (str, optional): 数据存储目录（用于保存图片和元数据）
            timeout (int, optional): 请求超时时间（秒）
            retry (int, optional): 失败重试次数
            use_selenium (bool, optional): 是否使用Selenium
            enable_xpath (bool, optional): 是否启用XPath选择器
            max_workers (int, optional): 最大并发下载数
            config (object, optional): 配置对象
        """
        # 保存配置对象
        self.config = config
        
        # 从配置中加载设置，如果参数提供则覆盖配置
        self.output_dir = output_dir or config.get('crawler', 'output_dir', 'output')
        self.data_dir = data_dir or config.get('crawler', 'data_dir', 'data')
        self.timeout = timeout or config.get('crawler', 'timeout', 10)
        self.retry = retry or config.get('crawler', 'retry', 3)
        self.use_selenium = use_selenium if use_selenium is not None else config.get('crawler', 'use_selenium', False)
        self.enable_xpath = enable_xpath if enable_xpath is not None else config.get('crawler', 'xpath_config', {}).get('enabled', False)
        self.max_workers = max_workers
        
        # 创建输出目录和数据目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化存储管理器
        self.storage_manager = StorageManager(self.data_dir)
        
        # 初始化解析器
        self.html_parser = HtmlParser()
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Selenium 渲染器
        self.renderer = None
        if self.use_selenium:
            self._init_selenium()
            
        logger.info(f"爬虫核心初始化完成，输出目录: {self.output_dir}, 数据目录: {self.data_dir}")

    
    def _init_selenium(self):
        """初始化Selenium渲染器"""
        try:
            # 从配置中获取Selenium相关设置
            selenium_config = self.config.get('crawler', 'selenium_config', {})
            headless = selenium_config.get('headless', True)
            proxy = selenium_config.get('proxy', None)
            page_load_wait = selenium_config.get('page_load_wait', 6)
            
            # 初始化SeleniumRenderer
            self.renderer = SeleniumRenderer(
                config=self.config,
                headless=headless,
                proxy=proxy,
                timeout=self.timeout,
                page_load_wait=page_load_wait,
                retry=self.retry
            )
            logger.info("Selenium渲染器初始化成功")
            
        except ImportError:
            logger.error("未安装Selenium或相关依赖，这些依赖已包含在项目中，请使用uv sync安装所有依赖")
            sys.exit(1)
        except Exception as e:
            logger.error(f"初始化Selenium渲染器失败: {str(e)}")
            sys.exit(1)
    
    def fetch_url(self, url):
        """获取URL内容
        
        Args:
            url (str): 要爬取的URL
            
        Returns:
            tuple: (是否成功, HTML内容或错误信息)
        """
        if self.use_selenium and self.renderer:
            return self._fetch_with_selenium(url)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url):
        """使用requests获取URL内容"""
        for attempt in range(self.retry + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return True, response.text
            except requests.exceptions.RequestException as e:
                if attempt < self.retry:
                    logger.warning(f"请求失败，重试 {attempt+1}/{self.retry}: {url}")
                    time.sleep(1)  # 等待1秒再重试
                else:
                    logger.error(f"请求失败: {url}, 错误: {str(e)}")
                    return False, str(e)
    
    def _fetch_with_selenium(self, url):
        """使用Selenium渲染器获取URL内容"""
        return self.renderer.render_page(url)
    
    def crawl(self, url, rule_id=None, task_id=None, notifier=None):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            task_id (str, optional): 任务ID，如果不提供则自动生成
            notifier (object, optional): 通知器对象，用于发送通知
            
        Returns:
            tuple: (是否成功, 任务ID, 任务目录)
        """
        logger.info(f"开始爬取: {url}")
        return self.crawl_task_based(url, task_id, rule_id, notifier)
        
    def crawl_task_based(self, url, task_id=None, rule_id=None, notifier=None):
        """基于任务的爬取方式
        
        Args:
            url (str): 要爬取的URL
            task_id (str, optional): 任务ID，如果不提供则自动生成
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            notifier (object, optional): 通知器对象，用于发送通知
            
        Returns:
            tuple: (是否成功, 任务ID, 任务目录)
        """
        # 创建任务目录
        task_id, task_dir = self.storage_manager.create_task_directory(task_id, url)
        logger.info(f"任务ID: {task_id}, 任务目录: {task_dir}")
        
        # 获取URL内容
        success, content = self.fetch_url(url)
        if not success:
            logger.error(f"获取页面失败: {content}")
            # 发送失败通知
            if notifier and hasattr(notifier, 'enabled') and notifier.enabled:
                notifier.send_crawler_report(url, task_dir, success=False)
            return False, task_id, task_dir
        
        # 保存页面HTML
        html_path = self.storage_manager.save_page_html(task_dir, url, content)
        
        # 获取XPath规则
        xpath_selector = None
        parsed_data = None
        
        # 如果启用XPath选择器，则使用XPath解析页面
        if self.enable_xpath:
            # 初始化XPath管理器
            xpath_manager = XPathManager()
            # 如果指定了规则ID，则使用指定的规则
            if rule_id:
                rule = xpath_manager.get_rule_by_id(rule_id)
                if rule:
                    xpath_selector = xpath_manager.get_xpath_selector(rule)
                    logger.info(f"使用指定的XPath规则ID: {rule_id}")
                else:
                    logger.warning(f"未找到指定的XPath规则ID: {rule_id}")
            
            # 如果没有指定规则ID或指定的规则不存在，则使用默认规则
            if not xpath_selector:
                default_rule = xpath_manager.get_rule_by_id(xpath_manager.default_rule_id)
                if default_rule:
                    xpath_selector = xpath_manager.get_xpath_selector(default_rule)
                    logger.info(f"使用默认XPath规则: {xpath_manager.default_rule_id}")
            
            # 解析HTML
            if xpath_selector:
                parsed_data = self.html_parser.parse_with_xpath(content, xpath_selector, url)
            else:
                parsed_data = self.html_parser.parse_html(content, url)
        else:
            logger.info("已禁用XPath选择器，将使用BeautifulSoup解析整个页面")
            parsed_data = self.html_parser.parse_html(content, url)
        
        logger.info(f"解析完成，找到 {len(parsed_data['images'])} 张图片")
        
        # 保存页面信息到JSON
        page_info_path = self.storage_manager.save_page_info(task_dir, parsed_data)
        
        # 下载图片
        if parsed_data['images']:
            # 初始化批量下载器
            batch_downloader = BatchDownloader(
                self.storage_manager,
                self.timeout,
                self.retry,
                self.max_workers
            )
            
            # 下载图片
            downloaded_images = batch_downloader.download_images(
                parsed_data['images'],
                url,
                task_dir
            )
            
            # 更新图片数据
            parsed_data['images'] = downloaded_images
            
            # 保存更新后的页面信息
            self.storage_manager.save_page_info(task_dir, parsed_data)
            
            # 导出图片数据到CSV
            if downloaded_images:
                self.storage_manager.save_images_csv(task_dir, downloaded_images)
        
        logger.info(f"爬虫任务完成，数据已保存到: {task_dir}")
        logger.info("可以使用generate_blog_from_crawler.py脚本生成博客，例如:")
        logger.info(f"python generate_blog_from_crawler.py --task-dir {task_dir}")
        
        # 发送邮件通知
        if notifier and hasattr(notifier, 'enabled') and notifier.enabled:
            notifier.send_crawler_report(url, task_dir, success=True)
        
        logger.info(f"爬取完成: {url}")
        return True, task_id, task_dir
    
    def close(self):
        """关闭资源"""
        if hasattr(self, 'renderer'):
            self.renderer.close()
            logger.info("Selenium渲染器已关闭")