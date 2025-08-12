#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI内容生成配置模块
管理AI模型相关配置，支持多模型切换

模型配置存储在models.json文件中，支持动态加载和切换。
当更换模型时，请确保同时更新对应的API Key环境变量。

使用示例:
    # 使用默认模型
    config = AIConfig()
    
    # 指定特定模型
    config = AIConfig(model_name="doubao")
    
    # 切换模型
    config.switch_model("other_model")
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class AIConfig:
    """AI配置管理类"""
    
    def __init__(self, model_name: Optional[str] = None):
        """初始化AI配置
        
        Args:
            model_name: 指定使用的模型名称，如果为None则使用默认模型
        """
        self._models_config = self._load_models_config()
        self._prompts_config = self._load_prompts_config()
        self._current_model = model_name or self._models_config.get("default_model", "doubao")
        self._config = self._load_default_config()
        self._load_env_config()
    
    def _load_models_config(self) -> Dict[str, Any]:
        """从JSON文件加载模型配置"""
        config_dir = Path(__file__).parent
        models_file = config_dir / "models.json"
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"警告：无法加载模型配置文件 {models_file}: {e}")
            # 返回默认的豆包配置
            return {
                "models": {
                    "doubao": {
                        "name": "豆包模型",
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "model": "doubao-seed-1-6-250615",
                        "api_key_env": "ARK_API_KEY",
                        "timeout": 60,
                        "max_retries": 3,
                        "generation_config": {
                            "max_tokens": 2000,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "frequency_penalty": 0.0,
                            "presence_penalty": 0.0
                        }
                    }
                },
                "default_model": "doubao"
            }
    
    def _load_prompts_config(self) -> Dict[str, Any]:
        """从JSON文件加载提示词配置"""
        config_dir = Path(__file__).parent
        prompts_file = config_dir / "prompts.json"
        
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"警告：无法加载提示词配置文件 {prompts_file}: {e}")
            # 返回默认的文案生成提示词
            return {
                "prompts": {
                    "article_generation": {
                        "system": "你是一个专业的内容创作者，擅长根据给定的素材生成高质量的文章。",
                        "user_template": "请根据以下内容生成一篇文章：\n\n标题：{title}\n\n内容描述：{description}\n\n图片信息：{images}\n\n评论信息：{comments}\n\n请生成一篇结构清晰、内容丰富的文章。"
                    }
                },
                "default_prompt": "article_generation"
            }
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        # 获取当前模型配置
        model_config = self._get_current_model_config()
        
        return {
            # 模型配置（从JSON文件加载）
            "ark": {
                "base_url": model_config.get("base_url", ""),
                "model": model_config.get("model", ""),
                "api_key": None,
                "timeout": model_config.get("timeout", 60),
                "max_retries": model_config.get("max_retries", 3)
            },
            # 内容生成配置（从模型配置中获取）
            "generation": model_config.get("generation_config", {
                "max_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }),
            # 提示词模板配置（从JSON文件加载）
            "prompts": self._prompts_config.get("prompts", {})
        }
    
    def _get_current_model_config(self) -> Dict[str, Any]:
        """获取当前模型的配置"""
        models = self._models_config.get("models", {})
        return models.get(self._current_model, {})
    
    def _load_env_config(self):
        """从环境变量加载配置"""
        # 获取当前模型配置
        model_config = self._get_current_model_config()
        
        # 加载API Key（根据模型配置中的api_key_env字段）
        api_key_env = model_config.get("api_key_env", "ARK_API_KEY")
        api_key = os.environ.get(api_key_env)
        if api_key:
            self._config["ark"]["api_key"] = api_key
        
        # 加载其他环境变量配置
        env_mappings = {
            "ARK_BASE_URL": ("ark", "base_url"),
            "ARK_MODEL": ("ark", "model"),
            "ARK_TIMEOUT": ("ark", "timeout"),
            "ARK_MAX_RETRIES": ("ark", "max_retries"),
            "AI_MAX_TOKENS": ("generation", "max_tokens"),
            "AI_TEMPERATURE": ("generation", "temperature"),
            "AI_TOP_P": ("generation", "top_p")
        }
        
        for env_key, (section, config_key) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value:
                # 尝试转换数据类型
                try:
                    if config_key in ["timeout", "max_retries", "max_tokens"]:
                        env_value = int(env_value)
                    elif config_key in ["temperature", "top_p", "frequency_penalty", "presence_penalty"]:
                        env_value = float(env_value)
                    self._config[section][config_key] = env_value
                except (ValueError, TypeError):
                    # 如果转换失败，保持原始字符串值
                    self._config[section][config_key] = env_value
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称，如果为None则返回整个节
            default: 默认值
            
        Returns:
            配置值
        """
        if section not in self._config:
            return default
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """设置配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称
            value: 配置值
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def get_ark_config(self) -> Dict[str, Any]:
        """获取豆包模型配置"""
        return self.get("ark", default={})
    
    def get_generation_config(self) -> Dict[str, Any]:
        """获取内容生成配置"""
        return self.get("generation", default={})
    
    def get_prompt_template(self, prompt_type: Optional[str] = None) -> Dict[str, str]:
        """获取提示词模板
        
        Args:
            prompt_type: 提示词类型，如果为None则使用默认提示词
            
        Returns:
            包含system和user_template的字典
        """
        if prompt_type is None:
            prompt_type = self._prompts_config.get("default_prompt", "article_generation")
        
        prompts = self.get("prompts", default={})
        return prompts.get(prompt_type, {})
    
    def get_available_prompts(self) -> Dict[str, str]:
        """获取可用的提示词模板列表
        
        Returns:
            提示词类型到描述的映射
        """
        prompts = self._prompts_config.get("prompts", {})
        # 简单返回提示词类型，可以后续扩展为包含描述
        return {key: key for key in prompts.keys()}
    
    def get_default_prompt_type(self) -> str:
        """获取默认提示词类型"""
        return self._prompts_config.get("default_prompt", "article_generation")
    
    def validate_config(self) -> bool:
        """验证配置是否完整
        
        Returns:
            配置是否有效
        """
        ark_config = self.get_ark_config()
        
        # 检查必需的配置项
        required_fields = ["base_url", "model", "api_key"]
        for field in required_fields:
            if not ark_config.get(field):
                return False
        
        return True
    
    def get_available_models(self) -> Dict[str, str]:
        """获取可用的模型列表
        
        Returns:
            模型名称到模型显示名称的映射
        """
        models = self._models_config.get("models", {})
        return {name: config.get("name", name) for name, config in models.items()}
    
    def get_current_model(self) -> str:
        """获取当前使用的模型名称"""
        return self._current_model
    
    def switch_model(self, model_name: str):
        """切换模型
        
        Args:
            model_name: 要切换到的模型名称
            
        Raises:
            ValueError: 如果模型不存在
        """
        models = self._models_config.get("models", {})
        if model_name not in models:
            available = list(models.keys())
            raise ValueError(f"模型 '{model_name}' 不存在。可用模型: {available}")
        
        self._current_model = model_name
        # 重新加载配置
        self._prompts_config = self._load_prompts_config()
        self._config = self._load_default_config()
        self._load_env_config()
        
        # 提醒用户检查API Key
        model_config = self._get_current_model_config()
        api_key_env = model_config.get("api_key_env", "ARK_API_KEY")
        print(f"已切换到模型: {model_config.get('name', model_name)}")
        print(f"请确保已设置正确的API Key环境变量: {api_key_env}")
    
    @property
    def ark_api_key(self) -> Optional[str]:
        """获取API Key"""
        return self.get("ark", "api_key")
    
    @property
    def ark_base_url(self) -> str:
        """获取API Base URL"""
        return self.get("ark", "base_url", "")
    
    @property
    def ark_model(self) -> str:
        """获取模型名称"""
        return self.get("ark", "model", "")
    
    @property
    def max_tokens(self) -> int:
        """获取最大token数"""
        return self.get("generation", "max_tokens", 2000)
    
    @property
    def temperature(self) -> float:
        """获取温度参数"""
        return self.get("generation", "temperature", 0.7)
    
    @property
    def top_p(self) -> float:
        """获取top_p参数"""
        return self.get("generation", "top_p", 0.9)
    
    def validate(self):
        """验证配置
        
        Raises:
            ValueError: 当必需的配置项缺失时
        """
        ark_config = self.get_ark_config()
        
        # 检查API Key
        if not ark_config.get("api_key"):
            model_config = self._get_current_model_config()
            api_key_env = model_config.get("api_key_env", "ARK_API_KEY")
            raise ValueError(f"未找到API Key。请设置环境变量: {api_key_env}")
        
        # 检查其他必需配置
        required_fields = ["base_url", "model"]
        for field in required_fields:
            if not ark_config.get(field):
                raise ValueError(f"配置项 '{field}' 不能为空")
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()


# 全局配置实例（使用默认模型）
ai_config = AIConfig()