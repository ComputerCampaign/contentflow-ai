#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import requests
import logging
import time
from urllib.parse import urlparse

# 导入自定义模块
from utils.downloader import Downloader
from utils.parser import Parser

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Crawler:
    """网页爬虫，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir="output", data_dir="data", timeout=10, retry=3, use_selenium=False):
        """初始化爬虫
        
        Args:
            output_dir (str): 输出目录（用于临时文件和日志）
            data_dir (str): 数据存储目录（用于保存图片和元数据）
            timeout (int): 请求超时时间（秒）
            retry (int): 失败重试次数
            use_selenium (bool): 是否使用Selenium
        """
        self.output_dir = output_dir
        self.data_dir = data_dir
        self.timeout = timeout
        self.retry = retry
        self.use_selenium = use_selenium
        
        # 创建输出目录和数据目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化下载器和解析器
        self.downloader = Downloader(data_dir, timeout, retry)
        self.parser = Parser()
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Selenium WebDriver
        self.driver = None
        if use_selenium:
            self._init_selenium()
    
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
            logger.error("未安装Selenium或相关依赖，请先安装: pip install selenium webdriver-manager")
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
    
    def crawl(self, url):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始爬取: {url}")
        
        # 获取URL内容
        success, content = self.fetch_url(url)
        if not success:
            logger.error(f"获取页面失败: {content}")
            return False
        
        # 解析HTML
        parsed_data = self.parser.parse_html(content, url)
        logger.info(f"解析完成，找到 {len(parsed_data['images'])} 张图片")
        
        # 导出解析结果
        self.parser.export_to_csv(parsed_data, self.data_dir)
        
        # 下载图片
        if parsed_data['images']:
            img_urls = [img['url'] for img in parsed_data['images']]
            self.downloader.download_images(img_urls, url)
        
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
    parser.add_argument("--output", default="output", help="输出目录，用于临时文件和日志（默认为'output'）")
    parser.add_argument("--data-dir", default="data", help="数据存储目录，用于保存图片和元数据（默认为'data'）")
    parser.add_argument("--use-selenium", action="store_true", help="使用Selenium和ChromeDriver进行爬取")
    parser.add_argument("--timeout", type=int, default=10, help="请求超时时间，单位为秒（默认为10秒）")
    parser.add_argument("--retry", type=int, default=3, help="失败重试次数（默认为3次）")
    
    args = parser.parse_args()
    
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
        # 开始爬取
        success = crawler.crawl(args.url)
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