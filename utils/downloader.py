import os
import requests
from tqdm import tqdm
import logging
from urllib.parse import urlparse, urljoin

class Downloader:
    """图片下载器，负责从URL下载图片并保存到本地"""
    
    def __init__(self, output_dir="output", timeout=10, retry=3):
        """初始化下载器
        
        Args:
            output_dir (str): 图片保存目录
            timeout (int): 请求超时时间（秒）
            retry (int): 失败重试次数
        """
        self.output_dir = output_dir
        self.timeout = timeout
        self.retry = retry
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建输出目录
        self.img_dir = os.path.join(output_dir, 'images')
        os.makedirs(self.img_dir, exist_ok=True)
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def download_image(self, img_url, base_url=None):
        """下载单张图片
        
        Args:
            img_url (str): 图片URL
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            tuple: (是否成功, 本地保存路径或错误信息)
        """
        # 处理相对URL
        if base_url and not img_url.startswith(('http://', 'https://')):
            img_url = urljoin(base_url, img_url)
        
        # 提取文件名
        parsed_url = urlparse(img_url)
        filename = os.path.basename(parsed_url.path)
        
        # 如果文件名为空或没有扩展名，使用URL的哈希值作为文件名
        if not filename or '.' not in filename:
            filename = f"{hash(img_url) & 0xffffffff}.jpg"
        
        # 本地保存路径
        local_path = os.path.join(self.img_dir, filename)
        
        # 已存在则跳过
        if os.path.exists(local_path):
            self.logger.info(f"图片已存在，跳过: {filename}")
            return True, local_path
        
        # 下载图片，带重试
        for attempt in range(self.retry + 1):
            try:
                response = self.session.get(img_url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    return False, f"非图片内容: {content_type}"
                
                # 获取文件大小
                file_size = int(response.headers.get('Content-Length', 0))
                
                # 下载并显示进度条
                with open(local_path, 'wb') as f:
                    if file_size > 0:
                        with tqdm(total=file_size, unit='B', unit_scale=True, 
                                 desc=filename) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        f.write(response.content)
                
                self.logger.info(f"图片下载成功: {filename}")
                return True, local_path
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retry:
                    self.logger.warning(f"下载失败，重试 {attempt+1}/{self.retry}: {img_url}")
                else:
                    self.logger.error(f"下载失败: {img_url}, 错误: {str(e)}")
                    return False, str(e)
    
    def download_images(self, img_urls, base_url=None):
        """批量下载图片
        
        Args:
            img_urls (list): 图片URL列表
            base_url (str, optional): 基础URL，用于处理相对路径
            
        Returns:
            list: 下载成功的图片信息列表，每个元素为包含url和local_path的字典
        """
        results = {}
        downloaded_images = []
        
        for img_url in img_urls:
            success, result = self.download_image(img_url, base_url)
            results[img_url] = {
                'success': success,
                'local_path' if success else 'error': result
            }
            
            # 如果下载成功，添加到下载图片列表
            if success:
                downloaded_images.append({
                    'url': img_url,
                    'local_path': result
                })
        
        # 统计下载结果
        success_count = sum(1 for r in results.values() if r['success'])
        self.logger.info(f"图片下载完成: {success_count}/{len(img_urls)} 成功")
        
        return downloaded_images