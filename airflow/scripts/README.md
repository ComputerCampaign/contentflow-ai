# Airflow 脚本和启动机制说明

本文档详细说明了Airflow的启动流程、卷挂载机制以及管理脚本的完整功能。

## 目录

- [Airflow启动完整流程](#airflow启动完整流程)
- [卷挂载机制详解](#卷挂载机制详解)
- [airflow-manager.sh 脚本功能](#airflow-managersh-脚本功能)
- [常见问题和解决方案](#常见问题和解决方案)

## Airflow启动完整流程

### 1. 镜像构建阶段（一次性）

**构建时机**：
- 首次部署时执行 `./airflow/scripts/airflow-manager.sh build`
- 修改了 `Dockerfile` 或依赖文件时
- 手动执行构建命令时

**构建过程**：
```dockerfile
# 基于本地的镜像
# docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/apache/airflow:2.9.3
# docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/apache/airflow:2.9.3 airflow:2.9.3
# docker build --platform linux/amd64 -t crawler-airflow .
FROM airflow:2.9.3

# 使用airflow用户
USER airflow

# 配置pip使用国内镜像源并安装Python依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir --trusted-host pypi.tuna.tsinghua.edu.cn -r /tmp/requirements.txt

# 复制配置文件
COPY airflow.cfg /opt/airflow/airflow.cfg
COPY webserver_config.py /opt/airflow/webserver_config.py

# 复制自定义脚本
COPY entrypoint.sh /opt/airflow/entrypoint.sh

# 设置工作目录
WORKDIR /opt/airflow

# 设置入口点
ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
```

**关键特点**：
- DAG文件**不会**打包到镜像中
- 只包含基础环境、依赖包和配置文件
- 生成镜像名称：`crawler-airflow:latest`

### 2. 服务启动阶段（每次启动）

**启动命令**：
```bash
./airflow/scripts/airflow-manager.sh start -d
```

**启动流程**：

#### 步骤1：Docker Compose解析配置
- 读取 `deploy/docker/docker-compose.yml`
- 使用已构建的镜像 `crawler-airflow:latest`
- **不会重新构建镜像**

#### 步骤2：启动MySQL服务
```yaml
crawler_mysql:
  image: docker.m.daocloud.io/library/mysql:8.0.39  # 直接拉取官方镜像
  volumes:
    - ../../data/db/mysql:/var/lib/mysql  # 数据持久化
```

#### 步骤3：启动Airflow Webserver
```yaml
airflow_webserver:
  image: crawler-airflow:latest  # 使用已构建镜像
  volumes:
    - ../../airflow/dags:/opt/airflow/dags      # 🔑 DAG文件卷挂载
    - ../../airflow/logs:/opt/airflow/logs      # 日志文件挂载
    - ../../airflow/plugins:/opt/airflow/plugins # 插件文件挂载
```

#### 步骤4：启动Airflow Scheduler
```yaml
airflow_scheduler:
  image: crawler-airflow:latest  # 使用相同镜像
  volumes:
    - ../../airflow/dags:/opt/airflow/dags      # 🔑 同样的DAG卷挂载
```

## 卷挂载机制详解

### 技术原理

**卷挂载配置**：
- **宿主机路径**：`/Users/zhangmiao/Workdir/computerCampaign/crawler/crawler/airflow/dags/`
- **容器内路径**：`/opt/airflow/dags/`
- **同步方式**：实时双向同步

**工作流程**：
1. 容器启动时，Docker将宿主机目录挂载到容器内
2. Airflow服务读取 `/opt/airflow/dags/` 目录中的DAG文件
3. 当宿主机DAG文件修改时，容器内立即可见
4. Airflow的DAG文件扫描器自动检测变化并重新加载

### 热更新机制

**自动检测**：
- Airflow默认每30秒扫描DAG目录
- 检测到文件变化时自动重新解析DAG
- 无需重启容器或重建镜像

**实际效果**：
- 修改DAG文件后保存
- 30秒内在Web UI中看到更新
- 支持语法错误检测和实时反馈

### 开发优势

1. **快速迭代**：修改DAG文件后无需重建Docker镜像
2. **调试便利**：实时查看DAG变更效果
3. **数据持久**：容器重启后DAG和日志数据保持不变
4. **版本控制**：DAG文件直接在宿主机上管理

### 对比说明

| 方式 | 镜像构建 | DAG更新 | 重启需求 |
|------|----------|---------|----------|
| **传统方式** | 每次DAG修改都需要 | 打包到镜像中 | 需要重启容器 |
| **当前方式** | 仅首次或依赖变更 | 卷挂载实时同步 | 无需重启 |

## airflow-manager.sh 脚本功能

### 基本命令

#### 服务管理
```bash
# 启动服务
./airflow-manager.sh start           # 前台启动
./airflow-manager.sh start -d        # 后台启动

# 停止服务
./airflow-manager.sh stop

# 重启服务
./airflow-manager.sh restart

# 查看状态
./airflow-manager.sh status
```

#### 日志管理
```bash
# 查看所有服务日志
./airflow-manager.sh logs

# 查看特定服务日志
./airflow-manager.sh logs airflow_webserver
./airflow-manager.sh logs airflow_scheduler
./airflow-manager.sh logs crawler_mysql

# 实时跟踪日志
./airflow-manager.sh logs --follow
./airflow-manager.sh logs airflow_webserver --follow
```

#### 镜像管理
```bash
# 构建镜像
./airflow-manager.sh build

# 无缓存构建
./airflow-manager.sh build --no-cache

# 清理资源
./airflow-manager.sh clean
./airflow-manager.sh clean --force
```

### 高级功能

#### 环境初始化
```bash
# 初始化环境
./airflow-manager.sh init

# 初始化数据库
./airflow-manager.sh db-init

# 升级数据库
./airflow-manager.sh db-upgrade
```

#### 容器操作
```bash
# 进入webserver容器
./airflow-manager.sh shell
./airflow-manager.sh shell webserver

# 进入scheduler容器
./airflow-manager.sh shell scheduler

# 进入MySQL容器
./airflow-manager.sh shell mysql
```

#### 用户管理
```bash
# 创建管理员用户
./airflow-manager.sh create-user admin

# 交互式创建用户
./airflow-manager.sh create-user
```

#### DAG管理
```bash
# 列出所有DAG
./airflow-manager.sh list-dags

# 测试特定DAG
./airflow-manager.sh test-dag daily_crawler_pipeline
./airflow-manager.sh test-dag example_crawler_workflow
```

#### 数据备份
```bash
# 备份数据
./airflow-manager.sh backup

# 恢复数据
./airflow-manager.sh restore
```

### 脚本选项

```bash
# 通用选项
-h, --help      # 显示帮助信息
-v, --verbose   # 详细输出
-f, --force     # 强制执行
-d, --detach    # 后台运行
--no-cache      # 构建时不使用缓存
```

### 使用示例

```bash
# 完整的部署流程
./airflow-manager.sh init          # 初始化环境
./airflow-manager.sh build         # 构建镜像
./airflow-manager.sh start -d      # 启动服务
./airflow-manager.sh status        # 检查状态

# 开发调试流程
./airflow-manager.sh logs airflow_scheduler --follow  # 查看调度器日志
./airflow-manager.sh shell webserver                  # 进入容器调试
./airflow-manager.sh test-dag my_dag                  # 测试DAG

# 维护操作
./airflow-manager.sh backup        # 备份数据
./airflow-manager.sh clean --force # 清理资源
./airflow-manager.sh restart       # 重启服务
```

## 常见问题和解决方案

### DAG文件问题

#### TaskGroup任务依赖错误
**错误现象**：
```
AirflowException: Dependency <Task(DummyOperator): extract>, <Task(DummyOperator): transform> already registered
```

**解决方案**：
```python
# 错误示例 - 缺少dag参数
with TaskGroup('data_pipeline', dag=dag) as data_pipeline:
    extract = DummyOperator(task_id='extract')  # ❌ 缺少dag=dag
    
# 正确示例 - 添加dag参数
with TaskGroup('data_pipeline', dag=dag) as data_pipeline:
    extract = DummyOperator(task_id='extract', dag=dag)  # ✅ 正确
```

#### Bash命令转义问题
**错误现象**：
```
SyntaxWarning: invalid escape sequence '\*'
```

**解决方案**：
```python
# 错误示例 - 无效转义序列
command = "find /path -name \*.log"  # ❌ 无效转义

# 正确示例 - 使用原始字符串
command = r"find /path -name *.log"  # ✅ 原始字符串
command = "find /path -name *.log"   # ✅ 或直接使用
```

### 服务启动问题

#### 容器启动失败
```bash
# 检查日志
./airflow-manager.sh logs

# 检查配置
docker-compose -f deploy/docker/docker-compose.yml config
```

#### 数据库连接失败
```bash
# 检查MySQL服务状态
docker-compose -f deploy/docker/docker-compose.yml ps crawler_mysql

# 测试数据库连接
docker-compose -f deploy/docker/docker-compose.yml exec crawler_mysql mysql -u root -p
```

#### Web界面无法访问
```bash
# 检查端口占用
netstat -tlnp | grep 8080

# 检查防火墙设置
sudo ufw status

# 检查服务健康状态
./airflow-manager.sh status
```

### 调试模式

```bash
# 启用详细输出
./airflow-manager.sh start --verbose

# 进入容器调试
./airflow-manager.sh shell webserver

# 检查Airflow配置
airflow config list

# 检查DAG语法
python -m py_compile /opt/airflow/dags/your_dag.py
```

### 镜像构建问题

如果遇到镜像构建失败的问题，请按以下步骤解决：

1. **基础镜像无法拉取**
   ```bash
   # 直接重新构建（Dockerfile已配置华为云镜像源）
   ./airflow-manager.sh build --no-cache
   ```

2. **平台兼容性问题**
   - 项目已配置为使用华为云镜像源，避免网络问题
   - Dockerfile 已优化为直接使用可用的基础镜像
   - 如遇平台警告，可以忽略（功能正常）

3. **Docker Compose 构建失败**
   ```bash
   # 直接使用 Docker 构建
   cd airflow/docker
   docker build --no-cache -t crawler-airflow:latest .
   ```

## start-airflow.sh 快速启动脚本优化

### 智能构建机制

为了提高开发效率，避免每次启动都重新构建镜像，`start-airflow.sh` 脚本已优化为智能构建模式：

#### 构建逻辑流程
```bash
# 1. 检查是否强制重建
if [ "$FORCE_REBUILD" = "true" ]; then
    log_info "强制重新构建镜像..."
    "$AIRFLOW_MANAGER" build
    
# 2. 检查镜像是否存在
elif check_image_exists; then
    log_info "检测到已存在的Airflow镜像，跳过构建步骤"
    log_warn "如需重新构建镜像，请使用 --rebuild 选项"
    
# 3. 镜像不存在，开始构建
else
    log_info "未检测到Airflow镜像，开始构建..."
    "$AIRFLOW_MANAGER" build
fi
```

#### 命令行选项

```bash
# 标准启动（智能构建模式）
./scripts/start-airflow.sh

# 跳过确认，自动部署
./scripts/start-airflow.sh --force

# 强制重新构建镜像
./scripts/start-airflow.sh --rebuild

# 详细输出模式
./scripts/start-airflow.sh --verbose

# 组合使用多个选项
./scripts/start-airflow.sh --force --rebuild --verbose
```

#### 优化效果对比

| 场景 | 优化前 | 优化后 | 时间节省 |
|------|--------|--------|----------|
| 首次部署 | 构建镜像 + 启动服务 | 构建镜像 + 启动服务 | 无变化 |
| 日常开发 | 每次都重建镜像 | 跳过构建，直接启动 | 节省2-5分钟 |
| 依赖更新 | 重建镜像 | 使用 `--rebuild` 重建 | 按需重建 |
| 配置调试 | 重建镜像 | 跳过构建 | 节省2-5分钟 |

#### 镜像检查机制

脚本通过以下函数检查镜像是否存在：
```bash
check_image_exists() {
    local image_name="crawler-airflow:latest"
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^$image_name$"; then
        return 0  # 镜像存在
    else
        return 1  # 镜像不存在
    fi
}
```

#### 使用建议

1. **日常开发**：直接使用 `./scripts/start-airflow.sh`，享受快速启动
2. **依赖更新**：修改 `requirements.txt` 后使用 `--rebuild` 选项
3. **配置更新**：修改 `airflow.cfg` 等配置文件后使用 `--rebuild` 选项
4. **自动化部署**：在CI/CD中使用 `--force` 选项跳过交互确认
5. **静默部署**：使用 `--quiet` 选项减少输出信息，适合脚本自动化
6. **问题排查**：使用 `--verbose` 选项查看详细的执行过程

#### 日志输出优化

为了解决启动时大量冗余日志的问题，已进行以下优化：

1. **Docker Compose日志配置**：
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"    # 单个日志文件最大10MB
       max-file: "3"       # 最多保留3个日志文件
   ```

2. **静默启动模式**：
   ```bash
   # airflow-manager.sh 中的静默启动
   docker-compose up -d --quiet-pull 2>/dev/null
   ```

3. **静默模式选项**：
   ```bash
   # 使用静默模式，大幅减少输出信息
   ./scripts/start-airflow.sh --quiet
   
   # 输出示例：
   # 🚀 正在部署Airflow平台...
   # ✅ 使用现有镜像
   # 🚀 启动服务...
   # ⏳ 等待服务启动...
   # ✅ 服务启动完成
   ```

### 与卷挂载机制的协同

智能构建机制与DAG卷挂载完美配合：
- **镜像层面**：包含基础环境和配置，按需构建
- **卷挂载层面**：DAG文件实时同步，无需重建
- **开发体验**：修改DAG文件立即生效，修改依赖时才重建镜像

## 最佳实践

### 开发流程
1. 在本地修改DAG文件
2. 保存文件后等待30秒自动重载
3. 在Web UI中检查DAG状态
4. 使用 `test-dag` 命令验证DAG逻辑
5. 查看日志排查问题

### 部署流程
1. 首次部署：`init` → `build` → `start`
2. 更新DAG：直接修改文件，无需重启
3. 更新依赖：修改requirements.txt → `build` → `restart`
4. 更新配置：修改配置文件 → `build` → `restart`

### 维护建议
1. 定期备份数据：`./airflow-manager.sh backup`
2. 监控日志文件大小：`./airflow-manager.sh logs`
3. 清理未使用资源：`./airflow-manager.sh clean`
4. 检查服务健康状态：`./airflow-manager.sh status`

---

*最后更新: 2024年12月*
*相关文件: airflow-manager.sh, docker-compose.yml, Dockerfile*