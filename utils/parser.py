from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import pandas as pd
import os
import json

class Parser:
    """HTML解析器，负责从网页中提取图片和标题信息"""
    
    def __init__(self):
        """初始化解析器"""
        # 设置日志
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def parse_html(self, html_content, base_url=None):
        """解析HTML内容，提取图片和标题
        
        Args:
            html_content (str): HTML内容
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            dict: 包含标题和图片URL的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取页面标题
        title = soup.title.text.strip() if soup.title else "未知标题"
        self.logger.info(f"页面标题: {title}")
        
        # 提取所有图片
        img_tags = soup.find_all('img')
        self.logger.info(f"找到 {len(img_tags)} 个图片标签")
        
        # 提取图片URL和alt文本
        images = []
        for img in img_tags:
            img_url = img.get('src')
            if not img_url:
                continue
                
            # 处理相对URL
            if base_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            # 提取alt文本作为图片标题
            img_alt = img.get('alt', '').strip()
            
            # 提取图片所在的父元素的文本，可能包含图片描述
            parent_text = ''
            parent = img.parent
            if parent and parent.name != 'body':
                parent_text = parent.get_text(strip=True)
                # 如果父文本太长，可能不是描述，而是页面的一部分
                if len(parent_text) > 200:
                    parent_text = parent_text[:197] + '...'
            
            images.append({
                'url': img_url,
                'alt': img_alt,
                'parent_text': parent_text
            })
        
        # 提取可能的文章标题（h1, h2等）
        headings = []
        for i in range(1, 4):  # h1, h2, h3
            for h in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': h.get_text(strip=True)
                })
        
        return {
            'page_title': title,
            'images': images,
            'headings': headings
        }
    
    def export_to_csv(self, parsed_data, output_dir):
        """将解析结果导出为CSV文件
        
        Args:
            parsed_data (dict): 解析结果
            output_dir (str): 输出目录
            
        Returns:
            str: CSV文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建图片数据框
        if parsed_data['images']:
            df_images = pd.DataFrame(parsed_data['images'])
            csv_path = os.path.join(output_dir, 'images.csv')
            df_images.to_csv(csv_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"图片数据已导出到: {csv_path}")
        else:
            csv_path = None
            self.logger.warning("没有找到图片数据，跳过CSV导出")
        
        # 导出页面信息为JSON
        json_path = os.path.join(output_dir, 'page_info.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"页面信息已导出到: {json_path}")
        
        return csv_path