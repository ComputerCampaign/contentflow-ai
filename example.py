#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例脚本，展示如何使用爬虫

使用方法：
    python example.py
"""

import os
import sys
from crawler import Crawler
import logging

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_usage():
    """爬虫使用示例"""
    # 示例URL
    url = "https://unsplash.com/"  # Unsplash是一个免费图片网站，适合测试爬虫
    
    # 输出目录和数据目录
    output_dir = "example_output"
    data_dir = "data"
    
    # 创建爬虫实例
    crawler = Crawler(
        output_dir=output_dir,
        data_dir=data_dir,
        timeout=15,
        retry=3,
        use_selenium=False  # 默认使用requests
    )
    
    try:
        # 开始爬取
        logger.info(f"开始爬取示例URL: {url}")
        success = crawler.crawl(url)
        
        if success:
            logger.info("爬取成功！")
            logger.info(f"输出目录: {os.path.abspath(output_dir)}")
            logger.info(f"数据目录: {os.path.abspath(data_dir)}")
            logger.info(f"图片保存在: {os.path.abspath(os.path.join(data_dir, 'images'))}")
            logger.info(f"数据文件: {os.path.abspath(os.path.join(data_dir, 'images.csv'))}")
            logger.info(f"页面信息: {os.path.abspath(os.path.join(data_dir, 'page_info.json'))}")
        else:
            logger.error("爬取失败！")
    except Exception as e:
        logger.exception(f"示例运行过程中发生错误: {str(e)}")
    finally:
        # 关闭资源
        crawler.close()

def example_with_selenium():
    """使用Selenium的爬虫示例"""
    # 示例URL - 选择一个可能需要JavaScript渲染的网站
    url = "https://www.pexels.com/"  # Pexels是另一个免费图片网站
    
    # 输出目录和数据目录
    output_dir = "example_selenium_output"
    data_dir = "data"
    
    # 创建爬虫实例，使用Selenium
    crawler = Crawler(
        output_dir=output_dir,
        data_dir=data_dir,
        timeout=15,
        retry=3,
        use_selenium=True  # 使用Selenium
    )
    
    try:
        # 开始爬取
        logger.info(f"开始使用Selenium爬取示例URL: {url}")
        success = crawler.crawl(url)
        
        if success:
            logger.info("爬取成功！")
            logger.info(f"输出目录: {os.path.abspath(output_dir)}")
            logger.info(f"数据目录: {os.path.abspath(data_dir)}")
            logger.info(f"图片保存在: {os.path.abspath(os.path.join(data_dir, 'images'))}")
            logger.info(f"数据文件: {os.path.abspath(os.path.join(data_dir, 'images.csv'))}")
            logger.info(f"页面信息: {os.path.abspath(os.path.join(data_dir, 'page_info.json'))}")
        else:
            logger.error("爬取失败！")
    except Exception as e:
        logger.exception(f"示例运行过程中发生错误: {str(e)}")
    finally:
        # 关闭资源
        crawler.close()

if __name__ == "__main__":
    print("=== 爬虫使用示例 ===")
    print("1. 使用requests爬取")
    print("2. 使用Selenium爬取")
    print("0. 退出")
    
    choice = input("请选择示例 (0-2): ")
    
    if choice == "1":
        example_usage()
    elif choice == "2":
        example_with_selenium()
    else:
        print("退出示例")
        sys.exit(0)