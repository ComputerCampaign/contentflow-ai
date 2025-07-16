#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
邮件通知模块，用于发送爬虫结果通知
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formatdate
import pandas as pd

# 导入配置
from config import config

# 导入日志配置
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__, file_path=__file__)

class EmailNotifier:
    """邮件通知类，用于发送爬虫结果通知"""
    
    def __init__(self):
        """初始化邮件通知器"""
        # 从配置中加载邮件设置
        self.enabled = config.get('email', 'enabled', False)
        self.smtp_server = config.get('email', 'smtp_server', '')
        self.smtp_port = config.get('email', 'smtp_port', 587)
        self.sender_email = config.get('email', 'sender_email', '')
        self.sender_password = config.get('email', 'sender_password', '')
        self.receiver_emails = config.get('email', 'receiver_emails', [])
        self.subject_prefix = config.get('email', 'subject_prefix', '[爬虫通知] ')
        
        # 检查是否启用了邮件通知
        if not self.enabled:
            logger.info("邮件通知功能未启用")
        elif not all([self.smtp_server, self.sender_email, self.receiver_emails]):
            logger.warning("邮件配置不完整，无法发送邮件通知")
            self.enabled = False
    
    def send_notification(self, subject, message, attachments=None, images=None):
        """发送通知邮件
        
        Args:
            subject (str): 邮件主题
            message (str): 邮件正文
            attachments (list, optional): 附件列表，每个元素为(文件路径, 文件名)元组
            images (list, optional): 图片列表，每个元素为(图片路径, 图片ID)元组
            
        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.info("邮件通知功能未启用，跳过发送")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.receiver_emails)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = f"{self.subject_prefix}{subject}"
            
            # 添加正文
            msg.attach(MIMEText(message, 'html'))
            
            # 添加附件
            if attachments:
                for file_path, file_name in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=file_name)
                        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
                        msg.attach(part)
                    else:
                        logger.warning(f"附件不存在: {file_path}")
            
            # 添加图片
            if images:
                for img_path, img_id in images:
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<{img_id}>')
                        msg.attach(img)
                    else:
                        logger.warning(f"图片不存在: {img_path}")
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"邮件已发送至: {', '.join(self.receiver_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def send_crawler_report(self, url, data_dir, success=True):
        """发送爬虫报告
        
        Args:
            url (str): 爬取的URL
            data_dir (str): 数据目录
            success (bool): 爬取是否成功
            
        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.info("邮件通知功能未启用，跳过发送报告")
            return False
        
        # 准备邮件主题
        subject = f"{'成功' if success else '失败'} - {url}"
        
        # 准备邮件正文
        message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
            </style>
        </head>
        <body>
            <h2>爬虫任务报告</h2>
            <p>URL: <a href="{url}">{url}</a></p>
            <p>状态: <span class="{'success' if success else 'failure'}">{'成功' if success else '失败'}</span></p>
        """
        
        # 添加图片信息（如果有）
        csv_path = os.path.join(data_dir, 'images.csv')
        attachments = []
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                message += f"""
                <h3>图片信息</h3>
                <p>共找到 {len(df)} 张图片</p>
                <table>
                    <tr>
                        <th>URL</th>
                        <th>描述</th>
                    </tr>
                """
                
                # 最多显示10张图片信息
                for i, row in df.head(10).iterrows():
                    alt = row.get('alt', '') or '无描述'
                    message += f"""
                    <tr>
                        <td><a href="{row['url']}" target="_blank">{row['url'][:50]}...</a></td>
                        <td>{alt[:100]}</td>
                    </tr>
                    """
                
                if len(df) > 10:
                    message += f"<tr><td colspan='2'>... 还有 {len(df) - 10} 张图片 ...</td></tr>"
                
                message += "</table>"
                
                # 添加CSV文件作为附件
                attachments.append((csv_path, 'images.csv'))
                
            except Exception as e:
                logger.error(f"处理图片CSV文件失败: {str(e)}")
                message += "<p>无法加载图片信息</p>"
        else:
            message += "<p>未找到图片信息</p>"
        
        # 结束邮件正文
        message += """
            <p>详细信息请查看附件。</p>
        </body>
        </html>
        """
        
        # 发送邮件
        return self.send_notification(subject, message, attachments)

# 创建全局通知器实例
notifier = EmailNotifier()

# 导出通知器实例，方便其他模块导入
__all__ = ['notifier']