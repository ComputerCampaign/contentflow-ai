#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
"""

import os
import sys
from app import create_app
from backend.extensions import db


def main():
    """主函数"""
    # 创建应用
    app = create_app()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init-db':
            # 初始化数据库
            with app.app_context():
                db.create_all()
                print('数据库初始化完成')
        
        elif command == 'create-admin':
            # 创建管理员用户
            with app.app_context():
                from backend.models.user import User
                
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    print('管理员用户已存在')
                    return
                
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin'
                )
                admin.set_password('admin123')
                admin.is_active = True
                
                db.session.add(admin)
                db.session.commit()
                print('管理员用户创建成功: admin/admin123')
        
        elif command == 'run':
            # 运行应用
            app.run(
                host=app.config.get('HOST', '0.0.0.0'),
                port=app.config.get('PORT', 5000),
                debug=app.config.get('DEBUG', True)
            )
        
        else:
            print(f'未知命令: {command}')
            print('可用命令: init-db, create-admin, run')
    
    else:
        # 默认运行应用
        app.run(
            host=app.config.get('HOST', '0.0.0.0'),
            port=app.config.get('PORT', 5000),
            debug=app.config.get('DEBUG', True)
        )


if __name__ == '__main__':
    main()