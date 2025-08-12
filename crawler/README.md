# Crawler模块使用说明

## 概述

Crawler模块是智能爬虫内容管理系统的核心组件，提供强大的网页内容抓取和解析功能。支持基于XPath规则的精确内容提取，特别针对Reddit等社交媒体平台进行了优化。

## 主要特性

- 🕷️ 智能网页内容抓取
- 🎯 基于XPath规则的精确内容提取
- 🌐 Selenium浏览器自动化支持
- 📱 Reddit等社交媒体平台专项支持
- 🖼️ 图片自动下载和处理
- 📝 评论和文本内容结构化提取
- ⚙️ 灵活的配置管理

## 安装和配置

### 依赖管理

本项目使用`uv`进行Python依赖管理：

```bash
# 安装项目依赖
uv sync
```

### 配置文件

主要配置文件位于：
- `crawler/config/config.json` - 主配置文件
- `crawler/config/xpath/xpath_rules.json` - XPath规则配置

## 使用方法

### 基本命令格式

```bash
uv run python -m crawler.crawler [参数]
```

### 完整示例命令

```bash
uv run python -m crawler.crawler \
  --url "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/" \
  --rule-ids "reddit_media,reddit_comments,reddit_post_title,reddit_post_description" \
  --data-dir ./crawler_data \
  --use-selenium true \
  --enable-xpath true \
  --timeout 60 \
  --headless false
```

### 命令行参数详解

#### 必需参数

- `--url <URL>`: 要爬取的网页URL
  - 示例：`--url "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/"`

#### 核心参数

- `--rule-ids <规则ID列表>`: 指定使用的XPath规则，用逗号分隔
  - 示例：`--rule-ids "reddit_media,reddit_comments,reddit_post_title,reddit_post_description"`
  - 可用规则ID见下文"可用XPath规则"部分

- `--data-dir <目录路径>`: 数据存储目录
  - 示例：`--data-dir ./crawler_data`
  - 默认：当前目录下的data文件夹

- `--enable-xpath <true/false>`: 启用XPath规则解析
  - 示例：`--enable-xpath true`
  - 默认：根据配置文件决定

#### Selenium配置参数

- `--use-selenium <true/false>`: 启用Selenium浏览器自动化
  - 示例：`--use-selenium true`
  - 推荐：对于动态内容网站设置为true

- `--headless <true/false>`: 无头模式运行浏览器
  - 示例：`--headless false`
  - true：后台运行，不显示浏览器窗口
  - false：显示浏览器窗口，便于调试

- `--proxy <代理地址>`: 设置代理服务器
  - 示例：`--proxy "http://127.0.0.1:8080"`

- `--user-agent <用户代理>`: 自定义用户代理字符串
  - 示例：`--user-agent "Mozilla/5.0 (compatible; CustomBot/1.0)"`

- `--page-load-wait <秒数>`: 页面加载等待时间
  - 示例：`--page-load-wait 10`
  - 默认：根据配置文件决定

#### 其他参数

- `--timeout <秒数>`: 请求超时时间
  - 示例：`--timeout 60`
  - 默认：30秒

- `--retry <次数>`: 失败重试次数
  - 示例：`--retry 3`
  - 默认：2次

- `--output <目录>`: 输出文件目录
  - 示例：`--output ./output`
  - 默认：项目根目录下的output文件夹

- `--task-id <任务ID>`: 指定任务ID
  - 示例：`--task-id "reddit_crawl_001"`
  - 默认：自动生成

#### 工具参数

- `--list-rules`: 列出所有可用的XPath规则
  - 示例：`uv run python -m crawler.crawler --list-rules`

- `--config <配置文件>`: 指定配置文件路径
  - 示例：`--config ./custom_config.json`

## 可用XPath规则

当前支持的XPath规则ID：

### Reddit专用规则

1. **reddit_media** - Reddit媒体图片
   - 描述：提取Reddit帖子中的媒体图片
   - 适用域名：reddit.com, www.reddit.com
   - 提取内容：图片URL和相关信息

2. **reddit_comments** - Reddit评论
   - 描述：提取Reddit帖子的评论内容
   - 适用域名：reddit.com, www.reddit.com
   - 提取内容：评论文本、作者、评分、时间戳等

3. **reddit_post_title** - Reddit帖子标题
   - 描述：提取Reddit帖子的标题信息
   - 适用域名：reddit.com, www.reddit.com
   - 提取内容：帖子标题

