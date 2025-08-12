#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理器，用于加载和管理XPath规则
重构版本：代码清晰，功能分离，便于扩展
"""

import os
import json
import re
from urllib.parse import urlparse
from lxml import etree

from crawler.config import crawler_config
from crawler.logger import setup_logger

logger = setup_logger(__name__, file_path=__file__)


class XPathManager:
    """XPath规则管理器，用于加载和管理XPath规则"""
    
    def __init__(self):
        """初始化XPath规则管理器"""
        self.enabled = crawler_config.get('xpath', {}).get('enabled', False)
        self.rules_path = crawler_config.get('xpath', {}).get('rules_path', 'config/xpath_rules.json')
        self.default_rule_id = crawler_config.get('xpath', {}).get('default_rule_id', 'general_article')
        self.rules = []
        
        logger.info(f"XPath管理器初始化 - enabled: {self.enabled}, rules_path: {self.rules_path}")
        logger.info(f"XPath配置: {crawler_config.get('xpath', {})}")
        
        if self.enabled:
            self._load_rules()
        else:
            logger.warning("XPath管理器被禁用")
    
    def _load_rules(self):
        """加载XPath规则"""
        try:
            if not os.path.exists(self.rules_path):
                logger.warning(f"XPath规则文件不存在: {self.rules_path}")
                return
                
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
            
            logger.info(f"已加载 {len(self.rules)} 条XPath规则")
        except Exception as e:
            logger.error(f"加载XPath规则失败: {str(e)}")

    def get_rule_by_id(self, rule_id):
        """根据规则ID获取XPath规则"""
        if not self.enabled or not self.rules:
            return None
        
        rule = next((r for r in self.rules if r.get('id') == rule_id), None)
        if rule:
            logger.info(f"找到ID为 {rule_id} 的XPath规则")
            logger.debug(f"规则内容: {json.dumps(rule, ensure_ascii=False, indent=2)}")
        else:
            logger.warning(f"未找到ID为 {rule_id} 的XPath规则")
        
        return rule
    
    def get_rules_by_ids(self, rule_ids):
        """根据规则ID列表获取多个XPath规则"""
        if not self.enabled or not self.rules or not rule_ids:
            return []
        
        matched_rules = [rule for rule_id in rule_ids 
                        for rule in [self.get_rule_by_id(rule_id)] if rule]
        
        logger.info(f"找到 {len(matched_rules)} 个匹配的XPath规则")
        return matched_rules
    
    def list_rules(self):
        """列出所有可用的XPath规则"""
        if not self.enabled or not self.rules:
            return []
        
        return [{
            'id': rule.get('id', 'unknown'),
            'name': rule.get('name', 'Unnamed Rule'),
            'description': rule.get('description', ''),
            'domain': rule.get('domain', 'any')
        } for rule in self.rules]
    
    def match_rule_by_url(self, url):
        """根据URL匹配XPath规则"""
        if not self.enabled or not self.rules:
            return None
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        for rule in self.rules:
            domain_patterns = rule.get('domain_patterns', [])
            if any(pattern in domain or domain in pattern for pattern in domain_patterns):
                logger.info(f"找到匹配域名 {domain} 的XPath规则: {rule['id']}")
                logger.debug(f"匹配到的规则内容: {json.dumps(rule, ensure_ascii=False, indent=2)}")
                return rule
        
        return None
    
    def extract_images_from_html(self, html_content, rule):
        """从HTML内容中提取图片信息"""
        images = []
        
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            elements = tree.xpath(rule['xpath'])
            
            if not elements:
                logger.warning(f"图片提取：XPath规则未匹配到任何元素: {rule['xpath']}")
                return images
            
            xpath_selects_img_directly = self._is_xpath_selecting_img_directly(rule['xpath'])
            
            if xpath_selects_img_directly:
                # XPath直接选择img标签
                img_elements = [elem for elem in elements if elem.tag == 'img']
                logger.info(f"图片提取：XPath直接选择了 {len(img_elements)} 个img标签")
            else:
                # XPath选择容器元素，在其中查找img标签
                img_elements = []
                for element in elements:
                    inner_imgs = element.xpath('.//img')
                    img_elements.extend(inner_imgs)
                logger.info(f"图片提取：在容器元素中找到 {len(img_elements)} 个img标签")
            
            for img in img_elements:
                img_url = img.get('src')
                if img_url:
                    images.append({
                        'url': img_url,
                        'alt': img.get('alt', ''),
                        'xpath_rule': rule['id']
                    })
            
            logger.info(f"图片提取：从规则 {rule['id']} 提取到 {len(images)} 张图片")
            
        except Exception as e:
            logger.error(f"图片提取失败: {str(e)}")
        
        return images
    
    def extract_comments_from_html(self, html_content, rule):
        """从HTML内容中提取评论信息"""
        if 'comment_xpath' not in rule:
            return []
        
        comments = []
        comment_xpath_config = rule.get('comment_xpath', {})
        
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 应用XPath选择器
            comment_elements = tree.xpath(rule['xpath'])
            
            if not comment_elements:
                logger.warning(f"评论提取：XPath规则未匹配到任何元素: {rule['xpath']}")
                return comments
            
            for element in comment_elements:
                comment_data = self._extract_single_comment(element, comment_xpath_config, rule['id'])
                if comment_data:
                    comments.append(comment_data)
            
            logger.info(f"评论提取：从规则 {rule['id']} 提取到 {len(comments)} 条评论")
                    
        except Exception as e:
            logger.error(f"评论提取失败: {str(e)}")
        
        return comments
    
    def apply_multiple_rules(self, html_content, url, rule_ids=None):
        """应用多个XPath规则解析HTML内容"""
        if not self.enabled or not self.rules:
            return None
        
        rules_to_apply = self._get_rules_to_apply(url, rule_ids)
        if not rules_to_apply:
            logger.warning("未找到可应用的XPath规则")
            return None
        
        logger.info(f"应用 {len(rules_to_apply)} 个XPath规则")
        
        combined_result = {
            'xpath_rules_used': [],
            'images': [],
            'comments': []
        }
        
        for rule in rules_to_apply:
            logger.info(f"应用XPath规则: {rule['name']} ({rule['id']})")
            logger.debug(f"当前应用的规则内容: {json.dumps(rule, ensure_ascii=False, indent=2)}")
            
            combined_result['xpath_rules_used'].append(rule['id'])
            
            # 独立进行图片提取
            images = self.extract_images_from_html(html_content, rule)
            self._merge_unique_images(combined_result['images'], images)
            
            # 独立进行评论提取
            comments = self.extract_comments_from_html(html_content, rule)
            combined_result['comments'].extend(comments)
        
        combined_result['comments_count'] = len(combined_result['comments'])
        
        logger.info(f"多规则XPath提取到 {len(combined_result['images'])} 张图片, {len(combined_result['comments'])} 条评论")
        
        return combined_result
    
    def apply_rules(self, html_content, url):
        """应用XPath规则解析HTML内容"""
        if not self.enabled or not self.rules:
            return None
        
        matched_rule = self.match_rule_by_url(url)
        if not matched_rule:
            matched_rule = self.get_rule_by_id(self.default_rule_id)
        
        if not matched_rule:
            logger.warning("未找到匹配的XPath规则")
            return None
        
        logger.info(f"使用XPath规则: {matched_rule['name']} ({matched_rule['id']})")
        logger.debug(f"当前使用的规则内容: {json.dumps(matched_rule, ensure_ascii=False, indent=2)}")
        
        # 独立进行图片提取
        images = self.extract_images_from_html(html_content, matched_rule)
        
        # 独立进行评论提取
        comments = self.extract_comments_from_html(html_content, matched_rule)
        
        logger.info(f"XPath规则提取到 {len(images)} 张图片, {len(comments)} 条评论")
        
        return {
            'xpath_rule_used': matched_rule['id'],
            'images': images,
            'comments': comments,
            'comments_count': len(comments)
        }
    
    def _is_xpath_selecting_img_directly(self, xpath):
        """检查XPath是否直接选择img标签"""
        return (xpath.strip().endswith('img') or 
                '/img[' in xpath or 
                '//img[' in xpath)
    
    def _get_rules_to_apply(self, url, rule_ids):
        """获取要应用的规则列表"""
        if rule_ids:
            return self.get_rules_by_ids(rule_ids)
        
        matched_rule = self.match_rule_by_url(url)
        if matched_rule:
            return [matched_rule]
        
        default_rule = self.get_rule_by_id(self.default_rule_id)
        return [default_rule] if default_rule else []
    
    def _merge_unique_images(self, existing_images, new_images):
        """合并图片列表，避免重复"""
        existing_urls = {img['url'] for img in existing_images}
        for img in new_images:
            if img['url'] not in existing_urls:
                existing_images.append(img)
                existing_urls.add(img['url'])
    
    def _log_matched_elements(self, elements):
        """记录匹配到的元素信息"""
        for i, element in enumerate(elements[:3]):  # 只记录前3个元素
            logger.info(f"匹配元素 {i+1}: 标签={element.tag}, 属性={dict(element.attrib)}")
            if element.tag == 'img':
                logger.info(f"  - src: {element.get('src')}")
                logger.info(f"  - alt: {element.get('alt')}")
                logger.info(f"  - class: {element.get('class')}")
    
    def _extract_single_comment(self, element, comment_xpath_config, rule_id):
        """从单个元素中提取评论数据"""
        comment_data = {}
        
        # 提取评论文本
        if 'text' in comment_xpath_config:
            text_elements = element.xpath(comment_xpath_config['text'])
            if text_elements:
                text_content = self._extract_text_content(text_elements[0])
                if text_content:
                    comment_data['text'] = text_content
        
        # 提取作者信息
        if 'author' in comment_xpath_config:
            author_elements = element.xpath(comment_xpath_config['author'])
            if author_elements:
                author_content = self._extract_text_content(author_elements[0])
                if author_content:
                    comment_data['author'] = author_content
        
        # 提取时间戳
        if 'timestamp' in comment_xpath_config:
            time_elements = element.xpath(comment_xpath_config['timestamp'])
            if time_elements:
                comment_data['timestamp'] = str(time_elements[0]).strip()
        
        # 提取评分/点赞数
        if 'score' in comment_xpath_config:
            score_elements = element.xpath(comment_xpath_config['score'])
            if score_elements:
                score = self._extract_score(score_elements[0])
                if score is not None:
                    comment_data['score'] = score
        
        # 提取互动数据
        if 'interactions' in comment_xpath_config:
            interaction_elements = element.xpath(comment_xpath_config['interactions'])
            comment_data['interactions'] = len(interaction_elements)
        
        # 验证并返回评论数据
        if comment_data.get('text') and len(comment_data['text']) > 5:
            comment_data['xpath_rule'] = rule_id
            comment_data['text'] = comment_data['text'][:500]  # 限制长度
            return comment_data
        
        return None
    
    def _extract_text_content(self, element):
        """提取元素的文本内容"""
        if isinstance(element, str):
            return element.strip()
        elif hasattr(element, 'text_content'):
            return element.text_content().strip()
        else:
            return str(element).strip()
    
    def _extract_score(self, element):
        """提取评分数字"""
        try:
            score_text = str(element).strip()
            numbers = re.findall(r'\d+', score_text)
            return int(numbers[0]) if numbers else None
        except:
            return None