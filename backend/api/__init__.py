#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API蓝图模块
"""

from flask import Blueprint
from backend.api.auth import auth_bp
from backend.api.tasks import tasks_bp
from backend.api.crawler import crawler_bp
from backend.api.monitoring import monitoring_bp
from backend.api.xpath import xpath_bp
# ai_config和ai_content_config已合并到ai_model中
from backend.api.ai_model import ai_model_bp
from backend.api.dashboard import dashboard_bp


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
    
    # 注册XPath配置API
    app.register_blueprint(xpath_bp, url_prefix=f'{api_prefix}/xpath')
    
    # ai_config和ai_content_config已合并到ai_model中，无需单独注册
    
    # 注册统一的AI模型配置API (替代ai-config)
    from backend.api.ai_model import ai_model_bp as ai_config_unified_bp
    app.register_blueprint(ai_config_unified_bp, url_prefix=f'{api_prefix}/ai-config', name='ai_config_unified')
    
    # 注册AI模型配置API (新路径)
    app.register_blueprint(ai_model_bp, url_prefix=f'{api_prefix}/ai-model')
    
    # 注册监控API
    app.register_blueprint(monitoring_bp, url_prefix=f'{api_prefix}/monitor')
    
    # 注册仪表板API
    app.register_blueprint(dashboard_bp, url_prefix=f'{api_prefix}/dashboard')


__all__ = [
    'register_blueprints',
    'auth_bp',
    'tasks_bp', 
    'crawler_bp',
    'xpath_bp',
    'ai_config_bp',
    'ai_content_config_bp',
    'ai_model_bp',
    'monitoring_bp',
    'dashboard_bp'
]