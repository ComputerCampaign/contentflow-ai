#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask扩展初始化
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
import redis

# 数据库
db = SQLAlchemy()

# 数据库迁移
migrate = Migrate()

# JWT认证
jwt = JWTManager()

# 限流器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100000 per day", "2000 per hour"],
    headers_enabled=True
)

# Redis连接
redis_client = None

# Celery任务队列
celery = Celery('crawler_platform')


def init_redis(app):
    """初始化Redis连接"""
    global redis_client
    redis_url = app.config.get('REDIS_URL')
    if redis_url:
        redis_client = redis.from_url(redis_url)
    return redis_client


def init_celery(app):
    """初始化Celery"""
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30分钟
        task_soft_time_limit=25 * 60,  # 25分钟
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    
    class ContextTask(celery.Task):
        """使Celery任务在Flask应用上下文中运行"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery