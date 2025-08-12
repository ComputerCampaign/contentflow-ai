#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from lxml import etree
import re

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class HtmlParser:
    """HTML解析器，基于XPath规则提取内容"""
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def extract_images_by_xpath(self, html_content, xpath_rule, base_url=None):
        """使用XPath规则提取图片
        
        Args:
            html_content (str): HTML内容
            xpath_rule (str): XPath选择器
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            list: 图片数据列表
        """
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            elements = tree.xpath(xpath_rule)
            logger.info(f"XPath规则匹配到 {len(elements)} 个元素")
            
            images = []
            
            for element in elements:
                # 如果元素本身是img标签
                if element.tag == 'img':
                    img_data = self._extract_image_from_element(element, base_url)
                    if img_data:
                        images.append(img_data)
                else:
                    # 在元素内查找img标签
                    img_elements = element.xpath('.//img')
                    for img in img_elements:
                        img_data = self._extract_image_from_element(img, base_url)
                        if img_data:
                            images.append(img_data)
            
            logger.info(f"提取到 {len(images)} 张图片")
            return images
            
        except Exception as e:
            logger.error(f"XPath图片提取失败: {str(e)}")
            return []
    
    def extract_text_by_xpath(self, html_content, xpath_rule):
        """使用XPath规则提取文本内容
        
        Args:
            html_content (str): HTML内容
            xpath_rule (str): XPath选择器
            
        Returns:
            list: 文本内容列表
        """
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            elements = tree.xpath(xpath_rule)
            logger.info(f"XPath规则匹配到 {len(elements)} 个元素")
            
            texts = []
            
            for element in elements:
                text_content = self._extract_text_from_element(element)
                if text_content:
                    texts.append({
                        'text': text_content,
                        'tag': element.tag if hasattr(element, 'tag') else 'text',
                        'attributes': dict(element.attrib) if hasattr(element, 'attrib') else {}
                    })
            
            logger.info(f"提取到 {len(texts)} 个文本内容")
            return texts
            
        except Exception as e:
            logger.error(f"XPath文本提取失败: {str(e)}")
            return []
    
    def extract_links_by_xpath(self, html_content, xpath_rule, base_url=None):
        """使用XPath规则提取链接
        
        Args:
            html_content (str): HTML内容
            xpath_rule (str): XPath选择器
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            list: 链接数据列表
        """
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            elements = tree.xpath(xpath_rule)
            logger.info(f"XPath规则匹配到 {len(elements)} 个元素")
            
            links = []
            
            for element in elements:
                # 如果元素本身是a标签
                if element.tag == 'a':
                    link_data = self._extract_link_from_element(element, base_url)
                    if link_data:
                        links.append(link_data)
                else:
                    # 在元素内查找a标签
                    link_elements = element.xpath('.//a')
                    for link in link_elements:
                        link_data = self._extract_link_from_element(link, base_url)
                        if link_data:
                            links.append(link_data)
            
            logger.info(f"提取到 {len(links)} 个链接")
            return links
            
        except Exception as e:
            logger.error(f"XPath链接提取失败: {str(e)}")
            return []
    
    def extract_elements_by_xpath(self, html_content, xpath_rule):
        """使用XPath规则提取通用元素
        
        Args:
            html_content (str): HTML内容
            xpath_rule (str): XPath选择器
            
        Returns:
            list: 元素数据列表
        """
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            elements = tree.xpath(xpath_rule)
            logger.info(f"XPath规则匹配到 {len(elements)} 个元素")
            
            results = []
            
            for element in elements:
                element_data = {
                    'tag': element.tag if hasattr(element, 'tag') else 'text',
                    'text': self._extract_text_from_element(element),
                    'attributes': dict(element.attrib) if hasattr(element, 'attrib') else {},
                }
                
                # 如果是文本节点
                if isinstance(element, str):
                    element_data = {
                        'tag': 'text',
                        'text': element.strip(),
                        'attributes': {}
                    }
                
                results.append(element_data)
            
            logger.info(f"提取到 {len(results)} 个元素")
            return results
            
        except Exception as e:
            logger.error(f"XPath元素提取失败: {str(e)}")
            return []
    
    def extract_by_xpath_rule(self, html_content, rule, base_url=None):
        """使用完整的XPath规则配置提取内容
        
        Args:
            html_content (str): HTML内容
            rule (dict): XPath规则配置，包含xpath、rule_type、field_name等字段
            base_url (str, optional): 基础URL
            
        Returns:
            dict: 提取结果，使用field_name作为键名
        """
        if not rule or 'xpath' not in rule:
            logger.warning("无效的XPath规则")
            return {}
        
        rule_id = rule.get('id', 'unknown')
        rule_type = rule.get('rule_type', 'general')  # 兼容旧的type字段
        field_name = rule.get('field_name')  # 获取字段名
        xpath_selector = rule['xpath']
        
        # 如果没有指定field_name，使用默认命名规则
        if not field_name:
            if rule_type == 'image':
                field_name = 'images'
            elif rule_type == 'text':
                field_name = 'texts'
            elif rule_type == 'link':
                field_name = 'links'
            else:
                field_name = 'elements'
        
        logger.info(f"应用XPath规则: {rule.get('name', 'Unknown')} ({rule_id}), 类型: {rule_type}, 字段名: {field_name}")
        
        # 根据规则类型选择提取方法
        if rule_type == 'image':
            extracted_data = self.extract_images_by_xpath(html_content, xpath_selector, base_url)
        elif rule_type == 'text':
            extracted_data = self.extract_text_by_xpath(html_content, xpath_selector)
        elif rule_type == 'link':
            extracted_data = self.extract_links_by_xpath(html_content, xpath_selector, base_url)
        else:
            # 通用提取，返回所有类型的数据
            extracted_data = {
                'images': self.extract_images_by_xpath(html_content, xpath_selector, base_url),
                'texts': self.extract_text_by_xpath(html_content, xpath_selector),
                'links': self.extract_links_by_xpath(html_content, xpath_selector, base_url),
                'elements': self.extract_elements_by_xpath(html_content, xpath_selector)
            }
        
        # 使用field_name作为键名返回结果
        result = {
            field_name: extracted_data,
            '_meta': {
                'rule_id': rule_id,
                'rule_type': rule_type,
                'field_name': field_name
            }
        }
        
        return result
    
    def _extract_image_from_element(self, img_element, base_url):
        """从img元素中提取图片数据"""
        try:
            img_url = img_element.get('src')
            if not img_url:
                return None
            
            # 处理相对URL
            if base_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            return {
                'url': img_url,
                'alt': img_element.get('alt', '').strip(),
                'title': img_element.get('title', '').strip(),
                'width': img_element.get('width', ''),
                'height': img_element.get('height', ''),
                'class': img_element.get('class', ''),
                'id': img_element.get('id', '')
            }
        except Exception as e:
            logger.debug(f"提取图片数据失败: {str(e)}")
            return None
    
    def _extract_link_from_element(self, link_element, base_url):
        """从a元素中提取链接数据"""
        try:
            href = link_element.get('href')
            if not href:
                return None
            
            # 处理相对URL
            if base_url and not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            return {
                'url': href,
                'text': self._extract_text_from_element(link_element),
                'title': link_element.get('title', '').strip(),
                'target': link_element.get('target', ''),
                'class': link_element.get('class', ''),
                'id': link_element.get('id', '')
            }
        except Exception as e:
            logger.debug(f"提取链接数据失败: {str(e)}")
            return None
    
    def _extract_text_from_element(self, element):
        """从元素中提取文本内容"""
        try:
            if isinstance(element, str):
                return element.strip()
            elif hasattr(element, 'text_content'):
                return element.text_content().strip()
            elif hasattr(element, 'text'):
                return element.text.strip() if element.text else ''
            else:
                return str(element).strip()
        except Exception as e:
            logger.debug(f"提取文本内容失败: {str(e)}")
            return ''