# XPath规则管理API文档

XPath规则管理API提供创建、查询、更新和删除XPath规则的功能，以及获取系统预设XPath规则的能力。

## API端点

### 1. 获取用户XPath规则列表

**GET** `/api/xpath/rules`

获取当前用户创建的所有XPath规则。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "rules": [
    {
      "id": 1,
      "name": "新闻文章规则",
      "domain": "news.example.com",
      "xpath": "//div[@class='article-content']",
      "description": "提取新闻网站的文章内容",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "博客内容规则",
      "domain": "blog.example.com",
      "xpath": "//article[@class='post-content']",
      "description": "提取博客网站的文章内容",
      "created_at": "2024-01-02T14:30:00Z",
      "updated_at": "2024-01-02T15:45:00Z"
    }
  ],
  "count": 2,
  "max_rules": 10
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 401: 未认证或令牌无效

### 2. 创建XPath规则

**POST** `/api/xpath/rules`

创建新的XPath规则。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 请求参数

```json
{
  "name": "规则名称",
  "domain": "适用的域名",
  "xpath": "XPath表达式",
  "description": "规则描述" (可选)
}
```

#### 响应

**成功** (201 Created)
```json
{
  "id": 3,
  "name": "规则名称",
  "domain": "适用的域名",
  "xpath": "XPath表达式",
  "description": "规则描述",
  "created_at": "2024-01-03T09:15:00Z",
  "updated_at": "2024-01-03T09:15:00Z"
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 缺少必要字段: name, domain, xpath
- 400: XPath表达式无效
- 401: 未认证或令牌无效
- 403: 已达到最大规则数量限制

### 3. 获取XPath规则详情

**GET** `/api/xpath/rules/<int:rule_id>`

获取指定ID的XPath规则详情。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "id": 1,
  "name": "新闻文章规则",
  "domain": "news.example.com",
  "xpath": "//div[@class='article-content']",
  "description": "提取新闻网站的文章内容",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "user_id": 1
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 401: 未认证或令牌无效
- 403: 无权访问此规则
- 404: 规则不存在

### 4. 更新XPath规则

**PUT** `/api/xpath/rules/<int:rule_id>`

更新指定ID的XPath规则。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 请求参数

```json
{
  "name": "更新后的规则名称",
  "domain": "更新后的适用域名",
  "xpath": "更新后的XPath表达式",
  "description": "更新后的规则描述" (可选)
}
```

#### 响应

**成功** (200 OK)
```json
{
  "id": 1,
  "name": "更新后的规则名称",
  "domain": "更新后的适用域名",
  "xpath": "更新后的XPath表达式",
  "description": "更新后的规则描述",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-03T11:30:00Z",
  "user_id": 1
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 缺少必要字段: name, domain, xpath
- 400: XPath表达式无效
- 401: 未认证或令牌无效
- 403: 无权修改此规则
- 404: 规则不存在

### 5. 删除XPath规则

**DELETE** `/api/xpath/rules/<int:rule_id>`

删除指定ID的XPath规则。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "message": "规则删除成功"
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 401: 未认证或令牌无效
- 403: 无权删除此规则
- 404: 规则不存在

### 6. 获取系统预设XPath规则

**GET** `/api/xpath/system-rules`

获取系统预设的XPath规则列表。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "rules": [
    {
      "id": "general_article",
      "name": "通用文章规则",
      "domain": "*",
      "xpath": "//article | //div[@class='article'] | //div[@class='content']",
      "description": "适用于大多数网站的通用文章内容提取规则"
    },
    {
      "id": "news_content",
      "name": "新闻内容规则",
      "domain": "*.news.* | *.newspaper.*",
      "xpath": "//div[@class='news-content'] | //div[@id='article-body']",
      "description": "适用于新闻网站的内容提取规则"
    }
  ]
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 401: 未认证或令牌无效

## XPath规则管理流程

1. 用户可以通过 `/api/xpath/rules` 查看自己创建的XPath规则
2. 用户可以通过 `/api/xpath/system-rules` 查看系统预设的XPath规则
3. 用户可以创建新的XPath规则，但受到用户组最大规则数量的限制
4. 用户只能查看、修改和删除自己创建的规则
5. 创建爬虫任务时，可以选择使用自己的规则或系统预设规则

## 使用示例

### curl 示例

```bash
# 获取用户XPath规则列表
curl -X GET http://localhost:8000/api/xpath/rules \
  -H "Authorization: Bearer <access_token>"

# 创建新的XPath规则
curl -X POST http://localhost:8000/api/xpath/rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "技术博客规则",
    "domain": "tech.example.com",
    "xpath": "//div[@class=\'tech-article\']",
    "description": "提取技术博客的文章内容"
  }'

# 获取XPath规则详情
curl -X GET http://localhost:8000/api/xpath/rules/1 \
  -H "Authorization: Bearer <access_token>"

# 更新XPath规则
curl -X PUT http://localhost:8000/api/xpath/rules/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "更新后的技术博客规则",
    "domain": "tech.example.com",
    "xpath": "//div[@class=\'tech-article-content\']",
    "description": "更新后的技术博客内容提取规则"
  }'

# 删除XPath规则
curl -X DELETE http://localhost:8000/api/xpath/rules/1 \
  -H "Authorization: Bearer <access_token>"

# 获取系统预设XPath规则
curl -X GET http://localhost:8000/api/xpath/system-rules \
  -H "Authorization: Bearer <access_token>"
```

### Python 示例

```python
import requests

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 获取用户XPath规则列表
response = requests.get('http://localhost:8000/api/xpath/rules',
                       headers=headers)
rules = response.json()['rules']
print(f"用户规则数量: {len(rules)}")

# 创建新的XPath规则
response = requests.post('http://localhost:8000/api/xpath/rules',
                        headers=headers,
                        json={
                            'name': '技术博客规则',
                            'domain': 'tech.example.com',
                            'xpath': "//div[@class='tech-article']",
                            'description': '提取技术博客的文章内容'
                        })
new_rule = response.json()
rule_id = new_rule['id']
print(f"规则创建成功，ID: {rule_id}")

# 获取系统预设XPath规则
response = requests.get('http://localhost:8000/api/xpath/system-rules',
                       headers=headers)
system_rules = response.json()['rules']
print(f"系统规则数量: {len(system_rules)}")
```

## 注意事项

1. XPath规则的数量受用户组限制，不同用户组可以创建的规则数量不同
2. XPath表达式需要符合标准XPath语法，否则会创建失败
3. 系统预设规则不能被修改或删除，但可以被所有用户使用
4. 域名支持通配符匹配，例如 `*.example.com` 可以匹配所有example.com的子域名
5. 创建爬虫任务时，如果URL的域名与规则的域名匹配，系统会自动推荐相应的规则