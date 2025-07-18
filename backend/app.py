#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后端主应用入口文件
"""

from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os

from .config.config import Config
from .models import db, User, UserGroup, UserXPathRule
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
    db_path = os.path.join(project_root, 'db', 'auth.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 确保db目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
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
    初始化数据库：创建默认用户组、管理员账户和默认XPath规则
    """
    from datetime import datetime
    from backend.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    try:
        # 创建默认用户组
        default_groups = [
            {
                'name': 'admin',
                'description': '管理员组，拥有所有权限',
                'max_xpath_rules': -1,  # 无限制
                'allowed_templates': ['*']  # 允许所有模板
            },
            {
                'name': 'user',
                'description': '普通用户组，拥有基本权限',
                'max_xpath_rules': 10,
                'allowed_templates': ['basic', 'simple']
            },
            {
                'name': 'guest',
                'description': '访客组，只有只读权限',
                'max_xpath_rules': 3,
                'allowed_templates': ['basic']
            }
        ]
        
        for group_data in default_groups:
            existing_group = UserGroup.get_by_name(group_data['name'])
            if not existing_group:
                UserGroup.create_group(
                    name=group_data['name'],
                    description=group_data['description'],
                    max_xpath_rules=group_data['max_xpath_rules'],
                    allowed_templates=group_data['allowed_templates']
                )
                logger.info(f"创建用户组: {group_data['name']}")
            else:
                logger.info(f"用户组已存在: {group_data['name']}")
        
        # 创建管理员账户
        admin_username = config.get('auth', 'admin_username', 'admin')
        admin_password = config.get('auth', 'admin_password', 'admin123')
        admin_email = config.get('auth', 'admin_email', 'admin@example.com')
        
        admin_group = UserGroup.get_admin_group()
        if not admin_group:
            logger.error("管理员组不存在，无法创建管理员用户")
            return
        
        admin = User.get_by_username(admin_username)
        if not admin:
            admin = User.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                group=admin_group
            )
            logger.info(f"已创建管理员账户: {admin_username}")
        else:
            logger.info(f"管理员账户已存在: {admin_username}")
        
        # 创建默认XPath规则
        create_default_xpath_rules(admin)
        
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def create_default_xpath_rules(admin_user):
    """
    创建默认XPath规则
    """
    from datetime import datetime
    from backend.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    if not admin_user:
        logger.warning("管理员用户不存在，跳过XPath规则创建")
        return
    
    default_rules = [
        {
            'rule_name': '通用文章规则',
            'domain': 'general',
            'xpath': '//title/text() | //h1/text() | //h2/text()',
            'description': '适用于大多数文章页面的通用XPath规则'
        },
        {
            'rule_name': '新闻文章规则',
            'domain': 'news',
            'xpath': '//h1[@class="title"] | //div[@class="article-body"]//p',
            'description': '适用于新闻网站的XPath规则'
        }
    ]
    
    for rule_data in default_rules:
        # 检查规则是否已存在
        existing_rule = UserXPathRule.query.filter_by(
            rule_name=rule_data['rule_name'],
            user_id=admin_user.id
        ).first()
        
        if not existing_rule:
            rule = UserXPathRule(
                rule_name=rule_data['rule_name'],
                domain=rule_data['domain'],
                xpath=rule_data['xpath'],
                description=rule_data['description'],
                user_id=admin_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(rule)
            logger.info(f"创建XPath规则: {rule_data['rule_name']}")
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)