#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
from urllib.parse import urlparse

# 导入自定义模块
from utils import notifier
from crawler_utils import XPathManager
from crawler_utils.crawler_core import CrawlerCore
from config import config

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class Crawler:
    """网页爬虫，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir=None, data_dir=None, timeout=None, retry=None, use_selenium=None, enable_xpath=None, max_workers=None):
        """初始化爬虫
        
        Args:
            output_dir (str, optional): 输出目录（用于临时文件和日志）
            data_dir (str, optional): 数据存储目录（用于保存图片和元数据）
            timeout (int, optional): 请求超时时间（秒）
            retry (int, optional): 失败重试次数
            use_selenium (bool, optional): 是否使用Selenium
            enable_xpath (bool, optional): 是否启用XPath选择器
            max_workers (int, optional): 最大并发下载数
        """
        # 初始化爬虫核心
        self.crawler_core = CrawlerCore(
            output_dir=output_dir,
            data_dir=data_dir,
            timeout=timeout,
            retry=retry,
            use_selenium=use_selenium,
            enable_xpath=enable_xpath,
            max_workers=max_workers,
            config=config
        )
        
        logger.info(f"爬虫初始化完成，输出目录: {self.crawler_core.output_dir}, 数据目录: {self.crawler_core.data_dir}")
        logger.info(f"邮件通知: {'已启用' if notifier.enabled else '未启用'}")
        logger.info("博客生成：请在爬虫完成后使用generate_blog_from_crawler.py脚本")
    
    def crawl(self, url, rule_id=None, task_id=None):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            rule_id (str, optional): XPath规则ID，用于指定使用哪个XPath规则
            task_id (str, optional): 任务ID，如果不提供则自动生成
            
        Returns:
            tuple: (是否成功, 任务ID, 任务目录)
        """
        return self.crawler_core.crawl(url, rule_id, task_id, notifier)
    
    def close(self):
        """关闭资源"""
        self.crawler_core.close()

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页图片和标题爬虫")
    parser.add_argument("--url", help="要爬取的网页URL")
    parser.add_argument("--task-id", help="任务ID，如果不提供则自动生成")
    parser.add_argument("--output", help="输出目录，用于临时文件和日志（默认使用配置文件设置）")
    parser.add_argument("--data-dir", help="数据存储目录，用于保存图片和元数据（默认使用配置文件设置）")
    parser.add_argument("--use-selenium", type=lambda x: x.lower() == 'true', help="使用Selenium和ChromeDriver进行爬取，值为true或false")
    parser.add_argument("--timeout", type=int, help="请求超时时间，单位为秒（默认使用配置文件设置）")
    parser.add_argument("--retry", type=int, help="失败重试次数（默认使用配置文件设置）")
    parser.add_argument("--config", help="配置文件路径（默认为'config.json'）")
    parser.add_argument("--email-notification", type=lambda x: x.lower() == 'true',help="是否启用邮件通知，值为true或false")
    # 博客生成现在通过独立脚本generate_blog_from_crawler.py完成
    parser.add_argument("--rule-id", help="XPath规则ID，用于指定使用哪个XPath规则（例如：reddit_media, twitter_media, general_article）")
    parser.add_argument("--enable-xpath", type=lambda x: x.lower() == 'true', help="启用XPath选择器，使用XPath规则解析页面，值为true或false（默认值取决于config.json中xpath_config.enabled的值）")
    parser.add_argument("--list-rules", action="store_true", help="列出所有可用的XPath规则")
    
    args = parser.parse_args()
    
    # 加载配置文件
    if args.config:
        config.__init__(args.config)
    
    # 处理邮件通知
    if args.email_notification is not None:  # 如果用户明确指定了邮件通知设置
        config.set('email', 'enabled', args.email_notification)
    
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
        use_selenium=args.use_selenium,
        enable_xpath=args.enable_xpath
    )
    
    try:
        # 开始爬取，传入规则ID和任务ID
        success, task_id, task_dir = crawler.crawl(args.url, args.rule_id, args.task_id)
        if not success:
            sys.exit(1)
        logger.info(f"爬取完成，任务ID: {task_id}, 任务目录: {task_dir}")
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