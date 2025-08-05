#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据模型模块
"""

from backend.models.base import db
from backend.models.user import User
from backend.models.user_group import UserGroup
from backend.models.user_xpath_rule import UserXPathRule

__all__ = ['db', 'User', 'UserGroup', 'UserXPathRule']