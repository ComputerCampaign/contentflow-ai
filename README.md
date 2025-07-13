# 网页图片和标题爬虫

这是一个简单的Python爬虫项目，用于从给定网页中抓取图片和标题信息。

## 功能特点

- 支持从指定URL抓取图片和标题
- 可以保存图片到本地目录
- 可以导出标题和图片URL到CSV文件
- 支持基本的错误处理和重试机制
- 可选择使用requests或selenium+chromedriver进行爬取

## 环境要求

- Python 3.8+
- uv (Python包管理工具)

## 环境设置

### 快速设置（推荐）

项目使用uv进行依赖管理，提供了简单的一步式环境设置：

```bash
./setup.sh
```

这个脚本会自动：
1. 检查并安装uv（如果需要）
2. 创建虚拟环境
3. 安装所有项目依赖

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

详细的虚拟环境管理指南请参考：
- [UV_VENV_GUIDE.md](UV_VENV_GUIDE.md) - 详细的uv虚拟环境指南
- [UV_GUIDE.md](UV_GUIDE.md) - uv依赖管理指南

## 使用方法

### 基本用法

```bash
python crawler.py --url "https://example.com" --output "output_folder" --data-dir "data_folder"
```

### 参数说明

- `--url`: 要爬取的网页URL（必需）
- `--output`: 输出目录，用于临时文件和日志（默认为"output"）
- `--data-dir`: 数据存储目录，用于保存图片和元数据（默认为"data"）
- `--use-selenium`: 使用Selenium和ChromeDriver进行爬取（默认使用requests）
- `--timeout`: 请求超时时间，单位为秒（默认为10秒）
- `--retry`: 失败重试次数（默认为3次）

## 项目结构

```
.
├── .uv/                # uv配置目录
├── README.md           # 项目说明文档
├── UV_GUIDE.md         # uv依赖管理指南
├── UV_VENV_GUIDE.md    # uv虚拟环境详细指南
├── pyproject.toml      # 项目配置和依赖管理（uv）
├── crawler.py          # 主爬虫脚本
├── setup.sh            # 简化的环境设置脚本
├── example.py          # 使用示例脚本
├── test_crawler.py     # 测试脚本
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── downloader.py   # 下载器
│   └── parser.py       # 解析器
├── output/             # 默认输出目录
└── data/               # 数据存储目录（不包含在版本控制中）
```

## 许可证

MIT