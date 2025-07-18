#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证相关API接口
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import User, db
from ..auth.jwt_handler import create_access_token
from ..auth.permissions import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    
    请求体:
    {
        "username": "用户名",
        "email": "邮箱",
        "password": "密码",
        "group_id": 用户组ID (可选，默认为普通用户组)
    }
    """
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"error": "缺少必要字段"}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "用户名已存在"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "邮箱已存在"}), 400
    
    # 创建新用户
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        group_id=data.get('group_id', 2)  # 默认为普通用户组
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "用户注册成功"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    请求体:
    {
        "username": "用户名",
        "password": "密码"
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({"error": "缺少用户名或密码"}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "用户名或密码错误"}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成访问令牌
    token = create_access_token({"sub": user.id})
    
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "group": user.group.name if user.group else None
        }
    })

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    获取当前登录用户信息
    """
    user = g.current_user
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "group": {
            "id": user.group.id,
            "name": user.group.name,
            "max_xpath_rules": user.group.max_xpath_rules,
            "allowed_templates": user.group.allowed_templates
        } if user.group else None,
        "xpath_rules_count": len(user.xpath_rules)
    })