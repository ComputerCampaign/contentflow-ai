#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理器，用于加载和管理XPath规则
重构版本：只负责规则管理，不包含解析逻辑
"""

import os
import json
from urllib.parse import urlparse

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
    
    def get_default_rule(self):
        """获取默认规则"""
        if not self.enabled or not self.rules:
            return None
        
        return self.get_rule_by_id(self.default_rule_id)
    
    def is_enabled(self):
        """检查XPath管理器是否启用"""
        return self.enabled and bool(self.rules)
    
    def get_rules_for_url(self, url, rule_ids=None):
        """根据URL和规则ID列表获取要应用的规则"""
        if not self.enabled or not self.rules:
            return []
        
        if rule_ids:
            # 使用指定的规则ID列表
            return self.get_rules_by_ids(rule_ids)
        
        # 尝试根据URL匹配规则
        matched_rule = self.match_rule_by_url(url)
        if matched_rule:
            return [matched_rule]
        
        # 使用默认规则
        default_rule = self.get_default_rule()
        return [default_rule] if default_rule else []
    
    def get_rule_xpath(self, rule):
        """获取规则的XPath选择器"""
        if not rule or 'xpath' not in rule:
            return None
        return rule['xpath']
    
    def get_rule_comment_config(self, rule):
        """获取规则的评论配置"""
        if not rule:
            return None
        return rule.get('comment_xpath', {})