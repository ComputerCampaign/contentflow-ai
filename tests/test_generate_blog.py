#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试独立博客生成脚本
"""

import os
import sys
import json
import unittest
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入被测试模块
from generate_blog import BlogGenerator, load_metadata, list_available_templates

class TestGenerateBlog(unittest.TestCase):
    """测试博客生成脚本"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # 创建测试图片
        self.test_images = []
        for i in range(3):
            img_path = self.temp_path / f"test_image_{i}.jpg"
            img_path.touch()
            self.test_images.append(str(img_path))
        
        # 创建测试元数据
        self.test_metadata = {
            "title": "测试博客标题",
            "url": "https://example.com/test",
            "source_name": "测试网站",
            "summary": "这是一个测试摘要",
            "content": "这是测试内容\n\n这是第二段",
            "tags": ["测试", "博客"]
        }
        
        self.metadata_path = self.temp_path / "test_metadata.json"
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_metadata, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()
    
    def test_load_metadata(self):
        """测试加载元数据"""
        metadata = load_metadata(str(self.metadata_path))
        self.assertEqual(metadata["title"], "测试博客标题")
        self.assertEqual(metadata["tags"], ["测试", "博客"])
    
    def test_list_templates(self):
        """测试列出模板"""
        templates = list_available_templates()
        self.assertIsInstance(templates, list)
        # 至少应该有默认模板
        self.assertGreaterEqual(len(templates), 1)
    
    def test_generate_blog(self):
        """测试生成博客"""
        # 创建输出路径
        output_path = self.temp_path / "test_blog.md"
        
        # 创建博客生成器
        generator = BlogGenerator()
        
        # 生成博客
        success, blog_path = generator.generate_blog(
            images=self.test_images,
            metadata=self.test_metadata,
            output_path=str(output_path)
        )
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(blog_path))
        
        # 检查博客内容
        with open(blog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("测试博客标题", content)
            self.assertIn("测试网站", content)
            self.assertIn("这是一个测试摘要", content)
            self.assertIn("这是测试内容", content)
    
    def test_generate_blog_with_template(self):
        """测试使用指定模板生成博客"""
        # 创建输出路径
        output_path = self.temp_path / "test_blog_template.md"
        
        # 获取可用模板
        templates = list_available_templates()
        if len(templates) > 1:
            # 使用非默认模板
            template_name = [t for t in templates if t != 'blog_template'][0]
            
            # 创建博客生成器
            generator = BlogGenerator(template_name=template_name)
            
            # 生成博客
            success, blog_path = generator.generate_blog(
                images=self.test_images,
                metadata=self.test_metadata,
                output_path=str(output_path)
            )
            
            # 验证结果
            self.assertTrue(success)
            self.assertTrue(os.path.exists(blog_path))

if __name__ == '__main__':
    unittest.main()