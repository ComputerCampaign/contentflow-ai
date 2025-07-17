#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证 JavaScript 脚本注入工具
用于检查 Selenium 中的 JavaScript 脚本是否正确注入
"""

import os
import sys
import argparse

# 导入自定义模块
from crawler_utils.selenium_renderer import SeleniumRenderer
from crawler_utils.js_injection_validator import JSInjectionValidator
from config.config import Config
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='验证 JavaScript 脚本注入工具')
    parser.add_argument('--headless', action='store_true', help='使用无头模式（默认为有头模式）')
    parser.add_argument('--url', type=str, help='要验证的URL（如果不提供则使用本地测试页面）')
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = Config()
        
        # 初始化 SeleniumRenderer（使用有头模式便于观察）
        headless = args.headless
        renderer = SeleniumRenderer(
            config=config,
            headless=headless,
            page_load_wait=5
        )
        
        logger.info(f"初始化 SeleniumRenderer 成功，使用{'无头' if headless else '有头'}模式")
        
        # 初始化验证器
        validator = JSInjectionValidator(renderer)
        
        # 如果提供了URL，则验证该URL
        if args.url:
            logger.info(f"正在验证URL: {args.url}")
            success, content = renderer.render_page(args.url)
            
            if not success:
                logger.error(f"页面加载失败: {content}")
                return 1
            
            # 验证脚本注入
            is_injected, details = validator.validate_injection()
            
            logger.info(f"JavaScript 脚本注入状态: {'成功' if is_injected else '失败'}")
            print("\n" + "=" * 50)
            print(f"URL: {args.url}")
            print(f"JavaScript 脚本注入: {'✓ 成功' if is_injected else '✗ 失败'}")
            print("=" * 50)
            print(details)
            print("=" * 50 + "\n")
            
        else:
            # 使用本地测试页面
            logger.info("使用本地测试页面验证脚本注入")
            success, result = validator.create_test_page()
            
            if not success:
                logger.error(f"测试失败: {result}")
                return 1
            
            print("\n" + "=" * 50)
            print("本地测试页面验证结果:")
            print("=" * 50)
            print(result)
            print("=" * 50 + "\n")
            
            # 如果是有头模式，提示用户查看浏览器
            if not headless:
                input("请查看浏览器窗口，按回车键继续...")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return 0
        
    except Exception as e:
        logger.error(f"验证过程中出错: {str(e)}")
        return 1
        
    finally:
        # 关闭 WebDriver
        if 'renderer' in locals() and renderer:
            renderer.close()


if __name__ == '__main__':
    sys.exit(main())