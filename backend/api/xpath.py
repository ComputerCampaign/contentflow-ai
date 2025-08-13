#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XPath配置API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.xpath import XPathConfig
from backend.utils.xpath_manager import xpath_manager
from datetime import datetime
from sqlalchemy import or_
import re
import uuid

# 创建蓝图
xpath_bp = Blueprint('xpath', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def sync_json_to_database(current_user):
    """从JSON文件同步数据到数据库"""
    try:
        # 从JSON文件加载规则
        json_rules = xpath_manager.load_xpath_configs_from_file()
        
        if not json_rules:
            current_app.logger.info("JSON文件中没有找到规则数据")
            return
        
        synced_count = 0
        updated_count = 0
        
        for rule_data in json_rules:
            try:
                # 检查必需字段
                required_fields = ['id', 'name', 'domain_patterns', 'xpath', 'rule_type', 'field_name']
                if not all(field in rule_data for field in required_fields):
                    current_app.logger.warning(f"跳过无效规则: {rule_data.get('id', 'unknown')}")
                    continue
                
                # 查找现有规则
                existing_config = XPathConfig.query.filter_by(rule_id=rule_data['id']).first()
                
                if existing_config:
                    # 更新现有规则
                    existing_config.name = rule_data['name']
                    existing_config.description = rule_data.get('description', '')
                    existing_config.domain_patterns = rule_data['domain_patterns']
                    existing_config.xpath = rule_data['xpath']
                    existing_config.rule_type = rule_data['rule_type']
                    existing_config.field_name = rule_data['field_name']
                    existing_config.comment_xpath = rule_data.get('comment_xpath')
                    existing_config.status = 'active'  # JSON文件中的规则默认为活跃状态
                    existing_config.is_public = True   # JSON文件中的规则默认为公开
                    existing_config.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # 创建新规则
                    new_config = XPathConfig(
                        rule_id=rule_data['id'],
                        name=rule_data['name'],
                        description=rule_data.get('description', ''),
                        domain_patterns=rule_data['domain_patterns'],
                        xpath=rule_data['xpath'],
                        rule_type=rule_data['rule_type'],
                        field_name=rule_data['field_name'],
                        comment_xpath=rule_data.get('comment_xpath'),
                        status='active',
                        is_public=True,
                        user_id=current_user.id
                    )
                    db.session.add(new_config)
                    synced_count += 1
                    
            except Exception as rule_error:
                current_app.logger.error(f"同步规则 {rule_data.get('id', 'unknown')} 失败: {str(rule_error)}")
                continue
        
        # 提交数据库更改
        db.session.commit()
        current_app.logger.info(f"JSON同步完成: 新增 {synced_count} 个规则, 更新 {updated_count} 个规则")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"从JSON文件同步数据失败: {str(e)}")
        raise


def validate_xpath_config(config_data, partial=False):
    """验证XPath配置数据"""
    if not partial:
        required_fields = ['rule_id', 'name', 'domain_patterns', 'xpath', 'rule_type', 'field_name']
        
        for field in required_fields:
            if field not in config_data or not config_data[field]:
                return False, f'缺少必需字段: {field}'
    
    # 验证rule_id格式
    if 'rule_id' in config_data:
        rule_id = config_data['rule_id'].strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', rule_id):
            return False, 'rule_id只能包含字母、数字和下划线'
    
    # 验证名称长度
    if 'name' in config_data:
        name = config_data['name'].strip()
        if len(name) < 2 or len(name) > 100:
            return False, '配置名称长度必须在2-100个字符之间'
    
    # 验证XPath表达式
    if 'xpath' in config_data:
        xpath = config_data['xpath'].strip()
        if not xpath:
            return False, 'XPath表达式不能为空'
    
    # 验证规则类型
    if 'rule_type' in config_data:
        rule_type = config_data['rule_type']
        valid_types = ['text', 'image', 'link', 'data']
        if rule_type not in valid_types:
            return False, f'规则类型必须是以下之一: {", ".join(valid_types)}'
    
    # 验证域名模式
    if 'domain_patterns' in config_data:
        domain_patterns = config_data['domain_patterns']
        if not isinstance(domain_patterns, list) or len(domain_patterns) == 0:
            return False, '域名模式必须是非空数组'
    
    # 验证字段名称
    if 'field_name' in config_data:
        field_name = config_data['field_name'].strip()
        if not field_name:
            return False, '字段名称不能为空'
    
    # 验证状态
    if 'status' in config_data:
        status = config_data['status']
        valid_statuses = ['active', 'inactive', 'testing']
        if status not in valid_statuses:
            return False, f'状态必须是以下之一: {", ".join(valid_statuses)}'
    
    # 验证布尔值字段
    if 'is_public' in config_data and not isinstance(config_data['is_public'], bool):
        return False, 'is_public必须是布尔值'
    
    return True, None


