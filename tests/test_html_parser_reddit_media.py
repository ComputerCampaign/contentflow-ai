# -*- coding: utf-8 -*-
import os
import json
import logging
from crawler_utils.html_parser import HtmlParser

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_xpath_rules(xpath_rules_path):
    """加载XPath规则配置文件"""
    with open(xpath_rules_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_html_file(html_file_path):
    """加载HTML文件内容"""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        return f.read()

def test_html_parser_with_reddit_media():
    # 1. 加载XPath规则
    xpath_rules_path = os.path.join(ROOT_DIR, 'config', 'xpath', 'xpath_rules.json')
    xpath_rules = load_xpath_rules(xpath_rules_path)

    # 2. 查找reddit_media规则
    reddit_media_rule = None
    for rule in xpath_rules['rules']:
        if rule['id'] == 'reddit_media':
            reddit_media_rule = rule
            break

    if not reddit_media_rule:
        raise ValueError("未找到ID为'reddit_media'的XPath规则")

    # 打印规则信息
    print(f"找到规则: {reddit_media_rule['id']}")
    print(f"XPath选择器: {reddit_media_rule['xpath']}")

    # 3. 加载本地HTML文件
    html_file_path = os.path.join(ROOT_DIR, 'data', 'task_20250717_154358_9275bff4', 'page.html')
    html_content = load_html_file(html_file_path)

    # 4. 初始化HTMLParser并解析HTML内容
    html_parser = HtmlParser()
    result = html_parser.parse_with_xpath(html_content, reddit_media_rule['xpath'])
    
    # 5. 打印结果
    print(f"\n解析结果:")
    print(f"页面标题: {result['page_title']}")
    print(f"找到 {len(result['images'])} 个图片")
    
    # 打印前3个图片的信息
    for i, img in enumerate(result['images'][:3], 1):
        print(f"图片 {i}:")
        print(f"  URL: {img['url']}")
        if img['alt']:
            print(f"  Alt文本: {img['alt']}")

if __name__ == "__main__":
    test_html_parser_with_reddit_media()