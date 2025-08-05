#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
无头浏览器渲染模块，提供基于Selenium的网页渲染功能，
并实现反爬虫检测绕过机制
"""

import os
import time
import timeout_decorator

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 导入日志配置
from crawler.logger import setup_logger
from crawler.config import crawler_config

# 设置日志
logger = setup_logger(__name__, file_path=__file__)


class SeleniumRenderer:
    """基于Selenium的网页渲染器，支持反爬虫检测绕过"""
    
    def __init__(self, config=None, headless=True, proxy=None, timeout=50, page_load_wait=6, retry=3):
        """
        初始化Selenium渲染器
        
        Args:
            config (object, optional): 配置对象
            headless (bool, optional): 是否使用无头模式，默认为True
            proxy (str, optional): 代理服务器地址，例如"http://127.0.0.1:8888"
            timeout (int, optional): 页面加载超时时间（秒）
            page_load_wait (int, optional): 页面加载后等待时间（秒）
            retry (int, optional): 失败重试次数
        """
        self.config = config or crawler_config
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.page_load_wait = page_load_wait
        self.retry = retry
        
        # 从配置中获取Selenium设置
        if self.config:
            selenium_config = self.config.get('selenium', {})
            self.page_load_wait = selenium_config.get('page_load_wait', self.page_load_wait)
        
        # 获取stealth.min.js文件路径
        scripts_config = self.config.get('scripts', {})
        stealth_path = scripts_config.get('stealth_path', 'crawler/config/scripts/stealth.min.js')
        
        # 如果是相对路径，则相对于项目根目录
        if not os.path.isabs(stealth_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.js_file_path = os.path.join(project_root, stealth_path)
        else:
            self.js_file_path = stealth_path
        
        # 初始化WebDriver
        self.driver = self._create_stealth_driver()
        logger.info("Selenium渲染器初始化成功")
    
    def _create_stealth_driver(self):
        """创建具有反爬虫检测绕过功能的WebDriver"""
        # 设置Chrome选项
        chrome_options = Options()
        
        # 从配置中获取Selenium设置
        selenium_config = {}
        if self.config:
            selenium_config = self.config.get('selenium', {})
        
        # 根据配置决定是否使用无头模式
        headless = selenium_config.get('headless', self.headless)
        if headless:
            chrome_options.add_argument('--headless')
            if selenium_config.get('disable_gpu', True):
                chrome_options.add_argument('--disable-gpu')
        
        # 添加其他常用选项
        if selenium_config.get('no_sandbox', True):
            chrome_options.add_argument('--no-sandbox')
        if selenium_config.get('disable_dev_shm_usage', True):
            chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 设置窗口大小
        window_size = selenium_config.get('window_size', '1920,1080')
        chrome_options.add_argument(f'--window-size={window_size}')
        
        # 设置用户代理
        user_agent = selenium_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                                        'Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # 如果提供了代理，则使用代理
        proxy = selenium_config.get('proxy', self.proxy)
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # 初始化WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 设置页面加载超时
        driver.set_page_load_timeout(self.timeout)
        
        # 注入stealth.min.js脚本以绕过反爬虫检测
        try:
            with open(self.js_file_path) as f:
                js = f.read()
            
            # 使用CDP命令在新文档上执行脚本，绕过WebDriver检测
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": js
            })
            logger.info("成功注入反爬虫检测绕过脚本")
        except Exception as e:
            logger.error(f"注入反爬虫检测绕过脚本失败: {str(e)}")
        
        return driver
    
    @timeout_decorator.timeout(200)
    def get_url(self, url):
        """获取URL（带超时装饰器）"""
        self.driver.get(url=url)
    
    def render_page(self, url):
        """渲染页面并返回页面源代码
        
        Args:
            url (str): 要渲染的URL
            
        Returns:
            tuple: (是否成功, HTML内容或错误信息)
        """
        for attempt in range(self.retry + 1):
            try:
                # 检查driver是否需要重启
                if hasattr(self.driver, 'service') and self.driver.service.process is None:
                    logger.warning("WebDriver已关闭，正在重新启动...")
                    self.driver = self._create_stealth_driver()
                
                # 获取URL
                self.get_url(url)

                logger.info(f"等待{self.page_load_wait}秒, 等待页面加载完成")
                # 等待页面加载完成
                time.sleep(self.page_load_wait)
                
                # 获取页面源代码
                html_content = self.driver.page_source
                return True, html_content
                
            except Exception as e:
                if attempt < self.retry:
                    logger.warning(f"渲染页面失败，重试 {attempt+1}/{self.retry}: {url}")
                    time.sleep(1)  # 等待1秒再重试
                    
                    # 如果driver出现问题，尝试重新创建
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = self._create_stealth_driver()
                else:
                    logger.error(f"渲染页面失败: {url}, 错误: {str(e)}")
                    return False, str(e)
    
    def find_by_xpath_and_move_to(self, xpath):
        """查找元素并移动到该元素"""
        try:
            button = self.driver.find_element('xpath', xpath)
            ActionChains(self.driver).move_to_element(button)
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"查找元素失败: {xpath}, 错误: {str(e)}")
            return False
    
    def click_by_xpath(self, xpath):
        """点击指定xpath的元素"""
        try:
            button = self.driver.find_element('xpath', xpath)
            ActionChains(self.driver).move_to_element(button)
            time.sleep(2)
            ActionChains(self.driver).click(button).perform()
            ActionChains(self.driver).release()
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"点击元素失败: {xpath}, 错误: {str(e)}")
            return False
    
    def close(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver已关闭")
            except Exception as e:
                logger.error(f"关闭WebDriver失败: {str(e)}")