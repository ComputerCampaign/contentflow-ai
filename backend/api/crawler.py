#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.crawler import CrawlerConfig, CrawlerResult
from datetime import datetime
from sqlalchemy import or_
import re
import requests
from urllib.parse import urlparse


crawler_bp = Blueprint('crawler', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def validate_url(url):
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_crawler_config(config_data):
    """验证爬虫配置数据"""
    required_fields = ['name']
    
    for field in required_fields:
        if field not in config_data or not config_data[field]:
            return False, f'缺少必需字段: {field}'
    
    # 验证超时时间
    if 'timeout' in config_data:
        timeout = config_data['timeout']
        if not isinstance(timeout, (int, float)) or timeout < 1 or timeout > 3600:
            return False, 'timeout值必须在1-3600秒之间'
    
    # 验证重试次数
    if 'retry' in config_data:
        retry = config_data['retry']
        if not isinstance(retry, int) or retry < 0 or retry > 10:
            return False, '重试次数必须在0-10之间'
    
    # 验证页面加载等待时间
    if 'page_load_wait' in config_data:
        page_load_wait = config_data['page_load_wait']
        if not isinstance(page_load_wait, int) or page_load_wait < 1 or page_load_wait > 60:
            return False, '页面加载等待时间必须在1-60秒之间'
    
    # 验证布尔值字段
    bool_fields = ['use_selenium', 'enable_xpath', 'headless', 'email_notification']
    for field in bool_fields:
        if field in config_data and not isinstance(config_data[field], bool):
            return False, f'{field}必须是布尔值'
    
    # 验证rule_ids格式
    if 'rule_ids' in config_data and config_data['rule_ids']:
        rule_ids = config_data['rule_ids']
        if not isinstance(rule_ids, str):
            return False, 'rule_ids必须是字符串'
        # 检查是否为逗号分隔的格式
        if not re.match(r'^[a-zA-Z0-9_,\s]+$', rule_ids):
            return False, 'rule_ids格式不正确，应为逗号分隔的字符串'
    
    return True, None


@crawler_bp.route('/configs', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_crawler_config():
    """创建爬虫配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证配置
        is_valid, message = validate_crawler_config(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message,
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 检查配置名称是否已存在
        existing_config = CrawlerConfig.query.filter_by(
            name=data['name'], user_id=current_user.id
        ).first()
        if existing_config:
            return jsonify({
                'success': False,
                'message': '配置名称已存在',
                'error_code': 'CONFIG_EXISTS'
            }), 409
        
        # 创建爬虫配置
        config = CrawlerConfig(
            name=data['name'],
            description=data.get('description', ''),
            output=data.get('output'),
            data_dir=data.get('data_dir'),
            use_selenium=data.get('use_selenium', False),
            timeout=data.get('timeout', 30),
            retry=data.get('retry', 3),
            config=data.get('config', 'config.json'),
            email_notification=data.get('email_notification', False),
            headless=data.get('headless', True),
            proxy=data.get('proxy'),
            page_load_wait=data.get('page_load_wait', 10),
            user_agent=data.get('user_agent'),
            rule_ids=data.get('rule_ids'),
            enable_xpath=data.get('enable_xpath', False),
            user_id=current_user.id
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '爬虫配置创建成功',
            'data': {
                'config': config.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建爬虫配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建爬虫配置失败，请稍后重试'
        }), 500


@crawler_bp.route('/configs', methods=['GET'])
@jwt_required()
def get_crawler_configs():
    """获取爬虫配置列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '').strip()
        use_selenium = request.args.get('use_selenium')
        enable_xpath = request.args.get('enable_xpath')
        enabled = request.args.get('enabled')
        
        # 构建查询
        query = CrawlerConfig.query.filter_by(user_id=current_user.id)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    CrawlerConfig.name.contains(search),
                    CrawlerConfig.description.contains(search)
                )
            )
        
        # 过滤条件
        if use_selenium is not None:
            use_selenium_bool = use_selenium.lower() == 'true'
            query = query.filter(CrawlerConfig.use_selenium == use_selenium_bool)
        
        if enable_xpath is not None:
            enable_xpath_bool = enable_xpath.lower() == 'true'
            query = query.filter(CrawlerConfig.enable_xpath == enable_xpath_bool)
        
        if enabled is not None:
            enabled_bool = enabled.lower() == 'true'
            query = query.filter(CrawlerConfig.enabled == enabled_bool)
        
        # 排序和分页
        query = query.order_by(CrawlerConfig.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        configs = [config.to_dict() for config in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取爬虫配置列表成功',
            'data': {
                'configs': configs,
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
        current_app.logger.error(f"获取爬虫配置列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取爬虫配置列表失败'
        }), 500


@crawler_bp.route('/configs/<config_id>', methods=['GET'])
@jwt_required()
def get_crawler_config(config_id):
    """获取爬虫配置详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫配置不存在'
            }), 404
        
        # 获取最近的爬取结果
        recent_results = CrawlerResult.query.filter_by(config_id=config_id)\
            .order_by(CrawlerResult.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'message': '获取配置成功',
            'data': config.to_dict(include_results=True),
            'recent_results': [result.to_dict() for result in recent_results]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取爬虫配置详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取爬虫配置详情失败'
        }), 500


@crawler_bp.route('/configs/<config_id>', methods=['PUT'])
@jwt_required()
def update_crawler_config(config_id):
    """更新爬虫配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫配置不存在'
            }), 404
        
        # 配置状态检查已移除（status字段不存在）
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证配置（如果提供了完整配置）
        if 'name' in data:
            # 构建完整配置用于验证
            full_config = {
                'name': data.get('name', config.name)
            }
            is_valid, message = validate_crawler_config(full_config)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        # 检查名称冲突
        if 'name' in data and data['name'] != config.name:
            existing_config = CrawlerConfig.query.filter_by(
                name=data['name'], user_id=current_user.id
            ).first()
            if existing_config:
                return jsonify({
                    'success': False,
                    'message': '配置名称已存在'
                }), 409
        
        # 可更新的字段
        updatable_fields = [
            'name', 'description', 'output', 'data_dir', 'use_selenium',
            'timeout', 'retry', 'config', 'email_notification', 'headless',
            'proxy', 'page_load_wait', 'user_agent', 'rule_ids', 'enable_xpath',
            'enabled'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(config, field, data[field])
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '爬虫配置更新成功',
            'data': {
                'config': config.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新爬虫配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新爬虫配置失败'
        }), 500


