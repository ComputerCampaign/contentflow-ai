#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt管理API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.prompt import PromptConfig
from backend.utils import success_response, error_response, paginated_response
from datetime import datetime
from sqlalchemy import or_
import json

# 创建蓝图
prompt_bp = Blueprint('prompt', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def validate_prompt_data(data, partial=False):
    """验证Prompt数据"""
    errors = []
    
    # 必需字段验证
    required_fields = ['name', 'content']
    if not partial:
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"字段 '{field}' 是必需的")
    
    # 字段长度验证
    if 'name' in data and len(data['name']) > 200:
        errors.append("Prompt名称不能超过200个字符")
    
    # 类型验证
    valid_types = ['content', 'title', 'summary', 'keywords']
    if 'type' in data and data['type'] not in valid_types:
        errors.append(f"Prompt类型必须是以下之一: {', '.join(valid_types)}")
    
    # 状态验证
    valid_statuses = ['active', 'inactive']
    if 'status' in data and data['status'] not in valid_statuses:
        errors.append(f"状态必须是以下之一: {', '.join(valid_statuses)}")
    
    return errors


@prompt_bp.route('', methods=['GET'])
@jwt_required()
def get_prompts():
    """获取Prompt列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        prompt_type = request.args.get('type', '').strip()
        status = request.args.get('status', '').strip()
        
        # 构建查询
        query = PromptConfig.query.filter_by(user_id=current_user.id)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    PromptConfig.name.contains(search),
                    PromptConfig.description.contains(search),
                    PromptConfig.content.contains(search)
                )
            )
        
        # 类型过滤
        if prompt_type:
            query = query.filter(PromptConfig.type == prompt_type)
        
        # 状态过滤
        if status:
            query = query.filter(PromptConfig.status == status)
        
        # 排序
        query = query.order_by(PromptConfig.updated_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        prompts = [prompt.to_dict() for prompt in pagination.items]
        
        return paginated_response(
            items=prompts,
            pagination={
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            },
            message='获取Prompt列表成功'
        )
        
    except Exception as e:
        current_app.logger.error(f"获取Prompt列表失败: {str(e)}")
        return error_response('获取Prompt列表失败', 500)


@prompt_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_prompt():
    """创建新的Prompt"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        data = request.get_json()
        if not data:
            return error_response('请提供Prompt数据', 400)
        
        # 验证数据
        errors = validate_prompt_data(data)
        if errors:
            return error_response(f'数据验证失败: {"; ".join(errors)}', 400)
        
        # 检查名称是否重复
        existing_prompt = PromptConfig.query.filter_by(
            name=data['name'], 
            user_id=current_user.id
        ).first()
        if existing_prompt:
            return error_response('Prompt名称已存在', 400)
        
        # 创建新Prompt
        prompt = PromptConfig(
            name=data['name'],
            content=data['content'],
            user_id=current_user.id,
            description=data.get('description', ''),
            type=data.get('type', 'content'),
            status=data.get('status', 'active')
        )
        
        # 设置变量说明
        if 'variables' in data and data['variables']:
            prompt.set_variables(data['variables'])
        
        db.session.add(prompt)
        db.session.commit()
        
        current_app.logger.info(f"用户 {current_user.username} 创建了Prompt: {prompt.name}")
        
        return success_response(
            data=prompt.to_dict(),
            message='Prompt创建成功'
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建Prompt失败: {str(e)}")
        return error_response('创建Prompt失败', 500)


@prompt_bp.route('/<prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt(prompt_id):
    """获取单个Prompt详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        prompt = PromptConfig.query.filter_by(
            id=prompt_id, 
            user_id=current_user.id
        ).first()
        
        if not prompt:
            return error_response('Prompt不存在', 404)
        
        return success_response(
            data=prompt.to_dict(),
            message='获取Prompt详情成功'
        )
        
    except Exception as e:
        current_app.logger.error(f"获取Prompt详情失败: {str(e)}")
        return error_response('获取Prompt详情失败', 500)


@prompt_bp.route('/<prompt_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("30 per minute")
def update_prompt(prompt_id):
    """更新Prompt"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        prompt = PromptConfig.query.filter_by(
            id=prompt_id, 
            user_id=current_user.id
        ).first()
        
        if not prompt:
            return error_response('Prompt不存在', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请提供更新数据', 400)
        
        # 验证数据
        errors = validate_prompt_data(data, partial=True)
        if errors:
            return error_response(f'数据验证失败: {"; ".join(errors)}', 400)
        
        # 检查名称是否重复（排除当前Prompt）
        if 'name' in data:
            existing_prompt = PromptConfig.query.filter(
                PromptConfig.name == data['name'],
                PromptConfig.user_id == current_user.id,
                PromptConfig.id != prompt_id
            ).first()
            if existing_prompt:
                return error_response('Prompt名称已存在', 400)
        
        # 更新字段
        updatable_fields = ['name', 'description', 'type', 'content', 'status']
        for field in updatable_fields:
            if field in data:
                setattr(prompt, field, data[field])
        
        # 更新变量说明
        if 'variables' in data:
            prompt.set_variables(data['variables'])
        
        prompt.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"用户 {current_user.username} 更新了Prompt: {prompt.name}")
        
        return success_response(
            data=prompt.to_dict(),
            message='Prompt更新成功'
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新Prompt失败: {str(e)}")
        return error_response('更新Prompt失败', 500)


@prompt_bp.route('/<prompt_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_prompt(prompt_id):
    """删除Prompt"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        prompt = PromptConfig.query.filter_by(
            id=prompt_id, 
            user_id=current_user.id
        ).first()
        
        if not prompt:
            return error_response('Prompt不存在', 404)
        
        prompt_name = prompt.name
        db.session.delete(prompt)
        db.session.commit()
        
        current_app.logger.info(f"用户 {current_user.username} 删除了Prompt: {prompt_name}")
        
        return success_response(
            message='Prompt删除成功'
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除Prompt失败: {str(e)}")
        return error_response('删除Prompt失败', 500)


@prompt_bp.route('/types', methods=['GET'])
@jwt_required()
def get_prompt_types():
    """获取Prompt类型列表"""
    try:
        types = [
            {'value': 'content', 'label': '内容生成'},
            {'value': 'title', 'label': '标题生成'},
            {'value': 'summary', 'label': '摘要生成'},
            {'value': 'keywords', 'label': '关键词提取'}
        ]
        
        return success_response(
            data=types,
            message='获取Prompt类型成功'
        )
        
    except Exception as e:
        current_app.logger.error(f"获取Prompt类型失败: {str(e)}")
        return error_response('获取Prompt类型失败', 500)


@prompt_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_prompt_statistics():
    """获取Prompt统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        # 总数统计
        total_count = PromptConfig.query.filter_by(user_id=current_user.id).count()
        active_count = PromptConfig.query.filter_by(
            user_id=current_user.id, 
            status='active'
        ).count()
        
        # 按类型统计
        type_stats = db.session.query(
            PromptConfig.type,
            db.func.count(PromptConfig.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(PromptConfig.type).all()
        
        type_counts = {stat.type: stat.count for stat in type_stats}
        
        # 使用次数统计
        total_usage = db.session.query(
            db.func.sum(PromptConfig.usage_count)
        ).filter_by(user_id=current_user.id).scalar() or 0
        
        statistics = {
            'total_count': total_count,
            'active_count': active_count,
            'inactive_count': total_count - active_count,
            'type_counts': type_counts,
            'total_usage': total_usage
        }
        
        return success_response(
            data=statistics,
            message='获取Prompt统计信息成功'
        )
        
    except Exception as e:
        current_app.logger.error(f"获取Prompt统计信息失败: {str(e)}")
        return error_response('获取Prompt统计信息失败', 500)


@prompt_bp.route('/<prompt_id>/use', methods=['POST'])
@jwt_required()
def use_prompt(prompt_id):
    """使用Prompt（增加使用次数）"""
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response('用户未找到', 401)
        
        prompt = PromptConfig.query.filter_by(
            id=prompt_id, 
            user_id=current_user.id
        ).first()
        
        if not prompt:
            return error_response('Prompt不存在', 404)
        
        if prompt.status != 'active':
            return error_response('Prompt未激活，无法使用', 400)
        
        prompt.increment_usage()
        
        return success_response(
            data={'usage_count': prompt.usage_count},
            message='Prompt使用记录成功'
        )
        
    except Exception as e:
        current_app.logger.error(f"记录Prompt使用失败: {str(e)}")
        return error_response('记录Prompt使用失败', 500)