#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户管理相关API接口
"""

from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash

from ..models import User, UserGroup, db
from ..auth.permissions import login_required, group_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@login_required
@group_required(['admin'])
def get_users():
    """
    获取所有用户列表（仅管理员可访问）
    """
    users = User.query.all()
    return jsonify({
        "users": [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "group": user.group.name if user.group else None,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        } for user in users]
    })

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@group_required(['admin'])
def get_user(user_id):
    """
    获取指定用户信息（仅管理员可访问）
    """
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "group": {
            "id": user.group.id,
            "name": user.group.name
        } if user.group else None,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "xpath_rules_count": len(user.xpath_rules)
    })

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@group_required(['admin'])
def update_user(user_id):
    """
    更新用户信息（仅管理员可访问）
    
    请求体:
    {
        "email": "新邮箱", (可选)
        "is_active": true/false, (可选)
        "group_id": 用户组ID, (可选)
        "password": "新密码" (可选)
    }
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error": "邮箱已被其他用户使用"}), 400
        user.email = data['email']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'group_id' in data:
        group = UserGroup.query.get(data['group_id'])
        if not group:
            return jsonify({"error": "用户组不存在"}), 400
        user.group_id = data['group_id']
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    
    db.session.commit()
    
    return jsonify({"message": "用户信息更新成功"})

@user_bp.route('/groups', methods=['GET'])
@login_required
def get_groups():
    """
    获取所有用户组列表
    """
    groups = UserGroup.query.all()
    return jsonify({
        "groups": [{
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "max_xpath_rules": group.max_xpath_rules,
            "allowed_templates": group.allowed_templates
        } for group in groups]
    })

@user_bp.route('/groups', methods=['POST'])
@login_required
@group_required(['admin'])
def create_group():
    """
    创建新用户组（仅管理员可访问）
    
    请求体:
    {
        "name": "用户组名称",
        "description": "用户组描述",
        "max_xpath_rules": 最大XPath规则数量,
        "allowed_templates": ["允许的模板列表"]
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ('name', 'max_xpath_rules', 'allowed_templates')):
        return jsonify({"error": "缺少必要字段"}), 400
    
    # 检查用户组名称是否已存在
    if UserGroup.query.filter_by(name=data['name']).first():
        return jsonify({"error": "用户组名称已存在"}), 400
    
    new_group = UserGroup(
        name=data['name'],
        description=data.get('description', ''),
        max_xpath_rules=data['max_xpath_rules'],
        allowed_templates=data['allowed_templates']
    )
    
    db.session.add(new_group)
    db.session.commit()
    
    return jsonify({
        "id": new_group.id,
        "name": new_group.name,
        "message": "用户组创建成功"
    }), 201