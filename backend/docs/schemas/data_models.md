# 数据模型定义

本文档定义了爬虫系统API中使用的主要数据模型和结构。

## 用户相关模型

### 用户模型 (User)

```json
{
  "id": 1,                           // 用户ID，整数
  "username": "example_user",        // 用户名，字符串
  "email": "user@example.com",       // 电子邮箱，字符串
  "group_id": 1,                     // 用户组ID，整数
  "created_at": "2024-01-01T00:00:00Z", // 创建时间，ISO 8601格式
  "rule_count": 5                    // 用户创建的XPath规则数量，整数
}
```

### 用户组模型 (UserGroup)

```json
{
  "id": 1,                           // 用户组ID，整数
  "name": "standard",                // 用户组名称，字符串
  "max_xpath_rules": 10,             // 最大XPath规则数量，整数
  "allowed_templates": [              // 允许使用的博客模板，字符串数组
    "default",
    "tech_blog"
  ]
}
```

### 认证令牌模型 (AuthToken)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // JWT访问令牌，字符串
  "token_type": "bearer",            // 令牌类型，字符串
  "expires_in": 86400                // 过期时间（秒），整数
}
```

## 爬虫相关模型

### 爬虫任务模型 (CrawlerTask)

```json
{
  "task_id": "task_20240101120000_1", // 任务ID，字符串
  "url": "https://example.com/article", // 爬取URL，字符串
  "task_name": "示例任务",            // 任务名称，字符串
  "created_at": "2024-01-01T12:00:00Z", // 创建时间，ISO 8601格式
  "user_id": 1,                     // 用户ID，整数
  "status": "success",               // 任务状态，字符串，可选值：pending, running, success, failed
  "use_selenium": true,              // 是否使用Selenium，布尔值
  "use_xpath": true,                 // 是否使用XPath规则，布尔值
  "xpath_rule_id": "general_article", // XPath规则ID，字符串或整数
  "is_user_rule": false,             // 是否用户自定义规则，布尔值
  "blog_template": "default"         // 博客模板名称，字符串
}
```

### 输出文件模型 (OutputFile)

```json
{
  "name": "content.json",            // 文件名，字符串
  "path": "content.json",            // 文件路径，字符串
  "size": 1024,                      // 文件大小（字节），整数
  "created_at": "2024-01-01T12:05:00Z" // 创建时间，ISO 8601格式
}
```

### 博客模板模型 (BlogTemplate)

```json
{
  "name": "default",                 // 模板名称，字符串
  "description": "默认博客模板",       // 模板描述，字符串
  "author": "System",                // 作者，字符串
  "version": "1.0",                  // 版本，字符串
  "preview": "https://example.com/templates/default/preview.png" // 预览图URL，字符串
}
```

## XPath规则相关模型

### 用户XPath规则模型 (UserXPathRule)

```json
{
  "id": 1,                           // 规则ID，整数
  "name": "新闻文章规则",              // 规则名称，字符串
  "domain": "news.example.com",       // 适用域名，字符串
  "xpath": "//div[@class='article-content']", // XPath表达式，字符串
  "description": "提取新闻网站的文章内容", // 规则描述，字符串
  "created_at": "2024-01-01T10:00:00Z", // 创建时间，ISO 8601格式
  "updated_at": "2024-01-01T10:00:00Z", // 更新时间，ISO 8601格式
  "user_id": 1                      // 用户ID，整数
}
```

### 系统XPath规则模型 (SystemXPathRule)

```json
{
  "id": "general_article",            // 规则ID，字符串
  "name": "通用文章规则",              // 规则名称，字符串
  "domain": "*",                     // 适用域名，字符串，支持通配符
  "xpath": "//article | //div[@class='article'] | //div[@class='content']", // XPath表达式，字符串
  "description": "适用于大多数网站的通用文章内容提取规则" // 规则描述，字符串
}
```

## 后门API相关模型

### 后门爬取任务模型 (BackdoorCrawlerTask)

```json
{
  "url": "https://example.com/article", // 爬取URL，字符串，必填
  "use_selenium": true,              // 是否使用Selenium，布尔值，可选
  "use_xpath": true,                 // 是否使用XPath规则，布尔值，可选
  "xpath_rule_id": "general_article", // XPath规则ID，字符串，可选
  "timeout": 30,                     // 超时时间（秒），整数，可选
  "retries": 3,                      // 重试次数，整数，可选
  "callback_url": "https://example.com/callback" // 回调URL，字符串，可选
}
```

### 后门任务状态模型 (BackdoorTaskStatus)

```json
{
  "task_id": "task_20240101120000_1", // 任务ID，字符串
  "status": "success",               // 任务状态，字符串，可选值：pending, running, success, failed
  "created_at": "2024-01-01T12:00:00Z", // 创建时间，ISO 8601格式
  "completed_at": "2024-01-01T12:05:00Z", // 完成时间，ISO 8601格式
  "result": {                       // 任务结果，对象，仅当状态为success时存在
    "title": "示例文章标题",           // 文章标题，字符串
    "content": "文章内容...",         // 文章内容，字符串
    "metadata": {                   // 元数据，对象
      "author": "作者名",            // 作者，字符串
      "publish_date": "2024-01-01", // 发布日期，字符串
      "tags": ["标签1", "标签2"]     // 标签，字符串数组
    }
  },
  "error": "错误描述"                 // 错误描述，字符串，仅当状态为failed时存在
}
```

## 错误响应模型

### 错误响应 (ErrorResponse)

```json
{
  "error": "错误描述",                // 错误描述，字符串
  "code": "ERROR_CODE",             // 错误代码，字符串，可选
  "details": "详细错误信息"           // 详细错误信息，字符串，可选
}
```

## 数据类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| 整数 | 32位整数 | 1, 42, -10 |
| 字符串 | UTF-8编码的文本 | "example", "用户名" |
| 布尔值 | 真或假 | true, false |
| 数组 | 有序列表 | [1, 2, 3], ["a", "b"] |
| 对象 | 键值对集合 | {"key": "value"} |
| 日期时间 | ISO 8601格式的时间戳 | "2024-01-01T12:00:00Z" |

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 数据关系图

```
User (用户) 1 ---> n UserXPathRule (用户XPath规则)
       |
       | 1
       v
 UserGroup (用户组) 1 ---> n BlogTemplate (博客模板)
       ^
       |
       | n
       |
User (用户) 1 ---> n CrawlerTask (爬虫任务) ---> 1 OutputFile (输出文件)
                                  |
                                  v
                          XPathRule (XPath规则)
                          /          \
                         /            \
        UserXPathRule (用户规则)  SystemXPathRule (系统规则)
```

## 注意事项

1. 所有时间戳均使用ISO 8601格式，并以UTC时区表示
2. 用户XPath规则的ID为整数，系统XPath规则的ID为字符串
3. 爬虫任务的ID格式为 `task_YYYYMMDDhhmmss_n`，其中n为序号
4. 错误响应中的code字段可用于客户端进行错误处理和国际化
5. 用户组决定了用户可以创建的最大XPath规则数量和可用的博客模板