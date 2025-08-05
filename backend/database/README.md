# 数据库管理层

数据库管理层提供了完整的数据库操作和管理功能，包括基础仓储、查询构建器、连接池管理、迁移管理等核心组件。

## 核心组件

### 1. 基础仓储 (BaseRepository)

提供通用的CRUD操作和数据库交互方法。

```python
from backend.database import BaseRepository
from backend.models.user import User

# 创建用户仓储
user_repo = BaseRepository(User)

# 创建用户
user = user_repo.create(
    username='test_user',
    email='test@example.com',
    password_hash='hashed_password'
)

# 获取用户
user = user_repo.get_by_id(1)
user = user_repo.get_by_field('username', 'test_user')

# 更新用户
user_repo.update(1, email='new_email@example.com')

# 删除用户
user_repo.delete(1)

# 分页查询
result = user_repo.paginate(page=1, per_page=10, is_active=True)
print(f"总数: {result['total']}, 当前页: {result['page']}")

# 批量操作
users_data = [
    {'username': 'user1', 'email': 'user1@example.com'},
    {'username': 'user2', 'email': 'user2@example.com'}
]
user_repo.bulk_create(users_data)
```

### 2. 查询构建器 (QueryBuilder)

提供灵活的查询构建功能。

```python
from backend.database import query
from backend.models.task import Task

# 基础查询
tasks = query(Task).filter_by(status='running').all()

# 复杂查询
tasks = (query(Task)
         .where('status', '=', 'completed')
         .where('created_at', '>=', '2024-01-01')
         .order_by_desc('created_at')
         .limit(10)
         .all())

# 条件查询
tasks = (query(Task)
         .where_in('status', ['pending', 'running'])
         .where_like('name', '%爬虫%')
         .where_not_null('user_id')
         .all())

# 聚合查询
total_tasks = query(Task).count()
avg_duration = query(Task).avg('duration')
max_created = query(Task).max('created_at')

# 分页查询
result = query(Task).where('status', '=', 'completed').paginate(page=1, per_page=20)

# JOIN查询
from backend.models.user import User
tasks_with_users = (query(Task)
                   .join(User, Task.user_id == User.id)
                   .filter(User.is_active == True)
                   .all())

# 原生SQL
results = query(Task).raw_sql(
    "SELECT status, COUNT(*) as count FROM tasks GROUP BY status"
)
```

### 3. 数据库管理器 (DatabaseManager)

提供高级数据库管理功能。

```python
from backend.database import DatabaseManager

db_manager = DatabaseManager()

# 创建所有表
db_manager.create_all_tables()

# 获取表信息
table_info = db_manager.get_table_info('users')
print(f"表行数: {table_info['row_count']}")

# 备份表
db_manager.backup_table('users', 'users_backup_20241201')

# 执行SQL
result = db_manager.execute_query(
    "SELECT COUNT(*) as total FROM users WHERE is_active = :active",
    {'active': True}
)

# 数据库统计
stats = db_manager.get_database_stats()
print(f"总表数: {stats['total_tables']}")
print(f"总行数: {stats['total_rows']}")

# 健康检查
health = db_manager.check_database_health()
if health['status'] != 'healthy':
    print(f"数据库问题: {health['issues']}")

# 清理旧数据
deleted_count = db_manager.cleanup_old_data('logs', 'created_at', days=30)
print(f"清理了 {deleted_count} 条旧日志")
```

### 4. 会话管理 (Session Management)

提供数据库会话的生命周期管理。

```python
from backend.database import db_transaction, db_session_scope, DatabaseSession

# 事务管理
with db_transaction() as session:
    user = User(username='test', email='test@example.com')
    session.add(user)
    # 自动提交或回滚

# 会话作用域
with db_session_scope() as session:
    users = session.query(User).all()
    # 自动关闭会话

# 自定义会话管理
with DatabaseSession().set_auto_commit(False) as session:
    # 手动控制提交
    user = User(username='manual', email='manual@example.com')
    session.add(user)
    session.commit()
```

### 5. 连接池管理 (ConnectionPoolManager)

管理数据库连接池，优化性能。

```python
from backend.database import get_pool_manager

pool_manager = get_pool_manager()

# 创建连接池
engine = pool_manager.create_pool(
    'mysql+pymysql://user:pass@localhost/db',
    pool_name='main',
    pool_size=10,
    max_overflow=20
)

# 获取连接池状态
status = pool_manager.get_pool_status('main')
print(f"连接池大小: {status['size']}")
print(f"已检出连接: {status['checked_out']}")

# 监控所有连接池
monitoring = pool_manager.monitor_pools()
print(f"健康连接池: {monitoring['summary']['healthy_pools']}")

# 优化连接池
optimization = pool_manager.optimize_pool('main')
if optimization['success']:
    print(f"优化建议: {optimization['recommendations']}")
```

