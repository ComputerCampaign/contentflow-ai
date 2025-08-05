#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容模板和生成内容模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import json


class ContentTemplate(db.Model):
    """内容模板模型"""
    
    __tablename__ = 'content_templates'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 模板内容
    template = db.Column(db.Text, nullable=False)  # Jinja2模板
    variables = db.Column(db.JSON, nullable=False)  # 变量定义
    
    # 输出配置
    output_format = db.Column(db.Enum('markdown', 'html', 'text', 'json', 
                                     name='output_format'), 
                             default='markdown', nullable=False)
    
    # AI配置
    ai_model = db.Column(db.String(100))  # AI模型名称
    ai_prompt = db.Column(db.Text)  # AI提示词
    ai_config = db.Column(db.JSON)  # AI配置参数
    
    # 状态信息
    status = db.Column(db.Enum('active', 'inactive', 'testing', name='template_status'), 
                      default='active', nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开模板
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)
    
    # 版本信息
    version = db.Column(db.String(20), default='1.0.0')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 外键
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # 关联关系
    tasks = db.relationship('Task', backref='content_template', lazy='dynamic')
    generated_contents = db.relationship('GeneratedContent', backref='template', 
                                        lazy='dynamic', cascade='all, delete-orphan',
                                        order_by='GeneratedContent.created_at.desc()')
    
    def __init__(self, name, template, variables, user_id, **kwargs):
        self.name = name
        self.template = template
        self.variables = variables if isinstance(variables, list) else []
        self.user_id = user_id
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def validate_template(self):
        """验证模板有效性"""
        errors = []
        
        try:
            from jinja2 import Template, TemplateSyntaxError
            Template(self.template)
        except TemplateSyntaxError as e:
            errors.append(f"模板语法错误: {str(e)}")
        except Exception as e:
            errors.append(f"模板验证失败: {str(e)}")
        
        # 验证变量定义
        if not self.variables:
            errors.append("至少需要定义一个变量")
        
        for var in self.variables:
            if not isinstance(var, dict) or 'name' not in var:
                errors.append("变量定义格式错误")
                break
        
        return errors
    
    def get_required_variables(self):
        """获取必需的变量列表"""
        return [var['name'] for var in self.variables if var.get('required', False)]
    
    def render_preview(self, sample_data=None):
        """渲染预览"""
        try:
            from jinja2 import Template
            
            # 使用示例数据或默认数据
            if not sample_data:
                sample_data = {}
                for var in self.variables:
                    var_name = var['name']
                    var_type = var.get('type', 'string')
                    
                    if var_type == 'string':
                        sample_data[var_name] = f"示例{var_name}"
                    elif var_type == 'number':
                        sample_data[var_name] = 123
                    elif var_type == 'boolean':
                        sample_data[var_name] = True
                    else:
                        sample_data[var_name] = f"示例{var_name}"
            
            template = Template(self.template)
            return template.render(**sample_data)
        
        except Exception as e:
            return f"预览生成失败: {str(e)}"
    
    def get_recent_contents(self, limit=10):
        """获取最近生成的内容"""
        return self.generated_contents.limit(limit).all()
    
    def to_dict(self, include_template=True, include_contents=False):
        """转换为字典"""
        data = {
            'template_id': self.id,
            'name': self.name,
            'description': self.description,
            'variables': self.variables,
            'output_format': self.output_format,
            'ai_model': self.ai_model,
            'ai_prompt': self.ai_prompt,
            'ai_config': self.ai_config,
            'status': self.status,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }
        
        if include_template:
            data['template'] = self.template
            data['preview'] = self.render_preview()
        
        if include_contents:
            data['recent_contents'] = [content.to_dict() for content in self.get_recent_contents(5)]
        
        return data
    
    def __repr__(self):
        return f'<ContentTemplate {self.name}>'


class GeneratedContent(db.Model):
    """生成内容模型"""
    
    __tablename__ = 'generated_contents'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    title = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    
    # 生成信息
    input_data = db.Column(db.JSON)  # 输入数据
    generation_config = db.Column(db.JSON)  # 生成配置
    
    # AI信息
    ai_model_used = db.Column(db.String(100))
    ai_tokens_used = db.Column(db.Integer)
    ai_cost = db.Column(db.Float)  # AI调用成本
    
    # 状态信息
    status = db.Column(db.Enum('generating', 'completed', 'failed', name='content_status'), 
                      default='generating', nullable=False)
    error_message = db.Column(db.Text)
    
    # 质量评估
    quality_score = db.Column(db.Float)  # 质量评分 0-1
    readability_score = db.Column(db.Float)  # 可读性评分 0-1
    
    # 文件信息
    file_path = db.Column(db.String(500))  # 保存的文件路径
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    
    # 统计信息
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    
    # 处理时间
    generation_time = db.Column(db.Float)  # 生成时间（秒）
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 外键
    template_id = db.Column(db.String(36), db.ForeignKey('content_templates.id'), nullable=False)
    task_execution_id = db.Column(db.String(36), db.ForeignKey('task_executions.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, content, template_id, user_id, **kwargs):
        self.content = content
        self.template_id = template_id
        self.user_id = user_id
        
        # 自动计算统计信息
        self.word_count = len(content.split())
        self.character_count = len(content)
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_completed(self, **kwargs):
        """设置为完成状态"""
        self.status = 'completed'
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.commit()
    
    def set_failed(self, error_message):
        """设置为失败状态"""
        self.status = 'failed'
        self.error_message = error_message
        db.session.commit()
    
    def calculate_quality_metrics(self):
        """计算质量指标"""
        # 简单的质量评估算法
        content_length = len(self.content)
        word_count = self.word_count
        
        # 基于长度的质量评分
        if content_length < 100:
            self.quality_score = 0.3
        elif content_length < 500:
            self.quality_score = 0.6
        elif content_length < 2000:
            self.quality_score = 0.8
        else:
            self.quality_score = 0.9
        
        # 基于词汇密度的可读性评分
        if word_count > 0:
            avg_word_length = content_length / word_count
            if avg_word_length < 4:
                self.readability_score = 0.9
            elif avg_word_length < 6:
                self.readability_score = 0.7
            else:
                self.readability_score = 0.5
        else:
            self.readability_score = 0.0
        
        db.session.commit()
    
    def get_content_preview(self, max_length=200):
        """获取内容预览"""
        if not self.content:
            return ""
        
        content = self.content.strip()
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + "..."
    
    def to_dict(self, include_content=False):
        """转换为字典"""
        data = {
            'content_id': self.id,
            'title': self.title,
            'status': self.status,
            'error_message': self.error_message,
            'input_data': self.input_data,
            'generation_config': self.generation_config,
            'ai_model_used': self.ai_model_used,
            'ai_tokens_used': self.ai_tokens_used,
            'ai_cost': self.ai_cost,
            'quality_score': self.quality_score,
            'readability_score': self.readability_score,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'generation_time': self.generation_time,
            'created_at': self.created_at.isoformat(),
            'template_id': self.template_id,
            'task_execution_id': self.task_execution_id,
            'user_id': self.user_id
        }
        
        if include_content:
            data['content'] = self.content
        else:
            data['content_preview'] = self.get_content_preview()
        
        return data
    
    def __repr__(self):
        return f'<GeneratedContent {self.id}>'