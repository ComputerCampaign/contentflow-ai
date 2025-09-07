#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频生成模块
实现图片转视频功能，支持任务状态轮询和结果下载
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional

import requests

from ..utils.logger import setup_logger
from ..managers.config_manager import ConfigManager
from ..managers.prompt_manager import PromptManager


class VideoGenerator:
    """
    视频生成器
    负责根据图片和文本提示生成视频内容
    使用豆包视频生成API
    """
    
    def __init__(self, config_dir: str = None, ai_content_dir: str = None):
        self.logger = setup_logger(__name__, file_path=True)
        self.config_manager = ConfigManager(config_dir)
        self.prompt_manager = PromptManager(config_dir)
        
        # 设置AI内容目录
        self.ai_content_dir = ai_content_dir or 'output'
        
        # 获取视频生成模型配置
        video_model_config = self.config_manager.get_video_model_config()
        
        # 获取配置
        self.api_key = self.config_manager.get_api_key('doubao_video')
        self.model_name = video_model_config.get('model', 'doubao-seedance-1-0-lite-i2v-250428')
        
        # 获取重试配置
        self.max_retries = video_model_config.get('max_retries', 3)
        
        # 获取轮询配置
        self.poll_interval = video_model_config.get('poll_interval', 5)
        self.max_poll_time = video_model_config.get('max_poll_time', 300)
        
        # API端点 - 使用配置中的base_url
        self.base_url = video_model_config.get('base_url', 'https://ark.cn-beijing.volces.com')
        self.create_task_url = self.base_url + '/api/v3/contents/generations/tasks'
        
        # HTTP请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        self.logger.info("VideoGenerator 初始化完成")
        self.logger.debug(f"使用模型: {self.model_name}")
        self.logger.debug(f"API端点: {self.create_task_url}")
        self.logger.debug(f"最大重试次数: {self.max_retries}")
        self.logger.debug(f"轮询间隔: {self.poll_interval}s")
        self.logger.debug(f"最大轮询时间: {self.max_poll_time}s")
    

    
    def generate_video_from_image(self, image_url: str, prompt: str, 
                                 output_path: str = None, task_id: str = None, generation_id: str = None) -> Dict[str, Any]:
        """
        从图片生成视频
        
        Args:
            image_url: 输入图片URL
            prompt: 视频生成提示词
            output_path: 输出文件路径（可选）
            task_id: 任务ID（用于日志上下文）
            generation_id: 生成ID（用于日志上下文）
        
        Returns:
            生成结果字典
        """
        try:
            # 构建日志上下文
            log_context = f"[task_id={task_id or 'unknown'}][generation_id={generation_id or 'unknown'}]"
            
            self.logger.info(f"{log_context} 开始生成视频，图片: {image_url}")
            self.logger.info(f"{log_context} 视频生成提示词: {prompt}")
            
            # 提交视频生成任务
            video_task_id = self._submit_video_task(image_url, prompt, log_context)
            
            # 轮询任务状态
            result = self._poll_task_status(video_task_id, log_context)
            
            # 下载视频文件（如果指定了输出路径）
            if output_path and result.get('video_url'):
                local_path = self._download_video(result['video_url'], output_path)
                result['local_path'] = local_path
            
            self.logger.info(f"{log_context} 视频生成完成，任务ID: {video_task_id}")
            self.logger.info(f"{log_context} 视频生成结果: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"{log_context} 视频生成失败: {e}")
            raise
    
    def generate_videos_from_text_result(self, text_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从文案生成结果生成视频
        
        Args:
            text_result: 文案生成结果数据，包含多平台内容和图片URL
        
        Returns:
            视频生成结果列表
        """
        results = []
        
        try:
            # 从文案结果中提取内容数据和图片URL
            content_data = text_result.get('content', {})
            image_urls = text_result.get('images', [])
            
            # 从内容数据中提取video_prompt
            video_prompt = None
            
            # 尝试从不同平台的内容中提取video_prompt
            for platform, platform_content in content_data.items():
                if isinstance(platform_content, dict) and 'video_prompt' in platform_content:
                    video_prompt = platform_content['video_prompt']
                    break
            
            if not video_prompt:
                self.logger.warning("未找到video_prompt，使用默认提示词")
                video_prompt = "生成一个有趣的视频"
            
            # 使用第一张图片生成视频
            if image_urls:
                image_url = image_urls[0]
                self.logger.info(f"使用图片 {image_url} 生成视频")
                
                result = self.generate_video_from_image(image_url, video_prompt)
                
                # 如果生成成功且有视频URL，下载视频
                if result.get('status') == 'completed' and result.get('video_url'):
                    video_url = result['video_url']
                    
                    # 生成本地文件名
                    import os
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"video_{timestamp}.mp4"
                    
                    # 设置下载路径（假设有ai_content_dir属性）
                    if hasattr(self, 'ai_content_dir'):
                        output_path = os.path.join(self.ai_content_dir, 'videos', filename)
                    else:
                        output_path = os.path.join('output', 'videos', filename)
                    
                    # 下载视频
                    try:
                        local_path = self._download_video(video_url, output_path)
                        result['local_video_path'] = local_path
                        self.logger.info(f"视频已下载到: {local_path}")
                    except Exception as e:
                        self.logger.error(f"视频下载失败: {e}")
                        result['download_error'] = str(e)
                
                results.append(result)
            else:
                self.logger.warning("没有可用的图片URL")
            
            return results
            
        except Exception as e:
            self.logger.error(f"从文案结果生成视频失败: {e}")
            raise
    
    def generate_videos_from_content(self, platform_content: Dict[str, Any], 
                                   images: List[str], 
                                   output_dir: str = None) -> Dict[str, Any]:
        """
        根据多平台内容生成视频（优化版：自动加载video_prompt，只生成一个视频）
        
        Args:
            platform_content: 多平台内容字典
            images: 图片URL列表
            output_dir: 输出目录
        
        Returns:
            视频生成结果
        """
        results = {
            'generation_id': f"video_{int(time.time())}",
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'video_result': None,
            'total_videos': 0,
            'success_count': 0,
            'failed_count': 0
        }
        
        try:            
            # 直接从根级别获取统一的video_prompt
            best_video_prompt = platform_content.get('video_prompt', '').strip()
            
            if not best_video_prompt:
                self.logger.warning("未找到可用的video_prompt，使用默认提示词")
                best_video_prompt = "生成一个吸引人的短视频，展示内容的核心要点"
            
            # 选择第一张图片生成视频（只生成一个视频）
            if not images:
                raise ValueError("没有可用的图片生成视频")
            
            selected_image = images[0]
            self.logger.info(f"使用图片生成视频: {selected_image}")
            self.logger.info(f"使用video_prompt: {best_video_prompt[:100]}...")
            
            try:
                # 生成输出路径
                output_path = None
                if output_dir:
                    import os
                    filename = f"ai_generated_video_{int(time.time())}.mp4"
                    output_path = os.path.join(output_dir, filename)
                
                # 生成视频
                video_result = self.generate_video_from_image(
                    selected_image, best_video_prompt, output_path
                )
                
                # 如果生成成功且有视频URL，自动下载视频到JSON结果同级目录
                local_video_path = None
                if video_result.get('status') == 'completed' and video_result.get('video_url'):
                    try:
                        video_url = video_result['video_url']
                        
                        # 生成本地文件名（使用时间戳）
                        import os
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"video_{timestamp}.mp4"
                        
                        # 设置下载路径到JSON结果的同级目录
                        if output_dir:
                            # 视频文件保存到output_dir（与JSON结果同级）
                            local_video_path = os.path.join(output_dir, filename)
                        else:
                            # 如果没有output_dir，使用ai_content_dir或默认输出目录
                            if hasattr(self, 'ai_content_dir') and self.ai_content_dir:
                                local_video_path = os.path.join(self.ai_content_dir, filename)
                            else:
                                # 使用默认输出目录，确保不会保存到根目录
                                default_output_dir = os.path.join(os.getcwd(), 'output')
                                os.makedirs(default_output_dir, exist_ok=True)
                                local_video_path = os.path.join(default_output_dir, filename)
                        
                        self.logger.info(f"开始下载视频到: {local_video_path}")
                        downloaded_path = self._download_video(video_url, local_video_path)
                        
                        # 更新结果中的本地路径信息
                        video_result['local_video_path'] = downloaded_path
                        video_result['video_filename'] = filename
                        
                        self.logger.info(f"视频下载成功: {downloaded_path}")
                        
                    except Exception as e:
                        self.logger.error(f"视频下载失败: {e}")
                        video_result['download_error'] = str(e)
                
                results['video_result'] = {
                    'image_url': selected_image,
                    'video_prompt': best_video_prompt,
                    'video_result': video_result,
                    'local_video_path': local_video_path,
                    'status': 'success'
                }
                
                results['success_count'] = 1
                results['total_videos'] = 1
                
                self.logger.info("视频生成成功")
                
            except Exception as e:
                self.logger.error(f"视频生成失败: {e}")
                results['video_result'] = {
                    'image_url': selected_image,
                    'video_prompt': best_video_prompt,
                    'error': str(e),
                    'status': 'failed'
                }
                results['failed_count'] = 1
                results['total_videos'] = 1
            
            self.logger.info(f"视频生成完成，成功: {results['success_count']}, 失败: {results['failed_count']}")
            return results
            
        except Exception as e:
            self.logger.error(f"视频生成失败: {e}")
            raise
    
    def _submit_video_task(self, image_url: str, prompt: str, log_context: str = "") -> str:
        """
        提交视频生成任务
        
        Args:
            image_url: 图片URL
            prompt: 文本提示
            log_context: 日志上下文
        
        Returns:
            任务ID
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"{log_context} 正在提交视频生成任务 (尝试 {attempt + 1}/{self.max_retries})")
                
                # 构建请求体
                request_data = {
                    "model": self.model_name,
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
                
                self.logger.info(f"{log_context} 【视频生成最终Prompt】")
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} 图片URL: {image_url}")
                self.logger.info(f"{log_context} 文本提示: {prompt}")
                self.logger.info(f"{log_context} 提示词字符数: {len(prompt)} 字符")
                self.logger.info(f"{log_context} --- 完整请求参数 ---")
                self.logger.info(f"{log_context} {json.dumps(request_data, ensure_ascii=False, indent=2)}")
                self.logger.info(f"{log_context} {'='*80}")
                
                # 打印完整HTTP请求信息（包括密钥）
                self.logger.info(f"{log_context} 【完整HTTP请求信息】")
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} 请求URL: {self.create_task_url}")
                self.logger.info(f"{log_context} 请求方法: POST")
                self.logger.info(f"{log_context} --- 完整请求头（含密钥） ---")
                for header_key, header_value in self.headers.items():
                    self.logger.info(f"{log_context} {header_key}: {header_value}")
                self.logger.info(f"{log_context} --- 完整请求体 ---")
                self.logger.info(f"{log_context} {json.dumps(request_data, ensure_ascii=False, indent=2)}")
                self.logger.info(f"{log_context} {'='*80}")
                
                # 发送HTTP POST请求
                response = requests.post(
                    self.create_task_url,
                    headers=self.headers,
                    json=request_data,
                    timeout=60
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析响应
                response_data = response.json()
                
                self.logger.info(f"{log_context} 【视频生成API返回结果】")
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} HTTP状态码: {response.status_code}")
                self.logger.info(f"{log_context} 响应内容长度: {len(response.text)} 字符")
                self.logger.info(f"{log_context} --- 完整API响应内容 ---")
                self.logger.info(f"{log_context} {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                self.logger.info(f"{log_context} {'='*80}")
                
                # 提取任务ID
                task_id = self._extract_task_id(response_data)
                
                self.logger.info(f"{log_context} 视频生成任务提交成功，任务ID: {task_id}")
                return task_id
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"{log_context} HTTP请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"{log_context} 所有重试均失败，最终错误: {e}")
                    raise
                time.sleep(2 ** attempt)
            except Exception as e:
                self.logger.warning(f"{log_context} 提交视频任务失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"{log_context} 所有重试均失败，最终错误: {e}")
                    raise
                time.sleep(2 ** attempt)
    
    def _extract_task_id(self, response_data: Dict[str, Any]) -> str:
        """
        从API响应中提取任务ID
        
        Args:
            response_data: API响应的JSON数据
        
        Returns:
            任务ID
        """
        try:
            # 根据豆包视频生成API的响应格式提取任务ID
            # 常见的字段名：id, task_id, taskId
            task_id = (
                response_data.get('id') or 
                response_data.get('task_id') or 
                response_data.get('taskId') or
                response_data.get('data', {}).get('id') or
                response_data.get('data', {}).get('task_id')
            )
            
            if task_id:
                return str(task_id)
            
            # 如果没有找到标准字段，记录响应结构并抛出错误
            self.logger.error(f"无法从响应中找到任务ID，响应结构: {response_data}")
            raise ValueError(f"API响应中未找到任务ID字段，响应: {response_data}")
            
        except Exception as e:
            self.logger.error(f"提取任务ID失败: {e}")
            raise ValueError(f"无法从API响应中提取任务ID: {e}")
    
    def _poll_task_status(self, task_id: str, log_context: str = "") -> Dict[str, Any]:
        """
        轮询任务状态
        
        Args:
            task_id: 任务ID
            log_context: 日志上下文
        
        Returns:
            任务结果
        """
        start_time = time.time()
        poll_count = 0
        
        self.logger.info(f"{log_context} 开始轮询任务状态，任务ID: {task_id}")
        
        while time.time() - start_time < self.max_poll_time:
            try:
                poll_count += 1
                elapsed_time = time.time() - start_time
                
                self.logger.debug(f"{log_context} 第 {poll_count} 次轮询，已耗时 {elapsed_time:.1f}s")
                
                # 查询任务状态
                status_result = self._query_task_status(task_id, log_context)
                
                status = status_result.get('status', '').lower()
                
                if status == 'completed' or status == 'success':
                    self.logger.info(f"{log_context} 任务 {task_id} 完成，总耗时 {elapsed_time:.1f}s")
                    self.logger.debug(f"{log_context} 任务完成结果: {status_result}")
                    return status_result
                elif status == 'failed' or status == 'error':
                    error_msg = status_result.get('error', '未知错误')
                    self.logger.error(f"{log_context} 任务 {task_id} 失败: {error_msg}")
                    raise Exception(f"任务失败: {error_msg}")
                elif status == 'processing' or status == 'running':
                    self.logger.info(f"{log_context} 任务 {task_id} 处理中... (第 {poll_count} 次检查)")
                else:
                    self.logger.info(f"{log_context} 任务 {task_id} 状态: {status} (第 {poll_count} 次检查)")
                
                # 等待下次轮询
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"{log_context} 查询任务状态失败 (第 {poll_count} 次): {e}")
                raise
        
        self.logger.error(f"{log_context} 任务 {task_id} 超时，超过最大等待时间 {self.max_poll_time} 秒")
        raise TimeoutError(f"任务 {task_id} 超时，超过最大等待时间 {self.max_poll_time} 秒")
    
    def _query_task_status(self, task_id: str, log_context: str = "") -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            log_context: 日志上下文
        
        Returns:
            状态信息
        """
        try:
            # 构建查询URL
            query_url = f"{self.base_url}/api/v3/contents/generations/tasks/{task_id}"
            
            self.logger.debug(f"{log_context} 查询任务状态，URL: {query_url}")
            
            # 发送HTTP GET请求
            response = requests.get(
                query_url,
                headers=self.headers,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 打印完整HTTP响应信息（与请求日志格式保持一致）
            self.logger.info(f"{log_context} 【任务状态查询响应结果】")
            self.logger.info(f"{log_context} {'='*80}")
            self.logger.info(f"{log_context} HTTP状态码: {response.status_code}")
            self.logger.info(f"{log_context} --- 完整响应头 ---")
            for header_key, header_value in response.headers.items():
                self.logger.info(f"{log_context} {header_key}: {header_value}")
            self.logger.info(f"{log_context} --- 完整响应体 ---")
            self.logger.info(f"{log_context} {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            self.logger.info(f"{log_context} {'='*80}")
            
            self.logger.debug(f"{log_context} 状态查询响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 标准化状态信息
            status_info = self._normalize_status_response(response_data, task_id)
            
            self.logger.debug(f"{log_context} 标准化后的状态: {status_info}")
            return status_info
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{log_context} HTTP请求失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"{log_context} 查询任务状态失败: {e}")
            raise
    
    def _normalize_status_response(self, response_data: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        标准化状态响应
        
        Args:
            response_data: API响应数据
            task_id: 任务ID
        
        Returns:
            标准化的状态信息
        """
        # 提取状态信息
        status = (
            response_data.get('status') or 
            response_data.get('state') or
            response_data.get('data', {}).get('status') or
            response_data.get('data', {}).get('state') or
            'unknown'
        ).lower()
        
        # 标准化状态值
        if status in ['completed', 'success', 'finished', 'done', 'succeeded']:
            # 提取视频URL
            video_url = (
                response_data.get('video_url') or
                response_data.get('url') or
                response_data.get('result_url') or
                response_data.get('content', {}).get('video_url') or
                response_data.get('content', {}).get('url') or
                response_data.get('data', {}).get('video_url') or
                response_data.get('data', {}).get('url') or
                response_data.get('data', {}).get('result_url')
            )
            
            return {
                'status': 'completed',
                'video_url': video_url,
                'task_id': task_id,
                'raw_response': response_data
            }
        elif status in ['failed', 'error', 'cancelled']:
            error_msg = (
                response_data.get('error') or
                response_data.get('error_message') or
                response_data.get('message') or
                response_data.get('data', {}).get('error') or
                '任务失败'
            )
            
            return {
                'status': 'failed',
                'error': error_msg,
                'task_id': task_id,
                'raw_response': response_data
            }
        else:
            # 处理中状态
            return {
                'status': 'processing',
                'task_id': task_id,
                'raw_response': response_data
            }
    
    def _download_video(self, video_url: str, output_path: str) -> str:
        """
        下载视频文件
        
        Args:
            video_url: 视频URL
            output_path: 输出路径
        
        Returns:
            本地文件路径
        """
        try:
            import os
            
            self.logger.info(f"开始下载视频文件")
            self.logger.info(f"视频URL: {video_url}")
            self.logger.info(f"保存路径: {output_path}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                self.logger.debug(f"创建输出目录: {output_dir}")
            
            # 下载文件
            self.logger.info("正在发送下载请求...")
            response = requests.get(video_url, timeout=300, stream=True)
            response.raise_for_status()
            
            # 获取文件大小信息
            content_length = response.headers.get('content-length')
            if content_length:
                file_size = int(content_length)
                self.logger.info(f"视频文件大小: {file_size / (1024*1024):.2f} MB")
            
            # 写入文件
            self.logger.info("开始写入本地文件...")
            downloaded_size = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            self.logger.info(f"视频下载完成: {output_path}")
            self.logger.info(f"下载文件大小: {downloaded_size / (1024*1024):.2f} MB")
            
            # 验证文件是否存在且大小合理
            if os.path.exists(output_path):
                actual_size = os.path.getsize(output_path)
                self.logger.info(f"本地文件大小验证: {actual_size / (1024*1024):.2f} MB")
                if actual_size < 1024:  # 小于1KB可能是错误文件
                    self.logger.warning(f"下载的文件大小异常小: {actual_size} bytes")
            
            return output_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP请求失败: {e}")
            self.logger.error(f"请求URL: {video_url}")
            raise
        except IOError as e:
            self.logger.error(f"文件写入失败: {e}")
            self.logger.error(f"目标路径: {output_path}")
            raise
        except Exception as e:
            self.logger.error(f"视频下载失败: {e}")
            self.logger.error(f"视频URL: {video_url}")
            self.logger.error(f"输出路径: {output_path}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态（公共接口）
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务状态信息
        """
        return self._query_task_status(task_id)


if __name__ == "__main__":
    # 测试代码
    import os
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        generator = VideoGenerator()
        
        # 测试数据
        test_image_url = "https://ark-project.tos-cn-beijing.volces.com/doc_image/see_i2v.jpeg"
        test_prompt = "天空的云飘动着，路上的车辆行驶"
        
        print("开始生成视频...")
        result = generator.generate_video_from_image(test_image_url, test_prompt)
        
        print("\n生成结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"测试失败: {e}")