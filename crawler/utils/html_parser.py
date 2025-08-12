#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from lxml import etree

# 导入日志配置
from crawler.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class HtmlParser:
    """HTML解析器，负责从网页中提取图片和标题信息"""
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def parse_with_xpath(self, html_content, xpath_selector=None, base_url=None):
        """使用XPath解析HTML内容，提取图片和标题
        
        Args:
            html_content (str): HTML内容
            xpath_selector (str, optional): XPath选择器，用于限定爬取区域
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            dict: 包含标题和图片URL的字典
        """
        try:
            # 使用lxml解析HTML
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            
            # 提取页面标题
            title_elements = tree.xpath('//title/text()')
            title = title_elements[0].strip() if title_elements else "未知标题"
            logger.info(f"页面标题: {title}")
            
            images = []
            
            # 如果提供了XPath选择器，使用XPath提取图片
            if xpath_selector:
                logger.info(f"使用XPath选择器: {xpath_selector}")
                
                # 检查选择器是否直接选择img标签
                if self._is_xpath_selecting_img_directly(xpath_selector):
                    # 直接选择img标签
                    img_elements = tree.xpath(xpath_selector)
                    logger.info(f"XPath直接选择img标签，找到 {len(img_elements)} 个图片")
                else:
                    # 在容器元素内查找img标签
                    container_elements = tree.xpath(xpath_selector)
                    img_elements = []
                    for container in container_elements:
                        img_elements.extend(container.xpath('.//img'))
                    logger.info(f"在容器内查找img标签，找到 {len(img_elements)} 个图片")
                
                # 提取图片信息
                for img in img_elements:
                    img_data = self._extract_image_data(img, base_url, tree)
                    if img_data:
                        images.append(img_data)
            else:
                # 如果没有提供XPath选择器，则在整个页面中查找图片
                img_elements = tree.xpath('//img')
                logger.info(f"在整个页面查找图片，找到 {len(img_elements)} 个图片标签")
                
                for img in img_elements:
                    img_data = self._extract_image_data(img, base_url, tree)
                    if img_data:
                        images.append(img_data)
            
            # 提取可能的文章标题（h1, h2等）
            headings = []
            for i in range(1, 4):  # h1, h2, h3
                for h_text in tree.xpath(f'//h{i}/text()'):
                    headings.append({
                        'level': i,
                        'text': h_text.strip()
                    })
            
            return {
                'page_title': title,
                'page_url': base_url,
                'images': images,
                'headings': headings
            }
            
        except Exception as e:
            logger.error(f"XPath解析失败: {str(e)}")
            return {
                'page_title': "解析失败",
                'page_url': base_url,
                'images': [],
                'headings': []
            }
    
    def _is_xpath_selecting_img_directly(self, xpath):
        """检查XPath是否直接选择img标签"""
        if not isinstance(xpath, str):
            return False
        
        xpath_lower = xpath.lower().strip()
        # 检查是否直接选择img标签
        return (
            xpath_lower.startswith('//img') or 
            xpath_lower.endswith('/img') or 
            xpath_lower.endswith('img') or
            '/img[' in xpath_lower or
            '//img[' in xpath_lower
        )
    
    def _extract_image_data(self, img_element, base_url, tree):
        """从img元素中提取图片数据"""
        try:
            img_url = img_element.get('src')
            if not img_url:
                return None
                
            # 处理相对URL
            if base_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)
            
            # 提取alt文本作为图片标题
            img_alt = img_element.get('alt', '').strip()
            
            # 提取图片所在的父元素的文本
            parent_text = ''
            try:
                parent_elements = tree.xpath(f"//img[@src='{img_element.get('src')}']/parent::*/text()")
                if parent_elements:
                    parent_text = ' '.join([text.strip() for text in parent_elements])
                    if len(parent_text) > 200:
                        parent_text = parent_text[:197] + '...'
            except Exception as e:
                logger.debug(f"提取父元素文本失败: {str(e)}")
            
            return {
                'url': img_url,
                'alt': img_alt,
                'parent_text': parent_text
            }
        except Exception as e:
            logger.debug(f"提取图片数据失败: {str(e)}")
            return None
    
    def parse_comments(self, html_content, base_url=None):
        """解析HTML内容，提取评论数据
        
        Args:
            html_content (str): HTML内容
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            list: 评论数据列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        comments = []
        
        # 通用评论选择器模式
        comment_selectors = [
            # 通用评论区域
            {'selector': '[class*="comment"]', 'type': 'class'},
            {'selector': '[id*="comment"]', 'type': 'id'},
            {'selector': '.comment, .comments', 'type': 'class'},
            # 社交媒体评论
            {'selector': '[data-testid*="tweet"]', 'type': 'attribute'},  # Twitter
            {'selector': '[class*="reply"]', 'type': 'class'},
            {'selector': '[class*="discussion"]', 'type': 'class'},
            # Reddit评论
            {'selector': '[class*="Comment"]', 'type': 'class'},
            {'selector': '[data-testid="comment"]', 'type': 'attribute'},
        ]
        
        for selector_info in comment_selectors:
            try:
                elements = soup.select(selector_info['selector'])
                for element in elements:
                    comment_data = self._extract_comment_data(element, base_url)
                    if comment_data and comment_data not in comments:
                        comments.append(comment_data)
            except Exception as e:
                logger.debug(f"评论选择器 {selector_info['selector']} 解析失败: {str(e)}")
                continue
        
        logger.info(f"提取到 {len(comments)} 条评论")
        return comments
    
    def _extract_comment_data(self, element, base_url=None):
        """从评论元素中提取数据
        
        Args:
            element: BeautifulSoup元素
            base_url: 基础URL
            
        Returns:
            dict: 评论数据
        """
        try:
            # 提取评论文本
            text_content = element.get_text(strip=True)
            if not text_content or len(text_content) < 5:  # 过滤太短的内容
                return None
            
            # 提取作者信息
            author = self._extract_author(element)
            
            # 提取时间信息
            timestamp = self._extract_timestamp(element)
            
            # 提取点赞数等互动数据
            interactions = self._extract_interactions(element)
            
            # 提取回复数据
            replies = self._extract_replies(element, base_url)
            
            return {
                'text': text_content[:500],  # 限制长度
                'author': author,
                'timestamp': timestamp,
                'interactions': interactions,
                'replies_count': len(replies),
                'replies': replies[:5] if replies else [],  # 最多保存5条回复
                'element_class': element.get('class', []),
                'element_id': element.get('id', '')
            }
        except Exception as e:
            logger.debug(f"提取评论数据失败: {str(e)}")
            return None
    
    def _extract_author(self, element):
        """提取评论作者信息"""
        author_selectors = [
            '[class*="author"]',
            '[class*="user"]',
            '[class*="name"]',
            'a[href*="/user/"]',
            'a[href*="/u/"]',
            '.username',
            '.user-name'
        ]
        
        for selector in author_selectors:
            try:
                author_elem = element.select_one(selector)
                if author_elem:
                    return author_elem.get_text(strip=True)
            except:
                continue
        return "匿名用户"
    
    def _extract_timestamp(self, element):
        """提取评论时间戳"""
        time_selectors = [
            'time',
            '[class*="time"]',
            '[class*="date"]',
            '[datetime]',
            '.timestamp'
        ]
        
        for selector in time_selectors:
            try:
                time_elem = element.select_one(selector)
                if time_elem:
                    # 尝试获取datetime属性或文本内容
                    return time_elem.get('datetime') or time_elem.get_text(strip=True)
            except:
                continue
        return None
    
    def _extract_interactions(self, element):
        """提取互动数据（点赞、回复等）"""
        interactions = {}
        
        # 点赞数
        like_selectors = [
            '[class*="like"]',
            '[class*="upvote"]',
            '[class*="heart"]',
            '[aria-label*="like"]'
        ]
        
        for selector in like_selectors:
            try:
                like_elem = element.select_one(selector)
                if like_elem:
                    like_text = like_elem.get_text(strip=True)
                    # 尝试提取数字
                    import re
                    numbers = re.findall(r'\d+', like_text)
                    if numbers:
                        interactions['likes'] = int(numbers[0])
                        break
            except:
                continue
        
        return interactions
    
    def _extract_replies(self, element, base_url=None):
        """提取回复数据"""
        replies = []
        
        # 查找嵌套的回复元素
        reply_selectors = [
            '[class*="reply"]',
            '[class*="child"]',
            '.nested-comment'
        ]
        
        for selector in reply_selectors:
            try:
                reply_elements = element.select(selector)
                for reply_elem in reply_elements[:5]:  # 最多5条回复
                    reply_data = self._extract_comment_data(reply_elem, base_url)
                    if reply_data:
                        replies.append(reply_data)
            except:
                continue
        
        return replies

    def parse_html(self, html_content, base_url=None):
        """解析HTML内容，提取图片、标题和评论
        
        Args:
            html_content (str): HTML内容
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            dict: 包含标题、图片URL和评论的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取页面标题
        title = soup.title.text.strip() if soup.title else "未知标题"
        logger.info(f"页面标题: {title}")
        
        # 提取所有图片
        img_tags = soup.find_all('img')
        logger.info(f"找到 {len(img_tags)} 个图片标签")
        
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
            
            # 提取图片所在的父元素的文本
            parent_text = ''
            parent = img.parent
            if parent:
                parent_text = parent.get_text(strip=True)
                if len(parent_text) > 200:
                    parent_text = parent_text[:197] + '...'
            
            images.append({
                'url': img_url,
                'alt': img_alt,
                'parent_text': parent_text
            })
        
        # 提取评论数据
        comments = self.parse_comments(html_content, base_url)
        
        # 提取页面描述
        description = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '').strip()
        
        return {
            'title': title,
            'description': description,
            'images': images,
            'comments': comments,
            'comments_count': len(comments)
        }