#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
import requests
from typing import Optional
from pathlib import Path

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 查找.env文件
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已加载环境变量文件: {env_file}")
except ImportError:
    print("提示: 安装python-dotenv可以自动加载.env文件")
    print("运行: uv add python-dotenv")

# 导入自定义模块
from ai_content_generator.generator import AIContentGenerator
from ai_content_generator.config import AIConfig
from ai_content_generator.utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

def _update_task_status_via_api(task_id, status, result=None, error_message=None):
    """调用后端接口更新任务状态
    
    Args:
        task_id (str): 任务ID
        status (str): 任务状态 ('success', 'failed')
        result (str, optional): 任务结果
        error_message (str, optional): 错误信息
    """
    try:
        # 从环境变量或配置文件获取后端API地址
        api_base_url = os.getenv('BACKEND_API_URL', 'http://localhost:5002/api/v1')
        url = f"{api_base_url}/tasks/{task_id}/status-airflow"
        
        payload = {'status': status}
        if result:
            payload['result'] = result
        if error_message:
            payload['error_message'] = error_message
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': os.getenv('AIRFLOW_API_KEY', 'airflow-secret-key')
        }
        
        logger.info(f"🌐 [AI_CONTENT_GENERATOR] 调用后端接口更新任务状态")
        logger.info(f"   - URL: {url}")
        logger.info(f"   - Payload: {payload}")
        logger.info(f"   - API Key: {headers['X-API-Key'][:10]}...")
        
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ [AI_CONTENT_GENERATOR] 任务 {task_id} 状态已成功更新为: {status}")
            try:
                response_data = response.json()
                logger.info(f"   - 后端响应: {response_data}")
            except:
                logger.info(f"   - 后端响应: {response.text}")
        else:
            logger.error(f"❌ [AI_CONTENT_GENERATOR] 更新任务状态失败: HTTP {response.status_code}")
            logger.error(f"   - 响应内容: {response.text}")
            
    except Exception as e:
        logger.error(f"💥 [AI_CONTENT_GENERATOR] 调用后端接口更新任务状态失败: {str(e)}")
        # 不抛出异常，避免影响内容生成主流程

class ContentGenerator:
    """AI内容生成器包装类，用于命令行调用"""
    
    def __init__(self, config_path: Optional[str] = None, base_path: str = "crawler_data"):
        """初始化内容生成器
        
        Args:
            config_path (str, optional): 配置文件路径
            base_path (str): 爬虫数据基础路径
        """
        # 加载配置
        if config_path and os.path.exists(config_path):
            config = AIConfig.from_file(config_path)
        else:
            config = AIConfig()
        
        # 初始化AI内容生成器
        self.generator = AIContentGenerator(config=config, base_path=base_path)
        
        logger.info(f"AI内容生成器初始化完成，数据路径: {base_path}")
    
    def generate_content(self, task_id: str, custom_prompt: Optional[str] = None) -> tuple:
        """生成内容
        
        Args:
            task_id (str): 任务ID
            custom_prompt (str, optional): 自定义提示词
            
        Returns:
            tuple: (是否成功, 生成的内容)
        """
        try:
            content = self.generator.generate_from_crawler_data(task_id, custom_prompt)
            if content:
                return True, content
            else:
                return False, None
        except Exception as e:
            logger.error(f"内容生成失败: {str(e)}")
            return False, None

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="AI内容生成器")
    parser.add_argument("--task-id", required=True, help="内容生成任务ID")
    parser.add_argument("--crawler-task-id", required=True, help="源爬虫任务ID")
    parser.add_argument("--ai-config-id", help="AI内容配置ID")
    parser.add_argument("--custom-prompt", help="自定义提示词")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--base-path", default="crawler_data", help="爬虫数据基础路径")
    
    args = parser.parse_args()
    
    # 检查必要参数
    if not args.task_id:
        logger.error("未提供内容生成任务ID，请使用--task-id参数指定任务ID")
        parser.print_help()
        sys.exit(1)
    
    if not args.crawler_task_id:
        logger.error("未提供源爬虫任务ID，请使用--crawler-task-id参数指定爬虫任务ID")
        parser.print_help()
        sys.exit(1)
    
    # 创建内容生成器实例
    try:
        generator = ContentGenerator(
            config_path=args.config,
            base_path=args.base_path
        )
    except Exception as e:
        logger.error(f"初始化内容生成器失败: {str(e)}")
        if args.task_id:
            _update_task_status_via_api(args.task_id, 'failed', None, f"初始化失败: {str(e)}")
        sys.exit(1)
    
    try:
        # 开始生成内容
        logger.info(f"🎯 [AI_CONTENT_GENERATOR] 开始生成内容，内容生成任务ID: {args.task_id}, 源爬虫任务ID: {args.crawler_task_id}")
        if args.ai_config_id:
            logger.info(f"🎯 [AI_CONTENT_GENERATOR] 使用AI配置ID: {args.ai_config_id}")
        success, content = generator.generate_content(args.crawler_task_id, args.custom_prompt)
        
        # 打印生成结果信息
        logger.info(f"🎯 [AI_CONTENT_GENERATOR] 生成结果 - 成功: {success}, 内容长度: {len(content) if content else 0}")
        
        # 调用后端接口更新任务状态
        logger.info(f"📡 [AI_CONTENT_GENERATOR] 准备调用后端接口更新任务状态，内容生成任务ID: {args.task_id}")
        _update_task_status_via_api(
            args.task_id, 
            'completed' if success else 'failed', 
            content if success else None,
            None if success else "内容生成失败"
        )
        
        if not success:
            sys.exit(1)
            
        logger.info(f"内容生成完成，任务ID: {args.task_id}")
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        _update_task_status_via_api(args.task_id, 'failed', None, '用户中断')
    except Exception as e:
        logger.exception(f"内容生成过程中发生错误: {str(e)}")
        _update_task_status_via_api(args.task_id, 'failed', None, str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()