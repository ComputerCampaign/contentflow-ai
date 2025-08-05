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
    """验证爬虫配置"""
    required_fields = ['name', 'target_urls']
    
    for field in required_fields:
        if field not in config_data:
            return False, f"缺少必需字段: {field}"
    
    # 验证名称
    name = config_data.get('name', '').strip()
    if not name or len(name) < 2:
        return False, "配置名称至少需要2个字符"
    
    # 验证目标URL
    target_urls = config_data.get('target_urls', [])
    if not isinstance(target_urls, list) or not target_urls:
        return False, "至少需要一个目标URL"
    
    for url in target_urls:
        if not validate_url(url):
            return False, f"无效的URL: {url}"
    
    # 验证爬取规则
    crawl_rules = config_data.get('crawl_rules', {})
    if crawl_rules:
        if not isinstance(crawl_rules, dict):
            return False, "爬取规则必须是JSON对象"
        
        # 验证CSS选择器
        selectors = crawl_rules.get('selectors', {})
        if selectors and not isinstance(selectors, dict):
            return False, "CSS选择器配置必须是JSON对象"
    
    return True, "配置验证通过"


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
                'message': message
            }), 400
        
        # 检查配置名称是否已存在
        existing_config = CrawlerConfig.query.filter_by(
            name=data['name'], user_id=current_user.id
        ).first()
        if existing_config:
            return jsonify({
                'success': False,
                'message': '配置名称已存在'
            }), 409
        
        # 创建爬虫配置
        config = CrawlerConfig(
            name=data['name'],
            target_urls=data['target_urls'],
            user_id=current_user.id,
            description=data.get('description', ''),
            crawl_rules=data.get('crawl_rules', {}),
            request_config=data.get('request_config', {}),
            schedule_config=data.get('schedule_config', {}),
            output_config=data.get('output_config', {}),
            tags=data.get('tags', [])
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
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = CrawlerConfig.query.filter_by(user_id=current_user.id)
        
        # 状态过滤
        if status:
            query = query.filter(CrawlerConfig.status == status)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    CrawlerConfig.name.contains(search),
                    CrawlerConfig.description.contains(search)
                )
            )
        
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
            'message': '获取爬虫配置详情成功',
            'data': {
                'config': config.to_dict(include_stats=True),
                'recent_results': [result.to_dict() for result in recent_results]
            }
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
        
        # 检查配置状态
        if config.status == 'running':
            return jsonify({
                'success': False,
                'message': '运行中的配置无法修改'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证配置（如果提供了完整配置）
        if 'name' in data or 'target_urls' in data:
            # 构建完整配置用于验证
            full_config = {
                'name': data.get('name', config.name),
                'target_urls': data.get('target_urls', config.target_urls)
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
            'name', 'description', 'target_urls', 'crawl_rules',
            'request_config', 'schedule_config', 'output_config', 'tags'
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
    """删除爬虫配置"""
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
        
        # 检查配置状态
        if config.status == 'running':
            return jsonify({
                'success': False,
                'message': '运行中的配置无法删除'
            }), 400
        
        # 删除相关的爬取结果
        CrawlerResult.query.filter_by(config_id=config_id).delete()
        
        # 删除配置
        db.session.delete(config)
        db.session.commit()
        
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
        max_pages = data.get('max_pages', 1)
        
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
                request_config = config.request_config or {}
                headers = request_config.get('headers', {})
                timeout = request_config.get('timeout', 30)
                
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
                
                # 如果有爬取规则，尝试提取数据
                crawl_rules = config.crawl_rules or {}
                if crawl_rules.get('selectors'):
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        extracted_data = {}
                        selectors = crawl_rules['selectors']
                        
                        for field, selector in selectors.items():
                            elements = soup.select(selector)
                            if elements:
                                extracted_data[field] = [elem.get_text().strip() for elem in elements[:5]]  # 最多5个
                            else:
                                extracted_data[field] = []
                        
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
        
        # 更新配置的测试时间
        config.last_test_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '爬虫配置测试完成',
            'data': {
                'config_id': config_id,
                'test_time': config.last_test_time.isoformat(),
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
        
        result = CrawlerResult.query.join(CrawlerConfig).filter(
            CrawlerResult.id == result_id,
            CrawlerConfig.user_id == current_user.id
        ).first()
        
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
                'message': '用户不存在'
            }), 401
        
        # 配置统计
        config_stats = {
            'total': CrawlerConfig.query.filter_by(user_id=current_user.id).count(),
            'active': CrawlerConfig.query.filter_by(user_id=current_user.id, status='active').count(),
            'inactive': CrawlerConfig.query.filter_by(user_id=current_user.id, status='inactive').count(),
            'running': CrawlerConfig.query.filter_by(user_id=current_user.id, status='running').count()
        }
        
        # 结果统计
        result_stats = {
            'total': CrawlerResult.query.join(CrawlerConfig).filter(
                CrawlerConfig.user_id == current_user.id
            ).count(),
            'success': CrawlerResult.query.join(CrawlerConfig).filter(
                CrawlerConfig.user_id == current_user.id,
                CrawlerResult.status == 'success'
            ).count(),
            'failed': CrawlerResult.query.join(CrawlerConfig).filter(
                CrawlerConfig.user_id == current_user.id,
                CrawlerResult.status == 'failed'
            ).count()
        }
        
        return jsonify({
            'success': True,
            'message': '获取统计信息成功',
            'data': {
                'config_stats': config_stats,
                'result_stats': result_stats
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败'
        }), 500