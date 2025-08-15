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


@tasks_bp.route('/<task_id>/command', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def get_task_command(task_id):
    """生成任务执行命令"""
    try:
        current_app.logger.info(f"开始生成任务命令，任务ID: {task_id}")
        
        current_user = get_current_user()
        if not current_user:
            current_app.logger.error(f"用户未找到，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        current_app.logger.info(f"用户验证成功，用户ID: {current_user.id}")
        
        # 获取任务
        task = Task.query.filter_by(
            id=task_id, user_id=current_user.id
        ).first()
        if not task:
            current_app.logger.error(f"任务未找到，任务ID: {task_id}, 用户ID: {current_user.id}")
            return jsonify({
                'success': False,
                'message': '任务未找到',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        current_app.logger.info(f"任务找到，任务名称: {task.name}, 类型: {task.type}, URL: {task.url}, 爬虫配置ID: {task.crawler_config_id}")
        
        # 支持爬虫任务和内容生成任务
        if task.type not in ['crawler', 'content_generation']:
            current_app.logger.error(f"不支持的任务类型: {task.type}，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '只支持爬虫任务和内容生成任务的命令生成',
                'error_code': 'INVALID_TASK_TYPE'
            }), 400
        
        # 根据任务类型处理不同的命令生成逻辑
        if task.type == 'crawler':
            # 爬虫任务的命令生成逻辑
            # 检查必需字段
            if not task.url:
                current_app.logger.error(f"任务缺少URL，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '任务缺少URL',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            if not task.crawler_config_id:
                current_app.logger.error(f"任务缺少爬虫配置ID，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '任务缺少爬虫配置ID',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            # 使用crawler API的命令生成逻辑
            from backend.api.crawler import generate_crawler_command_from_config
            from backend.models.crawler import CrawlerConfig
            
            current_app.logger.info(f"开始获取爬虫配置，配置ID: {task.crawler_config_id}")
            
            # 获取爬虫配置
            crawler_config = CrawlerConfig.query.get(task.crawler_config_id)
            if not crawler_config:
                current_app.logger.error(f"爬虫配置不存在，配置ID: {task.crawler_config_id}")
                return jsonify({
                    'success': False,
                    'message': '爬虫配置不存在',
                    'error_code': 'CONFIG_NOT_FOUND'
                }), 404
            
            current_app.logger.info(f"爬虫配置找到，配置名称: {crawler_config.name}")
            
            # 生成命令
            current_app.logger.info(f"开始生成命令，URL: {task.url}")
            command = generate_crawler_command_from_config(crawler_config, task.url, task_id)
            current_app.logger.info(f"命令生成成功: {command}")
            
            return jsonify({
                'success': True,
                'message': '命令生成成功',
                'data': {
                    'command': command,
                    'task_id': task_id,
                    'task_name': task.name,
                    'url': task.url,
                    'crawler_config_name': crawler_config.name
                }
            })
            
        elif task.type == 'content_generation':
            # 内容生成任务的命令生成逻辑
            # 检查必需字段
            if not task.crawler_task_id:
                current_app.logger.error(f"内容生成任务缺少爬虫任务ID，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '内容生成任务缺少爬虫任务ID',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            # 生成内容生成任务的命令
            command = f'uv run python -m ai_content_generator.example {task.crawler_task_id}'
            current_app.logger.info(f"内容生成命令生成成功: {command}")
            
            return jsonify({
                'success': True,
                'message': '命令生成成功',
                'data': {
                    'command': command,
                    'task_id': task_id,
                    'task_name': task.name,
                    'crawler_task_id': task.crawler_task_id,
                    'task_type': 'content_generation'
                }
            })
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"生成任务命令失败: {str(e)}")
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'生成命令失败: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
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
        source_task = Task.query.filter_by(id=source_task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        # 构建查询，排除已删除的任务
        query = Task.query.filter_by(user_id=current_user.id, is_deleted=False)
        
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
    """逻辑删除任务"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        # 执行逻辑删除
        task.soft_delete()
        
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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


@tasks_bp.route('/<task_id>/clone', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def clone_task(task_id):
    """克隆任务"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取原任务
        original_task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
        if not original_task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        # 创建克隆任务
        cloned_task = Task(
            name=f"{original_task.name} (副本)",
            type=original_task.type,
            url=original_task.url,
            config=original_task.config,
            crawler_config_id=original_task.crawler_config_id,
            source_task_id=original_task.source_task_id,
            crawler_task_id=original_task.crawler_task_id,
            ai_content_config_id=original_task.ai_content_config_id,
            xpath_config_id=original_task.xpath_config_id,
            user_id=current_user.id,
            description=original_task.description,
            priority=original_task.priority,
            status='pending'  # 克隆的任务状态为待执行
        )
        
        db.session.add(cloned_task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务克隆成功',
            'data': cloned_task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"克隆任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '克隆任务失败，请稍后重试'
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
            'total': Task.query.filter_by(user_id=current_user.id, is_deleted=False).count(),
            'pending': Task.query.filter_by(user_id=current_user.id, status='pending', is_deleted=False).count(),
            'running': Task.query.filter_by(user_id=current_user.id, status='running', is_deleted=False).count(),
            'completed': Task.query.filter_by(user_id=current_user.id, status='completed', is_deleted=False).count(),
            'failed': Task.query.filter_by(user_id=current_user.id, status='failed', is_deleted=False).count(),
            'paused': Task.query.filter_by(user_id=current_user.id, status='paused', is_deleted=False).count()
        }
        
        # 按类型统计
        type_stats = {}
        for task_type in ['crawler', 'content_generation', 'combined']:
            type_stats[task_type] = Task.query.filter_by(
                user_id=current_user.id, type=task_type, is_deleted=False
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id, is_deleted=False).first()
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


@tasks_bp.route('/next-airflow', methods=['GET'])
def get_next_task_for_airflow():
    """为Airflow获取下一个待执行的任务（无需JWT认证）"""
    try:
        # 检查API Key认证
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_api_key = current_app.config.get('AIRFLOW_API_KEY', 'airflow-secret-key')
        
        if not api_key or api_key != expected_api_key:
            return jsonify({
                'success': False,
                'message': 'API Key认证失败'
            }), 401
        
        # 获取查询参数
        task_type = request.args.get('type', '').strip()
        
        if not task_type:
            return jsonify({
                'success': False,
                'message': '任务类型参数不能为空'
            }), 400
        
        # 验证任务类型
        valid_types = ['crawler', 'ai_generation', 'blog_generation']
        if task_type not in valid_types:
            return jsonify({
                'success': False,
                'message': f'无效的任务类型，支持的类型: {", ".join(valid_types)}'
            }), 400
        
        # 查询下一个待执行的任务（不限制用户）
        # 按优先级降序、创建时间升序排列
        query = Task.query.filter(
            and_(
                Task.type == task_type,
                Task.status == 'pending'
            )
        ).order_by(
            Task.priority.desc(),
            Task.created_at.asc()
        )
        
        task = query.first()
        
        if not task:
            return jsonify({
                'success': True,
                'message': f'暂无待执行的{task_type}任务',
                'data': None
            }), 200
        
        # 更新任务状态为执行中
        old_status = task.status
        task.status = 'running'
        task.last_run = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        # 创建任务执行记录
        execution = TaskExecution(
            task_id=task.id,
            status='running'
        )
        
        db.session.add(execution)
        db.session.commit()
        
        current_app.logger.info(f"Airflow获取到下一个{task_type}任务: {task.id} - {task.name}")
        
        return jsonify({
            'success': True,
            'message': '成功获取下一个任务',
            'data': {
                'id': task.id,
                'name': task.name,
                'task_type': task.type,
                'url': task.url,
                'config': task.config,
                'priority': task.priority,
                'status': task.status,
                'old_status': old_status,
                'created_at': task.created_at.isoformat(),
                'started_at': task.last_run.isoformat() if task.last_run else None,
                'execution_id': execution.id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Airflow获取下一个任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取下一个任务失败，请稍后重试'
        }), 500


@tasks_bp.route('/<task_id>/status-airflow', methods=['PUT'])
def update_task_status_for_airflow(task_id):
    """为Airflow更新任务状态（使用API Key认证）"""
    try:
        # 验证API Key
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = current_app.config.get('AIRFLOW_API_KEY', 'airflow-secret-key')
        
        if not api_key or api_key != expected_key:
            current_app.logger.warning(f"无效的API Key访问任务状态更新接口，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '无效的API Key',
                'error_code': 'INVALID_API_KEY'
            }), 401
        
        current_app.logger.info(f"Airflow请求更新任务状态，任务ID: {task_id}")
        
        # 查找任务
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"任务不存在，任务ID: {task_id}")
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
        
        current_app.logger.info(f"任务状态更新成功，任务ID: {task_id}, 状态: {old_status} -> {status}")
        
        return jsonify({
            'success': True,
            'message': '任务状态更新成功',
            'data': {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': status,
                'progress': task.progress,
                'updated_at': task.updated_at.isoformat(),
                'execution_id': execution.id if execution else None
            }
        }), 200
        
    except Exception as e:
        import traceback
        db.session.rollback()
        current_app.logger.error(f"Airflow更新任务状态失败: {str(e)}")
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': '更新任务状态失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@tasks_bp.route('/<task_id>/detail-airflow', methods=['GET'])
def get_task_detail_for_airflow(task_id):
    """为Airflow获取任务详情（使用API Key认证）"""
    try:
        # 验证API Key
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = current_app.config.get('AIRFLOW_API_KEY', 'airflow-secret-key')
        
        if not api_key or api_key != expected_key:
            current_app.logger.warning(f"无效的API Key访问任务详情接口，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '无效的API Key',
                'error_code': 'INVALID_API_KEY'
            }), 401
        
        current_app.logger.info(f"Airflow请求获取任务详情，任务ID: {task_id}")
        
        # 查找任务
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"任务不存在，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        # 获取最近的执行记录
        latest_execution = TaskExecution.query.filter_by(
            task_id=task_id
        ).order_by(TaskExecution.created_at.desc()).first()
        
        return jsonify({
            'success': True,
            'message': '获取任务详情成功',
            'data': {
                'id': task.id,
                'name': task.name,
                'type': task.type,
                'url': task.url,
                'status': task.status,
                'progress': task.progress,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'crawler_config_id': task.crawler_config_id,
                'crawler_task_id': task.crawler_task_id,
                'ai_content_config_id': task.ai_content_config_id,
                'success_count': task.success_count or 0,
                'failure_count': task.failure_count or 0,
                'last_success_at': task.last_success_at.isoformat() if task.last_success_at else None,
                'last_failure_at': task.last_failure_at.isoformat() if task.last_failure_at else None,
                'latest_execution': {
                    'id': latest_execution.id,
                    'status': latest_execution.status,
                    'started_at': latest_execution.started_at.isoformat() if latest_execution.started_at else None,
                    'completed_at': latest_execution.completed_at.isoformat() if latest_execution.completed_at else None,
                    'error_message': latest_execution.error_message,
                    'dag_run_id': latest_execution.dag_run_id
                } if latest_execution else None
            }
        }), 200
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Airflow获取任务详情失败: {str(e)}")
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': '获取任务详情失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@tasks_bp.route('/<task_id>/command-airflow', methods=['GET'])
def get_task_command_for_airflow(task_id):
    """为Airflow获取任务执行命令（使用API Key认证）"""
    try:
        # 验证API Key
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = current_app.config.get('AIRFLOW_API_KEY', 'airflow-secret-key')
        
        if not api_key or api_key != expected_key:
            current_app.logger.warning(f"无效的API Key访问任务命令接口，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '无效的API Key',
                'error_code': 'INVALID_API_KEY'
            }), 401
        
        current_app.logger.info(f"Airflow请求获取任务命令，任务ID: {task_id}")
        
        # 查找任务
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"任务不存在，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        current_app.logger.info(f"任务找到，任务类型: {task.type}, 任务名称: {task.name}")
        
        # 根据任务类型生成命令
        if task.type == 'crawler':
            # 爬虫任务的命令生成逻辑
            if not task.crawler_config_id:
                current_app.logger.error(f"任务缺少爬虫配置ID，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '任务缺少爬虫配置ID',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            # 使用crawler API的命令生成逻辑
            from backend.api.crawler import generate_crawler_command_from_config
            from backend.models.crawler import CrawlerConfig
            
            current_app.logger.info(f"开始获取爬虫配置，配置ID: {task.crawler_config_id}")
            
            # 获取爬虫配置
            crawler_config = CrawlerConfig.query.get(task.crawler_config_id)
            if not crawler_config:
                current_app.logger.error(f"爬虫配置不存在，配置ID: {task.crawler_config_id}")
                return jsonify({
                    'success': False,
                    'message': '爬虫配置不存在',
                    'error_code': 'CONFIG_NOT_FOUND'
                }), 404
            
            current_app.logger.info(f"爬虫配置找到，配置名称: {crawler_config.name}")
            
            # 生成命令
            current_app.logger.info(f"开始生成命令，URL: {task.url}")
            command = generate_crawler_command_from_config(crawler_config, task.url, task_id)
            current_app.logger.info(f"命令生成成功: {command}")
            
            return jsonify({
                'success': True,
                'message': '命令生成成功',
                'data': {
                    'command': command,
                    'task_id': task_id,
                    'task_name': task.name,
                    'url': task.url,
                    'crawler_config_name': crawler_config.name
                }
            })
            
        elif task.type == 'content_generation':
            # 内容生成任务的命令生成逻辑
            # 检查必需字段
            if not task.crawler_task_id:
                current_app.logger.error(f"内容生成任务缺少爬虫任务ID，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '内容生成任务缺少爬虫任务ID',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            # 生成内容生成任务的命令
            command = f'uv run python -m ai_content_generator.example {task.crawler_task_id}'
            current_app.logger.info(f"内容生成命令生成成功: {command}")
            
            return jsonify({
                'success': True,
                'message': '命令生成成功',
                'data': {
                    'command': command,
                    'task_id': task_id,
                    'task_name': task.name,
                    'crawler_task_id': task.crawler_task_id,
                    'task_type': 'content_generation'
                }
            })
        
        else:
            current_app.logger.error(f"不支持的任务类型: {task.type}")
            return jsonify({
                'success': False,
                'message': f'不支持的任务类型: {task.type}',
                'error_code': 'UNSUPPORTED_TASK_TYPE'
            }), 400
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"获取任务命令时发生错误: {str(e)}")
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': '获取任务命令失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500
