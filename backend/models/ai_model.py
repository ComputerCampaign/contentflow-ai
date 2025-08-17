#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class AIModelConfig(db.Model):
    """AI模型配置模型 - 存储AI模型的配置信息"""
    
    __tablename__ = 'ai_model_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)  # 模型显示名称
    model_key = db.Column(db.String(100), nullable=False, unique=True)  # 模型标识符
    description = db.Column(db.Text)  # 模型描述
    
    # API配置
    api_key_env = db.Column(db.String(100), nullable=False)  # API密钥环境变量名
    base_url = db.Column(db.String(500), nullable=False)  # API基础URL
    model = db.Column(db.String(200), nullable=False)  # 实际模型名称
    
    # 生成配置
    max_tokens = db.Column(db.Integer, default=2000)  # 最大生成token数
    temperature = db.Column(db.Float, default=0.7)  # 生成温度
    top_p = db.Column(db.Float, default=0.9)  # top_p参数
    frequency_penalty = db.Column(db.Float, default=0)  # 频率惩罚
    presence_penalty = db.Column(db.Float, default=0)  # 存在惩罚
    
    # 其他配置
    max_retries = db.Column(db.Integer, default=3)  # 最大重试次数
    timeout = db.Column(db.Integer, default=60)  # 超时时间（秒）
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认模型
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 用户ID
    user_id = db.Column(db.String(36), nullable=False)
    
    def __init__(self, name, model_key, api_key_env, base_url, model, user_id, **kwargs):
        self.name = name
        self.model_key = model_key
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.model = model
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'model_key': self.model_key,
            'description': self.description,
            'api_key_env': self.api_key_env,
            'base_url': self.base_url,
            'model': self.model,
            'generation_config': {
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'top_p': self.top_p,
                'frequency_penalty': self.frequency_penalty,
                'presence_penalty': self.presence_penalty
            },
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    def to_models_json_format(self):
        """转换为models.json格式"""
        return {
            'api_key_env': self.api_key_env,
            'base_url': self.base_url,
            'generation_config': {
                'frequency_penalty': self.frequency_penalty,
                'max_tokens': self.max_tokens,
                'presence_penalty': self.presence_penalty,
                'temperature': self.temperature,
                'top_p': self.top_p
            },
            'max_retries': self.max_retries,
            'model': self.model,
            'name': self.name,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_models_json(cls, model_key, model_data, user_id):
        """从models.json格式创建模型实例"""
        generation_config = model_data.get('generation_config', {})
        
        return cls(
            name=model_data.get('name', model_key),
            model_key=model_key,
            api_key_env=model_data.get('api_key_env'),
            base_url=model_data.get('base_url'),
            model=model_data.get('model'),
            user_id=user_id,
            max_tokens=generation_config.get('max_tokens', 2000),
            temperature=generation_config.get('temperature', 0.7),
            top_p=generation_config.get('top_p', 0.9),
            frequency_penalty=generation_config.get('frequency_penalty', 0),
            presence_penalty=generation_config.get('presence_penalty', 0),
            max_retries=model_data.get('max_retries', 3),
            timeout=model_data.get('timeout', 60)
        )
    
    def __repr__(self):
        return f'<AIModelConfig {self.name} ({self.model_key}))>'