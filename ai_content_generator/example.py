#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Generator Example

This example demonstrates basic usage of the AI content generator.
"""

import os
import sys
from pathlib import Path
from ai_content_generator import AIContentGenerator, AIConfig

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


def main(task_id="task_1754985287"):
    """基本功能测试
    
    Args:
        task_id: 任务ID
    """
    
    print("=== AI内容生成基本测试 ===")
    print(f"测试数据: {task_id}")
    
    # 1. 基本用法测试
    generator = AIContentGenerator()
    
    # 从爬虫数据生成内容
    print("正在生成内容...")
    content = generator.generate_from_crawler_data(task_id)
    
    if content:
        print("✅ 内容生成成功")
        print(f"内容预览:\n{content}\n")
    else:
        print("❌ 内容生成失败\n")
    
    # 2. 配置信息
    config = AIConfig()
    print(f"当前模型: {config.get_current_model()}")
    print(f"默认提示词: {config.get_default_prompt_type()}")
    
    print("\n测试完成！")


if __name__ == "__main__":
    # 解析命令行参数
    task_id = "task_1754992451"  # 默认任务ID
    
    if len(sys.argv) >= 2:
        task_id = sys.argv[1]
    
    # 检查环境变量（根据当前模型配置）
    config = AIConfig()
    model_config = config._get_current_model_config()
    api_key_env = model_config.get("api_key_env", "ARK_API_KEY")
    
    if not os.getenv(api_key_env):
        print(f"警告: 未设置 {api_key_env} 环境变量")
        print(f"当前模型 '{config.get_current_model()}' 需要设置 {api_key_env} 环境变量")
        print(f"请在 .env 文件中设置 {api_key_env}=your_api_key")
        exit(1)

    try:
        main(task_id)
    except Exception as e:
        print(f"运行示例时出错: {e}")