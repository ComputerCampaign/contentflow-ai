#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模型
"""

from backend.extensions import db
from datetime import datetime
import uuid
import os
import hashlib


class FileRecord(db.Model):
    """文件记录模型"""
    
    __tablename__ = 'file_records'
    
    # 主键
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # 文件属性
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    file_type = db.Column(db.String(100))  # MIME类型
    file_extension = db.Column(db.String(20))  # 文件扩展名
    
    # 文件哈希
    md5_hash = db.Column(db.String(32))  # MD5哈希
    sha256_hash = db.Column(db.String(64))  # SHA256哈希
    
    # 分类信息
    category = db.Column(db.Enum('image', 'document', 'data', 'log', 'output', 'temp', 
                                name='file_category'), nullable=False)
    tags = db.Column(db.JSON)  # 标签列表
    
    # 状态信息
    status = db.Column(db.Enum('uploading', 'available', 'processing', 'archived', 'deleted', 
                              name='file_status'), default='uploading', nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    
    # 访问信息
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    
    # 存储信息
    storage_type = db.Column(db.Enum('local', 'github', 's3', 'oss', name='storage_type'), 
                            default='local', nullable=False)
    storage_config = db.Column(db.JSON)  # 存储配置
    
    # 关联信息
    related_task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'))
    related_content_id = db.Column(db.String(36), db.ForeignKey('generated_contents.id'))
    
    # 元数据
    file_metadata = db.Column(db.JSON)  # 文件元数据
    description = db.Column(db.Text)  # 文件描述
    
    # 过期信息
    expires_at = db.Column(db.DateTime)  # 过期时间
    auto_delete = db.Column(db.Boolean, default=False)  # 是否自动删除
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # 外键
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, filename, original_filename, file_path, file_size, 
                 user_id, category='document', **kwargs):
        self.filename = filename
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.user_id = user_id
        self.category = category
        
        # 自动设置文件扩展名
        self.file_extension = os.path.splitext(original_filename)[1].lower()
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_hashes(self, file_content=None):
        """计算文件哈希值"""
        if file_content is None:
            try:
                with open(self.file_path, 'rb') as f:
                    file_content = f.read()
            except Exception:
                return False
        
        # 计算MD5
        md5_hash = hashlib.md5()
        md5_hash.update(file_content)
        self.md5_hash = md5_hash.hexdigest()
        
        # 计算SHA256
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)
        self.sha256_hash = sha256_hash.hexdigest()
        
        db.session.commit()
        return True
    
    def set_available(self):
        """设置文件为可用状态"""
        self.status = 'available'
        db.session.commit()
    
    def increment_download(self):
        """增加下载次数"""
        self.download_count += 1
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def is_expired(self):
        """检查文件是否过期"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_file_url(self, base_url=None):
        """获取文件访问URL"""
        if self.storage_type == 'local':
            if base_url:
                return f"{base_url}/api/v1/files/{self.id}/download"
            return f"/api/v1/files/{self.id}/download"
        elif self.storage_type == 'github':
            # GitHub存储的URL
            config = self.storage_config or {}
            return config.get('url', '')
        else:
            # 其他存储类型
            config = self.storage_config or {}
            return config.get('url', '')
    
    def get_file_size_human(self):
        """获取人类可读的文件大小"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def is_image(self):
        """检查是否为图片文件"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        return self.file_extension.lower() in image_extensions
    
    def is_document(self):
        """检查是否为文档文件"""
        doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md', '.html', '.htm'}
        return self.file_extension.lower() in doc_extensions
    
    def soft_delete(self):
        """软删除文件"""
        self.status = 'deleted'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def hard_delete(self):
        """硬删除文件"""
        # 删除物理文件
        try:
            if self.storage_type == 'local' and os.path.exists(self.file_path):
                os.remove(self.file_path)
        except Exception:
            pass
        
        # 删除数据库记录
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self, include_path=False):
        """转换为字典"""
        data = {
            'file_id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_human': self.get_file_size_human(),
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'category': self.category,
            'tags': self.tags,
            'status': self.status,
            'is_public': self.is_public,
            'download_count': self.download_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'storage_type': self.storage_type,
            'description': self.description,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'is_image': self.is_image(),
            'is_document': self.is_document(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'related_task_id': self.related_task_id,
            'related_content_id': self.related_content_id,
            'download_url': self.get_file_url()
        }
        
        if include_path:
            data['file_path'] = self.file_path
            data['md5_hash'] = self.md5_hash
            data['sha256_hash'] = self.sha256_hash
            data['storage_config'] = self.storage_config
            data['file_metadata'] = self.file_metadata
        
        return data
    
    def __repr__(self):
        return f'<FileRecord {self.filename}>'