# Airflow 工作流调度平台

本模块提供了基于Apache Airflow的工作流调度平台，用于管理和调度爬虫平台的各种任务。

## 目录结构

```
airflow/
├── README.md                 # 本文档
├── dags/                     # DAG定义目录
│   └── example_crawler_dag.py # 示例爬虫DAG
├── config/                   # 配置文件目录
│   └── .env.example         # 环境变量示例
├── docker/                   # Docker构建文件
│   ├── Dockerfile           # Airflow镜像构建文件
│   ├── requirements.txt     # Python依赖
│   ├── airflow.cfg         # Airflow主配置文件
│   ├── webserver_config.py # Web服务器配置
│   └── entrypoint.sh       # 容器启动脚本
├── logs/                     # 日志目录
├── plugins/                  # 插件目录
└── scripts/                  # 管理脚本
    └── airflow-manager.sh   # Airflow管理脚本
```

## 功能特性

### 核心功能
- **工作流调度**: 支持复杂的DAG工作流定义和调度
- **任务管理**: 提供任务执行、监控、重试等功能
- **数据库集成**: 与MySQL数据库深度集成
- **Web界面**: 提供直观的Web管理界面
- **日志管理**: 完整的任务执行日志记录

### 技术特性
- **容器化部署**: 基于Docker的完整容器化方案
- **高可用性**: 支持多实例部署和负载均衡
- **安全认证**: 内置用户认证和权限管理
- **扩展性**: 支持自定义插件和操作符
- **监控告警**: 集成健康检查和邮件通知

## 快速开始

### 1. 环境准备

确保已安装以下依赖：
- Docker >= 20.10
- Docker Compose >= 2.0
- 至少4GB可用内存

### 2. 配置环境变量

```bash
# 复制环境变量文件
cp deploy/envs/.env.example deploy/envs/.env
cp airflow/config/.env.example airflow/config/.env

# 编辑配置文件（可选）
vim deploy/envs/.env
```

### 3. 启动服务

使用管理脚本启动Airflow服务：

```bash
# 初始化环境
./airflow/scripts/airflow-manager.sh init

# 构建镜像
./airflow/scripts/airflow-manager.sh build

# 启动服务
./airflow/scripts/airflow-manager.sh start -d
```

### 4. 访问Web界面

服务启动后，可以通过以下地址访问：

- **Airflow Web UI**: http://localhost:8080
- **默认用户名**: admin
- **默认密码**: admin123

## 管理脚本使用

`airflow-manager.sh` 脚本提供了完整的Airflow管理功能：

### 基本命令

```bash
# 查看帮助
./airflow/scripts/airflow-manager.sh --help

# 启动服务
./airflow/scripts/airflow-manager.sh start

# 停止服务
./airflow/scripts/airflow-manager.sh stop

# 重启服务
./airflow/scripts/airflow-manager.sh restart

# 查看状态
./airflow/scripts/airflow-manager.sh status

# 查看日志
./airflow/scripts/airflow-manager.sh logs
```

### 高级命令

```bash
# 进入容器
./airflow/scripts/airflow-manager.sh shell webserver

# 创建用户
./airflow/scripts/airflow-manager.sh create-user newuser

# 列出DAG
./airflow/scripts/airflow-manager.sh list-dags

# 测试DAG
./airflow/scripts/airflow-manager.sh test-dag example_crawler_workflow

# 清理资源
./airflow/scripts/airflow-manager.sh clean --force
```

## DAG开发指南

### 创建新的DAG

1. 在 `airflow/dags/` 目录下创建Python文件
2. 定义DAG和任务
3. 设置任务依赖关系

