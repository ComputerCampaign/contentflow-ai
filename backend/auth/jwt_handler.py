#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JWT令牌处理模块
"""

from datetime import datetime, timedelta
import jwt
import os
import sys
# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import config

# 从配置中获取JWT相关设置，如果不存在则使用默认值
JWT_SECRET = config.get('auth', 'jwt_secret', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = config.get('auth', 'jwt_algorithm', 'HS256')
JWT_EXPIRATION = config.get('auth', 'jwt_expiration', 3600)  # 默认1小时

def create_access_token(data: dict):
    """
    创建访问令牌
    
    Args:
        data (dict): 要编码到令牌中的数据
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    """
    验证令牌
    
    Args:
        token (str): JWT令牌
        
    Returns:
        dict: 解码后的令牌数据，如果验证失败则返回None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None