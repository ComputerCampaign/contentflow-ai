#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移管理
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from backend.extensions import db, migrate
from backend.database.session import get_db_session
import logging
import os
import datetime


logger = logging.getLogger(__name__)


class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.session = get_db_session()
        self.engine = db.engine
        self.migration_dir = 'migrations'
    
    def init_migration(self) -> bool:
        """初始化迁移环境"""
        try:
            from flask_migrate import init
            init(directory=self.migration_dir)
            logger.info("迁移环境初始化成功")
            return True
        except Exception as e:
            logger.error(f"迁移环境初始化失败: {str(e)}")
            return False
    
    def create_migration(self, message: str = None) -> bool:
        """创建迁移文件"""
        try:
            from flask_migrate import migrate as create_migrate
            
            if not message:
                message = f"auto_migration_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            create_migrate(directory=self.migration_dir, message=message)
            logger.info(f"迁移文件创建成功: {message}")
            return True
        except Exception as e:
            logger.error(f"创建迁移文件失败: {str(e)}")
            return False
    
    def upgrade_database(self, revision: str = 'head') -> bool:
        """升级数据库"""
        try:
            from flask_migrate import upgrade
            upgrade(directory=self.migration_dir, revision=revision)
            logger.info(f"数据库升级成功: {revision}")
            return True
        except Exception as e:
            logger.error(f"数据库升级失败: {str(e)}")
            return False
    
    def downgrade_database(self, revision: str) -> bool:
        """降级数据库"""
        try:
            from flask_migrate import downgrade
            downgrade(directory=self.migration_dir, revision=revision)
            logger.info(f"数据库降级成功: {revision}")
            return True
        except Exception as e:
            logger.error(f"数据库降级失败: {str(e)}")
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """获取当前数据库版本"""
        try:
            from flask_migrate import current
            return current(directory=self.migration_dir)
        except Exception as e:
            logger.error(f"获取当前版本失败: {str(e)}")
            return None
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """获取迁移历史"""
        try:
            from flask_migrate import history
            history_output = history(directory=self.migration_dir)
            
            # 解析历史输出
            migrations = []
            if history_output:
                for line in history_output.split('\n'):
                    if line.strip() and '->' in line:
                        parts = line.split('->')
                        if len(parts) >= 2:
                            migrations.append({
                                'revision': parts[0].strip(),
                                'description': parts[1].strip() if len(parts) > 1 else '',
                                'timestamp': datetime.datetime.now().isoformat()
                            })
            
            return migrations
        except Exception as e:
            logger.error(f"获取迁移历史失败: {str(e)}")
            return []
    
    def check_migration_status(self) -> Dict[str, Any]:
        """检查迁移状态"""
        try:
            current_rev = self.get_current_revision()
            history = self.get_migration_history()
            
            # 检查是否有待执行的迁移
            pending_migrations = self._get_pending_migrations()
            
            return {
                'current_revision': current_rev,
                'migration_history': history,
                'pending_migrations': pending_migrations,
                'is_up_to_date': len(pending_migrations) == 0
            }
        except Exception as e:
            logger.error(f"检查迁移状态失败: {str(e)}")
            return {}
    
    def _get_pending_migrations(self) -> List[str]:
        """获取待执行的迁移"""
        try:
            # 检查migrations目录下的文件
            if not os.path.exists(self.migration_dir):
                return []
            
            versions_dir = os.path.join(self.migration_dir, 'versions')
            if not os.path.exists(versions_dir):
                return []
            
            # 获取所有迁移文件
            migration_files = []
            for filename in os.listdir(versions_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    migration_files.append(filename)
            
            # 检查哪些迁移尚未执行
            current_rev = self.get_current_revision()
            pending = []
            
            for migration_file in sorted(migration_files):
                revision = migration_file.split('_')[0]
                if not current_rev or revision > current_rev:
                    pending.append(migration_file)
            
            return pending
        except Exception as e:
            logger.error(f"获取待执行迁移失败: {str(e)}")
            return []
    
    def validate_migration(self, revision: str) -> Dict[str, Any]:
        """验证迁移"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查迁移文件是否存在
            migration_file = self._find_migration_file(revision)
            if not migration_file:
                validation_result['valid'] = False
                validation_result['errors'].append(f"迁移文件不存在: {revision}")
                return validation_result
            
            # 检查迁移文件语法
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, migration_file, 'exec')
            except SyntaxError as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"迁移文件语法错误: {str(e)}")
            
            # 检查依赖关系
            dependencies = self._check_migration_dependencies(revision)
            if dependencies['missing']:
                validation_result['warnings'].append(
                    f"缺少依赖迁移: {', '.join(dependencies['missing'])}"
                )
            
            return validation_result
        except Exception as e:
            logger.error(f"验证迁移失败: {str(e)}")
            return {'valid': False, 'errors': [str(e)], 'warnings': []}
    
    def _find_migration_file(self, revision: str) -> Optional[str]:
        """查找迁移文件"""
        try:
            versions_dir = os.path.join(self.migration_dir, 'versions')
            if not os.path.exists(versions_dir):
                return None
            
            for filename in os.listdir(versions_dir):
                if filename.startswith(revision) and filename.endswith('.py'):
                    return os.path.join(versions_dir, filename)
            
            return None
        except Exception:
            return None
    
    def _check_migration_dependencies(self, revision: str) -> Dict[str, List[str]]:
        """检查迁移依赖"""
        try:
            migration_file = self._find_migration_file(revision)
            if not migration_file:
                return {'missing': [], 'satisfied': []}
            
            # 读取迁移文件内容
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找down_revision
            missing = []
            satisfied = []
            
            import re
            down_revision_match = re.search(r"down_revision = ['\"]([^'\"]*)['\"]", content)
            if down_revision_match:
                down_revision = down_revision_match.group(1)
                if down_revision and down_revision != 'None':
                    if self._find_migration_file(down_revision):
                        satisfied.append(down_revision)
                    else:
                        missing.append(down_revision)
            
            return {'missing': missing, 'satisfied': satisfied}
        except Exception as e:
            logger.error(f"检查迁移依赖失败: {str(e)}")
            return {'missing': [], 'satisfied': []}
    
    def backup_before_migration(self) -> bool:
        """迁移前备份"""
        try:
            from backend.database.manager import DatabaseManager
            
            db_manager = DatabaseManager()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 备份所有表
            table_names = db_manager.get_table_names()
            backup_success = True
            
            for table_name in table_names:
                backup_name = f"{table_name}_migration_backup_{timestamp}"
                if not db_manager.backup_table(table_name, backup_name):
                    backup_success = False
                    logger.error(f"备份表失败: {table_name}")
            
            if backup_success:
                logger.info(f"迁移前备份完成: {timestamp}")
            
            return backup_success
        except Exception as e:
            logger.error(f"迁移前备份失败: {str(e)}")
            return False
    
    def rollback_migration(self, backup_timestamp: str) -> bool:
        """回滚迁移"""
        try:
            from backend.database.manager import DatabaseManager
            
            db_manager = DatabaseManager()
            table_names = db_manager.get_table_names()
            rollback_success = True
            
            for table_name in table_names:
                backup_name = f"{table_name}_migration_backup_{backup_timestamp}"
                if db_manager.table_exists(backup_name):
                    if not db_manager.restore_table(table_name, backup_name):
                        rollback_success = False
                        logger.error(f"回滚表失败: {table_name}")
                else:
                    logger.warning(f"备份表不存在: {backup_name}")
            
            if rollback_success:
                logger.info(f"迁移回滚完成: {backup_timestamp}")
            
            return rollback_success
        except Exception as e:
            logger.error(f"迁移回滚失败: {str(e)}")
            return False
    
    def auto_migrate(self, create_backup: bool = True) -> Dict[str, Any]:
        """自动迁移"""
        result = {
            'success': False,
            'backup_timestamp': None,
            'applied_migrations': [],
            'errors': []
        }
        
        try:
            # 检查待执行的迁移
            pending_migrations = self._get_pending_migrations()
            if not pending_migrations:
                result['success'] = True
                result['message'] = '没有待执行的迁移'
                return result
            
            # 创建备份
            if create_backup:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                if self.backup_before_migration():
                    result['backup_timestamp'] = timestamp
                else:
                    result['errors'].append('备份失败')
                    return result
            
            # 执行迁移
            if self.upgrade_database():
                result['success'] = True
                result['applied_migrations'] = pending_migrations
                logger.info(f"自动迁移完成，应用了 {len(pending_migrations)} 个迁移")
            else:
                result['errors'].append('迁移执行失败')
            
        except Exception as e:
            result['errors'].append(str(e))
            logger.error(f"自动迁移失败: {str(e)}")
        
        return result
    
    def get_migration_info(self) -> Dict[str, Any]:
        """获取迁移信息"""
        try:
            return {
                'migration_directory': self.migration_dir,
                'current_revision': self.get_current_revision(),
                'migration_status': self.check_migration_status(),
                'database_tables': self._get_database_tables_info()
            }
        except Exception as e:
            logger.error(f"获取迁移信息失败: {str(e)}")
            return {}
    
    def _get_database_tables_info(self) -> List[Dict[str, Any]]:
        """获取数据库表信息"""
        try:
            inspector = inspect(self.engine)
            tables_info = []
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables_info.append({
                    'name': table_name,
                    'columns': len(columns),
                    'column_names': [col['name'] for col in columns]
                })
            
            return tables_info
        except Exception as e:
            logger.error(f"获取数据库表信息失败: {str(e)}")
            return []