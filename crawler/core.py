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
from typing import Dict, List, Optional, Any

# 导入自定义模块
from crawler.utils import StorageManager, BatchDownloader, HtmlParser, XPathManager
from crawler.utils.selenium_renderer import SeleniumRenderer
from crawler.config import crawler_config, CrawlerConfig
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class CrawlerCore:
    """网页爬虫核心类，用于抓取图片和标题信息"""
    
    def __init__(self, config: Optional[CrawlerConfig] = None, **kwargs):
        """初始化爬虫
        
        Args:
            config: 爬虫配置对象
            **kwargs: 其他配置参数，会覆盖config中的设置
        """
        # 使用传入的配置或使用全局配置实例
        self.config = config or crawler_config
        
        # 从配置中加载设置，如果kwargs提供则覆盖配置
        self.output_dir = kwargs.get('output_dir') or self.config.get('storage.output_dir', 'output')
        self.data_dir = kwargs.get('data_dir') or self.config.get('storage.base_dir', 'data')
        self.timeout = kwargs.get('timeout') or self.config.get('crawler.timeout', 30)
        self.retry = kwargs.get('retry') or self.config.get('crawler.retry', 3)
        self.use_selenium = kwargs.get('use_selenium', self.config.get('crawler.use_selenium', False))
        self.enable_xpath = kwargs.get('enable_xpath', self.config.get('crawler.enable_xpath', True))
        self.max_workers = kwargs.get('max_workers') or self.config.get('crawler.max_workers', 4)
        
        # 创建输出目录和数据目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化组件
        self.storage_manager = StorageManager(base_dir=self.data_dir)
        self.html_parser = HtmlParser()
        self.xpath_manager = XPathManager() if self.enable_xpath else None
        self.selenium_renderer = SeleniumRenderer(config=self.config) if self.use_selenium else None
        
        logger.info(f"爬虫初始化完成 - 输出目录: {self.output_dir}, 数据目录: {self.data_dir}")
        logger.info(f"配置 - 超时: {self.timeout}s, 重试: {self.retry}次, Selenium: {self.use_selenium}, XPath: {self.enable_xpath}")
        if self.xpath_manager:
            logger.info(f"XPath管理器初始化成功，启用状态: {self.xpath_manager.enabled}")
        else:
            logger.warning("XPath管理器未初始化")
    
    def crawl_url(self, url: str, task_name: Optional[str] = None, rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """爬取单个URL
        
        Args:
            url: 要爬取的URL
            task_name: 任务名称，用于创建存储目录
            rule_ids: XPath规则ID列表，用于指定使用哪些XPath规则
            
        Returns:
            爬取结果字典
        """
        logger.info(f"开始爬取URL: {url}")
        
        try:
            # 创建任务目录
            if not task_name:
                task_name = f"task_{int(time.time())}"
            
            task_dir = self.storage_manager.create_task_dir(task_name)
            
            # 获取网页内容
            html_content = self._fetch_html(url)
            if not html_content:
                return {'success': False, 'error': 'Failed to fetch HTML content'}
            
            # 保存页面源码
            html_file_path = self.storage_manager.save_page_html(task_dir, url, html_content)
            if html_file_path:
                logger.info(f"页面源码已保存: {html_file_path}")
            
            # 解析网页
            parse_result = self.html_parser.parse_html(html_content, url)
            
            # 应用XPath规则（如果启用）
            if self.xpath_manager:
                logger.info(f"开始应用XPath规则，rule_ids: {rule_ids}")
                if rule_ids:
                    # 使用指定的多个规则
                    logger.info(f"使用指定的多个规则: {rule_ids}")
                    xpath_result = self.xpath_manager.apply_multiple_rules(html_content, url, rule_ids)
                else:
                    # 使用默认的单规则或URL匹配
                    logger.info("使用默认的单规则或URL匹配")
                    xpath_result = self.xpath_manager.apply_rules(html_content, url)
                
                logger.info(f"XPath处理结果: {xpath_result is not None}")
                if xpath_result:
                    logger.info(f"XPath提取到 {len(xpath_result.get('images', []))} 张图片")
                    # 合并XPath结果
                    parse_result.update(xpath_result)
                else:
                    logger.warning("XPath规则未返回任何结果")
            else:
                logger.warning("XPath管理器未启用，跳过XPath规则应用")
            
            # 下载图片
            if parse_result.get('images'):
                downloader = BatchDownloader(
                    storage_manager=self.storage_manager,
                    timeout=self.timeout,
                    retry=self.retry,
                    max_workers=self.max_workers
                )
                
                download_result = downloader.download_images(
                    parse_result['images'],
                    url,
                    task_dir
                )
                
                parse_result['download_result'] = download_result
            
            # 保存元数据
            metadata = {
                'url': url,
                'title': parse_result.get('title', ''),
                'description': parse_result.get('description', ''),
                'images': parse_result.get('images', []),
                'comments': parse_result.get('comments', []),
                'comments_count': parse_result.get('comments_count', 0),
                'download_result': parse_result.get('download_result', {}),
                'crawl_time': time.time(),
                'task_name': task_name,
                'xpath_rule_used': parse_result.get('xpath_rule_used', None)
            }
            
            self.storage_manager.save_metadata(metadata, task_dir)
            
            logger.info(f"爬取完成 - 任务: {task_name}, 图片数量: {len(parse_result.get('images', []))}, 评论数量: {len(parse_result.get('comments', []))}")
            
            return {
                'success': True,
                'task_name': task_name,
                'task_dir': task_dir,
                'metadata': metadata,
                'result': parse_result
            }
            
        except Exception as e:
            logger.error(f"爬取URL失败: {url}, 错误: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def crawl_urls(self, urls: List[str], task_name: Optional[str] = None) -> Dict[str, Any]:
        """批量爬取多个URL
        
        Args:
            urls: URL列表
            task_name: 任务名称
            
        Returns:
            批量爬取结果
        """
        logger.info(f"开始批量爬取 {len(urls)} 个URL")
        
        if not task_name:
            task_name = f"batch_task_{int(time.time())}"
        
        results = []
        success_count = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"爬取进度: {i}/{len(urls)} - {url}")
            
            sub_task_name = f"{task_name}_url_{i}"
            result = self.crawl_url(url, sub_task_name)
            
            results.append({
                'url': url,
                'result': result
            })
            
            if result.get('success'):
                success_count += 1
            
            # 添加延迟避免过于频繁的请求
            time.sleep(1)
        
        logger.info(f"批量爬取完成 - 成功: {success_count}/{len(urls)}")
        
        return {
            'success': True,
            'task_name': task_name,
            'total_urls': len(urls),
            'success_count': success_count,
            'results': results
        }
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """获取网页HTML内容
        
        Args:
            url: 网页URL
            
        Returns:
            HTML内容字符串
        """
        for attempt in range(self.retry + 1):
            try:
                if self.use_selenium and self.selenium_renderer:
                    # 使用Selenium渲染
                    logger.debug(f"使用Selenium获取内容: {url} (尝试 {attempt + 1})")
                    success, html_content = self.selenium_renderer.render_page(url)
                    if success:
                        return html_content
                    else:
                        raise Exception(f"Selenium渲染失败: {html_content}")
                else:
                    # 使用requests获取
                    logger.debug(f"使用requests获取内容: {url} (尝试 {attempt + 1})")
                    headers = {
                        'User-Agent': self.config.get('crawler.user_agent', 
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    }
                    
                    response = requests.get(url, headers=headers, timeout=self.timeout)
                    response.raise_for_status()
                    return response.text
                    
            except Exception as e:
                logger.warning(f"获取HTML失败 (尝试 {attempt + 1}/{self.retry + 1}): {str(e)}")
                if attempt < self.retry:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"获取HTML最终失败: {url}")
        
        return None
    
    def get_task_result(self, task_name: str) -> Optional[Dict[str, Any]]:
        """获取任务结果
        
        Args:
            task_name: 任务名称
            
        Returns:
            任务结果字典
        """
        try:
            task_dir = os.path.join(self.data_dir, task_name)
            if not os.path.exists(task_dir):
                return None
            
            metadata_file = os.path.join(task_dir, 'metadata.json')
            if os.path.exists(metadata_file):
                return self.storage_manager.load_metadata(task_dir)
            
            return None
            
        except Exception as e:
            logger.error(f"获取任务结果失败: {task_name}, 错误: {str(e)}")
            return None
    
    def list_tasks(self) -> List[str]:
        """列出所有任务
        
        Returns:
            任务名称列表
        """
        try:
            if not os.path.exists(self.data_dir):
                return []
            
            tasks = []
            for item in os.listdir(self.data_dir):
                # 确保item是字符串类型
                if not isinstance(item, str):
                    continue
                item_path = os.path.join(self.data_dir, item)
                if os.path.isdir(item_path) and item.startswith('task_'):
                    tasks.append(item)
            
            return sorted(tasks)
            
        except Exception as e:
            logger.error(f"列出任务失败: {str(e)}")
            return []
    
    def cleanup_task(self, task_name: str) -> bool:
        """清理任务数据
        
        Args:
            task_name: 任务名称
            
        Returns:
            是否成功清理
        """
        try:
            task_dir = os.path.join(self.data_dir, task_name)
            if os.path.exists(task_dir):
                import shutil
                shutil.rmtree(task_dir)
                logger.info(f"任务数据已清理: {task_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"清理任务失败: {task_name}, 错误: {str(e)}")
            return False