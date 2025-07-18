#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫任务管理相关API接口
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
import os
import json

from ..models import User, UserXPathRule, db
from ..auth.permissions import login_required, group_required
from ..crawler_utils.crawler_core import CrawlerCore
from ..crawler_utils.xpath_manager import XPathManager
from ..config.config import Config

crawler_bp = Blueprint('crawler', __name__)

@crawler_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """
    创建新的爬虫任务
    
    请求体:
    {
        "url": "要爬取的URL",
        "task_name": "任务名称", (可选，默认自动生成)
        "use_selenium": true/false, (可选，默认false)
        "use_xpath": true/false, (可选，默认false)
        "xpath_rule_id": "XPath规则ID", (可选，当use_xpath为true时必须提供)
        "is_user_rule": true/false, (可选，默认false，表示是否使用用户自定义规则)
        "blog_template": "博客模板名称" (可选)
    }
    """
    data = request.get_json()
    
    if 'url' not in data:
        return jsonify({"error": "缺少必要字段: url"}), 400
    
    # 获取配置
    config = Config()
    
    # 初始化爬虫核心
    crawler = CrawlerCore(
        output_dir=config.get('crawler.output_dir'),
        data_dir=config.get('crawler.data_dir'),
        timeout=config.get('crawler.timeout'),
        retry=config.get('crawler.retry'),
        use_selenium=data.get('use_selenium', False),
        use_xpath=data.get('use_xpath', False),
        max_concurrent=config.get('crawler.max_concurrent')
    )
    
    # 处理XPath规则
    xpath_rule = None
    if data.get('use_xpath', False):
        if 'xpath_rule_id' not in data:
            return jsonify({"error": "使用XPath时必须提供xpath_rule_id"}), 400
        
        # 检查是否使用用户自定义规则
        if data.get('is_user_rule', False):
            rule = UserXPathRule.query.get(data['xpath_rule_id'])
            if not rule or rule.user_id != g.current_user.id:
                return jsonify({"error": "XPath规则不存在或无权访问"}), 404
            
            # 用户自定义规则直接使用规则内容
            xpath_rule = {
                "id": str(rule.id),
                "name": rule.rule_name,
                "domain": rule.domain,
                "xpath": rule.xpath
            }
        else:
            # 使用系统预设规则
            xpath_manager = XPathManager()
            system_rule = xpath_manager.get_rule(data['xpath_rule_id'])
            if not system_rule:
                return jsonify({"error": "系统XPath规则不存在"}), 404
            xpath_rule = system_rule
    
    # 检查博客模板权限
    if 'blog_template' in data and data['blog_template']:
        if not g.current_user.group:
            return jsonify({"error": "用户未分配用户组，无法使用博客模板"}), 403
        
        allowed_templates = g.current_user.group.allowed_templates
        if data['blog_template'] not in allowed_templates:
            return jsonify({"error": f"无权使用博客模板: {data['blog_template']}"}), 403
    
    # 执行爬取任务
    try:
        task_id = data.get('task_name', None) or f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{g.current_user.id}"
        result = crawler.crawl(
            url=data['url'],
            task_id=task_id,
            xpath_rule=xpath_rule
        )
        
        # 记录任务信息到用户任务历史
        task_info = {
            "task_id": task_id,
            "url": data['url'],
            "created_at": datetime.now().isoformat(),
            "user_id": g.current_user.id,
            "status": "success" if result else "failed",
            "use_selenium": data.get('use_selenium', False),
            "use_xpath": data.get('use_xpath', False),
            "xpath_rule_id": data.get('xpath_rule_id'),
            "is_user_rule": data.get('is_user_rule', False),
            "blog_template": data.get('blog_template')
        }
        
        # 保存任务信息
        tasks_dir = os.path.join(config.get('crawler.data_dir'), 'user_tasks')
        os.makedirs(tasks_dir, exist_ok=True)
        
        with open(os.path.join(tasks_dir, f"{task_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(task_info, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "task_id": task_id,
            "message": "爬取任务创建成功",
            "status": "success" if result else "failed"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"爬取任务执行失败: {str(e)}"
        }), 500

@crawler_bp.route('/tasks', methods=['GET'])
@login_required
def get_user_tasks():
    """
    获取当前用户的爬虫任务列表
    """
    config = Config()
    tasks_dir = os.path.join(config.get('crawler.data_dir'), 'user_tasks')
    
    if not os.path.exists(tasks_dir):
        return jsonify({"tasks": []})
    
    tasks = []
    for filename in os.listdir(tasks_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(tasks_dir, filename), 'r', encoding='utf-8') as f:
                    task_info = json.load(f)
                    
                    # 只返回当前用户的任务
                    if task_info.get('user_id') == g.current_user.id:
                        tasks.append({
                            "task_id": task_info.get('task_id'),
                            "url": task_info.get('url'),
                            "created_at": task_info.get('created_at'),
                            "status": task_info.get('status'),
                            "use_xpath": task_info.get('use_xpath'),
                            "blog_template": task_info.get('blog_template')
                        })
            except Exception:
                # 忽略无法解析的任务文件
                continue
    
    # 按创建时间倒序排序
    tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify({"tasks": tasks})

@crawler_bp.route('/tasks/<task_id>', methods=['GET'])
@login_required
def get_task_detail(task_id):
    """
    获取指定爬虫任务的详细信息
    """
    config = Config()
    task_file = os.path.join(config.get('crawler.data_dir'), 'user_tasks', f"{task_id}.json")
    
    if not os.path.exists(task_file):
        return jsonify({"error": "任务不存在"}), 404
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_info = json.load(f)
            
            # 验证任务所有权
            if task_info.get('user_id') != g.current_user.id:
                # 管理员可以查看所有任务
                if not g.current_user.group or g.current_user.group.name != 'admin':
                    return jsonify({"error": "无权访问此任务"}), 403
            
            # 获取任务输出文件信息
            task_output_dir = os.path.join(config.get('crawler.output_dir'), task_id)
            output_files = []
            
            if os.path.exists(task_output_dir):
                for root, _, files in os.walk(task_output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, task_output_dir)
                        output_files.append({
                            "name": file,
                            "path": rel_path,
                            "size": os.path.getsize(file_path),
                            "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                        })
            
            # 返回任务详情和输出文件信息
            return jsonify({
                **task_info,
                "output_files": output_files
            })
    
    except Exception as e:
        return jsonify({"error": f"获取任务详情失败: {str(e)}"}), 500

@crawler_bp.route('/templates', methods=['GET'])
@login_required
def get_available_templates():
    """
    获取当前用户可用的博客模板列表
    """
    if not g.current_user.group:
        return jsonify({"templates": []})
    
    allowed_templates = g.current_user.group.allowed_templates
    
    # 获取模板详细信息
    config = Config()
    templates_dir = config.get('blogs.templates_dir')
    
    templates = []
    for template_name in allowed_templates:
        template_path = os.path.join(templates_dir, template_name)
        if os.path.exists(template_path):
            # 尝试读取模板的元数据（如果有）
            meta_file = os.path.join(template_path, 'meta.json')
            meta = {}
            
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                except Exception:
                    pass
            
            templates.append({
                "name": template_name,
                "description": meta.get('description', ''),
                "author": meta.get('author', ''),
                "version": meta.get('version', '1.0'),
                "preview": meta.get('preview', '')
            })
    
    return jsonify({"templates": templates})