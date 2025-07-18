#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据模型模块
"""

from .base import db
from .user import User
from .user_group import UserGroup
from .user_xpath_rule import UserXPathRule

__all__ = ['db', 'User', 'UserGroup', 'UserXPathRule']