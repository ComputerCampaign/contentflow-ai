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
    """爬虫配置模型 - 对应crawler.py的命令行参数"""
    
    __tablename__ = 'crawler_configs'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 对应crawler.py命令行参数的字段（严格按照L85-102）
    # --url: 要爬取的网页URL（在任务提交时指定，不在配置中存储）
    # --task-id: 任务ID（在创建任务时动态生成，不在配置中存储）
    
    # --output: 输出目录，用于临时文件和日志
    output = db.Column(db.String(500))  # 对应--output参数
    
    # --data-dir: 数据存储目录，用于保存图片和元数据
    data_dir = db.Column(db.String(500))  # 对应--data-dir参数
    
    # --use-selenium: 使用Selenium和ChromeDriver进行爬取
    use_selenium = db.Column(db.Boolean, default=False)  # 对应--use-selenium参数
    
    # --timeout: 请求超时时间，单位为秒
    timeout = db.Column(db.Integer, default=30)  # 对应--timeout参数
    
    # --retry: 失败重试次数
    retry = db.Column(db.Integer, default=3)  # 对应--retry参数
    
    # --config: 配置文件路径（默认为'config.json'）
    config = db.Column(db.String(500), default='config.json')  # 对应--config参数
    
    # --email-notification: 是否启用邮件通知
    email_notification = db.Column(db.Boolean, default=False)  # 对应--email-notification参数
    
    # Selenium 配置参数
    # --headless: Selenium是否使用无头模式
    headless = db.Column(db.Boolean, default=True)  # 对应--headless参数
    
    # --proxy: Selenium使用的代理服务器地址
    proxy = db.Column(db.String(200))  # 对应--proxy参数
    
    # --page-load-wait: Selenium页面加载等待时间，单位为秒
    page_load_wait = db.Column(db.Integer, default=10)  # 对应--page-load-wait参数
    
    # --user-agent: Selenium使用的用户代理字符串
    user_agent = db.Column(db.String(500))  # 对应--user-agent参数
    
    # --rule-ids: XPath规则ID列表，用逗号分隔
    rule_ids = db.Column(db.String(500))  # 对应--rule-ids参数，存储逗号分隔的规则ID
    
    # --enable-xpath: 启用XPath选择器
    enable_xpath = db.Column(db.Boolean, default=False)  # 对应--enable-xpath参数
    
    # --list-rules: 列出所有可用的XPath规则（这是一个动作参数，不需要存储）
    
    # 时间戳字段保留
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 关联字段（移除外键约束）
    user_id = db.Column(db.String(36), nullable=False)  # 用户ID
    
    # 移除关联关系 - 使用简化的数据库设计
    
    def __init__(self, name, user_id, **kwargs):
        self.name = name
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_run_stats(self, success=True):
        """更新运行统计 - 已移除统计字段"""
        # 统计字段已从模型中移除
        pass
    
    def get_success_rate(self):
        """获取成功率 - 已移除统计字段"""
        # 统计字段已从模型中移除
        return 0
    
    def validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 验证基本配置
        if not self.name or len(self.name.strip()) == 0:
            errors.append("配置名称不能为空")
        
        if self.timeout <= 0:
            errors.append("超时时间必须大于0")
            
        if self.retry < 0:
            errors.append("重试次数不能小于0")
        
        return errors
    
    def get_latest_results(self, limit=10):
        """获取最新的爬取结果"""
        from backend.models.crawler import CrawlerResult
        return CrawlerResult.query.filter_by(config_id=self.id).order_by(CrawlerResult.created_at.desc()).limit(limit).all()
    
    def to_dict(self, include_results=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            # 对应crawler.py命令行参数的字段
            'output': self.output,
            'data_dir': self.data_dir,
            'use_selenium': self.use_selenium,
            'timeout': self.timeout,
            'retry': self.retry,
            'config': self.config,
            'email_notification': self.email_notification,
            # Selenium配置
            'headless': self.headless,
            'proxy': self.proxy,
            'page_load_wait': self.page_load_wait,
            'user_agent': self.user_agent,
            # XPath配置
            'rule_ids': self.rule_ids,
            'enable_xpath': self.enable_xpath,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
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
    page_metadata = db.Column(db.JSON)  # 页面元数据
    
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
    
    # 关联字段（移除外键约束）
    config_id = db.Column(db.String(36), nullable=False)  # 爬虫配置ID
    task_execution_id = db.Column(db.String(36))  # 任务执行ID
    
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
            'page_metadata': self.page_metadata,
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