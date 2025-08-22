#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard模型 - 用于存储仪表板展示面板数据
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class Dashboard(db.Model):
    """Dashboard模型 - 独立的展示面板数据存储"""
    
    __tablename__ = 'dashboard'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 面板类型标识
    panel_type = db.Column(db.String(50), nullable=False, index=True)
    
    # 任务趋势数据 - JSON格式存储
    task_trend = db.Column(db.JSON, nullable=True)
    
    # 统计信息 - JSON格式存储
    stats = db.Column(db.JSON, nullable=True)
    
    # 爬虫状态 - JSON格式存储
    crawler_status = db.Column(db.JSON, nullable=True)
    
    # 系统资源 - JSON格式存储
    system_resources = db.Column(db.JSON, nullable=True)
    
    # 资源历史 - JSON格式存储
    resource_history = db.Column(db.JSON, nullable=True)
    
    # 最近活动 - JSON格式存储
    recent_activities = db.Column(db.JSON, nullable=True)
    
    # 快速操作 - JSON格式存储
    quick_actions = db.Column(db.JSON, nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, panel_type='default', **kwargs):
        self.panel_type = panel_type
        self.task_trend = kwargs.get('task_trend')
        self.stats = kwargs.get('stats')
        self.crawler_status = kwargs.get('crawler_status')
        self.system_resources = kwargs.get('system_resources')
        self.resource_history = kwargs.get('resource_history')
        self.recent_activities = kwargs.get('recent_activities')
        self.quick_actions = kwargs.get('quick_actions')
    
    def update_data(self, **kwargs):
        """更新面板数据"""
        if 'task_trend' in kwargs:
            self.task_trend = kwargs['task_trend']
        if 'stats' in kwargs:
            self.stats = kwargs['stats']
        if 'crawler_status' in kwargs:
            self.crawler_status = kwargs['crawler_status']
        if 'system_resources' in kwargs:
            self.system_resources = kwargs['system_resources']
        if 'resource_history' in kwargs:
            self.resource_history = kwargs['resource_history']
        if 'recent_activities' in kwargs:
            self.recent_activities = kwargs['recent_activities']
        if 'quick_actions' in kwargs:
            self.quick_actions = kwargs['quick_actions']
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'panel_type': self.panel_type,
            'task_trend': self.task_trend,
            'stats': self.stats,
            'crawler_status': self.crawler_status,
            'system_resources': self.system_resources,
            'resource_history': self.resource_history,
            'recent_activities': self.recent_activities,
            'quick_actions': self.quick_actions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_dashboard_data(cls, panel_type='default'):
        """获取指定类型的面板数据"""
        dashboard = cls.query.filter_by(panel_type=panel_type).first()
        if dashboard:
            return dashboard.to_dict()
        return None
    
    @classmethod
    def create_or_update_dashboard(cls, panel_type='default', **data):
        """创建或更新面板数据"""
        dashboard = cls.query.filter_by(panel_type=panel_type).first()
        
        if dashboard:
            dashboard.update_data(**data)
            return dashboard
        else:
            dashboard = cls(panel_type=panel_type, **data)
            db.session.add(dashboard)
            db.session.commit()
            return dashboard
    
    def __repr__(self):
        return f'<Dashboard {self.panel_type}>'