4. **reddit_post_description** - Reddit帖子描述
   - 描述：提取Reddit帖子的描述信息
   - 适用域名：reddit.com, www.reddit.com
   - 提取内容：帖子正文描述

### 查看所有规则

```bash
uv run python -m crawler.crawler --list-rules
```

## 使用场景示例

### 1. 爬取Reddit帖子完整信息

```bash
# 获取帖子标题、描述、图片和评论
uv run python -m crawler.crawler \
  --url "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/" \
  --rule-ids "reddit_media,reddit_comments,reddit_post_title,reddit_post_description" \
  --use-selenium true \
  --enable-xpath true \
  --headless false
```

### 2. 仅获取Reddit图片

```bash
# 只提取媒体图片
uv run python -m crawler.crawler \
  --url "https://www.reddit.com/r/pics/comments/example/" \
  --rule-ids "reddit_media" \
  --use-selenium true \
  --enable-xpath true
```

### 3. 批量处理（脚本模式）

```bash
# 设置较长超时时间，适合批量处理
uv run python -m crawler.crawler \
  --url "https://www.reddit.com/r/technology/" \
  --rule-ids "reddit_post_title,reddit_post_description" \
  --timeout 120 \
  --retry 5 \
  --headless true
```

## 输出结果

### 文件结构

爬取完成后，结果将保存在指定的数据目录中：

```
data_dir/
├── task_[timestamp]/
│   ├── metadata.json      # 任务元数据
│   ├── content.json       # 提取的内容数据
│   ├── images/           # 下载的图片文件
│   └── logs/             # 任务日志
```

### 数据格式

提取的内容以JSON格式保存，包含：

```json
{
  "title": "帖子标题",
  "description": "帖子描述",
  "images": [
    {
      "url": "图片URL",
      "local_path": "本地保存路径",
      "alt_text": "图片描述"
    }
  ],
  "comments": [
    {
      "text": "评论内容",
      "author": "作者名",
      "score": "评分",
      "timestamp": "时间戳"
    }
  ],
  "xpath_rules_used": ["使用的规则ID列表"],
  "metadata": {
    "url": "原始URL",
    "crawl_time": "爬取时间",
    "task_id": "任务ID"
  }
}
```

## 故障排除

### 常见问题

1. **Selenium启动失败**
   - 确保已安装Chrome浏览器
   - 检查ChromeDriver版本兼容性
   - 尝试使用`--headless true`参数

2. **XPath规则无匹配结果**
   - 使用`--list-rules`查看可用规则
   - 检查目标网站是否更新了HTML结构
   - 尝试不同的规则ID组合

3. **网络连接问题**
   - 增加`--timeout`参数值
   - 使用`--proxy`设置代理
   - 检查目标网站的访问限制

4. **权限问题**
   - 确保数据目录有写入权限
   - 检查输出目录是否存在

### 调试模式

```bash
# 启用详细日志和浏览器显示
uv run python -m crawler.crawler \
  --url "目标URL" \
  --headless false \
  --timeout 120 \
  --retry 1
```

## 配置自定义规则

### 添加新的XPath规则

编辑`crawler/config/xpath/xpath_rules.json`文件：

```json
{
  "rules": [
    {
      "id": "custom_rule",
      "name": "自定义规则",
      "description": "规则描述",
      "domain_patterns": ["example.com"],
      "xpath": "//div[@class='content']",
      "rule_type": "text",
      "field_name": "custom_content"
    }
  ]
}
```

### 规则字段说明

- `id`: 规则唯一标识符
- `name`: 规则显示名称
- `description`: 规则描述
- `domain_patterns`: 适用的域名模式
- `xpath`: XPath选择器表达式
- `rule_type`: 规则类型（text/image/link）
- `field_name`: 结果字段名称

## 性能优化建议

1. **合理使用Selenium**
   - 仅在需要JavaScript渲染时启用
   - 使用无头模式提高性能

2. **规则选择**
   - 只使用必需的XPath规则
   - 避免过于复杂的XPath表达式

3. **网络优化**
   - 设置合适的超时时间
   - 使用代理分散请求

4. **资源管理**
   - 定期清理临时文件
   - 监控磁盘空间使用

## 更多信息

- 项目主页：[GitHub Repository]
- 问题反馈：[Issues]
- 文档更新：[Wiki]

---

*最后更新：2024年*