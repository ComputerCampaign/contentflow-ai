# 智能爬虫内容管理系统

一个集成AI内容生成能力的智能网页爬虫和内容管理平台，基于Flask和Vue.js构建。

## 功能特性

- 🕷️ **智能网页爬虫** - 基于XPath规则的精确内容提取，支持Reddit等社交媒体平台
- 🤖 **AI内容生成** - 集成豆包大模型，支持多模态内容生成（文本+图片）
- 🖼️ **图片处理** - 自动下载图片并上传至GitHub图床，确保链接稳定性
- 📝 **中文内容优化** - 专门针对中文社交媒体内容生成进行优化
- 📊 **数据分析和可视化** - 爬虫数据的结构化存储和分析
- 🔐 **用户认证和权限管理** - 完整的用户管理系统
- 📱 **响应式Web界面** - 现代化的管理界面

## 技术栈

### 后端
- Flask 2.3.3
- SQLAlchemy 2.0.23
- Flask-JWT-Extended
- Celery + Redis
- BeautifulSoup4 + Selenium

### AI内容生成
- 豆包大模型 (Doubao)
- 多模态内容生成（文本+图片）
- GitHub图床集成
- 中文内容优化

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

### 配置AI服务

1. 配置豆包API密钥：
```bash
export DOUBAO_API_KEY="your_api_key_here"
```

2. 配置GitHub图床（可选）：
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="username/repo"
```

### 启动服务

```bash
# 启动后端服务
cd backend
uv run python run.py

# 启动前端开发服务器
cd frontend
npm run dev

# 运行AI内容生成示例
cd ai_content_generator
uv run python example.py
```

## 项目结构

```
├── backend/              # Flask后端应用
├── frontend/             # Vue.js前端应用
├── crawler/              # 爬虫核心模块
├── ai_content_generator/ # AI内容生成模块
│   ├── config/          # 配置文件（模型、提示词）
│   ├── utils/           # 工具类（数据加载器、日志）
│   ├── generator.py     # 核心生成器
│   └── example.py       # 使用示例
├── blog_generator/       # 博客生成模块
├── crawler_data/         # 爬虫数据存储
├── data/                # 数据库存储目录
├── logs/                # 日志文件
└── output/              # 输出文件
```

## AI内容生成使用说明

### 基本使用

```python
from ai_content_generator.generator import ContentGenerator
from ai_content_generator.utils.data_loader import CrawlerDataLoader

# 初始化生成器
generator = ContentGenerator()

# 加载爬虫数据
loader = CrawlerDataLoader()
data = loader.load_data("path/to/crawler/data")

# 生成内容
result = generator.generate_content(data)
print(result.content)  # 生成的中文社交媒体内容
print(result.tags)     # 中文标签
```

### 特性说明

- **多模态生成**：支持基于图片和文本的内容生成
- **中文优化**：专门针对中文社交媒体内容进行优化
- **图片处理**：自动优先使用GitHub图床链接，确保稳定性
- **灵活配置**：支持自定义提示词模板和模型参数

## 许可证

MIT License