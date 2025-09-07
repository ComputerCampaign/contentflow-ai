#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器模块
负责加载和管理模型配置、提示词配置等
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import setup_logger

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 查找.env文件路径（从当前文件向上查找到项目根目录）
    current_dir = Path(__file__).parent
    env_file = None
    for parent in [current_dir] + list(current_dir.parents):
        potential_env = parent / '.env'
        if potential_env.exists():
            env_file = potential_env
            break
    
    if env_file:
        load_dotenv(env_file)
        print(f"ConfigManager已加载环境变量文件: {env_file}")
    else:
        print("ConfigManager未找到.env文件")
except ImportError:
    print("ConfigManager提示: 安装python-dotenv可以自动加载.env文件")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为当前目录
        """
        self.logger = setup_logger(__name__, file_path=True)
        
        self.logger.info("开始初始化配置管理器")
        
        if config_dir:
            self.config_dir = config_dir
            self.logger.debug(f"使用指定的配置目录: {config_dir}")
        else:
            # 默认配置目录为项目根目录下的config文件夹
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_dir = os.path.join(project_root, 'config')
            self.logger.debug(f"使用默认配置目录: {self.config_dir}")
        
        # 配置文件路径
        self.models_config_path = os.path.join(self.config_dir, 'models.json')
        self.prompts_config_path = os.path.join(self.config_dir, 'prompts.json')
        
        self.logger.debug(f"模型配置文件路径: {self.models_config_path}")
        self.logger.debug(f"提示词配置文件路径: {self.prompts_config_path}")
        
        # 检查配置文件是否存在
        if not os.path.exists(self.models_config_path):
            self.logger.warning(f"模型配置文件不存在: {self.models_config_path}")
        if not os.path.exists(self.prompts_config_path):
            self.logger.warning(f"提示词配置文件不存在: {self.prompts_config_path}")
        
        # 缓存配置
        self._models_config = None
        self._prompts_config = None
        
        self.logger.info(f"配置管理器初始化完成，配置目录: {self.config_dir}")
    
    def load_models_config(self) -> Dict[str, Any]:
        """
        加载模型配置
        
        Returns:
            模型配置字典
        """
        if self._models_config is None:
            self.logger.info(f"开始加载模型配置文件: {self.models_config_path}")
            
            try:
                # 检查文件大小
                file_size = os.path.getsize(self.models_config_path)
                self.logger.debug(f"模型配置文件大小: {file_size} bytes")
                
                with open(self.models_config_path, 'r', encoding='utf-8') as f:
                    self._models_config = json.load(f)
                
                # 记录配置详情
                models_count = len(self._models_config.get('models', {}))
                default_model = self._models_config.get('default_model', 'unknown')
                
                self.logger.info(f"模型配置加载成功，包含 {models_count} 个模型，默认模型: {default_model}")
                self.logger.debug(f"模型配置内容: {json.dumps(self._models_config, ensure_ascii=False, indent=2)}")
                
            except FileNotFoundError:
                self.logger.error(f"模型配置文件不存在: {self.models_config_path}")
                raise
            except json.JSONDecodeError as e:
                self.logger.error(f"模型配置文件格式错误: {e}")
                self.logger.error(f"文件路径: {self.models_config_path}")
                raise
            except Exception as e:
                self.logger.error(f"加载模型配置失败: {e}")
                raise
        else:
            self.logger.debug("使用缓存的模型配置")
        
        return self._models_config
    
    def load_prompts_config(self) -> Dict[str, Any]:
        """
        加载提示词配置
        
        Returns:
            提示词配置字典
        """
        if self._prompts_config is None:
            self.logger.info(f"开始加载提示词配置文件: {self.prompts_config_path}")
            
            try:
                # 检查文件大小
                file_size = os.path.getsize(self.prompts_config_path)
                self.logger.debug(f"提示词配置文件大小: {file_size} bytes")
                
                with open(self.prompts_config_path, 'r', encoding='utf-8') as f:
                    self._prompts_config = json.load(f)
                
                # 记录配置详情
                prompts_count = len(self._prompts_config.get('prompts', {}))
                default_prompt = self._prompts_config.get('default_prompt', 'unknown')
                
                self.logger.info(f"提示词配置加载成功，包含 {prompts_count} 个提示词模板，默认提示词: {default_prompt}")
                self.logger.debug(f"提示词配置内容: {json.dumps(self._prompts_config, ensure_ascii=False, indent=2)}")
                
            except FileNotFoundError:
                self.logger.error(f"提示词配置文件不存在: {self.prompts_config_path}")
                raise
            except json.JSONDecodeError as e:
                self.logger.error(f"提示词配置文件格式错误: {e}")
                self.logger.error(f"文件路径: {self.prompts_config_path}")
                raise
            except Exception as e:
                self.logger.error(f"加载提示词配置失败: {e}")
                raise
        else:
            self.logger.debug("使用缓存的提示词配置")
        
        return self._prompts_config
    
    def get_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """
        获取指定模型的配置
        
        Args:
            model_name: 模型名称，为None时返回默认模型配置
        
        Returns:
            模型配置字典
        """
        self.logger.debug(f"请求获取模型配置，指定模型: {model_name}")
        
        models_config = self.load_models_config()
        
        if model_name is None:
            model_name = models_config.get('default_model', 'doubao')
            self.logger.debug(f"使用默认模型: {model_name}")
        
        available_models = list(models_config.get('models', {}).keys())
        self.logger.debug(f"可用模型列表: {available_models}")
        
        if model_name not in models_config.get('models', {}):
            self.logger.error(f"模型 '{model_name}' 不存在，可用模型: {available_models}")
            raise ValueError(f"模型 '{model_name}' 不存在，可用模型: {available_models}")
        
        model_config = models_config['models'][model_name].copy()
        model_config['model_name'] = model_name
        
        self.logger.info(f"成功获取模型配置: {model_name}")
        self.logger.debug(f"模型配置详情: {json.dumps(model_config, ensure_ascii=False, indent=2)}")
        return model_config
    
    def get_content_model_config(self) -> Dict[str, Any]:
        """
        获取内容生成模型配置
        
        Returns:
            内容生成模型配置
        """
        models_config = self.load_models_config()
        content_model = models_config.get('default_content_model', 'doubao_content')
        return self.get_model_config(content_model)
    
    def get_video_model_config(self) -> Dict[str, Any]:
        """
        获取视频生成模型配置
        
        Returns:
            视频生成模型配置
        """
        models_config = self.load_models_config()
        video_model = models_config.get('default_video_model', 'doubao_video')
        return self.get_model_config(video_model)
    
    def get_prompt_config(self, prompt_type: str = None) -> Dict[str, Any]:
        """
        获取指定类型的提示词配置
        
        Args:
            prompt_type: 提示词类型，为None时返回默认提示词配置
        
        Returns:
            提示词配置字典
        """
        self.logger.debug(f"请求获取提示词配置，指定提示词: {prompt_type}")
        
        prompts_config = self.load_prompts_config()
        
        if prompt_type is None:
            prompt_type = prompts_config.get('default_prompt', 'multi_platform_content')
            self.logger.debug(f"使用默认提示词: {prompt_type}")
        
        available_prompts = list(prompts_config.get('prompts', {}).keys())
        self.logger.debug(f"可用提示词列表: {available_prompts}")
        
        if prompt_type not in prompts_config.get('prompts', {}):
            self.logger.error(f"提示词类型 '{prompt_type}' 不存在，可用类型: {available_prompts}")
            raise ValueError(f"提示词类型 '{prompt_type}' 不存在，可用类型: {available_prompts}")
        
        prompt_config = prompts_config['prompts'][prompt_type].copy()
        prompt_config['prompt_type'] = prompt_type
        
        self.logger.info(f"成功获取提示词配置: {prompt_type}")
        self.logger.debug(f"提示词配置详情: {json.dumps(prompt_config, ensure_ascii=False, indent=2)}")
        return prompt_config
    
    def get_multi_platform_prompt_config(self) -> Dict[str, Any]:
        """
        获取多平台内容生成提示词配置
        
        Returns:
            多平台提示词配置
        """
        return self.get_prompt_config('multi_platform_content')
    
    def get_api_key(self, model_name: str = None) -> str:
        """
        获取API密钥
        
        Args:
            model_name: 模型名称
        
        Returns:
            API密钥
        """
        self.logger.debug(f"请求获取API密钥，模型: {model_name}")
        
        model_config = self.get_model_config(model_name)
        api_key_env = model_config.get('api_key_env')
        
        self.logger.debug(f"API密钥环境变量名: {api_key_env}")
        
        if not api_key_env:
            self.logger.error(f"模型 '{model_name}' 未配置API密钥环境变量")
            raise ValueError(f"模型 '{model_name}' 未配置API密钥环境变量")
        
        api_key = os.getenv(api_key_env)
        if not api_key:
            self.logger.error(f"环境变量 '{api_key_env}' 未设置或为空")
            raise ValueError(f"环境变量 '{api_key_env}' 未设置或为空")
        
        # 记录API密钥长度（不记录实际内容）
        key_length = len(api_key) if api_key else 0
        self.logger.info(f"成功获取API密钥，长度: {key_length} 字符")
        
        return api_key
    
    def get_base_url(self, model_name: str = None) -> str:
        """
        获取API基础URL
        
        Args:
            model_name: 模型名称
        
        Returns:
            API基础URL
        """
        model_config = self.get_model_config(model_name)
        return model_config.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')
    
    def get_generation_config(self, model_name: str = None) -> Dict[str, Any]:
        """
        获取生成配置
        
        Args:
            model_name: 模型名称
        
        Returns:
            生成配置字典
        """
        model_config = self.get_model_config(model_name)
        return model_config.get('generation_config', {})
    
    def get_retry_config(self, model_name: str = None) -> Dict[str, Any]:
        """
        获取重试配置
        
        Args:
            model_name: 模型名称
        
        Returns:
            重试配置字典
        """
        model_config = self.get_model_config(model_name)
        return {
            'max_retries': model_config.get('max_retries', 3),
            'retry_delay': model_config.get('retry_delay', 1.0)
        }
    
    def validate_config(self) -> bool:
        """
        验证配置文件的完整性
        
        Returns:
            验证是否通过
        """
        self.logger.info("开始验证配置文件完整性")
        
        try:
            # 验证模型配置
            self.logger.debug("开始验证模型配置")
            models_config = self.load_models_config()
            
            # 检查必需字段
            if 'models' not in models_config:
                self.logger.error("模型配置缺少 'models' 字段")
                return False
            
            if 'default_model' not in models_config:
                self.logger.error("模型配置缺少 'default_model' 字段")
                return False
            
            # 检查默认模型是否存在
            default_model = models_config['default_model']
            self.logger.debug(f"验证默认模型: {default_model}")
            if default_model not in models_config['models']:
                self.logger.error(f"默认模型 '{default_model}' 在模型列表中不存在")
                return False
            
            # 检查每个模型的必需字段
            models_count = len(models_config['models'])
            self.logger.debug(f"验证 {models_count} 个模型配置")
            
            for model_name, model_config in models_config['models'].items():
                self.logger.debug(f"验证模型: {model_name}")
                required_fields = ['api_key_env', 'base_url', 'model']
                for field in required_fields:
                    if field not in model_config:
                        self.logger.error(f"模型 '{model_name}' 缺少必需字段: {field}")
                        return False
                self.logger.debug(f"模型 '{model_name}' 验证通过")
            
            self.logger.info("模型配置验证通过")
            
            # 验证提示词配置
            self.logger.debug("开始验证提示词配置")
            prompts_config = self.load_prompts_config()
            
            # 检查必需字段
            if 'prompts' not in prompts_config:
                self.logger.error("提示词配置缺少 'prompts' 字段")
                return False
            
            if 'default_prompt' not in prompts_config:
                self.logger.error("提示词配置缺少 'default_prompt' 字段")
                return False
            
            # 检查默认提示词是否存在
            default_prompt = prompts_config['default_prompt']
            self.logger.debug(f"验证默认提示词: {default_prompt}")
            if default_prompt not in prompts_config['prompts']:
                self.logger.error(f"默认提示词 '{default_prompt}' 在提示词列表中不存在")
                return False
            
            # 检查每个提示词的必需字段
            prompts_count = len(prompts_config['prompts'])
            self.logger.debug(f"验证 {prompts_count} 个提示词配置")
            
            for prompt_name, prompt_config in prompts_config['prompts'].items():
                self.logger.debug(f"验证提示词: {prompt_name}")
                if 'template' not in prompt_config:
                    self.logger.error(f"提示词 '{prompt_name}' 缺少 'template' 字段")
                    return False
                self.logger.debug(f"提示词 '{prompt_name}' 验证通过")
            
            self.logger.info("提示词配置验证通过")
            self.logger.info("配置验证完全通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def reload_config(self):
        """
        重新加载配置文件
        """
        self.logger.info("开始重新加载配置")
        
        # 清除缓存
        old_models_config = self._models_config is not None
        old_prompts_config = self._prompts_config is not None
        
        self._models_config = None
        self._prompts_config = None
        
        self.logger.debug(f"清除模型配置缓存: {old_models_config}")
        self.logger.debug(f"清除提示词配置缓存: {old_prompts_config}")
        
        # 重新加载配置以验证
        try:
            self.load_models_config()
            self.load_prompts_config()
            self.logger.info("配置重新加载成功")
        except Exception as e:
            self.logger.error(f"配置重新加载失败: {e}")
            raise
    
    def get_available_models(self) -> list:
        """
        获取可用的模型列表
        
        Returns:
            模型名称列表
        """
        models_config = self.load_models_config()
        return list(models_config.get('models', {}).keys())
    
    def get_available_prompts(self) -> list:
        """
        获取可用的提示词类型列表
        
        Returns:
            提示词类型列表
        """
        prompts_config = self.load_prompts_config()
        return list(prompts_config.get('prompts', {}).keys())
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        获取模型信息摘要
        
        Args:
            model_name: 模型名称
        
        Returns:
            模型信息字典
        """
        model_config = self.get_model_config(model_name)
        
        return {
            'model_name': model_config['model_name'],
            'model_id': model_config.get('model', 'unknown'),
            'base_url': model_config.get('base_url', ''),
            'has_api_key': bool(model_config.get('api_key_env')),
            'max_retries': model_config.get('max_retries', 3),
            'generation_config': model_config.get('generation_config', {})
        }
    
    def get_prompt_info(self, prompt_type: str = None) -> Dict[str, Any]:
        """
        获取提示词信息摘要
        
        Args:
            prompt_type: 提示词类型
        
        Returns:
            提示词信息字典
        """
        prompt_config = self.get_prompt_config(prompt_type)
        
        return {
            'prompt_type': prompt_config['prompt_type'],
            'description': prompt_config.get('description', ''),
            'required_variables': prompt_config.get('required_variables', []),
            'template_length': len(prompt_config.get('template', ''))
        }


