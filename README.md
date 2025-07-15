# 网页图片和标题爬虫

这是一个Python爬虫项目，用于从给定网页中抓取图片和标题信息，并提供邮件通知和博客生成功能。

## 功能特点

- 支持从指定URL抓取图片和标题
- 可以保存图片到本地目录
- 可以导出标题和图片URL到CSV文件
- 支持基本的错误处理和重试机制
- 可选择使用requests或selenium+chromedriver进行爬取
- 支持邮件通知功能，可在爬取完成后发送结果报告
- 支持自动生成Markdown格式的博客文章
- 支持图片上传到本地或远程存储
- 支持XPath规则配置，精确定位网页内容
- 支持基于任务ID的爬取，便于管理多个爬取任务

## 环境要求

- Python 3.8+
- uv (Python包管理工具)

## 环境设置

### 快速设置（推荐）

项目使用uv进行依赖管理，推荐使用以下脚本快速设置环境：

```bash
source ./setup_and_run.sh
# 或
. ./setup_and_run.sh
```

**注意：** 必须使用source命令运行此脚本，才能正确激活虚拟环境。

这个脚本会自动：
1. 创建虚拟环境并安装所有依赖
2. 自动激活虚拟环境
3. 验证Python环境是否正确
4. 检查.env文件是否存在，如果不存在则提示创建

您还可以使用此脚本直接运行测试：

```bash
source ./setup_and_run.sh --test [可选的测试文件路径]
# 或
. ./setup_and_run.sh --test [可选的测试文件路径]
```

或查看帮助信息：

```bash
source ./setup_and_run.sh --help
# 或
. ./setup_and_run.sh --help
```

### 手动设置

如果您已经安装了uv，可以直接使用以下命令一步完成环境设置：

```bash
uv sync
```

### 激活虚拟环境

```bash
source .venv/bin/activate
```

### 退出虚拟环境

```bash
deactivate
```

## 配置文件

项目使用JSON格式的配置文件（默认为`config.json`）来管理各种设置。您需要创建自己的`config.json`文件来配置项目。

### 配置文件安全性

**重要提示：** 项目使用环境变量管理敏感信息（如API密钥、访问令牌等），请遵循以下安全实践：

1. **永远不要**将包含真实凭证的`.env`文件提交到版本控制系统
2. 项目的`.gitignore`已配置为忽略`.env`文件
3. 所有敏感信息应存储在`.env`文件中（推荐）
4. 配置文件`config.json`中的敏感字段应留空，系统会自动从环境变量中读取值

### 使用环境变量管理敏感信息

项目支持从环境变量读取敏感信息，这是管理凭证的推荐方式。有两种方法可以设置环境变量：

#### 方法1：使用.env文件（推荐）

1. 复制项目根目录中的`.env.example`文件并重命名为`.env`
2. 在`.env`文件中填入您的实际值

```bash
# .env文件示例
CRAWLER_EMAIL_PASSWORD=your-email-password
CRAWLER_GITHUB_TOKEN=your-github-token
```

**注意：** 
- 项目已包含`python-dotenv`库作为依赖
- 如果您使用`setup_and_run.sh`脚本，它会自动检查`.env`文件是否存在，并提示您创建

#### 方法2：直接设置系统环境变量

在macOS或Linux系统上：

```bash
# 设置邮件密码
export CRAWLER_EMAIL_PASSWORD="your-email-password"

# 设置GitHub令牌
export CRAWLER_GITHUB_TOKEN="your-github-token"
```

您可以将这些命令添加到`~/.bashrc`、`~/.zshrc`或类似的shell配置文件中。

在Windows系统上：

```cmd
SET CRAWLER_EMAIL_PASSWORD=your-email-password
SET CRAWLER_GITHUB_TOKEN=your-github-token
```

或者通过系统设置添加环境变量。

**注意：** 使用环境变量后，您可以在配置文件中将敏感字段留空，系统会自动从环境变量中读取值。

### 创建配置文件

```bash
# 创建配置文件
touch config/config.json

# 编辑配置文件，添加您的设置
# 注意：所有敏感信息应存储在.env文件中，config.json可以安全地提交到版本控制系统
```

以下是一个基本的配置文件结构示例：

```json
{
    "crawler": {
        "output_dir": "output",
        "data_dir": "data",
        "timeout": 10,
        "retry": 3,
        "use_selenium": false
    },
    "email": {
        "enabled": false,
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender_email": "your_email@example.com",
        "sender_password": "",
        "receiver_emails": ["receiver@example.com"],
        "subject_prefix": "[爬虫通知] "
    },
    "blog": {
        "enabled": false,
        "template_path": "config/templates/blog_template.md",
        "templates_dir": "config/templates",
        "output_path": "blogs",
        "image_storage": {
            "type": "local",
            "base_url": "http://example.com/images/",
            "local_path": "static/images",
            "github": {
                "enabled": false,
                "repo_owner": "your-github-username",
                "repo_name": "your-image-repo",
                "branch": "main",
                "token": "",
                "image_path": "images",
                "base_url": ""
            }
        }
    }
}
```

