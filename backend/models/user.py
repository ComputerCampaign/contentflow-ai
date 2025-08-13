#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
import uuid


class User(db.Model):
    """用户模型"""
    
    __tablename__ = 'users'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    
    # 权限和状态
    role = db.Column(db.Enum('user', 'premium', 'admin', name='user_role'), 
                     default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # 使用统计
    api_calls_today = db.Column(db.Integer, default=0)
    api_calls_total = db.Column(db.Integer, default=0)
    last_api_call = db.Column(db.DateTime)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # 移除关联关系 - 使用简化的数据库设计
    
    def __init__(self, username, email, password, display_name=None, role='user'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.display_name = display_name or username
        self.role = role
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_tokens(self):
        """生成JWT令牌"""
        access_token = create_access_token(
            identity=self.id,
            additional_claims={
                'username': self.username,
                'role': self.role
            }
        )
        refresh_token = create_refresh_token(identity=self.id)
        return access_token, refresh_token
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def increment_api_calls(self):
        """增加API调用次数"""
        now = datetime.utcnow()
        
        # 如果是新的一天，重置今日调用次数
        if (self.last_api_call is None or 
            self.last_api_call.date() != now.date()):
            self.api_calls_today = 0
        
        self.api_calls_today += 1
        self.api_calls_total += 1
        self.last_api_call = now
        db.session.commit()
    
    def get_api_limit(self):
        """获取API调用限制"""
        limits = {
            'user': 100,
            'premium': 1000,
            'admin': 10000
        }
        return limits.get(self.role, 100)
    
    def can_make_api_call(self):
        """检查是否可以进行API调用"""
        if not self.is_active:
            return False
        return self.api_calls_today < self.get_api_limit()
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'api_calls_today': self.api_calls_today,
                'api_calls_total': self.api_calls_total,
                'api_limit': self.get_api_limit()
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'