#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理API
"""

from flask import Blueprint, request, jsonify, current_app, send_file, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, limiter
from backend.models.user import User
from backend.models.file import FileRecord
from datetime import datetime, timedelta
from sqlalchemy import or_
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import mimetypes


files_bp = Blueprint('files', __name__)


def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def allowed_file(filename):
    """检查文件类型是否允许"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'xls', 'xlsx', 'csv', 'json', 'xml', 'html', 'md'
    })
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_category(filename):
    """根据文件扩展名确定文件分类"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    image_exts = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}
    document_exts = {'pdf', 'doc', 'docx', 'txt', 'md', 'html', 'htm'}
    data_exts = {'csv', 'json', 'xml', 'xls', 'xlsx'}
    
    if ext in image_exts:
        return 'image'
    elif ext in document_exts:
        return 'document'
    elif ext in data_exts:
        return 'data'
    else:
        return 'document'


def ensure_upload_dir():
    """确保上传目录存在"""
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir


@files_bp.route('/upload', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def upload_file():
    """上传文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '不支持的文件类型'
            }), 400
        
        # 获取文件信息
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = ensure_upload_dir()
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 获取其他参数
        category = request.form.get('category', get_file_category(original_filename))
        description = request.form.get('description', '')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        is_public = request.form.get('is_public', 'false').lower() == 'true'
        
        # 保存文件
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(original_filename)
        
        # 创建文件记录
        file_record = FileRecord(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            user_id=current_user.id,
            category=category,
            file_type=mime_type,
            description=description,
            tags=tags,
            is_public=is_public
        )
        
        # 计算文件哈希
        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_record.calculate_hashes(file_content)
        
        # 设置为可用状态
        file_record.set_available()
        
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'data': {
                'file': file_record.to_dict()
            }
        }), 201
        
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'message': '文件大小超过限制'
        }), 413
    except Exception as e:
        # 清理已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        
        db.session.rollback()
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '文件上传失败，请稍后重试'
        }), 500


@files_bp.route('', methods=['GET'])
@jwt_required()
def get_files():
    """获取文件列表"""
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
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = FileRecord.query.filter_by(user_id=current_user.id)
        
        # 分类过滤
        if category:
            query = query.filter(FileRecord.category == category)
        
        # 状态过滤
        if status:
            query = query.filter(FileRecord.status == status)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    FileRecord.original_filename.contains(search),
                    FileRecord.description.contains(search)
                )
            )
        
        # 排序和分页
        query = query.order_by(FileRecord.created_at.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        files = [file_record.to_dict() for file_record in pagination.items]
        
        return jsonify({
            'success': True,
            'message': '获取文件列表成功',
            'data': {
                'files': files,
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
        current_app.logger.error(f"获取文件列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取文件列表失败'
        }), 500


@files_bp.route('/<file_id>', methods=['GET'])
@jwt_required()
def get_file_info(file_id):
    """获取文件信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        file_record = FileRecord.query.filter_by(
            id=file_id, user_id=current_user.id
        ).first()
        if not file_record:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '获取文件信息成功',
            'data': {
                'file': file_record.to_dict(include_path=True)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取文件信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取文件信息失败'
        }), 500


@files_bp.route('/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """下载文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        file_record = FileRecord.query.filter_by(
            id=file_id, user_id=current_user.id
        ).first()
        if not file_record:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 检查文件状态
        if file_record.status != 'available':
            return jsonify({
                'success': False,
                'message': '文件不可用'
            }), 400
        
        # 检查文件是否过期
        if file_record.is_expired():
            return jsonify({
                'success': False,
                'message': '文件已过期'
            }), 410
        
        # 检查文件是否存在
        if not os.path.exists(file_record.file_path):
            return jsonify({
                'success': False,
                'message': '文件不存在于服务器'
            }), 404
        
        # 增加下载次数
        file_record.increment_download()
        
        # 返回文件
        return send_file(
            file_record.file_path,
            as_attachment=True,
            download_name=file_record.original_filename,
            mimetype=file_record.file_type
        )
        
    except Exception as e:
        current_app.logger.error(f"文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '文件下载失败'
        }), 500


@files_bp.route('/<file_id>', methods=['PUT'])
@jwt_required()
def update_file_info(file_id):
    """更新文件信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        file_record = FileRecord.query.filter_by(
            id=file_id, user_id=current_user.id
        ).first()
        if not file_record:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 可更新的字段
        updatable_fields = [
            'description', 'tags', 'is_public', 'category', 'expires_at'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'expires_at' and data[field]:
                    # 解析过期时间
                    try:
                        expires_at = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        setattr(file_record, field, expires_at)
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'message': '过期时间格式无效'
                        }), 400
                else:
                    setattr(file_record, field, data[field])
        
        file_record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件信息更新成功',
            'data': {
                'file': file_record.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新文件信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新文件信息失败'
        }), 500


@files_bp.route('/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """删除文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        file_record = FileRecord.query.filter_by(
            id=file_id, user_id=current_user.id
        ).first()
        if not file_record:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 获取删除类型
        force_delete = request.args.get('force', 'false').lower() == 'true'
        
        if force_delete:
            # 硬删除
            file_record.hard_delete()
            message = '文件已永久删除'
        else:
            # 软删除
            file_record.soft_delete()
            message = '文件已删除'
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除文件失败'
        }), 500


