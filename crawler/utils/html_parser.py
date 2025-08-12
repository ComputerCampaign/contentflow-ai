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
        
        # 检查是否包含comment_xpath配置
        comment_xpath = rule.get('comment_xpath')
        if comment_xpath:
            logger.info(f"检测到评论XPath配置，使用专门的评论解析逻辑: {rule.get('name', 'Unknown')} ({rule_id})")
            extracted_data = self.extract_comments_by_xpath(html_content, xpath_selector, comment_xpath, base_url)
            
            # 使用field_name作为键名返回结果
            result = {
                field_name or 'comments': extracted_data,
                '_meta': {
                    'rule_id': rule_id,
                    'rule_type': 'comment',
                    'field_name': field_name or 'comments'
                }
            }
            return result
        
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
    
    def extract_comments_by_xpath(self, html_content, xpath_rule, comment_xpath, base_url=None):
        """使用XPath规则提取完整的评论树结构
        
        Args:
            html_content (str): HTML内容
            xpath_rule (str): 主XPath选择器，用于选择评论元素
            comment_xpath (dict): 评论字段的XPath配置
            base_url (str, optional): 基础URL
            
        Returns:
            dict: 包含评论树结构的数据
        """
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用主XPath选择器获取所有评论元素
            comment_elements = tree.xpath(xpath_rule)
            logger.info(f"XPath规则匹配到 {len(comment_elements)} 个评论元素")
            
            if not comment_elements:
                return {'comments': [], 'comment_tree': {}, 'total_count': 0}
            
            # 提取所有评论的基本信息
            comments = []
            comment_map = {}  # 用于构建评论树的映射
            
            for element in comment_elements:
                comment_data = self._extract_comment_data(element, comment_xpath, base_url)
                if comment_data:
                    comments.append(comment_data)
                    comment_map[comment_data['comment_id']] = comment_data
            
            # 构建评论树结构
            comment_tree = self._build_comment_tree(comments)
            
            logger.info(f"成功提取 {len(comments)} 条评论，构建了评论树结构")
            
            return {
                'comments': comments,
                'comment_tree': comment_tree,
                'total_count': len(comments),
                'max_depth': max([c.get('depth', 0) for c in comments]) if comments else 0
            }
            
        except Exception as e:
            logger.error(f"评论提取失败: {str(e)}")
            return {'comments': [], 'comment_tree': {}, 'total_count': 0}
    
    def _extract_comment_data(self, comment_element, comment_xpath, base_url):
        """从评论元素中提取评论数据
        
        Args:
            comment_element: 评论元素
            comment_xpath (dict): 评论字段的XPath配置
            base_url (str, optional): 基础URL
            
        Returns:
            dict: 评论数据
        """
        try:
            comment_data = {
                'comment_id': '',
                'parent_id': '',
                'author': '',
                'text': '',
                'score': 0,
                'timestamp': '',
                'depth': 0,
                'permalink': '',
                'children': []
            }
            
            # 从元素属性中提取基本信息
            comment_data['comment_id'] = comment_element.get('thingid', '')
            comment_data['parent_id'] = comment_element.get('parentid', '')
            comment_data['author'] = comment_element.get('author', '')
            comment_data['permalink'] = comment_element.get('permalink', '')
            
            # 处理深度信息
            try:
                comment_data['depth'] = int(comment_element.get('depth', '0'))
            except (ValueError, TypeError):
                comment_data['depth'] = 0
            
            # 处理分数信息
            try:
                comment_data['score'] = int(comment_element.get('score', '0'))
            except (ValueError, TypeError):
                comment_data['score'] = 0
            
            # 使用XPath配置提取其他字段
            for field_name, xpath_config in comment_xpath.items():
                if isinstance(xpath_config, str):
                    # 简单的XPath字符串
                    xpath_selector = xpath_config
                elif isinstance(xpath_config, dict) and 'xpath' in xpath_config:
                    # 复杂的XPath配置
                    xpath_selector = xpath_config['xpath']
                else:
                    continue
                
                try:
                    # 在当前评论元素内查找
                    result = comment_element.xpath(xpath_selector)
                    if result:
                        if field_name == 'text':
                            # 对于文本内容，提取所有文本并合并
                            if isinstance(result[0], str):
                                comment_data[field_name] = result[0].strip()
                            else:
                                comment_data[field_name] = self._extract_text_from_element(result[0])
                        elif field_name == 'timestamp':
                            # 对于时间戳，提取datetime属性或文本内容
                            if hasattr(result[0], 'get'):
                                datetime_attr = result[0].get('datetime', '')
                                if datetime_attr:
                                    comment_data[field_name] = datetime_attr
                                else:
                                    comment_data[field_name] = self._extract_text_from_element(result[0])
                            else:
                                comment_data[field_name] = str(result[0]).strip()
                        elif field_name == 'permalink' and base_url:
                            # 处理永久链接的相对URL
                            permalink = str(result[0]).strip() if result[0] else ''
                            if permalink and not permalink.startswith(('http://', 'https://')):
                                comment_data[field_name] = urljoin(base_url, permalink)
                            else:
                                comment_data[field_name] = permalink
                        else:
                            # 其他字段直接提取文本内容
                            if isinstance(result[0], str):
                                comment_data[field_name] = result[0].strip()
                            else:
                                comment_data[field_name] = self._extract_text_from_element(result[0])
                except Exception as e:
                    logger.debug(f"提取评论字段 {field_name} 失败: {str(e)}")
                    continue
            
            return comment_data
            
        except Exception as e:
            logger.debug(f"提取评论数据失败: {str(e)}")
            return None
    
    def _build_comment_tree(self, comments):
        """构建评论树结构
        
        Args:
            comments (list): 评论列表
            
        Returns:
            dict: 评论树结构
        """
        try:
            # 创建评论映射
            comment_map = {comment['comment_id']: comment for comment in comments}
            root_comments = []
            
            # 构建父子关系
            for comment in comments:
                parent_id = comment.get('parent_id', '')
                
                # 如果有父评论ID且父评论存在
                if parent_id and parent_id in comment_map:
                    parent_comment = comment_map[parent_id]
                    if 'children' not in parent_comment:
                        parent_comment['children'] = []
                    parent_comment['children'].append(comment)
                else:
                    # 顶级评论
                    root_comments.append(comment)
            
            # 按深度和分数排序
            def sort_comments(comment_list):
                comment_list.sort(key=lambda x: (-int(x.get('score', 0)) if str(x.get('score', 0)).isdigit() else 0, x.get('depth', 0)))
                for comment in comment_list:
                    if comment.get('children'):
                        sort_comments(comment['children'])
            
            sort_comments(root_comments)
            
            return {
                'root_comments': root_comments,
                'total_threads': len(root_comments),
                'comment_map': comment_map
            }
            
        except Exception as e:
            logger.error(f"构建评论树失败: {str(e)}")
            return {'root_comments': [], 'total_threads': 0, 'comment_map': {}}
    
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