#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台文案生成器模块
实现一次API调用生成抖音、小红书、微信视频号三个平台的差异化内容
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from openai import OpenAI
from ..managers.prompt_manager import PromptManager
from ..managers.config_manager import ConfigManager
from ..utils.logger import setup_logger


class MultiPlatformGenerator:
    """多平台文案生成器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化多平台文案生成器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config = ConfigManager(config_dir)
        self.prompt_manager = PromptManager(config_dir)
        self.client = None
        self.logger = setup_logger(__name__, file_path=True)
        
        # 初始化OpenAI客户端
        self._init_client()
    
    def _init_client(self):
        """
        初始化OpenAI客户端
        """
        try:
            # 获取内容生成模型配置
            model_config = self.config.get_model_config('doubao_content')
            
            # 获取API密钥
            api_key_env = model_config['api_key_env']
            api_key = os.getenv(api_key_env)
            if not api_key:
                raise ValueError(f"环境变量 '{api_key_env}' 未设置或为空")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=model_config['base_url']
            )
            
            self.model_name = model_config['model']
            self.generation_config = model_config.get('generation_config', {})
            self.max_retries = model_config.get('max_retries', 3)
            self.timeout = model_config.get('timeout', 60)
            
            self.logger.info(f"初始化多平台文案生成器成功，使用模型: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"初始化多平台文案生成器失败: {e}")
            raise
    
    def generate_multi_platform_content(self, crawler_data: Dict[str, Any], 
                                      custom_prompt: str = None, task_id: str = None) -> Dict[str, Any]:
        """
        生成多平台内容
        
        Args:
            crawler_data: 爬虫数据
            custom_prompt: 自定义提示词类型
            task_id: 任务ID，用于日志追踪
        
        Returns:
            包含所有平台内容的字典
        """
        generation_id = f"gen_{int(time.time())}"
        log_context = f"[task_id={task_id or 'unknown'}][generation_id={generation_id}]"
        
        try:
            self.logger.info(f"{log_context} 开始生成多平台内容")
            
            # 构建提示词
            prompt_data = self._prepare_prompt_data(crawler_data)
            prompt_type = custom_prompt or 'multi_platform_content'
            
            self.logger.info(f"{log_context} 使用提示词类型: {prompt_type}")
            self.logger.debug(f"{log_context} 提示词数据: {json.dumps(prompt_data, ensure_ascii=False, indent=2)}")
            
            prompt = self.prompt_manager.build_prompt(prompt_type, **prompt_data)
            
            # 记录完整的提示词内容
            self.logger.info(f"{log_context} 构建的系统提示词长度: {len(prompt.get('system', ''))} 字符")
            self.logger.info(f"{log_context} 构建的用户提示词长度: {len(prompt.get('user', ''))} 字符")
            self.logger.debug(f"{log_context} 完整系统提示词: {prompt.get('system', '')}")
            self.logger.debug(f"{log_context} 完整用户提示词: {prompt.get('user', '')}")
            
            # 构建API消息
            messages = self._build_messages(prompt, crawler_data)
            
            # 记录API请求信息
            self.logger.info(f"{log_context} API请求消息数量: {len(messages)}")
            self.logger.info(f"{log_context} 包含图片数量: {len([msg for msg in messages if msg.get('role') == 'user' and isinstance(msg.get('content'), list) and any(item.get('type') == 'image_url' for item in msg['content'])])}")
            
            # 调用API生成内容
            response = self._call_api(messages, log_context)
            
            # 解析响应
            content = self._parse_response(response, log_context)
            
            # 验证和格式化结果
            images = crawler_data.get('images', [])
            formatted_content = self._format_multi_platform_content(content, generation_id, images)
            
            self.logger.info(f"{log_context} 多平台内容生成成功，包含平台: {list(formatted_content.get('platforms', {}).keys())}")
            self.logger.info(f"{log_context} 包含图片URL数量: {len(images)}")
            return formatted_content
            
        except Exception as e:
            self.logger.error(f"{log_context} 多平台内容生成失败: {e}")
            raise
    
    def _prepare_prompt_data(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备提示词数据
        
        Args:
            crawler_data: 爬虫数据
        
        Returns:
            格式化的提示词数据
        """
        # 提取基本信息
        title = crawler_data.get('title', '未知标题')
        description = crawler_data.get('description', '无描述')
        url = crawler_data.get('url', '无链接')
        
        # 处理评论信息
        comments = crawler_data.get('comments', [])
        comments_count = len(comments)
        
        # 格式化热门评论（取前5条）
        formatted_comments = self._format_comments(comments[:5])
        
        return {
            'title': title,
            'description': description,
            'url': url,
            'comments_count': comments_count,
            'comments': formatted_comments
        }
    
    def _format_comments(self, comments: List[Dict]) -> str:
        """
        格式化评论信息
        
        Args:
            comments: 评论列表
        
        Returns:
            格式化的评论字符串
        """
        if not comments:
            return "暂无评论"
        
        formatted = []
        for i, comment in enumerate(comments, 1):
            # 兼容不同的评论字段名：text, content
            content = comment.get('text', comment.get('content', '')).strip()
            if content:
                # 限制单条评论长度
                if len(content) > 100:
                    content = content[:100] + "..."
                formatted.append(f"{i}. {content}")
        
        return "\n".join(formatted) if formatted else "暂无有效评论"
    
    def _build_messages(self, prompt: Dict[str, str], 
                       crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        构建API请求消息
        
        Args:
            prompt: 提示词字典
            crawler_data: 爬虫数据
        
        Returns:
            消息列表
        """
        messages = []
        
        # 添加系统消息
        if prompt.get('system'):
            messages.append({
                "role": "system",
                "content": prompt['system']
            })
        
        # 构建用户消息
        user_content = [{
            "type": "text",
            "text": prompt['user']
        }]
        
        # 添加图片信息（如果有）
        images = crawler_data.get('images', [])
        if images:
            # 只取前3张图片，避免token过多
            for image_url in images[:3]:
                if image_url and isinstance(image_url, str):
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    })
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
    
    def _call_api(self, messages: List[Dict[str, Any]], log_context: str = "") -> str:
        """
        调用API生成内容
        
        Args:
            messages: 消息列表
            log_context: 日志上下文
        
        Returns:
            API响应内容
        """
        # 记录API调用详细信息
        self.logger.info(f"{log_context} 开始调用API，模型: {self.model_name}")
        self.logger.info(f"{log_context} 生成配置: {json.dumps(self.generation_config, ensure_ascii=False)}")
        
        # 详细记录完整的prompt内容
        self.logger.info(f"{log_context} {'='*80}")
        self.logger.info(f"{log_context} 【完整PROMPT内容】")
        self.logger.info(f"{log_context} {'='*80}")
        
        total_prompt_chars = 0
        for i, message in enumerate(messages):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            
            self.logger.info(f"{log_context} --- 消息 {i+1}: {role.upper()} ---")
            
            if isinstance(content, str):
                char_count = len(content)
                total_prompt_chars += char_count
                self.logger.info(f"{log_context} 内容长度: {char_count} 字符")
                self.logger.info(f"{log_context} 内容:\n{content}")
            elif isinstance(content, list):
                text_parts = []
                image_count = 0
                for item in content:
                    if item.get('type') == 'text':
                        text_content = item.get('text', '')
                        char_count = len(text_content)
                        total_prompt_chars += char_count
                        text_parts.append(text_content)
                    elif item.get('type') == 'image_url':
                        image_count += 1
                        image_url = item.get('image_url', {}).get('url', '')
                        self.logger.info(f"{log_context} 图片 {image_count}: {image_url}")
                
                if text_parts:
                    combined_text = '\n'.join(text_parts)
                    self.logger.info(f"{log_context} 文本内容长度: {len(combined_text)} 字符")
                    self.logger.info(f"{log_context} 文本内容:\n{combined_text}")
                
                if image_count > 0:
                    self.logger.info(f"{log_context} 包含图片数量: {image_count}")
        
        self.logger.info(f"{log_context} {'='*80}")
        self.logger.info(f"{log_context} 【PROMPT统计信息】总字符数: {total_prompt_chars}")
        self.logger.info(f"{log_context} {'='*80}")
        
        self.logger.debug(f"{log_context} 完整API请求消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    timeout=self.timeout,
                    **self.generation_config
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # 记录API响应详细信息
                self.logger.info(f"{log_context} API调用成功，耗时: {duration:.2f}秒")
                
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    self.logger.info(f"{log_context} Token使用情况 - 输入: {usage.prompt_tokens}, 输出: {usage.completion_tokens}, 总计: {usage.total_tokens}")
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("API返回空内容")
                
                # 详细记录模型返回的原始结果
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} 【AI模型返回结果】")
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} 返回内容长度: {len(content)} 字符")
                self.logger.info(f"{log_context} 返回内容类型: {type(content).__name__}")
                self.logger.info(f"{log_context} --- 完整返回内容 ---")
                self.logger.info(f"{log_context} {content}")
                self.logger.info(f"{log_context} {'='*80}")
                self.logger.info(f"{log_context} 【返回结果统计】字符数: {len(content)}, 行数: {content.count(chr(10)) + 1}")
                self.logger.info(f"{log_context} {'='*80}")
                
                return content
                
            except Exception as e:
                self.logger.warning(f"{log_context} API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"{log_context} API调用最终失败，已重试 {self.max_retries} 次")
                    raise
                
                wait_time = 2 ** attempt
                self.logger.info(f"{log_context} 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)  # 指数退避
    
    def _parse_response(self, response_content: str, log_context: str = "") -> Dict[str, Any]:
        """
        解析API响应内容
        
        Args:
            response_content: API响应内容
            log_context: 日志上下文
        
        Returns:
            解析后的内容字典
        """
        try:
            self.logger.info(f"{log_context} 开始解析API响应")
            
            # 尝试提取JSON部分
            import re
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*({.*?})\s*```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                self.logger.info(f"{log_context} 从代码块中提取JSON内容")
            else:
                # 尝试直接解析整个响应
                json_str = response_content.strip()
                self.logger.info(f"{log_context} 直接解析整个响应内容")
            
            self.logger.debug(f"{log_context} 待解析的JSON字符串: {json_str}")
            
            # 解析JSON
            parsed_content = json.loads(json_str)
            
            self.logger.info(f"{log_context} JSON解析成功，包含字段: {list(parsed_content.keys())}")
            
            # 验证必要的平台字段
            required_platforms = ['douyin', 'xiaohongshu', 'weixin']
            missing_platforms = []
            for platform in required_platforms:
                if platform not in parsed_content:
                    missing_platforms.append(platform)
            
            if missing_platforms:
                self.logger.error(f"{log_context} 缺少平台内容: {missing_platforms}")
                raise ValueError(f"缺少平台内容: {missing_platforms}")
            
            # 检查是否有统一的video_prompt
            video_prompt = parsed_content.get('video_prompt', '')
            if video_prompt:
                self.logger.info(f"{log_context} 发现统一video_prompt，长度: {len(video_prompt)}")
            
            self.logger.info(f"{log_context} 平台内容验证通过，包含平台: {required_platforms}")
            
            # 记录每个平台的内容概要
            for platform in required_platforms:
                if platform in parsed_content:
                    content = parsed_content[platform]
                    if isinstance(content, dict):
                        title_len = len(content.get('title', ''))
                        content_len = len(content.get('content', ''))
                        hashtags_count = len(content.get('hashtags', []))
                        self.logger.info(f"{log_context} 平台 {platform}: 标题长度={title_len}, 内容长度={content_len}, 标签数量={hashtags_count}")
            
            return parsed_content
            
        except json.JSONDecodeError as e:
            self.logger.error(f"{log_context} JSON解析失败: {e}")
            self.logger.error(f"{log_context} 原始响应前500字符: {response_content[:500]}...")
            raise ValueError(f"API响应格式错误，无法解析JSON: {e}")
        except Exception as e:
            self.logger.error(f"{log_context} 响应解析失败: {e}")
            raise
    
    def _format_multi_platform_content(self, content: Dict[str, Any], generation_id: str = None, images: List[str] = None) -> Dict[str, Any]:
        """
        格式化多平台内容
        
        Args:
            content: 原始内容字典
            generation_id: 生成ID
            images: 图片URL列表
        
        Returns:
            格式化后的内容字典
        """
        if not generation_id:
            generation_id = f"gen_{int(time.time())}"
            
        log_context = f"[generation_id={generation_id}]"
        
        self.logger.info(f"{log_context} 开始格式化多平台内容")
        
        formatted = {
            'generation_id': generation_id,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'platforms': {},
            'video_prompt': content.get('video_prompt', ''),
            'images': images or [],  # 添加图片URL列表
            'generation_config': {
                'model': self.model_name,
                **self.generation_config
            }
        }
        
        # 格式化各平台内容
        platforms = ['douyin', 'xiaohongshu', 'weixin']
        for platform in platforms:
            if platform in content:
                platform_content = content[platform]
                formatted_platform = {
                    'title': platform_content.get('title', ''),
                    'content': platform_content.get('content', ''),
                    'hashtags': platform_content.get('hashtags', [])
                }
                formatted['platforms'][platform] = formatted_platform
                
                # 记录格式化后的平台内容统计
                self.logger.info(f"{log_context} 平台 {platform} 格式化完成: 标题={len(formatted_platform['title'])}字符, 内容={len(formatted_platform['content'])}字符, 标签={len(formatted_platform['hashtags'])}个")
                self.logger.debug(f"{log_context} 平台 {platform} 详细内容: {json.dumps(formatted_platform, ensure_ascii=False, indent=2)}")
        
        self.logger.info(f"{log_context} 多平台内容格式化完成，总平台数: {len(formatted['platforms'])}")
        
        return formatted
    
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """
        验证生成的内容是否符合要求
        
        Args:
            content: 生成的内容
        
        Returns:
            验证结果
        """
        try:
            platforms = content.get('platforms', {})
            
            # 检查必要平台
            required_platforms = ['douyin', 'xiaohongshu', 'weixin']
            for platform in required_platforms:
                if platform not in platforms:
                    self.logger.error(f"缺少平台内容: {platform}")
                    return False
                
                platform_content = platforms[platform]
                
                # 检查必要字段
                required_fields = ['title', 'content', 'hashtags']
                for field in required_fields:
                    if field not in platform_content:
                        self.logger.error(f"平台 {platform} 缺少字段: {field}")
                        return False
                
                # 检查内容长度
                title = platform_content['title']
                if not title or len(title.strip()) == 0:
                    self.logger.error(f"平台 {platform} 标题为空")
                    return False
                
                content_text = platform_content['content']
                if not content_text or len(content_text.strip()) == 0:
                    self.logger.error(f"平台 {platform} 内容为空")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"内容验证失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    import os
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        generator = MultiPlatformGenerator()
        
        # 测试数据
        test_data = {
            'title': '如何在工作中保持高效率',
            'description': '分享一些提高工作效率的实用技巧和方法',
            'url': 'https://example.com/efficiency-tips',
            'comments': [
                {'content': '很实用的建议，特别是时间管理部分'},
                {'content': '我试过番茄工作法，确实有效'},
                {'content': '希望能有更多关于团队协作的内容'}
            ],
            'images': ['https://example.com/image1.jpg']
        }
        
        print("开始生成多平台内容...")
        result = generator.generate_multi_platform_content(test_data)
        
        print("\n生成结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 验证内容
        is_valid = generator.validate_content(result)
        print(f"\n内容验证结果: {is_valid}")
        
    except Exception as e:
        print(f"测试失败: {e}")