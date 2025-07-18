# 网页图片爬虫与博客生成器

这是一个集成了网页图片爬取和博客生成功能的工具，可以自动抓取网页中的图片和标题，并根据抓取的内容生成博客文章。现在已升级为完整的Web应用，提供用户友好的界面和API接口。

## 功能特点

### 爬虫模块

- 支持图片和标题抓取：自动从网页中提取图片和标题
- 支持XPath规则配置：通过配置XPath规则，精确定位网页内容
- 支持任务ID管理：便于管理多个爬取任务
- 支持邮件通知：爬取完成后自动发送邮件通知
- 支持自定义输出目录：灵活设置爬取结果的存储位置
- 支持Selenium模式：处理动态加载的网页内容
- 支持反爬虫检测绕过：通过注入特殊脚本绕过网站的爬虫检测机制

### 博客生成模块

- 支持两种生成模式：从爬虫数据生成和从自定义数据生成
- 支持多种模板：可以选择不同的博客模板
- 支持图片上传：自动将图片上传到GitHub图床
- 支持元数据定制：可以自定义博客的标题、内容、标签等
- 支持自动标签生成：根据内容自动生成标签

### Web界面和API

- 用户认证与授权：支持用户注册、登录和权限管理
- 爬虫任务管理：通过Web界面创建和管理爬虫任务
- XPath规则管理：可视化创建、编辑和管理XPath规则
- 用户管理：管理员可以管理用户和用户组
- RESTful API：提供完整的API接口，支持第三方集成
- 响应式设计：适配不同设备的屏幕尺寸

## 环境要求

- Python 3.8+
- 主要依赖库：
  - requests：HTTP请求
  - beautifulsoup4：HTML解析
  - selenium：浏览器自动化
  - timeout-decorator：函数超时控制
  - 更多依赖见`pyproject.toml`文件

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
CRAWLER_EMAIL_PASSWORD=your-email-password
CRAWLER_GITHUB_TOKEN=your-github-token
```

3. 项目会自动加载`.env`文件中的环境变量

**重要提示**：程序不会保存配置文件，所有配置都是重新读取的，敏感信息只会存在于内存中。强烈建议使用环境变量管理敏感信息，而不是直接写入配置文件。

也可以直接设置系统环境变量：

```bash
# Linux/macOS
export CRAWLER_EMAIL_PASSWORD=your-email-password
export CRAWLER_GITHUB_TOKEN=your-github-token

