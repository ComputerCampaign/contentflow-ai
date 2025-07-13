#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫测试脚本

使用方法：
    python test_crawler.py
"""

import unittest
import os
import shutil
from crawler import Crawler
from utils.downloader import Downloader
from utils.parser import Parser

class TestCrawler(unittest.TestCase):
    """爬虫测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_output_dir = "test_output"
        self.test_data_dir = "test_data"
        # 确保测试目录不存在
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    def tearDown(self):
        """测试后清理"""
        # 清理测试目录
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    def test_downloader_init(self):
        """测试下载器初始化"""
        downloader = Downloader(self.test_data_dir)
        self.assertTrue(os.path.exists(self.test_data_dir))
        self.assertTrue(os.path.exists(os.path.join(self.test_data_dir, "images")))
    
    def test_parser_init(self):
        """测试解析器初始化"""
        parser = Parser()
        self.assertIsNotNone(parser)
    
    def test_crawler_init(self):
        """测试爬虫初始化"""
        crawler = Crawler(self.test_output_dir, self.test_data_dir)
        self.assertTrue(os.path.exists(self.test_output_dir))
        self.assertTrue(os.path.exists(self.test_data_dir))
        self.assertIsNotNone(crawler.downloader)
        self.assertIsNotNone(crawler.parser)
        crawler.close()
    
    def test_parser_html(self):
        """测试HTML解析"""
        parser = Parser()
        
        # 简单的HTML内容
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试页面</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <img src="test1.jpg" alt="测试图片1">
            <div>
                <img src="test2.jpg" alt="测试图片2">
                <p>测试段落</p>
            </div>
        </body>
        </html>
        """
        
        result = parser.parse_html(html_content, "http://example.com")
        
        # 验证结果
        self.assertEqual(result["page_title"], "测试页面")
        self.assertEqual(len(result["images"]), 2)
        self.assertEqual(result["images"][0]["url"], "http://example.com/test1.jpg")
        self.assertEqual(result["images"][0]["alt"], "测试图片1")
        self.assertEqual(result["images"][1]["url"], "http://example.com/test2.jpg")
        self.assertEqual(result["images"][1]["alt"], "测试图片2")
    
    def test_fetch_with_requests(self):
        """测试使用requests获取URL内容"""
        crawler = Crawler(self.test_output_dir, self.test_data_dir, timeout=5, retry=1)
        
        # 测试有效URL
        success, content = crawler._fetch_with_requests("https://httpbin.org/html")
        self.assertTrue(success)
        self.assertIn("<html>", content)
        
        # 测试无效URL
        success, error = crawler._fetch_with_requests("https://nonexistent-domain-123456789.com")
        self.assertFalse(success)
        
        crawler.close()

if __name__ == "__main__":
    unittest.main()