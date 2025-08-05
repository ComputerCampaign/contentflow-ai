#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置和结果模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class CrawlerConfig(db.Model):
    """爬虫配置模型"""
    
    __tablename__ = 'crawler_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 目标配置
    urls = db.Column(db.JSON, nullable=False)  # 目标URL列表
    
    # 爬取规则
    rules = db.Column(db.JSON, nullable=False)  # 爬取规则配置
    
    # 请求配置
    headers = db.Column(db.JSON)  # 请求头
    cookies = db.Column(db.JSON)  # Cookie
    proxy_config = db.Column(db.JSON)  # 代理配置
    
    # 调度配置
    schedule = db.Column(db.JSON)  # 调度配置
    
    # 限制配置
    rate_limit = db.Column(db.Float, default=1.0)  # 请求间隔（秒）
    max_depth = db.Column(db.Integer, default=1)  # 最大爬取深度
    max_pages = db.Column(db.Integer, default=100)  # 最大页面数
    timeout = db.Column(db.Integer, default=30)  # 请求超时（秒）
    
    # 状态信息
    status = db.Column(db.Enum('active', 'inactive', 'testing', name='config_status'), 
                      default='active', nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开配置
    
    # 统计信息
    total_runs = db.Column(db.Integer, default=0)
    successful_runs = db.Column(db.Integer, default=0)
    failed_runs = db.Column(db.Integer, default=0)
    last_run_at = db.Column(db.DateTime)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 外键
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # 关联关系
    tasks = db.relationship('Task', backref='crawler_config', lazy='dynamic')
    results = db.relationship('CrawlerResult', backref='config', lazy='dynamic',
                             cascade='all, delete-orphan',
                             order_by='CrawlerResult.created_at.desc()')
    
    def __init__(self, name, urls, rules, user_id, **kwargs):
        self.name = name
        self.urls = urls if isinstance(urls, list) else [urls]
        self.rules = rules
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_run_stats(self, success=True):
        """更新运行统计"""
        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        self.last_run_at = datetime.utcnow()
        db.session.commit()
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_runs == 0:
            return 0
        return round((self.successful_runs / self.total_runs) * 100, 2)
    
    def validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 验证URL
        if not self.urls or len(self.urls) == 0:
            errors.append("至少需要一个目标URL")
        
        # 验证规则
        required_rules = ['title_selector', 'content_selector']
        for rule in required_rules:
            if rule not in self.rules:
                errors.append(f"缺少必需的规则: {rule}")
        
        return errors
    
    def get_latest_results(self, limit=10):
        """获取最新的爬取结果"""
        return self.results.limit(limit).all()
    
    def to_dict(self, include_results=False):
        """转换为字典"""
        data = {
            'config_id': self.id,
            'name': self.name,
            'description': self.description,
            'urls': self.urls,
            'rules': self.rules,
            'headers': self.headers,
            'cookies': self.cookies,
            'proxy_config': self.proxy_config,
            'schedule': self.schedule,
            'rate_limit': self.rate_limit,
            'max_depth': self.max_depth,
            'max_pages': self.max_pages,
            'timeout': self.timeout,
            'status': self.status,
            'is_public': self.is_public,
            'total_runs': self.total_runs,
            'success_rate': self.get_success_rate(),
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }
        
        if include_results:
            data['recent_results'] = [result.to_dict() for result in self.get_latest_results(5)]
        
        return data
    
    def __repr__(self):
        return f'<CrawlerConfig {self.name}>'


class CrawlerResult(db.Model):
    """爬虫结果模型"""
    
    __tablename__ = 'crawler_results'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    url = db.Column(db.String(2000), nullable=False)
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    
    # 提取的数据
    extracted_data = db.Column(db.JSON)  # 提取的结构化数据
    metadata = db.Column(db.JSON)  # 页面元数据
    
    # 状态信息
    status = db.Column(db.Enum('success', 'failed', 'partial', name='result_status'), 
                      nullable=False)
    error_message = db.Column(db.Text)
    
    # 技术信息
    response_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # 响应时间（秒）
    content_type = db.Column(db.String(100))
    content_length = db.Column(db.Integer)
    
    # 处理信息
    processing_time = db.Column(db.Float)  # 处理时间（秒）
    retry_count = db.Column(db.Integer, default=0)
    
    # 文件信息
    images = db.Column(db.JSON)  # 图片URL列表
    files = db.Column(db.JSON)  # 文件URL列表
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 外键
    config_id = db.Column(db.String(36), db.ForeignKey('crawler_configs.id'), nullable=False)
    task_execution_id = db.Column(db.String(36), db.ForeignKey('task_executions.id'))
    
    def __init__(self, url, config_id, status='success', **kwargs):
        self.url = url
        self.config_id = config_id
        self.status = status
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_success(self, title=None, content=None, extracted_data=None, **kwargs):
        """设置成功结果"""
        self.status = 'success'
        self.title = title
        self.content = content
        self.extracted_data = extracted_data
        
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
            'result_id': self.id,
            'url': self.url,
            'title': self.title,
            'status': self.status,
            'error_message': self.error_message,
            'extracted_data': self.extracted_data,
            'metadata': self.metadata,
            'response_code': self.response_code,
            'response_time': self.response_time,
            'content_type': self.content_type,
            'content_length': self.content_length,
            'processing_time': self.processing_time,
            'retry_count': self.retry_count,
            'images': self.images,
            'files': self.files,
            'created_at': self.created_at.isoformat(),
            'config_id': self.config_id,
            'task_execution_id': self.task_execution_id
        }
        
        if include_content:
            data['content'] = self.content
        else:
            data['content_preview'] = self.get_content_preview()
        
        return data
    
    def __repr__(self):
        return f'<CrawlerResult {self.url}>'