#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API蓝图模块
"""

from flask import Blueprint
from backend.api.auth import auth_bp
from backend.api.tasks import tasks_bp
from backend.api.crawler import crawler_bp
from backend.api.content import content_bp
from backend.api.files import files_bp
from backend.api.monitoring import monitoring_bp


def register_blueprints(app):
    """注册所有API蓝图"""
    
    # API版本前缀
    api_prefix = '/api/v1'
    
    # 注册认证相关API
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    
    # 注册任务管理API
    app.register_blueprint(tasks_bp, url_prefix=f'{api_prefix}/tasks')
    
    # 注册爬虫配置API
    app.register_blueprint(crawler_bp, url_prefix=f'{api_prefix}/crawler')
    
    # 注册内容生成API
    app.register_blueprint(content_bp, url_prefix=f'{api_prefix}/content')
    
    # 注册文件管理API
    app.register_blueprint(files_bp, url_prefix=f'{api_prefix}/files')
    
    # 注册监控API
    app.register_blueprint(monitoring_bp, url_prefix=f'{api_prefix}/monitor')


__all__ = [
    'register_blueprints',
    'auth_bp',
    'tasks_bp', 
    'crawler_bp',
    'content_bp',
    'files_bp',
    'monitoring_bp'
]