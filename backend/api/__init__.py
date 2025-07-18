#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API模块初始化文件，用于注册所有API蓝图
"""

from flask import Blueprint

# 创建API主蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入各个子模块的蓝图
from .auth import auth_bp
from .user import user_bp
from .xpath import xpath_bp
from .crawler import crawler_bp

# 注册子蓝图
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(user_bp, url_prefix='/user')
api_bp.register_blueprint(xpath_bp, url_prefix='/xpath')
api_bp.register_blueprint(crawler_bp, url_prefix='/crawler')

# 导出API蓝图
__all__ = ['api_bp']