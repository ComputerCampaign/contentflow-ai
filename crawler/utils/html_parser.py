#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from lxml import etree

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class HtmlParser:
    """HTML解析器，负责从网页中提取图片和标题信息"""
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def parse_with_xpath(self, html_content, xpath_selector=None, base_url=None):
        """使用XPath解析HTML内容，提取图片和标题
        
        Args:
            html_content (str): HTML内容
            xpath_selector (str, optional): XPath选择器，用于限定爬取区域
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            dict: 包含标题和图片URL的字典
        """
        # 使用lxml解析HTML
        parser = etree.HTMLParser()
        tree = etree.fromstring(html_content, parser)
        
        # 提取页面标题
        title_elements = tree.xpath('//title/text()')
        title = title_elements[0].strip() if title_elements else "未知标题"
        logger.info(f"页面标题: {title}")
        
        # 如果提供了XPath选择器，则只在指定区域内查找图片
        if xpath_selector:
            # 查找匹配XPath选择器的元素
            selected_elements = tree.xpath(xpath_selector)
            
            if not selected_elements:
                logger.warning(f"未找到匹配XPath选择器的元素: {xpath_selector}")
                return {
                    'page_title': title,
                    'page_url': base_url,
                    'images': [],
                    'headings': []
                }
            
            # 检查选择器是否已经直接选择了img标签
            if xpath_selector.lower().startswith('//img') or xpath_selector.endswith('img'):
                # 如果选择器已经直接选择了img标签，直接使用选中的元素
                img_elements = selected_elements
                logger.info("XPath选择器直接选择了img标签，跳过内部img查找")
            else:
                # 否则，在选中的元素内查找img标签
                img_elements = []
                for elem in selected_elements:
                    img_elements.extend(elem.xpath('.//img'))
        else:
            # 如果没有提供XPath选择器，则在整个页面中查找图片
            img_elements = tree.xpath('//img')
        
        logger.info(f"找到 {len(img_elements)} 个图片标签")
        if xpath_selector:
            logger.info(f"使用XPath选择器: {xpath_selector}")

        
        # 提取图片URL和alt文本
        images = []
        for img in img_elements:
            img_url = img.get('src')
            if not img_url:
                continue
                
            # 处理相对URL
            if base_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            # 提取alt文本作为图片标题
            img_alt = img.get('alt', '').strip()
            
            # 提取图片所在的父元素的文本
            parent_text = ''
            parent_elements = tree.xpath(f"//img[@src='{img.get('src')}']/parent::*/text()")
            if parent_elements:
                parent_text = ' '.join([text.strip() for text in parent_elements])
                if len(parent_text) > 200:
                    parent_text = parent_text[:197] + '...'
            
            images.append({
                'url': img_url,
                'alt': img_alt,
                'parent_text': parent_text
            })
        
        # 提取可能的文章标题（h1, h2等）
        headings = []
        for i in range(1, 4):  # h1, h2, h3
            for h_text in tree.xpath(f'//h{i}/text()'):
                headings.append({
                    'level': i,
                    'text': h_text.strip()
                })
        
        return {
            'page_title': title,
            'page_url': base_url,
            'images': images,
            'headings': headings
        }
    
    def parse_html(self, html_content, base_url=None):
        """解析HTML内容，提取图片和标题
        
        Args:
            html_content (str): HTML内容
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            dict: 包含标题和图片URL的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取页面标题
        title = soup.title.text.strip() if soup.title else "未知标题"
        logger.info(f"页面标题: {title}")
        
        # 提取所有图片
        img_tags = soup.find_all('img')
        logger.info(f"找到 {len(img_tags)} 个图片标签")
        
        # 提取图片URL和alt文本
        images = []
        for img in img_tags:
            img_url = img.get('src')
            if not img_url:
                continue
                
            # 处理相对URL
            if base_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            # 提取alt文本作为图片标题
            img_alt = img.get('alt', '').strip()
            
            # 提取图片所在的父元素的文本，可能包含图片描述
            parent_text = ''
            parent = img.parent
            if parent and parent.name != 'body':
                parent_text = parent.get_text(strip=True)
                # 如果父文本太长，可能不是描述，而是页面的一部分
                if len(parent_text) > 200:
                    parent_text = parent_text[:197] + '...'
            
            images.append({
                'url': img_url,
                'alt': img_alt,
                'parent_text': parent_text
            })
        
        # 提取可能的文章标题（h1, h2等）
        headings = []
        for i in range(1, 4):  # h1, h2, h3
            for h in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': h.get_text(strip=True)
                })
        
        return {
            'page_title': title,
            'page_url': base_url,
            'images': images,
            'headings': headings
        }