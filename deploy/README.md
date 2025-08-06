# 爬虫平台部署指南

## 环境变量管理

### 统一配置方案

为了简化环境变量管理，我们将所有MySQL和Airflow的配置统一到 `deploy/envs/.env` 文件中。

### 配置步骤

1. **复制环境变量模板**
   ```bash
   cp deploy/envs/.env.example deploy/envs/.env
   ```

2. **编辑环境变量**
   ```bash
   vim deploy/envs/.env
   ```
   
   根据实际情况修改以下关键配置：
   - MySQL密码：`MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`
   - Airflow数据库密码：`AIRFLOW_DB_PASSWORD`
   - Airflow安全密钥：`AIRFLOW_FERNET_KEY` 和 `AIRFLOW_SECRET_KEY`
   - Airflow管理员密码：`AIRFLOW_ADMIN_PASSWORD`

## 启动步骤

### 1. 构建Airflow镜像

```bash
# 进入airflow目录
cd airflow

# 构建Docker镜像（指定平台为amd64以确保兼容性）
docker build --platform linux/amd64 -t crawler-airflow:latest -f docker/Dockerfile .
```

**注意**: 由于基础镜像使用的是amd64架构，需要指定 `--platform linux/amd64` 参数以确保在不同架构的机器（如Apple Silicon Mac）上也能正确构建镜像。

### 2. 启动服务

```bash
# 进入部署目录
cd deploy/docker

# 启动所有服务
docker-compose up -d
```

### 3. 验证服务状态

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f airflow_webserver
docker-compose logs -f airflow_scheduler
docker-compose logs -f crawler_mysql
```

### 4. 访问服务

- **Airflow Web UI**: http://localhost:8080
  - 用户名：admin（可在.env文件中修改）
  - 密码：admin123（可在.env文件中修改）

- **MySQL数据库**: localhost:8306
  - 用户名：crawler_usage
  - 密码：crawler_usage_Pwd123!（可在.env文件中修改）

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止服务并删除数据卷（谨慎使用）
docker-compose down -v
```

## 环境变量说明

### MySQL配置
- `MYSQL_HOST`: MySQL服务主机名（Docker网络内使用服务名）
- `MYSQL_PORT`: MySQL端口
- `MYSQL_DATABASE`: 数据库名称
- `MYSQL_USER`: MySQL用户名
- `MYSQL_PASSWORD`: MySQL用户密码
- `MYSQL_ROOT_PASSWORD`: MySQL root密码

### Airflow核心配置
- `AIRFLOW_UID`: Airflow运行用户ID
- `AIRFLOW_GID`: Airflow运行组ID
- `AIRFLOW_HOME`: Airflow主目录

### Airflow数据库配置
- `AIRFLOW_DB_HOST`: Airflow数据库主机
- `AIRFLOW_DB_PORT`: Airflow数据库端口
- `AIRFLOW_DB_NAME`: Airflow数据库名称
- `AIRFLOW_DB_USER`: Airflow数据库用户名
- `AIRFLOW_DB_PASSWORD`: Airflow数据库密码

### Airflow安全配置
- `AIRFLOW_FERNET_KEY`: 用于加密连接密码的密钥
- `AIRFLOW_SECRET_KEY`: Flask应用密钥

### Airflow管理员配置
- `AIRFLOW_ADMIN_USERNAME`: 管理员用户名
- `AIRFLOW_ADMIN_PASSWORD`: 管理员密码
- `AIRFLOW_ADMIN_EMAIL`: 管理员邮箱

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用：`lsof -i :8080` 和 `lsof -i :8306`
   - 检查Docker是否正常运行：`docker version`
   - 查看详细错误日志：`docker-compose logs [service_name]`

2. **数据库连接失败**
   - 确认MySQL服务已启动：`docker-compose ps`
   - 检查数据库配置是否正确
   - 查看MySQL日志：`docker-compose logs crawler_mysql`

3. **Airflow Web UI无法访问**
   - 确认webserver服务已启动：`docker-compose ps`
   - 检查防火墙设置
   - 查看webserver日志：`docker-compose logs airflow_webserver`

### 重置环境

如果需要完全重置环境：

```bash
# 停止所有服务并删除数据
docker-compose down -v

# 删除相关镜像（可选）
docker rmi crawler-airflow:latest

# 重新构建和启动
docker build --platform linux/amd64 -t crawler-airflow:latest -f ../airflow/docker/Dockerfile ../airflow
docker-compose up -d
```

## 生产环境注意事项

1. **安全配置**
   - 更换所有默认密码
   - 生成新的Fernet密钥：`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - 使用强密码策略

2. **数据备份**
   - 定期备份MySQL数据
   - 备份Airflow配置和DAG文件

3. **监控**
   - 监控服务健康状态
   - 设置日志轮转
   - 监控资源使用情况