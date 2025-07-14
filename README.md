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

## 环境要求

- Python 3.8+
- uv (Python包管理工具)

## 环境设置

### 快速设置（推荐）

项目使用uv进行依赖管理，推荐使用以下脚本快速设置环境：

```bash
./setup_and_run.sh
```

这个脚本会自动：
1. 检查并安装uv（如果需要）
2. 创建虚拟环境并安装所有依赖
3. 自动激活虚拟环境
4. 验证Python环境是否正确
5. 提供后续操作指导

您还可以使用此脚本直接运行测试：

```bash
./setup_and_run.sh --test [可选的测试文件路径]
```

或查看帮助信息：

```bash
./setup_and_run.sh --help
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

### 安装开发依赖

如果需要安装开发依赖（如测试工具），可以使用：

```bash
uv pip install -e ".[dev]"
```

### 虚拟环境管理

#### 什么是虚拟环境？

虚拟环境是一个独立的Python环境，它允许您为不同的项目安装不同版本的包，而不会相互干扰。这对于管理项目依赖非常重要，特别是当不同项目需要不同版本的同一个包时。

#### uv虚拟环境的优势

- **速度快**：uv创建虚拟环境比传统工具快10-100倍
- **简单**：单一命令即可创建和管理虚拟环境
- **兼容性**：与现有的virtualenv和venv格式兼容
- **轻量级**：最小化依赖，减少出错可能

#### 基本虚拟环境操作

```bash
# 手动创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf .venv
```

#### uv依赖管理常用命令

```bash
# 安装特定包
uv pip install package_name

# 更新依赖
uv pip install --upgrade .

# 查看已安装的包
uv pip list

# 卸载包
uv pip uninstall package_name

# 导出当前环境的依赖
uv pip freeze > requirements.txt
```

#### uv与pip的区别

- uv比pip快10-100倍
- uv内置了虚拟环境管理功能
- uv使用Rust编写，内存安全且高效
- uv可以直接从pyproject.toml安装依赖
- uv支持并行下载和安装
- uv提供sync命令，一步完成环境设置

#### 最佳实践

1. **为每个项目创建单独的虚拟环境**：避免依赖冲突
2. **使用版本控制忽略虚拟环境目录**：在.gitignore中添加`.venv/`
3. **记录项目依赖**：使用pyproject.toml或requirements.txt
4. **使用uv sync简化环境设置**：一步完成环境创建和依赖安装
5. **定期更新依赖**：使用`uv pip install --upgrade`

## 配置文件

项目使用JSON格式的配置文件（默认为`config.json`）来管理各种设置。主要配置项包括：

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
python crawler.py --url "https://example.com" --output "output_folder" --data-dir "data_folder"
```

### 参数说明

- `--url`: 要爬取的网页URL（必需）
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
├── .uv/                # uv配置目录
├── README.md           # 项目说明文档
├── pyproject.toml      # 项目配置和依赖管理（uv）
├── config/             # 配置目录
│   ├── __init__.py     # 配置包初始化文件
│   ├── config.py       # 配置管理模块
│   ├── config.json     # 配置文件
│   └── templates/      # 模板目录
│       ├── blog_template.md  # 默认博客模板
│       ├── simple_template.md # 简单博客模板
│       └── detailed_template.md # 详细博客模板
├── crawler.py          # 主爬虫脚本
├── generate_blog.py    # 独立博客生成脚本
├── setup_and_run.sh    # 环境设置和运行脚本
├── examples/           # 示例目录
│   ├── metadata_example.json # 示例元数据文件
│   ├── generate_blog_example.sh # 博客生成示例脚本
│   ├── images/         # 示例图片目录
│   └── output/         # 示例输出目录
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── downloader.py   # 下载器
│   ├── parser.py       # 解析器
│   ├── notifier.py     # 邮件通知模块
│   └── blog_generator.py # 博客生成模块
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

## 许可证

MIT