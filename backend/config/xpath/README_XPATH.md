# XPath规则配置指南

## 概述

本文档介绍如何配置和使用XPath规则来限定爬虫的爬取区域，避免获取到过多无关数据。

## XPath规则文件

XPath规则存储在 `config/xpath/xpath_rules.json` 文件中，采用JSON格式。每条规则包含以下字段：

- `id`: 规则的唯一标识符
- `name`: 规则的名称
- `description`: 规则的描述
- `domain_patterns`: 适用的域名模式列表，用于自动匹配
- `xpath`: XPath表达式，用于限定爬取区域

示例规则：

```json
{
    "id": "reddit_media",
    "name": "Reddit媒体图片",
    "description": "Reddit网站媒体图片区域",
    "domain_patterns": ["reddit.com", "www.reddit.com"],
    "xpath": "//div[contains(@class, 'media-lightbox-img')]"
}
```

## 配置启用XPath规则

在 `config/config.json` 文件中，添加了XPath配置部分：

```json
"crawler": {
    ...
    "xpath_config": {
        "enabled": true,
        "rules_path": "config/xpath/xpath_rules.json",
        "default_rule_id": "general_article"
    }
}
```

- `enabled`: 是否启用XPath规则
- `rules_path`: XPath规则文件的路径
- `default_rule_id`: 默认使用的规则ID，当没有找到匹配的规则时使用

## 使用方法

### 命令行参数

爬虫程序支持以下与XPath相关的命令行参数：

- `--rule-id`: 指定使用的XPath规则ID
- `--list-rules`: 列出所有可用的XPath规则

### 示例

1. 使用指定的XPath规则ID爬取网页：

```bash
python crawler.py --url https://www.reddit.com/r/pics --rule-id reddit_media
```

2. 使用自动匹配的XPath规则爬取网页：

```bash
python crawler.py --url https://www.reddit.com/r/pics
```

3. 列出所有可用的XPath规则：

```bash
python crawler.py --list-rules
```

## 添加新规则

要添加新的XPath规则，请编辑 `config/xpath/xpath_rules.json` 文件，在 `rules` 数组中添加新的规则对象。

示例：

```json
{
    "id": "custom_rule",
    "name": "自定义规则",
    "description": "自定义网站的特定区域",
    "domain_patterns": ["example.com", "www.example.com"],
    "xpath": "//div[@id='content']"
}
```

## 获取XPath表达式

要获取网页元素的XPath表达式，可以使用浏览器的开发者工具：

1. 在Chrome或Firefox中，右键点击目标元素
2. 选择"检查"或"Inspect Element"
3. 在元素上右键点击
4. 选择"Copy > Copy XPath"

获取到的XPath可能需要进行调整，使其更加通用。例如，将具体的ID值替换为contains函数：

```
//div[@id='specific-id']  ->  //div[contains(@id, 'specific')]
```

## 调试XPath

如果XPath规则未能正确匹配目标元素，可以在浏览器的开发者工具中进行测试：

1. 打开开发者工具的Console面板
2. 使用以下JavaScript代码测试XPath表达式：

```javascript
document.evaluate("your-xpath-here", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
```

这将返回匹配的节点列表，可以查看是否正确匹配了目标元素。