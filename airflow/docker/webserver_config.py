# -*- coding: utf-8 -*-
"""
Airflow Web服务器配置文件
"""

import os
from flask_appbuilder.security.manager import AUTH_DB

# 基础配置
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask配置
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# 认证配置
AUTH_TYPE = AUTH_DB
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# 用户注册配置
AUTH_USER_REGISTRATION = False
AUTH_USER_REGISTRATION_ROLE = "Public"

# 密码复杂度要求
AUTH_PASSWORD_COMPLEXITY_ENABLED = True
AUTH_PASSWORD_COMPLEXITY_VALIDATOR = {
    'min_length': 8,
    'max_length': 128,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_numbers': True,
    'require_special_chars': False
}

# 会话配置
PERMANENT_SESSION_LIFETIME = 1800  # 30分钟

# 安全配置
SECRET_KEY = os.environ.get('AIRFLOW_SECRET_KEY', 'your-secret-key-here')

# 数据库配置
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'AIRFLOW_DATABASE_URL',
    f"mysql+pymysql://{os.environ.get('AIRFLOW_DB_USER', 'crawler_airflow_user')}:"
    f"{os.environ.get('AIRFLOW_DB_PASSWORD', 'crawler_airflow_password')}@"
    f"{os.environ.get('AIRFLOW_DB_HOST', 'crawler_mysql')}:"
    f"{os.environ.get('AIRFLOW_DB_PORT', '3306')}/"
    f"{os.environ.get('AIRFLOW_DB_NAME', 'crawler_airflow_db')}"
)

# 日志配置
LOG_LEVEL = 'INFO'

# 国际化配置
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'zh': {'flag': 'cn', 'name': '中文'}
}

# 默认语言
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

# 页面配置
PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 上传配置
UPLOAD_FOLDER = '/opt/airflow/uploads/'
IMG_UPLOAD_FOLDER = '/opt/airflow/uploads/'
IMG_UPLOAD_URL = '/uploads/'
IMG_SIZE = (150, 150, True)

# 缓存配置
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# 邮件配置
MAIL_SERVER = os.environ.get('AIRFLOW_SMTP_HOST', 'localhost')
MAIL_PORT = int(os.environ.get('AIRFLOW_SMTP_PORT', '587'))
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('AIRFLOW_SMTP_USER', '')
MAIL_PASSWORD = os.environ.get('AIRFLOW_SMTP_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.environ.get('AIRFLOW_SMTP_FROM', 'airflow@example.com')

# 自定义安全管理器（可选）
# from airflow.www.security import AirflowSecurityManager
# SECURITY_MANAGER_CLASS = AirflowSecurityManager

# 自定义视图（可选）
# from airflow.www.views import HomeView
# FAB_INDEX_VIEW = 'HomeView'

# API配置
API_TITLE = 'Crawler Platform Airflow API'
API_VERSION = 'v1'
OPENAPI_VERSION = '3.0.2'

# 自定义CSS和JS（可选）
# APP_THEME = 'bootstrap-theme.css'
# CUSTOM_SECURITY_MANAGER = None