#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫模块日志配置
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

def setup_logger(name: str, level: int = logging.INFO, file_path: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        file_path: 文件路径（用于确定日志文件位置）
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 清除现有的处理器，重新配置
    logger.handlers.clear()
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if file_path:
        # 确定日志目录
        if os.path.isfile(file_path):
            # 从 crawler/crawler/xxx.py 向上一级到 crawler/ 目录，然后添加 logs
            log_dir = os.path.join(os.path.dirname(file_path), '..', 'logs')
        else:
            log_dir = os.path.join(os.getcwd(), 'logs')
        
        log_dir = os.path.abspath(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件名
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'crawler_{today}.log')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return logging.getLogger(name)