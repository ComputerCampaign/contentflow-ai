#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库会话管理
"""

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from backend.extensions import db
import logging


logger = logging.getLogger(__name__)


def get_db_session():
    """获取数据库会话"""
    return db.session


def close_db_session(session=None):
    """关闭数据库会话"""
    if session is None:
        session = db.session
    
    try:
        session.close()
    except Exception as e:
        logger.error(f"关闭数据库会话失败: {str(e)}")


@contextmanager
def db_transaction(session=None):
    """数据库事务上下文管理器"""
    if session is None:
        session = get_db_session()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"数据库事务失败: {str(e)}")
        raise
    finally:
        session.close()


@contextmanager
def db_session_scope():
    """数据库会话作用域管理器"""
    session = get_db_session()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"数据库操作失败: {str(e)}")
        raise
    finally:
        session.close()


def safe_execute(func, *args, **kwargs):
    """安全执行数据库操作"""
    try:
        return func(*args, **kwargs)
    except SQLAlchemyError as e:
        logger.error(f"数据库操作异常: {str(e)}")
        db.session.rollback()
        raise
    except Exception as e:
        logger.error(f"未知异常: {str(e)}")
        db.session.rollback()
        raise


def batch_execute(operations, session=None):
    """批量执行数据库操作"""
    if session is None:
        session = get_db_session()
    
    results = []
    try:
        for operation in operations:
            if callable(operation):
                result = operation(session)
                results.append(result)
            else:
                logger.warning(f"跳过非可调用操作: {operation}")
        
        session.commit()
        return results
    
    except Exception as e:
        session.rollback()
        logger.error(f"批量操作失败: {str(e)}")
        raise


class DatabaseSession:
    """数据库会话管理类"""
    
    def __init__(self, session=None):
        self.session = session or get_db_session()
        self._auto_commit = True
        self._auto_rollback = True
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self._auto_rollback:
                self.session.rollback()
                logger.error(f"会话回滚: {exc_val}")
        else:
            if self._auto_commit:
                try:
                    self.session.commit()
                except Exception as e:
                    self.session.rollback()
                    logger.error(f"提交失败，已回滚: {str(e)}")
                    raise
        
        self.session.close()
    
    def set_auto_commit(self, auto_commit):
        """设置自动提交"""
        self._auto_commit = auto_commit
        return self
    
    def set_auto_rollback(self, auto_rollback):
        """设置自动回滚"""
        self._auto_rollback = auto_rollback
        return self


def create_session_factory(engine):
    """创建会话工厂"""
    Session = sessionmaker(bind=engine)
    return scoped_session(Session)


def health_check():
    """数据库健康检查"""
    try:
        session = get_db_session()
        session.execute('SELECT 1')
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return False


def get_connection_info():
    """获取数据库连接信息"""
    try:
        engine = db.engine
        return {
            'url': str(engine.url).replace(engine.url.password or '', '***'),
            'pool_size': engine.pool.size(),
            'checked_in': engine.pool.checkedin(),
            'checked_out': engine.pool.checkedout(),
            'overflow': engine.pool.overflow(),
            'invalid': engine.pool.invalid()
        }
    except Exception as e:
        logger.error(f"获取连接信息失败: {str(e)}")
        return {}