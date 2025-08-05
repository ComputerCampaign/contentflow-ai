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
    type = db.Column(db.Enum('crawler', 'content_generation', 'full_pipeline', 
                            name='task_type'), nullable=False)
    
    # 状态管理
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', 
                              'cancelled', 'paused', name='task_status'), 
                      default='pending', nullable=False)
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # 配置信息
    config = db.Column(db.JSON)  # 任务配置
    priority = db.Column(db.Integer, default=5)  # 1-10，数字越大优先级越高
    
    # 调度信息
    schedule = db.Column(db.String(100))  # Cron表达式
    next_run = db.Column(db.DateTime)
    last_run = db.Column(db.DateTime)
    
    # 执行统计
    total_executions = db.Column(db.Integer, default=0)
    successful_executions = db.Column(db.Integer, default=0)
    failed_executions = db.Column(db.Integer, default=0)
    
    # 结果信息
    result_summary = db.Column(db.JSON)  # 执行结果摘要
    output_files = db.Column(db.JSON)  # 输出文件列表
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 外键
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    crawler_config_id = db.Column(db.String(36), db.ForeignKey('crawler_configs.id'))
    content_template_id = db.Column(db.String(36), db.ForeignKey('content_templates.id'))
    
    # 关联关系
    executions = db.relationship('TaskExecution', backref='task', lazy='dynamic',
                                cascade='all, delete-orphan', 
                                order_by='TaskExecution.created_at.desc()')
    
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
            self.successful_executions += 1
            if result:
                self.result_summary = result
        else:
            self.status = 'failed'
            self.failed_executions += 1
        
        db.session.commit()
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_executions == 0:
            return 0
        return round((self.successful_executions / self.total_executions) * 100, 2)
    
    def get_latest_execution(self):
        """获取最新执行记录"""
        return self.executions.first()
    
    def to_dict(self, include_executions=False):
        """转换为字典"""
        data = {
            'task_id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'progress': self.progress,
            'config': self.config,
            'priority': self.priority,
            'schedule': self.schedule,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'total_executions': self.total_executions,
            'success_rate': self.get_success_rate(),
            'result_summary': self.result_summary,
            'output_files': self.output_files,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'crawler_config_id': self.crawler_config_id,
            'content_template_id': self.content_template_id
        }
        
        if include_executions:
            data['executions'] = [exec.to_dict() for exec in self.executions.limit(10)]
        
        return data
    
    def __repr__(self):
        return f'<Task {self.name}>'


class TaskExecution(db.Model):
    """任务执行记录模型"""
    
    __tablename__ = 'task_executions'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 执行信息
    dag_run_id = db.Column(db.String(100))  # Airflow DAG运行ID
    status = db.Column(db.Enum('running', 'success', 'failed', 'cancelled', 
                              name='execution_status'), nullable=False)
    
    # 时间信息
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 执行时长（秒）
    
    # 结果信息
    result = db.Column(db.JSON)  # 执行结果
    error_message = db.Column(db.Text)  # 错误信息
    logs = db.Column(db.Text)  # 执行日志
    
    # 统计信息
    items_processed = db.Column(db.Integer, default=0)
    items_success = db.Column(db.Integer, default=0)
    items_failed = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 外键
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    
    def __init__(self, task_id, status='running', **kwargs):
        self.task_id = task_id
        self.status = status
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_progress(self, items_processed=None, items_success=None, items_failed=None):
        """更新执行进度"""
        if items_processed is not None:
            self.items_processed = items_processed
        if items_success is not None:
            self.items_success = items_success
        if items_failed is not None:
            self.items_failed = items_failed
        db.session.commit()
    
    def get_success_rate(self):
        """获取执行成功率"""
        if self.items_processed == 0:
            return 0
        return round((self.items_success / self.items_processed) * 100, 2)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'execution_id': self.id,
            'dag_run_id': self.dag_run_id,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'result': self.result,
            'error_message': self.error_message,
            'items_processed': self.items_processed,
            'items_success': self.items_success,
            'items_failed': self.items_failed,
            'success_rate': self.get_success_rate(),
            'created_at': self.created_at.isoformat(),
            'task_id': self.task_id
        }
    
    def __repr__(self):
        return f'<TaskExecution {self.id}>'