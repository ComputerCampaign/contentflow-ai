#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
import requests
from urllib.parse import urlparse

# 导入自定义模块
from crawler.utils.xpath_manager import XPathManager
from crawler.core import CrawlerCore
from crawler.config import crawler_config
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

# 简化的通知器类
class SimpleNotifier:
    def __init__(self):
        self.enabled = False
    
    def send_notification(self, *args, **kwargs):
        pass

notifier = SimpleNotifier()

def _update_task_status_via_api(task_id, status, result=None, error_message=None):
    """调用后端接口更新任务状态
    
    Args:
        task_id (str): 任务ID
        status (str): 任务状态 ('success', 'failed')
        result (str, optional): 任务结果
        error_message (str, optional): 错误信息
    """
    try:
        # 从环境变量或配置文件获取后端API地址
        api_base_url = os.getenv('BACKEND_API_URL', 'http://localhost:5002/api/v1')
        url = f"{api_base_url}/tasks/{task_id}/status-airflow"
        
        payload = {'status': status}
        if result:
            payload['result'] = result
        if error_message:
            payload['error_message'] = error_message
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': os.getenv('AIRFLOW_API_KEY', 'airflow-secret-key')
        }
        
        logger.info(f"🌐 [CRAWLER] 调用后端接口更新任务状态")
        logger.info(f"   - URL: {url}")
        logger.info(f"   - Payload: {payload}")
        logger.info(f"   - API Key: {headers['X-API-Key'][:10]}...")
        
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ [CRAWLER] 任务 {task_id} 状态已成功更新为: {status}")
            try:
                response_data = response.json()
                logger.info(f"   - 后端响应: {response_data}")
            except:
                logger.info(f"   - 后端响应: {response.text}")
        else:
            logger.error(f"❌ [CRAWLER] 更新任务状态失败: HTTP {response.status_code}")
            logger.error(f"   - 响应内容: {response.text}")
            
    except Exception as e:
        logger.error(f"💥 [CRAWLER] 调用后端接口更新任务状态失败: {str(e)}")
        # 不抛出异常，避免影响爬虫主流程

