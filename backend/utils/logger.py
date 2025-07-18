#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块，用于统一管理项目的日志配置
"""

import os
import sys
import logging
from datetime import datetime

# 日志目录
LOG_DIR = 'logs'

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 获取当前日期作为日志文件名的一部分
date_str = datetime.now().strftime('%Y-%m-%d')

def setup_logger(name=None, log_file=None, level=logging.INFO, file_path=None):
    """
    设置日志记录器
    
    Args:
        name (str, optional): 日志记录器名称，如果为None，则使用file_path
        log_file (str, optional): 日志文件路径，如果为None，则使用默认路径
        level (int, optional): 日志级别，默认为INFO
        file_path (str, optional): 文件路径，用于替代name，如果name为None或__main__，则使用此参数
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 如果未提供name，则使用file_path
    if name is None and file_path is not None:
        name = file_path
    
    # 处理模块名称
    if name == "__main__" or name is None:
        # 如果提供了file_path，使用它
        if file_path is not None:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
        else:
            # 否则使用调用脚本的文件名
            module_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    else:
        # 保留完整的包名，只在日志文件名中使用最后一部分
        module_name = name.split('.')[-1]
    
    # 如果未指定日志文件，则使用模块名称作为日志文件名
    if log_file is None:
        log_file = os.path.join(LOG_DIR, f"{module_name}_{date_str}.log")
    
    # 创建日志记录器
    # 如果是主程序或者使用了file_path，使用模块名称作为logger名称
    if name == "__main__" or (name is None and file_path is not None):
        logger_name = module_name
    else:
        # 直接使用传入的名称
        logger_name = name
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # 移除所有现有的处理器
    for handler in logger.handlers[:]:  # 使用切片创建副本，避免在迭代时修改列表
        logger.removeHandler(handler)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None, log_file=None, level=logging.INFO, file_path=None):
    """
    获取日志记录器，是setup_logger的便捷封装
    
    Args:
        name (str, optional): 日志记录器名称
        log_file (str, optional): 日志文件路径
        level (int, optional): 日志级别
        file_path (str, optional): 文件路径
        
    Returns:
        logging.Logger: 日志记录器
    """
    return setup_logger(name, log_file, level, file_path)