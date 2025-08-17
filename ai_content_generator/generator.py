#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Generator

This module provides intelligent content generation capabilities using the Doubao model.
It generates text content based on crawler data including metadata and images.
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any

from openai import OpenAI

from ai_content_generator.config import AIConfig
from ai_content_generator.utils.logger import setup_logger
from ai_content_generator.utils.data_loader import DataLoader, CrawlerData

logger = setup_logger(__name__, file_path=__file__)


class AIContentGenerator:
    """AI内容生成器"""
    
    def __init__(self, config: Optional[AIConfig] = None, base_path: str = "crawler_data"):
        """初始化AI内容生成器
        
        Args:
            config: AI配置对象
            base_path: 爬虫数据基础路径
        """
        # 加载配置
        self.config = config or AIConfig()
        
        # 验证配置
        self.config.validate()
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.config.ark_api_key,
            base_url=self.config.ark_base_url
        )
        
        # 初始化数据加载器
        self.data_loader = DataLoader(base_path)
        
        logger.info("AI内容生成器初始化完成")
    
    def generate_from_crawler_data(self, task_name: str, 
                                 custom_prompt: Optional[str] = None,
                                 save_to_file: bool = True) -> Optional[str]:
        """根据爬虫数据生成内容
        
        Args:
            task_name: 任务名称
            custom_prompt: 自定义提示词
            save_to_file: 是否保存到文件
            
        Returns:
            生成的内容，如果失败返回None
        """
        logger.info(f"=== 开始内容生成流程 ===")
        logger.info(f"任务名称: {task_name}")
        logger.info(f"自定义提示词: {'是' if custom_prompt else '否'}")
        logger.info(f"保存到文件: {'是' if save_to_file else '否'}")
        
        # 加载爬虫数据
        logger.info("正在加载爬虫数据...")
        crawler_data = self.data_loader.load_crawler_data(task_name)
        if not crawler_data:
            logger.error(f"无法加载爬虫数据: {task_name}")
            return None
            
        # 记录加载的数据信息
        logger.info(f"数据加载成功: 标题={crawler_data.title}, 评论数={len(crawler_data.comments)}, 图片={'有' if crawler_data.image_url else '无'}")
        
        result = self._generate_content_from_data(crawler_data, custom_prompt)
        
        if result:
            logger.info(f"内容生成成功，输出长度: {len(result)} 字符")
            logger.info(f"完整生成内容:\n{result}")
            
            # 保存生成的内容到文件
            if save_to_file:
                saved_path = self._save_generated_content(task_name, result, custom_prompt)
                if saved_path:
                    logger.info(f"内容已保存到: {saved_path}")
                else:
                    logger.warning("内容保存失败")
        else:
            logger.error("内容生成失败")
            
        logger.info(f"=== 内容生成流程结束 ===")
        return result
    
    def generate_from_data_object(self, crawler_data: CrawlerData, 
                                custom_prompt: Optional[str] = None) -> str:
        """根据爬虫数据对象生成内容
        
        Args:
            crawler_data: 爬虫数据对象
            custom_prompt: 自定义提示词
            
        Returns:
            生成的内容
        """
        return self._generate_content_from_data(crawler_data, custom_prompt)
    
    def _generate_content_from_data(self, crawler_data: CrawlerData, 
                                  custom_prompt: Optional[str] = None) -> str:
        """根据爬虫数据生成内容的核心方法
        
        Args:
            crawler_data: 爬虫数据对象
            custom_prompt: 自定义提示词
            
        Returns:
            生成的内容
        """
        try:
            # 构建提示词
            logger.info("正在构建提示词...")
            prompt = self._build_prompt(crawler_data, custom_prompt)
            logger.info(f"提示词构建完成，长度: {len(prompt)} 字符")
            
            # 构建消息
            logger.info("正在构建API消息...")
            messages = self._build_messages(prompt, crawler_data.image_url)
            
            # 记录最终构建的API消息
            logger.info(f"=== 最终API消息 (共{len(messages)}条) ===")
            import json
            logger.info(json.dumps(messages, ensure_ascii=False, indent=2))
            logger.info(f"=== API消息结束 ===")
            
            # 设置生成参数
            generation_params = {
                'model': self.config.ark_model,
                'messages': messages,
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'top_p': self.config.top_p
            }
            
            logger.info(f"API调用参数:")
            logger.info(f"  - 模型: {generation_params['model']}")
            logger.info(f"  - 最大tokens: {generation_params['max_tokens']}")
            logger.info(f"  - 温度: {generation_params['temperature']}")
            logger.info(f"  - top_p: {generation_params['top_p']}")
            
            logger.info(f"开始调用API生成内容...")
            
            # 调用API，如果图片URL无法访问，则重试不带图片的请求
            try:
                response = self.client.chat.completions.create(**generation_params)
                logger.info("API调用成功")
            except Exception as e:
                if "image_url" in str(e) and "downloading" in str(e):
                    logger.warning(f"图片URL无法访问，尝试不使用图片生成内容: {e}")
                    # 重新构建不包含图片的消息
                    logger.info("重新构建纯文本消息...")
                    messages = self._build_messages(prompt, None)
                    generation_params['messages'] = messages
                    logger.info("重新调用API...")
                    response = self.client.chat.completions.create(**generation_params)
                    logger.info("API重试调用成功")
                else:
                    raise e
            
            # 记录API响应信息
            logger.info(f"API响应信息:")
            logger.info(f"  - 响应ID: {response.id}")
            logger.info(f"  - 模型: {response.model}")
            logger.info(f"  - 创建时间: {response.created}")
            if hasattr(response, 'usage') and response.usage:
                logger.info(f"  - Token使用情况:")
                logger.info(f"    * 输入tokens: {response.usage.prompt_tokens}")
                logger.info(f"    * 输出tokens: {response.usage.completion_tokens}")
                logger.info(f"    * 总tokens: {response.usage.total_tokens}")
            
            # 提取生成的内容
            content = response.choices[0].message.content
            
            logger.info("内容生成完成")
            return content
            
        except Exception as e:
            logger.error(f"内容生成失败: {str(e)}")
            raise
    
    def _build_prompt(self, crawler_data: CrawlerData, custom_prompt: Optional[str] = None) -> str:
        """构建提示词
        
        Args:
            crawler_data: 爬虫数据对象
            custom_prompt: 自定义提示词
            
        Returns:
            构建的提示词
        """
        if custom_prompt:
            logger.info("使用自定义提示词")
            logger.info(f"自定义提示词内容: {custom_prompt}")
            return custom_prompt
            
        # 使用配置文件中的默认提示词模板
        logger.info("使用配置文件中的默认提示词模板")
        
        # 获取默认提示词模板
        prompt_template = self.config.get_prompt_template()
        if not prompt_template or 'user_template' not in prompt_template:
            logger.warning("未找到提示词模板，使用备用提示词")
            return self._build_fallback_prompt(crawler_data)
        
        user_template = prompt_template['user_template']
        logger.info(f"使用提示词模板: {self.config.get_default_prompt_type()}")
        
        # 准备模板变量
        template_vars = {
            'title': crawler_data.title or '无标题',
            'description': crawler_data.description or '无描述',
            'url': getattr(crawler_data, 'url', '无来源链接'),
            'comments_count': len(crawler_data.comments) if crawler_data.comments else 0,
            'images': self._format_images_info(crawler_data.image_url),
            'comments': self._format_comments_info(crawler_data.comments)
        }
        
        # 填充模板
        try:
            final_prompt = user_template.format(**template_vars)
            logger.info(f"提示词模板填充完成，最终长度: {len(final_prompt)} 字符")
            return final_prompt
        except KeyError as e:
            logger.error(f"提示词模板变量缺失: {e}，使用备用提示词")
            return self._build_fallback_prompt(crawler_data)
    
    def _build_fallback_prompt(self, crawler_data: CrawlerData) -> str:
        """构建备用提示词（当模板不可用时使用）
        
        Args:
            crawler_data: 爬虫数据对象
            
        Returns:
            备用提示词
        """
        logger.info("构建备用提示词")
        prompt_parts = [
            "请根据以下信息生成一篇有趣的社交媒体内容：",
            f"\n标题：{crawler_data.title}"
        ]
        
        if crawler_data.comments:
            selected_comments = crawler_data.comments[:5]  # 最多使用5条评论
            prompt_parts.append("\n用户评论：")
            for i, comment in enumerate(selected_comments, 1):
                prompt_parts.append(f"{i}. {comment}")
        
        prompt_parts.extend([
            "\n请生成一篇富有创意和吸引力的中文内容，要求：",
            "1. 结合标题和用户评论的情感氛围",
            "2. 使用适当的emoji表情符号",
            "3. 包含相关的中文话题标签（如#历史回忆 #老照片 #城市变迁等）",
            "4. 内容要有层次感和可读性，语言生动有趣",
            "5. 字数控制在200-400字之间",
            "6. 全文以中文为主，避免使用英文词汇和标签"
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_images_info(self, image_url: Optional[str]) -> str:
        """格式化图片信息
        
        Args:
            image_url: 图片URL
            
        Returns:
            格式化的图片信息
        """
        if not image_url:
            return "无图片"
        return f"包含图片: {image_url}"
    
    def _format_comments_info(self, comments: Optional[List[str]]) -> str:
        """格式化评论信息
        
        Args:
            comments: 评论列表
            
        Returns:
            格式化的评论信息
        """
        if not comments:
            return "无评论"
        
        # 选择前5条最有价值的评论
        selected_comments = comments[:5]
        formatted_comments = []
        
        for i, comment in enumerate(selected_comments, 1):
            # 限制每条评论的长度，避免提示词过长
            comment_text = comment[:200] + '...' if len(comment) > 200 else comment
            formatted_comments.append(f"{i}. {comment_text}")
        
        return "\n".join(formatted_comments)
    
    def _build_messages(self, prompt: str, image_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """构建消息列表
        
        Args:
            prompt: 提示词
            image_url: 图片URL
            
        Returns:
            消息列表
        """
        logger.info("开始构建API消息")
        messages = []
        
        # 添加系统消息
        prompt_template = self.config.get_prompt_template()
        if prompt_template and 'system' in prompt_template:
            system_prompt = prompt_template['system']
            logger.info(f"使用配置文件中的系统提示词")
        else:
            # 备用系统提示词
            system_prompt = (
                "你是一个专业的中文内容创作助手，擅长创作有趣、有吸引力的中文社交媒体内容。"
                "请根据提供的信息和图片（如果有）生成高质量的中文内容，使用中文话题标签。"
            )
            logger.info(f"使用备用系统提示词")
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        logger.info(f"添加系统消息，长度: {len(system_prompt)} 字符")
        
        # 构建用户消息
        if image_url and image_url.startswith('http'):
            # 多模态消息（文本+图片URL）
            logger.info(f"构建多模态消息: 文本({len(prompt)}字符) + 图片({image_url})")
            user_content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        else:
            # 纯文本消息（本地图片路径暂不支持）
            logger.info(f"构建纯文本消息，长度: {len(prompt)} 字符")
            user_content = prompt
            if image_url:
                logger.warning(f"本地图片路径暂不支持: {image_url}")
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        logger.info(f"消息构建完成，总消息数: {len(messages)}")
        return messages
    
    def batch_generate_from_tasks(self, task_ids: Optional[List[str]] = None,
                                 custom_prompt: Optional[str] = None,
                                 max_items: Optional[int] = None,
                                 save_to_file: bool = True) -> List[Dict[str, Any]]:
         """批量生成多个任务的内容
         
         Args:
             task_ids: 任务ID列表，如果为None则处理所有任务
             custom_prompt: 自定义提示词
             max_items: 最大处理项目数量
             save_to_file: 是否保存到文件
             
         Returns:
             生成结果列表
         """
         results = []
         
         try:
             # 获取要处理的任务列表
             if task_ids is None:
                 task_ids = self.data_loader.list_tasks()
             
             if max_items:
                 task_ids = task_ids[:max_items]
             
             logger.info(f"开始批量生成内容，共 {len(task_ids)} 个任务")
             
             for i, task_name in enumerate(task_ids, 1):
                 try:
                     logger.info(f"处理任务 {i}/{len(task_ids)}: {task_name}")
                     
                     content = self.generate_from_crawler_data(
                         task_name=task_name,
                         custom_prompt=custom_prompt,
                         save_to_file=save_to_file
                     )
                     
                     results.append({
                         "task_id": task_name,
                         "success": content is not None,
                         "content": content,
                         "error": None if content else "生成失败"
                     })
                     
                     # 简单的速率控制
                     if i % 3 == 0 and i < len(task_ids):
                         time.sleep(1)
                         
                 except Exception as e:
                     logger.error(f"处理任务 {task_name} 失败: {str(e)}")
                     results.append({
                         "task_id": task_name,
                         "success": False,
                         "content": None,
                         "error": str(e)
                     })
             
             success_count = sum(1 for r in results if r["success"])
             logger.info(f"批量生成完成，成功: {success_count}/{len(results)}")
             
         except Exception as e:
             logger.error(f"批量生成失败: {str(e)}")
             
         return results
    
    def _save_generated_content(self, task_name: str, content: str, custom_prompt: Optional[str] = None) -> Optional[str]:
        """保存生成的内容到爬虫任务目录
        
        Args:
            task_name: 任务名称
            content: 生成的内容
            custom_prompt: 自定义提示词（用于文件命名）
            
        Returns:
            保存的文件路径，如果保存失败返回None
        """
        try:
            # 构建保存路径
            task_path = self.data_loader.base_path / task_name
            if not task_path.exists():
                logger.error(f"任务目录不存在: {task_path}")
                return None
            
            # 创建ai_content目录
            ai_content_dir = task_path / "ai_content"
            ai_content_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if custom_prompt:
                # 如果有自定义提示词，使用custom前缀
                filename = f"content_custom_{timestamp}.txt"
            else:
                # 使用默认前缀
                filename = f"content_default_{timestamp}.txt"
            
            file_path = ai_content_dir / filename
            
            # 保存内容到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入元信息
                f.write(f"# AI生成内容\n")
                f.write(f"# 任务ID: {task_name}\n")
                f.write(f"# 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 提示词类型: {'自定义' if custom_prompt else '默认'}\n")
                if custom_prompt:
                    f.write(f"# 自定义提示词: {custom_prompt[:100]}{'...' if len(custom_prompt) > 100 else ''}\n")
                f.write(f"\n{'='*50}\n\n")
                
                # 写入生成的内容
                f.write(content)
            
            logger.info(f"内容保存成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存生成内容失败: {str(e)}")
            return None