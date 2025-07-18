#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库表和初始化默认数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.models import db, User, UserGroup, UserXPathRule
from backend.config.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        db.create_all()
        logger.info("数据库表创建成功")
        
        # 创建默认用户组
        create_default_groups()
        
        # 创建管理员用户
        create_admin_user()
        
        # 创建默认XPath规则
        create_default_xpath_rules()
        
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def create_default_groups():
    """创建默认用户组"""
    default_groups = [
        {
            'name': 'admin',
            'description': '管理员组，拥有所有权限',
            'permissions': ['read', 'write', 'delete', 'admin']
        },
        {
            'name': 'user',
            'description': '普通用户组，拥有基本权限',
            'permissions': ['read', 'write']
        },
        {
            'name': 'guest',
            'description': '访客组，只有只读权限',
            'permissions': ['read']
        }
    ]
    
    for group_data in default_groups:
        existing_group = UserGroup.query.filter_by(name=group_data['name']).first()
        if not existing_group:
            group = UserGroup(
                name=group_data['name'],
                description=group_data['description'],
                permissions=group_data['permissions']
            )
            db.session.add(group)
            logger.info(f"创建用户组: {group_data['name']}")
    
    db.session.commit()

def create_admin_user():
    """创建管理员用户"""
    config = Config()
    admin_username = config.get('auth.admin_username', 'admin')
    admin_password = config.get('auth.admin_password', 'admin123')
    admin_email = config.get('auth.admin_email', 'admin@example.com')
    
    # 检查管理员是否已存在
    existing_admin = User.query.filter_by(username=admin_username).first()
    if existing_admin:
        logger.info(f"管理员用户 {admin_username} 已存在")
        return
    
    # 获取管理员组
    admin_group = UserGroup.query.filter_by(name='admin').first()
    if not admin_group:
        logger.error("管理员组不存在，无法创建管理员用户")
        return
    
    # 创建管理员用户
    admin_user = User(
        username=admin_username,
        email=admin_email,
        is_active=True,
        created_at=datetime.utcnow()
    )
    admin_user.set_password(admin_password)
    admin_user.groups.append(admin_group)
    
    db.session.add(admin_user)
    db.session.commit()
    
    logger.info(f"管理员用户创建成功: {admin_username}")

def create_default_xpath_rules():
    """创建默认XPath规则"""
    default_rules = [
        {
            'rule_id': 'general_article',
            'name': '通用文章规则',
            'description': '适用于大多数文章页面的通用XPath规则',
            'xpath_config': {
                'title': '//title/text() | //h1/text() | //h2/text()',
                'content': '//article//p/text() | //div[@class="content"]//p/text() | //div[@id="content"]//p/text()',
                'images': '//img/@src',
                'links': '//a/@href'
            },
            'is_active': True
        },
        {
            'rule_id': 'news_article',
            'name': '新闻文章规则',
            'description': '适用于新闻网站的XPath规则',
            'xpath_config': {
                'title': '//h1[@class="title"] | //h1[@class="headline"] | //title',
                'content': '//div[@class="article-body"]//p | //div[@class="content"]//p',
                'author': '//span[@class="author"] | //div[@class="byline"]',
                'publish_date': '//time/@datetime | //span[@class="date"]',
                'images': '//div[@class="article-body"]//img/@src'
            },
            'is_active': True
        }
    ]
    
    # 获取管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        logger.warning("管理员用户不存在，跳过XPath规则创建")
        return
    
    for rule_data in default_rules:
        existing_rule = UserXPathRule.query.filter_by(rule_id=rule_data['rule_id']).first()
        if not existing_rule:
            rule = UserXPathRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                description=rule_data['description'],
                xpath_config=rule_data['xpath_config'],
                is_active=rule_data['is_active'],
                user_id=admin_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(rule)
            logger.info(f"创建XPath规则: {rule_data['rule_id']}")
    
    db.session.commit()

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_database()
    print("数据库初始化完成！")