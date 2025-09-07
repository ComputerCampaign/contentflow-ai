from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule

from utils.utils import (
    get_pending_task, handle_task_success, handle_task_failure,
    submit_task_via_api, poll_task_status, api_client
)
from config.config import DAG_CONFIG, TASK_TYPES
import logging

# DAG默认参数
default_args = DAG_CONFIG['default_args'].copy()
default_args.update({
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
})

# 创建DAG - 优化后的简化版本
dag = DAG(
    'crawler_task_pipeline_optimized',
    default_args=default_args,
    description='优化后的爬虫任务处理流水线 - 简化流程，集成结果上传',
    schedule_interval=timedelta(minutes=20),  # 缩短调度间隔
    catchup=False,
    tags=['crawler', 'pipeline', 'optimized'],
)

def process_crawler_task(**context):
    """
    优化后的爬虫任务处理函数 - 集成获取、执行、轮询和结果处理
    """
    try:
        logging.info("🚀 [OPTIMIZED] 开始处理爬虫任务...")
        
        # 1. 获取待执行任务
        logging.info("📋 [OPTIMIZED] 获取待执行的爬虫任务...")
        task = api_client.get_next_task(TASK_TYPES['CRAWLER'].upper())
        
        if not task:
            logging.info("📭 [OPTIMIZED] 没有待执行的爬虫任务，跳过本次调度")
            return {'success': True, 'message': '没有待执行任务', 'task_processed': False}
        
        task_id = task['id']
        task_name = task.get('name', '未知任务')
        logging.info(f"📋 [OPTIMIZED] 找到待执行任务: {task_id} ({task_name})")
        
        # 存储任务信息到XCom
        context['task_instance'].xcom_push(key='crawler_task', value=task)
        context['task_instance'].xcom_push(key='task_id', value=task_id)
        
        # 2. 提交任务执行
        logging.info(f"🔄 [OPTIMIZED] 提交任务 {task_id} 执行请求...")
        submit_result = api_client.execute_task(task_id)
        logging.info(f"✅ [OPTIMIZED] 任务 {task_id} 提交成功: {submit_result}")
        
        # 3. 轮询任务状态（简化版本）
        import time
        max_wait_time = 1800  # 最大等待30分钟
        poll_interval = 15    # 轮询间隔15秒
        start_time = time.time()
        
        logging.info(f"⏳ [OPTIMIZED] 开始轮询任务 {task_id} 状态...")
        
        while time.time() - start_time < max_wait_time:
            task_status = api_client.get_task_status(task_id)
            
            if not task_status:
                logging.warning(f"⚠️ [OPTIMIZED] 无法获取任务 {task_id} 状态，继续等待...")
                time.sleep(poll_interval)
                continue
            
            current_status = task_status.get('status')
            elapsed_time = int(time.time() - start_time)
            
            if current_status == 'completed':
                logging.info(f"✅ [OPTIMIZED] 任务 {task_id} 执行成功！耗时: {elapsed_time}秒")
                
                # 4. 处理成功结果
                try:
                    # 更新任务状态为已完成
                    api_client.update_task_status(task_id, 'completed', result='任务执行成功')
                    logging.info(f"📊 [OPTIMIZED] 任务 {task_id} 状态已更新为完成")
                    
                    # 注意：爬虫结果上传由爬虫服务自动完成，无需在DAG中处理
                    logging.info(f"📤 [OPTIMIZED] 爬虫结果将由爬虫服务自动上传到后端")
                    
                except Exception as e:
                    logging.error(f"❌ [OPTIMIZED] 处理任务成功结果时出错: {str(e)}")
                
                return {
                    'success': True,
                    'task_id': task_id,
                    'status': 'completed',
                    'message': '任务执行成功',
                    'elapsed_time': elapsed_time,
                    'task_processed': True
                }
                
            elif current_status == 'failed':
                error_message = task_status.get('error_message', '未知错误')
                logging.error(f"❌ [OPTIMIZED] 任务 {task_id} 执行失败: {error_message}")
                
                # 处理失败结果
                try:
                    api_client.update_task_status(task_id, 'failed', error_message=error_message)
                    logging.info(f"📊 [OPTIMIZED] 任务 {task_id} 状态已更新为失败")
                except Exception as e:
                    logging.error(f"❌ [OPTIMIZED] 更新失败状态时出错: {str(e)}")
                
                return {
                    'success': False,
                    'task_id': task_id,
                    'status': 'failed',
                    'message': f'任务执行失败: {error_message}',
                    'elapsed_time': elapsed_time,
                    'task_processed': True
                }
                
            elif current_status in ['running', 'pending']:
                # 每分钟输出一次进度
                if elapsed_time % 60 == 0 and elapsed_time > 0:
                    logging.info(f"⏳ [OPTIMIZED] 任务 {task_id} 仍在执行中，已等待 {elapsed_time}秒")
                time.sleep(poll_interval)
                continue
            else:
                logging.warning(f"⚠️ [OPTIMIZED] 任务 {task_id} 状态未知: {current_status}")
                time.sleep(poll_interval)
                continue
        
        # 超时处理
        elapsed_time = int(time.time() - start_time)
        logging.error(f"⏰ [OPTIMIZED] 任务 {task_id} 执行超时，已等待 {elapsed_time}秒")
        
        try:
            api_client.update_task_status(task_id, 'failed', error_message=f'任务执行超时，已等待 {elapsed_time}秒')
        except Exception as e:
            logging.error(f"❌ [OPTIMIZED] 更新超时状态时出错: {str(e)}")
        
        return {
            'success': False,
            'task_id': task_id,
            'status': 'timeout',
            'message': f'任务执行超时，已等待 {elapsed_time}秒',
            'elapsed_time': elapsed_time,
            'task_processed': True
        }
        
    except Exception as e:
        logging.error(f"💥 [OPTIMIZED] 处理爬虫任务时发生异常: {str(e)}")
        return {
            'success': False,
            'status': 'error',
            'message': f'处理任务时发生异常: {str(e)}',
            'task_processed': False
        }

# 优化后的单一任务处理节点
process_crawler_tasks = PythonOperator(
    task_id='process_crawler_tasks',
    python_callable=process_crawler_task,
    dag=dag,
)

# 任务完成标记
task_complete = DummyOperator(
    task_id='task_complete',
    dag=dag,
)

# 简化的任务依赖关系
process_crawler_tasks >> task_complete