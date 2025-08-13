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
from backend.models.xpath import XPathConfig
from backend.models.ai_content import AIContentConfig

from backend.utils.xpath_manager import xpath_manager
from datetime import datetime
from sqlalchemy import and_, or_


tasks_bp = Blueprint('tasks', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def validate_task_config(task_type, config, url=None):
    """验证任务配置"""
    if not isinstance(config, dict):
        return False, "配置必须是JSON对象"
    
    if task_type == 'crawler':
        # 爬虫任务必须有URL
        if not url or not url.strip():
            return False, "爬虫任务必须提供目标URL"
        
        # 验证URL格式
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url.strip()):
            return False, "无效的URL格式"
        
        required_fields = ['crawler_config_id']
        for field in required_fields:
            if field not in config:
                return False, f"爬虫任务缺少必需字段: {field}"
        
        # 验证爬虫配置是否存在
        crawler_config = CrawlerConfig.query.get(config['crawler_config_id'])
        if not crawler_config:
            return False, "指定的爬虫配置不存在"
        
        # 验证XPath配置（如果提供）
        if 'xpath_config_id' in config and config['xpath_config_id']:
            xpath_config = XPathConfig.query.get(config['xpath_config_id'])
            if not xpath_config:
                return False, "指定的XPath配置不存在"
    

    
    return True, "配置验证通过"


