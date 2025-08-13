#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.task import Task, TaskExecution
from backend.models.crawler import CrawlerConfig, CrawlerResult

from datetime import datetime, timedelta
from sqlalchemy import func, and_
import psutil
import os
import time


monitoring_bp = Blueprint('monitoring', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def check_admin_permission(user):
    """检查管理员权限"""
    return user and user.role == 'admin'


@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # 检查系统资源
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_status = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'status': 'healthy' if cpu_percent < 90 and memory.percent < 90 and disk.percent < 90 else 'warning'
        }
    except Exception as e:
        system_status = {'status': f'error: {str(e)}'}
    
    overall_status = 'healthy' if db_status == 'healthy' and system_status.get('status') == 'healthy' else 'unhealthy'
    
    return jsonify({
        'success': True,
        'message': '健康检查完成',
        'data': {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status,
            'system': system_status,
            'version': current_app.config.get('VERSION', '1.0.0')
        }
    }), 200


@monitoring_bp.route('/stats/overview', methods=['GET'])
@jwt_required()
def get_overview_stats():
    """获取概览统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 用户统计
        user_stats = {
            'total_tasks': Task.query.filter_by(user_id=current_user.id).count(),
            'running_tasks': Task.query.filter_by(user_id=current_user.id, status='running').count(),
            'total_configs': CrawlerConfig.query.filter_by(user_id=current_user.id).count()
        }
        
        # 最近24小时活动 - 使用简单字段查询
        last_24h = datetime.utcnow() - timedelta(hours=24)
        
        # 获取用户的任务ID列表
        user_task_ids = [task.id for task in Task.query.filter_by(user_id=current_user.id).all()]
        # 获取用户的配置ID列表
        user_config_ids = [config.id for config in CrawlerConfig.query.filter_by(user_id=current_user.id).all()]
        
        recent_activity = {
            'task_executions': TaskExecution.query.filter(
                TaskExecution.task_id.in_(user_task_ids),
                TaskExecution.created_at >= last_24h
            ).count() if user_task_ids else 0,
            'crawler_results': CrawlerResult.query.filter(
                CrawlerResult.config_id.in_(user_config_ids),
                CrawlerResult.created_at >= last_24h
            ).count() if user_config_ids else 0
        }
        
        return jsonify({
            'success': True,
            'message': '获取概览统计成功',
            'data': {
                'user_stats': user_stats,
                'recent_activity': recent_activity,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取概览统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取概览统计失败'
        }), 500


@monitoring_bp.route('/stats/system', methods=['GET'])
@jwt_required()
def get_system_stats():
    """获取系统统计信息（管理员权限）"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        if not check_admin_permission(current_user):
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        # 系统资源统计
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_resources = {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'free': disk.free,
                'used': disk.used,
                'percent': disk.percent
            }
        }
        
        # 数据库统计
        db_stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_tasks': Task.query.count(),
            'running_tasks': Task.query.filter_by(status='running').count(),
            'total_configs': CrawlerConfig.query.count()
        }
        
        # 性能统计
        last_24h = datetime.utcnow() - timedelta(hours=24)
        performance_stats = {
            'task_executions_24h': TaskExecution.query.filter(
                TaskExecution.created_at >= last_24h
            ).count(),
            'successful_executions_24h': TaskExecution.query.filter(
                TaskExecution.created_at >= last_24h,
                TaskExecution.status == 'completed'
            ).count(),
            'failed_executions_24h': TaskExecution.query.filter(
                TaskExecution.created_at >= last_24h,
                TaskExecution.status == 'failed'
            ).count()
        }
        
        return jsonify({
            'success': True,
            'message': '获取系统统计成功',
            'data': {
                'system_resources': system_resources,
                'database_stats': db_stats,
                'performance_stats': performance_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取系统统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取系统统计失败'
        }), 500


@monitoring_bp.route('/stats/performance', methods=['GET'])
@jwt_required()
def get_performance_stats():
    """获取性能统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取时间范围参数
        days = request.args.get('days', 7, type=int)
        if days > 30:
            days = 30  # 限制最大查询范围
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取用户的任务ID列表
        user_task_ids = [task.id for task in Task.query.filter_by(user_id=current_user.id).all()]
        
        # 任务执行性能 - 使用简单字段查询
        task_performance = db.session.query(
            func.date(TaskExecution.created_at).label('date'),
            func.count(TaskExecution.id).label('total'),
            func.sum(func.case([(TaskExecution.status == 'completed', 1)], else_=0)).label('success'),
            func.sum(func.case([(TaskExecution.status == 'failed', 1)], else_=0)).label('failed'),
            func.avg(TaskExecution.duration).label('avg_duration')
        ).filter(
            TaskExecution.task_id.in_(user_task_ids),
            TaskExecution.created_at >= start_date
        ).group_by(func.date(TaskExecution.created_at)).all() if user_task_ids else []
        
        # 获取用户的配置ID列表
        user_config_ids = [config.id for config in CrawlerConfig.query.filter_by(user_id=current_user.id).all()]
        
        # 爬虫性能 - 使用简单字段查询
        crawler_performance = db.session.query(
            func.date(CrawlerResult.created_at).label('date'),
            func.count(CrawlerResult.id).label('total'),
            func.sum(func.case([(CrawlerResult.status == 'success', 1)], else_=0)).label('success'),
            func.avg(CrawlerResult.response_time).label('avg_response_time')
        ).filter(
            CrawlerResult.config_id.in_(user_config_ids),
            CrawlerResult.created_at >= start_date
        ).group_by(func.date(CrawlerResult.created_at)).all() if user_config_ids else []
        

        
        # 格式化数据
        task_data = [{
            'date': row.date.isoformat(),
            'total': row.total,
            'success': row.success or 0,
            'failed': row.failed or 0,
            'success_rate': (row.success or 0) / row.total if row.total > 0 else 0,
            'avg_duration': float(row.avg_duration) if row.avg_duration else 0
        } for row in task_performance]
        
        crawler_data = [{
            'date': row.date.isoformat(),
            'total': row.total,
            'success': row.success or 0,
            'success_rate': (row.success or 0) / row.total if row.total > 0 else 0,
            'avg_response_time': float(row.avg_response_time) if row.avg_response_time else 0
        } for row in crawler_performance]
        
        return jsonify({
            'success': True,
            'message': '获取性能统计成功',
            'data': {
                'task_performance': task_data,
                'crawler_performance': crawler_data,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': datetime.utcnow().isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取性能统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取性能统计失败'
        }), 500


@monitoring_bp.route('/logs', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_logs():
    """获取系统日志（管理员权限）"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        if not check_admin_permission(current_user):
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        # 获取查询参数
        level = request.args.get('level', 'INFO')
        lines = min(request.args.get('lines', 100, type=int), 1000)
        
        # 读取日志文件
        log_file = current_app.config.get('LOG_FILE', 'app.log')
        logs = []
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    # 获取最后N行
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        if line and (level == 'ALL' or level in line):
                            logs.append(line)
            else:
                logs = ['日志文件不存在']
        except Exception as e:
            logs = [f'读取日志文件失败: {str(e)}']
        
        return jsonify({
            'success': True,
            'message': '获取日志成功',
            'data': {
                'logs': logs,
                'level': level,
                'lines': len(logs),
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取日志失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取日志失败'
        }), 500


@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """获取系统告警信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        alerts = []
        
        # 检查用户相关的告警
        # 1. 失败的任务执行 - 使用简单字段查询
        last_hour = datetime.utcnow() - timedelta(hours=1)
        user_task_ids = [task.id for task in Task.query.filter_by(user_id=current_user.id).all()]
        failed_tasks = TaskExecution.query.filter(
            TaskExecution.task_id.in_(user_task_ids),
            TaskExecution.status == 'failed',
            TaskExecution.created_at >= last_hour
        ).count() if user_task_ids else 0
        
        if failed_tasks > 0:
            alerts.append({
                'type': 'warning',
                'message': f'最近1小时内有{failed_tasks}个任务执行失败',
                'timestamp': datetime.utcnow().isoformat(),
                'category': 'task_execution'
            })
        
        # 2. 长时间运行的任务
        long_running_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'running',
            Task.updated_at < datetime.utcnow() - timedelta(hours=2)
        ).count()
        
        if long_running_tasks > 0:
            alerts.append({
                'type': 'info',
                'message': f'有{long_running_tasks}个任务运行时间超过2小时',
                'timestamp': datetime.utcnow().isoformat(),
                'category': 'task_performance'
            })
        
        # 3. 存储空间告警（如果是管理员）
        if check_admin_permission(current_user):
            try:
                disk = psutil.disk_usage('/')
                if disk.percent > 85:
                    alerts.append({
                        'type': 'error' if disk.percent > 95 else 'warning',
                        'message': f'磁盘使用率达到{disk.percent:.1f}%',
                        'timestamp': datetime.utcnow().isoformat(),
                        'category': 'system_resource'
                    })
            except Exception:
                pass
        
        return jsonify({
            'success': True,
            'message': '获取告警信息成功',
            'data': {
                'alerts': alerts,
                'count': len(alerts),
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取告警信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取告警信息失败'
        }), 500


@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """获取实时指标"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取用户的任务ID列表
        user_task_ids = [task.id for task in Task.query.filter_by(user_id=current_user.id).all()]
        
        # 实时指标
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_metrics': {
                'active_tasks': Task.query.filter_by(
                    user_id=current_user.id, status='running'
                ).count(),
                'pending_tasks': Task.query.filter_by(
                    user_id=current_user.id, status='pending'
                ).count(),
                'total_executions_today': TaskExecution.query.filter(
                    TaskExecution.task_id.in_(user_task_ids),
                    func.date(TaskExecution.created_at) == datetime.utcnow().date()
                ).count() if user_task_ids else 0
            }
        }
        
        # 如果是管理员，添加系统指标
        if check_admin_permission(current_user):
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                metrics['system_metrics'] = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'active_connections': db.session.execute(
                        'SELECT count(*) FROM information_schema.processlist'
                    ).scalar() if current_app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('mysql') else 0
                }
            except Exception as e:
                metrics['system_metrics'] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'message': '获取实时指标成功',
            'data': metrics
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取实时指标失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取实时指标失败'
        }), 500