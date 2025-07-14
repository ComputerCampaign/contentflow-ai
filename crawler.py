#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import requests
import logging
import time
import json
from urllib.parse import urlparse

# 导入自定义模块
from utils import Downloader, Parser, notifier, blog_generator, xpath_manager
from config import config

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Crawler:
    """网页爬虫，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir=None, data_dir=None, timeout=None, retry=None, use_selenium=None):
        """初始化爬虫
        
        Args:
            output_dir (str, optional): 输出目录（用于临时文件和日志）
            data_dir (str, optional): 数据存储目录（用于保存图片和元数据）
            timeout (int, optional): 请求超时时间（秒）
            retry (int, optional): 失败重试次数
            use_selenium (bool, optional): 是否使用Selenium
        """
        # 从配置中加载设置，如果参数提供则覆盖配置
        self.output_dir = output_dir or config.get('crawler', 'output_dir', 'output')
        self.data_dir = data_dir or config.get('crawler', 'data_dir', 'data')
        self.timeout = timeout or config.get('crawler', 'timeout', 10)
        self.retry = retry or config.get('crawler', 'retry', 3)
        self.use_selenium = use_selenium if use_selenium is not None else config.get('crawler', 'use_selenium', False)
        
        # 创建输出目录和数据目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化下载器和解析器
        self.downloader = Downloader(self.data_dir, self.timeout, self.retry)
        self.parser = Parser()
        
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
        logger.info(f"博客生成: {'已启用' if blog_generator.enabled else '未启用'}")

    
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
    
    def crawl(self, url, rule_id=None):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始爬取: {url}")
        
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
        if 'xpath_manager' in dir(utils):
            # 如果指定了规则ID，则使用指定的规则
            if rule_id:
                xpath_selector = utils.xpath_manager.get_xpath_by_id(rule_id)
                if xpath_selector:
                    logger.info(f"使用指定的XPath规则ID: {rule_id}")
                else:
                    logger.warning(f"未找到指定的XPath规则ID: {rule_id}，将使用自动匹配")
            
            # 如果没有指定规则ID或指定的规则不存在，则根据URL自动匹配
            if not xpath_selector:
                xpath_selector = utils.xpath_manager.get_xpath_by_url(url)
                if xpath_selector:
                    logger.info(f"根据URL自动匹配XPath规则: {xpath_selector}")
        
        # 解析HTML
        if xpath_selector:
            parsed_data = self.parser.parse_with_xpath(content, xpath_selector, url)
        else:
            parsed_data = self.parser.parse_html(content, url)
        
        logger.info(f"解析完成，找到 {len(parsed_data['images'])} 张图片")
        
        # 导出解析结果
        self.parser.export_to_csv(parsed_data, self.data_dir)
        
        # 保存页面信息到JSON
        try:
            page_info_path = os.path.join(self.data_dir, 'page_info.json')
            with open(page_info_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=4, ensure_ascii=False)
            logger.info(f"页面信息已保存到: {page_info_path}")
        except Exception as e:
            logger.error(f"保存页面信息失败: {str(e)}")
        
        # 下载图片
        downloaded_images = []
        if parsed_data['images']:
            img_urls = [img['url'] for img in parsed_data['images']]
            downloaded_images = self.downloader.download_images(img_urls, url)
        
        # 生成博客
        if blog_generator.enabled:
            blog_success, blog_path = blog_generator.generate_blog(url, content, parsed_data, self.data_dir)
            if blog_success:
                logger.info(f"博客已生成: {blog_path}")
            else:
                logger.warning("博客生成失败")
        
        # 发送邮件通知
        if notifier.enabled:
            notifier.send_crawler_report(url, self.data_dir, success=True)
        
        logger.info(f"爬取完成: {url}")
        return True
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver已关闭")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页图片和标题爬虫")
    parser.add_argument("--url", required=True, help="要爬取的网页URL")
    parser.add_argument("--output", help="输出目录，用于临时文件和日志（默认使用配置文件设置）")
    parser.add_argument("--data-dir", help="数据存储目录，用于保存图片和元数据（默认使用配置文件设置）")
    parser.add_argument("--use-selenium", action="store_true", help="使用Selenium和ChromeDriver进行爬取")
    parser.add_argument("--timeout", type=int, help="请求超时时间，单位为秒（默认使用配置文件设置）")
    parser.add_argument("--retry", type=int, help="失败重试次数（默认使用配置文件设置）")
    parser.add_argument("--config", help="配置文件路径（默认为'config.json'）")
    parser.add_argument("--enable-email", action="store_true", help="启用邮件通知")
    parser.add_argument("--disable-email", action="store_true", help="禁用邮件通知")
    parser.add_argument("--enable-blog", action="store_true", help="启用博客生成")
    parser.add_argument("--disable-blog", action="store_true", help="禁用博客生成")
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
    
    if args.enable_blog:
        config.set('blog', 'enabled', True)
    elif args.disable_blog:
        config.set('blog', 'enabled', False)
    
    # 保存配置更改
    config.save()
    
    # 如果指定了列出规则
    if args.list_rules:
        from utils.xpath_manager import list_rules
        print(list_rules())
        sys.exit(0)
    
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
        # 开始爬取，传入规则ID
        success = crawler.crawl(args.url, args.rule_id)
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