#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XPath配置模型
"""

from backend.extensions import db
from datetime import datetime
import uuid


class XPathConfig(db.Model):
    """XPath配置模型"""
    
    __tablename__ = 'xpath_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    rule_id = db.Column(db.String(100), nullable=False, unique=True)  # 规则ID
    name = db.Column(db.String(200), nullable=False)  # 规则名称
    description = db.Column(db.Text)  # 规则描述
    
    # 域名配置
    domain_patterns = db.Column(db.JSON, nullable=False)  # 域名匹配模式列表
    
    # XPath配置
    xpath = db.Column(db.Text, nullable=False)  # 主XPath表达式
    rule_type = db.Column(db.Enum('text', 'image', 'link', 'data', name='xpath_rule_type'), 
                         nullable=False)  # 规则类型
    field_name = db.Column(db.String(100), nullable=False)  # 字段名称
    
    # 扩展XPath配置（用于复杂提取）
    comment_xpath = db.Column(db.JSON)  # 评论相关的XPath配置
    
    # 状态信息
    status = db.Column(db.Enum('active', 'inactive', 'testing', name='xpath_status'), 
                      default='active', nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开配置
    
    # 统计信息
    usage_count = db.Column(db.Integer, default=0)  # 使用次数
    last_used_at = db.Column(db.DateTime)  # 最后使用时间
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 关联字段（移除外键约束）
    user_id = db.Column(db.String(36), nullable=False)  # 用户ID
    
    def __init__(self, rule_id, name, domain_patterns, xpath, rule_type, field_name, user_id, **kwargs):
        self.rule_id = rule_id
        self.name = name
        self.domain_patterns = domain_patterns if isinstance(domain_patterns, list) else [domain_patterns]
        self.xpath = xpath
        self.rule_type = rule_type
        self.field_name = field_name
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_usage_stats(self, success=True):
        """更新使用统计"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def get_success_rate(self):
        """获取成功率"""
        # 成功率统计已简化，返回固定值
        return 0
    
    def matches_domain(self, url):
        """检查URL是否匹配域名模式"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        for pattern in self.domain_patterns:
            if pattern.lower() in domain:
                return True
        return False
    
    def validate_config(self):
        """验证配置有效性"""
        errors = []
        
        if not self.rule_id or len(self.rule_id.strip()) == 0:
            errors.append("规则ID不能为空")
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("规则名称不能为空")
        
        if not self.domain_patterns or len(self.domain_patterns) == 0:
            errors.append("至少需要一个域名模式")
        
        if not self.xpath or len(self.xpath.strip()) == 0:
            errors.append("XPath表达式不能为空")
        
        if not self.field_name or len(self.field_name.strip()) == 0:
            errors.append("字段名称不能为空")
        
        return errors
    
    def to_dict(self):
        """转换为字典"""
        return {
            'config_id': self.id,
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'domain_patterns': self.domain_patterns,
            'xpath': self.xpath,
            'rule_type': self.rule_type,
            'field_name': self.field_name,
            'comment_xpath': self.comment_xpath,
            'status': self.status,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<XPathConfig {self.rule_id}>'