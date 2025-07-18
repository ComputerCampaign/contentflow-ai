#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
权限检查模块
"""

from functools import wraps
from flask import request, jsonify, g
import os
import sys
# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.auth.jwt_handler import verify_token
from backend.models import User, UserGroup

def login_required(f):
    """
    登录验证装饰器
    
    验证请求中的JWT令牌，确保用户已登录
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({"error": "未提供认证令牌"}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "无效的认证令牌"}), 401
        
        user_id = payload.get('sub')
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({"error": "用户不存在或已禁用"}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorated

def group_required(group_names):
    """
    用户组权限验证装饰器
    
    验证用户是否属于指定的用户组
    
    Args:
        group_names (list): 允许访问的用户组名称列表
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not g.current_user.group or g.current_user.group.name not in group_names:
                return jsonify({"error": "权限不足"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_xpath_limit(f):
    """
    XPath规则数量限制检查装饰器
    
    检查用户是否已达到XPath规则数量限制
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = g.current_user
        group = user.group
        
        # 管理员组无限制
        if group and group.name == 'admin':
            return f(*args, **kwargs)
        
        # 检查用户已创建的XPath规则数量
        current_count = len(user.xpath_rules)
        max_allowed = group.max_xpath_rules if group else 10
        
        if current_count >= max_allowed:
            return jsonify({"error": f"已达到最大XPath规则限制 ({max_allowed})"}), 403
            
        return f(*args, **kwargs)
    return decorated_function