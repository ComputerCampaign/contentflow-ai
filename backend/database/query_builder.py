#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库查询构建器
"""

from typing import List, Dict, Any, Optional, Union, Type
from sqlalchemy.orm import Query, joinedload, selectinload
from sqlalchemy import and_, or_, not_, func, desc, asc, text
from sqlalchemy.sql import operators
from backend.extensions import db
from backend.database.session import get_db_session
import logging


logger = logging.getLogger(__name__)


class QueryBuilder:
    """查询构建器"""
    
    def __init__(self, model_class: Type[db.Model], session=None):
        self.model_class = model_class
        self.session = session or get_db_session()
        self._query = self.session.query(model_class)
        self._joins = []
        self._filters = []
        self._orders = []
        self._groups = []
        self._havings = []
        self._limit_value = None
        self._offset_value = None
        self._distinct_value = False
    
    def filter(self, *conditions) -> 'QueryBuilder':
        """添加过滤条件"""
        self._filters.extend(conditions)
        return self
    
    def filter_by(self, **kwargs) -> 'QueryBuilder':
        """根据字段过滤"""
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                field = getattr(self.model_class, key)
                self._filters.append(field == value)
        return self
    
    def where(self, field_name: str, operator: str, value: Any) -> 'QueryBuilder':
        """添加WHERE条件"""
        try:
            field = getattr(self.model_class, field_name)
            
            if operator == '=':
                condition = field == value
            elif operator == '!=':
                condition = field != value
            elif operator == '>':
                condition = field > value
            elif operator == '>=':
                condition = field >= value
            elif operator == '<':
                condition = field < value
            elif operator == '<=':
                condition = field <= value
            elif operator == 'like':
                condition = field.like(value)
            elif operator == 'ilike':
                condition = field.ilike(value)
            elif operator == 'in':
                condition = field.in_(value)
            elif operator == 'not_in':
                condition = ~field.in_(value)
            elif operator == 'is_null':
                condition = field.is_(None)
            elif operator == 'is_not_null':
                condition = field.isnot(None)
            elif operator == 'between':
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    condition = field.between(value[0], value[1])
                else:
                    raise ValueError("between操作符需要包含两个值的列表或元组")
            else:
                raise ValueError(f"不支持的操作符: {operator}")
            
            self._filters.append(condition)
            return self
        
        except AttributeError:
            raise ValueError(f"字段 {field_name} 不存在于模型 {self.model_class.__name__}")
    
    def where_in(self, field_name: str, values: List[Any]) -> 'QueryBuilder':
        """IN条件"""
        return self.where(field_name, 'in', values)
    
    def where_not_in(self, field_name: str, values: List[Any]) -> 'QueryBuilder':
        """NOT IN条件"""
        return self.where(field_name, 'not_in', values)
    
    def where_like(self, field_name: str, pattern: str) -> 'QueryBuilder':
        """LIKE条件"""
        return self.where(field_name, 'like', pattern)
    
    def where_between(self, field_name: str, start: Any, end: Any) -> 'QueryBuilder':
        """BETWEEN条件"""
        return self.where(field_name, 'between', [start, end])
    
    def where_null(self, field_name: str) -> 'QueryBuilder':
        """IS NULL条件"""
        return self.where(field_name, 'is_null', None)
    
    def where_not_null(self, field_name: str) -> 'QueryBuilder':
        """IS NOT NULL条件"""
        return self.where(field_name, 'is_not_null', None)
    
    def or_where(self, *conditions) -> 'QueryBuilder':
        """OR条件"""
        if conditions:
            self._filters.append(or_(*conditions))
        return self
    
    def and_where(self, *conditions) -> 'QueryBuilder':
        """AND条件"""
        if conditions:
            self._filters.append(and_(*conditions))
        return self
    
    def join(self, *args, **kwargs) -> 'QueryBuilder':
        """JOIN操作"""
        self._joins.append(('join', args, kwargs))
        return self
    
    def left_join(self, *args, **kwargs) -> 'QueryBuilder':
        """LEFT JOIN操作"""
        self._joins.append(('outerjoin', args, kwargs))
        return self
    
    def order_by(self, field_name: str, direction: str = 'asc') -> 'QueryBuilder':
        """排序"""
        try:
            field = getattr(self.model_class, field_name)
            if direction.lower() == 'desc':
                self._orders.append(desc(field))
            else:
                self._orders.append(asc(field))
            return self
        except AttributeError:
            raise ValueError(f"字段 {field_name} 不存在于模型 {self.model_class.__name__}")
    
    def order_by_desc(self, field_name: str) -> 'QueryBuilder':
        """降序排序"""
        return self.order_by(field_name, 'desc')
    
    def order_by_asc(self, field_name: str) -> 'QueryBuilder':
        """升序排序"""
        return self.order_by(field_name, 'asc')
    
    def group_by(self, *field_names) -> 'QueryBuilder':
        """分组"""
        for field_name in field_names:
            try:
                field = getattr(self.model_class, field_name)
                self._groups.append(field)
            except AttributeError:
                raise ValueError(f"字段 {field_name} 不存在于模型 {self.model_class.__name__}")
        return self
    
    def having(self, condition) -> 'QueryBuilder':
        """HAVING条件"""
        self._havings.append(condition)
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """限制结果数量"""
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """偏移量"""
        self._offset_value = count
        return self
    
    def distinct(self, *columns) -> 'QueryBuilder':
        """去重"""
        self._distinct_value = True
        if columns:
            self._query = self._query.distinct(*columns)
        return self
    
    def with_entities(self, *entities) -> 'QueryBuilder':
        """指定查询字段"""
        self._query = self._query.with_entities(*entities)
        return self
    
    def eager_load(self, *relationships) -> 'QueryBuilder':
        """预加载关联关系"""
        for relationship in relationships:
            self._query = self._query.options(joinedload(relationship))
        return self
    
    def select_load(self, *relationships) -> 'QueryBuilder':
        """选择性加载关联关系"""
        for relationship in relationships:
            self._query = self._query.options(selectinload(relationship))
        return self
    
    def build_query(self) -> Query:
        """构建最终查询"""
        query = self._query
        
        # 应用JOIN
        for join_type, args, kwargs in self._joins:
            if join_type == 'join':
                query = query.join(*args, **kwargs)
            elif join_type == 'outerjoin':
                query = query.outerjoin(*args, **kwargs)
        
        # 应用过滤条件
        if self._filters:
            query = query.filter(and_(*self._filters))
        
        # 应用分组
        if self._groups:
            query = query.group_by(*self._groups)
        
        # 应用HAVING条件
        if self._havings:
            query = query.having(and_(*self._havings))
        
        # 应用排序
        if self._orders:
            query = query.order_by(*self._orders)
        
        # 应用去重
        if self._distinct_value and not hasattr(query, '_distinct'):
            query = query.distinct()
        
        # 应用偏移量
        if self._offset_value is not None:
            query = query.offset(self._offset_value)
        
        # 应用限制
        if self._limit_value is not None:
            query = query.limit(self._limit_value)
        
        return query
    
    def get(self) -> Optional[db.Model]:
        """获取单个结果"""
        try:
            return self.build_query().first()
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise
    
    def all(self) -> List[db.Model]:
        """获取所有结果"""
        try:
            return self.build_query().all()
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise
    
    def count(self) -> int:
        """统计数量"""
        try:
            # 构建计数查询
            query = self.session.query(self.model_class)
            
            # 应用JOIN
            for join_type, args, kwargs in self._joins:
                if join_type == 'join':
                    query = query.join(*args, **kwargs)
                elif join_type == 'outerjoin':
                    query = query.outerjoin(*args, **kwargs)
            
            # 应用过滤条件
            if self._filters:
                query = query.filter(and_(*self._filters))
            
            return query.count()
        except Exception as e:
            logger.error(f"计数查询失败: {str(e)}")
            raise
    
    def exists(self) -> bool:
        """检查是否存在"""
        try:
            return self.build_query().first() is not None
        except Exception as e:
            logger.error(f"存在性查询失败: {str(e)}")
            raise
    
    def paginate(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """分页查询"""
        try:
            # 计算总数
            total = self.count()
            
            # 计算偏移量
            offset = (page - 1) * per_page
            
            # 获取分页数据
            items = self.offset(offset).limit(per_page).all()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'has_prev': page > 1,
                'has_next': page * per_page < total
            }
        except Exception as e:
            logger.error(f"分页查询失败: {str(e)}")
            raise
    
    def aggregate(self, func_name: str, field_name: str) -> Any:
        """聚合查询"""
        try:
            field = getattr(self.model_class, field_name)
            
            if func_name == 'count':
                agg_func = func.count(field)
            elif func_name == 'sum':
                agg_func = func.sum(field)
            elif func_name == 'avg':
                agg_func = func.avg(field)
            elif func_name == 'max':
                agg_func = func.max(field)
            elif func_name == 'min':
                agg_func = func.min(field)
            else:
                raise ValueError(f"不支持的聚合函数: {func_name}")
            
            query = self.session.query(agg_func)
            
            # 应用JOIN
            for join_type, args, kwargs in self._joins:
                if join_type == 'join':
                    query = query.select_from(self.model_class).join(*args, **kwargs)
                elif join_type == 'outerjoin':
                    query = query.select_from(self.model_class).outerjoin(*args, **kwargs)
            
            # 应用过滤条件
            if self._filters:
                query = query.filter(and_(*self._filters))
            
            return query.scalar()
        
        except AttributeError:
            raise ValueError(f"字段 {field_name} 不存在于模型 {self.model_class.__name__}")
        except Exception as e:
            logger.error(f"聚合查询失败: {str(e)}")
            raise
    
    def sum(self, field_name: str) -> Any:
        """求和"""
        return self.aggregate('sum', field_name)
    
    def avg(self, field_name: str) -> Any:
        """平均值"""
        return self.aggregate('avg', field_name)
    
    def max(self, field_name: str) -> Any:
        """最大值"""
        return self.aggregate('max', field_name)
    
    def min(self, field_name: str) -> Any:
        """最小值"""
        return self.aggregate('min', field_name)
    
    def raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行原生SQL"""
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
            
            return rows
        except Exception as e:
            logger.error(f"原生SQL查询失败: {str(e)}")
            raise
    
    def clone(self) -> 'QueryBuilder':
        """克隆查询构建器"""
        new_builder = QueryBuilder(self.model_class, self.session)
        new_builder._filters = self._filters.copy()
        new_builder._joins = self._joins.copy()
        new_builder._orders = self._orders.copy()
        new_builder._groups = self._groups.copy()
        new_builder._havings = self._havings.copy()
        new_builder._limit_value = self._limit_value
        new_builder._offset_value = self._offset_value
        new_builder._distinct_value = self._distinct_value
        return new_builder
    
    def reset(self) -> 'QueryBuilder':
        """重置查询构建器"""
        self._query = self.session.query(self.model_class)
        self._joins = []
        self._filters = []
        self._orders = []
        self._groups = []
        self._havings = []
        self._limit_value = None
        self._offset_value = None
        self._distinct_value = False
        return self
    
    def to_sql(self) -> str:
        """获取SQL语句"""
        try:
            query = self.build_query()
            return str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        except Exception as e:
            logger.error(f"生成SQL失败: {str(e)}")
            return str(self.build_query())


def query(model_class: Type[db.Model], session=None) -> QueryBuilder:
    """创建查询构建器"""
    return QueryBuilder(model_class, session)