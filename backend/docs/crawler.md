# 爬虫功能API文档

爬虫功能API提供创建爬虫任务、查询任务状态和获取爬取结果等功能。

## API端点

### 1. 创建爬虫任务

**POST** `/api/crawler/tasks`

创建新的爬虫任务。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 请求参数

```json
{
  "url": "要爬取的URL",
  "task_name": "任务名称", (可选，默认自动生成)
  "use_selenium": true/false, (可选，默认false)
  "use_xpath": true/false, (可选，默认false)
  "xpath_rule_id": "XPath规则ID", (可选，当use_xpath为true时必须提供)
  "is_user_rule": true/false, (可选，默认false，表示是否使用用户自定义规则)
  "blog_template": "博客模板名称" (可选)
}
```

#### 响应

**成功** (200 OK)
```json
{
  "task_id": "task_20240101120000_1",
  "message": "爬取任务创建成功",
  "status": "success"
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 缺少必要字段: url
- 400: 使用XPath时必须提供xpath_rule_id
- 403: 用户未分配用户组，无法使用博客模板
- 403: 无权使用博客模板
- 404: XPath规则不存在或无权访问
- 404: 系统XPath规则不存在
- 500: 爬取任务执行失败

### 2. 获取用户任务列表

**GET** `/api/crawler/tasks`

获取当前用户的爬虫任务列表。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "tasks": [
    {
      "task_id": "task_20240101120000_1",
      "url": "https://example.com/article",
      "created_at": "2024-01-01T12:00:00Z",
      "status": "success",
      "use_xpath": true,
      "blog_template": "default"
    },
    {
      "task_id": "task_20240102150000_1",
      "url": "https://example.com/another-article",
      "created_at": "2024-01-02T15:00:00Z",
      "status": "failed",
      "use_xpath": false,
      "blog_template": null
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

### 3. 获取任务详情

**GET** `/api/crawler/tasks/<task_id>`

获取指定爬虫任务的详细信息。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "task_id": "task_20240101120000_1",
  "url": "https://example.com/article",
  "created_at": "2024-01-01T12:00:00Z",
  "user_id": 1,
  "status": "success",
  "use_selenium": false,
  "use_xpath": true,
  "xpath_rule_id": "general_article",
  "is_user_rule": false,
  "blog_template": "default",
  "output_files": [
    {
      "name": "content.json",
      "path": "content.json",
      "size": 1024,
      "created_at": "2024-01-01T12:05:00Z"
    },
    {
      "name": "metadata.json",
      "path": "metadata.json",
      "size": 512,
      "created_at": "2024-01-01T12:05:00Z"
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
- 403: 无权访问此任务
- 404: 任务不存在
- 500: 获取任务详情失败

### 4. 获取可用博客模板

**GET** `/api/crawler/templates`

获取当前用户可用的博客模板列表。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "templates": [
    {
      "name": "default",
      "description": "默认博客模板",
      "author": "System",
      "version": "1.0",
      "preview": "https://example.com/templates/default/preview.png"
    },
    {
      "name": "tech_blog",
      "description": "技术博客模板",
      "author": "Admin",
      "version": "2.1",
      "preview": "https://example.com/templates/tech_blog/preview.png"
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

## 爬虫任务流程

1. 用户通过 `/api/crawler/tasks` 创建爬虫任务
2. 系统异步执行爬取任务
3. 用户可以通过 `/api/crawler/tasks` 查询自己的任务列表
4. 用户可以通过 `/api/crawler/tasks/<task_id>` 查询特定任务的详情和输出文件
5. 如果任务配置了博客模板，系统会自动生成博客内容

## 使用示例

### curl 示例

```bash
# 创建爬虫任务
curl -X POST http://localhost:8000/api/crawler/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "url": "https://example.com/article",
    "use_xpath": true,
    "xpath_rule_id": "general_article",
    "blog_template": "default"
  }'

# 获取任务列表
curl -X GET http://localhost:8000/api/crawler/tasks \
  -H "Authorization: Bearer <access_token>"

# 获取任务详情
curl -X GET http://localhost:8000/api/crawler/tasks/task_20240101120000_1 \
  -H "Authorization: Bearer <access_token>"

# 获取可用博客模板
curl -X GET http://localhost:8000/api/crawler/templates \
  -H "Authorization: Bearer <access_token>"
```

### Python 示例

```python
import requests

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 创建爬虫任务
response = requests.post('http://localhost:8000/api/crawler/tasks',
                        headers=headers,
                        json={
                            'url': 'https://example.com/article',
                            'use_xpath': True,
                            'xpath_rule_id': 'general_article',
                            'blog_template': 'default'
                        })
data = response.json()
task_id = data['task_id']
print(f"任务创建成功，ID: {task_id}")

# 获取任务详情
response = requests.get(f'http://localhost:8000/api/crawler/tasks/{task_id}',
                       headers=headers)
task_info = response.json()
print(f"任务状态: {task_info['status']}")
print(f"输出文件数量: {len(task_info['output_files'])}")
```

## 注意事项

1. 爬虫任务是异步执行的，创建任务后需要通过任务ID查询状态
2. 使用XPath规则可以提高爬取精度，但需要提前创建或选择合适的规则
3. 博客模板功能需要用户组权限支持，不同用户组可以使用不同的模板
4. 使用Selenium可以处理动态加载的网页，但会增加爬取时间
5. 任务输出文件通常包括内容JSON和元数据JSON，可以通过任务详情API获取