**注意：** 配置文件中的敏感字段（如`sender_password`和`token`）应留空，系统会自动从环境变量中读取值：
- `sender_password` 从环境变量 `CRAWLER_EMAIL_PASSWORD` 中读取
- GitHub `token` 从环境变量 `CRAWLER_GITHUB_TOKEN` 中读取

### 主要配置项

### 爬虫配置

```json
"crawler": {
    "output_dir": "output",
    "data_dir": "data",
    "timeout": 10,
    "retry": 3,
    "use_selenium": false
}
```

### 邮件通知配置

```json
"email": {
    "enabled": false,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "sender_email": "your_email@example.com",
    "sender_password": "",
    "receiver_emails": ["receiver@example.com"],
    "subject_prefix": "[爬虫通知] "
}
```

### 博客生成配置

```json
"blog": {
    "enabled": false,
    "template_path": "config/templates/blog_template.md",
    "templates_dir": "config/templates",
    "output_path": "blogs",
    "image_storage": {
        "type": "local",
        "base_url": "http://example.com/images/",
        "local_path": "static/images",
        "github": {
            "enabled": false,
            "repo_owner": "your-github-username",
            "repo_name": "your-image-repo",
            "branch": "main",
            "token": "",
            "image_path": "images",
            "base_url": ""
        }
    }
}
```

图片存储支持两种类型：
- `local`: 将图片存储在本地目录
- `github`: 将图片上传到GitHub仓库作为图床

要使用GitHub图床，需要设置以下参数：
1. 将 `image_storage.type` 设置为 `github`
2. 将 `image_storage.github.enabled` 设置为 `true`
3. 设置 `repo_owner` 和 `repo_name` 为您的GitHub用户名和仓库名
4. 设置 `token` 为您的GitHub个人访问令牌（需要有repo权限）
5. 可选：自定义 `branch`、`image_path` 和 `base_url`

您可以通过编辑配置文件或使用命令行参数来修改这些设置。

## 使用方法

### 基本用法

```bash
# 基本爬取
python crawler.py --url "https://example.com" --output "output_folder" --data-dir "data_folder"

# 使用任务ID爬取
python crawler.py --url "https://example.com" --task-id "my_task" --output "output_folder"

# 使用XPath规则爬取
python crawler.py --url "https://www.reddit.com/r/pics" --rule-id "reddit_media"

# 列出所有可用的XPath规则
python crawler.py --list-rules
```

### 参数说明

- `--url`: 要爬取的网页URL（必需）
- `--task-id`: 任务ID，如果不提供则自动生成，用于管理多个爬取任务
- `--output`: 输出目录，用于临时文件和日志（默认使用配置文件设置）
- `--data-dir`: 数据存储目录，用于保存图片和元数据（默认使用配置文件设置）
- `--use-selenium`: 使用Selenium和ChromeDriver进行爬取（默认使用配置文件设置）
- `--timeout`: 请求超时时间，单位为秒（默认使用配置文件设置）
- `--retry`: 失败重试次数（默认使用配置文件设置）
- `--config`: 配置文件路径（默认为'config.json'）
- `--enable-email`: 启用邮件通知
- `--disable-email`: 禁用邮件通知
- `--enable-blog`: 启用博客生成
- `--disable-blog`: 禁用博客生成
- `--rule-id`: XPath规则ID，用于指定使用哪个XPath规则（例如：reddit_media, twitter_media, general_article）
- `--list-rules`: 列出所有可用的XPath规则

### 独立博客生成

项目提供了一个独立的博客生成脚本，可以根据提供的图片列表、元数据和模板生成博客文章：

```bash
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json --template template_name --output output.md
```

#### 参数说明

- `--images`: 图片路径列表（可选）
- `--metadata`: 元数据文件路径（必需），JSON格式
- `--template`: 模板名称（可选，默认使用'default'模板）
- `--output`: 输出文件路径（可选，默认生成到配置的博客目录）
- `--list-templates`: 列出可用的模板

#### 示例

查看示例目录中的`examples/generate_blog_example.sh`脚本，了解如何使用独立博客生成功能：

```bash
# 列出可用的模板
python generate_blog.py --list-templates

# 使用默认模板生成博客
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json

# 使用指定模板生成博客
python generate_blog.py --images image1.jpg image2.jpg --metadata metadata.json --template simple_template
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
├── generate_blog.py    # 独立博客生成脚本
├── setup_and_run.sh    # 环境设置和运行脚本
├── examples/           # 示例目录
│   ├── metadata_example.json # 示例元数据文件
│   ├── generate_blog_example.sh # 博客生成示例脚本
│   ├── crawler_example.sh # 爬虫功能示例脚本
│   ├── images/         # 示例图片目录
│   └── output/         # 示例输出目录
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── notifier.py     # 邮件通知模块
│   ├── blog_generator.py # 博客生成模块
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
├── static/             # 静态资源目录
│   └── images/         # 博客图片存储目录
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