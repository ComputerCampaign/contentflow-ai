#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户组模型
"""

from sqlalchemy.dialects.sqlite import JSON
from backend.models.base import db


class UserGroup(db.Model):
    """用户组模型"""
    __tablename__ = 'user_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # 权限配置
    max_xpath_rules = db.Column(db.Integer, default=10)  # 最大XPath规则数量
    allowed_templates = db.Column(JSON)  # 允许使用的博客模板
    
    # 关联
    users = db.relationship("User", back_populates="group")
    
    def __repr__(self):
        return f"<UserGroup {self.name}>"
    
    def is_admin_group(self):
        """检查是否为管理员组"""
        return self.name == 'admin'
    
    def has_unlimited_xpath_rules(self):
        """检查是否有无限XPath规则权限"""
        return self.max_xpath_rules == -1
    
    def can_use_all_templates(self):
        """检查是否可以使用所有模板"""
        return self.allowed_templates and '*' in self.allowed_templates
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_xpath_rules': self.max_xpath_rules,
            'allowed_templates': self.allowed_templates,
            'users_count': len(self.users)
        }
    
    @classmethod
    def create_group(cls, name, description=None, max_xpath_rules=10, allowed_templates=None):
        """创建新用户组"""
        group = cls(
            name=name,
            description=description,
            max_xpath_rules=max_xpath_rules,
            allowed_templates=allowed_templates or []
        )
        
        db.session.add(group)
        db.session.commit()
        
        return group
    
    @classmethod
    def get_by_name(cls, name):
        """根据名称获取用户组"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_admin_group(cls):
        """获取管理员组"""
        return cls.get_by_name('admin')
    
    @classmethod
    def get_default_group(cls):
        """获取默认用户组"""
        return cls.get_by_name('user') or cls.get_by_name('default')