#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import requests
import time
import json
from urllib.parse import urlparse

# 导入自定义模块
from utils import notifier
from crawler_utils import StorageManager, BatchDownloader, HtmlParser, ImageDownloader, XPathManager
from config import config

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class Crawler:
    """网页爬虫，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir=None, data_dir=None, timeout=None, retry=None, use_selenium=None, max_workers=5):
        """初始化爬虫
        
        Args:
            output_dir (str, optional): 输出目录（用于临时文件和日志）
            data_dir (str, optional): 数据存储目录（用于保存图片和元数据）
            timeout (int, optional): 请求超时时间（秒）
            retry (int, optional): 失败重试次数
            use_selenium (bool, optional): 是否使用Selenium
            max_workers (int, optional): 最大并发下载数
        """
        # 从配置中加载设置，如果参数提供则覆盖配置
        self.output_dir = output_dir or config.get('crawler', 'output_dir', 'output')
        self.data_dir = data_dir or config.get('crawler', 'data_dir', 'data')
        self.timeout = timeout or config.get('crawler', 'timeout', 10)
        self.retry = retry or config.get('crawler', 'retry', 3)
        self.use_selenium = use_selenium if use_selenium is not None else config.get('crawler', 'use_selenium', False)
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
        
        # Selenium WebDriver
        self.driver = None
        if self.use_selenium:
            self._init_selenium()
            
        logger.info(f"爬虫初始化完成，输出目录: {self.output_dir}, 数据目录: {self.data_dir}")
        logger.info(f"邮件通知: {'已启用' if notifier.enabled else '未启用'}")
        logger.info("博客生成：请在爬虫完成后使用generate_blog_from_crawler.py脚本")

    
    def _init_selenium(self):
        """初始化Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            
            # 设置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # 初始化WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Selenium WebDriver初始化成功")
            
        except ImportError:
            logger.error("未安装Selenium或相关依赖，这些依赖已包含在项目中，请使用uv sync安装所有依赖")
            sys.exit(1)
        except Exception as e:
            logger.error(f"初始化Selenium失败: {str(e)}")
            sys.exit(1)
    
    def fetch_url(self, url):
        """获取URL内容
        
        Args:
            url (str): 要爬取的URL
            
        Returns:
            tuple: (是否成功, HTML内容或错误信息)
        """
        if self.use_selenium and self.driver:
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
        """使用Selenium获取URL内容"""
        for attempt in range(self.retry + 1):
            try:
                self.driver.get(url)
                # 等待页面加载完成
                time.sleep(3)  # 简单等待，可以改用显式等待
                html_content = self.driver.page_source
                return True, html_content
            except Exception as e:
                if attempt < self.retry:
                    logger.warning(f"Selenium请求失败，重试 {attempt+1}/{self.retry}: {url}")
                    time.sleep(1)  # 等待1秒再重试
                else:
                    logger.error(f"Selenium请求失败: {url}, 错误: {str(e)}")
                    return False, str(e)
    
    def crawl(self, url, rule_id=None, task_id=None):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            task_id (str, optional): 任务ID，如果不提供则自动生成
            
        Returns:
            tuple: (是否成功, 任务ID, 任务目录) 如果使用基于任务的爬取
            bool: 是否成功 如果使用传统爬取方式
        """
        logger.info(f"开始爬取: {url}")
        
        # 如果提供了任务ID，使用基于任务的爬取方式
        if task_id is not None or config.get('crawler', 'use_task_based', False):
            return self.crawl_task_based(url, task_id, rule_id)
        
        # 否则使用传统爬取方式（保持向后兼容性）
        # 获取URL内容
        success, content = self.fetch_url(url)
        if not success:
            logger.error(f"获取页面失败: {content}")
            # 发送失败通知
            if notifier.enabled:
                notifier.send_crawler_report(url, self.data_dir, success=False)
            return False
        
        # 获取XPath规则
        xpath_selector = None
        # 初始化XPath管理器
        xpath_manager = XPathManager()
        # 如果指定了规则ID，则使用指定的规则
        if rule_id:
            rule = xpath_manager.get_rule_by_id(rule_id)
            if rule:
                xpath_selector = xpath_manager.get_xpath_selector(rule)
                logger.info(f"使用指定的XPath规则ID: {rule_id}")
            else:
                logger.warning(f"未找到指定的XPath规则ID: {rule_id}，将使用自动匹配")
        
        # 如果没有指定规则ID或指定的规则不存在，则根据URL自动匹配
        if not xpath_selector:
            rule = xpath_manager.get_rule_for_url(url)
            if rule:
                xpath_selector = xpath_manager.get_xpath_selector(rule)
                logger.info(f"根据URL自动匹配XPath规则: {rule.get('id', 'unknown')}")

        
        # 解析HTML
        if xpath_selector:
            parsed_data = self.html_parser.parse_with_xpath(content, xpath_selector, url)
        else:
            parsed_data = self.html_parser.parse_html(content, url)
        
        logger.info(f"解析完成，找到 {len(parsed_data['images'])} 张图片")
        
        # 导出解析结果
        images_csv_path = self.storage_manager.save_images_csv(self.data_dir, parsed_data['images'])
        logger.info(f"图片数据已导出到: {images_csv_path}")
        

        # 下载图片
        downloaded_images = []
        if parsed_data['images']:
            # 初始化批量下载器
            batch_downloader = BatchDownloader(self.storage_manager, self.timeout, self.retry, self.max_workers)
            # 下载图片
            downloaded_images = batch_downloader.download_images(parsed_data['images'], url, self.data_dir)
            
            # 更新解析数据中的图片信息，添加本地路径和GitHub URL
            for img_data in parsed_data['images']:
                # 查找对应的下载图片数据
                for downloaded_img in downloaded_images:
                    if img_data['url'] == downloaded_img['url']:
                        # 添加本地路径
                        if 'local_path' in downloaded_img:
                            img_data['local_path'] = downloaded_img['local_path']
                        # 添加GitHub URL
                        if 'github_url' in downloaded_img:
                            img_data['github_url'] = downloaded_img['github_url']
                        break
        
        # 保存更新后的页面信息到JSON
        try:
            page_info_path = self.storage_manager.save_page_info(self.data_dir, parsed_data)
            logger.info(f"更新后的页面信息已保存到: {page_info_path}")
        except Exception as e:
            logger.error(f"保存更新后的页面信息失败: {str(e)}")
        
        # 不再直接生成博客，改为在爬虫完成后手动运行generate_blog_from_crawler.py脚本
        logger.info("爬虫数据已保存，可以使用generate_blog_from_crawler.py脚本生成博客")
        
        # 发送邮件通知
        if notifier.enabled:
            notifier.send_crawler_report(url, self.data_dir, success=True)
        
        logger.info(f"爬取完成: {url}")
        return True
        
    def crawl_task_based(self, url, task_id=None, rule_id=None):
        """基于任务的爬取方式
        
        Args:
            url (str): 要爬取的URL
            task_id (str, optional): 任务ID，如果不提供则自动生成
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            
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
            if notifier.enabled:
                notifier.send_crawler_report(url, task_dir, success=False)
            return False, task_id, task_dir
        
        # 保存页面HTML
        html_path = self.storage_manager.save_page_html(task_dir, url, content)
        
        # 获取XPath规则
        xpath_selector = None
        # 初始化XPath管理器
        xpath_manager = XPathManager()
        # 如果指定了规则ID，则使用指定的规则
        if rule_id:
            rule = xpath_manager.get_rule_by_id(rule_id)
            if rule:
                xpath_selector = xpath_manager.get_xpath_selector(rule)
                logger.info(f"使用指定的XPath规则ID: {rule_id}")
            else:
                logger.warning(f"未找到指定的XPath规则ID: {rule_id}，将使用自动匹配")
        
        # 如果没有指定规则ID或指定的规则不存在，则根据URL自动匹配
        if not xpath_selector:
            rule = xpath_manager.get_rule_for_url(url)
            if rule:
                xpath_selector = xpath_manager.get_xpath_selector(rule)
                logger.info(f"根据URL自动匹配XPath规则: {rule.get('id', 'unknown')}")
        
        # 解析HTML
        if xpath_selector:
            parsed_data = self.html_parser.parse_with_xpath(content, xpath_selector, url)
        else:
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
        
        # 不再直接生成博客，改为在爬虫完成后手动运行generate_blog_from_crawler.py脚本
        logger.info(f"爬虫任务完成，数据已保存到: {task_dir}")
        logger.info("可以使用generate_blog_from_crawler.py脚本生成博客，例如:")
        logger.info(f"python generate_blog_from_crawler.py --task-dir {task_dir}")
        
        # 发送邮件通知
        if notifier.enabled:
            notifier.send_crawler_report(url, task_dir, success=True)
        
        logger.info(f"爬取完成: {url}")
        return True, task_id, task_dir
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver已关闭")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页图片和标题爬虫")
    parser.add_argument("--url", help="要爬取的网页URL")
    parser.add_argument("--task-id", help="任务ID，如果不提供则自动生成")
    parser.add_argument("--output", help="输出目录，用于临时文件和日志（默认使用配置文件设置）")
    parser.add_argument("--data-dir", help="数据存储目录，用于保存图片和元数据（默认使用配置文件设置）")
    parser.add_argument("--use-selenium", action="store_true", help="使用Selenium和ChromeDriver进行爬取")
    parser.add_argument("--timeout", type=int, help="请求超时时间，单位为秒（默认使用配置文件设置）")
    parser.add_argument("--retry", type=int, help="失败重试次数（默认使用配置文件设置）")
    parser.add_argument("--config", help="配置文件路径（默认为'config.json'）")
    parser.add_argument("--enable-email", action="store_true", help="启用邮件通知")
    parser.add_argument("--disable-email", action="store_true", help="禁用邮件通知")
    # 博客生成现在通过独立脚本generate_blog_from_crawler.py完成
    parser.add_argument("--rule-id", help="XPath规则ID，用于指定使用哪个XPath规则（例如：reddit_media, twitter_media, general_article）")
    parser.add_argument("--list-rules", action="store_true", help="列出所有可用的XPath规则")
    
    args = parser.parse_args()
    
    # 加载配置文件
    if args.config:
        config.__init__(args.config)
    
    # 处理邮件通知和博客生成的命令行开关
    if args.enable_email:
        config.set('email', 'enabled', True)
    elif args.disable_email:
        config.set('email', 'enabled', False)
    
    # 博客生成现在通过独立脚本generate_blog_from_crawler.py完成
    
    # 保存配置更改
    config.save()
    
    # 如果指定了列出规则
    if args.list_rules:
        # 从正确的模块导入XPathManager
        from crawler_utils.xpath_manager import XPathManager
        # 创建XPathManager实例并调用list_rules方法
        xpath_manager = XPathManager()
        print(xpath_manager.list_rules())
        sys.exit(0)
    
    # 检查是否提供了URL
    if not args.url:
        logger.error("未提供URL，请使用--url参数指定要爬取的网页URL")
        parser.print_help()
        sys.exit(1)
        
    # 验证URL
    try:
        result = urlparse(args.url)
        if not all([result.scheme, result.netloc]):
            logger.error(f"无效的URL: {args.url}")
            sys.exit(1)
    except Exception:
        logger.error(f"无效的URL: {args.url}")
        sys.exit(1)
    
    # 创建爬虫实例
    crawler = Crawler(
        output_dir=args.output,
        data_dir=args.data_dir,
        timeout=args.timeout,
        retry=args.retry,
        use_selenium=args.use_selenium
    )
    
    try:
        # 开始爬取，传入规则ID和任务ID
        success = crawler.crawl(args.url, args.rule_id, args.task_id)
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
    except Exception as e:
        logger.exception(f"爬取过程中发生错误: {str(e)}")
        sys.exit(1)
    finally:
        # 关闭资源
        crawler.close()

if __name__ == "__main__":
    main()