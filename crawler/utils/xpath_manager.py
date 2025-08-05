#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理器，用于加载和管理XPath规则
"""

import os
import json
from urllib.parse import urlparse

from crawler.config import crawler_config

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class XPathManager:
    """XPath规则管理器，用于加载和管理XPath规则"""
    
    def __init__(self):
        """初始化XPath规则管理器"""
        self.enabled = crawler_config.get('xpath', {}).get('enabled', False)
        self.rules_path = crawler_config.get('xpath', {}).get('rules_path', 'config/xpath_rules.json')
        self.default_rule_id = crawler_config.get('xpath', {}).get('default_rule_id', 'general_article')
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