### 示例DAG结构

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# 默认参数
default_args = {
    'owner': 'crawler-platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建DAG
dag = DAG(
    'my_crawler_dag',
    default_args=default_args,
    description='我的爬虫DAG',
    schedule_interval='@daily',
    catchup=False,
)

# 定义任务
def my_task():
    print("执行我的任务")

task1 = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag,
)
```

### 最佳实践

1. **任务幂等性**: 确保任务可以安全重复执行
2. **错误处理**: 添加适当的异常处理和重试机制
3. **资源管理**: 合理设置任务的资源限制
4. **日志记录**: 添加详细的日志信息
5. **测试验证**: 在部署前充分测试DAG

## 配置说明

### 核心配置

主要配置文件位于 `airflow/docker/airflow.cfg`，包含：

- **数据库配置**: MySQL连接设置
- **执行器配置**: LocalExecutor设置
- **安全配置**: 认证和加密设置
- **性能配置**: 并发和资源限制
- **日志配置**: 日志级别和格式

### 环境变量

关键环境变量说明：

```bash
# 数据库连接
AIRFLOW_DB_HOST=crawler_mysql
AIRFLOW_DB_NAME=crawler_airflow_db
AIRFLOW_DB_USER=crawler_airflow_user
AIRFLOW_DB_PASSWORD=crawler_airflow_password

# 安全密钥
AIRFLOW_FERNET_KEY=your-fernet-key
AIRFLOW_SECRET_KEY=your-secret-key

# 管理员用户
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin123
```

## 监控和维护

### 健康检查

系统提供多层健康检查：

1. **容器健康检查**: Docker容器级别的健康状态
2. **服务健康检查**: Airflow服务的运行状态
3. **数据库健康检查**: MySQL连接和查询状态

### 日志管理

```bash
# 查看实时日志
./airflow/scripts/airflow-manager.sh logs --follow

# 查看特定服务日志
./airflow/scripts/airflow-manager.sh logs airflow_webserver

# 查看调度器日志
./airflow/scripts/airflow-manager.sh logs airflow_scheduler
```

### 性能优化

1. **并发设置**: 根据硬件资源调整并发参数
2. **内存管理**: 监控内存使用情况
3. **数据库优化**: 定期清理历史数据
4. **日志轮转**: 配置日志文件轮转

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查日志
   ./airflow/scripts/airflow-manager.sh logs
   
   # 检查配置
   docker-compose config
   ```

2. **数据库连接失败**
   ```bash
   # 检查MySQL服务状态
   docker-compose ps crawler_mysql
   
   # 测试数据库连接
   docker-compose exec crawler_mysql mysql -u root -p
   ```

3. **Web界面无法访问**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep 8080
   
   # 检查防火墙设置
   sudo ufw status
   ```

### 调试模式

```bash
# 启用详细输出
./airflow/scripts/airflow-manager.sh start --verbose

# 进入容器调试
./airflow/scripts/airflow-manager.sh shell webserver

# 检查Airflow配置
airflow config list
```

## 安全考虑

### 生产环境配置

1. **更换默认密钥**: 生成新的Fernet Key和Secret Key
2. **修改默认密码**: 更改管理员用户密码
3. **网络安全**: 配置防火墙和网络访问控制
4. **SSL/TLS**: 启用HTTPS访问
5. **备份策略**: 定期备份数据库和配置

### 密钥生成

```bash
# 生成Fernet Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 生成Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 扩展开发

### 自定义操作符

在 `airflow/plugins/` 目录下创建自定义操作符：

```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class CrawlerOperator(BaseOperator):
    @apply_defaults
    def __init__(self, target_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_url = target_url
    
    def execute(self, context):
        # 实现爬虫逻辑
        pass
```

### 自定义传感器

```python
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

class DataSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def poke(self, context):
        # 实现检测逻辑
        return True
```

## 版本信息

- **Airflow版本**: 2.8.1
- **Python版本**: 3.11
- **MySQL版本**: 8.0.39
- **Docker版本**: 20.10+

## 支持和反馈

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮件支持: admin@crawler-platform.com
- 文档更新: 欢迎提交PR改进文档

---

*最后更新: 2024年12月*