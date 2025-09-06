#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫结果模型
"""
from backend.extensions import db
from datetime import datetime

class CrawlerResult(db.Model):
    """爬虫结果模型 - 根据实际数据库表结构设计"""
    
    __tablename__ = 'crawler_results'
    
    # 主键 - 使用传入的task_id作为id
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    
    # 基本信息 - 根据数据库表结构
    url = db.Column(db.String(2000), nullable=False)  # varchar(2000)
    title = db.Column(db.String(500))  # varchar(500)
    content = db.Column(db.Text)  # text字段，对应数据库的content
    
    # 提取的数据 - 根据数据库表结构
    extracted_data = db.Column(db.JSON)  # json字段
    page_metadata = db.Column(db.JSON)  # json字段
    images = db.Column(db.JSON)  # json字段
    files = db.Column(db.JSON)  # json字段
    
    # 状态和错误信息 - 根据数据库表结构
    status = db.Column(db.Enum('success', 'failed', 'partial', name='status_enum'), nullable=False)
    error_message = db.Column(db.Text)
    
    # 技术信息 - 根据数据库表结构
    response_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    content_type = db.Column(db.String(100))
    content_length = db.Column(db.Integer)
    processing_time = db.Column(db.Float)
    retry_count = db.Column(db.Integer)
    
    # 时间戳 - 根据数据库表结构
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联字段 - 根据数据库表结构
    config_id = db.Column(db.String(36), nullable=False)  # varchar(36)
    
    def __init__(self, task_id, url, config_id, status='success', **kwargs):
        self.id = task_id  # 直接将task_id赋值给id字段
        self.url = url
        self.config_id = config_id
        self.status = status
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_success(self, title=None, content=None, **kwargs):
        """设置成功结果"""
        self.status = 'success'
        self.title = title
        self.content = content
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_failure(self, error_message, **kwargs):
        """设置失败结果"""
        self.status = 'failed'
        self.error_message = error_message
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_content_preview(self, max_length=200):
        """获取内容预览"""
        if not self.content:
            return ""
        
        content = self.content.strip()
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + "..."
    
    def to_dict(self, include_content=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'extracted_data': self.extracted_data,
            'page_metadata': self.page_metadata,
            'images': self.images,
            'files': self.files,
            'status': self.status,
            'error_message': self.error_message,
            'response_code': self.response_code,
            'response_time': self.response_time,
            'content_type': self.content_type,
            'content_length': self.content_length,
            'processing_time': self.processing_time,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'config_id': self.config_id
        }
        
        if include_content:
            data['content_preview'] = self.get_content_preview()
        
        return data
    
    def __repr__(self):
        return f'<CrawlerResult {self.url}>'