# Windows
set CRAWLER_EMAIL_PASSWORD=your-email-password
set CRAWLER_GITHUB_TOKEN=your-github-token
```

### 创建配置文件

如果需要手动创建配置文件，可以参考以下结构：

```json
{
  "crawler": {
    "data_dir": "data",
    "use_selenium": false,
    "timeout": 30,
    "retry": 3,
    "selenium_config": {
      "headless": true,
      "proxy": null,
      "page_load_wait": 6,
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      "disable_gpu": true,
      "no_sandbox": true,
      "disable_dev_shm_usage": true,
      "window_size": "1920,1080"
    }
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

### Selenium 配置

Selenium 模式用于处理动态加载的网页内容，可以通过以下参数进行配置：

- `headless`: 是否使用无头模式（不显示浏览器界面），默认为 `true`
- `proxy`: 代理服务器地址，格式为 `http://host:port` 或 `socks5://host:port`，默认为 `null`
- `page_load_wait`: 页面加载等待时间（秒），默认为 `6`
- `user_agent`: 自定义用户代理字符串，用于模拟特定浏览器
- `disable_gpu`: 是否禁用 GPU 加速，默认为 `true`
- `no_sandbox`: 是否禁用沙盒模式，默认为 `true`
- `disable_dev_shm_usage`: 是否禁用 /dev/shm 使用，默认为 `true`
- `window_size`: 浏览器窗口大小，格式为 `宽度,高度`，默认为 `1920,1080`

这些配置可以在 `config.json` 文件中的 `crawler.selenium_config` 部分进行设置，也可以通过命令行参数 `--use-selenium` 启用 Selenium 模式。

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
├── uv.lock             # uv依赖锁定文件
├── .env.example        # 环境变量示例文件
├── .uv/                # uv配置目录
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
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── notifier.py     # 邮件通知模块
│   ├── blog_generator.py # 博客生成器模块
│   ├── generate_blog.py # 博客生成模块
│   └── logger.py       # 日志模块
├── crawler_utils/      # 爬虫工具函数
│   ├── __init__.py
│   ├── batch_downloader.py # 批量下载器
│   ├── crawler_core.py # 爬虫核心功能
│   ├── github_image_uploader.py # GitHub图片上传模块
│   ├── html_parser.py  # HTML解析器
│   ├── image_downloader.py # 图片下载器
│   ├── selenium_renderer.py # Selenium渲染器模块
│   ├── storage_manager.py # 存储管理器
│   └── xpath_manager.py # XPath管理器
├── tests/              # 测试目录
│   ├── __init__.py
│   ├── test_crawler_basic.py # 爬虫基础测试
│   ├── test_selenium_renderer.py # Selenium渲染器测试
│   ├── test_stealth_driver.py # 无头浏览器测试
│   ├── test_enable_xpath.py # XPath功能测试
│   ├── test_xpath_rules.py # XPath规则测试
│   └── test_timeout_decorator.py # 超时控制测试
├── logs/               # 日志目录
├── blogs/              # 生成的博客目录
│   ├── .gitkeep
│   ├── README.md       # 博客目录说明文档
│   ├── drafts/         # 博客草稿目录
│   │   └── .gitkeep
│   └── published/      # 已发布博客目录
│       └── .gitkeep
├── output/             # 默认输出目录（临时文件）
│   ├── .gitkeep
│   └── README.md       # 输出目录说明文档
└── data/               # 数据存储目录（不包含在版本控制中）
    ├── .gitkeep
    └── README.md       # 数据目录说明文档
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

## Selenium渲染器

项目提供了强大的Selenium渲染器模块，用于处理动态加载的网页内容和绕过反爬虫检测。

### 功能特点

- **自动驱动管理**：使用ChromeDriverManager自动下载和管理chromedriver，无需手动下载和配置chromedriver路径
- **反爬虫检测绕过**：通过注入特殊JavaScript脚本，绕过网站的WebDriver检测机制
- **JavaScript脚本注入验证**：提供工具验证JavaScript脚本是否正确注入，确保反爬虫检测绕过有效
- **无头模式支持**：支持无头模式运行，提高性能和稳定性
- **代理支持**：支持配置代理服务器，便于处理IP限制
- **自动重试**：自动处理页面加载失败的情况，支持多次重试
- **元素交互**：支持查找和点击页面元素，便于处理复杂的交互场景
- **超时控制**：使用timeout_decorator包实现页面加载和操作的超时控制，防止长时间卡住

### 配置方法

在`config.json`中配置Selenium渲染器：

```json
"selenium_config": {
  "headless": true,       // 是否使用无头模式
  "proxy": null,          // 代理服务器地址，例如"http://127.0.0.1:8888"
  "page_load_wait": 6     // 页面加载后等待时间（秒）
}
```

### ChromeDriverManager说明

本项目使用`webdriver_manager`库的`ChromeDriverManager`来自动管理chromedriver：

- **自动下载**：根据当前Chrome浏览器版本自动下载匹配的chromedriver
- **自动缓存**：下载的chromedriver会被缓存在本地（默认在`~/.wdm`目录），避免重复下载
- **版本匹配**：自动确保chromedriver版本与Chrome浏览器版本兼容
- **无需手动配置**：不需要手动下载chromedriver或设置环境变量

这大大简化了环境配置，使用户可以专注于爬虫功能而不必担心驱动程序的兼容性问题。

### 使用方法

启用Selenium模式爬取：

```bash
python crawler.py --url https://example.com --use-selenium
```

### JavaScript脚本注入验证

为了确保反爬虫检测绕过脚本（stealth.min.js）正确注入，我们提供了验证工具：

```bash
# 使用本地测试页面验证（有头模式）
python tests/verify_js_injection.py

# 使用本地测试页面验证（无头模式）
python tests/verify_js_injection.py --headless

# 验证特定URL（有头模式）
python tests/verify_js_injection.py --url https://example.com

# 验证特定URL（无头模式）
python tests/verify_js_injection.py --headless --url https://example.com
```

验证工具会检查以下关键属性：

- **navigator.webdriver**: 应该是 `undefined` 或 `false`
- **window.chrome**: 应该存在
- **navigator.plugins.length**: 应该大于 0
- **navigator.languages**: 应该存在且非空

更多详细信息，请参阅 `docs/js_injection_verification.md` 文档。

### 使用任务ID

```bash
python crawler.py --url https://example.com --task-id my_task_name
```

如果不提供任务ID，系统会自动生成一个基于时间戳和随机UUID的任务ID，格式为`task_时间戳_随机字符串`。

任务ID将用于创建任务目录，所有与该任务相关的数据（图片、元数据等）都会存储在该目录中。

## Web应用安装与使用

### 安装前端依赖

```bash
cd frontend
npm install
```

### 构建前端

```bash
cd frontend
npm run build
```

### 启动Web应用

```bash
# 启动Flask后端服务
python app.py
```

默认情况下，Web应用将在 http://localhost:5000 上运行。

### 初始管理员账户

首次运行时，系统会自动创建一个管理员账户：

- 用户名：admin
- 密码：admin

**请在首次登录后立即修改密码！**

### API文档

API文档可通过以下URL访问：

```
http://localhost:5000/api/docs
```

## 许可证

MIT