@crawler_bp.route('/configs/<config_id>', methods=['DELETE'])
@jwt_required()
def delete_crawler_config(config_id):
    """逻辑删除爬虫配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫配置不存在'
            }), 404
        
        # 删除相关的爬取结果
        CrawlerResult.query.filter_by(config_id=config_id).delete()
        
        # 删除配置
        db.session.delete(config)
        
        return jsonify({
            'success': True,
            'message': '爬虫配置删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除爬虫配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除爬虫配置失败'
        }), 500


def generate_crawler_command(config_data, url, task_id=None, task_name=None):
    """生成爬虫命令"""
    command_parts = ['uv', 'run', 'python', '-m', 'crawler.crawler']
    
    # 添加基本参数
    command_parts.extend(['--url', url])
    
    # 添加任务ID和任务名称参数
    if task_id:
        command_parts.extend(['--task-id', task_id])
    if task_name:
        command_parts.extend(['--task-name', task_name])
    
    if config_data.get('output'):
        command_parts.extend(['--output', config_data['output']])
    
    if config_data.get('data_dir'):
        command_parts.extend(['--data-dir', config_data['data_dir']])
    
    # 处理selenium参数，根据数据库值映射
    selenium_value = config_data.get('use_selenium', False)
    command_parts.extend(['--use-selenium', str(selenium_value).lower()])
    
    if config_data.get('timeout'):
        command_parts.extend(['--timeout', str(config_data['timeout'])])
    
    if config_data.get('retry'):
        command_parts.extend(['--retry', str(config_data['retry'])])
    
    if config_data.get('config'):
        command_parts.extend(['--config', config_data['config']])
    
    # 处理headless参数，根据数据库值映射
    headless_value = config_data.get('headless', True)
    command_parts.extend(['--headless', str(headless_value).lower()])
    
    if config_data.get('proxy'):
        command_parts.extend(['--proxy', config_data['proxy']])
    
    if config_data.get('page_load_wait'):
        command_parts.extend(['--page-load-wait', str(config_data['page_load_wait'])])
    
    # 注释掉user-agent参数，避免shell执行时的空格问题
    # if config_data.get('user_agent'):
    #     command_parts.extend(['--user-agent', config_data['user_agent']])
    
    # 验证并过滤有效的rule_ids
    if config_data.get('rule_ids'):
        valid_rule_ids = config_data['rule_ids']
        try:
            from backend.models.xpath import XPathConfig
            # 获取当前存在且启用的规则ID列表
            rule_id_list = [rid.strip() for rid in config_data['rule_ids'].split(',') if rid.strip()]
            existing_rules = XPathConfig.query.filter(
            XPathConfig.rule_id.in_(rule_id_list),
            XPathConfig.enabled == True,
            XPathConfig.status == 'active'
        ).all()
            existing_rule_ids = [rule.rule_id for rule in existing_rules]
            
            if existing_rule_ids:
                valid_rule_ids = ','.join(existing_rule_ids)
                
                # 如果有规则被删除，记录警告
                if len(existing_rule_ids) != len(rule_id_list):
                    removed_rules = set(rule_id_list) - set(existing_rule_ids)
                    current_app.logger.warning(f"配置中的部分XPath规则已被删除: {removed_rules}")
            else:
                current_app.logger.warning("配置中的所有XPath规则都已被删除或禁用")
                # 如果所有规则都被删除，使用原始配置以保持向后兼容
                valid_rule_ids = config_data['rule_ids']
                
            command_parts.extend(['--rule-ids', valid_rule_ids])
        except Exception as e:
            current_app.logger.error(f"验证XPath规则时出错: {str(e)}")
            # 如果验证失败，使用原始配置
            command_parts.extend(['--rule-ids', config_data['rule_ids']])
    
    # 处理enable_xpath参数，根据数据库值映射
    xpath_value = config_data.get('enable_xpath', False)
    command_parts.extend(['--enable-xpath', str(xpath_value).lower()])
    
    return ' '.join(command_parts)


def generate_crawler_command_from_config(config, url, task_id=None, task_name=None):
    """从配置对象生成爬虫命令"""
    # 验证并过滤有效的rule_ids
    valid_rule_ids = config.rule_ids
    if config.rule_ids:
        try:
            from backend.models.xpath import XPathConfig
            # 获取当前存在且启用的规则ID列表
            rule_id_list = [rid.strip() for rid in config.rule_ids.split(',') if rid.strip()]
            existing_rules = XPathConfig.query.filter(
            XPathConfig.rule_id.in_(rule_id_list),
            XPathConfig.enabled == True,
            XPathConfig.status == 'active'
        ).all()
            existing_rule_ids = [rule.rule_id for rule in existing_rules]
            
            if existing_rule_ids:
                valid_rule_ids = ','.join(existing_rule_ids)
                
                # 如果有规则被删除，记录警告
                if len(existing_rule_ids) != len(rule_id_list):
                    removed_rules = set(rule_id_list) - set(existing_rule_ids)
                    current_app.logger.warning(f"配置中的部分XPath规则已被删除: {removed_rules}")
            else:
                current_app.logger.warning("配置中的所有XPath规则都已被删除或禁用")
                # 如果所有规则都被删除，使用原始配置以保持向后兼容
                valid_rule_ids = config.rule_ids
        except Exception as e:
            current_app.logger.error(f"验证XPath规则时出错: {str(e)}")
            # 如果验证失败，使用原始配置
            pass
    
    config_data = {
        'output': config.output,
        'data_dir': config.data_dir,
        'use_selenium': config.use_selenium,
        'timeout': config.timeout,
        'retry': config.retry,
        'config': config.config,
        'headless': config.headless,
        'proxy': config.proxy,
        'page_load_wait': config.page_load_wait,
        'user_agent': config.user_agent,
        'rule_ids': valid_rule_ids,
        'enable_xpath': config.enable_xpath
    }
    return generate_crawler_command(config_data, url, task_id, task_name)


def is_valid_url(url):
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@crawler_bp.route('/configs/validate', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def validate_config():
    """验证爬虫配置"""
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
        
        # 验证配置
        is_valid, message = validate_crawler_config(data)
        
        warnings = []
        errors = []
        
        if not is_valid:
            errors.append(message)
        
        # 添加警告检查
        if data.get('timeout', 30) > 300:
            warnings.append('超时时间过长，可能影响性能')
        
        if data.get('retry', 3) > 5:
            warnings.append('重试次数过多，可能导致被目标网站封禁')
        
        # 生成命令预览
        command_preview = generate_crawler_command(data, 'https://example.com')
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'warnings': warnings,
            'errors': errors,
            'command_preview': command_preview
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@crawler_bp.route('/configs/<config_id>/command', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def get_crawler_command(config_id):
    """生成爬虫执行命令"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 获取配置
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '配置未找到',
                'error_code': 'CONFIG_NOT_FOUND'
            }), 404
        
        # 获取URL参数
        url = request.args.get('url')
        if not url:
            return jsonify({
                'success': False,
                'message': '缺少URL参数',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        # 记录原始URL参数用于调试
        current_app.logger.info(f"原始URL参数: '{url}', 类型: {type(url)}")
        
        # 清理URL参数，去除空格和反引号
        cleaned_url = url.strip().strip('`')
        current_app.logger.info(f"清理后URL参数: '{cleaned_url}'")
        
        if not is_valid_url(cleaned_url):
            current_app.logger.error(f"URL验证失败: '{cleaned_url}'")
            return jsonify({
                'success': False,
                'message': f'无效的URL格式: {cleaned_url}',
                'error_code': 'VALIDATION_ERROR'
            }), 400
        
        url = cleaned_url
        
        # 生成命令
        command = generate_crawler_command_from_config(config, url)
        
        return jsonify({
            'success': True,
            'command': command,
            'config_name': config.name,
            'url': url
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成命令失败: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@crawler_bp.route('/configs/<config_id>/test', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def test_crawler_config(config_id):
    """测试爬虫配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫配置不存在'
            }), 404
        
        data = request.get_json() or {}
        test_url = data.get('test_url')
        
        # 确定测试URL
        if test_url:
            if not validate_url(test_url):
                return jsonify({
                    'success': False,
                    'message': '测试URL格式无效'
                }), 400
            test_urls = [test_url]
        else:
            test_urls = config.target_urls[:1]  # 只测试第一个URL
        
        # 执行测试爬取
        test_results = []
        for url in test_urls:
            try:
                # 获取请求配置
                headers = {'User-Agent': config.user_agent}
                timeout = config.timeout
                
                # 发送请求
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                # 基本信息
                result = {
                    'url': url,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', ''),
                    'encoding': response.encoding,
                    'success': True,
                    'error': None
                }
                
                # 如果启用了XPath，尝试提取数据
                if config.enable_xpath:
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        extracted_data = {}
                        # 这里可以添加基本的XPath测试逻辑
                        # 由于这是测试功能，暂时使用简单的CSS选择器
                        test_selectors = {
                            'title': 'title',
                            'links': 'a',
                            'images': 'img'
                        }
                        
                        for field, selector in test_selectors.items():
                            elements = soup.select(selector)
                            if elements:
                                if field == 'title':
                                    extracted_data[field] = elements[0].get_text().strip() if elements else ''
                                else:
                                    extracted_data[field] = [elem.get('href' if field == 'links' else 'src', '') for elem in elements[:5]]  # 最多5个
                            else:
                                extracted_data[field] = [] if field != 'title' else ''
                        
                        result['extracted_data'] = extracted_data
                        result['extraction_success'] = True
                        
                    except Exception as e:
                        result['extracted_data'] = {}
                        result['extraction_success'] = False
                        result['extraction_error'] = str(e)
                
                test_results.append(result)
                
            except Exception as e:
                test_results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'status_code': None,
                    'content_length': 0
                })
        
        # 更新配置的更新时间
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '爬虫配置测试完成',
            'data': {
                'config_id': config_id,
                'test_results': test_results,
                'summary': {
                    'total_urls': len(test_results),
                    'successful_urls': len([r for r in test_results if r.get('success')]),
                    'failed_urls': len([r for r in test_results if not r.get('success')])
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"测试爬虫配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '测试爬虫配置失败'
        }), 500


@crawler_bp.route('/configs/<config_id>/results', methods=['GET'])
@jwt_required()
def get_crawler_results(config_id):
    """获取爬虫结果"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        config = CrawlerConfig.query.filter_by(
            id=config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫配置不存在'
            }), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # 构建查询
        query = CrawlerResult.query.filter_by(config_id=config_id)
        
        if status:
            query = query.filter(CrawlerResult.status == status)
        
        # 排序和分页
        query = query.order_by(CrawlerResult.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        results = [result.to_dict() for result in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取爬虫结果成功',
            'data': {
                'results': results,
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
        current_app.logger.error(f"获取爬虫结果失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取爬虫结果失败'
        }), 500


@crawler_bp.route('/results/<result_id>', methods=['GET'])
@jwt_required()
def get_crawler_result(result_id):
    """获取单个爬虫结果详情"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 先获取爬虫结果
        result = CrawlerResult.query.filter_by(id=result_id).first()

        
        # 验证配置所有权
        config = CrawlerConfig.query.filter_by(
            id=result.config_id, user_id=current_user.id
        ).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '爬虫结果不存在'
            }), 404
        
        if not result:
            return jsonify({
                'success': False,
                'message': '爬虫结果不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '获取爬虫结果详情成功',
            'data': {
                'result': result.to_dict(include_content=True)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取爬虫结果详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取爬虫结果详情失败'
        }), 500


@crawler_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_crawler_stats():
    """获取爬虫统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # 获取配置统计
        total_configs = CrawlerConfig.query.filter_by(user_id=current_user.id).count()
        selenium_configs = CrawlerConfig.query.filter_by(
            user_id=current_user.id, use_selenium=True
        ).count()
        xpath_configs = CrawlerConfig.query.filter_by(
            user_id=current_user.id, enable_xpath=True
        ).count()
        
        # 获取结果统计
        total_results = CrawlerResult.query.join(CrawlerConfig).filter(
            CrawlerConfig.user_id == current_user.id
        ).count()
        
        success_results = CrawlerResult.query.join(CrawlerConfig).filter(
            CrawlerConfig.user_id == current_user.id,
            CrawlerResult.status == 'success'
        ).count()
        
        failed_results = CrawlerResult.query.join(CrawlerConfig).filter(
            CrawlerConfig.user_id == current_user.id,
            CrawlerResult.status == 'failed'
        ).count()
        
        pending_results = CrawlerResult.query.join(CrawlerConfig).filter(
            CrawlerConfig.user_id == current_user.id,
            CrawlerResult.status == 'pending'
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'configs': {
                    'total': total_configs,
                    'selenium_enabled': selenium_configs,
                    'xpath_enabled': xpath_configs
                },
                'results': {
                    'total': total_results,
                    'success': success_results,
                    'failed': failed_results,
                    'pending': pending_results
                },
                'success_rate': round(success_results / total_results * 100, 2) if total_results > 0 else 0
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败，请稍后重试',
            'error_code': 'INTERNAL_ERROR'
        }), 500