#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试启用XPath选择器功能
"""

import sys
import argparse
from crawler import Crawler
from config import config

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试启用XPath选择器功能")
    parser.add_argument("--url", default="https://www.reddit.com/r/beautiful_houses/comments/1kbcdcn/outdoor_caf%C3%A9_by_kamakanstudio_shiraz_iran/", help="要爬取的网页URL")
    parser.add_argument("--enable-xpath", type=lambda x: x.lower() == 'true', help="启用XPath选择器，使用XPath规则解析页面，值为true或false")
    
    args = parser.parse_args()
    
    # 打印参数信息
    print(f"URL: {args.url}")
    print(f"启用XPath选择器: {args.enable_xpath}")
    print(f"配置文件中的启用XPath选择器: {config.get('crawler', 'xpath_config', {}).get('enabled', False)}")
    
    # 创建爬虫实例
    crawler = Crawler(
        enable_xpath=args.enable_xpath
    )
    
    print(f"爬虫实例中的启用XPath选择器: {crawler.enable_xpath}")
    
    # 开始爬取
    success, task_id, task_dir = crawler.crawl(args.url)
    if not success:
        sys.exit(1)
    print(f"爬取完成，任务ID: {task_id}, 任务目录: {task_dir}")
    
    # 关闭资源
    crawler.close()

if __name__ == "__main__":
    main()