#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容生成配置模型
"""

from backend.extensions import db
from datetime import datetime
import uuid


class AIContentConfig(db.Model):
    """AI内容生成配置模型 - 对应ai_content_generator的配置"""
    
    __tablename__ = 'ai_content_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # AI模型配置
    model_name = db.Column(db.String(100), default='doubao-pro-4k')  # 使用的AI模型
    api_key_env = db.Column(db.String(100), default='ARK_API_KEY')  # API密钥环境变量名
    base_url = db.Column(db.String(500))  # API基础URL
    
    # 内容生成配置
    prompt_type = db.Column(db.String(50), default='blog_post')  # 提示词类型
    custom_prompt = db.Column(db.Text)  # 自定义提示词
    max_tokens = db.Column(db.Integer, default=2000)  # 最大生成token数
    temperature = db.Column(db.Float, default=0.7)  # 生成温度
    
    # 输出配置
    output_format = db.Column(db.Enum('markdown', 'html', 'text', name='output_format'), 
                             default='markdown')  # 输出格式
    include_images = db.Column(db.Boolean, default=True)  # 是否包含图片
    include_metadata = db.Column(db.Boolean, default=True)  # 是否包含元数据
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 用户ID
    user_id = db.Column(db.String(36), nullable=False)
    
    def __init__(self, name, user_id, **kwargs):
        self.name = name
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_name': self.model_name,
            'api_key_env': self.api_key_env,
            'base_url': self.base_url,
            'prompt_type': self.prompt_type,
            'custom_prompt': self.custom_prompt,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'output_format': self.output_format,
            'include_images': self.include_images,
            'include_metadata': self.include_metadata,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_ai_generator_params(self):
        """获取AI内容生成器参数"""
        params = {
            'model': self.model_name,
            'max-tokens': self.max_tokens,
            'temperature': self.temperature,
            'output-format': self.output_format
        }
        
        if self.custom_prompt:
            params['custom-prompt'] = self.custom_prompt
        
        if self.base_url:
            params['base-url'] = self.base_url
            
        return params
    
    def __repr__(self):
        return f'<AIContentConfig {self.name}>'