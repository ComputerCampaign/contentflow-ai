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