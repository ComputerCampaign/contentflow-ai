#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主应用入口文件
"""

import os
import argparse
import logging
from backend import create_app

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    主函数，解析命令行参数并启动应用
    """
    parser = argparse.ArgumentParser(description='爬虫应用服务')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='是否启用调试模式')
    
    args = parser.parse_args()
    
    # 创建并启动Flask应用
    app = create_app()
    logger.info(f"启动Flask应用，地址: {args.host}:{args.port}，调试模式: {args.debug}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()