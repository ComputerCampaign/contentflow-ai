#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理器模块
处理爬虫数据读取和AI生成结果存储
"""

import json
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..utils.logger import setup_logger


class FileManager:
    """文件管理器"""
    
    def __init__(self):
        """
        初始化文件管理器
        """
        self.logger = setup_logger(__name__, file_path=True)
        self.ai_content_dir = 'ai_content'
        
        self.logger.info("文件管理器初始化完成")
    
    def load_crawler_data(self, task_dir: str) -> Dict[str, Any]:
        """
        从爬虫任务目录加载数据
        
        Args:
            task_dir: 爬虫任务目录路径
        
        Returns:
            爬虫数据字典
        """
        try:
            self.logger.info(f"开始加载爬虫数据，原始路径: {task_dir}")
            
            # 路径转换：如果是相对路径，转换为crawler_data/[task_dir]的完整路径
            if not os.path.isabs(task_dir):
                # 获取项目根目录（crawler目录的上级目录）
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                task_dir = os.path.join(current_dir, 'crawler_data', task_dir)
                self.logger.debug(f"相对路径转换为绝对路径: {task_dir}")
            
            # 确保路径正确
            task_dir = os.path.abspath(task_dir)
            self.logger.debug(f"最终任务目录路径: {task_dir}")
            
            if not os.path.exists(task_dir):
                self.logger.error(f"任务目录不存在: {task_dir}")
                raise FileNotFoundError(f"任务目录不存在: {task_dir}")
            
            # 加载元数据文件
            metadata_file = os.path.join(task_dir, "metadata", "metadata.json")
            self.logger.debug(f"尝试加载元数据文件: {metadata_file}")
            
            if not os.path.exists(metadata_file):
                self.logger.error(f"元数据文件不存在: {metadata_file}")
                raise FileNotFoundError(f"元数据文件不存在: {metadata_file}")
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                self.logger.debug(f"元数据文件加载成功，包含 {len(metadata)} 个字段")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"元数据文件加载失败: {e}")
                raise ValueError(f"元数据文件加载失败: {e}")
            
            # 从metadata中提取图片URL，优先使用github_url
            image_url = None
            images = metadata.get('images', [])
            if images and len(images) > 0:
                first_image = images[0]
                # 优先使用github_url，如果没有则使用原始url
                image_url = first_image.get('github_url') or first_image.get('url')
                self.logger.debug(f"提取图片URL: {image_url}")
            
            crawler_data = {
                'task_dir': task_dir,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'url': metadata.get('url', ''),
                'comments': metadata.get('comments', []),
                'images': [image_url] if image_url else [],
                'metadata': metadata
            }
            
            self.logger.debug(f"构建爬虫数据结构，评论数: {len(crawler_data.get('comments', []))}，图片数: {len(crawler_data.get('images', []))}")
            
            # 验证数据完整性
            self._validate_crawler_data(crawler_data)
            
            self.logger.info(f"爬虫数据加载完成，标题: {crawler_data.get('title', '未知')}，评论数: {len(crawler_data.get('comments', []))}")
            return crawler_data
            
        except Exception as e:
            self.logger.error(f"加载爬虫数据失败: {e}")
            raise
    
    def _find_data_files(self, task_dir: str) -> List[str]:
        """
        查找数据文件
        
        Args:
            task_dir: 任务目录
        
        Returns:
            数据文件路径列表
        """
        data_files = []
        
        # 常见的数据文件名模式
        patterns = [
            'data.json',
            'result.json',
            'content.json',
            'info.json',
            'metadata.json'
        ]
        
        for pattern in patterns:
            file_path = os.path.join(task_dir, pattern)
            if os.path.exists(file_path):
                data_files.append(file_path)
        
        # 查找所有JSON文件
        for file_name in os.listdir(task_dir):
            if file_name.endswith('.json') and file_name not in [os.path.basename(f) for f in data_files]:
                file_path = os.path.join(task_dir, file_name)
                if os.path.isfile(file_path):
                    data_files.append(file_path)
        
        self.logger.info(f"找到 {len(data_files)} 个数据文件")
        return data_files
    
    def _find_image_files(self, task_dir: str) -> List[str]:
        """
        查找图片文件
        
        Args:
            task_dir: 任务目录
        
        Returns:
            图片文件路径列表
        """
        image_files = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        try:
            for root, dirs, files in os.walk(task_dir):
                for file_name in files:
                    file_ext = os.path.splitext(file_name)[1].lower()
                    if file_ext in image_extensions:
                        file_path = os.path.join(root, file_name)
                        # 转换为相对路径或URL格式
                        image_files.append(f"file://{os.path.abspath(file_path)}")
            
            self.logger.info(f"找到 {len(image_files)} 个图片文件")
            return image_files
            
        except Exception as e:
            self.logger.warning(f"查找图片文件失败: {e}")
            return []
    
    def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载JSON文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            JSON数据或None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"成功加载文件: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON解析失败 {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"文件加载失败 {file_path}: {e}")
            return None
    
    def _merge_crawler_data(self, base_data: Dict[str, Any], 
                           new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并爬虫数据
        
        Args:
            base_data: 基础数据
            new_data: 新数据
        
        Returns:
            合并后的数据
        """
        try:
            # 合并基本字段
            if 'title' in new_data and new_data['title']:
                base_data['title'] = new_data['title']
            
            if 'description' in new_data and new_data['description']:
                base_data['description'] = new_data['description']
            
            if 'url' in new_data and new_data['url']:
                base_data['url'] = new_data['url']
            
            # 合并评论
            if 'comments' in new_data and isinstance(new_data['comments'], list):
                base_data['comments'].extend(new_data['comments'])
            
            # 合并图片
            if 'images' in new_data and isinstance(new_data['images'], list):
                base_data['images'].extend(new_data['images'])
            
            # 合并元数据
            if 'metadata' in new_data and isinstance(new_data['metadata'], dict):
                base_data['metadata'].update(new_data['metadata'])
            
            # 处理其他可能的字段
            for key, value in new_data.items():
                if key not in base_data and value:
                    base_data[key] = value
            
            return base_data
            
        except Exception as e:
            self.logger.error(f"数据合并失败: {e}")
            return base_data
    
    def _validate_crawler_data(self, crawler_data: Dict[str, Any]):
        """
        验证爬虫数据
        
        Args:
            crawler_data: 爬虫数据
        
        Raises:
            ValueError: 数据验证失败
        """
        if not crawler_data.get('title'):
            raise ValueError("缺少标题信息")
        
        # 去重图片
        if crawler_data.get('images'):
            crawler_data['images'] = list(set(crawler_data['images']))
    
    def create_ai_content_dir(self, task_dir: str) -> str:
        """
        在任务目录中创建AI内容目录
        
        Args:
            task_dir: 任务目录
        
        Returns:
            AI内容目录路径
        """
        try:
            ai_dir = os.path.join(task_dir, self.ai_content_dir)
            os.makedirs(ai_dir, exist_ok=True)
            
            self.logger.info(f"AI内容目录已创建: {ai_dir}")
            return ai_dir
            
        except Exception as e:
            self.logger.error(f"创建AI内容目录失败: {e}")
            raise
    
    def save_generation_result(self, task_dir: str, result: Dict[str, Any], 
                             result_type: str = 'content') -> str:
        """
        保存生成结果
        
        Args:
            task_dir: 任务目录
            result: 生成结果
            result_type: 结果类型 ('text', 'video', 'content', 'full', 'final')
        
        Returns:
            保存的文件路径
        """
        try:
            self.logger.info(f"开始保存生成结果，任务目录: {task_dir}，结果类型: {result_type}")
            
            # 转换相对路径为绝对路径
            if not os.path.isabs(task_dir):
                task_dir = os.path.abspath(os.path.join('crawler_data', task_dir))
                self.logger.debug(f"相对路径转换为绝对路径: {task_dir}")
            
            # 根据结果类型决定保存位置和文件名
            if result_type == 'final':
                # 最终结果保存在爬虫任务同目录下
                save_dir = task_dir
                filename = 'ai_generation_result.json'
                self.logger.debug(f"最终结果保存位置: {save_dir}")
            elif result_type == 'text':
                # 文案结果保存在ai_content子目录，使用固定文件名
                save_dir = self.create_ai_content_dir(task_dir)
                filename = 'text_generation_result.json'
                self.logger.debug(f"文案结果保存位置: {save_dir}，文件名: {filename}")
            elif result_type == 'video':
                # 视频结果保存在ai_content子目录，使用固定文件名
                save_dir = self.create_ai_content_dir(task_dir)
                filename = 'video_generation_result.json'
                self.logger.debug(f"视频结果保存位置: {save_dir}，文件名: {filename}")
            else:
                # 其他结果保存在ai_content子目录，使用时间戳
                save_dir = self.create_ai_content_dir(task_dir)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{result_type}_generation_{timestamp}.json"
                self.logger.debug(f"中间结果保存位置: {save_dir}，文件名: {filename}")
            
            file_path = os.path.join(save_dir, filename)
            
            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 计算结果大小信息
            result_size = len(str(result))
            result_keys = list(result.keys()) if isinstance(result, dict) else []
            self.logger.debug(f"结果数据大小: {result_size} 字符，包含字段: {result_keys}")
            
            # 添加保存信息到结果中
            result_with_meta = {
                **result,
                'save_info': {
                    'saved_at': datetime.now().isoformat(),
                    'file_path': file_path,
                    'result_type': result_type
                }
            }
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
            
            # 获取保存后的文件大小
            file_size = os.path.getsize(file_path)
            self.logger.info(f"生成结果已保存: {file_path}，文件大小: {file_size} 字节")
            return file_path
            
        except Exception as e:
            self.logger.error(f"保存生成结果失败: {e}")
            raise
    
    def load_generation_result(self, task_dir: str, 
                             result_type: str = None) -> Optional[Dict[str, Any]]:
        """
        加载生成结果
        
        Args:
            task_dir: 任务目录
            result_type: 结果类型（可选）
        
        Returns:
            生成结果或None
        """
        try:
            ai_dir = os.path.join(task_dir, self.ai_content_dir)
            
            if not os.path.exists(ai_dir):
                self.logger.info(f"AI内容目录不存在: {ai_dir}")
                return None
            
            # 查找结果文件
            result_files = []
            for file_name in os.listdir(ai_dir):
                if file_name.endswith('.json'):
                    if result_type is None or result_type in file_name:
                        result_files.append(os.path.join(ai_dir, file_name))
            
            if not result_files:
                self.logger.info(f"未找到生成结果文件")
                return None
            
            # 加载最新的结果文件
            result_files.sort(key=os.path.getmtime, reverse=True)
            latest_file = result_files[0]
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            self.logger.info(f"加载生成结果: {latest_file}")
            return result
            
        except Exception as e:
            self.logger.error(f"加载生成结果失败: {e}")
            return None
    
    def load_text_generation_result(self, task_dir: str) -> Optional[Dict[str, Any]]:
        """
        加载文案生成结果
        
        Args:
            task_dir: 任务目录
        
        Returns:
            文案生成结果或None
        """
        try:
            # 转换相对路径为绝对路径
            if not os.path.isabs(task_dir):
                task_dir = os.path.abspath(os.path.join('crawler_data', task_dir))
            
            ai_dir = os.path.join(task_dir, self.ai_content_dir)
            text_result_file = os.path.join(ai_dir, 'text_generation_result.json')
            
            if not os.path.exists(text_result_file):
                self.logger.warning(f"文案生成结果文件不存在: {text_result_file}")
                return None
            
            with open(text_result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            self.logger.info(f"成功加载文案生成结果: {text_result_file}")
            return result
            
        except Exception as e:
            self.logger.error(f"加载文案生成结果失败: {e}")
            return None
    
    def list_generation_results(self, task_dir: str) -> List[Dict[str, Any]]:
        """
        列出所有生成结果
        
        Args:
            task_dir: 任务目录
        
        Returns:
            结果文件信息列表
        """
        try:
            ai_dir = os.path.join(task_dir, self.ai_content_dir)
            
            if not os.path.exists(ai_dir):
                return []
            
            results = []
            for file_name in os.listdir(ai_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(ai_dir, file_name)
                    file_stat = os.stat(file_path)
                    
                    results.append({
                        'filename': file_name,
                        'file_path': file_path,
                        'size': file_stat.st_size,
                        'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
            
            # 按修改时间排序
            results.sort(key=lambda x: x['modified_at'], reverse=True)
            
            self.logger.info(f"找到 {len(results)} 个生成结果文件")
            return results
            
        except Exception as e:
            self.logger.error(f"列出生成结果失败: {e}")
            return []
    
    def cleanup_old_results(self, task_dir: str, keep_count: int = 10):
        """
        清理旧的生成结果
        
        Args:
            task_dir: 任务目录
            keep_count: 保留的文件数量
        """
        try:
            results = self.list_generation_results(task_dir)
            
            if len(results) <= keep_count:
                self.logger.info(f"文件数量 {len(results)} 未超过限制 {keep_count}，无需清理")
                return
            
            # 删除多余的文件
            files_to_delete = results[keep_count:]
            deleted_count = 0
            
            for file_info in files_to_delete:
                try:
                    os.remove(file_info['file_path'])
                    deleted_count += 1
                    self.logger.debug(f"删除文件: {file_info['filename']}")
                except Exception as e:
                    self.logger.warning(f"删除文件失败 {file_info['filename']}: {e}")
            
            self.logger.info(f"清理完成，删除了 {deleted_count} 个旧文件")
            
        except Exception as e:
            self.logger.error(f"清理旧结果失败: {e}")
    
    def export_results(self, task_dir: str, export_dir: str):
        """
        导出生成结果到指定目录
        
        Args:
            task_dir: 任务目录
            export_dir: 导出目录
        """
        try:
            ai_dir = os.path.join(task_dir, self.ai_content_dir)
            
            if not os.path.exists(ai_dir):
                raise FileNotFoundError(f"AI内容目录不存在: {ai_dir}")
            
            # 创建导出目录
            os.makedirs(export_dir, exist_ok=True)
            
            # 复制所有文件
            copied_count = 0
            for file_name in os.listdir(ai_dir):
                src_path = os.path.join(ai_dir, file_name)
                dst_path = os.path.join(export_dir, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
                    copied_count += 1
            
            self.logger.info(f"导出完成，复制了 {copied_count} 个文件到 {export_dir}")
            
        except Exception as e:
            self.logger.error(f"导出结果失败: {e}")
            raise


if __name__ == "__main__":
    # 测试代码
    import tempfile
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        file_manager = FileManager()
        
        # 创建测试数据
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 创建测试数据文件
            test_data = {
                'title': '测试标题',
                'description': '测试描述',
                'url': 'https://example.com/test',
                'comments': [
                    {'content': '测试评论1'},
                    {'content': '测试评论2'}
                ],
                'metadata': {'source': 'test'}
            }
            
            data_file = os.path.join(temp_dir, 'data.json')
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            # 测试加载数据
            print("\n测试加载爬虫数据...")
            crawler_data = file_manager.load_crawler_data(temp_dir)
            print(f"加载结果: {json.dumps(crawler_data, ensure_ascii=False, indent=2)}")
            
            # 测试保存结果
            print("\n测试保存生成结果...")
            test_result = {
                'generation_id': 'test_123',
                'platforms': {
                    'douyin': {'title': '抖音标题', 'content': '抖音内容'}
                }
            }
            
            saved_path = file_manager.save_generation_result(temp_dir, test_result, 'content')
            print(f"保存路径: {saved_path}")
            
            # 测试列出结果
            print("\n测试列出生成结果...")
            results = file_manager.list_generation_results(temp_dir)
            for result in results:
                print(f"文件: {result['filename']}, 大小: {result['size']} bytes")
            
    except Exception as e:
        print(f"测试失败: {e}")