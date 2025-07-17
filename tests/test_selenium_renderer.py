#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Selenium渲染器功能
"""

import os
import sys
import unittest

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler_utils.selenium_renderer import SeleniumRenderer
from config.config import Config


class TestSeleniumRenderer(unittest.TestCase):
    """测试Selenium渲染器功能"""
    
    def setUp(self):
        """测试前准备"""
        # 加载配置
        self.config = Config()
        # 初始化渲染器
        self.renderer = SeleniumRenderer(
            config=self.config,
            headless=True,  # 使用无头模式
            timeout=30,
            page_load_wait=5,
            retry=2
        )
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'renderer'):
            self.renderer.close()
    
    def test_render_page(self):
        """测试页面渲染功能"""
        # 测试渲染百度首页
        success, content = self.renderer.render_page('https://www.baidu.com')
        self.assertTrue(success)
        self.assertIn('百度一下', content)
    
    def test_find_element(self):
        """测试查找元素功能"""
        # 先渲染页面
        self.renderer.render_page('https://www.baidu.com')
        # 测试查找搜索框
        result = self.renderer.find_by_xpath_and_move_to('//input[@id="kw"]')
        self.assertTrue(result)
    
    def test_click_element(self):
        """测试点击元素功能"""
        # 先渲染页面
        self.renderer.render_page('https://www.baidu.com')
        # 测试点击"百度一下"按钮
        result = self.renderer.click_by_xpath('//input[@id="su"]')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()