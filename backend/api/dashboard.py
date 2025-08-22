#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard API - 仪表板接口
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.dashboard import Dashboard
from backend.extensions import db
from datetime import datetime, timedelta
import random

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__)


def require_auth():
    """检查用户认证"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return False
        return True
    except:
        return False


def generate_mock_task_trend():
    """生成模拟任务趋势数据"""
    dates = []
    success_data = []
    failed_data = []
    
    # 生成最近7天的数据
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        dates.append(date.strftime('%m-%d'))
        success_data.append(random.randint(10, 50))
        failed_data.append(random.randint(0, 10))
    
    return {
        'dates': dates,
        'success': success_data,
        'failed': failed_data
    }


def generate_mock_stats():
    """生成模拟统计数据"""
    return {
        'total_tasks': random.randint(100, 500),
        'completed_tasks': random.randint(80, 400),
        'failed_tasks': random.randint(5, 50),
        'success_rate': round(random.uniform(0.8, 0.95), 2),
        'avg_duration': round(random.uniform(2.5, 8.0), 1),
        'active_crawlers': random.randint(3, 15)
    }


def generate_mock_crawler_status():
    """生成模拟爬虫状态数据"""
    statuses = ['running', 'idle', 'error', 'stopped']
    crawlers = []
    
    for i in range(random.randint(5, 10)):
        crawlers.append({
            'id': f'crawler_{i+1}',
            'name': f'爬虫{i+1}',
            'status': random.choice(statuses),
            'last_run': (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
            'success_rate': round(random.uniform(0.7, 0.98), 2),
            'total_requests': random.randint(100, 1000)
        })
    
    return crawlers


def generate_mock_system_resources():
    """生成模拟系统资源数据"""
    return {
        'cpu_usage': round(random.uniform(20, 80), 1),
        'memory_usage': round(random.uniform(30, 90), 1),
        'disk_usage': round(random.uniform(40, 85), 1),
        'network_io': {
            'bytes_sent': random.randint(1000000, 10000000),
            'bytes_recv': random.randint(5000000, 50000000)
        },
        'active_connections': random.randint(10, 100)
    }


def generate_mock_resource_history():
    """生成模拟资源历史数据"""
    history = []
    
    for i in range(24):  # 24小时数据
        timestamp = datetime.now() - timedelta(hours=23-i)
        history.append({
            'timestamp': timestamp.isoformat(),
            'cpu': round(random.uniform(20, 80), 1),
            'memory': round(random.uniform(30, 90), 1),
            'disk': round(random.uniform(40, 85), 1)
        })
    
    return history


def generate_mock_recent_activities():
    """生成模拟最近活动数据"""
    activities = []
    activity_types = ['task_completed', 'crawler_started', 'error_occurred', 'user_login']
    
    for i in range(random.randint(5, 15)):
        activities.append({
            'id': f'activity_{i+1}',
            'type': random.choice(activity_types),
            'message': f'活动消息 {i+1}',
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            'user': f'用户{random.randint(1, 10)}',
            'status': random.choice(['success', 'warning', 'error'])
        })
    
    return activities


def generate_mock_quick_actions():
    """生成模拟快速操作数据"""
    return [
        {
            'id': 'start_crawler',
            'name': '启动爬虫',
            'icon': 'play',
            'enabled': True
        },
        {
            'id': 'stop_all',
            'name': '停止所有',
            'icon': 'stop',
            'enabled': True
        },
        {
            'id': 'clear_logs',
            'name': '清理日志',
            'icon': 'trash',
            'enabled': True
        },
        {
            'id': 'export_data',
            'name': '导出数据',
            'icon': 'download',
            'enabled': False
        }
    ]


@dashboard_bp.route('/task-trend', methods=['GET'])
@jwt_required()
def get_task_trends():
    """获取任务趋势数据"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        # 获取或创建dashboard数据
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('task_trend'):
            # 生成并保存模拟数据
            mock_data = generate_mock_task_trend()
            Dashboard.create_or_update_dashboard('main', task_trend=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['task_trend'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取统计信息"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('stats'):
            mock_data = generate_mock_stats()
            Dashboard.create_or_update_dashboard('main', stats=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['stats'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/crawler-status', methods=['GET'])
@jwt_required()
def get_crawler_status():
    """获取爬虫状态"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('crawler_status'):
            mock_data = generate_mock_crawler_status()
            Dashboard.create_or_update_dashboard('main', crawler_status=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['crawler_status'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/system-resources', methods=['GET'])
@jwt_required()
def get_system_resources():
    """获取系统资源"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('system_resources'):
            mock_data = generate_mock_system_resources()
            Dashboard.create_or_update_dashboard('main', system_resources=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['system_resources'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/resource-history', methods=['GET'])
@jwt_required()
def get_resource_history():
    """获取资源历史"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('resource_history'):
            mock_data = generate_mock_resource_history()
            Dashboard.create_or_update_dashboard('main', resource_history=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['resource_history'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """获取最近活动"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('recent_activities'):
            mock_data = generate_mock_recent_activities()
            Dashboard.create_or_update_dashboard('main', recent_activities=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['recent_activities'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/quick-actions', methods=['GET'])
@jwt_required()
def get_quick_actions():
    """获取快速操作"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        dashboard = Dashboard.get_dashboard_data('main')
        if not dashboard or not dashboard.get('quick_actions'):
            mock_data = generate_mock_quick_actions()
            Dashboard.create_or_update_dashboard('main', quick_actions=mock_data)
            return jsonify(mock_data)
        
        return jsonify(dashboard['quick_actions'])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_dashboard():
    """刷新仪表板数据"""
    try:
        if not require_auth():
            return jsonify({'error': '未授权访问'}), 401
        
        # 重新生成所有模拟数据
        dashboard_data = {
            'task_trend': generate_mock_task_trend(),
            'stats': generate_mock_stats(),
            'crawler_status': generate_mock_crawler_status(),
            'system_resources': generate_mock_system_resources(),
            'resource_history': generate_mock_resource_history(),
            'recent_activities': generate_mock_recent_activities(),
            'quick_actions': generate_mock_quick_actions()
        }
        
        Dashboard.create_or_update_dashboard('main', **dashboard_data)
        
        return jsonify({
            'message': '仪表板数据已刷新',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500