class Crawler:
    """网页爬虫，用于抓取图片和标题信息"""
    
    def __init__(self, output_dir=None, data_dir=None, timeout=None, retry=None, use_selenium=None, enable_xpath=None, max_workers=None):
        """初始化爬虫
        
        Args:
            output_dir (str, optional): 输出目录（用于临时文件和日志）
            data_dir (str, optional): 数据存储目录（用于保存图片和元数据）
            timeout (int, optional): 请求超时时间（秒）
            retry (int, optional): 失败重试次数
            use_selenium (bool, optional): 是否使用Selenium
            enable_xpath (bool, optional): 是否启用XPath选择器
            max_workers (int, optional): 最大并发下载数
        """
        # 初始化爬虫核心
        self.crawler_core = CrawlerCore(
            output_dir=output_dir,
            data_dir=data_dir,
            timeout=timeout,
            retry=retry,
            use_selenium=use_selenium,
            enable_xpath=enable_xpath,
            max_workers=max_workers
        )
        
        logger.info(f"爬虫初始化完成，输出目录: {self.crawler_core.output_dir}, 数据目录: {self.crawler_core.data_dir}")
        logger.info(f"邮件通知: {'已启用' if notifier.enabled else '未启用'}")
    
    def crawl(self, url, rule_ids=None, task_id=None):
        """爬取指定URL的图片和标题
        
        Args:
            url (str): 要爬取的URL
            rule_ids (list, optional): XPath规则ID列表，用于指定使用哪些XPath规则
            task_id (str, optional): 任务ID，如果不提供则自动生成
            
        Returns:
            tuple: (是否成功, 任务ID, 任务目录)
        """
        result = self.crawler_core.crawl_url(url, task_id, rule_ids=rule_ids)
        if result.get('success'):
            return True, result.get('task_name'), result.get('task_dir')
        else:
            return False, None, None
    
    def close(self):
        """关闭资源"""
        # CrawlerCore没有close方法，这里只是占位
        pass

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页图片和标题爬虫")
    parser.add_argument("--url", help="要爬取的网页URL")
    parser.add_argument("--task-id", help="任务ID，如果不提供则自动生成")
    parser.add_argument("--output", help="输出目录，用于临时文件和日志（默认使用配置文件设置）")
    parser.add_argument("--data-dir", help="数据存储目录，用于保存图片和元数据（默认使用配置文件设置）")
    parser.add_argument("--use-selenium", type=lambda x: x.lower() == 'true', help="使用Selenium和ChromeDriver进行爬取，值为true或false")
    parser.add_argument("--timeout", type=int, help="请求超时时间，单位为秒（默认使用配置文件设置）")
    parser.add_argument("--retry", type=int, help="失败重试次数（默认使用配置文件设置）")
    parser.add_argument("--config", help="配置文件路径（默认为'config.json'）")
    parser.add_argument("--email-notification", type=lambda x: x.lower() == 'true',help="是否启用邮件通知，值为true或false")
    # Selenium 配置参数
    parser.add_argument("--headless", type=lambda x: x.lower() == 'true', help="Selenium是否使用无头模式（不显示浏览器界面），值为true或false")
    parser.add_argument("--proxy", help="Selenium使用的代理服务器地址，格式为http://host:port或socks5://host:port")
    parser.add_argument("--page-load-wait", type=int, help="Selenium页面加载等待时间，单位为秒")
    parser.add_argument("--user-agent", help="Selenium使用的用户代理字符串")
    parser.add_argument("--rule-ids", help="XPath规则ID列表，用逗号分隔，用于指定使用哪些XPath规则（例如：reddit_media,reddit_comments）")
    parser.add_argument("--enable-xpath", type=lambda x: x.lower() == 'true', help="启用XPath选择器，使用XPath规则解析页面，值为true或false（默认值取决于config.json中xpath_config.enabled的值）")
    parser.add_argument("--list-rules", action="store_true", help="列出所有可用的XPath规则")
    
    args = parser.parse_args()
    
    # 加载配置文件
    if args.config:
        # 简化配置处理，直接使用crawler_config
        pass
    
    # 处理邮件通知
    if args.email_notification is not None:
        # 简化处理，crawler模块暂不支持邮件通知
        pass
    
    # 处理 Selenium 配置参数
    if args.headless is not None:
        crawler_config.selenium_headless = args.headless
    if args.proxy is not None:
        crawler_config.selenium_proxy = args.proxy
    if args.page_load_wait is not None:
        crawler_config.selenium_page_load_wait = args.page_load_wait
    if args.user_agent is not None:
        crawler_config.selenium_user_agent = args.user_agent
    
    # 如果指定了列出规则
    if args.list_rules:
        # 从正确的模块导入XPathManager
        from crawler.utils.xpath_manager import XPathManager
        # 创建XPathManager实例并调用list_rules方法
        xpath_manager = XPathManager()
        print(xpath_manager.list_rules())
        sys.exit(0)
    
    # 检查是否提供了URL
    if not args.url:
        logger.error("未提供URL，请使用--url参数指定要爬取的网页URL")
        parser.print_help()
        sys.exit(1)
        
    # 验证URL
    try:
        result = urlparse(args.url)
        if not all([result.scheme, result.netloc]):
            logger.error(f"无效的URL: {args.url}")
            sys.exit(1)
    except Exception:
        logger.error(f"无效的URL: {args.url}")
        sys.exit(1)
    
    # 创建爬虫实例
    crawler = Crawler(
        output_dir=args.output,
        data_dir=args.data_dir,
        timeout=args.timeout,
        retry=args.retry,
        use_selenium=args.use_selenium,
        enable_xpath=args.enable_xpath
    )
    
    try:
        # 解析规则ID列表
        rule_ids = None
        if args.rule_ids:
            rule_ids = [rule_id.strip() for rule_id in args.rule_ids.split(',') if rule_id.strip()]
            logger.info(f"指定的XPath规则ID: {rule_ids}")
        
        # 开始爬取，传入规则ID列表和任务ID
        success, task_id, task_dir = crawler.crawl(args.url, rule_ids, args.task_id)
        
        # 打印爬取结果信息
        logger.info(f"🎯 [CRAWLER] 爬取结果 - 成功: {success}, 任务ID: {task_id}, 任务目录: {task_dir}")
        
        # 调用后端接口更新任务状态
        if args.task_id:
            logger.info(f"📡 [CRAWLER] 准备调用后端接口更新任务状态，任务ID: {args.task_id}")
            _update_task_status_via_api(args.task_id, 'completed' if success else 'failed', task_dir if success else None)
        else:
            logger.warning(f"⚠️ [CRAWLER] 未提供任务ID，跳过状态回传")
        
        if not success:
            sys.exit(1)
        logger.info(f"爬取完成，任务ID: {task_id}, 任务目录: {task_dir}")
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        if args.task_id:
            _update_task_status_via_api(args.task_id, 'failed', None, '用户中断')
    except Exception as e:
        logger.exception(f"爬取过程中发生错误: {str(e)}")
        if args.task_id:
            _update_task_status_via_api(args.task_id, 'failed', None, str(e))
        sys.exit(1)
    finally:
        # 关闭资源
        crawler.close()

if __name__ == "__main__":
    main()