@files_bp.route('/batch-upload', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def batch_upload_files():
    """批量上传文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 检查是否有文件
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 限制批量上传数量
        max_files = current_app.config.get('MAX_BATCH_UPLOAD', 10)
        if len(files) > max_files:
            return jsonify({
                'success': False,
                'message': f'批量上传最多支持{max_files}个文件'
            }), 400
        
        uploaded_files = []
        failed_files = []
        
        # 确保上传目录存在
        upload_dir = ensure_upload_dir()
        
        for file in files:
            try:
                if file.filename == '' or not allowed_file(file.filename):
                    failed_files.append({
                        'filename': file.filename,
                        'error': '文件类型不支持'
                    })
                    continue
                
                # 处理单个文件
                original_filename = secure_filename(file.filename)
                file_extension = os.path.splitext(original_filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # 保存文件
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                mime_type, _ = mimetypes.guess_type(original_filename)
                
                # 创建文件记录
                file_record = FileRecord(
                    filename=unique_filename,
                    original_filename=original_filename,
                    file_path=file_path,
                    file_size=file_size,
                    user_id=current_user.id,
                    category=get_file_category(original_filename),
                    file_type=mime_type
                )
                
                # 计算文件哈希
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                file_record.calculate_hashes(file_content)
                file_record.set_available()
                
                db.session.add(file_record)
                uploaded_files.append(file_record.to_dict())
                
            except Exception as e:
                failed_files.append({
                    'filename': file.filename,
                    'error': str(e)
                })
                # 清理失败的文件
                if 'file_path' in locals() and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'批量上传完成，成功{len(uploaded_files)}个，失败{len(failed_files)}个',
            'data': {
                'uploaded_files': uploaded_files,
                'failed_files': failed_files,
                'summary': {
                    'total': len(files),
                    'success': len(uploaded_files),
                    'failed': len(failed_files)
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批量上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '批量上传失败，请稍后重试'
        }), 500


@files_bp.route('/cleanup', methods=['POST'])
@jwt_required()
@limiter.limit("1 per hour")
def cleanup_files():
    """清理过期和删除的文件"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 查找需要清理的文件
        now = datetime.utcnow()
        
        # 过期文件
        expired_files = FileRecord.query.filter(
            FileRecord.user_id == current_user.id,
            FileRecord.expires_at < now,
            FileRecord.auto_delete == True
        ).all()
        
        # 已删除的文件（软删除超过30天）
        deleted_files = FileRecord.query.filter(
            FileRecord.user_id == current_user.id,
            FileRecord.status == 'deleted',
            FileRecord.updated_at < now - timedelta(days=30)
        ).all()
        
        cleaned_count = 0
        
        # 清理过期文件
        for file_record in expired_files:
            try:
                file_record.hard_delete()
                cleaned_count += 1
            except Exception as e:
                current_app.logger.error(f"清理过期文件失败 {file_record.id}: {str(e)}")
        
        # 清理已删除文件
        for file_record in deleted_files:
            try:
                file_record.hard_delete()
                cleaned_count += 1
            except Exception as e:
                current_app.logger.error(f"清理已删除文件失败 {file_record.id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'文件清理完成，共清理{cleaned_count}个文件',
            'data': {
                'cleaned_count': cleaned_count,
                'expired_files': len(expired_files),
                'deleted_files': len(deleted_files)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"文件清理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '文件清理失败'
        }), 500


@files_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_file_stats():
    """获取文件统计信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 基本统计
        total_files = FileRecord.query.filter_by(user_id=current_user.id).count()
        available_files = FileRecord.query.filter_by(
            user_id=current_user.id, status='available'
        ).count()
        deleted_files = FileRecord.query.filter_by(
            user_id=current_user.id, status='deleted'
        ).count()
        
        # 按分类统计
        category_stats = {}
        for category in ['image', 'document', 'data', 'log', 'output', 'temp']:
            category_stats[category] = FileRecord.query.filter_by(
                user_id=current_user.id, category=category
            ).count()
        
        # 存储统计
        from sqlalchemy import func
        total_size = db.session.query(func.sum(FileRecord.file_size)).filter_by(
            user_id=current_user.id, status='available'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'message': '获取文件统计信息成功',
            'data': {
                'file_stats': {
                    'total': total_files,
                    'available': available_files,
                    'deleted': deleted_files
                },
                'category_stats': category_stats,
                'storage_stats': {
                    'total_size': total_size,
                    'total_size_human': FileRecord.get_file_size_human(FileRecord(file_size=total_size))
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取文件统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取文件统计信息失败'
        }), 500