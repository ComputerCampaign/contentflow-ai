#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JavaScript 脚本注入验证工具
用于验证 Selenium 中的 JavaScript 脚本是否正确注入
"""

import os
import json
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)


class JSInjectionValidator:
    """JavaScript 脚本注入验证器"""
    
    def __init__(self, selenium_renderer):
        """初始化验证器
        
        Args:
            selenium_renderer: SeleniumRenderer 实例
        """
        self.renderer = selenium_renderer
    
    def validate_injection(self):
        """验证 JavaScript 脚本是否正确注入
        
        Returns:
            tuple: (是否成功注入, 详细信息)
        """
        if not self.renderer or not self.renderer.driver:
            return False, "SeleniumRenderer 未初始化或 driver 不可用"
        
        try:
            # 执行 JavaScript 来检查关键属性
            js_check = """
            return {
                'webdriver_value': navigator.webdriver,
                'chrome_exists': typeof window.chrome !== 'undefined',
                'plugins_length': navigator.plugins.length,
                'languages_exists': Array.isArray(navigator.languages) && navigator.languages.length > 0,
                'permissions_exists': typeof navigator.permissions !== 'undefined',
                'user_agent': navigator.userAgent
            }
            """
            js_result = self.renderer.driver.execute_script(js_check)
            
            # 判断脚本是否成功注入
            is_injected = (
                (js_result['webdriver_value'] is None or js_result['webdriver_value'] is False) and  # webdriver 属性应该被隐藏或为 False
                js_result['chrome_exists'] and           # chrome 对象应该存在
                js_result['plugins_length'] > 0 and      # 应该有插件
                js_result['languages_exists']            # languages 应该存在
            )
            
            # 格式化结果
            result_info = {
                "注入状态": "成功" if is_injected else "失败",
                "详细信息": js_result
            }
            
            return is_injected, json.dumps(result_info, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"验证 JavaScript 脚本注入时出错: {str(e)}")
            return False, f"验证失败: {str(e)}"
    
    def create_test_page(self):
        """创建一个测试页面并打开，用于验证脚本注入
        
        Returns:
            tuple: (是否成功, 结果信息)
        """
        # 创建一个测试页面，用于验证脚本注入
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JS Injection Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .result { margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
                .success { color: green; }
                .failure { color: red; }
                pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto; }
            </style>
        </head>
        <body>
            <h1>JavaScript 脚本注入测试</h1>
            <div class="result" id="result">检测中...</div>
            <div id="details"></div>
            
            <script>
                // 检查是否存在 navigator.webdriver 属性
                const webdriverValue = navigator.webdriver;
                const resultDiv = document.getElementById('result');
                const detailsDiv = document.getElementById('details');
                
                if (webdriverValue === undefined || webdriverValue === false) {
                    resultDiv.innerHTML = '<span class="success">✓ 脚本注入成功!</span> ' +
                        'navigator.webdriver 属性已被隐藏';
                    resultDiv.className = 'result success';
                } else {
                    resultDiv.innerHTML = '<span class="failure">✗ 脚本注入失败!</span> ' +
                        `navigator.webdriver = ${webdriverValue}`;
                    resultDiv.className = 'result failure';
                }
                
                // 检查其他可能被 stealth.js 修改的属性
                const automationInfo = {
                    'navigator.webdriver': navigator.webdriver,
                    'window.chrome': typeof window.chrome,
                    'window.navigator.plugins.length': navigator.plugins.length,
                    'window.navigator.languages': navigator.languages.join(', '),
                    'navigator.permissions': typeof navigator.permissions,
                    'navigator.userAgent': navigator.userAgent
                };
                
                // 显示检测结果
                detailsDiv.innerHTML = '<h2>详细检测结果:</h2><pre>' + 
                    JSON.stringify(automationInfo, null, 2) + '</pre>';
            </script>
        </body>
        </html>
        """
        
        # 保存测试页面到临时文件
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_html_path = os.path.join(temp_dir, 'js_injection_test.html')
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        try:
            # 使用 file:// 协议打开本地 HTML 文件
            file_url = f"file://{temp_html_path}"
            success, content = self.renderer.render_page(file_url)
            
            if not success:
                return False, f"页面加载失败: {content}"
            
            # 获取页面中的检测结果
            try:
                result_text = self.renderer.driver.find_element('id', 'result').text
                details_html = self.renderer.driver.find_element('id', 'details').get_attribute('innerHTML')
                
                # 截图保存
                screenshot_path = os.path.join(temp_dir, 'js_injection_test_screenshot.png')
                self.renderer.driver.save_screenshot(screenshot_path)
                
                return True, f"测试结果: {result_text}\n\n详细信息: {details_html}\n\n截图已保存到: {screenshot_path}"
                
            except Exception as e:
                return False, f"获取测试结果失败: {str(e)}"
            
        except Exception as e:
            return False, f"测试失败: {str(e)}"
        finally:
            # 不删除临时文件，以便用户查看
            logger.info(f"测试页面已保存到: {temp_html_path}")