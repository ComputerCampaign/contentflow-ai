# Flask后端应用

数据爬取博客发布平台的后端API服务，基于Flask框架构建，提供完整的用户管理、任务调度、爬虫配置、内容生成和文件管理功能。

## 功能特性

### 核心模块
- **用户管理**: 用户注册、登录、权限控制
- **任务管理**: 任务创建、执行、监控和统计
- **爬虫配置**: 网页爬取规则配置和测试
- **内容生成**: 基于模板的内容生成和管理
- **文件管理**: 文件上传、下载、存储和清理
- **系统监控**: 性能监控、健康检查和告警

### 技术特性
- RESTful API设计
- JWT身份认证
- 接口限流保护
- 数据库迁移支持
- 完整的错误处理
- 日志记录和监控
- CORS跨域支持

## 技术栈

- **框架**: Flask 2.3.3
- **数据库**: MySQL (通过PyMySQL)
- **ORM**: SQLAlchemy
- **认证**: JWT (Flask-JWT-Extended)
- **限流**: Flask-Limiter
- **迁移**: Flask-Migrate
- **跨域**: Flask-CORS
- **密码加密**: bcrypt
- **HTML解析**: BeautifulSoup4
- **模板引擎**: Jinja2
- **系统监控**: psutil

## 项目结构

```
backend/
├── api/                    # API蓝图模块
│   ├── __init__.py        # 蓝图注册
│   ├── auth.py            # 认证API
│   ├── tasks.py           # 任务管理API
│   ├── crawler.py         # 爬虫配置API
│   ├── content.py         # 内容生成API
│   ├── files.py           # 文件管理API
│   └── monitoring.py      # 监控API
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── user.py            # 用户模型
│   ├── task.py            # 任务模型
│   ├── crawler.py         # 爬虫模型
│   ├── content.py         # 内容模型
│   └── file.py            # 文件模型
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── response.py        # 响应工具
│   └── exceptions.py      # 异常处理
├── migrations/             # 数据库迁移文件
├── logs/                   # 日志文件目录
├── uploads/                # 文件上传目录
├── app.py                  # 应用入口
├── config.py               # 配置文件
├── extensions.py           # 扩展初始化
├── requirements.txt        # 依赖包列表
└── README.md              # 项目说明
```

## 安装和配置

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- pip

### 2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 环境配置
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/crawler_db

# JWT配置
JWT_SECRET_KEY=your-secret-key-here

# 应用配置
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-app-secret-key

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# 日志配置
LOG_DIR=logs
LOG_REQUESTS=False

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. 数据库初始化
```bash
# 初始化数据库迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade

# 创建管理员用户
flask create-admin
```

## 运行应用

### 开发环境
```bash
# 直接运行
python app.py

# 或使用Flask命令
flask run --host=0.0.0.0 --port=5000
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API文档

### 认证API (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /refresh` - 刷新令牌
- `POST /logout` - 用户登出
- `GET /profile` - 获取用户资料
- `PUT /profile` - 更新用户资料
- `PUT /password` - 修改密码
- `GET /verify` - 验证令牌

### 任务管理API (`/api/v1/tasks`)
- `POST /tasks` - 创建任务
- `GET /tasks` - 获取任务列表
- `GET /tasks/{id}` - 获取任务详情
- `PUT /tasks/{id}` - 更新任务
- `DELETE /tasks/{id}` - 删除任务
- `POST /tasks/{id}/control` - 控制任务执行
- `GET /tasks/{id}/executions` - 获取执行记录
- `GET /tasks/stats` - 获取任务统计

### 爬虫配置API (`/api/v1/crawler`)
- `POST /configs` - 创建爬虫配置
- `GET /configs` - 获取配置列表
- `GET /configs/{id}` - 获取配置详情
- `PUT /configs/{id}` - 更新配置
- `DELETE /configs/{id}` - 删除配置
- `POST /configs/{id}/test` - 测试配置
- `GET /configs/{id}/results` - 获取爬取结果
- `GET /results/{id}` - 获取结果详情
- `GET /stats` - 获取爬虫统计

