# XPath配置管理API文档

## 概述

XPath配置管理API提供XPath规则的创建、查询、更新和删除功能，以及与`crawler/config/xpath/xpath_rules.json`文件的同步机制。确保数据库中的XPath配置与JSON文件保持一致。

**基础URL**: `http://localhost:5000/api/xpath`

**认证**: 所有接口都需要Bearer Token认证

## XPath规则结构

XPath规则包含以下核心字段：

| 字段名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `rule_id` | string | 是 | 规则唯一标识符 |
| `name` | string | 是 | 规则名称 |
| `description` | string | 否 | 规则描述 |
| `domain_patterns` | array | 是 | 适用的域名模式列表 |
| `xpath` | string | 是 | 主XPath表达式 |
| `rule_type` | enum | 是 | 规则类型：text/image/link/data |
| `field_name` | string | 是 | 提取数据的字段名称 |
| `comment_xpath` | object | 否 | 扩展XPath配置（用于复杂提取） |
| `status` | enum | 否 | 规则状态：active/inactive/testing |
| `is_public` | boolean | 否 | 是否为公开规则 |

## API接口

### 1. 创建XPath规则

**接口**: `POST /rules`

**描述**: 创建新的XPath规则

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "rule_id": "string",                 // 必需，规则ID，唯一标识符
  "name": "string",                    // 必需，规则名称
  "description": "string",             // 可选，规则描述
  "domain_patterns": ["string"],       // 必需，域名模式数组
  "xpath": "string",                   // 必需，XPath表达式
  "rule_type": "text|image|link|data", // 必需，规则类型
  "field_name": "string",              // 必需，字段名称
  "comment_xpath": {                   // 可选，扩展XPath配置
    "text": "string",
    "author": "string",
    "score": "string",
    "timestamp": "string"
  },
  "status": "active|inactive|testing", // 可选，默认active
  "is_public": boolean                 // 可选，默认false
}
```

**请求示例**:
```json
{
  "rule_id": "reddit_post_title",
  "name": "Reddit帖子标题提取",
  "description": "提取Reddit帖子的标题信息",
  "domain_patterns": ["reddit.com", "www.reddit.com"],
  "xpath": "//h1[@id='post-title-t3_1mgqbmr']/text()",
  "rule_type": "text",
  "field_name": "title",
  "status": "active",
  "is_public": true
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "XPath规则创建成功",
  "data": {
    "id": "uuid-string",
    "rule_id": "reddit_post_title",
    "name": "Reddit帖子标题提取",
    "description": "提取Reddit帖子的标题信息",
    "domain_patterns": ["reddit.com", "www.reddit.com"],
    "xpath": "//h1[@id='post-title-t3_1mgqbmr']/text()",
    "rule_type": "text",
    "field_name": "title",
    "comment_xpath": null,
    "status": "active",
    "is_public": true,
    "usage_count": 0,
    "last_used_at": null,
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
- `409`: 规则ID已存在
- `500`: 服务器内部错误

---

### 2. 获取XPath规则列表

**接口**: `GET /rules`

**描述**: 获取XPath规则列表，支持分页和过滤

**认证**: 需要Bearer Token

**查询参数**:
- `page`: 页码，默认1
- `per_page`: 每页数量，默认10，最大100
- `search`: 搜索关键词，在名称和描述中搜索
- `rule_type`: 过滤规则类型，text/image/link/data
- `status`: 过滤状态，active/inactive/testing
- `is_public`: 过滤公开状态，true/false
- `domain`: 过滤域名模式

**请求示例**:
```
GET /api/xpath/rules?page=1&per_page=10&rule_type=text&status=active&is_public=true
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "rules": [
      {
        "id": "uuid-string",
        "rule_id": "reddit_post_title",
        "name": "Reddit帖子标题提取",
        "description": "提取Reddit帖子的标题信息",
        "domain_patterns": ["reddit.com", "www.reddit.com"],
        "xpath": "//h1[@id='post-title-t3_1mgqbmr']/text()",
        "rule_type": "text",
        "field_name": "title",
        "status": "active",
        "is_public": true,
        "usage_count": 5,
        "last_used_at": "2024-01-15T09:00:00Z",
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

### 3. 获取单个XPath规则

**接口**: `GET /rules/{rule_id}`

**描述**: 获取指定rule_id的XPath规则详情

**认证**: 需要Bearer Token

**路径参数**:
- `rule_id`: 规则ID（不是数据库主键ID）

**响应格式**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "rule_id": "reddit_post_title",
    "name": "Reddit帖子标题提取",
    "description": "提取Reddit帖子的标题信息",
    "domain_patterns": ["reddit.com", "www.reddit.com"],
    "xpath": "//h1[@id='post-title-t3_1mgqbmr']/text()",
    "rule_type": "text",
    "field_name": "title",
    "comment_xpath": null,
    "status": "active",
    "is_public": true,
    "usage_count": 5,
    "last_used_at": "2024-01-15T09:00:00Z",
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `404`: 规则不存在
- `500`: 服务器内部错误

---

### 4. 更新XPath规则

**接口**: `PUT /rules/{rule_id}`

**描述**: 更新指定rule_id的XPath规则

**认证**: 需要Bearer Token

**路径参数**:
- `rule_id`: 规则ID

**请求参数**: 与创建规则相同，所有字段都是可选的（除了rule_id不能修改）

**请求示例**:
```json
{
  "name": "更新后的Reddit帖子标题提取",
  "description": "更新后的描述",
  "status": "active"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "XPath规则更新成功",
  "data": {
    "id": "uuid-string",
    "rule_id": "reddit_post_title",
    "name": "更新后的Reddit帖子标题提取",
    "description": "更新后的描述",
    "status": "active",
    "updated_at": "2024-01-15T11:00:00Z"
    // ... 其他字段
  }
}
```

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 规则不存在
- `500`: 服务器内部错误

---

### 5. 删除XPath规则

**接口**: `DELETE /rules/{rule_id}`

**描述**: 删除指定rule_id的XPath规则

**认证**: 需要Bearer Token

**路径参数**:
- `rule_id`: 规则ID

**响应格式**:
```json
{
  "success": true,
  "message": "XPath规则删除成功"
}
```

**状态码**:
- `200`: 删除成功
- `401`: 未授权
- `404`: 规则不存在
- `409`: 规则正在被任务使用，无法删除
- `500`: 服务器内部错误

---

### 6. 验证XPath规则

**接口**: `POST /rules/validate`

**描述**: 验证XPath规则的有效性，不保存到数据库

**认证**: 需要Bearer Token

**请求参数**: 与创建规则相同

**响应格式**:
```json
{
  "success": true,
  "message": "XPath规则验证通过",
  "data": {
    "valid": true,
    "warnings": [
      "建议添加更多域名模式以提高规则的适用性"
    ],
    "xpath_syntax": "valid",
    "domain_patterns_count": 2
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "XPath规则验证失败",
  "data": {
    "valid": false,
    "errors": [
      "XPath语法错误：缺少闭合括号",
      "domain_patterns不能为空",
      "rule_type必须是text、image、link或data之一"
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

### 7. 同步到JSON文件

**接口**: `POST /sync/to-json`

**描述**: 将数据库中的活跃公开XPath规则同步到JSON文件

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "message": "成功同步 4 个规则到JSON文件",
  "data": {
    "synced_rules": 4,
    "json_file_path": "/path/to/crawler/config/xpath/xpath_rules.json",
    "sync_time": "2024-01-15T11:00:00Z"
  }
}
```

**状态码**:
- `200`: 同步成功
- `401`: 未授权
- `500`: 同步失败或服务器内部错误

---

### 8. 从JSON文件同步

**接口**: `POST /sync/from-json`

**描述**: 从JSON文件同步XPath规则到数据库

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "message": "JSON到数据库同步完成: 创建 2 个，更新 2 个规则",
  "data": {
    "created_rules": 2,
    "updated_rules": 2,
    "json_file_path": "/path/to/crawler/config/xpath/xpath_rules.json",
    "sync_time": "2024-01-15T11:00:00Z"
  }
}
```

**状态码**:
- `200`: 同步成功
- `401`: 未授权
- `500`: 同步失败或服务器内部错误

---

### 9. 双向同步

**接口**: `POST /sync/bidirectional`

**描述**: 执行双向同步：先从JSON同步到数据库，再从数据库同步到JSON

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "message": "双向同步完成: JSON到数据库同步完成: 创建 1 个，更新 1 个规则; 成功同步 4 个规则到JSON文件",
  "data": {
    "json_to_db": {
      "created_rules": 1,
      "updated_rules": 1
    },
    "db_to_json": {
      "synced_rules": 4
    },
    "sync_time": "2024-01-15T11:00:00Z"
  }
}
```

**状态码**:
- `200`: 同步成功
- `401`: 未授权
- `500`: 同步失败或服务器内部错误

---

### 10. 获取JSON文件信息

**接口**: `GET /sync/json-info`

**描述**: 获取JSON文件的基本信息和统计数据

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "data": {
    "file_path": "/path/to/crawler/config/xpath/xpath_rules.json",
    "exists": true,
    "total_rules": 4,
    "rule_types": {
      "text": 2,
      "image": 1,
      "data": 1
    },
    "rule_ids": [
      "reddit_media",
      "reddit_comments",
      "reddit_post_title",
      "reddit_post_description"
    ],
    "file_size": 2048,
    "last_modified": "2024-01-15T11:00:00Z"
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `500`: 服务器内部错误

---

### 11. 测试XPath规则

**接口**: `POST /rules/test`

**描述**: 在指定URL上测试XPath规则的提取效果

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "rule_id": "string",     // 可选，已存在的规则ID
  "xpath": "string",       // 可选，临时XPath表达式
  "url": "string",         // 必需，测试URL
  "use_selenium": boolean  // 可选，是否使用Selenium，默认false
}
```

**请求示例**:
```json
{
  "rule_id": "reddit_post_title",
  "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
  "use_selenium": true
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "XPath规则测试完成",
  "data": {
    "rule_id": "reddit_post_title",
    "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
    "extracted_data": [
      "Leicester, England 1954"
    ],
    "extraction_count": 1,
    "execution_time": 2.5,
    "status": "success"
  }
}
```

**状态码**:
- `200`: 测试完成
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 规则不存在
- `500`: 测试失败或服务器内部错误

---

## 复杂XPath规则示例

### Reddit评论提取规则

```json
{
  "rule_id": "reddit_comments",
  "name": "Reddit评论",
  "description": "Reddit网站评论区域 - 基于最新HTML结构优化",
  "domain_patterns": ["reddit.com", "www.reddit.com"],
  "xpath": "//shreddit-comment[@author and @thingid]",
  "rule_type": "data",
  "field_name": "reddit_comments",
  "comment_xpath": {
    "text": ".//div[contains(@class, 'md') and contains(@class, 'text-14-scalable')]//p/text() | .//div[contains(@id, '-post-rtjson-content')]//p/text()",
    "author": "@author",
    "score": "@score",
    "timestamp": ".//time/@datetime",
    "comment_id": "@thingid",
    "depth": "@depth",
    "permalink": "@permalink"
  },
  "status": "active",
  "is_public": true
}
```

## 使用示例

### JavaScript示例

```javascript
// 创建XPath规则
const createXPathRule = async (ruleData, token) => {
  const response = await fetch('/api/xpath/rules', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(ruleData)
  });
  return await response.json();
};

// 获取规则列表
const getXPathRules = async (token, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const response = await fetch(`/api/xpath/rules?${queryString}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 同步到JSON文件
const syncToJson = async (token) => {
  const response = await fetch('/api/xpath/sync/to-json', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 测试XPath规则
const testXPathRule = async (testData, token) => {
  const response = await fetch('/api/xpath/rules/test', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(testData)
  });
  return await response.json();
};
```

### Python示例

```python
import requests

def create_xpath_rule(rule_data, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post('/api/xpath/rules', json=rule_data, headers=headers)
    return response.json()

def sync_xpath_to_json(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('/api/xpath/sync/to-json', headers=headers)
    return response.json()

def test_xpath_rule(rule_id, url, token, use_selenium=False):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'rule_id': rule_id,
        'url': url,
        'use_selenium': use_selenium
    }
    response = requests.post('/api/xpath/rules/test', json=data, headers=headers)
    return response.json()
```

## 同步机制说明

### 自动同步触发时机

1. **创建规则时**: 如果规则设置为公开（`is_public=true`），自动同步到JSON文件
2. **更新规则时**: 如果规则状态或公开性发生变化，自动同步到JSON文件
3. **删除规则时**: 自动从JSON文件中移除对应规则
4. **任务创建时**: 创建爬虫任务时自动执行双向同步

### 手动同步选项

1. **数据库→JSON**: 将数据库中的活跃公开规则同步到JSON文件
2. **JSON→数据库**: 将JSON文件中的规则导入到数据库
3. **双向同步**: 先导入JSON规则，再导出到JSON文件，确保完全一致

## 最佳实践

1. **规则命名**: 使用描述性的rule_id，如"site_content_title"、"product_price"
2. **域名模式**: 包含主域名和常见子域名，如["example.com", "www.example.com"]
3. **XPath编写**: 
   - 使用相对路径提高规则的通用性
   - 避免使用绝对位置索引，如[1]、[2]
   - 优先使用class、id等稳定属性
4. **规则测试**: 创建规则后使用测试接口验证提取效果
5. **版本管理**: 重要规则修改前先备份，使用描述字段记录变更原因
6. **性能优化**: 复杂规则使用comment_xpath分解，避免单个XPath过于复杂

## 错误处理

常见错误代码：
- `RULE_ID_EXISTS`: 规则ID已存在
- `INVALID_XPATH`: XPath语法错误
- `INVALID_RULE_TYPE`: 无效的规则类型
- `DOMAIN_PATTERNS_EMPTY`: 域名模式不能为空
- `RULE_IN_USE`: 规则正在被任务使用
- `SYNC_FAILED`: 同步操作失败
- `JSON_FILE_ERROR`: JSON文件读写错误

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本
  - 支持完整的XPath规则CRUD操作
  - 数据库与JSON文件双向同步机制
  - XPath规则验证和测试功能
  - 复杂规则支持（comment_xpath）