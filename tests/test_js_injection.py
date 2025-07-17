#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 JavaScript 脚本是否正确注入到 Selenium 中
"""

import os
import sys
import unittest

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler_utils.selenium_renderer import SeleniumRenderer
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)


class TestJSInjection(unittest.TestCase):
    """测试 JavaScript 脚本注入"""
    
    def setUp(self):
        """初始化测试环境"""
        self.renderer = SeleniumRenderer(headless=False)  # 使用有头模式便于观察
    
    def tearDown(self):
        """清理测试环境"""
        if hasattr(self, 'renderer') and self.renderer:
            self.renderer.close()
    
    def test_js_injection(self):
        """测试 JavaScript 脚本是否正确注入"""
        # 创建一个测试页面，用于验证脚本注入
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JS Injection Test</title>
        </head>
        <body>
            <h1>Testing JavaScript Injection</h1>
            <div id="result">Not Injected</div>
            <script>
                // 检查是否存在 navigator.webdriver 属性
                // 如果 stealth.js 正确注入，这个属性应该是 undefined 或 false
                const webdriverValue = navigator.webdriver;
                document.getElementById('result').innerText = 
                    `WebDriver: ${webdriverValue === undefined ? 'undefined (正常)' : webdriverValue}`;
                
                // 检查其他可能被 stealth.js 修改的属性
                const automationInfo = {
                    'navigator.webdriver': navigator.webdriver,
                    'window.chrome': typeof window.chrome,
                    'window.navigator.plugins.length': navigator.plugins.length,
                    'window.navigator.languages': navigator.languages,
                    'navigator.permissions': typeof navigator.permissions
                };
                
                // 显示检测结果
                const resultDiv = document.createElement('div');
                resultDiv.innerHTML = '<h2>详细检测结果:</h2><pre>' + 
                    JSON.stringify(automationInfo, null, 2) + '</pre>';
                document.body.appendChild(resultDiv);
            </script>
        </body>
        </html>
        """
        
        # 保存测试页面到临时文件
        temp_html_path = os.path.join(os.path.dirname(__file__), 'temp_test_injection.html')
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        try:
            # 使用 file:// 协议打开本地 HTML 文件
            file_url = f"file://{temp_html_path}"
            success, content = self.renderer.render_page(file_url)
            
            # 验证页面是否成功加载
            self.assertTrue(success, "页面加载失败")
            
            # 获取页面中的检测结果
            result_text = self.renderer.driver.find_element('id', 'result').text
            logger.info(f"检测结果: {result_text}")
            
            # 验证 webdriver 属性是否被隐藏（undefined 或 false）
            self.assertTrue(
                'undefined' in result_text or 'false' in result_text.lower(),
                f"JavaScript 脚本注入失败，webdriver 属性未被隐藏: {result_text}"
            )
            
            # 执行 JavaScript 来检查更多属性
            js_check = """
            return {
                'webdriver_value': navigator.webdriver,
                'chrome_exists': typeof window.chrome !== 'undefined',
                'plugins_length': navigator.plugins.length > 0,
                'languages_exists': Array.isArray(navigator.languages) && navigator.languages.length > 0
            }
            """
            js_result = self.renderer.driver.execute_script(js_check)
            logger.info(f"JavaScript 检查结果: {js_result}")
            
            # 验证关键属性
            self.assertTrue(
                js_result['webdriver_value'] is None or js_result['webdriver_value'] is False,
                "navigator.webdriver 属性未被隐藏或设为 False"
            )
            self.assertTrue(js_result['chrome_exists'], "window.chrome 属性不存在")
            self.assertTrue(js_result['plugins_length'], "navigator.plugins 长度异常")
            self.assertTrue(js_result['languages_exists'], "navigator.languages 属性异常")
            
            logger.info("JavaScript 脚本注入测试通过！")
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)


if __name__ == '__main__':
    unittest.main()