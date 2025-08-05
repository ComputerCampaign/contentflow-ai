# 博客生成模块 (Blog Generator)

独立的博客生成功能模块，用于根据爬虫结果自动生成博客文章。

## 功能特性

- 🚀 独立模块设计，与爬虫和后端API服务分离
- 📝 支持自定义博客模板
- 🖼️ 自动处理图片上传到GitHub图床
- 🏷️ 智能标签生成
- 📊 支持多种数据源（JSON元数据、CSV文件等）
- 🎨 Markdown格式输出
- 📁 自动文件管理（草稿/发布目录）

## 目录结构

```
blog_generator/
├── __init__.py              # 模块初始化
├── blog_generator.py        # 主要博客生成器类
├── config.py               # 配置管理
├── logger.py               # 日志配置
├── README.md               # 说明文档
├── config/                 # 配置文件目录
│   ├── blog_config.json    # 博客配置文件
│   └── templates/          # 模板目录
│       └── blog_template.md # 默认博客模板
└── utils/                  # 工具模块
    ├── __init__.py
    └── generate_blog.py     # 博客生成工具
```

## 快速开始

### 基本使用

```python
from blog_generator import BlogGenerator, blog_config

# 创建博客生成器实例
generator = BlogGenerator()

# 生成博客
success, blog_path = generator.generate_blog(
    url="https://example.com",
    html_content="<html>...</html>",
    parsed_data={
        "page_title": "示例文章",
        "headings": [{"level": 1, "text": "标题1"}]
    },
    data_dir="/path/to/data"
)

if success:
    print(f"博客已生成: {blog_path}")
```

### 使用工具模块

```python
from blog_generator.utils import BlogGenerator, load_metadata

# 加载元数据
metadata = load_metadata("metadata.json")

# 创建生成器并生成博客
generator = BlogGenerator(template_name="custom")
success, path = generator.generate_blog(
    images=["image1.jpg", "image2.jpg"],
    metadata=metadata
)
```

## 配置说明

### 博客配置 (blog_config.json)

```json
{
    "blog": {
        "enabled": true,
        "output_dir": "blogs",
        "template_file": "blog_generator/config/templates/blog_template.md",
        "use_crawler_image_storage": true
    },
    "content": {
        "min_length": 500,
        "max_length": 3000,
        "include_images": true
    }
}
```

### 模板变量

博客模板支持以下变量：

- `{title}` - 文章标题
- `{date}` - 发布日期
- `{source_name}` - 来源网站名称
- `{source_url}` - 来源URL
- `{summary}` - 文章摘要
- `{image_gallery}` - 图片画廊
- `{content}` - 文章内容
- `{tags}` - 标签

## API 参考

### BlogGenerator 类

#### 方法

- `__init__(template_name=None)` - 初始化生成器
- `generate_blog(url, html_content, parsed_data, data_dir)` - 生成博客文章

#### 配置方法

- `blog_config.get(*keys, default=None)` - 获取配置值
- `blog_config.set(*keys, value=value)` - 设置配置值

### 工具函数

- `load_metadata(metadata_path)` - 加载元数据文件
- `list_available_templates()` - 列出可用模板

## 依赖要求

- Python 3.7+
- pandas
- beautifulsoup4
- requests

## 注意事项

1. 确保GitHub图床配置正确（如果使用图片上传功能）
2. 模板文件必须使用UTF-8编码
3. 生成的博客文件默认保存在`blogs/drafts`目录
4. 图片会自动上传到GitHub图床并在博客中引用

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本博客生成功能
- 集成GitHub图床上传
- 支持自定义模板