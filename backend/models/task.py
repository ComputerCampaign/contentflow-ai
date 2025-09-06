#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class Task(db.Model):
    """任务模型"""
    
    __tablename__ = 'tasks'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum('crawler', 'content_generation', 'combined', name='task_type'), nullable=False)
    
    # 爬虫任务字段
    url = db.Column(db.String(2000))  # 目标URL（爬虫任务必需）
    
    # 内容生成任务字段
    source_task_id = db.Column(db.String(36))  # 源任务ID（内容生成任务引用的爬虫任务）
    crawler_task_id = db.Column(db.String(36))  # 爬虫任务ID（用于传递给ai_content_generator）
    

    
    # 状态管理
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', 
                              'cancelled', 'paused', name='task_status'), 
                      default='pending', nullable=False)
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # 配置信息
    config = db.Column(db.JSON)  # 任务配置
    priority = db.Column(db.Integer, default=5)  # 1-10，数字越大优先级越高
    
    # 调度信息已移除 - 当前版本不支持定时任务
    last_run = db.Column(db.DateTime)
    
    # 执行统计简化 - 只保留基本统计
    total_executions = db.Column(db.Integer, default=0)
    
    # 结果信息已移除 - 通过TaskExecution记录详细结果
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 逻辑删除
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # 逻辑删除标记
    deleted_at = db.Column(db.DateTime)  # 删除时间
    
    # 关联信息
    user_id = db.Column(db.String(36), nullable=False)  # 用户ID
    crawler_config_id = db.Column(db.String(36))  # 爬虫配置ID
    xpath_config_id = db.Column(db.String(36))  # XPath配置ID
    ai_content_config_id = db.Column(db.String(36))  # AI内容生成配置ID

    
    # 关联关系
    # 移除关系定义
    
    def __init__(self, name, type, user_id, config=None, **kwargs):
        self.name = name
        self.type = type
        self.user_id = user_id
        self.config = config or {}
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_status(self, status, progress=None):
        """更新任务状态"""
        self.status = status
        if progress is not None:
            self.progress = max(0, min(100, progress))
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def start_execution(self):
        """开始执行任务"""
        execution = TaskExecution(
            task_id=self.id,
            status='running'
        )
        db.session.add(execution)
        
        self.status = 'running'
        self.progress = 0
        self.last_run = datetime.utcnow()
        self.total_executions += 1
        
        db.session.commit()
        return execution
    
    def complete_execution(self, execution_id, success=True, result=None, error=None):
        """完成任务执行"""
        execution = TaskExecution.query.get(execution_id)
        if execution:
            execution.status = 'success' if success else 'failed'
            execution.end_time = datetime.utcnow()
            execution.duration = int((execution.end_time - execution.start_time).total_seconds())
            execution.result = result
            execution.error_message = error
        
        if success:
            self.status = 'completed'
            self.progress = 100
        else:
            self.status = 'failed'
        
        db.session.commit()
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_executions == 0:
            return 0
        # 通过查询TaskExecution计算成功率
        from backend.models.task import TaskExecution
        success_count = TaskExecution.query.filter_by(task_id=self.id, status='success').count()
        return round((success_count / self.total_executions) * 100, 2)
    
    def get_latest_execution(self):
        """获取最新执行记录"""
        from backend.models.task import TaskExecution
        return TaskExecution.query.filter_by(task_id=self.id).order_by(TaskExecution.created_at.desc()).first()
    
    def get_crawler_params(self):
        """获取完整的爬虫服务参数"""
        if self.type != 'crawler':
            return None
        
        params = {
            'url': self.url,
            'task-id': self.id
        }
        
        # 从crawler_config获取基础参数
        if self.crawler_config_id:
            from backend.models.crawler_configs import CrawlerConfig
            crawler_config = CrawlerConfig.query.get(self.crawler_config_id)
            if crawler_config:
                config_dict = crawler_config.to_dict()
                # 映射配置字段到命令行参数
                param_mapping = {
                    'output': 'output',
                    'data_dir': 'data-dir',
                    'use_selenium': 'use-selenium',
                    'timeout': 'timeout',
                    'retry': 'retry',
                    'config': 'config',
                    'email_notification': 'email-notification',
                    'headless': 'headless',
                    'proxy': 'proxy',
                    'page_load_wait': 'page-load-wait',
                    'user_agent': 'user-agent',
                    'enable_xpath': 'enable-xpath'
                }
                
                for config_key, param_key in param_mapping.items():
                    if config_dict.get(config_key) is not None:
                        params[param_key] = config_dict[config_key]
        
        # 从xpath_config获取rule_ids
        if self.xpath_config_id:
            # 简化设计：直接使用xpath_config_id作为rule-ids
            params['rule-ids'] = str(self.xpath_config_id)
        
        return params
    
    def soft_delete(self):
        """逻辑删除任务"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """恢复已删除的任务"""
        self.is_deleted = False
        self.deleted_at = None
        db.session.commit()
    
    def to_dict(self, include_executions=False):
        """转换为字典"""
        data = {
            'id': self.id,  # 修复：使用'id'而不是'task_id'以保持前端一致性
            'task_id': self.id,  # 保留task_id以兼容现有代码
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'url': self.url,

            'status': self.status,
            'progress': self.progress,
            'config': self.config,
            'priority': self.priority,

            'last_run': self.last_run.isoformat() if self.last_run else None,
            'total_executions': self.total_executions,
            'success_rate': self.get_success_rate(),

            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'createdAt': self.created_at.isoformat(),  # 前端期望的字段名
            'updatedAt': self.updated_at.isoformat(),  # 前端期望的字段名
            'user_id': self.user_id,
            'crawler_config_id': self.crawler_config_id,
            'xpath_config_id': self.xpath_config_id,

        }
        
        # 添加爬虫配置信息
        if self.crawler_config_id:
            from backend.models.crawler_configs import CrawlerConfig
            crawler_config = CrawlerConfig.query.get(self.crawler_config_id)
            if crawler_config:
                data['crawlerConfig'] = {
                    'id': crawler_config.id,
                    'name': crawler_config.name,
                    'description': crawler_config.description
                }
            else:
                data['crawlerConfig'] = None
        else:
            data['crawlerConfig'] = None
        
        # 添加XPath配置信息
        if self.xpath_config_id:
            from backend.models.xpath import XPathConfig
            xpath_config = XPathConfig.query.get(self.xpath_config_id)
            if xpath_config:
                data['xpathConfig'] = {
                    'id': xpath_config.id,
                    'name': xpath_config.name,
                    'description': xpath_config.description
                }
            else:
                data['xpathConfig'] = None
        else:
            data['xpathConfig'] = None
        
        if include_executions:
            # TaskExecution功能已移除
            data['executions'] = []
        
        return data
    
    def __repr__(self):
        return f'<Task {self.name}>'


# TaskExecution模型已移除