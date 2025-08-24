#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt管理模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class PromptConfig(db.Model):
    """Prompt配置模型 - 存储AI内容生成的提示词模板"""
    
    __tablename__ = 'prompt_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)  # Prompt名称
    description = db.Column(db.Text)  # Prompt描述
    type = db.Column(db.String(50), nullable=False, default='content')  # Prompt类型：content, title, summary, keywords
    
    # Prompt内容
    content = db.Column(db.Text, nullable=False)  # 提示词内容
    variables = db.Column(db.Text)  # 变量说明（JSON格式存储）
    
    # 状态
    status = db.Column(db.String(20), default='active')  # 状态：active, inactive
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0)  # 使用次数
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 用户ID
    user_id = db.Column(db.String(36), nullable=False)
    
    def __init__(self, name, content, user_id, **kwargs):
        self.name = name
        self.content = content
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """转换为字典格式"""
        variables_data = None
        if self.variables:
            try:
                variables_data = json.loads(self.variables)
            except:
                variables_data = self.variables
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'content': self.content,
            'variables': variables_data,
            'status': self.status,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    def set_variables(self, variables_dict):
        """设置变量说明"""
        if isinstance(variables_dict, dict):
            self.variables = json.dumps(variables_dict, ensure_ascii=False)
        else:
            self.variables = str(variables_dict)
    
    def get_variables(self):
        """获取变量说明"""
        if not self.variables:
            return {}
        try:
            return json.loads(self.variables)
        except:
            return {}
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_by_type(cls, prompt_type, user_id, status='active'):
        """根据类型获取Prompt"""
        return cls.query.filter_by(
            type=prompt_type, 
            user_id=user_id, 
            status=status
        ).all()
    
    @classmethod
    def get_active_prompts(cls, user_id):
        """获取用户的所有活跃Prompt"""
        return cls.query.filter_by(
            user_id=user_id, 
            status='active'
        ).order_by(cls.updated_at.desc()).all()
    
    def __repr__(self):
        return f'<PromptConfig {self.name} ({self.type}))>'