@xpath_bp.route('/rules', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_xpath_rule():
    """创建XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证配置数据
        is_valid, error_message = validate_xpath_config(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message,
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查rule_id是否已存在
        existing_config = XPathConfig.query.filter_by(
            rule_id=data['rule_id']
        ).first()
        if existing_config:
            return jsonify({
                'success': False,
                'message': '规则ID已存在',
                'error_code': 'RULE_ID_EXISTS'
            }), 409
        
        # 创建XPath配置
        config = XPathConfig(
            rule_id=data['rule_id'],
            name=data['name'],
            description=data.get('description', ''),
            domain_patterns=data['domain_patterns'],
            xpath=data['xpath'],
            rule_type=data['rule_type'],
            field_name=data['field_name'],
            comment_xpath=data.get('comment_xpath'),
            status=data.get('status', 'active'),
            is_public=data.get('is_public', False),
            user_id=current_user.id
        )
        
        db.session.add(config)
        db.session.commit()
        
        # 如果是公开规则，同步到JSON文件
        if config.is_public and config.status == 'active':
            try:
                xpath_manager.write_xpath_configs_to_file()
            except Exception as sync_error:
                current_app.logger.error(f"同步XPath配置到JSON文件失败: {str(sync_error)}")
        
        return jsonify({
            'success': True,
            'message': 'XPath规则创建成功',
            'data': config.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules', methods=['GET'])
@jwt_required()
def get_xpath_rules():
    """获取XPath规则列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 在查询数据库之前，先从JSON文件同步数据到数据库
        try:
            sync_json_to_database(current_user)
        except Exception as sync_error:
            current_app.logger.warning(f"从JSON文件同步数据失败: {str(sync_error)}")
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '').strip()
        rule_type = request.args.get('rule_type', '').strip()
        status = request.args.get('status', '').strip()
        is_public = request.args.get('is_public', '').strip()
        domain = request.args.get('domain', '').strip()
        
        # 构建查询 - 显示用户自己的规则和公开规则
        query = XPathConfig.query.filter(
            or_(
                XPathConfig.user_id == current_user.id,
                XPathConfig.is_public == True
            )
        )
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    XPathConfig.name.contains(search),
                    XPathConfig.description.contains(search),
                    XPathConfig.rule_id.contains(search)
                )
            )
        
        # 规则类型过滤
        if rule_type:
            query = query.filter(XPathConfig.rule_type == rule_type)
        
        # 状态过滤
        if status:
            query = query.filter(XPathConfig.status == status)
        
        # 公开状态过滤
        if is_public:
            is_public_bool = is_public.lower() == 'true'
            query = query.filter(XPathConfig.is_public == is_public_bool)
        
        # 域名过滤
        if domain:
            query = query.filter(XPathConfig.domain_patterns.contains([domain]))
        
        # 排序和分页
        query = query.order_by(XPathConfig.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        rules = [rule.to_dict() for rule in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'rules': rules,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取XPath规则列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取XPath规则列表失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules/<rule_id>', methods=['GET'])
@jwt_required()
def get_xpath_rule(rule_id):
    """获取单个XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 查找规则 - 用户自己的规则或公开规则
        config = XPathConfig.query.filter(
            XPathConfig.rule_id == rule_id,
            or_(
                XPathConfig.user_id == current_user.id,
                XPathConfig.is_public == True
            )
        ).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': 'XPath规则不存在',
                'error_code': 'RULE_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules/<rule_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("20 per minute")
def update_xpath_rule(rule_id):
    """更新XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 只能更新自己的规则
        config = XPathConfig.query.filter_by(
            rule_id=rule_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': 'XPath规则不存在或无权限修改',
                'error_code': 'RULE_NOT_FOUND'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证配置数据
        is_valid, error_message = validate_xpath_config(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message,
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查rule_id是否重复（如果要更新rule_id）
        if 'rule_id' in data and data['rule_id'] != config.rule_id:
            existing_config = XPathConfig.query.filter_by(
                rule_id=data['rule_id']
            ).first()
            if existing_config:
                return jsonify({
                    'success': False,
                    'message': '规则ID已存在',
                    'error_code': 'RULE_ID_EXISTS'
                }), 409
        
        # 更新配置
        config.rule_id = data.get('rule_id', config.rule_id)
        config.name = data['name']
        config.description = data.get('description', config.description)
        config.domain_patterns = data.get('domain_patterns', config.domain_patterns)
        config.xpath = data['xpath']
        config.rule_type = data.get('rule_type', config.rule_type)
        config.field_name = data.get('field_name', config.field_name)
        config.comment_xpath = data.get('comment_xpath', config.comment_xpath)
        config.status = data.get('status', config.status)
        config.is_public = data.get('is_public', config.is_public)
        config.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 如果是公开规则，同步到JSON文件
        if config.is_public and config.status == 'active':
            try:
                xpath_manager.write_xpath_configs_to_file()
            except Exception as sync_error:
                current_app.logger.error(f"同步XPath配置到JSON文件失败: {str(sync_error)}")
        
        return jsonify({
            'success': True,
            'message': 'XPath规则更新成功',
            'data': config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules/<rule_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_xpath_rule(rule_id):
    """删除XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 只能删除自己的规则
        config = XPathConfig.query.filter_by(
            rule_id=rule_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': 'XPath规则不存在或无权限删除',
                'error_code': 'RULE_NOT_FOUND'
            }), 404
        
        # 检查是否有任务正在使用此配置
        from backend.models.task import Task
        active_tasks = Task.query.filter(
            Task.xpath_config_id == config.id,
            Task.status.in_(['pending', 'running'])
        ).count()
        if active_tasks > 0:
            return jsonify({
                'success': False,
                'message': f'无法删除规则，有 {active_tasks} 个任务正在使用此规则',
                'error_code': 'RULE_IN_USE'
            }), 400
        
        db.session.delete(config)
        db.session.commit()
        
        # 如果是公开规则，同步到JSON文件
        if config.is_public:
            try:
                xpath_manager.write_xpath_configs_to_file()
            except Exception as sync_error:
                current_app.logger.error(f"同步XPath配置到JSON文件失败: {str(sync_error)}")
        
        return jsonify({
            'success': True,
            'message': 'XPath规则删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules/validate', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def validate_xpath_rule():
    """验证XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 验证规则数据
        validation_error = validate_xpath_config(data)
        if validation_error:
            return jsonify({
                'success': False,
                'message': validation_error,
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查rule_id是否已存在
        if 'rule_id' in data:
            existing_rule = XPathConfig.query.filter_by(rule_id=data['rule_id']).first()
            if existing_rule:
                return jsonify({
                    'success': False,
                    'message': '规则ID已存在',
                    'error_code': 'RULE_ID_EXISTS'
                }), 409
        
        # 验证XPath语法
        warnings = []
        errors = []
        
        try:
            from lxml import etree
            etree.XPath(data['xpath'])
        except Exception as e:
            errors.append(f'XPath语法错误: {str(e)}')
        
        # 检查域名模式格式
        if 'domain_patterns' in data:
            for pattern in data['domain_patterns']:
                if not isinstance(pattern, str) or len(pattern.strip()) == 0:
                    warnings.append('域名模式包含空字符串')
        
        return jsonify({
            'success': True,
            'data': {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"验证XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '验证XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/rules/test', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def test_xpath_rule():
    """测试XPath规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        rule_id = data.get('rule_id')
        test_url = data.get('url', '').strip()
        use_selenium = data.get('selenium', False)
        
        if not rule_id:
            return jsonify({
                'success': False,
                'message': '缺少rule_id参数',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        if not test_url:
            return jsonify({
                'success': False,
                'message': '缺少url参数',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 查找规则
        config = XPathConfig.query.filter(
            XPathConfig.rule_id == rule_id,
            or_(
                XPathConfig.user_id == current_user.id,
                XPathConfig.is_public == True
            )
        ).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': 'XPath规则不存在',
                'error_code': 'RULE_NOT_FOUND'
            }), 404
        
        # 验证URL格式
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(test_url):
            return jsonify({
                'success': False,
                'message': '无效的URL格式',
                'error_code': 'INVALID_URL'
            }), 400
        
        # 检查域名匹配
        if config.domain_patterns:
            domain_match = False
            for pattern in config.domain_patterns:
                if pattern in test_url:
                    domain_match = True
                    break
            
            if not domain_match:
                return jsonify({
                    'success': False,
                    'message': '测试URL不匹配规则的域名模式',
                    'error_code': 'DOMAIN_MISMATCH',
                    'data': {
                        'domain_patterns': config.domain_patterns
                    }
                }), 400
        
        # 执行测试
        try:
            if use_selenium:
                # TODO: 实现Selenium测试逻辑
                results = []
                response_info = {'method': 'selenium'}
            else:
                import requests
                from lxml import html
                
                # 发送请求
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(test_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # 解析HTML
                tree = html.fromstring(response.content)
                
                # 执行XPath查询
                elements = tree.xpath(config.xpath)
                
                # 提取结果
                results = []
                for element in elements[:10]:  # 最多返回10个结果
                    if config.rule_type == 'text':
                        results.append(element.text_content().strip() if hasattr(element, 'text_content') else str(element).strip())
                    elif config.rule_type == 'attribute' and config.field_name:
                        results.append(element.get(config.field_name, '') if hasattr(element, 'get') else '')
                    elif config.rule_type == 'html':
                        results.append(html.tostring(element, encoding='unicode') if hasattr(element, 'tag') else str(element))
                    elif config.rule_type == 'link':
                        href = element.get('href', '') if hasattr(element, 'get') else ''
                        results.append(href)
                    elif config.rule_type == 'image':
                        src = element.get('src', '') if hasattr(element, 'get') else ''
                        results.append(src)
                    else:
                        results.append(str(element))
                
                response_info = {
                    'method': 'requests',
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', '')
                }
            
            # 更新使用统计
            config.update_usage_stats(True)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'rule_id': rule_id,
                    'url': test_url,
                    'xpath': config.xpath,
                    'rule_type': config.rule_type,
                    'results_count': len(results),
                    'results': results,
                    'response_info': response_info
                }
            }), 200
            
        except Exception as e:
            # 更新使用统计（失败）
            config.update_usage_stats(False)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'XPath测试失败: {str(e)}',
                'error_code': 'TEST_FAILED',
                'data': {
                    'rule_id': rule_id,
                    'url': test_url,
                    'xpath': config.xpath
                }
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"测试XPath规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '测试XPath规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/configs/<config_id>/test', methods=['POST'])
@jwt_required()
def test_xpath_config(config_id):
    """测试XPath配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = XPathConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': 'XPath配置不存在'
            }), 404
        
        data = request.get_json()
        test_url = data.get('test_url', '').strip()
        
        if not test_url:
            return jsonify({
                'success': False,
                'message': '请提供测试URL'
            }), 400
        
        # 验证URL格式
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(test_url):
            return jsonify({
                'success': False,
                'message': '无效的URL格式'
            }), 400
        
        # 检查域名匹配
        if config.domain_patterns:
            domain_match = False
            for pattern in config.domain_patterns:
                if pattern in test_url:
                    domain_match = True
                    break
            
            if not domain_match:
                return jsonify({
                    'success': False,
                    'message': '测试URL不匹配配置的域名模式',
                    'data': {
                        'domain_patterns': config.domain_patterns
                    }
                }), 400
        
        # 执行测试（这里可以添加实际的XPath测试逻辑）
        try:
            import requests
            from lxml import html
            
            # 发送请求
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(test_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 解析HTML
            tree = html.fromstring(response.content)
            
            # 执行XPath查询
            elements = tree.xpath(config.xpath)
            
            # 提取结果
            results = []
            for element in elements[:10]:  # 最多返回10个结果
                if config.rule_type == 'text':
                    results.append(element.text_content().strip() if hasattr(element, 'text_content') else str(element).strip())
                elif config.rule_type == 'attribute' and config.field_name:
                    results.append(element.get(config.field_name, '') if hasattr(element, 'get') else '')
                elif config.rule_type == 'html':
                    results.append(html.tostring(element, encoding='unicode') if hasattr(element, 'tag') else str(element))
                else:
                    results.append(str(element))
            
            # 更新使用统计
            config.update_usage_stats(True)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'XPath配置测试成功',
                'data': {
                    'config_id': config_id,
                    'test_url': test_url,
                    'xpath': config.xpath,
                    'rule_type': config.rule_type,
                    'results_count': len(results),
                    'results': results,
                    'response_info': {
                        'status_code': response.status_code,
                        'content_length': len(response.content),
                        'content_type': response.headers.get('content-type', '')
                    }
                }
            }), 200
            
        except Exception as e:
            # 更新使用统计（失败）
            config.update_usage_stats(False)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'XPath测试失败: {str(e)}',
                'data': {
                    'config_id': config_id,
                    'test_url': test_url,
                    'xpath': config.xpath
                }
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"测试XPath配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '测试XPath配置失败'
        }), 500


@xpath_bp.route('/sync/to-json', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def sync_rules_to_json():
    """同步规则到JSON文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 只同步公开且活跃的规则
        public_rules = XPathConfig.query.filter_by(
            is_public=True,
            status='active'
        ).all()
        
        try:
            xpath_manager.write_xpath_configs_to_file()
            
            return jsonify({
                'success': True,
                'data': {
                    'synced_count': len(public_rules),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'同步到JSON文件失败: {str(e)}',
                'error_code': 'SYNC_FAILED'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"同步规则到JSON失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '同步规则到JSON失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/sync/from-json', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def sync_rules_from_json():
    """从JSON文件同步规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        try:
            # TODO: 实现从JSON文件读取规则的逻辑
            imported_count = 0
            updated_count = 0
            
            return jsonify({
                'success': True,
                'data': {
                    'imported_count': imported_count,
                    'updated_count': updated_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'从JSON文件同步失败: {str(e)}',
                'error_code': 'SYNC_FAILED'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"从JSON同步规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '从JSON同步规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/sync/bidirectional', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def sync_rules_bidirectional():
    """双向同步规则"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        try:
            # TODO: 实现双向同步逻辑
            to_json_count = 0
            from_json_count = 0
            conflicts_count = 0
            
            return jsonify({
                'success': True,
                'data': {
                    'to_json_count': to_json_count,
                    'from_json_count': from_json_count,
                    'conflicts_count': conflicts_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'双向同步失败: {str(e)}',
                'error_code': 'SYNC_FAILED'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"双向同步规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '双向同步规则失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/sync/json-info', methods=['GET'])
@jwt_required()
def get_json_info():
    """获取JSON文件信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        try:
            # TODO: 实现获取JSON文件信息的逻辑
            import os
            json_file_path = 'data/xpath_configs.json'  # 假设的路径
            
            if os.path.exists(json_file_path):
                stat = os.stat(json_file_path)
                file_info = {
                    'exists': True,
                    'size': stat.st_size,
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'rules_count': 0  # TODO: 从文件中读取实际数量
                }
            else:
                file_info = {
                    'exists': False,
                    'size': 0,
                    'modified_at': None,
                    'rules_count': 0
                }
            
            return jsonify({
                'success': True,
                'data': file_info
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取JSON文件信息失败: {str(e)}',
                'error_code': 'FILE_ERROR'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"获取JSON文件信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取JSON文件信息失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@xpath_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_xpath_stats():
    """获取XPath规则统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 规则统计
        rule_stats = {
            'total': XPathConfig.query.filter_by(user_id=current_user.id).count(),
            'active': XPathConfig.query.filter_by(user_id=current_user.id, status='active').count(),
            'inactive': XPathConfig.query.filter_by(user_id=current_user.id, status='inactive').count(),
        }
        
        # 规则类型统计
        rule_type_stats = {}
        rule_types = ['text', 'attribute', 'html', 'link', 'image']
        for rule_type in rule_types:
            rule_type_stats[rule_type] = XPathConfig.query.filter_by(
                user_id=current_user.id, rule_type=rule_type
            ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'rule_stats': rule_stats,
                'rule_type_stats': rule_type_stats
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500