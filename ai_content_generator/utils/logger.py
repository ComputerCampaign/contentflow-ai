#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI内容生成模块日志配置
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(name: str, 
                 level: int = logging.INFO,
                 file_path: Optional[str] = None,
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        file_path: 文件路径，用于确定日志文件位置
        max_bytes: 日志文件最大大小
        backup_count: 备份文件数量
        
    Returns:
        配置好的日志记录器
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
        # 确定日志文件路径
        if os.path.isfile(file_path):
            # 如果传入的是文件路径，使用其目录
            log_dir = os.path.dirname(file_path)
        else:
            # 如果传入的是目录路径，直接使用
            log_dir = file_path
        
        # 确保日志目录存在
        if not log_dir:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件路径
        log_file = os.path.join(log_dir, 'ai_content_generator.log')
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger