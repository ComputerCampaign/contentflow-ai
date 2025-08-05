#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.task import Task, TaskExecution
from backend.models.crawler import CrawlerConfig
from backend.models.content import ContentTemplate
from datetime import datetime
from sqlalchemy import and_, or_


tasks_bp = Blueprint('tasks', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def validate_task_config(task_type, config):
    """验证任务配置"""
    if not isinstance(config, dict):
        return False, "配置必须是JSON对象"
    
    if task_type == 'crawler':
        required_fields = ['crawler_config_id']
        for field in required_fields:
            if field not in config:
                return False, f"爬虫任务缺少必需字段: {field}"
        
        # 验证爬虫配置是否存在
        crawler_config = CrawlerConfig.query.get(config['crawler_config_id'])
        if not crawler_config:
            return False, "指定的爬虫配置不存在"
    
    elif task_type == 'content_generation':
        required_fields = ['template_id']
        for field in required_fields:
            if field not in config:
                return False, f"内容生成任务缺少必需字段: {field}"
        
        # 验证模板是否存在
        template = ContentTemplate.query.get(config['template_id'])
        if not template:
            return False, "指定的内容模板不存在"
    
    elif task_type == 'full_pipeline':
        required_fields = ['crawler_config_id', 'template_id']
        for field in required_fields:
            if field not in config:
                return False, f"全流程任务缺少必需字段: {field}"
    
    return True, "配置验证通过"


@tasks_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_task():
    """创建新任务"""
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
        task_type = data.get('type', '')
        config = data.get('config', {})
        
        if not all([name, task_type]):
            return jsonify({
                'success': False,
                'message': '任务名称和类型不能为空'
            }), 400
        
        # 验证任务类型
        valid_types = ['crawler', 'content_generation', 'full_pipeline']
        if task_type not in valid_types:
            return jsonify({
                'success': False,
                'message': f'无效的任务类型，支持的类型: {", ".join(valid_types)}'
            }), 400
        
        # 验证任务配置
        is_valid, message = validate_task_config(task_type, config)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # 创建任务
        task = Task(
            name=name,
            type=task_type,
            config=config,
            user_id=current_user.id,
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            schedule_config=data.get('schedule_config', {}),
            timeout_seconds=data.get('timeout_seconds', 3600),
            retry_count=data.get('retry_count', 3),
            tags=data.get('tags', [])
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'data': {
                'task': task.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建任务失败，请稍后重试'
        }), 500


@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取任务列表"""
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
        task_type = request.args.get('type')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = Task.query.filter_by(user_id=current_user.id)
        
        # 状态过滤
        if status:
            query = query.filter(Task.status == status)
        
        # 类型过滤
        if task_type:
            query = query.filter(Task.type == task_type)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    Task.name.contains(search),
                    Task.description.contains(search)
                )
            )
        
        # 排序和分页
        query = query.order_by(Task.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tasks = [task.to_dict() for task in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取任务列表成功',
            'data': {
                'tasks': tasks,
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
        current_app.logger.error(f"获取任务列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取任务列表失败'
        }), 500


@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """获取任务详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        # 获取执行记录
        executions = TaskExecution.query.filter_by(task_id=task_id)\
            .order_by(TaskExecution.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'message': '获取任务详情成功',
            'data': {
                'task': task.to_dict(include_stats=True),
                'recent_executions': [exec.to_dict() for exec in executions]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取任务详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取任务详情失败'
        }), 500


@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """更新任务"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        # 检查任务状态
        if task.status == 'running':
            return jsonify({
                'success': False,
                'message': '运行中的任务无法修改'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 可更新的字段
        updatable_fields = [
            'name', 'description', 'config', 'priority', 
            'schedule_config', 'timeout_seconds', 'retry_count', 'tags'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'config':
                    # 验证配置
                    is_valid, message = validate_task_config(task.type, data[field])
                    if not is_valid:
                        return jsonify({
                            'success': False,
                            'message': message
                        }), 400
                
                setattr(task, field, data[field])
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务更新成功',
            'data': {
                'task': task.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新任务失败'
        }), 500


@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        # 检查任务状态
        if task.status == 'running':
            return jsonify({
                'success': False,
                'message': '运行中的任务无法删除'
            }), 400
        
        # 删除相关的执行记录
        TaskExecution.query.filter_by(task_id=task_id).delete()
        
        # 删除任务
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除任务失败'
        }), 500


@tasks_bp.route('/<task_id>/control', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def control_task(task_id):
    """控制任务执行"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        action = data.get('action', '').lower()
        valid_actions = ['start', 'stop', 'pause', 'resume']
        
        if action not in valid_actions:
            return jsonify({
                'success': False,
                'message': f'无效的操作，支持的操作: {", ".join(valid_actions)}'
            }), 400
        
        # 执行控制操作
        if action == 'start':
            if task.status == 'running':
                return jsonify({
                    'success': False,
                    'message': '任务已在运行中'
                }), 400
            
            # 启动任务
            execution = task.start_execution()
            message = '任务启动成功'
            
        elif action == 'stop':
            if task.status not in ['running', 'paused']:
                return jsonify({
                    'success': False,
                    'message': '只能停止运行中或暂停的任务'
                }), 400
            
            # 停止任务
            task.stop_execution()
            message = '任务停止成功'
            
        elif action == 'pause':
            if task.status != 'running':
                return jsonify({
                    'success': False,
                    'message': '只能暂停运行中的任务'
                }), 400
            
            # 暂停任务
            task.pause_execution()
            message = '任务暂停成功'
            
        elif action == 'resume':
            if task.status != 'paused':
                return jsonify({
                    'success': False,
                    'message': '只能恢复暂停的任务'
                }), 400
            
            # 恢复任务
            task.resume_execution()
            message = '任务恢复成功'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'task': task.to_dict(),
                'action': action
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"控制任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '控制任务失败'
        }), 500


@tasks_bp.route('/<task_id>/executions', methods=['GET'])
@jwt_required()
def get_task_executions(task_id):
    """获取任务执行记录"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # 构建查询
        query = TaskExecution.query.filter_by(task_id=task_id)
        
        if status:
            query = query.filter(TaskExecution.status == status)
        
        # 排序和分页
        query = query.order_by(TaskExecution.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        executions = [execution.to_dict() for execution in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取执行记录成功',
            'data': {
                'executions': executions,
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
        current_app.logger.error(f"获取执行记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取执行记录失败'
        }), 500


@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """获取任务统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 统计各状态任务数量
        stats = {
            'total': Task.query.filter_by(user_id=current_user.id).count(),
            'pending': Task.query.filter_by(user_id=current_user.id, status='pending').count(),
            'running': Task.query.filter_by(user_id=current_user.id, status='running').count(),
            'completed': Task.query.filter_by(user_id=current_user.id, status='completed').count(),
            'failed': Task.query.filter_by(user_id=current_user.id, status='failed').count(),
            'paused': Task.query.filter_by(user_id=current_user.id, status='paused').count()
        }
        
        # 按类型统计
        type_stats = {}
        for task_type in ['crawler', 'content_generation', 'full_pipeline']:
            type_stats[task_type] = Task.query.filter_by(
                user_id=current_user.id, type=task_type
            ).count()
        
        return jsonify({
            'success': True,
            'message': '获取统计信息成功',
            'data': {
                'status_stats': stats,
                'type_stats': type_stats
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败'
        }), 500