@tasks_bp.route('/crawler', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_crawler_task():
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
        url = data.get('url', '').strip()
        crawler_config_id = data.get('crawler_config_id', '').strip()
        
        if not all([name, url, crawler_config_id]):
            return jsonify({
                'success': False,
                'message': '任务名称、URL和爬虫配置ID不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证爬虫配置是否存在
        crawler_config = CrawlerConfig.query.get(crawler_config_id)
        if not crawler_config:
            return jsonify({
                'success': False,
                'message': '指定的爬虫配置不存在',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 验证XPath配置（如果提供）
        xpath_config_ids = data.get('xpath_config_ids', [])
        if xpath_config_ids:
            for xpath_id in xpath_config_ids:
                xpath_config = XPathConfig.query.get(xpath_id)
                if not xpath_config:
                    return jsonify({
                        'success': False,
                        'message': f'XPath配置 {xpath_id} 不存在',
                        'error_code': 'CONFIG_NOT_FOUND'
                    }), 404
        
        # 构建任务配置
        config = {
            'crawler_config_id': crawler_config_id,
            'xpath_config_ids': xpath_config_ids
        }
        if data.get('config'):
            config.update(data['config'])
        
        # 创建爬虫任务
        task = Task(
            name=name,
            type='crawler',
            config=config,
            url=url,
            crawler_config_id=crawler_config_id,
            xpath_config_id=xpath_config_ids[0] if xpath_config_ids else None,
            user_id=current_user.id,
            description=data.get('description', ''),
            priority=data.get('priority', 5)
        )
        
        db.session.add(task)
        db.session.flush()  # 获取任务ID但不提交事务
        
        # 如果指定了XPath配置，写入JSON文件
        if xpath_config_ids:
            try:
                # 将选中的XPath配置写入JSON文件
                success = xpath_manager.write_xpath_configs_to_file(xpath_config_ids)
                if not success:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'message': '写入XPath配置文件失败',
                        'error_code': 'XPATH_SYNC_FAILED'
                    }), 500
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"写入XPath配置失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '写入XPath配置失败',
                    'error_code': 'XPATH_SYNC_FAILED'
                }), 500
        
        db.session.commit()
        
        # 生成命令预览
        command_preview = task.get_crawler_params()
        task_dict = task.to_dict()
        task_dict['command_preview'] = command_preview
        
        return jsonify({
            'success': True,
            'message': '爬虫任务创建成功',
            'data': task_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建爬虫任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建爬虫任务失败，请稍后重试'
        }), 500


@tasks_bp.route('/content-generation', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_content_generation_task():
    """创建内容生成任务"""
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
        source_task_id = data.get('source_task_id', '').strip()
        ai_content_config_id = data.get('ai_content_config_id', '').strip()
        
        if not all([name, source_task_id, ai_content_config_id]):
            return jsonify({
                'success': False,
                'message': '任务名称、源任务ID和AI内容配置ID不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证源任务是否存在且已完成
        source_task = Task.query.filter_by(id=source_task_id, user_id=current_user.id).first()
        if not source_task:
            return jsonify({
                'success': False,
                'message': '源任务不存在',
                'error_code': 'SOURCE_TASK_NOT_FOUND'
            }), 404
        
        if source_task.status != 'completed':
            return jsonify({
                'success': False,
                'message': '源任务未完成',
                'error_code': 'SOURCE_TASK_NOT_COMPLETED'
            }), 409
        
        # 验证AI内容配置是否存在
        ai_config = AIContentConfig.query.get(ai_content_config_id)
        if not ai_config:
            return jsonify({
                'success': False,
                'message': '指定的AI内容配置不存在',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 构建任务配置
        config = {
            'ai_content_config_id': ai_content_config_id,
            'source_task_id': source_task_id
        }
        if data.get('config'):
            config.update(data['config'])
        
        # 创建内容生成任务
        task = Task(
            name=name,
            type='content_generation',
            config=config,
            source_task_id=source_task_id,
            crawler_task_id=source_task_id,
            ai_content_config_id=ai_content_config_id,
            user_id=current_user.id,
            description=data.get('description', ''),
            priority=data.get('priority', 5)
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 生成命令预览
        task_dict = task.to_dict()
        task_dict['command_preview'] = f'python example.py {source_task_id}'
        
        return jsonify({
            'success': True,
            'message': '内容生成任务创建成功',
            'data': task_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建内容生成任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建内容生成任务失败，请稍后重试'
        }), 500


@tasks_bp.route('/combined', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_combined_task():
    """创建组合任务（爬虫+内容生成）"""
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
        url = data.get('url', '').strip()
        crawler_config_id = data.get('crawler_config_id', '').strip()
        ai_content_config_id = data.get('ai_content_config_id', '').strip()
        
        if not all([name, url, crawler_config_id, ai_content_config_id]):
            return jsonify({
                'success': False,
                'message': '任务名称、URL、爬虫配置ID和AI内容配置ID不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证爬虫配置是否存在
        crawler_config = CrawlerConfig.query.get(crawler_config_id)
        if not crawler_config:
            return jsonify({
                'success': False,
                'message': '指定的爬虫配置不存在',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 验证AI内容配置是否存在
        ai_config = AIContentConfig.query.get(ai_content_config_id)
        if not ai_config:
            return jsonify({
                'success': False,
                'message': '指定的AI内容配置不存在',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 验证XPath配置（如果提供）
        xpath_config_ids = data.get('xpath_config_ids', [])
        if xpath_config_ids:
            for xpath_id in xpath_config_ids:
                xpath_config = XPathConfig.query.get(xpath_id)
                if not xpath_config:
                    return jsonify({
                        'success': False,
                        'message': f'XPath配置 {xpath_id} 不存在',
                        'error_code': 'CONFIG_NOT_FOUND'
                    }), 404
        
        # 构建任务配置
        config = {
            'crawler_config_id': crawler_config_id,
            'ai_content_config_id': ai_content_config_id,
            'xpath_config_ids': xpath_config_ids
        }
        if data.get('config'):
            config.update(data['config'])
        
        # 创建组合任务
        task = Task(
            name=name,
            type='combined',
            config=config,
            url=url,
            crawler_config_id=crawler_config_id,
            ai_content_config_id=ai_content_config_id,
            xpath_config_id=xpath_config_ids[0] if xpath_config_ids else None,
            user_id=current_user.id,
            description=data.get('description', ''),
            priority=data.get('priority', 5)
        )
        
        db.session.add(task)
        db.session.flush()  # 获取任务ID但不提交事务
        
        # 如果指定了XPath配置，写入JSON文件
        if xpath_config_ids:
            try:
                # 将选中的XPath配置写入JSON文件
                success = xpath_manager.write_xpath_configs_to_file(xpath_config_ids)
                if not success:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'message': '写入XPath配置文件失败',
                        'error_code': 'XPATH_SYNC_FAILED'
                    }), 500
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"写入XPath配置失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '写入XPath配置失败',
                    'error_code': 'XPATH_SYNC_FAILED'
                }), 500
        
        db.session.commit()
        
        # 生成执行计划
        crawler_command = task.get_crawler_params()
        execution_plan = [
            {
                'step': 1,
                'type': 'crawler',
                'command': crawler_command
            },
            {
                'step': 2,
                'type': 'content_generation',
                'command': f'python example.py <crawler_task_id>'
            }
        ]
        
        task_dict = task.to_dict()
        task_dict['execution_plan'] = execution_plan
        
        return jsonify({
            'success': True,
            'message': '组合任务创建成功',
            'data': task_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建组合任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建组合任务失败，请稍后重试'
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
            'name', 'description', 'config', 'url', 'priority', 
            'schedule_config', 'timeout_seconds', 'retry_count', 'tags'
        ]
        
        # 获取URL（用于配置验证）
        url = data.get('url', task.url)
        
        for field in updatable_fields:
            if field in data:
                if field == 'config':
                    # 验证配置
                    is_valid, message = validate_task_config(task.type, data[field], url)
                    if not is_valid:
                        return jsonify({
                            'success': False,
                            'message': message
                        }), 400
                    
                    # 更新外键关联
                    if task.type in ['crawler', 'full_pipeline']:
                        task.crawler_config_id = data[field].get('crawler_config_id')
                        task.xpath_config_id = data[field].get('xpath_config_id')
                    
                    if task.type in ['content_generation', 'full_pipeline']:
                        task.content_template_id = data[field].get('template_id')
                
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


@tasks_bp.route('/<task_id>/status', methods=['PUT'])
@jwt_required()
@limiter.limit("100 per minute")
def update_task_status(task_id):
    """更新任务状态（主要用于Airflow）"""
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
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 获取状态参数
        status = data.get('status', '').strip()
        if not status:
            return jsonify({
                'success': False,
                'message': '状态不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证状态值
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled', 'paused']
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'无效的状态值，支持的状态: {", ".join(valid_statuses)}',
                'error_code': 'INVALID_STATUS'
            }), 400
        
        # 更新任务状态
        old_status = task.status
        task.status = status
        task.updated_at = datetime.utcnow()
        
        # 处理进度信息
        progress = data.get('progress')
        if progress is not None:
            if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
                return jsonify({
                    'success': False,
                    'message': '进度值必须是0-100之间的数字',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            task.progress = progress
        
        # 创建或更新执行记录
        dag_run_id = data.get('dag_run_id')
        error_message = data.get('error_message')
        execution_info = data.get('execution_info', {})
        
        # 查找现有执行记录或创建新的
        execution = None
        if dag_run_id:
            execution = TaskExecution.query.filter_by(
                task_id=task_id,
                dag_run_id=dag_run_id
            ).first()
        
        if not execution:
            # 创建新的执行记录
            execution = TaskExecution(
                task_id=task_id,
                status=status,
                dag_run_id=dag_run_id,
                error_message=error_message,
                execution_info=execution_info,
                started_at=datetime.utcnow() if status == 'running' else None,
                completed_at=datetime.utcnow() if status in ['completed', 'failed', 'cancelled'] else None
            )
            db.session.add(execution)
        else:
            # 更新现有执行记录
            execution.status = status
            execution.error_message = error_message
            execution.execution_info = execution_info
            execution.updated_at = datetime.utcnow()
            
            if status == 'running' and not execution.started_at:
                execution.started_at = datetime.utcnow()
            elif status in ['completed', 'failed', 'cancelled'] and not execution.completed_at:
                execution.completed_at = datetime.utcnow()
        
        # 更新任务统计
        if status == 'completed':
            task.success_count = (task.success_count or 0) + 1
            task.last_success_at = datetime.utcnow()
        elif status == 'failed':
            task.failure_count = (task.failure_count or 0) + 1
            task.last_failure_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务状态更新成功',
            'data': {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': status,
                'progress': task.progress,
                'updated_at': task.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新任务状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新任务状态失败，请稍后重试'
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


@tasks_bp.route('/<task_id>/crawler-params', methods=['GET'])
@jwt_required()
def get_crawler_params(task_id):
    """获取任务的爬虫服务参数"""
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
        
        # 获取爬虫参数
        params = task.get_crawler_params()
        if params is None:
            return jsonify({
                'success': False,
                'message': '该任务不是爬虫任务'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '获取爬虫参数成功',
            'data': {
                'params': params,
                'task_type': task.type
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取爬虫参数失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取爬虫参数失败'
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
        for task_type in ['crawler', 'content_generation', 'combined']:
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


@tasks_bp.route('/<task_id>/cancel', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def cancel_task(task_id):
    """取消任务"""
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
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        # 检查任务状态
        if task.status in ['completed', 'failed', 'cancelled']:
            return jsonify({
                'success': False,
                'message': '任务已完成或已取消，无法再次取消',
                'error_code': 'INVALID_STATUS'
            }), 400
        
        data = request.get_json() or {}
        reason = data.get('reason', '用户手动取消')
        
        # 更新任务状态
        old_status = task.status
        task.status = 'cancelled'
        task.updated_at = datetime.utcnow()
        
        # 创建执行记录
        execution = TaskExecution(
            task_id=task_id,
            status='cancelled',
            error_message=f'任务被取消: {reason}',
            completed_at=datetime.utcnow()
        )
        db.session.add(execution)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务取消成功',
            'data': {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': 'cancelled',
                'reason': reason,
                'cancelled_at': task.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '取消任务失败，请稍后重试'
        }), 500


@tasks_bp.route('/<task_id>/retry', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def retry_task(task_id):
    """重试任务"""
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
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        # 检查任务状态
        if task.status not in ['failed', 'cancelled']:
            return jsonify({
                'success': False,
                'message': '只能重试失败或已取消的任务',
                'error_code': 'INVALID_STATUS'
            }), 400
        
        data = request.get_json() or {}
        
        # 重置配置（如果指定）
        reset_config = data.get('reset_config', False)
        if reset_config and 'config' in data:
            # 验证新配置
            is_valid, message = validate_task_config(task.type, data['config'], task.url)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message,
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            task.config = data['config']
        
        # 更新优先级（如果指定）
        if 'priority' in data:
            priority = data['priority']
            if not isinstance(priority, int) or priority < 1 or priority > 10:
                return jsonify({
                    'success': False,
                    'message': '优先级必须是1-10之间的整数',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            task.priority = priority
        
        # 重置任务状态
        old_status = task.status
        task.status = 'pending'
        task.progress = 0
        task.updated_at = datetime.utcnow()
        
        # 增加重试计数
        task.retry_count = (task.retry_count or 0) + 1
        
        # 创建新的执行记录
        execution = TaskExecution(
            task_id=task_id,
            status='pending',
            execution_info={'retry_count': task.retry_count, 'reason': data.get('reason', '手动重试')}
        )
        db.session.add(execution)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务重试成功',
            'data': {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': 'pending',
                'retry_count': task.retry_count,
                'priority': task.priority,
                'retried_at': task.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"重试任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '重试任务失败，请稍后重试'
        }), 500