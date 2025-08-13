# 爬虫配置管理API文档

## 概述

爬虫配置管理API提供爬虫配置的创建、查询、更新和删除功能。配置参数严格对应crawler.py的命令行参数，确保配置的准确性和可用性。

**基础URL**: `http://localhost:5000/api/crawler`

**认证**: 所有接口都需要Bearer Token认证

## 配置参数说明

爬虫配置参数直接对应`uv run python -m crawler.crawler`命令的参数：

| 参数名 | 对应命令行参数 | 类型 | 默认值 | 描述 |
|--------|---------------|------|--------|------|
| `output` | `--output` | string | null | 输出目录，用于临时文件和日志 |
| `data_dir` | `--data-dir` | string | null | 数据存储目录，用于保存图片和元数据 |
| `use_selenium` | `--use-selenium` | boolean | false | 使用Selenium和ChromeDriver进行爬取 |
| `timeout` | `--timeout` | integer | 30 | 请求超时时间（秒） |
| `retry` | `--retry` | integer | 3 | 失败重试次数 |
| `config` | `--config` | string | "config.json" | 配置文件路径 |
| `email_notification` | `--email-notification` | boolean | false | 是否启用邮件通知 |
| `headless` | `--headless` | boolean | true | Selenium是否使用无头模式 |
| `proxy` | `--proxy` | string | null | Selenium使用的代理服务器地址 |
| `page_load_wait` | `--page-load-wait` | integer | 10 | Selenium页面加载等待时间（秒） |
| `user_agent` | `--user-agent` | string | null | Selenium使用的用户代理字符串 |
| `rule_ids` | `--rule-ids` | string | null | XPath规则ID列表，用逗号分隔 |
| `enable_xpath` | `--enable-xpath` | boolean | false | 启用XPath选择器 |

## API接口

### 1. 创建爬虫配置

**接口**: `POST /configs`

**描述**: 创建新的爬虫配置

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "name": "string",                    // 必需，配置名称，最多200字符
  "description": "string",             // 可选，配置描述
  "output": "string",                  // 可选，输出目录
  "data_dir": "string",               // 可选，数据存储目录
  "use_selenium": boolean,             // 可选，是否使用Selenium，默认false
  "timeout": integer,                  // 可选，超时时间，默认30秒
  "retry": integer,                    // 可选，重试次数，默认3次
  "config": "string",                 // 可选，配置文件路径，默认"config.json"
  "email_notification": boolean,       // 可选，邮件通知，默认false
  "headless": boolean,                 // 可选，无头模式，默认true
  "proxy": "string",                  // 可选，代理服务器地址
  "page_load_wait": integer,           // 可选，页面加载等待时间，默认10秒
  "user_agent": "string",             // 可选，用户代理字符串
  "rule_ids": "string",               // 可选，XPath规则ID，逗号分隔
  "enable_xpath": boolean              // 可选，启用XPath，默认false
}
```

**请求示例**:
```json
{
  "name": "Reddit爬虫配置",
  "description": "用于爬取Reddit网站内容的配置",
  "data_dir": "./crawler_data",
  "use_selenium": true,
  "timeout": 60,
  "retry": 3,
  "headless": false,
  "enable_xpath": true,
  "rule_ids": "reddit_media,reddit_comments,reddit_post_title,reddit_post_description"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "爬虫配置创建成功",
  "data": {
    "id": "uuid-string",
    "name": "Reddit爬虫配置",
    "description": "用于爬取Reddit网站内容的配置",
    "output": null,
    "data_dir": "./crawler_data",
    "use_selenium": true,
    "timeout": 60,
    "retry": 3,
    "config": "config.json",
    "email_notification": false,
    "headless": false,
    "proxy": null,
    "page_load_wait": 10,
    "user_agent": null,
    "rule_ids": "reddit_media,reddit_comments,reddit_post_title,reddit_post_description",
    "enable_xpath": true,
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**状态码**:
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `500`: 服务器内部错误

---

### 2. 获取爬虫配置列表

**接口**: `GET /configs`

**描述**: 获取当前用户的爬虫配置列表，支持分页和搜索

**认证**: 需要Bearer Token

**查询参数**:
- `page`: 页码，默认1
- `per_page`: 每页数量，默认10，最大100
- `search`: 搜索关键词，在名称和描述中搜索
- `use_selenium`: 过滤是否使用Selenium，true/false
- `enable_xpath`: 过滤是否启用XPath，true/false

**请求示例**:
```
GET /api/crawler/configs?page=1&per_page=10&search=reddit&use_selenium=true
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "configs": [
      {
        "id": "uuid-string",
        "name": "Reddit爬虫配置",
        "description": "用于爬取Reddit网站内容的配置",
        "use_selenium": true,
        "enable_xpath": true,
        "timeout": 60,
        "retry": 3,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1,
      "has_prev": false,
      "has_next": false
    }
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `500`: 服务器内部错误

---

### 3. 获取单个爬虫配置

**接口**: `GET /configs/{config_id}`

**描述**: 获取指定ID的爬虫配置详情

**认证**: 需要Bearer Token

**路径参数**:
- `config_id`: 配置ID

**响应格式**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "name": "Reddit爬虫配置",
    "description": "用于爬取Reddit网站内容的配置",
    "output": null,
    "data_dir": "./crawler_data",
    "use_selenium": true,
    "timeout": 60,
    "retry": 3,
    "config": "config.json",
    "email_notification": false,
    "headless": false,
    "proxy": null,
    "page_load_wait": 10,
    "user_agent": null,
    "rule_ids": "reddit_media,reddit_comments,reddit_post_title,reddit_post_description",
    "enable_xpath": true,
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `404`: 配置不存在
- `500`: 服务器内部错误

---

### 4. 更新爬虫配置

**接口**: `PUT /configs/{config_id}`

**描述**: 更新指定ID的爬虫配置

**认证**: 需要Bearer Token

**路径参数**:
- `config_id`: 配置ID

**请求参数**: 与创建配置相同，所有字段都是可选的

**请求示例**:
```json
{
  "name": "更新后的Reddit爬虫配置",
  "timeout": 90,
  "headless": true
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "爬虫配置更新成功",
  "data": {
    "id": "uuid-string",
    "name": "更新后的Reddit爬虫配置",
    "description": "用于爬取Reddit网站内容的配置",
    "timeout": 90,
    "headless": true,
    "updated_at": "2024-01-15T11:00:00Z"
    // ... 其他字段
  }
}
```

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 配置不存在
- `500`: 服务器内部错误

---

### 5. 删除爬虫配置

**接口**: `DELETE /configs/{config_id}`

**描述**: 删除指定ID的爬虫配置

**认证**: 需要Bearer Token

**路径参数**:
- `config_id`: 配置ID

**响应格式**:
```json
{
  "success": true,
  "message": "爬虫配置删除成功"
}
```

**状态码**:
- `200`: 删除成功
- `401`: 未授权
- `404`: 配置不存在
- `409`: 配置正在被任务使用，无法删除
- `500`: 服务器内部错误

---

### 6. 验证爬虫配置

**接口**: `POST /configs/validate`

**描述**: 验证爬虫配置的有效性，不保存到数据库

**认证**: 需要Bearer Token

**请求参数**: 与创建配置相同

**响应格式**:
```json
{
  "success": true,
  "message": "配置验证通过",
  "data": {
    "valid": true,
    "warnings": [
      "建议设置data_dir参数以保存爬取的数据"
    ],
    "command_preview": "uv run python -m crawler.crawler --data-dir ./crawler_data --use-selenium true --timeout 60 --retry 3 --headless false --enable-xpath true --rule-ids reddit_media,reddit_comments,reddit_post_title,reddit_post_description"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "配置验证失败",
  "data": {
    "valid": false,
    "errors": [
      "timeout值必须在1-3600秒之间",
      "rule_ids格式不正确，应为逗号分隔的字符串"
    ]
  }
}
```

**状态码**:
- `200`: 验证完成（无论成功或失败）
- `400`: 请求参数错误
- `401`: 未授权
- `500`: 服务器内部错误

---

### 7. 生成爬虫命令

**接口**: `GET /configs/{config_id}/command`

**描述**: 根据配置生成对应的crawler命令行

**认证**: 需要Bearer Token

**路径参数**:
- `config_id`: 配置ID

**查询参数**:
- `url`: 目标URL（必需）

**请求示例**:
```
GET /api/crawler/configs/uuid-string/command?url=https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "command": "uv run python -m crawler.crawler --url \"https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/\" --data-dir ./crawler_data --use-selenium true --timeout 60 --retry 3 --headless false --enable-xpath true --rule-ids reddit_media,reddit_comments,reddit_post_title,reddit_post_description",
    "config_id": "uuid-string",
    "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/"
  }
}
```

**状态码**:
- `200`: 生成成功
- `400`: 缺少URL参数
- `401`: 未授权
- `404`: 配置不存在
- `500`: 服务器内部错误

---

## 使用示例

### JavaScript示例

```javascript
// 创建爬虫配置
const createCrawlerConfig = async (configData, token) => {
  const response = await fetch('/api/crawler/configs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(configData)
  });
  return await response.json();
};

