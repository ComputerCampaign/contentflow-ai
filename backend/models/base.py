#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库基础配置
"""

from flask_sqlalchemy import SQLAlchemy

# 数据库实例将在app.py中初始化
db = SQLAlchemy()