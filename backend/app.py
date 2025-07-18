#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后端主应用入口文件
"""

from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os

from .config.config import Config
from .models import db, User, UserGroup
from .api import api_bp

def create_app():
    """
    创建并配置Flask应用
    """
    import os
    # 设置静态文件目录
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    
    # 加载配置
    config = Config()
    
    # 配置数据库
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', 'auth.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config.get('auth', 'secret_key', os.urandom(24).hex())
    app.config['JWT_SECRET_KEY'] = config.get('auth', 'jwt_secret_key', os.urandom(24).hex())
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.get('auth', 'jwt_access_token_expires', 86400)  # 默认1天
    
    # 初始化扩展
    db.init_app(app)
    
    # 配置CORS
    CORS(app, resources={r"/api/*": {"origins": config.get('auth', 'cors_origins', '*')}})
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 静态文件路由
    @app.route('/')
    def index():
        """提供前端主页"""
        try:
            return send_file(os.path.join(static_folder, 'index.html'))
        except FileNotFoundError:
            return jsonify({"error": "前端文件未找到，请先构建前端项目"}), 404
    
    @app.route('/<path:path>')
    def static_files(path):
        """提供静态文件"""
        # 如果是API路径，返回404
        if path.startswith('api/'):
            return jsonify({"error": "API路径不存在"}), 404
        
        # 尝试提供静态文件
        try:
            return send_from_directory(static_folder, path)
        except FileNotFoundError:
            # 如果文件不存在，返回index.html（用于SPA路由）
            try:
                return send_file(os.path.join(static_folder, 'index.html'))
            except FileNotFoundError:
                return jsonify({"error": "前端文件未找到，请先构建前端项目"}), 404
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "资源不存在"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "服务器内部错误"}), 500
    
    # 创建数据库表和初始化管理员账户
    with app.app_context():
        db.create_all()
        init_admin_account(config)
    
    return app

def init_admin_account(config):
    """
    初始化管理员账户和用户组
    """
    # 创建管理员用户组
    admin_group = UserGroup.get_admin_group()
    if not admin_group:
        admin_group = UserGroup.create_group(
            name='admin',
            description='管理员组',
            max_xpath_rules=-1,  # 无限制
            allowed_templates=['*']  # 允许所有模板
        )
    
    # 创建普通用户组
    user_group = UserGroup.get_default_group()
    if not user_group:
        user_group = UserGroup.create_group(
            name='user',
            description='普通用户组',
            max_xpath_rules=10,
            allowed_templates=['basic', 'simple']
        )
    
    # 用户组更改已在create_group方法中提交
    
    # 创建管理员账户
    admin_username = config.get('auth', 'admin_username', 'admin')
    admin_password = config.get('auth', 'admin_password', 'admin123')
    admin_email = config.get('auth', 'admin_email', 'admin@example.com')
    
    admin = User.get_by_username(admin_username)
    if not admin:
        admin = User.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            group=admin_group
        )
        print(f"已创建管理员账户: {admin_username}")
    else:
        print(f"管理员账户已存在: {admin_username}")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)