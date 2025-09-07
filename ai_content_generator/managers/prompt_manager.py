#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理器模块
负责加载和管理AI内容生成的提示词模板
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import setup_logger


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化提示词管理器
        
        Args:
            config_dir: 配置文件目录路径
        """
        if config_dir is None:
            # 默认使用项目根目录下的config文件夹
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            self.logger = setup_logger(__name__, file_path=True)
            self.logger.debug(f"使用默认配置目录: {config_dir}")
        else:
            self.logger = setup_logger(__name__, file_path=True)
            self.logger.debug(f"使用指定配置目录: {config_dir}")
        
        self.config_dir = Path(config_dir)
        self.prompts_file = self.config_dir / "prompts.json"
        self.logger.debug(f"提示词配置文件路径: {self.prompts_file}")
        
        self.prompts_config = self._load_prompts_config()
        
        prompt_types = list(self.prompts_config.get('prompts', {}).keys())
        self.logger.info(f"提示词管理器初始化完成，配置目录: {self.config_dir}，可用提示词类型: {prompt_types}")
    
    def _load_prompts_config(self) -> Dict[str, Any]:
        """
        加载提示词配置文件
        
        Returns:
            提示词配置字典
        """
        try:
            self.logger.debug(f"开始加载提示词配置文件: {self.prompts_file}")
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            prompt_count = len(config.get('prompts', {}))
            default_prompt = config.get('default_prompt', 'None')
            self.logger.info(f"提示词配置加载成功，包含 {prompt_count} 个提示词类型，默认类型: {default_prompt}")
            
            return config
            
        except FileNotFoundError:
            self.logger.error(f"提示词配置文件不存在: {self.prompts_file}")
            raise FileNotFoundError(f"提示词配置文件不存在: {self.prompts_file}")
        except json.JSONDecodeError as e:
            self.logger.error(f"提示词配置文件格式错误: {e}")
            raise ValueError(f"提示词配置文件格式错误: {e}")
    
    def get_prompt_template(self, prompt_type: str = None) -> Dict[str, str]:
        """
        获取指定类型的提示词模板
        
        Args:
            prompt_type: 提示词类型，如果为None则使用默认类型
        
        Returns:
            包含system和user_template的字典
        """
        if prompt_type is None:
            prompt_type = self.prompts_config.get('default_prompt', 'multi_platform_content')
            self.logger.debug(f"使用默认提示词类型: {prompt_type}")
        else:
            self.logger.debug(f"使用指定提示词类型: {prompt_type}")
        
        prompts = self.prompts_config.get('prompts', {})
        if prompt_type not in prompts:
            available_types = list(prompts.keys())
            self.logger.error(f"未找到提示词类型 '{prompt_type}'，可用类型: {available_types}")
            raise ValueError(f"未找到提示词类型 '{prompt_type}'，可用类型: {available_types}")
        
        template = prompts[prompt_type]
        system_length = len(template.get('system', ''))
        user_template_length = len(template.get('user_template', ''))
        self.logger.debug(f"获取提示词模板 '{prompt_type}'，系统提示词长度: {system_length}，用户模板长度: {user_template_length}")
        
        return template
    
    def build_prompt(self, prompt_type: str = None, **kwargs) -> Dict[str, str]:
        """
        构建完整的提示词
        
        Args:
            prompt_type: 提示词类型
            **kwargs: 模板变量
        
        Returns:
            包含system和user的完整提示词字典
        """
        self.logger.debug(f"开始构建提示词，类型: {prompt_type}，变量数量: {len(kwargs)}")
        
        template = self.get_prompt_template(prompt_type)
        
        # 获取系统提示词
        system_prompt = template.get('system', '')
        
        # 构建用户提示词，替换模板变量
        user_template = template.get('user_template', '')
        self.logger.debug(f"模板变量: {list(kwargs.keys())}")
        
        user_prompt = self._replace_template_variables(user_template, **kwargs)
        
        result = {
            'system': system_prompt,
            'user': user_prompt
        }
        
        system_length = len(system_prompt)
        user_length = len(user_prompt)
        self.logger.info(f"提示词构建完成，类型: {prompt_type}，系统提示词长度: {system_length}，用户提示词长度: {user_length}")
        
        return result
    
    def _replace_template_variables(self, template: str, **kwargs) -> str:
        """
        替换模板中的变量
        
        Args:
            template: 模板字符串
            **kwargs: 变量字典
        
        Returns:
            替换后的字符串
        """
        try:
            self.logger.debug(f"开始替换模板变量，模板长度: {len(template)}，变量: {list(kwargs.keys())}")
            
            result = template.format(**kwargs)
            
            self.logger.debug(f"模板变量替换完成，结果长度: {len(result)}")
            return result
            
        except KeyError as e:
            missing_var = str(e).strip("'")
            self.logger.error(f"模板变量缺失: {missing_var}，可用变量: {list(kwargs.keys())}")
            raise ValueError(f"模板变量缺失: {missing_var}")
    
    def get_available_prompt_types(self) -> list:
        """
        获取所有可用的提示词类型
        
        Returns:
            提示词类型列表
        """
        return list(self.prompts_config.get('prompts', {}).keys())
    
    def get_default_prompt_type(self) -> str:
        """
        获取默认提示词类型
        
        Returns:
            默认提示词类型
        """
        return self.prompts_config.get('default_prompt', 'multi_platform_content')
    
    def validate_template_variables(self, prompt_type: str = None) -> list:
        """
        验证模板中需要的变量
        
        Args:
            prompt_type: 提示词类型
        
        Returns:
            需要的变量列表
        """
        template = self.get_prompt_template(prompt_type)
        user_template = template.get('user_template', '')
        
        # 简单的变量提取，查找 {variable} 格式的变量
        import re
        variables = re.findall(r'\{(\w+)\}', user_template)
        return list(set(variables))  # 去重


if __name__ == "__main__":
    # 测试代码
    try:
        pm = PromptManager()
        print("可用的提示词类型:", pm.get_available_prompt_types())
        print("默认提示词类型:", pm.get_default_prompt_type())
        
        # 测试多平台内容模板
        variables = pm.validate_template_variables('multi_platform_content')
        print("多平台内容模板需要的变量:", variables)
        
        # 构建示例提示词
        test_data = {
            'title': '测试标题',
            'description': '测试描述',
            'url': 'https://example.com',
            'comments_count': 100,
            'comments': '用户评论示例'
        }
        
        prompt = pm.build_prompt('multi_platform_content', **test_data)
        print("\n构建的提示词:")
        print(f"System: {prompt['system'][:100]}...")
        print(f"User: {prompt['user'][:200]}...")
        
    except Exception as e:
        print(f"测试失败: {e}")