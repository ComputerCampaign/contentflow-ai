from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
import sys

# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.crawler_utils.crawler_core import CrawlerCore
from backend.utils.logger import get_logger
from backend.config.config import Config

backdoor_bp = Blueprint('backdoor', __name__, url_prefix='/api/backdoor')
logger = get_logger(__name__)
config = Config()

# 存储任务状态的简单内存缓存
task_cache = {}

@backdoor_bp.route('/submit', methods=['POST'])
def submit_task():
    """提交爬取任务（无需认证）"""
    try:
        # 检查后门API是否启用
        if not config.get('backdoor.enabled', False):
            return jsonify({'error': '后门API已禁用'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL参数是必需的'}), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 获取可选参数
        xpath_rule_id = data.get('xpath_rule_id', 'general_article')
        output_format = data.get('output_format', 'json')
        include_images = data.get('include_images', True)
        
        # 记录任务
        task_info = {
            'task_id': task_id,
            'url': url,
            'xpath_rule_id': xpath_rule_id,
            'output_format': output_format,
            'include_images': include_images,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        task_cache[task_id] = task_info
        
        # 记录日志
        if config.get('backdoor.log_requests', True):
            logger.info(f"后门API任务提交: {task_id}, URL: {url}, IP: {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '任务已提交，请使用task_id查询状态'
        }), 200
        
    except Exception as e:
        logger.error(f"后门API任务提交失败: {str(e)}")
        return jsonify({'error': f'任务提交失败: {str(e)}'}), 500

@backdoor_bp.route('/crawl', methods=['POST'])
def quick_crawl():
    """快速爬取（同步执行）"""
    try:
        # 检查后门API是否启用
        if not config.get('backdoor.enabled', False):
            return jsonify({'error': '后门API已禁用'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL参数是必需的'}), 400
        
        # 获取可选参数
        xpath_rule_id = data.get('xpath_rule_id', 'general_article')
        include_images = data.get('include_images', True)
        
        # 记录日志
        if config.get('backdoor.log_requests', True):
            logger.info(f"后门API快速爬取: URL: {url}, IP: {request.remote_addr}")
        
        # 执行爬取
        crawler = CrawlerCore()
        result = crawler.crawl_url(
            url=url,
            xpath_rule_id=xpath_rule_id,
            include_images=include_images
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '爬取完成'
        }), 200
        
    except Exception as e:
        logger.error(f"后门API快速爬取失败: {str(e)}")
        return jsonify({'error': f'爬取失败: {str(e)}'}), 500

@backdoor_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """查询任务状态"""
    try:
        # 检查后门API是否启用
        if not config.get('backdoor.enabled', False):
            return jsonify({'error': '后门API已禁用'}), 403
        
        if task_id not in task_cache:
            return jsonify({'error': '任务不存在'}), 404
        
        task_info = task_cache[task_id]
        
        return jsonify({
            'success': True,
            'task_info': task_info
        }), 200
        
    except Exception as e:
        logger.error(f"后门API状态查询失败: {str(e)}")
        return jsonify({'error': f'状态查询失败: {str(e)}'}), 500

@backdoor_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'backdoor_enabled': config.get('backdoor.enabled', False)
    }), 200