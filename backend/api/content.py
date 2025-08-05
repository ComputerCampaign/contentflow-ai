#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容生成API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.content import ContentTemplate, GeneratedContent
from datetime import datetime
from sqlalchemy import or_
from jinja2 import Template, TemplateSyntaxError
import json


content_bp = Blueprint('content', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def validate_template_content(content):
    """验证模板内容"""
    try:
        # 尝试解析Jinja2模板
        Template(content)
        return True, "模板格式正确"
    except TemplateSyntaxError as e:
        return False, f"模板语法错误: {str(e)}"
    except Exception as e:
        return False, f"模板验证失败: {str(e)}"


def validate_template_variables(variables):
    """验证模板变量定义"""
    if not isinstance(variables, dict):
        return False, "变量定义必须是JSON对象"
    
    for var_name, var_config in variables.items():
        if not isinstance(var_config, dict):
            return False, f"变量 {var_name} 的配置必须是JSON对象"
        
        # 检查必需字段
        if 'type' not in var_config:
            return False, f"变量 {var_name} 缺少类型定义"
        
        # 验证变量类型
        valid_types = ['string', 'number', 'boolean', 'array', 'object']
        if var_config['type'] not in valid_types:
            return False, f"变量 {var_name} 的类型无效，支持的类型: {", ".join(valid_types)}"
    
    return True, "变量定义正确"


@content_bp.route('/templates', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_template():
    """创建内容模板"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 获取必需字段
        name = data.get('name', '').strip()
        content = data.get('content', '').strip()
        
        if not all([name, content]):
            return jsonify({
                'success': False,
                'message': '模板名称和内容不能为空'
            }), 400
        
        # 验证模板名称长度
        if len(name) < 2 or len(name) > 100:
            return jsonify({
                'success': False,
                'message': '模板名称长度必须在2-100个字符之间'
            }), 400
        
        # 检查模板名称是否已存在
        existing_template = ContentTemplate.query.filter_by(
            name=name, user_id=current_user.id
        ).first()
        if existing_template:
            return jsonify({
                'success': False,
                'message': '模板名称已存在'
            }), 409
        
        # 验证模板内容
        is_valid, message = validate_template_content(content)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # 验证变量定义
        variables = data.get('variables', {})
        if variables:
            is_valid, message = validate_template_variables(variables)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        # 创建模板
        template = ContentTemplate(
            name=name,
            content=content,
            user_id=current_user.id,
            description=data.get('description', ''),
            variables=variables,
            output_format=data.get('output_format', 'text'),
            ai_config=data.get('ai_config', {}),
            tags=data.get('tags', [])
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '内容模板创建成功',
            'data': {
                'template': template.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建内容模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建内容模板失败，请稍后重试'
        }), 500


@content_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """获取内容模板列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        output_format = request.args.get('output_format')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = ContentTemplate.query.filter_by(user_id=current_user.id)
        
        # 状态过滤
        if status:
            query = query.filter(ContentTemplate.status == status)
        
        # 输出格式过滤
        if output_format:
            query = query.filter(ContentTemplate.output_format == output_format)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    ContentTemplate.name.contains(search),
                    ContentTemplate.description.contains(search)
                )
            )
        
        # 排序和分页
        query = query.order_by(ContentTemplate.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        templates = [template.to_dict() for template in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取内容模板列表成功',
            'data': {
                'templates': templates,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取内容模板列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取内容模板列表失败'
        }), 500


@content_bp.route('/templates/<template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """获取内容模板详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        template = ContentTemplate.query.filter_by(
            id=template_id, user_id=current_user.id
        ).first()
        if not template:
            return jsonify({
                'success': False,
                'message': '内容模板不存在'
            }), 404
        
        # 获取最近的生成内容
        recent_contents = GeneratedContent.query.filter_by(template_id=template_id)\
            .order_by(GeneratedContent.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'message': '获取内容模板详情成功',
            'data': {
                'template': template.to_dict(include_stats=True),
                'recent_contents': [content.to_dict() for content in recent_contents]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取内容模板详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取内容模板详情失败'
        }), 500


@content_bp.route('/templates/<template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """更新内容模板"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        template = ContentTemplate.query.filter_by(
            id=template_id, user_id=current_user.id
        ).first()
        if not template:
            return jsonify({
                'success': False,
                'message': '内容模板不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证模板内容（如果提供）
        if 'content' in data:
            is_valid, message = validate_template_content(data['content'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        # 验证变量定义（如果提供）
        if 'variables' in data:
            is_valid, message = validate_template_variables(data['variables'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        # 检查名称冲突
        if 'name' in data and data['name'] != template.name:
            existing_template = ContentTemplate.query.filter_by(
                name=data['name'], user_id=current_user.id
            ).first()
            if existing_template:
                return jsonify({
                    'success': False,
                    'message': '模板名称已存在'
                }), 409
        
        # 可更新的字段
        updatable_fields = [
            'name', 'description', 'content', 'variables',
            'output_format', 'ai_config', 'tags'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(template, field, data[field])
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '内容模板更新成功',
            'data': {
                'template': template.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新内容模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新内容模板失败'
        }), 500


@content_bp.route('/templates/<template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """删除内容模板"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        template = ContentTemplate.query.filter_by(
            id=template_id, user_id=current_user.id
        ).first()
        if not template:
            return jsonify({
                'success': False,
                'message': '内容模板不存在'
            }), 404
        
        # 删除相关的生成内容
        GeneratedContent.query.filter_by(template_id=template_id).delete()
        
        # 删除模板
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '内容模板删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除内容模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除内容模板失败'
        }), 500


@content_bp.route('/templates/<template_id>/preview', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def preview_template(template_id):
    """预览模板生成效果"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        template = ContentTemplate.query.filter_by(
            id=template_id, user_id=current_user.id
        ).first()
        if not template:
            return jsonify({
                'success': False,
                'message': '内容模板不存在'
            }), 404
        
        data = request.get_json() or {}
        preview_data = data.get('data', {})
        
        # 生成预览
        preview_result = template.generate_preview(preview_data)
        
        return jsonify({
            'success': True,
            'message': '模板预览生成成功',
            'data': {
                'template_id': template_id,
                'preview_data': preview_data,
                'preview_result': preview_result
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"模板预览失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'模板预览失败: {str(e)}'
        }), 500


@content_bp.route('/generate', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def generate_content():
    """生成内容"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        template_id = data.get('template_id')
        input_data = data.get('input_data', {})
        
        if not template_id:
            return jsonify({
                'success': False,
                'message': '模板ID不能为空'
            }), 400
        
        # 获取模板
        template = ContentTemplate.query.filter_by(
            id=template_id, user_id=current_user.id
        ).first()
        if not template:
            return jsonify({
                'success': False,
                'message': '内容模板不存在'
            }), 404
        
        # 检查模板状态
        if template.status != 'active':
            return jsonify({
                'success': False,
                'message': '模板未激活，无法生成内容'
            }), 400
        
        # 创建生成内容记录
        generated_content = GeneratedContent(
            template_id=template_id,
            user_id=current_user.id,
            input_data=input_data,
            generation_config=data.get('generation_config', {}),
            ai_config=data.get('ai_config', template.ai_config)
        )
        
        try:
            # 生成内容
            result = template.generate_content(input_data)
            
            # 更新生成记录
            generated_content.generated_content = result.get('content', '')
            generated_content.status = 'completed'
            generated_content.ai_usage = result.get('ai_usage', {})
            generated_content.quality_score = result.get('quality_score', 0.0)
            generated_content.metadata = result.get('metadata', {})
            
            # 更新模板使用统计
            template.increment_usage()
            
        except Exception as e:
            # 生成失败
            generated_content.status = 'failed'
            generated_content.error_message = str(e)
            current_app.logger.error(f"内容生成失败: {str(e)}")
        
        db.session.add(generated_content)
        db.session.commit()
        
        if generated_content.status == 'completed':
            return jsonify({
                'success': True,
                'message': '内容生成成功',
                'data': {
                    'content': generated_content.to_dict(include_content=True)
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'内容生成失败: {generated_content.error_message}',
                'data': {
                    'content': generated_content.to_dict()
                }
            }), 500
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"生成内容失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '生成内容失败，请稍后重试'
        }), 500


@content_bp.route('/contents', methods=['GET'])
@jwt_required()
def get_generated_contents():
    """获取生成内容列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        template_id = request.args.get('template_id')
        
        # 构建查询
        query = GeneratedContent.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter(GeneratedContent.status == status)
        
        if template_id:
            query = query.filter(GeneratedContent.template_id == template_id)
        
        # 排序和分页
        query = query.order_by(GeneratedContent.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        contents = [content.to_dict() for content in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取生成内容列表成功',
            'data': {
                'contents': contents,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取生成内容列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取生成内容列表失败'
        }), 500


@content_bp.route('/contents/<content_id>', methods=['GET'])
@jwt_required()
def get_generated_content(content_id):
    """获取生成内容详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        content = GeneratedContent.query.filter_by(
            id=content_id, user_id=current_user.id
        ).first()
        if not content:
            return jsonify({
                'success': False,
                'message': '生成内容不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '获取生成内容详情成功',
            'data': {
                'content': content.to_dict(include_content=True)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取生成内容详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取生成内容详情失败'
        }), 500


@content_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_content_stats():
    """获取内容生成统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 模板统计
        template_stats = {
            'total': ContentTemplate.query.filter_by(user_id=current_user.id).count(),
            'active': ContentTemplate.query.filter_by(user_id=current_user.id, status='active').count(),
            'inactive': ContentTemplate.query.filter_by(user_id=current_user.id, status='inactive').count()
        }
        
        # 生成内容统计
        content_stats = {
            'total': GeneratedContent.query.filter_by(user_id=current_user.id).count(),
            'completed': GeneratedContent.query.filter_by(user_id=current_user.id, status='completed').count(),
            'failed': GeneratedContent.query.filter_by(user_id=current_user.id, status='failed').count(),
            'processing': GeneratedContent.query.filter_by(user_id=current_user.id, status='processing').count()
        }
        
        return jsonify({
            'success': True,
            'message': '获取统计信息成功',
            'data': {
                'template_stats': template_stats,
                'content_stats': content_stats
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败'
        }), 500