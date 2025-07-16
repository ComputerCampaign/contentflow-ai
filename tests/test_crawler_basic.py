#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试爬虫基本功能
"""

import sys
import argparse
from crawler import Crawler
from config import config

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试爬虫基本功能")
    parser.add_argument("--url", default="https://www.example.com", help="要爬取的网页URL")
    parser.add_argument("--rule-id", help="使用的规则ID")
    parser.add_argument("--use-selenium", type=lambda x: x.lower() == 'true', default=False, help="是否使用Selenium，值为true或false")
    parser.add_argument("--enable-xpath", type=lambda x: x.lower() == 'true', default=True, help="启用XPath选择器，使用XPath规则解析页面，值为true或false")
    
    args = parser.parse_args()
    
    # 打印参数信息
    print(f"URL: {args.url}")
    print(f"规则ID: {args.rule_id}")
    print(f"使用Selenium: {args.use_selenium}")
    print(f"启用XPath选择器: {args.enable_xpath}")
    
    # 创建爬虫实例
    crawler = Crawler(
        use_selenium=args.use_selenium,
        enable_xpath=args.enable_xpath
    )
    
    # 开始爬取
    success, task_id, task_dir = crawler.crawl(args.url, rule_id=args.rule_id)
    if not success:
        sys.exit(1)
    print(f"爬取完成，任务ID: {task_id}, 任务目录: {task_dir}")
    
    # 关闭资源
    crawler.close()

if __name__ == "__main__":
    main()