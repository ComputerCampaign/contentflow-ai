#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
博客生成模块日志配置
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name, level=logging.INFO, file_path=None):
    """设置日志记录器
    
    Args:
        name (str): 日志记录器名称
        level (int): 日志级别
        file_path (str): 文件路径，用于生成日志文件名
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if file_path:
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        log_file = os.path.join(log_dir, f'blog_generator_{module_name}.log')
        
        # 创建文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
default_logger = setup_logger('blog_generator')