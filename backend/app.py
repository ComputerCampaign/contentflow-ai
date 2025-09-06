#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用主入口文件
数据爬取博客发布平台后端API服务
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.config import Config
from backend.extensions import db, jwt, limiter, migrate
from backend.api import register_blueprints
from backend.models.user import User
from backend.models.task import Task
from backend.models.crawler_configs import CrawlerConfig
from backend.models.crawler_result import CrawlerResult
from backend.models.dashboard import Dashboard
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    register_blueprints(app)
    
    # 配置日志
    configure_logging(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册JWT回调
    register_jwt_callbacks(app)
    
    # 注册CLI命令
    register_cli_commands(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    @app.before_request
    def log_request_info():
        """记录请求信息"""
        if app.config.get('LOG_REQUESTS', False):
            app.logger.info(f'Request: {request.method} {request.url}')
    
    return app


def configure_logging(app):
    """配置日志"""
    # 确保日志目录存在
    log_dir = app.config.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置文件日志（无论是否为调试模式都输出到文件）
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask应用启动')


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': '请求参数错误',
            'error_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': '未授权访问',
            'error_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': '权限不足',
            'error_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '资源不存在',
            'error_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': '请求方法不允许',
            'error_code': 405
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'success': False,
            'message': '请求实体过大',
            'error_code': 413
        }), 413
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'message': '请求过于频繁，请稍后重试',
            'error_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'服务器内部错误: {str(error)}')
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error_code': 500
        }), 500


def register_jwt_callbacks(app):
    """注册JWT回调函数"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': '令牌已过期',
            'error_code': 'TOKEN_EXPIRED'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': '无效的令牌',
            'error_code': 'INVALID_TOKEN'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': '缺少访问令牌',
            'error_code': 'MISSING_TOKEN'
        }), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': '需要新的令牌',
            'error_code': 'FRESH_TOKEN_REQUIRED'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': '令牌已被撤销',
            'error_code': 'TOKEN_REVOKED'
        }), 401


def register_cli_commands(app):
    """注册CLI命令"""
    
    @app.cli.command()
    def init_db():
        """初始化数据库"""
        db.create_all()
        print('数据库初始化完成')
    
    @app.cli.command()
    def create_admin():
        """创建管理员用户"""
        from backend.models.user import User
        
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('管理员用户已存在')
            return
        
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        admin.is_active = True
        
        db.session.add(admin)
        db.session.commit()
        print('管理员用户创建成功: admin/admin123')
    

    
    @app.cli.command()
    def show_stats():
        """显示系统统计信息"""
        from datetime import datetime
        print('=== 系统统计信息 ===')
        print(f'用户总数: {User.query.count()}')
        print(f'活跃用户: {User.query.filter_by(is_active=True).count()}')
        print(f'任务总数: {Task.query.count()}')
        print(f'运行中任务: {Task.query.filter_by(status="running").count()}')
        print(f'爬虫配置: {CrawlerConfig.query.count()}')
        
        # 今日活动
        today = datetime.utcnow().date()
        today_executions = TaskExecution.query.filter(
            db.func.date(TaskExecution.created_at) == today
        ).count()
        print(f'今日任务执行: {today_executions}')


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 开发环境运行
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )