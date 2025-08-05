# 智能爬虫内容管理系统

一个基于Flask和Vue.js的智能网页爬虫和内容管理平台。

## 功能特性

- 🕷️ 智能网页爬虫配置
- 🤖 AI内容生成
- 📊 数据分析和可视化
- 🔐 用户认证和权限管理
- 📱 响应式Web界面

## 技术栈

### 后端
- Flask 2.3.3
- SQLAlchemy 2.0.23
- Flask-JWT-Extended
- Celery + Redis
- BeautifulSoup4 + Selenium

### 前端
- Vue.js 3
- Element Plus
- Pinia状态管理
- Vite构建工具

## 快速开始

### 安装依赖

```bash
# 使用uv管理Python依赖
uv sync

# 安装前端依赖
cd frontend
npm install
```

### 启动服务

```bash
# 启动后端服务
cd backend
uv run python run.py

# 启动前端开发服务器
cd frontend
npm run dev
```

## 项目结构

```
├── backend/          # Flask后端应用
├── frontend/         # Vue.js前端应用
├── crawler/          # 爬虫核心模块
├── blog_generator/   # 博客生成模块
├── data/            # 数据存储目录
├── logs/            # 日志文件
└── output/          # 输出文件
```

## 许可证

MIT License