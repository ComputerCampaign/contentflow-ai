#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.extensions import db, limiter
from backend.models.user import User
from datetime import datetime, timedelta
import re


auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    
    return True, "密码格式正确"


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 获取必需字段
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 验证必需字段
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和密码不能为空'
            }), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 50:
            return jsonify({
                'success': False,
                'message': '用户名长度必须在3-50个字符之间'
            }), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': '邮箱格式不正确'
            }), 400
        
        # 验证密码强度（文档要求最少6字符）
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': '密码长度至少6位',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': '用户名已存在',
                'error_code': 'USERNAME_EXISTS'
            }), 409
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': '邮箱已被注册',
                'error_code': 'EMAIL_EXISTS'
            }), 409
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password=password,
            display_name=data.get('display_name', username),
            role=data.get('role', 'user')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户注册成功',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"注册失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '注册失败，请稍后重试'
        }), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 获取登录凭据
        identifier = data.get('username') or data.get('email', '')
        password = data.get('password', '')
        
        if not all([identifier, password]):
            return jsonify({
                'success': False,
                'message': '用户名/邮箱和密码不能为空'
            }), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = None
        if '@' in identifier:
            user = User.query.filter_by(email=identifier.lower()).first()
        else:
            user = User.query.filter_by(username=identifier).first()
        
        # 验证用户和密码
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': '用户名/邮箱或密码错误',
                'error_code': 'INVALID_CREDENTIALS'
            }), 401
        
        # 检查账户状态
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': '账户已被禁用',
                'error_code': 'ACCOUNT_DISABLED'
            }), 403
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT令牌
        access_token, refresh_token = user.generate_tokens()
        
        # 获取过期时间（转换为秒）
        expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
        if hasattr(expires_in, 'total_seconds'):
            expires_in = int(expires_in.total_seconds())
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': expires_in,
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"登录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500


@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    """获取当前登录用户的权限列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 404

        # 这里可以根据用户角色或更细粒度的权限系统返回权限列表
        # 示例：硬编码权限列表
        permissions = []
        if user.role == 'admin':
            permissions = ['admin:*', 'user:view', 'user:edit', 'crawler:run', 'ai:generate']
        else:
            permissions = ['user:view', 'crawler:view']

        return jsonify({
            'success': True,
            'message': '权限获取成功',
            'data': permissions
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户权限失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取用户权限失败，请稍后重试'
        }), 500
    

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.status != 'active':
            return jsonify({
                'success': False,
                'message': '用户不存在或账户已被禁用'
            }), 401
        
        # 生成新的访问令牌
        new_token = user.generate_token()
        
        return jsonify({
            'success': True,
            'message': 'Token刷新成功',
            'data': {
                'access_token': new_token,
                'token_type': 'Bearer',
                'expires_in': 86400
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"令牌刷新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '令牌刷新失败'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # 获取当前JWT令牌
        jti = get_jwt()['jti']
        
        # 这里可以将令牌加入黑名单（需要Redis支持）
        # 暂时只返回成功响应
        
        return jsonify({
            'success': True,
            'message': '登出成功'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"登出失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登出失败'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取用户资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '获取用户信息成功',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户资料失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取用户资料失败'
        }), 500


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """更新用户资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 可更新的字段
        if 'display_name' in data:
            user.display_name = data['display_name']
        
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user.id
            ).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': '邮箱已被其他用户使用',
                    'error_code': 'EMAIL_EXISTS'
                }), 409
            user.email = data['email']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户信息更新成功',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户资料失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新用户资料失败'
        }), 500


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not all([current_password, new_password]):
            return jsonify({
                'success': False,
                'message': '当前密码和新密码不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证当前密码
        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'message': '当前密码错误',
                'error_code': 'INVALID_CURRENT_PASSWORD'
            }), 401
        
        # 验证新密码强度（文档要求最少6字符）
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': '新密码长度至少6位',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 更新密码
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"修改密码失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '修改密码失败'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """验证令牌有效性"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.status != 'active':
            return jsonify({
                'success': False,
                'message': '令牌无效或用户已被禁用'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '令牌有效',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"验证令牌失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '令牌验证失败'
        }), 500