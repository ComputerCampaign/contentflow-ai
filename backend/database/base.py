#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础仓储类
"""

from typing import List, Optional, Dict, Any, Type, Union
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc, func
from backend.extensions import db
from backend.database.session import get_db_session, db_transaction
import logging


logger = logging.getLogger(__name__)


class BaseRepository:
    """基础仓储类"""
    
    def __init__(self, model_class: Type[db.Model]):
        self.model_class = model_class
        self.session = get_db_session()
    
    def create(self, **kwargs) -> db.Model:
        """创建记录"""
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            self.session.commit()
            logger.info(f"创建{self.model_class.__name__}记录成功: {instance.id}")
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"创建{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def get_by_id(self, record_id: int) -> Optional[db.Model]:
        """根据ID获取记录"""
        try:
            return self.session.query(self.model_class).filter(
                self.model_class.id == record_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"获取{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def get_by_field(self, field_name: str, value: Any) -> Optional[db.Model]:
        """根据字段获取记录"""
        try:
            field = getattr(self.model_class, field_name)
            return self.session.query(self.model_class).filter(
                field == value
            ).first()
        except (AttributeError, SQLAlchemyError) as e:
            logger.error(f"根据字段获取{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[db.Model]:
        """获取所有记录"""
        try:
            query = self.session.query(self.model_class)
            if offset > 0:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"获取{self.model_class.__name__}所有记录失败: {str(e)}")
            raise
    
    def filter_by(self, **kwargs) -> List[db.Model]:
        """根据条件过滤记录"""
        try:
            return self.session.query(self.model_class).filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            logger.error(f"过滤{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def update(self, record_id: int, **kwargs) -> Optional[db.Model]:
        """更新记录"""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.session.commit()
            logger.info(f"更新{self.model_class.__name__}记录成功: {record_id}")
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"更新{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def delete(self, record_id: int) -> bool:
        """删除记录"""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return False
            
            self.session.delete(instance)
            self.session.commit()
            logger.info(f"删除{self.model_class.__name__}记录成功: {record_id}")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"删除{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def delete_by_field(self, field_name: str, value: Any) -> int:
        """根据字段删除记录"""
        try:
            field = getattr(self.model_class, field_name)
            count = self.session.query(self.model_class).filter(
                field == value
            ).delete()
            self.session.commit()
            logger.info(f"根据字段删除{self.model_class.__name__}记录: {count}条")
            return count
        except (AttributeError, SQLAlchemyError) as e:
            self.session.rollback()
            logger.error(f"根据字段删除{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def count(self, **kwargs) -> int:
        """统计记录数量"""
        try:
            query = self.session.query(self.model_class)
            if kwargs:
                query = query.filter_by(**kwargs)
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"统计{self.model_class.__name__}记录数量失败: {str(e)}")
            raise
    
    def exists(self, **kwargs) -> bool:
        """检查记录是否存在"""
        try:
            return self.session.query(self.model_class).filter_by(**kwargs).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"检查{self.model_class.__name__}记录存在性失败: {str(e)}")
            raise
    
    def paginate(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """分页查询"""
        try:
            query = self.session.query(self.model_class)
            
            # 应用过滤条件
            if filters:
                query = query.filter_by(**filters)
            
            # 计算总数
            total = query.count()
            
            # 分页
            offset = (page - 1) * per_page
            items = query.offset(offset).limit(per_page).all()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'has_prev': page > 1,
                'has_next': page * per_page < total
            }
        except SQLAlchemyError as e:
            logger.error(f"分页查询{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def bulk_create(self, records: List[Dict[str, Any]]) -> List[db.Model]:
        """批量创建记录"""
        try:
            instances = []
            for record_data in records:
                instance = self.model_class(**record_data)
                instances.append(instance)
                self.session.add(instance)
            
            self.session.commit()
            logger.info(f"批量创建{self.model_class.__name__}记录成功: {len(instances)}条")
            return instances
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"批量创建{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新记录"""
        try:
            count = 0
            for update_data in updates:
                record_id = update_data.pop('id', None)
                if record_id:
                    updated = self.session.query(self.model_class).filter(
                        self.model_class.id == record_id
                    ).update(update_data)
                    count += updated
            
            self.session.commit()
            logger.info(f"批量更新{self.model_class.__name__}记录成功: {count}条")
            return count
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"批量更新{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def bulk_delete(self, record_ids: List[int]) -> int:
        """批量删除记录"""
        try:
            count = self.session.query(self.model_class).filter(
                self.model_class.id.in_(record_ids)
            ).delete(synchronize_session=False)
            
            self.session.commit()
            logger.info(f"批量删除{self.model_class.__name__}记录成功: {count}条")
            return count
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"批量删除{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def search(self, search_term: str, search_fields: List[str]) -> List[db.Model]:
        """搜索记录"""
        try:
            conditions = []
            for field_name in search_fields:
                if hasattr(self.model_class, field_name):
                    field = getattr(self.model_class, field_name)
                    conditions.append(field.like(f'%{search_term}%'))
            
            if not conditions:
                return []
            
            return self.session.query(self.model_class).filter(
                or_(*conditions)
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"搜索{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def order_by(self, field_name: str, desc_order: bool = False) -> Query:
        """排序查询"""
        try:
            field = getattr(self.model_class, field_name)
            query = self.session.query(self.model_class)
            
            if desc_order:
                return query.order_by(desc(field))
            else:
                return query.order_by(asc(field))
        except AttributeError as e:
            logger.error(f"排序字段不存在: {field_name}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"排序查询{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def aggregate(self, field_name: str, func_name: str = 'count') -> Any:
        """聚合查询"""
        try:
            field = getattr(self.model_class, field_name)
            
            if func_name == 'count':
                return self.session.query(func.count(field)).scalar()
            elif func_name == 'sum':
                return self.session.query(func.sum(field)).scalar()
            elif func_name == 'avg':
                return self.session.query(func.avg(field)).scalar()
            elif func_name == 'max':
                return self.session.query(func.max(field)).scalar()
            elif func_name == 'min':
                return self.session.query(func.min(field)).scalar()
            else:
                raise ValueError(f"不支持的聚合函数: {func_name}")
        except (AttributeError, SQLAlchemyError) as e:
            logger.error(f"聚合查询{self.model_class.__name__}失败: {str(e)}")
            raise
    
    def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple:
        """获取或创建记录"""
        try:
            instance = self.session.query(self.model_class).filter_by(**kwargs).first()
            
            if instance:
                return instance, False
            else:
                create_data = kwargs.copy()
                if defaults:
                    create_data.update(defaults)
                
                instance = self.model_class(**create_data)
                self.session.add(instance)
                self.session.commit()
                logger.info(f"创建新{self.model_class.__name__}记录: {instance.id}")
                return instance, True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"获取或创建{self.model_class.__name__}记录失败: {str(e)}")
            raise
    
    def refresh(self, instance: db.Model) -> db.Model:
        """刷新实例"""
        try:
            self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            logger.error(f"刷新{self.model_class.__name__}实例失败: {str(e)}")
            raise
    
    def merge(self, instance: db.Model) -> db.Model:
        """合并实例"""
        try:
            merged = self.session.merge(instance)
            self.session.commit()
            return merged
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"合并{self.model_class.__name__}实例失败: {str(e)}")
            raise