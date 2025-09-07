#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流编排器模块
统一管理文案生成和视频生成的完整工作流程
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from ..generators.multi_platform_generator import MultiPlatformGenerator
from ..generators.video_generator import VideoGenerator
from ..managers.config_manager import ConfigManager
from ..managers.file_manager import FileManager
from ..utils.logger import setup_logger


class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化工作流编排器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config = ConfigManager(config_dir)
        self.content_generator = MultiPlatformGenerator(config_dir)
        self.video_generator = VideoGenerator(config_dir)
        self.file_manager = FileManager()
        self.logger = setup_logger(__name__, file_path=True)
        
        self.logger.info("工作流编排器初始化完成")
    
    def execute_content_workflow(self, crawler_data: Dict[str, Any], 
                               output_dir: str,
                               custom_prompt: str = None) -> Dict[str, Any]:
        """
        执行内容生成工作流
        
        Args:
            crawler_data: 爬虫数据
            output_dir: 输出目录
            custom_prompt: 自定义提示词类型
        
        Returns:
            内容生成结果
        """
        workflow_id = f"content_{int(time.time())}"
        
        try:
            self.logger.info(f"开始执行内容生成工作流 [workflow_id={workflow_id}]")
            self.logger.debug(f"输入数据: {json.dumps(crawler_data, ensure_ascii=False, indent=2)}")
            self.logger.debug(f"自定义提示词类型: {custom_prompt}")
            self.logger.debug(f"输出目录: {output_dir}")
            
            # 验证输入数据
            self.logger.info(f"验证输入数据 [workflow_id={workflow_id}]")
            if not self.validate_crawler_data(crawler_data):
                raise ValueError("输入数据验证失败")
            self.logger.info(f"输入数据验证通过 [workflow_id={workflow_id}]")
            
            # 生成多平台内容
            self.logger.info(f"开始生成多平台内容 [workflow_id={workflow_id}]")
            content_result = self.content_generator.generate_multi_platform_content(
                crawler_data, custom_prompt
            )
            self.logger.info(f"多平台内容生成完成 [workflow_id={workflow_id}]")
            self.logger.debug(f"生成结果: {json.dumps(content_result, ensure_ascii=False, indent=2)}")
            
            # 验证内容
            if not self.content_generator.validate_content(content_result):
                raise ValueError("生成的内容验证失败")
            
            # 使用file_manager保存文案结果
            self.logger.info(f"保存文案结果 [workflow_id={workflow_id}]")
            self.file_manager.save_generation_result(output_dir, content_result, 'text')
            
            # 构建返回结果
            result = {
                'workflow_type': 'content_only',
                'workflow_id': workflow_id,
                'status': 'success',
                'content_result': content_result,
                'output_files': {
                    'content': os.path.join(output_dir, 'text_generation_result.json')
                },
                'execution_time': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'summary': {
                    'platforms_generated': len(content_result.get('platforms', {})),
                    'total_content_items': self._count_content_items(content_result)
                }
            }
            
            self.logger.info(f"内容生成工作流执行完成 [workflow_id={workflow_id}]")
            return result
            
        except Exception as e:
            self.logger.error(f"内容生成工作流执行失败 [workflow_id={workflow_id}]: {e}")
            raise
    
    def execute_video_workflow(self, crawler_data: Dict[str, Any] = None, 
                              output_dir: str = None, content_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行视频生成工作流
        
        Args:
            crawler_data: 爬虫数据（已弃用，保留兼容性）
            output_dir: 输出目录
            content_result: 内容生成结果（可选，如果不提供则从文案文件加载）
        
        Returns:
            视频生成结果
        """
        workflow_id = f"video_{int(time.time())}"
        
        try:
            self.logger.info(f"开始执行视频生成工作流 [workflow_id={workflow_id}]")
            
            # 如果没有提供内容结果，从文案文件加载
            if content_result is None:
                self.logger.info(f"从文案文件加载内容结果 [workflow_id={workflow_id}]")
                content_result = self.file_manager.load_text_generation_result(output_dir)
                if not content_result:
                    raise FileNotFoundError(f"找不到文案生成结果文件: {os.path.join(output_dir, 'text_generation_result.json')}")
            
            # 从文案结果中提取图片URL和video_prompt
            images = content_result.get('images', [])
            self.logger.info(f"从文案结果中提取到图片数量: {len(images)} [workflow_id={workflow_id}]")
            
            # 记录图片URL详情
            for i, img_url in enumerate(images[:3]):  # 只记录前3个
                self.logger.debug(f"图片URL {i+1}: {img_url} [workflow_id={workflow_id}]")
            
            if not images:
                self.logger.warning(f"文案结果中没有找到图片URL，跳过视频生成 [workflow_id={workflow_id}]")
                return {
                    'workflow_type': 'video',
                    'workflow_id': workflow_id,
                    'status': 'skipped',
                    'message': '文案结果中没有可用图片URL，跳过视频生成',
                    'execution_time': time.strftime('%Y-%m-%dT%H:%M:%SZ')
                }
            
            # 视频直接保存到输出目录（与JSON文件同级）
            video_output_dir = output_dir
            os.makedirs(video_output_dir, exist_ok=True)
            self.logger.debug(f"视频输出目录: {video_output_dir}")
            
            # 生成视频
            self.logger.info(f"调用视频生成器 [workflow_id={workflow_id}]")
            video_result = self.video_generator.generate_videos_from_content(
                content_result, images, video_output_dir
            )
            self.logger.info(f"视频生成完成，成功: {video_result.get('success_count', 0)}, 失败: {video_result.get('failed_count', 0)} [workflow_id={workflow_id}]")
            
            # 使用file_manager保存视频结果
            self.logger.info(f"保存视频结果 [workflow_id={workflow_id}]")
            self.file_manager.save_generation_result(output_dir, video_result, 'video')
            
            # 构建返回结果
            result = {
                'workflow_type': 'video',
                'workflow_id': workflow_id,
                'status': 'success',
                'video_result': video_result,
                'output_file': os.path.join(output_dir, 'video_generation_result.json'),
                'execution_time': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'summary': {
                    'total_videos': video_result.get('total_videos', 0),
                    'successful_videos': video_result.get('success_count', 0),
                    'failed_videos': video_result.get('failed_count', 0)
                }
            }
            
            self.logger.info(f"视频生成工作流执行完成 [workflow_id={workflow_id}]")
            return result
            
        except Exception as e:
            self.logger.error(f"视频生成工作流执行失败 [workflow_id={workflow_id}]: {e}")
            raise
    
    def execute_full_workflow(self, crawler_data: Dict[str, Any], 
                            output_dir: str,
                            custom_prompt: str = None) -> Dict[str, Any]:
        """
        执行完整工作流（内容生成 + 视频生成）
        
        Args:
            crawler_data: 爬虫数据
            output_dir: 输出目录
            custom_prompt: 自定义提示词类型
        
        Returns:
            完整工作流结果
        """
        workflow_id = f"full_{int(time.time())}"
        
        try:
            self.logger.info(f"开始执行完整工作流 [workflow_id={workflow_id}]")
            self.logger.debug(f"输入数据: {json.dumps(crawler_data, ensure_ascii=False, indent=2)}")
            self.logger.debug(f"自定义提示词类型: {custom_prompt}")
            self.logger.debug(f"输出目录: {output_dir}")
            
            # 第一步：生成多平台内容
            self.logger.info(f"步骤1: 生成多平台内容 [workflow_id={workflow_id}]")
            content_result = self.content_generator.generate_multi_platform_content(
                crawler_data, custom_prompt
            )
            self.logger.info(f"内容生成完成，生成了 {len(content_result.get('platforms', {}))} 个平台的内容 [workflow_id={workflow_id}]")
            
            # 验证内容
            if not self.content_generator.validate_content(content_result):
                raise ValueError("生成的内容验证失败")
            
            # 保存内容结果到输出目录
            content_file = os.path.join(output_dir, 'multi_platform_content.json')
            self.logger.info(f"保存内容结果到: {content_file} [workflow_id={workflow_id}]")
            self._save_json_result(content_result, content_file)
            
            # 第二步：生成视频
            self.logger.info(f"步骤2: 生成视频 [workflow_id={workflow_id}]")
            
            # 获取图片列表
            images = crawler_data.get('images', [])
            self.logger.info(f"检查视频生成条件，可用图片数量: {len(images)} [workflow_id={workflow_id}]")
            video_result = None
            video_file = None
            
            if images:
                self.logger.info(f"开始视频生成流程 [workflow_id={workflow_id}]")
                # 视频直接保存到输出目录（与JSON文件同级）
                video_output_dir = output_dir
                os.makedirs(video_output_dir, exist_ok=True)
                self.logger.debug(f"视频输出目录: {video_output_dir}")
                
                # 生成视频
                self.logger.info(f"调用视频生成器 [workflow_id={workflow_id}]")
                video_result = self.video_generator.generate_videos_from_content(
                    content_result, images, video_output_dir
                )
                self.logger.info(f"视频生成完成，成功: {video_result.get('success_count', 0)}, 失败: {video_result.get('failed_count', 0)} [workflow_id={workflow_id}]")
                
                # 保存视频结果
                video_file = os.path.join(output_dir, 'video_generation_result.json')
                self.logger.info(f"保存视频结果到: {video_file} [workflow_id={workflow_id}]")
                self._save_json_result(video_result, video_file)
            else:
                self.logger.warning(f"没有找到图片，跳过视频生成 [workflow_id={workflow_id}]")
                video_result = {
                    'generation_id': f"video_{int(time.time())}",
                    'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'platforms': {},
                    'total_videos': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'message': '没有可用图片，跳过视频生成'
                }
            
            # 构建完整结果
            result = {
                'workflow_type': 'full',
                'workflow_id': workflow_id,
                'status': 'success',
                'content_result': content_result,
                'video_result': video_result,
                'output_files': {
                    'content': content_file,
                    'videos': video_file
                },
                'execution_time': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'summary': {
                    'platforms_generated': len(content_result.get('platforms', {})),
                    'total_content_items': self._count_content_items(content_result),
                    'total_videos': video_result.get('total_videos', 0) if video_result else 0,
                    'successful_videos': video_result.get('success_count', 0) if video_result else 0,
                    'failed_videos': video_result.get('failed_count', 0) if video_result else 0
                }
            }
            
            self.logger.info(f"完整工作流执行完成 [workflow_id={workflow_id}]")
            return result
            
        except Exception as e:
            self.logger.error(f"完整工作流执行失败 [workflow_id={workflow_id}]: {e}")
            raise
    
    def execute_workflow(self, mode: str, crawler_data: Dict[str, Any], 
                        output_dir: str, custom_prompt: str = None) -> Dict[str, Any]:
        """
        根据模式执行相应的工作流
        
        Args:
            mode: 执行模式 ('content', 'video', 'full')
            crawler_data: 爬虫数据
            output_dir: 输出目录
            custom_prompt: 自定义提示词类型
        
        Returns:
            工作流执行结果
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        if mode == 'content':
            return self.execute_content_workflow(crawler_data, output_dir, custom_prompt)
        elif mode == 'video':
            return self.execute_video_workflow(crawler_data, output_dir)
        elif mode == 'full':
            return self.execute_full_workflow(crawler_data, output_dir, custom_prompt)
        else:
            raise ValueError(f"不支持的工作流模式: {mode}")
    
    def _save_json_result(self, data: Dict[str, Any], file_path: str):
        """
        保存JSON结果到文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"结果已保存到: {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            raise
    
    def _count_content_items(self, content_result: Dict[str, Any]) -> int:
        """
        统计内容项数量
        
        Args:
            content_result: 内容生成结果
        
        Returns:
            内容项总数
        """
        count = 0
        platforms = content_result.get('platforms', {})
        
        for platform_content in platforms.values():
            # 统计标题、内容、标签等
            if platform_content.get('title'):
                count += 1
            if platform_content.get('content'):
                count += 1
            if platform_content.get('hashtags'):
                count += len(platform_content['hashtags'])
            if platform_content.get('video_prompt'):
                count += 1
        
        return count
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        获取工作流状态（用于异步执行）
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            工作流状态信息
        """
        # 这里可以实现工作流状态跟踪逻辑
        # 目前返回基本状态信息
        return {
            'workflow_id': workflow_id,
            'status': 'unknown',
            'message': '工作流状态跟踪功能待实现'
        }
    
    def validate_crawler_data(self, crawler_data: Dict[str, Any]) -> bool:
        """
        验证爬虫数据的完整性
        
        Args:
            crawler_data: 爬虫数据
        
        Returns:
            验证结果
        """
        try:
            # 检查必要字段
            required_fields = ['title']
            for field in required_fields:
                if field not in crawler_data or not crawler_data[field]:
                    self.logger.error(f"缺少必要字段: {field}")
                    return False
            
            # 检查数据类型
            if not isinstance(crawler_data.get('title'), str):
                self.logger.error("标题必须是字符串类型")
                return False
            
            # 检查可选字段的类型
            if 'comments' in crawler_data and not isinstance(crawler_data['comments'], list):
                self.logger.error("评论必须是列表类型")
                return False
            
            if 'images' in crawler_data and not isinstance(crawler_data['images'], list):
                self.logger.error("图片必须是列表类型")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return False
    
    def create_workflow_summary(self, result: Dict[str, Any]) -> str:
        """
        创建工作流执行摘要
        
        Args:
            result: 工作流执行结果
        
        Returns:
            执行摘要文本
        """
        try:
            workflow_type = result.get('workflow_type', 'unknown')
            summary = result.get('summary', {})
            
            summary_text = f"工作流类型: {workflow_type}\n"
            summary_text += f"执行状态: {result.get('status', 'unknown')}\n"
            summary_text += f"执行时间: {result.get('execution_time', 'unknown')}\n"
            
            if 'platforms_generated' in summary:
                summary_text += f"生成平台数: {summary['platforms_generated']}\n"
            
            if 'total_content_items' in summary:
                summary_text += f"内容项总数: {summary['total_content_items']}\n"
            
            if 'total_videos' in summary:
                summary_text += f"视频总数: {summary['total_videos']}\n"
                summary_text += f"成功视频: {summary.get('successful_videos', 0)}\n"
                summary_text += f"失败视频: {summary.get('failed_videos', 0)}\n"
            
            output_files = result.get('output_files', {})
            if output_files:
                summary_text += "\n输出文件:\n"
                for file_type, file_path in output_files.items():
                    if file_path:
                        summary_text += f"  {file_type}: {file_path}\n"
            
            return summary_text
            
        except Exception as e:
            self.logger.error(f"创建摘要失败: {e}")
            return f"摘要生成失败: {e}"


if __name__ == "__main__":
    # 测试代码
    import tempfile
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        orchestrator = WorkflowOrchestrator()
        
        # 测试数据
        test_data = {
            'title': '提高工作效率的10个技巧',
            'description': '分享实用的工作效率提升方法',
            'url': 'https://example.com/efficiency-tips',
            'comments': [
                {'content': '很实用的建议'},
                {'content': '时间管理很重要'},
                {'content': '希望有更多案例'}
            ],
            'images': ['https://example.com/image1.jpg']
        }
        
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 测试内容生成工作流
            print("\n测试内容生成工作流...")
            content_result = orchestrator.execute_workflow(
                'content', test_data, temp_dir
            )
            
            print("内容生成结果摘要:")
            print(orchestrator.create_workflow_summary(content_result))
            
    except Exception as e:
        print(f"测试失败: {e}")