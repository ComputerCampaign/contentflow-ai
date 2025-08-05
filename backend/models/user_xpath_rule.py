#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户XPath规则模型
"""

from datetime import datetime
from backend.models.base import db


class UserXPathRule(db.Model):
    """用户XPath规则模型"""
    __tablename__ = 'user_xpath_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    xpath = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="xpath_rules")
    
    def __repr__(self):
        return f"<UserXPathRule {self.rule_name}>"
    
    def is_valid_xpath(self):
        """验证XPath语法是否正确"""
        try:
            from lxml import etree
            etree.XPath(self.xpath)
            return True
        except Exception:
            return False
    
    def get_domain_rules_count(self):
        """获取同域名下的规则数量"""
        return self.__class__.query.filter_by(
            user_id=self.user_id,
            domain=self.domain
        ).count()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'domain': self.domain,
            'xpath': self.xpath,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None
        }
    
    @classmethod
    def create_rule(cls, user, rule_name, domain, xpath, description=None):
        """创建新的XPath规则"""
        # 检查用户是否有权限创建规则
        if not user.can_create_xpath_rule():
            raise ValueError("用户已达到XPath规则创建上限")
        
        # 检查规则名称是否重复
        existing_rule = cls.query.filter_by(
            user_id=user.id,
            rule_name=rule_name
        ).first()
        
        if existing_rule:
            raise ValueError(f"规则名称 '{rule_name}' 已存在")
        
        rule = cls(
            user=user,
            rule_name=rule_name,
            domain=domain,
            xpath=xpath,
            description=description
        )
        
        # 验证XPath语法
        if not rule.is_valid_xpath():
            raise ValueError("XPath语法错误")
        
        db.session.add(rule)
        db.session.commit()
        
        return rule
    
    @classmethod
    def get_user_rules(cls, user_id, domain=None):
        """获取用户的XPath规则"""
        query = cls.query.filter_by(user_id=user_id)
        
        if domain:
            query = query.filter_by(domain=domain)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_name_and_user(cls, rule_name, user_id):
        """根据规则名称和用户ID获取规则"""
        return cls.query.filter_by(
            rule_name=rule_name,
            user_id=user_id
        ).first()
    
    @classmethod
    def get_domain_rules(cls, domain, user_id=None):
        """获取指定域名的规则"""
        query = cls.query.filter_by(domain=domain)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.all()