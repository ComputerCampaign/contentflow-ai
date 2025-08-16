# -*- coding: utf-8 -*-
"""
Airflow DAGs 工具函数模块
封装常用的API操作和任务处理函数，提高代码复用性
"""

import requests
import logging
import json
from typing import Dict, Any, Optional
from config.config import API_CONFIG, get_api_url, get_task_type_param, TASK_STATUS


class APIClient:
    """
    API客户端类，封装所有后端API调用
    """
    
    def __init__(self):
        self.config = API_CONFIG
        self.headers = self.config['headers'].copy()
        # 添加Airflow API Key认证
        self.headers['X-API-Key'] = 'airflow-secret-key'
        self.timeout = self.config['timeout']
        self.retry_count = self.config['retry_count']
        self.retry_delay = self.config['retry_delay']
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        
        Raises:
            requests.exceptions.RequestException: 请求失败时抛出异常
        """
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('timeout', self.timeout)
        
        # 打印请求信息用于调试
        params = kwargs.get('params')
        if params:
            import urllib.parse
            params_str = f"?{urllib.parse.urlencode(params)}"
        else:
            params_str = ""
        logging.info(f"[Airflow API调用] {method} {url}{params_str}")
        
        for attempt in range(self.retry_count + 1):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count:
                    logging.error(f"API请求失败 (尝试 {attempt + 1}/{self.retry_count + 1}): {str(e)}")
                    raise
                else:
                    logging.warning(f"API请求失败 (尝试 {attempt + 1}/{self.retry_count + 1}): {str(e)}，{self.retry_delay}秒后重试")
                    import time
                    time.sleep(self.retry_delay)
    
    def get_next_task(self, task_type: str) -> Optional[Dict[str, Any]]:
        """
        获取下一个待执行的任务
        
        Args:
            task_type: 任务类型 ('CRAWLER' 或 'AI_GENERATION')
        
        Returns:
            Dict: 任务数据，如果没有任务则返回None
        """
        try:
            if task_type == 'CRAWLER':
                url = get_api_url('tasks', 'get_next_crawler_task')
            elif task_type == 'AI_GENERATION':
                url = get_api_url('tasks', 'get_next_generation_task')
            else:
                raise ValueError(f"不支持的任务类型: {task_type}")
            
            params = {'type': get_task_type_param(task_type)}
            response = self._make_request('GET', url, params=params)
            
            data = response.json()
            if data and 'data' in data and data['data']:
                task = data['data']
                logging.info(f"获取到{task_type}任务: {task['id']}")
                return task
            else:
                logging.info(f"暂无{task_type}任务")
                return None
                
        except Exception as e:
            logging.error(f"获取{task_type}任务失败: {str(e)}")
            raise
    
    def get_task_command(self, task_id: int) -> Optional[str]:
        """
        获取任务执行命令
        
        Args:
            task_id: 任务ID
        
        Returns:
            str: 执行命令，如果获取失败则返回None
        """
        try:
            url = get_api_url('tasks', 'get_task_command', task_id=task_id)
            response = self._make_request('GET', url)
            
            command_data = response.json()
            if command_data.get('success') and 'data' in command_data and 'command' in command_data['data']:
                command = command_data['data']['command']
                logging.info(f"获取任务 {task_id} 执行命令: {command}")
                return command
            else:
                logging.error(f"任务 {task_id} 命令数据格式错误: {command_data}")
                return None
                
        except Exception as e:
            logging.error(f"获取任务 {task_id} 命令失败: {str(e)}")
            raise
    
    def update_task_status(self, task_id: int, status: str, result: Optional[str] = None, 
                          error_message: Optional[str] = None) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态
            result: 任务结果（可选）
            error_message: 错误信息（可选）
        
        Returns:
            bool: 更新是否成功
        """
        try:
            payload = {'status': status}
            
            if result:
                payload['result'] = result
            if error_message:
                payload['error_message'] = error_message
            
            url = get_api_url('tasks', 'update_task_status', task_id=task_id)
            response = self._make_request('PUT', url, json=payload)
            
            logging.info(f"任务 {task_id} 状态已更新为: {status}")
            return True
            
        except Exception as e:
            logging.error(f"更新任务 {task_id} 状态失败: {str(e)}")
            raise
    
    def execute_task(self, task_id: int) -> Dict[str, Any]:
        """
        执行指定任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            Dict: 执行结果
        
        Raises:
            requests.exceptions.RequestException: 请求失败时抛出异常
        """
        try:
            url = get_api_url('tasks', 'execute_task', task_id=task_id)
            response = self._make_request('POST', url)
            
            result = response.json()
            logging.info(f"任务 {task_id} 执行请求已发送")
            return result
            
        except Exception as e:
            logging.error(f"执行任务 {task_id} 失败: {str(e)}")
            raise
    
    def get_task_status(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            Dict: 任务状态信息，如果任务不存在返回None
        
        Raises:
            requests.exceptions.RequestException: 请求失败时抛出异常
        """
        try:
            url = get_api_url('tasks', 'get_task_detail', task_id=task_id)
            response = self._make_request('GET', url)
            
            result = response.json()
            if result.get('success'):
                return result.get('data')
            else:
                logging.warning(f"获取任务 {task_id} 状态失败: {result.get('message')}")
                return None
            
        except Exception as e:
            logging.error(f"获取任务 {task_id} 状态失败: {str(e)}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """
        检查后端服务健康状态
        
        Returns:
            Dict: 健康检查结果
        """
        try:
            url = get_api_url('monitoring', 'health_check')
            response = self._make_request('GET', url)
            
            health_data = response.json()
            logging.info("后端服务健康检查通过")
            return health_data
            
        except Exception as e:
            logging.error(f"后端服务健康检查失败: {str(e)}")
            raise


# 全局API客户端实例
api_client = APIClient()


def submit_task_via_api(**context) -> Dict[str, Any]:
    """
    通过API提交任务执行请求（不等待完成）
    
    Args:
        **context: Airflow上下文，包含task_instance等信息
    
    Returns:
        Dict: 提交结果
    """
    try:
        # 从XCom获取任务ID
        task_id = context['task_instance'].xcom_pull(key='task_id')
        
        if not task_id:
            # 如果XCom中没有task_id，尝试从crawler_task中获取
            crawler_task = context['task_instance'].xcom_pull(key='crawler_task')
            if crawler_task and 'id' in crawler_task:
                task_id = crawler_task['id']
            else:
                raise ValueError("无法获取任务ID")
        
        logging.info(f"🚀 [AIRFLOW] 开始提交任务执行请求 {task_id}")
        
        # 执行前检查任务状态
        logging.info(f"📋 [AIRFLOW] 检查任务 {task_id} 的当前状态...")
        pre_status = api_client.get_task_status(task_id)
        if pre_status:
            current_status = pre_status.get('status', '未知')
            task_name = pre_status.get('name', '未知任务')
            logging.info(f"📋 [AIRFLOW] 任务 {task_id} ({task_name}) 当前状态: {current_status}")
            
            # 如果任务已经在运行中，记录详细信息
            if current_status == 'running':
                started_at = pre_status.get('started_at')
                logging.warning(f"⚠️ [AIRFLOW] 任务 {task_id} 当前状态为 running，可能已在执行中")
                if started_at:
                    logging.warning(f"⚠️ [AIRFLOW] 任务开始时间: {started_at}")
        else:
            logging.warning(f"⚠️ [AIRFLOW] 无法获取任务 {task_id} 的执行前状态")
        
        # 调用API执行任务
        logging.info(f"🔄 [AIRFLOW] 发送执行请求到后端API...")
        result = api_client.execute_task(task_id)
        
        logging.info(f"✅ [AIRFLOW] 任务 {task_id} 执行请求成功发送")
        logging.info(f"📤 [AIRFLOW] API响应: {result}")
        
        # 执行后立即检查状态
        logging.info(f"📋 [AIRFLOW] 执行后立即检查任务状态...")
        post_status = api_client.get_task_status(task_id)
        if post_status:
            new_status = post_status.get('status', '未知')
            logging.info(f"📋 [AIRFLOW] 任务 {task_id} 执行后状态: {new_status}")
            if new_status != pre_status.get('status') if pre_status else None:
                logging.info(f"🔄 [AIRFLOW] 任务状态已从 {pre_status.get('status') if pre_status else '未知'} 变更为 {new_status}")
        
        # 将任务ID和提交结果存储到XCom
        context['task_instance'].xcom_push(key='submitted_task_id', value=task_id)
        context['task_instance'].xcom_push(key='submit_result', value=result)
        
        submit_result = {
            'success': True,
            'task_id': task_id,
            'message': '任务提交成功',
            'api_response': result
        }
        
        logging.info(f"✅ [AIRFLOW] 任务 {task_id} 提交完成")
        return submit_result
        
    except Exception as e:
        logging.error(f"💥 [AIRFLOW] 提交任务失败: {str(e)}")
        context['task_instance'].xcom_push(key='submit_result', value={'success': False, 'error': str(e)})
        raise


def poll_task_status(**context) -> Dict[str, Any]:
    """
    轮询检查任务执行状态直到完成
    
    Args:
        **context: Airflow上下文，包含task_instance等信息
    
    Returns:
        Dict: 执行结果
    """
    import time
    
    try:
        # 从XCom获取任务ID
        task_id = context['task_instance'].xcom_pull(key='submitted_task_id')
        
        if not task_id:
            # 尝试从其他可能的key获取
            task_id = context['task_instance'].xcom_pull(key='task_id')
            if not task_id:
                crawler_task = context['task_instance'].xcom_pull(key='crawler_task')
                if crawler_task and 'id' in crawler_task:
                    task_id = crawler_task['id']
                else:
                    raise ValueError("无法获取任务ID")
        
        logging.info(f"⏳ [AIRFLOW] 开始轮询任务 {task_id} 的执行状态...")
        
        # 轮询等待任务完成
        max_wait_time = 3600  # 最大等待时间1小时
        poll_interval = 10    # 轮询间隔10秒
        start_time = time.time()
        poll_count = 0
        
        logging.info(f"⏳ [AIRFLOW] 轮询配置: 最大等待时间 {max_wait_time}秒，轮询间隔 {poll_interval}秒")
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            elapsed_time = int(time.time() - start_time)
            
            logging.info(f"🔍 [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} - 已等待 {elapsed_time}秒，开始获取任务状态...")
            
            # 获取任务状态
            try:
                task_status = api_client.get_task_status(task_id)
            except Exception as e:
                logging.error(f"❌ [AIRFLOW] [轮询 #{poll_count}] 获取任务 {task_id} 状态时发生异常: {str(e)}")
                logging.info(f"⏳ [AIRFLOW] [轮询 #{poll_count}] 将在 {poll_interval} 秒后重试...")
                time.sleep(poll_interval)
                continue
            
            if not task_status:
                logging.error(f"❌ [AIRFLOW] [轮询 #{poll_count}] 无法获取任务 {task_id} 的状态信息")
                logging.info(f"⏳ [AIRFLOW] [轮询 #{poll_count}] 将在 {poll_interval} 秒后重试...")
                time.sleep(poll_interval)
                continue
            
            current_status = task_status.get('status')
            task_name = task_status.get('name', '未知任务')
            
            logging.info(f"📊 [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} ({task_name}) 当前状态: {current_status}")
            
            # 检查任务是否完成
            if current_status == 'completed':
                logging.info(f"✅ [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} 执行成功完成！")
                logging.info(f"⏱️ [AIRFLOW] [轮询 #{poll_count}] 总等待时间: {elapsed_time}秒，轮询次数: {poll_count}")
                
                final_result = {
                    'success': True,
                    'status': 'completed',
                    'task_id': task_id,
                    'task_data': task_status,
                    'message': '任务执行成功',
                    'elapsed_time': elapsed_time,
                    'poll_count': poll_count
                }
                break
            elif current_status == 'failed':
                error_message = task_status.get('error_message', '未知错误')
                logging.error(f"❌ [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} 执行失败！")
                logging.error(f"💥 [AIRFLOW] [轮询 #{poll_count}] 失败原因: {error_message}")
                logging.info(f"⏱️ [AIRFLOW] [轮询 #{poll_count}] 总等待时间: {elapsed_time}秒，轮询次数: {poll_count}")
                
                final_result = {
                    'success': False,
                    'status': 'failed',
                    'task_id': task_id,
                    'task_data': task_status,
                    'message': f'任务执行失败: {error_message}',
                    'elapsed_time': elapsed_time,
                    'poll_count': poll_count
                }
                break
            elif current_status in ['running', 'pending']:
                # 任务仍在执行中，继续等待
                remaining_time = max_wait_time - elapsed_time
                logging.info(f"⏳ [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} 仍在执行中 (状态: {current_status})")
                
                # 每5次轮询输出一次进度摘要
                if poll_count % 5 == 0:
                    logging.info(f"📊 [AIRFLOW] [进度摘要] 任务 {task_id} 已轮询 {poll_count} 次，累计等待 {elapsed_time}秒，状态: {current_status}")
                
                time.sleep(poll_interval)
                continue
            else:
                # 未知状态
                logging.warning(f"⚠️ [AIRFLOW] [轮询 #{poll_count}] 任务 {task_id} 状态未知: {current_status}")
                time.sleep(poll_interval)
                continue
        else:
            # 超时
            elapsed_time = int(time.time() - start_time)
            final_status = current_status if 'current_status' in locals() else '未知'
            logging.error(f"⏰ [AIRFLOW] 任务 {task_id} 执行超时！总等待时间: {elapsed_time}秒，轮询次数: {poll_count}")
            
            final_result = {
                'success': False,
                'status': 'timeout',
                'task_id': task_id,
                'message': f'任务等待超时，已等待 {elapsed_time}秒，轮询 {poll_count} 次',
                'elapsed_time': elapsed_time,
                'poll_count': poll_count
            }
        
        # 将执行结果存储到XCom
        context['task_instance'].xcom_push(key='execution_result', value=final_result)
        context['task_instance'].xcom_push(key='execution_status', value=final_result['status'])
        
        # 如果任务失败或超时，抛出异常让Airflow知道任务失败
        if not final_result['success']:
            error_msg = final_result['message']
            logging.error(f"💥 [AIRFLOW] 任务执行失败，准备抛出异常: {error_msg}")
            context['task_instance'].xcom_push(key='error_message', value=error_msg)
            raise Exception(error_msg)
        
        logging.info(f"✅ [AIRFLOW] 任务 {task_id} 轮询完成，最终结果: {final_result}")
        return final_result
        
    except Exception as e:
        logging.error(f"💥 [AIRFLOW] 轮询任务状态失败: {str(e)}")
        context['task_instance'].xcom_push(key='execution_result', value={'success': False, 'error': str(e)})
        context['task_instance'].xcom_push(key='execution_status', value='error')
        context['task_instance'].xcom_push(key='error_message', value=str(e))
        raise


def get_pending_task(task_type: str, **context) -> Optional[Dict[str, Any]]:
    """
    获取待执行任务的通用函数
    
    Args:
        task_type: 任务类型
        **context: Airflow上下文
    
    Returns:
        Dict: 任务数据
    """
    task = api_client.get_next_task(task_type)
    
    if task:
        # 将任务数据存储到XCom中供后续任务使用
        task_key = f'{task_type.lower()}_task'
        context['task_instance'].xcom_push(key=task_key, value=task)
        return task
    else:
        logging.info(f"没有找到{task_type}任务，跳过执行")
        return None


def generate_task_command(task_type: str, **context) -> Optional[str]:
    """
    生成任务执行命令的通用函数
    
    Args:
        task_type: 任务类型
        **context: Airflow上下文
    
    Returns:
        str: 执行命令
    """
    # 从XCom获取任务数据
    task_key = f'{task_type.lower()}_task'
    task = context['task_instance'].xcom_pull(key=task_key)
    
    if not task:
        logging.warning(f"未找到{task_type}任务数据，跳过命令生成")
        return None
    
    task_id = task['id']
    command = api_client.get_task_command(task_id)
    
    if command:
        # 将命令存储到XCom中供BashOperator使用
        command_key = f'{task_type.lower()}_command'
        context['task_instance'].xcom_push(key=command_key, value=command)
        return command
    else:
        return None


def handle_task_success(task_type: str, **context) -> None:
    """
    处理任务成功完成的通用函数
    
    Args:
        task_type: 任务类型
        **context: Airflow上下文
    """
    task_key = f'{task_type.lower()}_task'
    task = context['task_instance'].xcom_pull(key=task_key)
    
    if task:
        task_id = task['id']
        api_client.update_task_status(
            task_id, 
            TASK_STATUS['COMPLETED'], 
            result=f'{task_type}任务执行成功'
        )
        logging.info(f"{task_type}任务 {task_id} 执行成功")
    else:
        logging.warning(f"没有找到{task_type}任务信息，无法更新状态")


def handle_task_failure(task_type: str, **context) -> None:
    """
    处理任务执行失败的通用函数
    
    Args:
        task_type: 任务类型
        **context: Airflow上下文
    """
    task_key = f'{task_type.lower()}_task'
    task = context['task_instance'].xcom_pull(key=task_key)
    
    if task:
        task_id = task['id']
        
        # 获取失败原因
        error_message = f"{task_type}任务执行失败"
        try:
            # 尝试从上下文获取更详细的错误信息
            dag_run = context.get('dag_run')
            if dag_run:
                failed_task_instances = dag_run.get_task_instances(state='failed')
                if failed_task_instances:
                    # 获取第一个失败任务的错误信息
                    failed_ti = failed_task_instances[0]
                    if hasattr(failed_ti, 'log') and failed_ti.log:
                        error_message = f"任务失败: {str(failed_ti.log)[:500]}"  # 限制错误信息长度
        except Exception as e:
            logging.warning(f"获取详细错误信息失败: {str(e)}")
        
        api_client.update_task_status(
            task_id, 
            TASK_STATUS['FAILED'], 
            error_message=error_message
        )
        logging.error(f"{task_type}任务 {task_id} 执行失败: {error_message}")
    else:
        logging.warning(f"没有找到{task_type}任务信息，无法更新失败状态")


def store_task_results(task_type: str, **context) -> None:
    """
    存储任务结果的通用函数（占位函数）
    
    Args:
        task_type: 任务类型
        **context: Airflow上下文
    """
    task_key = f'{task_type.lower()}_task'
    task = context['task_instance'].xcom_pull(key=task_key)
    
    if task:
        task_id = task['id']
        logging.info(f"任务 {task_id} 的{task_type}结果已存储在本地文件中")
        # TODO: 实现具体的结果存储逻辑
        # 可能包括：
        # 1. 读取生成的结果文件
        # 2. 处理和格式化结果
        # 3. 存储到数据库或文件系统
        # 4. 生成质量报告
        # 5. 触发后续的处理流程
    else:
        logging.warning(f"没有找到{task_type}任务信息，跳过结果存储")


def check_system_health(**context) -> Dict[str, Any]:
    """
    系统健康检查函数
    
    Args:
        **context: Airflow上下文
    
    Returns:
        Dict: 健康检查结果
    """
    try:
        health_result = api_client.check_health()
        
        # 将健康检查结果存储到XCom
        context['task_instance'].xcom_push(key='health_check_result', value=health_result)
        
        return health_result
        
    except Exception as e:
        logging.error(f"系统健康检查失败: {str(e)}")
        # 健康检查失败时返回基本信息
        error_result = {
            'status': 'error',
            'message': str(e),
            'timestamp': context['ts']
        }
        context['task_instance'].xcom_push(key='health_check_result', value=error_result)
        return error_result