# -*- coding: utf-8 -*-
"""
Airflow DAGs 配置文件
统一管理后端API地址和接口配置
"""

import os

# 后端API基础配置
BACKEND_BASE_URL = os.environ.get('BACKEND_BASE_URL', 'http://192.168.212.188:5002')

# API接口配置
API_ENDPOINTS = {
    # 任务管理接口
    'tasks': {
        'get_next_crawler_task': f'{BACKEND_BASE_URL}/api/v1/tasks/next-airflow',
        'get_next_generation_task': f'{BACKEND_BASE_URL}/api/v1/tasks/next-airflow',
        'get_task_command': f'{BACKEND_BASE_URL}/api/v1/tasks/{{task_id}}/command-airflow',
        'update_task_status': f'{BACKEND_BASE_URL}/api/v1/tasks/{{task_id}}/status-airflow',
        'get_task_detail': f'{BACKEND_BASE_URL}/api/v1/tasks/{{task_id}}/detail-airflow',
    },
    
    # 爬虫相关接口
    'crawler': {
        'get_crawler_config': f'{BACKEND_BASE_URL}/api/v1/crawler/config',
        'update_crawler_status': f'{BACKEND_BASE_URL}/api/v1/crawler/status',
        'upload_crawler_results': f'{BACKEND_BASE_URL}/api/v1/crawler/results',
    },
    
    # AI内容生成接口
    'ai_content': {
        'get_generation_config': f'{BACKEND_BASE_URL}/api/v1/ai/config',
        'update_generation_status': f'{BACKEND_BASE_URL}/api/v1/ai/status',
        'upload_generation_results': f'{BACKEND_BASE_URL}/api/v1/ai/results',
    },
    
    # 监控和健康检查接口
    'monitoring': {
        'health_check': f'{BACKEND_BASE_URL}/api/v1/monitor/health',
        'system_status': f'{BACKEND_BASE_URL}/api/v1/monitor/status',
    }
}

# HTTP请求配置
API_CONFIG = {
    'base_url': BACKEND_BASE_URL,  # 后端API基础地址
    'headers': {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Airflow-DAG/1.0'
    },
    'timeout': 30,  # 请求超时时间（秒）
    'retry_count': 3,  # 重试次数
    'retry_delay': 5,  # 重试间隔（秒）
}

# 任务类型配置
TASK_TYPES = {
    'CRAWLER': 'crawler',
    'AI_GENERATION': 'ai_generation',
    'BLOG_GENERATION': 'blog_generation',
}

# 任务状态配置
TASK_STATUS = {
    'PENDING': 'pending',
    'IN_PROGRESS': 'in_progress',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled',
}

# DAG默认配置
DAG_CONFIG = {
    'default_args': {
        'owner': 'crawler-platform',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
    },
    'crawler_dag': {
        'schedule_interval_minutes': 30,
        'description': '爬虫任务处理流水线',
        'tags': ['crawler', 'pipeline'],
    },
    'content_generation_dag': {
        'schedule_interval_minutes': 45,
        'description': 'AI内容生成任务流水线',
        'tags': ['ai', 'content', 'generation'],
    }
}

# 工具函数
def get_api_url(category, endpoint, **kwargs):
    """
    获取API接口URL
    
    Args:
        category: 接口分类（如 'tasks', 'crawler'）
        endpoint: 接口名称
        **kwargs: URL模板参数
    
    Returns:
        str: 完整的API URL
    """
    if category not in API_ENDPOINTS:
        raise ValueError(f"未知的API分类: {category}")
    
    if endpoint not in API_ENDPOINTS[category]:
        raise ValueError(f"未知的接口: {category}.{endpoint}")
    
    url_template = API_ENDPOINTS[category][endpoint]
    return url_template.format(**kwargs)

def get_task_type_param(task_type):
    """
    获取任务类型参数
    
    Args:
        task_type: 任务类型
    
    Returns:
        str: 任务类型参数值
    """
    return TASK_TYPES.get(task_type.upper(), task_type)

def get_request_config():
    """
    获取HTTP请求配置
    
    Returns:
        dict: 请求配置字典
    """
    return API_CONFIG.copy()