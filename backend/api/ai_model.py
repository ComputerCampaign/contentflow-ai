#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.ai_model import AIModelConfig
from datetime import datetime
from sqlalchemy import or_
import json
import os
import uuid

# 创建蓝图
ai_model_bp = Blueprint('ai_model', __name__)

# 配置文件路径
MODELS_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ai_content_generator', 'config', 'models.json')
PROMPTS_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ai_content_generator', 'config', 'prompts.json')


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def load_models_json():
    """从models.json文件加载配置"""
    try:
        if os.path.exists(MODELS_JSON_PATH):
            with open(MODELS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        current_app.logger.error(f"加载models.json失败: {str(e)}")
        return None


def load_prompts_json():
    """从prompts.json文件加载配置"""
    try:
        if os.path.exists(PROMPTS_JSON_PATH):
            with open(PROMPTS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        current_app.logger.error(f"加载prompts.json失败: {str(e)}")
        return None


def save_prompts_json(data):
    """保存配置到prompts.json文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(PROMPTS_JSON_PATH), exist_ok=True)
        
        with open(PROMPTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        current_app.logger.error(f"保存prompts.json失败: {str(e)}")
        return False


def save_models_json(data):
    """保存配置到models.json文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(MODELS_JSON_PATH), exist_ok=True)
        
        with open(MODELS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        current_app.logger.error(f"保存models.json失败: {str(e)}")
        return False


def sync_database_to_json(current_user):
    """从数据库同步到JSON文件"""
    try:
        # 获取用户的所有AI模型配置
        models = AIModelConfig.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        # 构建models.json格式的数据
        models_data = {
            "models": {},
            "default_model": None,
            "_note": "模型替换说明：当更换模型时，请确保同时更新对应的API_KEY环境变量。例如，如果使用OpenAI模型，需要设置OPENAI_API_KEY环境变量。"
        }
        
        default_model = None
        for model in models:
            models_data["models"][model.model_key] = model.to_models_json_format()
            if model.is_default:
                default_model = model.model_key
        
        # 设置默认模型
        if default_model:
            models_data["default_model"] = default_model
        elif models:
            # 如果没有设置默认模型，使用第一个
            models_data["default_model"] = models[0].model_key
        
        # 保存到文件
        return save_models_json(models_data)
    except Exception as e:
        current_app.logger.error(f"同步数据库到JSON失败: {str(e)}")
        return False


def sync_json_to_database(current_user):
    """从JSON文件同步到数据库"""
    try:
        json_data = load_models_json()
        if not json_data or 'models' not in json_data:
            return False
        
        models_data = json_data['models']
        default_model = json_data.get('default_model')
        
        synced_count = 0
        updated_count = 0
        
        for model_key, model_data in models_data.items():
            # 检查模型是否已存在
            existing_model = AIModelConfig.query.filter_by(
                model_key=model_key, 
                user_id=current_user.id
            ).first()
            
            if existing_model:
                # 更新现有模型
                existing_model.name = model_data.get('name', model_key)
                existing_model.api_key_env = model_data.get('api_key_env')
                existing_model.base_url = model_data.get('base_url')
                existing_model.model = model_data.get('model')
                
                generation_config = model_data.get('generation_config', {})
                existing_model.max_tokens = generation_config.get('max_tokens', 2000)
                existing_model.temperature = generation_config.get('temperature', 0.7)
                existing_model.top_p = generation_config.get('top_p', 0.9)
                existing_model.frequency_penalty = generation_config.get('frequency_penalty', 0)
                existing_model.presence_penalty = generation_config.get('presence_penalty', 0)
                
                existing_model.max_retries = model_data.get('max_retries', 3)
                existing_model.timeout = model_data.get('timeout', 60)
                existing_model.is_default = (model_key == default_model)
                existing_model.updated_at = datetime.utcnow()
                
                updated_count += 1
            else:
                # 创建新模型
                new_model = AIModelConfig.from_models_json(model_key, model_data, current_user.id)
                new_model.is_default = (model_key == default_model)
                db.session.add(new_model)
                synced_count += 1
        
        db.session.commit()
        current_app.logger.info(f"同步完成: 新增 {synced_count} 个模型，更新 {updated_count} 个模型")
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"同步JSON到数据库失败: {str(e)}")
        return False


def validate_model_config(config_data, partial=False):
    """验证AI模型配置数据"""
    errors = []
    
    # 必需字段验证
    required_fields = ['name', 'model_key', 'api_key_env', 'base_url', 'model']
    if not partial:
        for field in required_fields:
            if field not in config_data or not config_data[field]:
                errors.append(f"字段 '{field}' 是必需的")
    
    # 字段长度验证
    if 'name' in config_data and len(config_data['name']) > 200:
        errors.append("模型名称不能超过200个字符")
    
    if 'model_key' in config_data and len(config_data['model_key']) > 100:
        errors.append("模型标识符不能超过100个字符")
    
    # 数值范围验证
    if 'temperature' in config_data:
        temp = config_data['temperature']
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            errors.append("温度值必须在0-2之间")
    
    if 'top_p' in config_data:
        top_p = config_data['top_p']
        if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
            errors.append("top_p值必须在0-1之间")
    
    if 'max_tokens' in config_data:
        max_tokens = config_data['max_tokens']
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 32000:
            errors.append("最大token数必须在1-32000之间")
    
    return errors


@ai_model_bp.route('/models', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_model():
    """创建AI模型配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证数据
        errors = validate_model_config(data)
        if errors:
            return jsonify({
                'success': False,
                'message': '数据验证失败',
                'errors': errors
            }), 400
        
        # 检查模型标识符是否已存在
        existing_model = AIModelConfig.query.filter_by(
            model_key=data['model_key'],
            user_id=current_user.id
        ).first()
        
        if existing_model:
            return jsonify({
                'success': False,
                'message': f"模型标识符 '{data['model_key']}' 已存在"
            }), 400
        
        # 创建新模型
        new_model = AIModelConfig(
            name=data['name'],
            model_key=data['model_key'],
            api_key_env=data['api_key_env'],
            base_url=data['base_url'],
            model=data['model'],
            user_id=current_user.id,
            description=data.get('description'),
            max_tokens=data.get('max_tokens', 2000),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9),
            frequency_penalty=data.get('frequency_penalty', 0),
            presence_penalty=data.get('presence_penalty', 0),
            max_retries=data.get('max_retries', 3),
            timeout=data.get('timeout', 60),
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if new_model.is_default:
            AIModelConfig.query.filter_by(
                user_id=current_user.id,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(new_model)
        db.session.commit()
        
        # 同步到JSON文件
        sync_database_to_json(current_user)
        
        return jsonify({
            'success': True,
            'message': 'AI模型配置创建成功',
            'data': new_model.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建AI模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建AI模型配置失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/models', methods=['GET'])
@jwt_required()
def get_models():
    """获取AI模型配置列表"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page_str = request.args.get('per_page') or request.args.get('pageSize', '20')
        per_page = min(int(per_page_str), 100)
        search = request.args.get('search', '').strip()
        is_active = request.args.get('is_active')
        
        # 构建查询
        query = AIModelConfig.query.filter_by(user_id=current_user.id)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    AIModelConfig.name.contains(search),
                    AIModelConfig.model_key.contains(search),
                    AIModelConfig.description.contains(search)
                )
            )
        
        # 状态过滤
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            query = query.filter(AIModelConfig.is_active == is_active_bool)
        
        # 排序
        query = query.order_by(AIModelConfig.is_default.desc(), AIModelConfig.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        models = [model.to_dict() for model in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'models': models,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取AI模型配置列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取AI模型配置列表失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/models/<model_id>', methods=['GET'])
@jwt_required()
def get_model(model_id):
    """获取单个AI模型配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        model = AIModelConfig.query.filter_by(
            id=model_id,
            user_id=current_user.id
        ).first()
        
        if not model:
            return jsonify({
                'success': False,
                'message': 'AI模型配置未找到'
            }), 404
        
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取AI模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取AI模型配置失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/models/<model_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("20 per minute")
def update_model(model_id):
    """更新AI模型配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        model = AIModelConfig.query.filter_by(
            id=model_id,
            user_id=current_user.id
        ).first()
        
        if not model:
            return jsonify({
                'success': False,
                'message': 'AI模型配置未找到'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 验证数据
        errors = validate_model_config(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'message': '数据验证失败',
                'errors': errors
            }), 400
        
        # 检查模型标识符是否与其他模型冲突
        if 'model_key' in data and data['model_key'] != model.model_key:
            existing_model = AIModelConfig.query.filter_by(
                model_key=data['model_key'],
                user_id=current_user.id
            ).filter(AIModelConfig.id != model_id).first()
            
            if existing_model:
                return jsonify({
                    'success': False,
                    'message': f"模型标识符 '{data['model_key']}' 已存在"
                }), 400
        
        # 更新字段
        updatable_fields = [
            'name', 'model_key', 'description', 'api_key_env', 'base_url', 'model',
            'max_tokens', 'temperature', 'top_p', 'frequency_penalty', 'presence_penalty',
            'max_retries', 'timeout', 'is_active', 'is_default'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(model, field, data[field])
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if data.get('is_default'):
            AIModelConfig.query.filter_by(
                user_id=current_user.id,
                is_default=True
            ).filter(AIModelConfig.id != model_id).update({'is_default': False})
        
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到JSON文件
        sync_database_to_json(current_user)
        
        return jsonify({
            'success': True,
            'message': 'AI模型配置更新成功',
            'data': model.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新AI模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新AI模型配置失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/models/<model_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_model(model_id):
    """删除AI模型配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        model = AIModelConfig.query.filter_by(
            id=model_id,
            user_id=current_user.id
        ).first()
        
        if not model:
            return jsonify({
                'success': False,
                'message': 'AI模型配置未找到'
            }), 404
        
        # 如果是默认模型，需要先设置其他模型为默认
        if model.is_default:
            other_model = AIModelConfig.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).filter(AIModelConfig.id != model_id).first()
            
            if other_model:
                other_model.is_default = True
        
        db.session.delete(model)
        db.session.commit()
        
        # 同步到JSON文件
        sync_database_to_json(current_user)
        
        return jsonify({
            'success': True,
            'message': 'AI模型配置删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除AI模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除AI模型配置失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/sync/to-json', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def sync_to_json():
    """同步数据库配置到JSON文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        success = sync_database_to_json(current_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': '同步到JSON文件成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '同步到JSON文件失败'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"同步到JSON文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '同步到JSON文件失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/sync/from-json', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def sync_from_json():
    """从JSON文件同步配置到数据库"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        success = sync_json_to_database(current_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': '从JSON文件同步成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '从JSON文件同步失败'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"从JSON文件同步失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '从JSON文件同步失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/sync/bidirectional', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def sync_bidirectional():
    """双向同步：先从JSON同步到数据库，再从数据库同步到JSON"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未找到'
            }), 401
        
        # 先从JSON同步到数据库
        json_success = sync_json_to_database(current_user)
        # 再从数据库同步到JSON
        db_success = sync_database_to_json(current_user)
        
        if json_success and db_success:
            return jsonify({
                'success': True,
                'message': '双向同步成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '双向同步部分失败'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"双向同步失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '双向同步失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/json-info', methods=['GET'])
@jwt_required()
def get_json_info():
    """获取JSON文件信息"""
    try:
        json_data = load_models_json()
        
        if json_data:
            models_count = len(json_data.get('models', {}))
            default_model = json_data.get('default_model')
            
            return jsonify({
                'success': True,
                'data': {
                    'file_exists': True,
                    'models_count': models_count,
                    'default_model': default_model,
                    'file_path': MODELS_JSON_PATH
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'file_exists': False,
                    'models_count': 0,
                    'default_model': None,
                    'file_path': MODELS_JSON_PATH
                }
            })
            
    except Exception as e:
        current_app.logger.error(f"获取JSON文件信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取JSON文件信息失败',
            'error': str(e)
        }), 500


# ==================== Prompts 相关路由 ====================

def validate_prompts_config(config_data):
    """验证提示词配置格式"""
    try:
        if not isinstance(config_data, dict):
            return False, "配置必须是字典格式"
        
        # 检查必需的字段
        required_fields = ['prompts']
        for field in required_fields:
            if field not in config_data:
                return False, f"缺少必需字段: {field}"
        
        # 验证prompts字段
        prompts = config_data.get('prompts', {})
        if not isinstance(prompts, dict):
            return False, "prompts字段必须是字典格式"
        
        return True, None
        
    except Exception as e:
        return False, f"验证配置时发生错误: {str(e)}"


@ai_model_bp.route('/prompts', methods=['GET'])
@jwt_required()
def get_prompts():
    """获取提示词配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未认证'
            }), 401
        
        config_data = load_prompts_json()
        if config_data is None:
            return jsonify({
                'success': False,
                'message': '加载提示词配置失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': config_data,
            'message': '获取提示词配置成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取提示词配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取提示词配置失败',
            'error': str(e)
        }), 500


@ai_model_bp.route('/prompts', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_prompts():
    """更新提示词配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未认证'
            }), 401
        
        config_data = request.get_json()
        if not config_data:
            return jsonify({
                'success': False,
                'message': '请提供配置数据'
            }), 400
        
        # 验证配置格式
        is_valid, error_message = validate_prompts_config(config_data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': f'配置格式错误: {error_message}'
            }), 400
        
        # 保存配置
        if not save_prompts_json(config_data):
            return jsonify({
                'success': False,
                'message': '保存提示词配置失败'
            }), 500
        
        current_app.logger.info(f"用户 {current_user.username} 更新了提示词配置")
        
        return jsonify({
            'success': True,
            'message': '提示词配置更新成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"更新提示词配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新提示词配置失败',
            'error': str(e)
        }), 500