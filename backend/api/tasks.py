#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.task import Task
from backend.models.xpath import XPathConfig
from backend.models.ai_model import AIModelConfig
from backend.models.ai_content import AIContentConfig
from backend.models.crawler_result import CrawlerResult
from backend.models.crawler_configs import CrawlerConfig
from backend.api.crawler_configs import generate_crawler_command_from_config
from datetime import datetime
from sqlalchemy import and_, or_
from functools import wraps
import subprocess
import logging
import json
import os
from logging.handlers import RotatingFileHandler


tasks_bp = Blueprint('tasks', __name__)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            try:
                json_data = request.get_json(silent=True)
                if json_data:
                    api_key = json_data.get('api_key')
            except Exception:
                pass
        
        expected_key = current_app.config.get('AIRFLOW_API_KEY', 'airflow-secret-key')
        
        if not api_key or api_key != expected_key:
            current_app.logger.warning(f"无效的API Key访问接口: {request.path}")
            return jsonify({
                'success': False,
                'message': '无效的API Key',
                'error_code': 'INVALID_API_KEY'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# 配置logging输出到文件
def configure_thread_logging():
    """配置线程中的logging输出到文件"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log')
    
    # 获取root logger
    logger = logging.getLogger()
    
    # 检查是否已经配置过文件handler
    has_file_handler = any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers)
    
    if not has_file_handler:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10240000, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

# 初始化logging配置
configure_thread_logging()

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

# ==================== 爬虫任务相关API ====================
@tasks_bp.route('/crawler', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_crawler_task():
    """创建爬虫任务"""
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
        
        # 检查任务名称是否重复（同一用户下）
        existing_task_by_name = Task.query.filter(
            Task.name == name,
            Task.user_id == current_user.id,
            Task.is_deleted == False
        ).first()
        
        if existing_task_by_name:
            return jsonify({
                'success': False,
                'message': f'任务名称 "{name}" 已存在，请使用其他名称',
                'error_code': 'DUPLICATE_NAME'
            }), 400
        
        # 检查URL是否重复（同一用户下的爬虫任务）
        existing_task_by_url = Task.query.filter(
            Task.url == url,
            Task.user_id == current_user.id,
            Task.type == 'crawler',
            Task.is_deleted == False
        ).first()
        
        if existing_task_by_url:
            return jsonify({
                'success': False,
                'message': f'URL "{url}" 已存在于任务 "{existing_task_by_url.name}" 中，请使用其他URL',
                'error_code': 'DUPLICATE_URL'
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
        db.session.flush()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'data': {
                'task_id': task.id,
                'name': task.name,
                'type': task.type,
                'url': task.url,
                'status': task.status
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建爬虫任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建任务失败',
            'error': str(e)
        }), 500

@tasks_bp.route('/crawler/results/upload', methods=['POST'])
def upload_crawler_results():
    """上传爬虫结果"""
    try:
        # 验证API密钥
        api_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('AIRFLOW_API_KEY')
        if not api_key or api_key != expected_key:
            return jsonify({
                'success': False,
                'message': '无效的API密钥'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证必需字段
        required_fields = ['results']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        results = data['results']
        config_id = data.get('config_id', '')  # 可选的配置ID
        
        # 批量创建爬虫结果
        created_results = []
        for result_data in results:
            try:
                crawler_result = CrawlerResult(
                    task_id=result_data.get('task_id'),
                    url=result_data.get('url', ''),
                    config_id=config_id,
                    title=result_data.get('title'),
                    content=result_data.get('content'),
                    extracted_data=result_data.get('extracted_data'),
                    page_metadata=result_data.get('page_metadata'),
                    status=result_data.get('status', 'success'),
                    error_message=result_data.get('error_message'),
                    response_code=result_data.get('response_code'),
                    response_time=result_data.get('response_time'),
                    content_type=result_data.get('content_type'),
                    content_length=result_data.get('content_length'),
                    processing_time=result_data.get('processing_time'),
                    retry_count=result_data.get('retry_count', 0),
                    images=result_data.get('images'),
                    files=result_data.get('files')
                )
                
                db.session.add(crawler_result)
                created_results.append(crawler_result)
                
            except Exception as e:
                current_app.logger.error(f"创建爬虫结果失败: {str(e)}")
                continue
        
        # 统计结果
        success_count = len([r for r in created_results if r.status == 'success'])
        failed_count = len([r for r in created_results if r.status == 'failed'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功上传 {len(created_results)} 条爬虫结果',
            'data': {
                'uploaded_count': len(created_results),
                'success_count': success_count,
                'failed_count': failed_count
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"上传爬虫结果失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '上传爬虫结果失败，请稍后重试'
        }), 500

# ==================== 文本生成任务相关API ====================
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
        ai_model_config_name = data.get('ai_model_config_name', '').strip()
        
        if not all([name, source_task_id, ai_model_config_name]):
            return jsonify({
                'success': False,
                'message': '任务名称、源任务ID和AI模型配置名称不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查任务名称是否重复
        existing_task = Task.query.filter_by(
            name=name,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        if existing_task:
            return jsonify({
                'success': False,
                'message': '任务名称已存在，请使用其他名称',
                'error_code': 'DUPLICATE_TASK_NAME'
            }), 409
        
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
        
        # 验证AI模型配置是否存在
        ai_config = AIModelConfig.query.filter_by(name=ai_model_config_name).first()
        if not ai_config:
            return jsonify({
                'success': False,
                'message': '指定的AI模型配置不存在',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 构建任务配置
        config = {
            'ai_model_config_name': ai_model_config_name,
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
            ai_content_config_id=ai_config.id,
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

# ==================== 通用的任务管理 ====================
@tasks_bp.route('/<task_id>/results', methods=['GET'])
@jwt_required()
def get_task_results(task_id):
    """获取任务结果"""
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
        
        if task.type == 'crawler':
            # 爬虫任务结果
            from backend.models.crawler_result import CrawlerResult
            
            # 获取该任务的所有爬虫结果（优先使用task_id查询）
            crawler_results = []
            
            # 首先尝试通过id查询（id现在就是task_id）
            task_result = CrawlerResult.query.filter_by(id=task_id).first()
            if task_result:
                crawler_results = [task_result]
           
            crawler_results_data = []
            # 添加爬虫结果详情
            for crawler_result in crawler_results:
                result_data = {
                    'id': crawler_result.id,
                    'url': crawler_result.url,
                    'title': crawler_result.title,
                    'content_preview': crawler_result.content[:200] + '...' if crawler_result.content and len(crawler_result.content) > 200 else crawler_result.content,
                    'content_length': len(crawler_result.content) if crawler_result.content else 0,
                    'extracted_data': crawler_result.extracted_data,
                    'page_metadata': crawler_result.page_metadata,
                    'created_at': crawler_result.created_at.isoformat() if crawler_result.created_at else None
                }
                crawler_results_data.append(result_data)
            
            return jsonify({
                'success': True,
                'message': '获取任务结果成功',
                'data': {
                    'task_id': task_id,
                    'task_name': task.name,
                    'task_type': task.type,
                    'status': task.status,
                    'start_time': task.last_run.isoformat() if task.last_run else None,
                    'end_time': task.updated_at.isoformat() if task.updated_at else None,
                    'items_processed': len(crawler_results),
                    'items_success': len([r for r in crawler_results if r.status == 'success']),
                    'items_failed': len([r for r in crawler_results if r.status == 'failed']),
                    'error_message': None,
                    'crawler_results': crawler_results_data
                }
            }), 200
        
        elif task.type == 'content_generation':
            return jsonify({
                'success': True,
                'message': '获取任务结果成功',
                'data': {
                    'task_id': task_id,
                    'task_name': task.name,
                    'task_type': task.type,
                    'status': task.status,
                    'execution_id': None,  # TaskExecution功能已移除
                    'execution_status': task.status,
                    'start_time': task.last_run.isoformat() if task.last_run else None,
                    'end_time': task.updated_at.isoformat() if task.updated_at else None,
                    'items_processed': 0,
                    'items_success': 0,
                    'items_failed': 0,
                    'error_message': None,
                    'result': {},  # TaskExecution功能已移除
                    'generated_content': []
                }
            }), 200
    
    except Exception as e:
        current_app.logger.error(f"获取任务结果失败: {str(e)}")
        # 根据错误类型返回更友好的错误信息
        error_message = '获取任务结果失败'
        
        return jsonify({
            'success': False,
            'message': error_message,
            'data': {
                'task_id': task_id if 'task_id' in locals() else None,
                'task_name': None,
                'task_type': None,
                'status': 'error',
                'execution_id': None,
                'execution_status': 'error',
                'start_time': None,
                'end_time': None,
                'items_processed': 0,
                'items_success': 0,
                'items_failed': 0,
                'error_message': str(e),
                'crawler_results': []
            }
        }), 500

@tasks_bp.route('/<task_id>/execute-airflow', methods=['POST'])
@api_key_required
def execute_task_for_airflow(task_id):
    """为Airflow执行任务（使用API Key认证）"""
    try:
        # 查找任务
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"❌ [BACKEND] 任务不存在，任务ID: {task_id}")
            return jsonify({
                'success': False,
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        # 检查任务状态
        allowed_statuses = ['pending', 'failed', 'running']
        if task.status not in allowed_statuses:
            return jsonify({
                'success': False,
                'message': f'任务状态不允许执行，当前状态: {task.status}',
                'error_code': 'INVALID_TASK_STATUS'
            }), 400

        # 获取执行命令
        if task.type == 'crawler':
            # 获取爬虫配置
            crawler_config = CrawlerConfig.query.get(task.crawler_config_id)
            if not crawler_config:
                current_app.logger.error(f"爬虫配置不存在，配置ID: {task.crawler_config_id}")
                return jsonify({
                    'success': False,
                    'message': '爬虫配置不存在',
                    'error_code': 'CONFIG_NOT_FOUND'
                }), 404
            
            # 生成命令
            command = generate_crawler_command_from_config(crawler_config, task.url, task_id, task.name)
            current_app.logger.info(f"生成的执行命令: {command}")
            
        elif task.type == 'content_generation':
            if not task.crawler_task_id:
                current_app.logger.error(f"内容生成任务缺少爬虫任务ID，任务ID: {task_id}")
                return jsonify({
                    'success': False,
                    'message': '内容生成任务缺少爬虫任务ID',
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            # 获取爬虫任务的名称
            crawler_task = Task.query.get(task.crawler_task_id)
            if not crawler_task:
                current_app.logger.error(f"源爬虫任务不存在，任务ID: {task.crawler_task_id}")
                return jsonify({
                    'success': False,
                    'message': '源爬虫任务不存在',
                    'error_code': 'CRAWLER_TASK_NOT_FOUND'
                }), 404
            
            command = f'uv run python -m ai_content_generator.content_generator --task-id {task_id} --crawler-task-name {crawler_task.name}'
            current_app.logger.info(f"生成的执行命令: {command}")
            
        else:
            current_app.logger.error(f"不支持的任务类型: {task.type}")
            return jsonify({
                'success': False,
                'message': f'不支持的任务类型: {task.type}',
                'error_code': 'UNSUPPORTED_TASK_TYPE'
            }), 400
        
        # 更新任务状态为运行中
        task.status = 'running'
        task.last_run = datetime.utcnow()
        
        db.session.commit()
        current_app.logger.info(f"✅ [BACKEND] 任务 {task_id} 状态已更新为运行中，开始时间: {task.last_run}")
        
        # 直接启动命令，不监听子进程
        # 设置工作目录为项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            # 使用 Popen 启动进程但不等待结果
            # 爬虫模块会在执行完成后主动调用后端接口更新状态
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=project_root,
                stdout=subprocess.DEVNULL,  # 不捕获输出
                stderr=subprocess.DEVNULL,  # 不捕获错误
                start_new_session=True      # 创建新的进程组，避免被父进程影响
            )
        except Exception as e:
            current_app.logger.error(f"❌ [BACKEND] 启动命令失败: {str(e)}")
            task.status = 'failed'
            task.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'启动任务失败: {str(e)}',
                'error_code': 'EXECUTION_ERROR'
            }), 500
        
        response_data = {
            'success': True,
            'message': '任务已开始执行',
            'data': {
                'task_id': task_id,
                'task_name': task.name,
                'command': command,
                'status': 'running',
                'started_at': task.last_run.isoformat() if task.last_run else None
            }
        }
        return jsonify(response_data)
    except Exception as e:
        import traceback
        current_app.logger.error(f"执行任务时发生错误: {str(e)}")
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        
        # 如果任务状态已更新为运行中，需要回滚
        try:
            task_obj = Task.query.get(task_id)
            if task_obj and task_obj.status == 'running':
                task_obj.status = 'failed'
                task_obj.updated_at = datetime.utcnow()
                db.session.commit()
        except:
            pass
            
        return jsonify({
            'success': False,
            'message': '执行任务失败',
            'error_code': 'INTERNAL_ERROR'
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
            command = generate_crawler_command_from_config(crawler_config, task.url, task_id, task.name)
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
            
            # 获取AI内容配置ID
            ai_content_config_id = None
            if hasattr(task, 'config') and task.config:
                
                try:
                    config_data = json.loads(task.config) if isinstance(task.config, str) else task.config
                    ai_content_config_id = config_data.get('ai_content_config_id')
                except (json.JSONDecodeError, AttributeError):
                    current_app.logger.warning(f"任务配置解析失败，任务ID: {task_id}")
            
            # 获取爬虫任务的名称
            crawler_task = Task.query.get(task.crawler_task_id)
            if not crawler_task:
                current_app.logger.error(f"源爬虫任务不存在，任务ID: {task.crawler_task_id}")
                return jsonify({
                    'success': False,
                    'message': '源爬虫任务不存在',
                    'error_code': 'CRAWLER_TASK_NOT_FOUND'
                }), 404
            
            # 如果没有AI配置ID，使用默认命令
            if not ai_content_config_id:
                current_app.logger.warning(f"内容生成任务缺少AI内容配置ID，使用默认命令，任务ID: {task_id}")
                command = f'uv run python -m ai_content_generator.content_generator --task-id {task_id} --crawler-task-name {crawler_task.name}'
            else:
                # 验证AI内容配置是否存在
                ai_config = AIContentConfig.query.get(ai_content_config_id)
                if not ai_config:
                    current_app.logger.error(f"AI内容配置不存在，配置ID: {ai_content_config_id}")
                    return jsonify({
                        'success': False,
                        'message': 'AI内容配置不存在',
                        'error_code': 'CONFIG_NOT_FOUND'
                    }), 404
                
                # 生成带AI配置的命令
                command = f'uv run python -m ai_content_generator.content_generator --task-id {task_id} --crawler-task-name {crawler_task.name} --ai-config-id {ai_content_config_id}'
                current_app.logger.info(f"使用AI配置 {ai_config.name} 生成命令")
            
            current_app.logger.info(f"内容生成命令生成成功: {command}")
            
            return jsonify({
                'success': True,
                'message': '命令生成成功',
                'data': {
                    'command': command,
                    'task_id': task_id,
                    'task_name': task.name,
                    'crawler_task_id': task.crawler_task_id,
                    'ai_content_config_id': ai_content_config_id,
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
        page_str = request.args.get('page', '1')
        try:
            page = int(page_str)
        except (ValueError, TypeError):
            page = 1
        
        per_page_str = request.args.get('pageSize', '20')
        try:
            per_page = min(int(per_page_str), 100)
        except (ValueError, TypeError):
            per_page = 20
        status = request.args.get('status')
        task_type = request.args.get('task_type')
        priority = request.args.get('priority')
        # 转换priority为整数类型（如果不为None且不为'undefined'）
        if priority and priority != 'undefined':
            try:
                priority = int(priority)
            except (ValueError, TypeError):
                priority = None
        keyword = request.args.get('keyword')
        search = request.args.get('search', keyword if keyword else '').strip()
        
        # 处理前端发送的undefined字符串
        if status == 'undefined':
            status = None
        if task_type == 'undefined':
            task_type = None
        if priority == 'undefined':
            priority = None
        if keyword == 'undefined':
            keyword = None
        if search == 'undefined':
            search = ''
        
        # 构建查询，排除已删除的任务
        query = Task.query.filter_by(user_id=current_user.id, is_deleted=False)
        
        # 状态过滤
        if status:
            query = query.filter(Task.status == status)
        
        # 类型过滤
        if task_type:
            query = query.filter(Task.type == task_type)
        
        # 优先级过滤
        if priority:
            query = query.filter(Task.priority == priority)
        
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
        
        # 调试信息
        current_app.logger.info(f"Debug - page: {page} (type: {type(page)}), per_page: {per_page} (type: {type(per_page)})")
        
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
        
        return jsonify({
            'success': True,
            'message': '获取任务详情成功',
            'data': {
                'task': task.to_dict(include_executions=True),
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

@tasks_bp.route('/batch-action', methods=['POST'])
@jwt_required()
def batch_task_action():
    """批量操作任务（删除、启动、暂停、取消）"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401

        data = request.get_json()
        if not data or 'ids' not in data or 'action' not in data:
            return jsonify({
                'success': False,
                'message': '请求数据不完整，需要ids和action字段'
            }), 400

        task_ids = data['ids']
        action = data['action']

        if not isinstance(task_ids, list) or not task_ids:
            return jsonify({
                'success': False,
                'message': 'ids必须是非空列表'
            }), 400

        if action not in ['delete', 'execute', 'pause', 'cancel']:
            return jsonify({
                'success': False,
                'message': '无效的操作类型'
            }), 400

        # 批量查询任务
        tasks = Task.query.filter(
            Task.id.in_(task_ids),
            Task.user_id == current_user.id,
            Task.is_deleted == False
        ).all()

        if len(tasks) != len(task_ids):
            # 找出不存在或不属于当前用户的任务ID
            found_ids = {task.id for task in tasks}
            missing_ids = [tid for tid in task_ids if tid not in found_ids]
            return jsonify({
                'success': False,
                'message': f'部分任务不存在或无权操作: {missing_ids}'
            }), 404

        success_count = 0
        failed_tasks = []

        for task in tasks:
            try:
                if action == 'delete':
                    if task.status == 'running':
                        failed_tasks.append({'id': task.id, 'message': '运行中的任务无法删除'})
                        continue
                    task.soft_delete()
                elif action == 'execute':
                    if task.status == 'running':
                        failed_tasks.append({'id': task.id, 'message': '任务已在运行中'})
                        continue
                    # 触发任务执行逻辑，这里简化为更新状态
                    task.status = 'pending' # 假设触发后状态变为pending等待调度
                    # TODO: 实际集成Airflow触发DAG的逻辑
                elif action == 'pause':
                    if task.status not in ['running', 'pending']:
                        failed_tasks.append({'id': task.id, 'message': '只有运行中或待处理的任务才能暂停'})
                        continue
                    task.status = 'paused'
                elif action == 'cancel':
                    if task.status not in ['running', 'pending', 'paused']:
                        failed_tasks.append({'id': task.id, 'message': '只有运行中、待处理或暂停的任务才能取消'})
                        continue
                    task.status = 'cancelled'
                
                task.updated_at = datetime.utcnow()
                db.session.add(task)
                success_count += 1
            except Exception as e:
                failed_tasks.append({'id': task.id, 'message': str(e)})

        db.session.commit()

        if failed_tasks:
            return jsonify({
                'success': False,
                'message': f'部分任务操作失败，成功 {success_count} 个，失败 {len(failed_tasks)} 个。详情：{failed_tasks}',
                'data': {'success_count': success_count, 'failed_tasks': failed_tasks}
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': f'成功对 {success_count} 个任务执行了 {action} 操作'
            }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批量操作任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '批量操作失败'
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
        
        task_type = request.args.get('task_type')

        base_query = Task.query.filter_by(user_id=current_user.id, is_deleted=False)
        if task_type:
            base_query = base_query.filter_by(type=task_type)

        stats = {
            'total': base_query.count(),
            'pending': base_query.filter_by(status='pending').count(),
            'running': base_query.filter_by(status='running').count(),
            'completed': base_query.filter_by(status='completed').count(),
            'failed': base_query.filter_by(status='failed').count(),
            'paused': base_query.filter_by(status='paused').count()
        }

        type_stats = {}
        if not task_type:
            for t_type in ['crawler', 'content_generation', 'combined']:
                type_stats[t_type] = Task.query.filter_by(
                    user_id=current_user.id, type=t_type, is_deleted=False
                ).count()
        else:
            type_stats[task_type] = stats['total']
        
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


@tasks_bp.route('/next-airflow', methods=['GET'])
@api_key_required
def get_next_task_for_airflow():
    """为Airflow获取下一个待执行的任务（无需JWT认证）"""
    try:
        # 获取查询参数
        task_type = request.args.get('type', '').strip()
        
        if not task_type:
            return jsonify({
                'success': False,
                'message': '任务类型参数不能为空'
            }), 400
        
        # 验证任务类型
        valid_types = ['crawler', 'content_generation']
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
        db.session.commit()
        
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
                'execution_id': None  # TaskExecution功能已移除
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
@api_key_required
def update_task_status_for_airflow(task_id):
    """为Airflow更新任务状态（使用API Key认证）"""
    try:
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
        
        current_app.logger.info(f'任务状态更新: {task_id}, 状态: {status}, DAG运行ID: {dag_run_id}, 错误信息: {error_message}')
        
        # 更新任务最后运行时间
        task.last_run = datetime.utcnow()
        
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
                'execution_id': None  # TaskExecution功能已移除
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
        # 查找任务
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"❌ [BACKEND] 任务不存在: {task_id}")
            return jsonify({
                'success': False,
                'message': '任务不存在',
                'error_code': 'TASK_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '获取任务详情成功',
            'data': {
                'id': task.id,
                'status': task.status
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