// 获取配置列表
const getCrawlerConfigs = async (token, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const response = await fetch(`/api/crawler/configs?${queryString}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 生成爬虫命令
const generateCrawlerCommand = async (configId, url, token) => {
  const response = await fetch(`/api/crawler/configs/${configId}/command?url=${encodeURIComponent(url)}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### Python示例

```python
import requests

def create_crawler_config(config_data, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post('/api/crawler/configs', json=config_data, headers=headers)
    return response.json()

def get_crawler_configs(token, **params):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/api/crawler/configs', params=params, headers=headers)
    return response.json()

def generate_crawler_command(config_id, url, token):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'url': url}
    response = requests.get(f'/api/crawler/configs/{config_id}/command', 
                          params=params, headers=headers)
    return response.json()
```

## 配置最佳实践

1. **命名规范**: 使用描述性的配置名称，如"Reddit爬虫配置"、"新闻网站爬虫配置"
2. **参数设置**: 
   - 对于JavaScript重度网站，建议启用`use_selenium`
   - 设置合理的`timeout`值，避免过长等待
   - 根据网站响应速度调整`retry`次数
3. **XPath规则**: 启用`enable_xpath`时，确保`rule_ids`对应的规则已在数据库中配置
4. **资源管理**: 合理设置`data_dir`，避免磁盘空间不足
5. **性能优化**: 生产环境建议启用`headless`模式以提高性能

## 错误处理

所有API都遵循统一的错误响应格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  }
}
```

常见错误代码：
- `VALIDATION_ERROR`: 参数验证失败
- `CONFIG_NOT_FOUND`: 配置不存在
- `CONFIG_IN_USE`: 配置正在被使用
- `INVALID_URL`: URL格式不正确
- `INVALID_RULE_IDS`: XPath规则ID格式错误

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本
  - 支持完整的爬虫配置CRUD操作
  - 参数验证和命令生成功能
  - 与crawler.py命令行参数完全对应