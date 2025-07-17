# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  date:  2021-09-10
  file:  headless_render
  Description :
-------------------------------------------------
"""

import os
import sys
import time
import requests
import timeout_decorator

from browsermobproxy import Server

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


class Crawler:
    js_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './script/stealth.min.js'))

    def __init__(self, handler='headless'):
        if handler == 'source':
            pass
        elif handler == 'headless':
            self.proxy = None
            # self.proxy, self.server = self._create_browser_bom_proxy_server(proxy=None)
            # 配置本地代理
            self.proxy = "http://127.0.0.1:8888"
            self.driver = self._create_stealth_driver(self.proxy)

    def update_driver(self):
        try:
            if isinstance(self.driver, webdriver.Chrome):
                self.driver.quit()
                self.driver = self._create_stealth_driver(proxy=self.proxy)
            else:
                self.driver = self._create_stealth_driver(proxy=self.proxy)
        except:
            pass

    def _create_browser_bom_proxy_server(self, proxy=None):
        server = Server("/usr/local/browsermob-proxy/bin/browsermob-proxy")
        server.start()
        try:
            proxy = server.create_proxy(params=proxy)
            print("开启代理成功")
        except Exception as e:
            print("error:{}".format(e))
            print("使用代理IP出现异常，尝试不使用代理")
            try:
                proxy = server.create_proxy().proxy
            except Exception as e:
                server.stop()
                print("errro:{}".format(e))
                print("开启浏览器代理失败")
                sys.exit()
        return proxy, server

    def _create_stealth_driver(self, proxy=None):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        if proxy is not None:
            chrome_options.add_argument('--proxy-server={0}'.format(proxy))
        driver = webdriver.Chrome(options=chrome_options)

        # selenium4.0版本之后引入的新功能，通过js注入绕过web_driver的检测属性
        with open(self.js_file_path) as f:
            js = f.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })
        return driver

    @timeout_decorator.timeout(200)
    def get_url(self, url):
        self.driver.get(url=url)

    # 只渲染页面，不做其他操作
    def chrome_headless_render(self, task_url, sleep_time=3):
        try:
            if self.driver.service.process is None:
                print("driver already quite, restart driver now!")
                self.driver = self._create_stealth_driver()
            self.driver.set_page_load_timeout(50)
            self.get_url(url=task_url)
            time.sleep(sleep_time)
            return self.driver.page_source
        except Exception as e:
            print("crawler error:{}".format(e))
            self.driver.quit()
            self.driver = self._create_stealth_driver()

    def find_by_xpath_and_move_to(self, xpath):
        try:
            button = self.driver.find_element('xpath', xpath)
            ActionChains(self.driver).move_to_element(button)
            time.sleep(2)
            return True
        except:
            return False

    # 点击传入的xpath对应的元素
    def click_by_xpath(self, xpath):
        try:
            button = self.driver.find_element('xpath', xpath)
            ActionChains(self.driver).move_to_element(button)
            time.sleep(2)
            ActionChains(self.driver).click(button).perform()
            ActionChains(self.driver).release()
            time.sleep(1)
            return True
        except:
            return False

    def close(self):
        try:
            self.driver.quit()
            print("quite driver success!")
        except Exception as e:
            print("quite driver error:{}".format(e))

    # 添加一个requests的请求函数，与上面的方法没有联系
    def do_request(self, url, retry_times=5, headers=None, data=None):
        for _ in range(retry_times):
            try:
                if data is not None:
                    response = requests.post(url=url, headers=headers, data=data, timeout=5)
                else:
                    time.sleep(1)
                    response = requests.get(url=url, headers=headers, timeout=5)
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                print("crawler error:{e}".format(e=e))
        time.sleep(1)
        raise Exception("重试次数达到上限")
