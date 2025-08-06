# -*- coding: utf-8 -*-
"""
示例爬虫DAG

这个DAG展示了如何在Airflow中集成爬虫平台的功能，包括：
1. 数据爬取任务
2. 数据处理任务
3. 博客生成任务
4. 数据清理任务
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import logging

# 默认参数
default_args = {
    'owner': 'crawler-platform',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# 创建DAG
dag = DAG(
    'example_crawler_workflow',
    default_args=default_args,
    description='示例爬虫工作流',
    schedule_interval='@daily',  # 每天执行一次
    max_active_runs=1,
    tags=['crawler', 'example', 'daily'],
)

# Python函数定义
def check_crawler_status(**context):
    """
    检查爬虫服务状态
    """
    logging.info("检查爬虫服务状态...")
    
    # 这里可以添加实际的健康检查逻辑
    # 例如：检查数据库连接、检查API服务等
    
    try:
        # 模拟健康检查
        import requests
        import os
        
        # 获取后端API地址
        backend_url = Variable.get("BACKEND_API_URL", default_var="http://localhost:5000")
        
        # 检查API健康状态
        response = requests.get(f"{backend_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            logging.info("爬虫服务状态正常")
            return True
        else:
            logging.error(f"爬虫服务状态异常: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"健康检查失败: {str(e)}")
        return False

def run_crawler_task(**context):
    """
    执行爬虫任务
    """
    logging.info("开始执行爬虫任务...")
    
    # 获取任务参数
    task_config = context.get('params', {})
    target_url = task_config.get('target_url', 'https://example.com')
    
    logging.info(f"爬取目标: {target_url}")
    
    # 这里可以调用实际的爬虫逻辑
    # 例如：导入爬虫模块并执行
    
    try:
        # 模拟爬虫执行
        import time
        import random
        
        # 模拟爬取时间
        crawl_time = random.randint(10, 30)
        logging.info(f"预计爬取时间: {crawl_time}秒")
        
        time.sleep(crawl_time)
        
        # 模拟爬取结果
        result = {
            'status': 'success',
            'url': target_url,
            'items_count': random.randint(50, 200),
            'duration': crawl_time
        }
        
        logging.info(f"爬取完成: {result}")
        
        # 将结果存储到XCom中，供下游任务使用
        return result
        
    except Exception as e:
        logging.error(f"爬虫任务执行失败: {str(e)}")
        raise

def process_crawled_data(**context):
    """
    处理爬取的数据
    """
    logging.info("开始处理爬取的数据...")
    
    # 从上游任务获取数据
    crawler_result = context['task_instance'].xcom_pull(task_ids='run_crawler')
    
    if not crawler_result:
        logging.error("未获取到爬虫数据")
        raise ValueError("未获取到爬虫数据")
    
    logging.info(f"处理数据: {crawler_result}")
    
    try:
        # 模拟数据处理逻辑
        processed_count = crawler_result.get('items_count', 0)
        
        # 数据清洗、转换等处理
        processed_result = {
            'original_count': processed_count,
            'processed_count': int(processed_count * 0.8),  # 模拟处理后的数据量
            'processing_time': 15,
            'status': 'processed'
        }
        
        logging.info(f"数据处理完成: {processed_result}")
        return processed_result
        
    except Exception as e:
        logging.error(f"数据处理失败: {str(e)}")
        raise

def generate_blog_content(**context):
    """
    生成博客内容
    """
    logging.info("开始生成博客内容...")
    
    # 从上游任务获取处理后的数据
    processed_data = context['task_instance'].xcom_pull(task_ids='process_data')
    
    if not processed_data:
        logging.error("未获取到处理后的数据")
        raise ValueError("未获取到处理后的数据")
    
    logging.info(f"基于数据生成博客: {processed_data}")
    
    try:
        # 模拟博客生成逻辑
        blog_result = {
            'title': f"数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
            'content_length': 2500,
            'images_count': 5,
            'generation_time': 20,
            'status': 'generated'
        }
        
        logging.info(f"博客生成完成: {blog_result}")
        return blog_result
        
    except Exception as e:
        logging.error(f"博客生成失败: {str(e)}")
        raise

def cleanup_temp_files(**context):
    """
    清理临时文件
    """
    logging.info("开始清理临时文件...")
    
    try:
        # 模拟清理逻辑
        import os
        import glob
        
        # 清理临时目录
        temp_patterns = [
            '/tmp/crawler_*',
            '/tmp/airflow_*',
        ]
        
        cleaned_files = 0
        for pattern in temp_patterns:
            files = glob.glob(pattern)
            for file in files:
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                        cleaned_files += 1
                except Exception as e:
                    logging.warning(f"清理文件失败 {file}: {str(e)}")
        
        logging.info(f"清理完成，删除了 {cleaned_files} 个临时文件")
        return {'cleaned_files': cleaned_files}
        
    except Exception as e:
        logging.error(f"清理任务失败: {str(e)}")
        # 清理任务失败不应该影响整个工作流
        return {'cleaned_files': 0, 'error': str(e)}

# 任务定义

# 开始任务
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# 健康检查任务
health_check = PythonOperator(
    task_id='health_check',
    python_callable=check_crawler_status,
    dag=dag,
)

# 爬虫任务
crawler_task = PythonOperator(
    task_id='run_crawler',
    python_callable=run_crawler_task,
    params={
        'target_url': 'https://example.com',
        'max_pages': 10,
    },
    dag=dag,
)

# 数据处理任务
process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_crawled_data,
    dag=dag,
)

# 博客生成任务
blog_task = PythonOperator(
    task_id='generate_blog',
    python_callable=generate_blog_content,
    dag=dag,
)

# 系统状态检查任务
system_check = BashOperator(
    task_id='system_check',
    bash_command='''
    echo "检查系统资源使用情况..."
    df -h
    free -m
    echo "系统检查完成"
    ''',
    dag=dag,
)

# 清理任务
cleanup_task = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_temp_files,
    trigger_rule='all_done',  # 无论上游任务成功或失败都执行
    dag=dag,
)

# 结束任务
end_task = DummyOperator(
    task_id='end',
    trigger_rule='all_done',
    dag=dag,
)

# 定义任务依赖关系
start_task >> health_check >> crawler_task >> process_task >> blog_task
start_task >> system_check
[blog_task, system_check] >> cleanup_task >> end_task

# 任务组示例（可选）
from airflow.utils.task_group import TaskGroup

with TaskGroup("data_pipeline", dag=dag) as data_pipeline:
    extract = DummyOperator(task_id="extract", dag=dag)
    transform = DummyOperator(task_id="transform", dag=dag)
    load = DummyOperator(task_id="load", dag=dag)
    
    extract >> transform >> load

# 如果需要，可以将任务组集成到主工作流中
# start_task >> data_pipeline >> end_task