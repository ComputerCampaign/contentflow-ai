#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫任务DAG
处理后端配置的爬虫任务，通过API接口获取任务并执行
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import requests
import json
import logging
from config import API_CONFIG, get_api_url, get_task_type_param, TASK_STATUS, DAG_CONFIG
from utils import (get_pending_task, generate_task_command, handle_task_success, 
                   handle_task_failure, store_task_results)

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
    'crawler_task_pipeline',
    default_args=default_args,
    description='爬虫任务处理流水线',
    schedule_interval=timedelta(minutes=60),  # 每30分钟执行一次
    catchup=False,
    tags=['crawler', 'pipeline'],
)

# 从配置文件获取API配置
api_config = API_CONFIG
api_headers = api_config['headers']
api_timeout = api_config['timeout']
api_retry_count = api_config['retry_count']
api_retry_delay = api_config['retry_delay']

def get_pending_crawler_task(**context):
    """
    获取待执行的爬虫任务
    """
    return get_pending_task('CRAWLER', **context)

def generate_crawler_command(**context):
    """
    生成爬虫执行命令
    """
    return generate_task_command('CRAWLER', **context)

# 任务状态更新功能已移至utils模块中的APIClient类

def handle_crawler_success(**context):
    """
    处理爬虫任务成功完成
    """
    handle_task_success('CRAWLER', **context)

def handle_crawler_failure(**context):
    """
    处理爬虫任务执行失败
    """
    handle_task_failure('CRAWLER', **context)

def store_crawler_results(**context):
    """
    存储爬虫结果
    """
    store_task_results('CRAWLER', **context)

# 任务定义

# 1. 获取待执行的爬虫任务
get_task = PythonOperator(
    task_id='get_pending_crawler_task',
    python_callable=get_pending_crawler_task,
    dag=dag,
)

# 2. 生成爬虫执行命令
generate_command = PythonOperator(
    task_id='generate_crawler_command',
    python_callable=generate_crawler_command,
    dag=dag,
)

# 3. 执行爬虫任务
execute_crawler = BashOperator(
    task_id='execute_crawler_task',
    bash_command="{{ task_instance.xcom_pull(key='crawler_command') or 'echo \"没有找到爬虫命令，跳过执行\"' }}",
    dag=dag,
)

# 4. 处理成功情况
handle_success = PythonOperator(
    task_id='handle_crawler_success',
    python_callable=handle_crawler_success,
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# 5. 存储爬虫结果（占位）
store_results = PythonOperator(
    task_id='store_crawler_results',
    python_callable=store_crawler_results,
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# 6. 处理失败情况
handle_failure = PythonOperator(
    task_id='handle_crawler_failure',
    python_callable=handle_crawler_failure,
    trigger_rule='one_failed',
    dag=dag,
)

# 任务依赖关系
get_task >> generate_command >> execute_crawler
execute_crawler >> [handle_success, handle_failure]
handle_success >> store_results