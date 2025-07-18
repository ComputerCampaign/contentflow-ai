#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证模块，用于管理用户认证和权限
"""

from ..models import User, UserGroup, UserXPathRule, db
from .jwt_handler import create_access_token, verify_token
from .permissions import login_required, group_required, check_xpath_limit

__all__ = [
    'User', 'UserGroup', 'UserXPathRule', 'db',
    'create_access_token', 'verify_token',
    'login_required', 'group_required', 'check_xpath_limit'
]