#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接池管理
"""

from typing import Dict, Any, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.exc import SQLAlchemyError
import logging
import time
import threading


logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """数据库连接池管理器"""
    
    def __init__(self):
        self._pools = {}
        self._pool_stats = {}
        self._lock = threading.Lock()
    
    def create_pool(self, 
                   database_url: str,
                   pool_name: str = 'default',
                   pool_size: int = 10,
                   max_overflow: int = 20,
                   pool_timeout: int = 30,
                   pool_recycle: int = 3600,
                   pool_pre_ping: bool = True,
                   **kwargs) -> Engine:
        """创建连接池"""
        try:
            with self._lock:
                if pool_name in self._pools:
                    logger.warning(f"连接池 {pool_name} 已存在，将被替换")
                
                # 创建引擎配置
                engine_config = {
                    'poolclass': QueuePool,
                    'pool_size': pool_size,
                    'max_overflow': max_overflow,
                    'pool_timeout': pool_timeout,
                    'pool_recycle': pool_recycle,
                    'pool_pre_ping': pool_pre_ping,
                    'echo': kwargs.get('echo', False),
                    'echo_pool': kwargs.get('echo_pool', False)
                }
                
                # 合并额外配置
                engine_config.update(kwargs)
                
                # 创建引擎
                engine = create_engine(database_url, **engine_config)
                
                # 注册事件监听器
                self._register_pool_events(engine, pool_name)
                
                # 保存连接池
                self._pools[pool_name] = engine
                self._pool_stats[pool_name] = {
                    'created_at': time.time(),
                    'connections_created': 0,
                    'connections_closed': 0,
                    'connections_checked_out': 0,
                    'connections_checked_in': 0,
                    'pool_timeouts': 0,
                    'pool_errors': 0
                }
                
                logger.info(f"连接池 {pool_name} 创建成功")
                return engine
        
        except Exception as e:
            logger.error(f"创建连接池失败: {str(e)}")
            raise
    
    def get_pool(self, pool_name: str = 'default') -> Optional[Engine]:
        """获取连接池"""
        return self._pools.get(pool_name)
    
    def remove_pool(self, pool_name: str) -> bool:
        """移除连接池"""
        try:
            with self._lock:
                if pool_name in self._pools:
                    engine = self._pools[pool_name]
                    engine.dispose()
                    del self._pools[pool_name]
                    del self._pool_stats[pool_name]
                    logger.info(f"连接池 {pool_name} 已移除")
                    return True
                else:
                    logger.warning(f"连接池 {pool_name} 不存在")
                    return False
        except Exception as e:
            logger.error(f"移除连接池失败: {str(e)}")
            return False
    
    def get_pool_status(self, pool_name: str = 'default') -> Dict[str, Any]:
        """获取连接池状态"""
        try:
            engine = self._pools.get(pool_name)
            if not engine:
                return {'error': f'连接池 {pool_name} 不存在'}
            
            pool = engine.pool
            stats = self._pool_stats.get(pool_name, {})
            
            status = {
                'pool_name': pool_name,
                'pool_class': pool.__class__.__name__,
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid(),
                'statistics': stats,
                'health': self._check_pool_health(pool)
            }
            
            return status
        except Exception as e:
            logger.error(f"获取连接池状态失败: {str(e)}")
            return {'error': str(e)}
    
    def get_all_pools_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有连接池状态"""
        status = {}
        for pool_name in self._pools.keys():
            status[pool_name] = self.get_pool_status(pool_name)
        return status
    
    def _check_pool_health(self, pool) -> Dict[str, Any]:
        """检查连接池健康状态"""
        health = {
            'status': 'healthy',
            'issues': [],
            'recommendations': []
        }
        
        try:
            # 检查连接池使用率
            total_connections = pool.size() + pool.overflow()
            used_connections = pool.checkedout()
            
            if total_connections > 0:
                usage_rate = used_connections / total_connections
                
                if usage_rate > 0.9:
                    health['status'] = 'warning'
                    health['issues'].append('连接池使用率过高 (>90%)')
                    health['recommendations'].append('考虑增加连接池大小或优化查询')
                elif usage_rate > 0.8:
                    health['recommendations'].append('连接池使用率较高，建议监控')
            
            # 检查无效连接
            if pool.invalid() > 0:
                health['status'] = 'warning'
                health['issues'].append(f'存在 {pool.invalid()} 个无效连接')
                health['recommendations'].append('检查数据库连接稳定性')
            
            # 检查溢出连接
            if pool.overflow() > pool.size() * 0.5:
                health['status'] = 'warning'
                health['issues'].append('溢出连接过多')
                health['recommendations'].append('考虑增加基础连接池大小')
        
        except Exception as e:
            health['status'] = 'error'
            health['issues'].append(f'健康检查失败: {str(e)}')
        
        return health
    
    def _register_pool_events(self, engine: Engine, pool_name: str):
        """注册连接池事件监听器"""
        
        @event.listens_for(engine, 'connect')
        def on_connect(dbapi_connection, connection_record):
            """连接创建事件"""
            self._pool_stats[pool_name]['connections_created'] += 1
            logger.debug(f"连接池 {pool_name}: 新连接已创建")
        
        @event.listens_for(engine, 'checkout')
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出事件"""
            self._pool_stats[pool_name]['connections_checked_out'] += 1
            logger.debug(f"连接池 {pool_name}: 连接已检出")
        
        @event.listens_for(engine, 'checkin')
        def on_checkin(dbapi_connection, connection_record):
            """连接检入事件"""
            self._pool_stats[pool_name]['connections_checked_in'] += 1
            logger.debug(f"连接池 {pool_name}: 连接已检入")
        
        @event.listens_for(engine, 'close')
        def on_close(dbapi_connection, connection_record):
            """连接关闭事件"""
            self._pool_stats[pool_name]['connections_closed'] += 1
            logger.debug(f"连接池 {pool_name}: 连接已关闭")
        
        @event.listens_for(engine, 'invalidate')
        def on_invalidate(dbapi_connection, connection_record, exception):
            """连接失效事件"""
            self._pool_stats[pool_name]['pool_errors'] += 1
            logger.warning(f"连接池 {pool_name}: 连接失效 - {str(exception)}")
    
    def optimize_pool(self, pool_name: str) -> Dict[str, Any]:
        """优化连接池"""
        try:
            engine = self._pools.get(pool_name)
            if not engine:
                return {'success': False, 'error': f'连接池 {pool_name} 不存在'}
            
            pool = engine.pool
            stats = self._pool_stats.get(pool_name, {})
            
            recommendations = []
            actions_taken = []
            
            # 分析连接使用模式
            total_checkouts = stats.get('connections_checked_out', 0)
            total_checkins = stats.get('connections_checked_in', 0)
            
            if total_checkouts > 0:
                # 检查连接泄漏
                if total_checkouts > total_checkins * 1.1:
                    recommendations.append('可能存在连接泄漏，检查代码中的连接关闭')
                
                # 检查连接池大小
                current_usage = pool.checkedout()
                if current_usage > pool.size() * 0.8:
                    recommendations.append('考虑增加连接池大小')
            
            # 清理无效连接
            invalid_count = pool.invalid()
            if invalid_count > 0:
                try:
                    # 重新创建连接池可以清理无效连接
                    pool.recreate()
                    actions_taken.append(f'清理了 {invalid_count} 个无效连接')
                except Exception as e:
                    recommendations.append(f'手动清理无效连接失败: {str(e)}')
            
            return {
                'success': True,
                'recommendations': recommendations,
                'actions_taken': actions_taken,
                'current_status': self.get_pool_status(pool_name)
            }
        
        except Exception as e:
            logger.error(f"优化连接池失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def monitor_pools(self) -> Dict[str, Any]:
        """监控所有连接池"""
        try:
            monitoring_data = {
                'timestamp': time.time(),
                'pools': {},
                'summary': {
                    'total_pools': len(self._pools),
                    'healthy_pools': 0,
                    'warning_pools': 0,
                    'error_pools': 0,
                    'total_connections': 0,
                    'active_connections': 0
                }
            }
            
            for pool_name in self._pools.keys():
                pool_status = self.get_pool_status(pool_name)
                monitoring_data['pools'][pool_name] = pool_status
                
                # 更新汇总信息
                if 'error' not in pool_status:
                    health_status = pool_status.get('health', {}).get('status', 'unknown')
                    
                    if health_status == 'healthy':
                        monitoring_data['summary']['healthy_pools'] += 1
                    elif health_status == 'warning':
                        monitoring_data['summary']['warning_pools'] += 1
                    else:
                        monitoring_data['summary']['error_pools'] += 1
                    
                    monitoring_data['summary']['total_connections'] += pool_status.get('size', 0)
                    monitoring_data['summary']['active_connections'] += pool_status.get('checked_out', 0)
                else:
                    monitoring_data['summary']['error_pools'] += 1
            
            return monitoring_data
        
        except Exception as e:
            logger.error(f"监控连接池失败: {str(e)}")
            return {'error': str(e)}
    
    def dispose_all_pools(self):
        """释放所有连接池"""
        try:
            with self._lock:
                for pool_name, engine in self._pools.items():
                    try:
                        engine.dispose()
                        logger.info(f"连接池 {pool_name} 已释放")
                    except Exception as e:
                        logger.error(f"释放连接池 {pool_name} 失败: {str(e)}")
                
                self._pools.clear()
                self._pool_stats.clear()
                logger.info("所有连接池已释放")
        
        except Exception as e:
            logger.error(f"释放所有连接池失败: {str(e)}")


# 全局连接池管理器实例
pool_manager = ConnectionPoolManager()


def get_pool_manager() -> ConnectionPoolManager:
    """获取连接池管理器实例"""
    return pool_manager


def create_optimized_engine(database_url: str, **kwargs) -> Engine:
    """创建优化的数据库引擎"""
    default_config = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'echo': False
    }
    
    # 合并配置
    config = {**default_config, **kwargs}
    
    return pool_manager.create_pool(database_url, **config)