# 网页图片爬虫与博客生成器

这是一个集成了网页图片爬取和博客生成功能的工具，可以自动抓取网页中的图片和标题，并根据抓取的内容生成博客文章。

## 功能特点

### 爬虫模块

- 支持图片和标题抓取：自动从网页中提取图片和标题
- 支持XPath规则配置：通过配置XPath规则，精确定位网页内容
- 支持任务ID管理：便于管理多个爬取任务
- 支持邮件通知：爬取完成后自动发送邮件通知
- 支持自定义输出目录：灵活设置爬取结果的存储位置
- 支持Selenium模式：处理动态加载的网页内容

### 博客生成模块

- 支持两种生成模式：从爬虫数据生成和从自定义数据生成
- 支持多种模板：可以选择不同的博客模板
- 支持图片上传：自动将图片上传到GitHub图床
- 支持元数据定制：可以自定义博客的标题、内容、标签等
- 支持自动标签生成：根据内容自动生成标签

## 环境要求

- Python 3.8+
- 依赖库：见`pyproject.toml`文件

## 环境设置

### 快速设置

使用`uv`进行依赖管理（推荐）：

```bash
# 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用setup_and_run.sh脚本自动设置环境
./setup_and_run.sh
```

### 查看帮助

```bash
# 查看爬虫帮助
python crawler.py --help

# 查看博客生成帮助
python generate_blog.py --help
```

### 手动设置

```bash
# 使用uv同步依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate
```

## 配置

### 配置文件

项目使用`config/config.json`作为配置文件。首次运行时，如果配置文件不存在，将自动创建默认配置文件。

**注意**：敏感信息（如邮箱密码、GitHub token）应通过环境变量管理，而不是直接写入配置文件。

### 环境变量

推荐使用`.env`文件管理敏感信息：

1. 在项目根目录创建`.env`文件
2. 添加敏感信息，例如：

```
EMAIL_PASSWORD=your_email_password
GITHUB_TOKEN=your_github_token
```

3. 项目会自动加载`.env`文件中的环境变量

也可以直接设置系统环境变量：

```bash
# Linux/macOS
export EMAIL_PASSWORD=your_email_password
export GITHUB_TOKEN=your_github_token

# Windows
set EMAIL_PASSWORD=your_email_password
set GITHUB_TOKEN=your_github_token
```

### 创建配置文件

如果需要手动创建配置文件，可以参考以下结构：

```json
{
  "crawler": {
    "data_dir": "data",
    "use_selenium": false,
    "timeout": 30,
    "retry": 3
  },
  "email": {
    "enable": true,
    "sender": "your_email@example.com",
    "receiver": "receiver_email@example.com",
    "smtp_server": "smtp.example.com",
    "smtp_port": 587
  },
  "blog": {
    "templates_dir": "config/templates",
    "output_path": "blogs",
    "use_crawler_image_storage": true,
    "github": {
      "repo_owner": "your_github_username",
      "repo_name": "your_repo_name"
    }
  }
}
```

**注意**：敏感信息如`sender_password`和GitHub `token`应通过环境变量设置，不要直接写入配置文件。

### 邮件通知配置

邮件通知功能需要配置以下参数：

- `enable`: 是否启用邮件通知
- `sender`: 发件人邮箱
- `receiver`: 收件人邮箱
- `smtp_server`: SMTP服务器地址
- `smtp_port`: SMTP服务器端口

发件人密码通过环境变量`EMAIL_PASSWORD`设置。

### 博客生成配置

博客生成功能需要配置以下参数：

- `templates_dir`: 模板目录路径
- `output_path`: 博客输出目录路径
- `use_crawler_image_storage`: 是否使用爬虫的图片存储设置

图片存储目前仅支持GitHub图床，需要配置：

- `github.repo_owner`: GitHub用户名
- `github.repo_name`: GitHub仓库名

GitHub token通过环境变量`GITHUB_TOKEN`设置。

## 使用方法

### 爬虫功能

#### 基本爬取

```bash
python crawler.py --url https://example.com
```

#### 使用任务ID爬取

```bash
python crawler.py --url https://example.com --task-id my_task
```

#### 使用XPath规则爬取

```bash
python crawler.py --url https://example.com --rule-id rule_name
```

#### 列出所有可用XPath规则

```bash
python crawler.py --list-rules
```

#### 参数说明

- `--url`: 要爬取的网页URL
- `--task-id`: 任务ID，用于管理多个爬取任务
- `--output`: 输出目录路径
- `--data-dir`: 数据存储目录路径
- `--use-selenium`: 使用Selenium模式爬取
- `--timeout`: 请求超时时间（秒）
- `--retry`: 请求重试次数
- `--config`: 配置文件路径
- `--enable-email`: 启用邮件通知
- `--disable-email`: 禁用邮件通知
- `--rule-id`: 使用指定的XPath规则ID
- `--list-rules`: 列出所有可用的XPath规则

### 博客生成功能

博客生成支持两种模式：从爬虫数据生成和从自定义数据生成。

#### 1. 从爬虫数据生成博客

```bash
python generate_blog.py --task-dir "data/tasks/task_123456789" [--template template_name] [--output output.md]
```

##### 参数说明

