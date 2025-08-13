#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XPath配置管理工具
"""

import json
import os
from typing import List, Dict, Any
from backend.models.xpath import XPathConfig
from backend.extensions import db


class XPathConfigManager:
    """XPath配置管理器"""
    
    def __init__(self, xpath_rules_path: str = None):
        """
        初始化XPath配置管理器
        
        Args:
            xpath_rules_path: xpath_rules.json文件路径
        """
        if xpath_rules_path is None:
            # 默认路径
            self.xpath_rules_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'crawler', 'config', 'xpath', 'xpath_rules.json'
            )
        else:
            self.xpath_rules_path = xpath_rules_path
    
    def write_xpath_configs_to_file(self, xpath_config_ids: List[str] = None) -> bool:
        """
        将数据库中的XPath配置写入JSON文件
        
        Args:
            xpath_config_ids: 要写入的XPath配置ID列表，如果为None则写入所有活跃配置
            
        Returns:
            bool: 是否成功写入
        """
        try:
            # 查询XPath配置
            if xpath_config_ids:
                xpath_configs = XPathConfig.query.filter(
                    XPathConfig.id.in_(xpath_config_ids),
                    XPathConfig.status == 'active'
                ).all()
            else:
                xpath_configs = XPathConfig.query.filter(
                    XPathConfig.status == 'active'
                ).all()
            
            # 转换为JSON格式
            rules_data = {
                "rules": []
            }
            
            for config in xpath_configs:
                rule_data = {
                    "id": config.rule_id,
                    "name": config.name,
                    "description": config.description or "",
                    "domain_patterns": config.domain_patterns,
                    "xpath": config.xpath,
                    "rule_type": config.rule_type,
                    "field_name": config.field_name
                }
                
                # 如果有评论XPath配置，添加到规则中
                if config.comment_xpath:
                    rule_data["comment_xpath"] = config.comment_xpath
                
                rules_data["rules"].append(rule_data)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.xpath_rules_path), exist_ok=True)
            
            # 写入文件
            with open(self.xpath_rules_path, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=4)
            
            return True
            
        except Exception as e:
            print(f"写入XPath配置文件失败: {str(e)}")
            return False
    
    def load_xpath_configs_from_file(self) -> List[Dict[str, Any]]:
        """
        从JSON文件加载XPath配置
        
        Returns:
            List[Dict]: XPath配置列表
        """
        try:
            if not os.path.exists(self.xpath_rules_path):
                return []
            
            with open(self.xpath_rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('rules', [])
            
        except Exception as e:
            print(f"加载XPath配置文件失败: {str(e)}")
            return []
    
    def get_xpath_config_by_rule_ids(self, rule_ids: List[str]) -> List[str]:
        """
        根据规则ID列表获取对应的XPath配置ID
        
        Args:
            rule_ids: 规则ID列表
            
        Returns:
            List[str]: XPath配置ID列表
        """
        try:
            xpath_configs = XPathConfig.query.filter(
                XPathConfig.rule_id.in_(rule_ids),
                XPathConfig.status == 'active'
            ).all()
            
            return [config.id for config in xpath_configs]
            
        except Exception as e:
            print(f"获取XPath配置ID失败: {str(e)}")
            return []
    
    def validate_xpath_rules_file(self) -> bool:
        """
        验证xpath_rules.json文件格式是否正确
        
        Returns:
            bool: 文件格式是否正确
        """
        try:
            rules = self.load_xpath_configs_from_file()
            
            for rule in rules:
                required_fields = ['id', 'name', 'domain_patterns', 'xpath', 'rule_type', 'field_name']
                for field in required_fields:
                    if field not in rule:
                        return False
            
            return True
            
        except Exception:
            return False


# 全局实例
xpath_manager = XPathConfigManager()