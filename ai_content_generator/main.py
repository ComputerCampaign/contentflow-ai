#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容生成模块主入口
支持模块化架构和多种生成模式
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已加载环境变量文件: {env_file}")
except ImportError:
    print("提示: 安装python-dotenv可以自动加载.env文件")
    print("运行: uv add python-dotenv")

# 导入新的模块化组件
from ai_content_generator.managers import ConfigManager, FileManager
from ai_content_generator.workflows import WorkflowOrchestrator
from ai_content_generator.utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=True)


class AIContentGeneratorCLI:
    """AI内容生成器命令行接口"""
    
    def __init__(self):
        """
        初始化CLI
        """
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        
        logger.info("AI内容生成器CLI初始化完成")
    

    
    def run_modular_mode(self, args):
        """
        运行模块化模式
        
        Args:
            args: 命令行参数
        """
        logger.info(f"运行模块化模式: {args.mode}")
        
        try:
            # 加载爬虫数据
            crawler_data = self.file_manager.load_crawler_data(args.task_dir)
            
            # 创建输出目录
            output_dir = os.path.join(args.task_dir, 'ai_content')
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建工作流编排器
            orchestrator = WorkflowOrchestrator(args.config_dir, output_dir)
            
            # 根据模式执行相应工作流
            if args.mode == 'content':
                result = orchestrator.execute_content_workflow(
                    crawler_data, output_dir, args.prompt_type
                )
            elif args.mode == 'video':
                result = orchestrator.execute_video_workflow(
                    crawler_data, output_dir
                )
            elif args.mode == 'full':
                result = orchestrator.execute_full_workflow(
                    crawler_data, output_dir, args.prompt_type
                )
            else:
                raise ValueError(f"不支持的模式: {args.mode}")
            
            # 添加task_id到结果中
            if hasattr(args, 'task_id') and args.task_id:
                result['task_id'] = args.task_id
                logger.info(f"任务ID已添加到结果中: {args.task_id}")
            
            # 保存最终结果到爬虫任务同目录下
            final_result_file = self.file_manager.save_generation_result(
                args.task_dir, result, 'final'
            )
            
            logger.info(f"最终结果已保存到爬虫任务目录: {final_result_file}")
            
            logger.info(f"模块化模式执行成功: {args.mode}")
            return True, result
                
        except Exception as e:
            logger.error(f"模块化模式执行失败: {e}")
            return False, {'error': str(e)}
    
    def run(self, args):
        """
        运行AI内容生成器
        
        Args:
            args: 命令行参数
        
        Returns:
            tuple: (是否成功, 结果)
        """
        try:
            # 运行模块化模式
            return self.run_modular_mode(args)
                
        except Exception as e:
            logger.error(f"运行失败: {e}")
            return False, {'error': str(e)}


def create_parser():
    """
    创建命令行参数解析器
    
    Returns:
        ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(
        description="AI内容生成器 - 支持多平台文案生成和图片转视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --mode content --task-dir /path/to/crawler/task --task-id 272de618-0f92-4bc2-9ed0-4823fa30dba0
  python main.py --mode video --task-dir /path/to/crawler/task --task-id 272de618-0f92-4bc2-9ed0-4823fa30dba0
  python main.py --mode full --task-dir /path/to/crawler/task --task-id 272de618-0f92-4bc2-9ed0-4823fa30dba0
  
  # 兼容传统模式的命令格式:
  uv run python -m ai_content_generator.main --mode content --task-dir earth-20250827-001 --task-id 272de618-0f92-4bc2-9ed0-4823fa30dba0
        """
    )
    
    # 模块化模式参数
    parser.add_argument(
        '--mode',
        choices=['content', 'video', 'full'],
        required=True,
        help='生成模式: content(仅文案), video(仅视频), full(文案+视频)'
    )
    parser.add_argument(
        '--task-dir',
        required=True,
        help='爬虫任务目录路径'
    )
    parser.add_argument(
        '--prompt-type',
        help='提示词类型，默认使用配置文件中的默认值'
    )
    parser.add_argument(
        '--config-dir',
        help='配置文件目录路径'
    )
    parser.add_argument(
        '--task-id',
        help='任务ID，用于标记生成的内容所属任务'
    )
    
    # 通用参数
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='AI Content Generator 2.0.0'
    )
    
    return parser


def main():
    """
    主函数
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    logger.info("=== AI内容生成器启动 ===")
    logger.info(f"命令行参数: {vars(args)}")
    
    try:
        # 创建CLI实例
        cli = AIContentGeneratorCLI()
        
        # 运行模块化模式
        success, result = cli.run(args)
        
        if success:
            logger.info("=== 执行成功 ===")
            if isinstance(result, dict):
                logger.info(f"结果摘要: {result.get('summary', '无摘要')}")
            sys.exit(0)
        else:
            logger.error("=== 执行失败 ===")
            if isinstance(result, dict) and 'error' in result:
                logger.error(f"错误信息: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"程序执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()