### 内容生成API (`/api/v1/content`)
- `POST /templates` - 创建内容模板
- `GET /templates` - 获取模板列表
- `GET /templates/{id}` - 获取模板详情
- `PUT /templates/{id}` - 更新模板
- `DELETE /templates/{id}` - 删除模板
- `POST /templates/{id}/preview` - 预览模板
- `POST /generate` - 生成内容
- `GET /generated` - 获取生成内容列表
- `GET /generated/{id}` - 获取生成内容详情
- `GET /stats` - 获取内容统计

### 文件管理API (`/api/v1/files`)
- `POST /upload` - 上传文件
- `GET /` - 获取文件列表
- `GET /{id}` - 获取文件信息
- `GET /{id}/download` - 下载文件
- `PUT /{id}` - 更新文件信息
- `DELETE /{id}` - 删除文件
- `POST /batch-upload` - 批量上传
- `POST /cleanup` - 清理文件
- `GET /stats` - 获取文件统计

### 监控API (`/api/v1/monitoring`)
- `GET /health` - 健康检查
- `GET /stats/overview` - 概览统计
- `GET /stats/system` - 系统统计
- `GET /stats/performance` - 性能统计
- `GET /logs` - 获取日志
- `GET /alerts` - 获取告警
- `GET /metrics` - 获取实时指标

## CLI命令

```bash
# 初始化数据库
flask init-db

# 创建管理员用户
flask create-admin

# 清理过期文件
flask cleanup-files

# 显示系统统计
flask show-stats
```

## 数据模型

### 用户模型 (User)
- 基本信息：用户名、邮箱、密码
- 权限管理：角色、状态
- 统计信息：注册时间、最后登录

### 任务模型 (Task)
- 任务信息：名称、类型、描述
- 配置数据：任务配置、调度设置
- 状态管理：执行状态、优先级
- 统计数据：执行次数、成功率

### 爬虫配置模型 (CrawlerConfig)
- 目标配置：URL、爬取规则
- 请求配置：请求头、代理设置
- 调度配置：频率、重试策略
- 运行统计：执行次数、成功率

### 内容模板模型 (ContentTemplate)
- 模板内容：Jinja2模板
- 变量定义：输入变量配置
- 输出配置：格式、AI设置
- 使用统计：使用次数、评分

### 文件记录模型 (FileRecord)
- 文件信息：名称、大小、类型
- 存储信息：路径、哈希值
- 分类管理：类别、标签
- 状态管理：可用性、过期时间

## 安全特性

- JWT令牌认证
- 密码bcrypt加密
- 接口访问限流
- 文件类型验证
- SQL注入防护
- XSS攻击防护
- CORS跨域控制

## 监控和日志

- 应用性能监控
- 系统资源监控
- 错误日志记录
- 访问日志记录
- 健康检查接口
- 实时告警功能

## 开发指南

### 添加新的API端点
1. 在对应的蓝图文件中添加路由
2. 实现业务逻辑
3. 添加输入验证
4. 添加错误处理
5. 更新API文档

### 添加新的数据模型
1. 在models目录创建模型文件
2. 定义模型类和关系
3. 生成数据库迁移
4. 更新相关API

### 测试
```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=backend
```

## 部署

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 生产环境配置
- 使用环境变量管理配置
- 配置反向代理(Nginx)
- 设置SSL证书
- 配置日志轮转
- 设置监控告警

## 故障排除

### 常见问题
1. **数据库连接失败**: 检查数据库配置和网络连接
2. **JWT令牌错误**: 检查密钥配置和令牌有效期
3. **文件上传失败**: 检查上传目录权限和文件大小限制
4. **接口限流**: 检查请求频率和限流配置

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License