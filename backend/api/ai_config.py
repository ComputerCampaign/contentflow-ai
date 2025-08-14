#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI配置API
"""

import json
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import limiter
from backend.models.user import User

# 创建蓝图
ai_config_bp = Blueprint('ai_config', __name__)

# 配置文件路径
PROMPTS_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'ai_content_generator', 'config', 'prompts.json'
)
MODELS_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'ai_content_generator', 'config', 'models.json'
)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def load_json_config(file_path):
    """加载JSON配置文件"""
    try:
        if not os.path.exists(file_path):
            current_app.logger.error(f"配置文件不存在: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"加载配置文件失败 {file_path}: {str(e)}")
        return None


def save_json_config(file_path, config_data):
    """保存JSON配置文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        current_app.logger.error(f"保存配置文件失败 {file_path}: {str(e)}")
        return False


def validate_prompts_config(config_data):
    """验证提示词配置格式"""
    if not isinstance(config_data, dict):
        return False, "配置必须是JSON对象"
    
    if 'prompts' not in config_data:
        return False, "缺少prompts字段"
    
    if not isinstance(config_data['prompts'], dict):
        return False, "prompts字段必须是对象"
    
    # 验证每个提示词模板
    for key, prompt in config_data['prompts'].items():
        if not isinstance(prompt, dict):
            return False, f"提示词模板 {key} 必须是对象"
        
        if 'system' not in prompt or 'user_template' not in prompt:
            return False, f"提示词模板 {key} 缺少必需字段 system 或 user_template"
    
    # 验证默认提示词
    if 'default_prompt' in config_data:
        default_prompt = config_data['default_prompt']
        if default_prompt and default_prompt not in config_data['prompts']:
            return False, f"默认提示词 {default_prompt} 不存在"
    
    return True, "配置格式正确"


def validate_models_config(config_data):
    """验证模型配置格式"""
    if not isinstance(config_data, dict):
        return False, "配置必须是JSON对象"
    
    if 'models' not in config_data:
        return False, "缺少models字段"
    
    if not isinstance(config_data['models'], dict):
        return False, "models字段必须是对象"
    
    # 验证每个模型配置
    for key, model in config_data['models'].items():
        if not isinstance(model, dict):
            return False, f"模型配置 {key} 必须是对象"
        
        required_fields = ['name', 'base_url', 'model', 'api_key_env', 'timeout', 'max_retries', 'generation_config']
        for field in required_fields:
            if field not in model:
                return False, f"模型配置 {key} 缺少必需字段 {field}"
        
        # 验证generation_config
        gen_config = model['generation_config']
        if not isinstance(gen_config, dict):
            return False, f"模型配置 {key} 的 generation_config 必须是对象"
        
        gen_required_fields = ['max_tokens', 'temperature', 'top_p', 'frequency_penalty', 'presence_penalty']
        for field in gen_required_fields:
            if field not in gen_config:
                return False, f"模型配置 {key} 的 generation_config 缺少必需字段 {field}"
    
    # 验证默认模型
    if 'default_model' in config_data:
        default_model = config_data['default_model']
        if default_model and default_model not in config_data['models']:
            return False, f"默认模型 {default_model} 不存在"
    
    return True, "配置格式正确"


@ai_config_bp.route('/prompts', methods=['GET'])
@jwt_required()
def get_prompts_config():
    """获取提示词配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未认证'
            }), 401
        
        config_data = load_json_config(PROMPTS_CONFIG_PATH)
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
            'message': '获取提示词配置失败'
        }), 500


@ai_config_bp.route('/prompts', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_prompts_config():
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
        if not save_json_config(PROMPTS_CONFIG_PATH, config_data):
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
            'message': '更新提示词配置失败'
        }), 500


@ai_config_bp.route('/models', methods=['GET'])
@jwt_required()
def get_models_config():
    """获取模型配置"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未认证'
            }), 401
        
        config_data = load_json_config(MODELS_CONFIG_PATH)
        if config_data is None:
            return jsonify({
                'success': False,
                'message': '加载模型配置失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': config_data,
            'message': '获取模型配置成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取模型配置失败'
        }), 500


@ai_config_bp.route('/models', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_models_config():
    """更新模型配置"""
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
        is_valid, error_message = validate_models_config(config_data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': f'配置格式错误: {error_message}'
            }), 400
        
        # 保存配置
        if not save_json_config(MODELS_CONFIG_PATH, config_data):
            return jsonify({
                'success': False,
                'message': '保存模型配置失败'
            }), 500
        
        current_app.logger.info(f"用户 {current_user.username} 更新了模型配置")
        
        return jsonify({
            'success': True,
            'message': '模型配置更新成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"更新模型配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新模型配置失败'
        }), 500


@ai_config_bp.route('/validate/<config_type>', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def validate_config(config_type):
    """验证配置格式"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未认证'
            }), 401
        
        if config_type not in ['prompts', 'models']:
            return jsonify({
                'success': False,
                'message': '不支持的配置类型'
            }), 400
        
        config_data = request.get_json()
        if not config_data:
            return jsonify({
                'success': False,
                'message': '请提供配置数据'
            }), 400
        
        # 根据类型验证配置
        if config_type == 'prompts':
            is_valid, error_message = validate_prompts_config(config_data)
        else:
            is_valid, error_message = validate_models_config(config_data)
        
        return jsonify({
            'success': is_valid,
            'message': error_message,
            'valid': is_valid
        })
        
    except Exception as e:
        current_app.logger.error(f"验证配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '验证配置失败'
        }), 500