#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理器，用于加载和管理XPath规则
"""

import os
import json
from urllib.parse import urlparse
from config import config

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class XPathManager:
    """XPath规则管理器，用于加载和管理XPath规则"""
    
    def __init__(self):
        """初始化XPath规则管理器"""
        self.enabled = config.get('crawler', 'xpath_config', {}).get('enabled', False)
        self.rules_path = config.get('crawler', 'xpath_config', {}).get('rules_path', 'config/xpath_rules.json')
        self.default_rule_id = config.get('crawler', 'xpath_config', {}).get('default_rule_id', 'general_article')
        self.rules = []
        
        if self.enabled:
            self._load_rules()
    
    def _load_rules(self):
        """加载XPath规则"""
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保我们获取的是规则列表，而不是整个JSON对象
                    self.rules = data.get('rules', [])
                logger.info(f"已加载 {len(self.rules)} 条XPath规则")
            else:
                logger.warning(f"XPath规则文件不存在: {self.rules_path}")
        except Exception as e:
            logger.error(f"加载XPath规则失败: {str(e)}")
    
    def get_rule_for_url(self, url):
        """根据URL获取匹配的XPath规则
        
        Args:
            url (str): 网页URL
            
        Returns:
            dict: 匹配的XPath规则，如果没有匹配则返回默认规则
        """
        if not self.enabled or not self.rules:
            return None
        
        # 解析URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # 查找匹配的规则
        for rule in self.rules:
            # 检查域名匹配
            if 'domain' in rule and domain:
                if isinstance(rule['domain'], list):
                    if not any(d in domain for d in rule['domain']):
                        continue
                elif rule['domain'] not in domain:
                    continue
            
            # 检查路径匹配
            if 'path_pattern' in rule and path:
                import re
                if not re.search(rule['path_pattern'], path):
                    continue
            
            # 找到匹配的规则
            logger.info(f"找到匹配的XPath规则: {rule.get('id', 'unknown')}")
            return rule
        
        # 如果没有匹配的规则，返回默认规则
        default_rule = next((r for r in self.rules if r.get('id') == self.default_rule_id), None)
        if default_rule:
            logger.info(f"使用默认XPath规则: {self.default_rule_id}")
            return default_rule
        
        logger.warning("未找到匹配的XPath规则，也没有默认规则")
        return None
    
    def get_rule_by_id(self, rule_id):
        """根据规则ID获取XPath规则
        
        Args:
            rule_id (str): 规则ID
            
        Returns:
            dict: 匹配的XPath规则，如果没有匹配则返回None
        """
        if not self.enabled or not self.rules:
            return None
        
        rule = next((r for r in self.rules if r.get('id') == rule_id), None)
        if rule:
            logger.info(f"找到ID为 {rule_id} 的XPath规则")
            return rule
        
        logger.warning(f"未找到ID为 {rule_id} 的XPath规则")
        return None
    
    def list_rules(self):
        """列出所有可用的XPath规则
        
        Returns:
            list: 规则列表，每个规则包含id、name和description
        """
        if not self.enabled or not self.rules:
            return []
        
        return [{
            'id': rule.get('id', 'unknown'),
            'name': rule.get('name', 'Unnamed Rule'),
            'description': rule.get('description', ''),
            'domain': rule.get('domain', 'any')
        } for rule in self.rules]
    
    def get_xpath_selector(self, rule):
        """从规则中获取XPath选择器
        
        Args:
            rule (dict): XPath规则
            
        Returns:
            str: XPath选择器
        """
        if not rule or 'xpath' not in rule:
            return None
        
        return rule['xpath']
    
    def get_rule_options(self, rule):
        """从规则中获取选项
        
        Args:
            rule (dict): XPath规则
            
        Returns:
            dict: 规则选项
        """
        if not rule or 'options' not in rule:
            return {}
        
        return rule['options']