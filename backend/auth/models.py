#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户和权限模型 - 兼容性导入

注意：此文件保留用于向后兼容，新代码请使用 backend.models 模块
"""

# 从新的模型模块导入
from ..models import db, User, UserGroup, UserXPathRule

# 保持向后兼容
__all__ = ['db', 'User', 'UserGroup', 'UserXPathRule']