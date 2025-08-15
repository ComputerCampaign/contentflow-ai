# -*- coding: utf-8 -*-
"""
Airflow DAG配置模块

提供统一的配置管理，包括API配置、任务状态常量等
"""

from .config import (
    API_CONFIG,
    get_api_url,
    get_task_type_param,
    TASK_STATUS,
    DAG_CONFIG
)

__all__ = [
    'API_CONFIG',
    'get_api_url',
    'get_task_type_param',
    'TASK_STATUS',
    'DAG_CONFIG'
]