- `--task-dir`: 爬虫任务目录路径（必需），包含page_info.json和images.csv文件
- `--template`: 模板名称（可选，默认使用'default'模板）
- `--output`: 输出文件路径（可选，默认生成到配置的博客目录）
- `--list-templates`: 列出可用的模板

##### 示例

查看示例目录中的`examples/generate_blog_from_crawler_example.sh`脚本，了解如何使用从爬虫数据生成博客功能：

```bash
# 列出可用的模板
python generate_blog.py --list-templates

# 使用默认模板从爬虫任务目录生成博客
python generate_blog.py --task-dir "data/tasks/task_123456789"

# 使用指定模板和输出路径从爬虫任务目录生成博客
python generate_blog.py --task-dir "data/tasks/task_123456789" --template simple_template --output "blogs/my_blog.md"
```

#### 2. 从自定义数据生成博客

```bash
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json [--template template_name] [--output output.md]
```

##### 参数说明

- `--images`: 图片路径列表（可选）
- `--metadata`: 元数据文件路径（必需），JSON格式
- `--template`: 模板名称（可选，默认使用'default'模板）
- `--output`: 输出文件路径（可选，默认生成到配置的博客目录）
- `--list-templates`: 列出可用的模板

##### 示例

查看示例目录中的`examples/generate_blog_example.sh`脚本，了解如何使用自定义数据生成博客功能：

```bash
# 列出可用的模板
python generate_blog.py --list-templates

# 使用默认模板生成博客
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json

# 使用指定模板生成博客
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json --template simple_template
```

#### 综合示例

查看`examples/generate_blog_combined_example.sh`脚本，了解如何使用两种模式生成博客：

```bash
# 运行综合示例脚本
./examples/generate_blog_combined_example.sh [爬虫任务目录路径]
```

## 项目结构

```
.
├── README.md           # 项目说明文档
├── pyproject.toml      # 项目配置和依赖管理
├── config/             # 配置目录
│   ├── __init__.py     # 配置包初始化文件
│   ├── config.py       # 配置管理模块
│   ├── config.json     # 配置文件
│   ├── templates/      # 模板目录
│   │   ├── blog_template.md  # 默认博客模板
│   │   ├── simple_template.md # 简单博客模板
│   │   └── detailed_template.md # 详细博客模板
│   └── xpath/          # XPath规则目录
│       ├── README_XPATH.md # XPath规则说明文档
│       └── xpath_rules.json # XPath规则配置文件
├── crawler.py          # 主爬虫脚本
├── generate_blog.py    # 博客生成脚本（支持两种模式）
├── setup_and_run.sh    # 环境设置和运行脚本
├── examples/           # 示例目录
│   ├── metadata_example.json # 示例元数据文件
│   ├── generate_blog_example.sh # 自定义数据博客生成示例脚本
│   ├── generate_blog_from_crawler_example.sh # 爬虫数据博客生成示例脚本
│   ├── generate_blog_combined_example.sh # 综合博客生成示例脚本
│   ├── crawler_example.sh # 爬虫功能示例脚本
│   ├── images/         # 示例图片目录
│   └── output/         # 示例输出目录
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── notifier.py     # 邮件通知模块
│   ├── generate_blog.py # 博客生成模块
│   └── github_image_uploader.py # GitHub图片上传模块
├── crawler_utils/      # 爬虫工具函数
│   ├── __init__.py
│   ├── batch_downloader.py # 批量下载器
│   ├── html_parser.py  # HTML解析器
│   ├── image_downloader.py # 图片下载器
│   ├── storage_manager.py # 存储管理器
│   └── xpath_manager.py # XPath管理器
├── blogs/              # 生成的博客目录
│   ├── drafts/         # 博客草稿目录
│   └── published/      # 已发布博客目录
├── output/             # 默认输出目录（日志和临时文件）
└── data/               # 数据存储目录（不包含在版本控制中）
    ├── images/         # 原始图片存储目录
    └── metadata/       # 元数据存储目录
```

## XPath规则配置

项目支持使用XPath规则来精确定位网页内容，提高爬取效率和准确性。

### XPath规则文件

XPath规则存储在 `config/xpath/xpath_rules.json` 文件中，采用JSON格式。每条规则包含以下字段：

- `id`: 规则的唯一标识符
- `name`: 规则的名称
- `description`: 规则的描述
- `domain_patterns`: 适用的域名模式列表，用于自动匹配
- `xpath`: XPath表达式，用于限定爬取区域

### 使用XPath规则

1. 使用指定的XPath规则ID爬取网页：

```bash
python crawler.py --url https://www.reddit.com/r/pics --rule-id reddit_media
```

2. 使用自动匹配的XPath规则爬取网页（根据域名自动选择规则）：

```bash
python crawler.py --url https://www.reddit.com/r/pics
```

3. 列出所有可用的XPath规则：

```bash
python crawler.py --list-rules
```

更多关于XPath规则的详细信息，请参阅 `config/xpath/README_XPATH.md` 文件。

## 基于任务ID的爬取

项目支持基于任务ID的爬取，便于管理多个爬取任务。

### 使用任务ID

```bash
python crawler.py --url https://example.com --task-id my_task_name
```

如果不提供任务ID，系统会自动生成一个基于时间戳的任务ID。

任务ID将用于创建任务目录，所有与该任务相关的数据（图片、元数据等）都会存储在该目录中。

## 许可证

MIT