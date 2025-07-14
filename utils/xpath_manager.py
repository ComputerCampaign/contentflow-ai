#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理器，用于加载和管理XPath规则
"""

import os
import json
import logging
from urllib.parse import urlparse
from config import config

# 设置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        if not os.path.exists(self.rules_path):
            logger.warning(f"XPath规则文件不存在: {self.rules_path}")
            logger.info(f"请确保文件路径正确，当前配置的路径为: {self.rules_path}")
            return
        
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
            logger.info(f"已加载 {len(self.rules)} 条XPath规则")
        except Exception as e:
            logger.error(f"加载XPath规则失败: {str(e)}")
    
    def get_rule_by_id(self, rule_id):
        """根据规则ID获取XPath规则
        
        Args:
            rule_id (str): 规则ID
            
        Returns:
            dict or None: XPath规则字典，如果未找到则返回None
        """
        if not self.enabled or not self.rules:
            return None
        
        for rule in self.rules:
            if rule.get('id') == rule_id:
                return rule
        
        return None
    
    def get_rule_by_url(self, url):
        """根据URL获取匹配的XPath规则
        
        Args:
            url (str): 网页URL
            
        Returns:
            dict or None: XPath规则字典，如果未找到则返回None
        """
        if not self.enabled or not self.rules:
            return None
        
        # 解析URL获取域名
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
        except Exception:
            logger.warning(f"解析URL失败: {url}")
            return self.get_rule_by_id(self.default_rule_id)
        
        # 查找匹配的规则
        for rule in self.rules:
            domain_patterns = rule.get('domain_patterns', [])
            for pattern in domain_patterns:
                if pattern.lower() in domain or domain.endswith('.' + pattern.lower()):
                    logger.info(f"找到匹配的XPath规则: {rule.get('name')} (ID: {rule.get('id')})")
                    return rule
        
        # 如果没有找到匹配的规则，返回默认规则
        default_rule = self.get_rule_by_id(self.default_rule_id)
        if default_rule:
            logger.info(f"使用默认XPath规则: {default_rule.get('name')} (ID: {default_rule.get('id')})")
        else:
            logger.warning(f"未找到默认XPath规则: {self.default_rule_id}")
        
        return default_rule
    
    def get_xpath_by_url(self, url):
        """根据URL获取匹配的XPath表达式
        
        Args:
            url (str): 网页URL
            
        Returns:
            str or None: XPath表达式，如果未找到则返回None
        """
        rule = self.get_rule_by_url(url)
        return rule.get('xpath') if rule else None
    
    def get_xpath_by_id(self, rule_id):
        """根据规则ID获取XPath表达式
        
        Args:
            rule_id (str): 规则ID
            
        Returns:
            str or None: XPath表达式，如果未找到则返回None
        """
        rule = self.get_rule_by_id(rule_id)
        return rule.get('xpath') if rule else None

# 创建全局XPath规则管理器实例
xpath_manager = XPathManager()

# 导出XPath规则管理器实例，方便其他模块导入
__all__ = ['xpath_manager']