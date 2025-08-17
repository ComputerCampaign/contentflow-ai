#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一响应格式工具
"""

from flask import jsonify
from typing import Any, Dict, Optional


def success_response(data: Any = None, message: str = "操作成功", status_code: int = 200) -> tuple:
    """
    成功响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        tuple: (响应JSON, 状态码)
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code


def error_response(message: str = "操作失败", status_code: int = 400, error_code: Optional[str] = None, data: Any = None) -> tuple:
    """
    错误响应格式
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 错误代码
        data: 额外的错误数据
        
    Returns:
        tuple: (响应JSON, 状态码)
    """
    response = {
        'success': False,
        'message': message
    }
    
    if error_code:
        response['error_code'] = error_code
        
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code


def paginated_response(items: list, pagination: Dict, message: str = "获取成功") -> tuple:
    """
    分页响应格式
    
    Args:
        items: 数据列表
        pagination: 分页信息
        message: 响应消息
        
    Returns:
        tuple: (响应JSON, 状态码)
    """
    return success_response({
        'items': items,
        'pagination': pagination
    }, message)