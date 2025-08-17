#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本生成任务DAG
处理后端配置的AI内容生成任务，通过API接口获取任务并执行
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import requests
import json
import logging
from config import API_CONFIG, get_api_url, get_task_type_param, TASK_STATUS, DAG_CONFIG
from utils import (get_pending_task, handle_task_success, 
                   handle_task_failure, store_task_results, submit_task_via_api, poll_task_status)

# 默认参数
default_args = {
    'owner': 'crawler-platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG定义
dag = DAG(
    'content_generation_pipeline',
    default_args=default_args,
    description='AI内容生成任务处理流水线',
    schedule_interval=timedelta(minutes=600),  # 每45分钟执行一次
    catchup=False,
    tags=['content-generation', 'ai', 'pipeline'],
)

# 从配置文件获取API配置
api_config = API_CONFIG
api_headers = api_config['headers']
api_timeout = api_config['timeout']
api_retry_count = api_config['retry_count']
api_retry_delay = api_config['retry_delay']

def get_pending_generation_task(**context):
    """
    获取待执行的内容生成任务
    """
    return get_pending_task('AI_GENERATION', **context)

# 任务状态更新功能已移至utils模块中的APIClient类

def handle_generation_success(**context):
    """
    处理内容生成任务成功完成
    """
    handle_task_success('AI_GENERATION', **context)

def handle_generation_failure(**context):
    """
    处理内容生成任务执行失败
    """
    handle_task_failure('AI_GENERATION', **context)

def store_generation_results(**context):
    """
    存储内容生成结果
    """
    store_task_results('AI_GENERATION', **context)

# 任务定义

# 1. 获取待执行的内容生成任务
get_task = PythonOperator(
    task_id='get_pending_generation_task',
    python_callable=get_pending_generation_task,
    dag=dag,
)

# 2. 提交内容生成任务执行请求
submit_generation_task = PythonOperator(
    task_id='submit_generation_task',
    python_callable=submit_task_via_api,
    dag=dag,
)

# 3. 轮询内容生成任务状态
poll_generation_status = PythonOperator(
    task_id='poll_generation_status',
    python_callable=poll_task_status,
    dag=dag,
)

# 4. 处理内容生成任务成功
handle_generation_success = PythonOperator(
    task_id='handle_generation_success',
    python_callable=handle_generation_success,
    dag=dag,
)

# 5. 处理内容生成任务失败
handle_generation_failure = PythonOperator(
    task_id='handle_generation_failure',
    python_callable=handle_generation_failure,
    dag=dag,
)

# 6. 存储内容生成结果
store_generation_results = PythonOperator(
    task_id='store_generation_results',
    python_callable=store_generation_results,
    dag=dag,
)

# 任务依赖关系
get_task >> submit_generation_task >> poll_generation_status
poll_generation_status >> [handle_generation_success, handle_generation_failure]
handle_generation_success >> store_generation_results