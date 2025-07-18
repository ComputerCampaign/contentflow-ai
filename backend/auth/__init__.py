#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证模块，用于管理用户认证和权限
"""

import os
import sys
# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.models import User, UserGroup, UserXPathRule, db
from backend.auth.jwt_handler import create_access_token, verify_token
from backend.auth.permissions import login_required, group_required, check_xpath_limit

__all__ = [
    'User', 'UserGroup', 'UserXPathRule', 'db',
    'create_access_token', 'verify_token',
    'login_required', 'group_required', 'check_xpath_limit'
]