### 6. 迁移管理 (MigrationManager)

管理数据库版本控制和迁移。

```python
from backend.database import MigrationManager

migration_manager = MigrationManager()

# 初始化迁移环境
migration_manager.init_migration()

# 创建迁移
migration_manager.create_migration('添加用户表索引')

# 升级数据库
migration_manager.upgrade_database()

# 检查迁移状态
status = migration_manager.check_migration_status()
print(f"当前版本: {status['current_revision']}")
print(f"待执行迁移: {len(status['pending_migrations'])}")

# 验证迁移
validation = migration_manager.validate_migration('abc123')
if not validation['valid']:
    print(f"迁移错误: {validation['errors']}")

# 自动迁移
result = migration_manager.auto_migrate(create_backup=True)
if result['success']:
    print(f"应用了 {len(result['applied_migrations'])} 个迁移")
```

## 最佳实践

### 1. 仓储模式使用

```python
# 为每个模型创建专门的仓储类
class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.get_by_field('email', email)
    
    def find_active_users(self) -> List[User]:
        return self.filter_by(is_active=True)
    
    def search_users(self, keyword: str) -> List[User]:
        return self.search(keyword, ['username', 'email', 'full_name'])

# 使用专门的仓储
user_repo = UserRepository()
user = user_repo.find_by_email('test@example.com')
active_users = user_repo.find_active_users()
```

### 2. 查询优化

```python
# 使用预加载避免N+1查询
tasks = (query(Task)
         .eager_load('user', 'spider_config')
         .filter_by(status='running')
         .all())

# 使用索引字段进行查询
tasks = query(Task).where('user_id', '=', user_id).all()

# 限制查询结果数量
recent_tasks = (query(Task)
                .order_by_desc('created_at')
                .limit(100)
                .all())
```

### 3. 事务管理

```python
# 复杂业务逻辑使用事务
def create_task_with_config(task_data, config_data):
    with db_transaction() as session:
        # 创建爬虫配置
        config = SpiderConfig(**config_data)
        session.add(config)
        session.flush()  # 获取ID但不提交
        
        # 创建任务
        task_data['spider_config_id'] = config.id
        task = Task(**task_data)
        session.add(task)
        
        # 自动提交或回滚
        return task
```

### 4. 连接池配置

```python
# 生产环境连接池配置
engine = pool_manager.create_pool(
    database_url,
    pool_name='production',
    pool_size=20,           # 基础连接数
    max_overflow=30,        # 最大溢出连接
    pool_timeout=60,        # 获取连接超时
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True      # 连接前检查
)
```

### 5. 错误处理

```python
from sqlalchemy.exc import SQLAlchemyError

def safe_database_operation():
    try:
        with db_transaction() as session:
            # 数据库操作
            pass
    except SQLAlchemyError as e:
        logger.error(f"数据库操作失败: {str(e)}")
        # 处理数据库错误
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        # 处理其他错误
```

## 性能优化建议

1. **使用连接池**: 配置合适的连接池大小，避免频繁创建连接
2. **查询优化**: 使用索引字段查询，避免全表扫描
3. **预加载关联**: 使用eager_load避免N+1查询问题
4. **批量操作**: 使用bulk_create、bulk_update进行批量操作
5. **分页查询**: 大数据量查询使用分页，避免内存溢出
6. **定期维护**: 定期清理旧数据，优化表结构

## 监控和维护

```python
# 定期健康检查
def database_health_check():
    db_manager = DatabaseManager()
    health = db_manager.check_database_health()
    
    if health['status'] != 'healthy':
        # 发送告警
        send_alert(f"数据库健康检查失败: {health['issues']}")
    
    return health

# 连接池监控
def monitor_connection_pools():
    pool_manager = get_pool_manager()
    monitoring = pool_manager.monitor_pools()
    
    for pool_name, status in monitoring['pools'].items():
        if status.get('health', {}).get('status') != 'healthy':
            # 记录问题
            logger.warning(f"连接池 {pool_name} 状态异常")
```

这个数据库管理层为Flask应用提供了完整的数据库操作和管理功能，支持高性能、高可用的数据库访问模式。