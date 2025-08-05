#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.base import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关联
    group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'))
    group = db.relationship("UserGroup", back_populates="users")
    xpath_rules = db.relationship("UserXPathRule", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.group and self.group.name == 'admin'
    
    def can_create_xpath_rule(self):
        """检查是否可以创建XPath规则"""
        if not self.group:
            return False
        
        # 管理员无限制
        if self.group.max_xpath_rules == -1:
            return True
        
        # 检查当前规则数量
        current_count = len(self.xpath_rules)
        return current_count < self.group.max_xpath_rules
    
    def get_allowed_templates(self):
        """获取允许使用的模板列表"""
        if not self.group or not self.group.allowed_templates:
            return []
        
        # 如果包含通配符，返回所有模板
        if '*' in self.group.allowed_templates:
            return ['*']
        
        return self.group.allowed_templates
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'group_id': self.group_id,
            'group_name': self.group.name if self.group else None,
            'xpath_rules_count': len(self.xpath_rules)
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def create_user(cls, username, email, password, group=None):
        """创建新用户"""
        user = cls(
            username=username,
            email=email,
            group=group
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def get_by_username(cls, username):
        """根据用户名获取用户"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def authenticate(cls, username, password):
        """用户认证"""
        user = cls.get_by_username(username)
        if user and user.check_password(password) and user.is_active:
            user.update_last_login()
            return user
        return None