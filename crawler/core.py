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
            
            # 初始化解析结果
            parse_result = {
                'title': '',
                'description': '',
                'images': [],
                'texts': [],
                'links': [],
                'elements': [],
                'comments': [],
                'comments_count': 0
            }
            
            # 应用XPath规则（如果启用）
            if self.xpath_manager and self.xpath_manager.is_enabled():
                logger.info(f"开始应用XPath规则，rule_ids: {rule_ids}")
                
                # 获取要应用的规则列表
                rules_to_apply = self.xpath_manager.get_rules_for_url(url, rule_ids)
                
                if rules_to_apply:
                    logger.info(f"找到 {len(rules_to_apply)} 个XPath规则")
                    
                    # 应用每个规则并合并结果
                    xpath_result = self._apply_xpath_rules(html_content, rules_to_apply, url)
                    
                    if xpath_result:
                        logger.info(f"XPath提取到 {len(xpath_result.get('images', []))} 张图片, {len(xpath_result.get('texts', []))} 个文本, {len(xpath_result.get('links', []))} 个链接")
                        # 合并XPath结果
                        self._merge_xpath_results(parse_result, xpath_result)
                    else:
                        logger.warning("XPath规则未返回任何结果")
                else:
                    logger.warning("未找到可应用的XPath规则")
            else:
                logger.warning("XPath管理器未启用或无可用规则，跳过XPath规则应用")
            
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
                'texts': parse_result.get('texts', []),
                'links': parse_result.get('links', []),
                'elements': parse_result.get('elements', []),
                'comments': parse_result.get('comments', []),
                'comments_count': parse_result.get('comments_count', 0),
                'download_result': parse_result.get('download_result', {}),
                'crawl_time': time.time(),
                'task_name': task_name,
                'xpath_rules_used': parse_result.get('xpath_rules_used', [])
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
    
    def _apply_xpath_rules(self, html_content, rules, url):
        """应用XPath规则列表并合并结果
        
        Args:
            html_content (str): HTML内容
            rules (list): XPath规则列表
            url (str): 页面URL
            
        Returns:
            dict: 合并后的解析结果
        """
        combined_result = {
            'images': [],
            'texts': [],
            'links': [],
            'elements': [],
            'comments': [],
            'xpath_rules_used': []
        }
        
        for rule in rules:
            try:
                logger.info(f"应用XPath规则: {rule.get('name', 'Unknown')} ({rule.get('id', 'unknown')})")
                
                # 使用html_parser的新方法处理规则
                rule_result = self.html_parser.extract_by_xpath_rule(html_content, rule, url)
                
                if rule_result:
                    # 获取元数据
                    meta = rule_result.get('_meta', {})
                    rule_id = meta.get('rule_id') or rule.get('id', 'unknown')
                    rule_type = meta.get('rule_type', 'general')
                    field_name = meta.get('field_name', 'unknown')
                    
                    # 获取实际数据（排除_meta）
                    data_key = field_name
                    extracted_data = rule_result.get(data_key, [])
                    
                    # 根据规则类型合并数据
                    if rule_type == 'image' and isinstance(extracted_data, list):
                        self._merge_unique_images(combined_result['images'], extracted_data)
                    elif rule_type == 'text' and isinstance(extracted_data, list):
                        combined_result['texts'].extend(extracted_data)
                    elif rule_type == 'link' and isinstance(extracted_data, list):
                        self._merge_unique_links(combined_result['links'], extracted_data)
                    elif rule_type == 'general' and isinstance(extracted_data, dict):
                        # 通用类型返回的是包含所有类型的字典
                        self._merge_unique_images(combined_result['images'], extracted_data.get('images', []))
                        combined_result['texts'].extend(extracted_data.get('texts', []))
                        self._merge_unique_links(combined_result['links'], extracted_data.get('links', []))
                        combined_result['elements'].extend(extracted_data.get('elements', []))
                    else:
                        # 其他情况，将数据添加到elements中
                        if isinstance(extracted_data, list):
                            combined_result['elements'].extend(extracted_data)
                        else:
                            combined_result['elements'].append(extracted_data)
                    
                    # 记录使用的规则
                    if rule_id not in combined_result['xpath_rules_used']:
                        combined_result['xpath_rules_used'].append(rule_id)
                
            except Exception as e:
                logger.error(f"应用XPath规则失败: {rule.get('id', 'unknown')}, 错误: {str(e)}")
                continue
        
        # 将文本结果转换为评论格式以保持兼容性
        for text_item in combined_result['texts']:
            if text_item.get('text'):
                combined_result['comments'].append({
                    'text': text_item['text'],
                    'author': 'Unknown',
                    'timestamp': None,
                    'xpath_rule': 'text_extraction'
                })
        
        combined_result['comments_count'] = len(combined_result['comments'])
        
        return combined_result if any(combined_result[key] for key in ['images', 'texts', 'links', 'elements']) else None
    
    def _merge_xpath_results(self, parse_result, xpath_result):
        """将XPath结果合并到解析结果中
        
        Args:
            parse_result (dict): 原始解析结果
            xpath_result (dict): XPath解析结果
        """
        # 合并图片（去重）
        self._merge_unique_images(parse_result['images'], xpath_result.get('images', []))
        
        # 合并文本
        parse_result['texts'].extend(xpath_result.get('texts', []))
        
        # 合并链接（去重）
        self._merge_unique_links(parse_result['links'], xpath_result.get('links', []))
        
        # 合并通用元素
        parse_result['elements'].extend(xpath_result.get('elements', []))
        
        # 合并评论
        parse_result['comments'].extend(xpath_result.get('comments', []))
        
        # 更新评论数量
        parse_result['comments_count'] = len(parse_result['comments'])
        
        # 记录使用的XPath规则
        if xpath_result.get('xpath_rules_used'):
            parse_result['xpath_rules_used'] = xpath_result['xpath_rules_used']
    
    def _merge_unique_images(self, existing_images, new_images):
        """合并图片列表，避免重复
        
        Args:
            existing_images (list): 现有图片列表
            new_images (list): 新图片列表
        """
        existing_urls = {img['url'] for img in existing_images}
        for img in new_images:
            if img['url'] not in existing_urls:
                existing_images.append(img)
                existing_urls.add(img['url'])
    
    def _merge_unique_links(self, existing_links, new_links):
        """合并链接列表，避免重复
        
        Args:
            existing_links (list): 现有链接列表
            new_links (list): 新链接列表
        """
        existing_urls = {link['url'] for link in existing_links}
        for link in new_links:
            if link['url'] not in existing_urls:
                existing_links.append(link)
                existing_urls.add(link['url'])
    
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