if __name__ == "__main__":
    # 测试代码
    import tempfile
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 创建测试配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 创建测试模型配置
            models_config = {
                "models": {
                    "test_model": {
                        "api_key_env": "TEST_API_KEY",
                        "base_url": "https://test.api.com",
                        "model": "test-model-v1",
                        "max_retries": 3,
                        "generation_config": {
                            "temperature": 0.7,
                            "max_tokens": 2000
                        }
                    }
                },
                "default_model": "test_model"
            }
            
            models_file = os.path.join(temp_dir, 'models.json')
            with open(models_file, 'w', encoding='utf-8') as f:
                json.dump(models_config, f, ensure_ascii=False, indent=2)
            
            # 创建测试提示词配置
            prompts_config = {
                "prompts": {
                    "test_prompt": {
                        "description": "测试提示词",
                        "template": "请根据以下信息生成内容：{content}",
                        "required_variables": ["content"]
                    }
                },
                "default_prompt": "test_prompt"
            }
            
            prompts_file = os.path.join(temp_dir, 'prompts.json')
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_config, f, ensure_ascii=False, indent=2)
            
            # 测试配置管理器
            print("\n测试配置管理器...")
            config_manager = ConfigManager(temp_dir)
            
            # 测试验证配置
            print(f"配置验证: {config_manager.validate_config()}")
            
            # 测试获取模型配置
            print("\n测试获取模型配置...")
            model_config = config_manager.get_model_config()
            print(f"模型配置: {json.dumps(model_config, ensure_ascii=False, indent=2)}")
            
            # 测试获取提示词配置
            print("\n测试获取提示词配置...")
            prompt_config = config_manager.get_prompt_config()
            print(f"提示词配置: {json.dumps(prompt_config, ensure_ascii=False, indent=2)}")
            
            # 测试获取可用列表
            print(f"\n可用模型: {config_manager.get_available_models()}")
            print(f"可用提示词: {config_manager.get_available_prompts()}")
            
    except Exception as e:
        print(f"测试失败: {e}")