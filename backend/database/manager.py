#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
"""

from typing import Dict, List, Any, Optional, Type
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from backend.extensions import db
from backend.database.session import get_db_session, db_transaction
from backend.database.base import BaseRepository
import logging
import datetime


logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.session = get_db_session()
        self.engine = db.engine
        self.metadata = db.metadata
        self._repositories = {}
    
    def get_repository(self, model_class: Type[db.Model]) -> BaseRepository:
        """获取模型仓储"""
        model_name = model_class.__name__
        if model_name not in self._repositories:
            self._repositories[model_name] = BaseRepository(model_class)
        return self._repositories[model_name]
    
    def create_all_tables(self) -> bool:
        """创建所有表"""
        try:
            db.create_all()
            logger.info("所有数据表创建成功")
            return True
        except SQLAlchemyError as e:
            logger.error(f"创建数据表失败: {str(e)}")
            return False
    
    def drop_all_tables(self) -> bool:
        """删除所有表"""
        try:
            db.drop_all()
            logger.info("所有数据表删除成功")
            return True
        except SQLAlchemyError as e:
            logger.error(f"删除数据表失败: {str(e)}")
            return False
    
    def get_table_names(self) -> List[str]:
        """获取所有表名"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except SQLAlchemyError as e:
            logger.error(f"获取表名失败: {str(e)}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except SQLAlchemyError as e:
            logger.error(f"检查表存在性失败: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        try:
            inspector = inspect(self.engine)
            
            if not self.table_exists(table_name):
                return {}
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            primary_key = inspector.get_pk_constraint(table_name)
            
            return {
                'name': table_name,
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys,
                'primary_key': primary_key,
                'row_count': self.get_table_row_count(table_name)
            }
        except SQLAlchemyError as e:
            logger.error(f"获取表信息失败: {str(e)}")
            return {}
    
    def get_table_row_count(self, table_name: str) -> int:
        """获取表行数"""
        try:
            result = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"获取表行数失败: {str(e)}")
            return 0
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行SQL语句"""
        try:
            if params:
                result = self.session.execute(text(sql), params)
            else:
                result = self.session.execute(text(sql))
            
            self.session.commit()
            logger.info(f"SQL执行成功: {sql[:100]}...")
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"SQL执行失败: {str(e)}")
            raise
    
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行查询SQL"""
        try:
            if params:
                result = self.session.execute(text(sql), params)
            else:
                result = self.session.execute(text(sql))
            
            # 转换为字典列表
            columns = result.keys()
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row)))
            
            logger.info(f"查询执行成功: {sql[:100]}...")
            return rows
        except SQLAlchemyError as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise
    
    def backup_table(self, table_name: str, backup_name: Optional[str] = None) -> bool:
        """备份表"""
        try:
            if not backup_name:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{table_name}_backup_{timestamp}"
            
            sql = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"
            self.execute_sql(sql)
            
            logger.info(f"表备份成功: {table_name} -> {backup_name}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"表备份失败: {str(e)}")
            return False
    
    def restore_table(self, table_name: str, backup_name: str) -> bool:
        """恢复表"""
        try:
            # 删除原表
            self.execute_sql(f"DROP TABLE IF EXISTS {table_name}")
            
            # 从备份恢复
            self.execute_sql(f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}")
            
            logger.info(f"表恢复成功: {backup_name} -> {table_name}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"表恢复失败: {str(e)}")
            return False
    
    def truncate_table(self, table_name: str) -> bool:
        """清空表"""
        try:
            self.execute_sql(f"TRUNCATE TABLE {table_name}")
            logger.info(f"表清空成功: {table_name}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"表清空失败: {str(e)}")
            return False
    
    def optimize_table(self, table_name: str) -> bool:
        """优化表"""
        try:
            # MySQL优化表
            self.execute_sql(f"OPTIMIZE TABLE {table_name}")
            logger.info(f"表优化成功: {table_name}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"表优化失败: {str(e)}")
            return False
    
    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """分析表"""
        try:
            # 获取表统计信息
            stats = {
                'row_count': self.get_table_row_count(table_name),
                'table_info': self.get_table_info(table_name)
            }
            
            # 获取表大小（MySQL）
            try:
                size_query = """
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                FROM information_schema.TABLES 
                WHERE table_schema = DATABASE() AND table_name = :table_name
                """
                result = self.execute_query(size_query, {'table_name': table_name})
                if result:
                    stats['size_mb'] = result[0]['size_mb']
            except:
                stats['size_mb'] = 0
            
            logger.info(f"表分析完成: {table_name}")
            return stats
        except SQLAlchemyError as e:
            logger.error(f"表分析失败: {str(e)}")
            return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            stats = {
                'tables': [],
                'total_tables': 0,
                'total_rows': 0,
                'database_size_mb': 0
            }
            
            table_names = self.get_table_names()
            stats['total_tables'] = len(table_names)
            
            for table_name in table_names:
                table_stats = self.analyze_table(table_name)
                stats['tables'].append({
                    'name': table_name,
                    'rows': table_stats.get('row_count', 0),
                    'size_mb': table_stats.get('size_mb', 0)
                })
                stats['total_rows'] += table_stats.get('row_count', 0)
                stats['database_size_mb'] += table_stats.get('size_mb', 0)
            
            return stats
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {str(e)}")
            return {}
    
    def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        health_status = {
            'status': 'healthy',
            'issues': [],
            'recommendations': []
        }
        
        try:
            # 检查连接
            self.session.execute(text('SELECT 1'))
            
            # 检查表状态
            table_names = self.get_table_names()
            if not table_names:
                health_status['issues'].append('没有找到任何数据表')
                health_status['status'] = 'warning'
            
            # 检查每个表的状态
            for table_name in table_names:
                try:
                    row_count = self.get_table_row_count(table_name)
                    if row_count == 0:
                        health_status['recommendations'].append(f'表 {table_name} 为空')
                except Exception as e:
                    health_status['issues'].append(f'表 {table_name} 访问异常: {str(e)}')
                    health_status['status'] = 'error'
            
            # 检查连接池状态
            try:
                pool = self.engine.pool
                if hasattr(pool, 'checkedout') and pool.checkedout() > pool.size() * 0.8:
                    health_status['issues'].append('数据库连接池使用率过高')
                    health_status['status'] = 'warning'
            except:
                pass
            
        except Exception as e:
            health_status['status'] = 'error'
            health_status['issues'].append(f'数据库连接失败: {str(e)}')
        
        return health_status
    
    def cleanup_old_data(self, table_name: str, date_field: str, days: int = 30) -> int:
        """清理旧数据"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            sql = f"DELETE FROM {table_name} WHERE {date_field} < :cutoff_date"
            result = self.execute_sql(sql, {'cutoff_date': cutoff_date})
            
            deleted_count = result.rowcount if result else 0
            logger.info(f"清理旧数据完成: {table_name}, 删除 {deleted_count} 条记录")
            return deleted_count
        except SQLAlchemyError as e:
            logger.error(f"清理旧数据失败: {str(e)}")
            return 0
    
    def vacuum_database(self) -> bool:
        """数据库清理"""
        try:
            # 对于MySQL，执行优化操作
            table_names = self.get_table_names()
            for table_name in table_names:
                self.optimize_table(table_name)
            
            logger.info("数据库清理完成")
            return True
        except Exception as e:
            logger.error(f"数据库清理失败: {str(e)}")
            return False
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢查询（MySQL）"""
        try:
            sql = """
            SELECT 
                sql_text,
                exec_count,
                avg_timer_wait/1000000000 as avg_time_sec,
                sum_timer_wait/1000000000 as total_time_sec
            FROM performance_schema.events_statements_summary_by_digest 
            ORDER BY avg_timer_wait DESC 
            LIMIT :limit
            """
            return self.execute_query(sql, {'limit': limit})
        except Exception as e:
            logger.error(f"获取慢查询失败: {str(e)}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        try:
            self.session.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")