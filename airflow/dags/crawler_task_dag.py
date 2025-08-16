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
    'crawler_task_pipeline',
    default_args=default_args,
    description='爬虫任务处理流水线',
    schedule_interval=timedelta(minutes=600),  # 每30分钟执行一次
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

# 2. 提交爬虫任务执行请求
submit_crawler_task = PythonOperator(
    task_id='submit_crawler_task',
    python_callable=submit_task_via_api,
    dag=dag,
)

# 3. 轮询检查任务执行状态
poll_crawler_status = PythonOperator(
    task_id='poll_crawler_status',
    python_callable=poll_task_status,
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
get_task >> submit_crawler_task >> poll_crawler_status
poll_crawler_status >> [handle_success, handle_failure]
handle_success >> store_results