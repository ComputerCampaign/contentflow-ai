#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XPath规则管理相关API接口
"""

from flask import Blueprint, request, jsonify, g

import os
import sys
# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.models import UserXPathRule, db
from backend.auth.permissions import login_required, check_xpath_limit
from backend.crawler_utils.xpath_manager import XPathManager

xpath_bp = Blueprint('xpath', __name__)

@xpath_bp.route('/rules', methods=['GET'])
@login_required
def get_user_xpath_rules():
    """
    获取当前用户的XPath规则列表
    """
    user = g.current_user
    rules = user.xpath_rules
    
    return jsonify({
        "rules": [{
            "id": rule.id,
            "rule_name": rule.rule_name,
            "domain": rule.domain,
            "xpath": rule.xpath,
            "description": rule.description,
            "created_at": rule.created_at.isoformat()
        } for rule in rules]
    })

@xpath_bp.route('/rules', methods=['POST'])
@login_required
@check_xpath_limit
def create_xpath_rule():
    """
    创建新的XPath规则
    
    请求体:
    {
        "rule_name": "规则名称",
        "domain": "适用域名",
        "xpath": "XPath表达式",
        "description": "规则描述" (可选)
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ('rule_name', 'domain', 'xpath')):
        return jsonify({"error": "缺少必要字段"}), 400
    
    # 检查规则名称是否已存在
    if UserXPathRule.query.filter_by(user_id=g.current_user.id, rule_name=data['rule_name']).first():
        return jsonify({"error": "规则名称已存在"}), 400
    
    new_rule = UserXPathRule(
        rule_name=data['rule_name'],
        domain=data['domain'],
        xpath=data['xpath'],
        description=data.get('description', ''),
        user_id=g.current_user.id
    )
    
    db.session.add(new_rule)
    db.session.commit()
    
    return jsonify({
        "id": new_rule.id,
        "rule_name": new_rule.rule_name,
        "message": "XPath规则创建成功"
    }), 201

@xpath_bp.route('/rules/<int:rule_id>', methods=['GET'])
@login_required
def get_xpath_rule(rule_id):
    """
    获取指定XPath规则详情
    """
    rule = UserXPathRule.query.get_or_404(rule_id)
    
    # 验证规则所有权
    if rule.user_id != g.current_user.id:
        return jsonify({"error": "无权访问此规则"}), 403
    
    return jsonify({
        "id": rule.id,
        "rule_name": rule.rule_name,
        "domain": rule.domain,
        "xpath": rule.xpath,
        "description": rule.description,
        "created_at": rule.created_at.isoformat()
    })

@xpath_bp.route('/rules/<int:rule_id>', methods=['PUT'])
@login_required
def update_xpath_rule(rule_id):
    """
    更新指定XPath规则
    
    请求体:
    {
        "rule_name": "规则名称", (可选)
        "domain": "适用域名", (可选)
        "xpath": "XPath表达式", (可选)
        "description": "规则描述" (可选)
    }
    """
    rule = UserXPathRule.query.get_or_404(rule_id)
    
    # 验证规则所有权
    if rule.user_id != g.current_user.id:
        return jsonify({"error": "无权修改此规则"}), 403
    
    data = request.get_json()
    
    if 'rule_name' in data:
        # 检查规则名称是否已被其他规则使用
        existing_rule = UserXPathRule.query.filter_by(user_id=g.current_user.id, rule_name=data['rule_name']).first()
        if existing_rule and existing_rule.id != rule_id:
            return jsonify({"error": "规则名称已被其他规则使用"}), 400
        rule.rule_name = data['rule_name']
    
    if 'domain' in data:
        rule.domain = data['domain']
    
    if 'xpath' in data:
        rule.xpath = data['xpath']
    
    if 'description' in data:
        rule.description = data['description']
    
    db.session.commit()
    
    return jsonify({"message": "XPath规则更新成功"})

@xpath_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_xpath_rule(rule_id):
    """
    删除指定XPath规则
    """
    rule = UserXPathRule.query.get_or_404(rule_id)
    
    # 验证规则所有权
    if rule.user_id != g.current_user.id:
        return jsonify({"error": "无权删除此规则"}), 403
    
    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({"message": "XPath规则删除成功"})

@xpath_bp.route('/system-rules', methods=['GET'])
@login_required
def get_system_xpath_rules():
    """
    获取系统预设的XPath规则列表
    """
    xpath_manager = XPathManager()
    system_rules = xpath_manager.list_rules()
    
    return jsonify({
        "rules": system_rules
    })