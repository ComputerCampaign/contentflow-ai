# 任务管理API文档

## 概述

任务管理API提供任务的创建、查询、更新和状态管理功能。支持三种任务类型：爬虫任务（crawler）、内容生成任务（content_generation）和组合任务（combined）。任务创建后由Airflow调度系统自动执行。

**基础URL**: `http://localhost:5000/api/tasks`

**认证**: 所有接口都需要Bearer Token认证

## 任务类型说明

### 1. 爬虫任务（crawler）
- **用途**: 执行网页爬取操作
- **执行方式**: `uv run python -m crawler.crawler --url <url> [其他参数]`
- **必需配置**: 爬虫配置（CrawlerConfig）、目标URL
- **可选配置**: XPath配置（XPathConfig）

### 2. 内容生成任务（content_generation）
- **用途**: 基于爬虫数据生成AI内容
- **执行方式**: `python example.py <crawler_task_id>`
- **必需配置**: AI内容配置（AIContentConfig）、源爬虫任务ID
- **依赖关系**: 必须有已完成的爬虫任务作为数据源

### 3. 组合任务（combined）
- **用途**: 先执行爬虫，再执行内容生成
- **执行方式**: 按顺序执行爬虫和内容生成
- **必需配置**: 爬虫配置 + AI内容配置 + 目标URL
- **优势**: 一次性完成完整的数据获取和内容生成流程

## 任务状态

| 状态 | 描述 | 可转换状态 |
|------|------|----------|
| `pending` | 等待执行 | running, cancelled |
| `running` | 正在执行 | completed, failed, paused |
| `completed` | 执行完成 | - |
| `failed` | 执行失败 | pending（重新执行） |
| `cancelled` | 已取消 | pending（重新执行） |
| `paused` | 已暂停 | running, cancelled |

## API接口

### 1. 创建爬虫任务

**接口**: `POST /crawler`

**描述**: 创建新的爬虫任务

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "name": "string",                    // 必需，任务名称
  "description": "string",             // 可选，任务描述
  "url": "string",                     // 必需，目标URL
  "crawler_config_id": "string",       // 必需，爬虫配置ID
  "xpath_config_ids": ["string"],      // 可选，XPath配置ID列表
  "priority": integer,                 // 可选，优先级1-10，默认5
  "config": {                          // 可选，额外配置
    "custom_headers": {},
    "retry_on_failure": true
  }
}
```

**请求示例**:
```json
{
  "name": "Reddit Leicester 1954 爬虫任务",
  "description": "爬取Reddit上Leicester 1954的帖子内容",
  "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
  "crawler_config_id": "reddit-crawler-config-001",
  "xpath_config_ids": ["reddit_media", "reddit_comments", "reddit_post_title", "reddit_post_description"],
  "priority": 8
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "爬虫任务创建成功",
  "data": {
    "id": "task-crawler-001",
    "name": "Reddit Leicester 1954 爬虫任务",
    "description": "爬取Reddit上Leicester 1954的帖子内容",
    "type": "crawler",
    "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
    "status": "pending",
    "progress": 0,
    "priority": 8,
    "config": {
      "crawler_config_id": "reddit-crawler-config-001",
      "xpath_config_ids": ["reddit_media", "reddit_comments", "reddit_post_title", "reddit_post_description"]
    },
    "crawler_config_id": "reddit-crawler-config-001",
    "xpath_config_id": "reddit_media",
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "command_preview": "uv run python -m crawler.crawler --url \"https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/\" --data-dir ./crawler_data --use-selenium true --timeout 60 --retry 3 --headless false --enable-xpath true --rule-ids reddit_media,reddit_comments,reddit_post_title,reddit_post_description"
  }
}
```

**状态码**:
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 配置不存在
- `500`: 服务器内部错误

---

### 2. 创建内容生成任务

**接口**: `POST /content-generation`

**描述**: 创建新的内容生成任务

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "name": "string",                    // 必需，任务名称
  "description": "string",             // 可选，任务描述
  "source_task_id": "string",          // 必需，源爬虫任务ID
  "ai_content_config_id": "string",    // 必需，AI内容配置ID
  "priority": integer,                 // 可选，优先级1-10，默认5
  "config": {                          // 可选，额外配置
    "custom_prompt": "string",
    "output_format": "markdown"
  }
}
```

**请求示例**:
```json
{
  "name": "Leicester 1954 内容生成任务",
  "description": "基于爬虫数据生成关于Leicester 1954的博客文章",
  "source_task_id": "task-crawler-001",
  "ai_content_config_id": "ai-content-config-001",
  "priority": 6
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "内容生成任务创建成功",
  "data": {
    "id": "task-content-gen-001",
    "name": "Leicester 1954 内容生成任务",
    "description": "基于爬虫数据生成关于Leicester 1954的博客文章",
    "type": "content_generation",
    "source_task_id": "task-crawler-001",
    "crawler_task_id": "task-crawler-001",
    "status": "pending",
    "progress": 0,
    "priority": 6,
    "config": {
      "ai_content_config_id": "ai-content-config-001",
      "source_task_id": "task-crawler-001"
    },
    "ai_content_config_id": "ai-content-config-001",
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "command_preview": "python example.py task-crawler-001"
  }
}
```

**状态码**:
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 配置或源任务不存在
- `409`: 源任务未完成
- `500`: 服务器内部错误

---

### 3. 创建组合任务

**接口**: `POST /combined`

**描述**: 创建新的组合任务（爬虫+内容生成）

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "name": "string",                    // 必需，任务名称
  "description": "string",             // 可选，任务描述
  "url": "string",                     // 必需，目标URL
  "crawler_config_id": "string",       // 必需，爬虫配置ID
  "ai_content_config_id": "string",    // 必需，AI内容配置ID
  "xpath_config_ids": ["string"],      // 可选，XPath配置ID列表
  "priority": integer,                 // 可选，优先级1-10，默认5
  "config": {                          // 可选，额外配置
    "crawler_config": {},
    "ai_config": {}
  }
}
```

**请求示例**:
```json
{
  "name": "Reddit内容爬取+生成组合任务",
  "description": "先爬取Reddit内容，然后生成博客文章",
  "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
  "crawler_config_id": "reddit-crawler-config-001",
  "ai_content_config_id": "ai-content-config-001",
  "xpath_config_ids": ["reddit_media", "reddit_comments", "reddit_post_title", "reddit_post_description"],
  "priority": 9
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "组合任务创建成功",
  "data": {
    "id": "task-combined-001",
    "name": "Reddit内容爬取+生成组合任务",
    "description": "先爬取Reddit内容，然后生成博客文章",
    "type": "combined",
    "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
    "status": "pending",
    "progress": 0,
    "priority": 9,
    "config": {
      "crawler_config_id": "reddit-crawler-config-001",
      "ai_content_config_id": "ai-content-config-001",
      "xpath_config_ids": ["reddit_media", "reddit_comments", "reddit_post_title", "reddit_post_description"]
    },
    "crawler_config_id": "reddit-crawler-config-001",
    "ai_content_config_id": "ai-content-config-001",
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:40:00Z",
    "updated_at": "2024-01-15T10:40:00Z",
    "execution_plan": [
      {
        "step": 1,
        "type": "crawler",
        "command": "uv run python -m crawler.crawler --url \"https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/\" --data-dir ./crawler_data --use-selenium true --timeout 60 --retry 3 --headless false --enable-xpath true --rule-ids reddit_media,reddit_comments,reddit_post_title,reddit_post_description"
      },
      {
        "step": 2,
        "type": "content_generation",
        "command": "python example.py <crawler_task_id>"
      }
    ]
  }
}
```

**状态码**:
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 配置不存在
- `500`: 服务器内部错误

---

### 4. 获取任务列表

**接口**: `GET /`

**描述**: 获取当前用户的任务列表，支持分页和过滤

**认证**: 需要Bearer Token

**查询参数**:
- `page`: 页码，默认1
- `per_page`: 每页数量，默认10，最大100
- `type`: 过滤任务类型，crawler/content_generation/combined
- `status`: 过滤任务状态，pending/running/completed/failed/cancelled/paused
- `priority`: 过滤优先级，1-10
- `search`: 搜索关键词，在名称和描述中搜索
- `sort`: 排序字段，created_at/updated_at/priority/name
- `order`: 排序方向，asc/desc，默认desc

**请求示例**:
```
GET /api/tasks?page=1&per_page=10&type=crawler&status=pending&sort=priority&order=desc
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "task-crawler-001",
        "name": "Reddit Leicester 1954 爬虫任务",
        "description": "爬取Reddit上Leicester 1954的帖子内容",
        "type": "crawler",
        "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
        "status": "pending",
        "progress": 0,
        "priority": 8,
        "total_executions": 0,
        "last_run": null,
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
    },
    "statistics": {
      "total_tasks": 1,
      "by_status": {
        "pending": 1,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
        "paused": 0
      },
      "by_type": {
        "crawler": 1,
        "content_generation": 0,
        "combined": 0
      }
    }
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `500`: 服务器内部错误

---

### 5. 获取单个任务详情

**接口**: `GET /{task_id}`

**描述**: 获取指定ID的任务详情

**认证**: 需要Bearer Token

**路径参数**:
- `task_id`: 任务ID

**响应格式**:
```json
{
  "success": true,
  "data": {
    "id": "task-crawler-001",
    "name": "Reddit Leicester 1954 爬虫任务",
    "description": "爬取Reddit上Leicester 1954的帖子内容",
    "type": "crawler",
    "url": "https://www.reddit.com/r/UrbanHell/comments/1mgqbmr/leicester_england_1954/",
    "status": "pending",
    "progress": 0,
    "priority": 8,
    "config": {
      "crawler_config_id": "reddit-crawler-config-001",
      "xpath_config_ids": ["reddit_media", "reddit_comments", "reddit_post_title", "reddit_post_description"]
    },
    "total_executions": 0,
    "last_run": null,
    "crawler_config_id": "reddit-crawler-config-001",
    "xpath_config_id": "reddit_media",
    "user_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "related_configs": {
      "crawler_config": {
        "id": "reddit-crawler-config-001",
        "name": "Reddit爬虫配置",
        "use_selenium": true,
        "timeout": 60
      },
      "xpath_configs": [
        {
          "rule_id": "reddit_media",
          "name": "Reddit媒体图片",
          "rule_type": "image"
        }
      ]
    }
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权
- `404`: 任务不存在
- `500`: 服务器内部错误

---

### 6. 更新任务状态

**接口**: `PUT /{task_id}/status`

**描述**: 更新任务状态（主要供Airflow调用）

**认证**: 需要Bearer Token或API Key

**路径参数**:
- `task_id`: 任务ID

**请求参数**:
```json
{
  "status": "string",                  // 必需，新状态
  "progress": integer,                 // 可选，进度0-100
  "dag_run_id": "string",              // 可选，Airflow DAG运行ID
  "error_message": "string",           // 可选，错误信息（失败时）
  "result": {},                        // 可选，执行结果
  "execution_info": {                  // 可选，执行信息
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:35:00Z",
    "duration": 300,
    "items_processed": 10
  }
}
```

**请求示例**:
```json
{
  "status": "running",
  "progress": 50,
  "dag_run_id": "crawler_dag_2024-01-15T10:30:00"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "任务状态更新成功",
  "data": {
    "id": "task-crawler-001",
    "status": "running",
    "progress": 50,
    "updated_at": "2024-01-15T10:32:00Z",
    "last_run": "2024-01-15T10:30:00Z",
    "total_executions": 1
  }
}
```

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误或状态转换无效
- `401`: 未授权
- `404`: 任务不存在
- `500`: 服务器内部错误

---

### 7. 获取任务执行历史

**接口**: `GET /{task_id}/executions`

**描述**: 获取任务的执行历史记录

**认证**: 需要Bearer Token

**路径参数**:
- `task_id`: 任务ID

**查询参数**:
- `page`: 页码，默认1
- `per_page`: 每页数量，默认10
- `status`: 过滤执行状态

**响应格式**:
```json
{
  "success": true,
  "data": {
    "executions": [
      {
        "id": "execution-001",
        "dag_run_id": "crawler_dag_2024-01-15T10:30:00",
        "status": "success",
        "start_time": "2024-01-15T10:30:00Z",
        "end_time": "2024-01-15T10:35:00Z",
        "duration": 300,
        "items_processed": 10,
        "items_success": 10,
        "items_failed": 0,
        "result": {
          "extracted_data_count": 10,
          "images_downloaded": 5
        },
        "error_message": null,
        "created_at": "2024-01-15T10:30:00Z"
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
- `404`: 任务不存在
- `500`: 服务器内部错误

---

### 8. 取消任务

**接口**: `POST /{task_id}/cancel`

**描述**: 取消待执行或正在执行的任务

**认证**: 需要Bearer Token

**路径参数**:
- `task_id`: 任务ID

**请求参数**:
```json
{
  "reason": "string"  // 可选，取消原因
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "任务取消成功",
  "data": {
    "id": "task-crawler-001",
    "status": "cancelled",
    "updated_at": "2024-01-15T10:45:00Z"
  }
}
```

**状态码**:
- `200`: 取消成功
- `400`: 任务状态不允许取消
- `401`: 未授权
- `404`: 任务不存在
- `500`: 服务器内部错误

---

### 9. 重新执行任务

**接口**: `POST /{task_id}/retry`

**描述**: 重新执行失败或取消的任务

**认证**: 需要Bearer Token

**路径参数**:
- `task_id`: 任务ID

**请求参数**:
```json
{
  "reset_config": boolean,  // 可选，是否重置配置，默认false
  "priority": integer       // 可选，新的优先级
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "任务重新执行成功",
  "data": {
    "id": "task-crawler-001",
    "status": "pending",
    "progress": 0,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**状态码**:
- `200`: 重新执行成功
- `400`: 任务状态不允许重新执行
- `401`: 未授权
- `404`: 任务不存在
- `500`: 服务器内部错误

---

### 10. 删除任务

**接口**: `DELETE /{task_id}`

**描述**: 删除任务（仅限已完成、失败或取消的任务）

**认证**: 需要Bearer Token

**路径参数**:
- `task_id`: 任务ID

**响应格式**:
```json
{
  "success": true,
  "message": "任务删除成功"
}
```

**状态码**:
- `200`: 删除成功
- `400`: 任务状态不允许删除
- `401`: 未授权
- `404`: 任务不存在
- `500`: 服务器内部错误

---

## 使用示例

### JavaScript示例

```javascript
// 创建爬虫任务
const createCrawlerTask = async (taskData, token) => {
  const response = await fetch('/api/tasks/crawler', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(taskData)
  });
  return await response.json();
};

// 创建内容生成任务
const createContentGenerationTask = async (taskData, token) => {
  const response = await fetch('/api/tasks/content-generation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(taskData)
  });
  return await response.json();
};

// 获取任务列表
const getTasks = async (token, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const response = await fetch(`/api/tasks?${queryString}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 更新任务状态
const updateTaskStatus = async (taskId, statusData, token) => {
  const response = await fetch(`/api/tasks/${taskId}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(statusData)
  });
  return await response.json();
};

// 取消任务
const cancelTask = async (taskId, reason, token) => {
  const response = await fetch(`/api/tasks/${taskId}/cancel`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ reason })
  });
  return await response.json();
};
```

### Python示例

```python
import requests

def create_crawler_task(task_data, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post('/api/tasks/crawler', json=task_data, headers=headers)
    return response.json()

def create_combined_task(task_data, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post('/api/tasks/combined', json=task_data, headers=headers)
    return response.json()

def get_tasks(token, **params):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/api/tasks', params=params, headers=headers)
    return response.json()

def update_task_status(task_id, status_data, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.put(f'/api/tasks/{task_id}/status', 
                          json=status_data, headers=headers)
    return response.json()

def get_task_executions(task_id, token, **params):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'/api/tasks/{task_id}/executions', 
                          params=params, headers=headers)
    return response.json()
```

## Airflow集成说明

### 任务调度流程

1. **任务发现**: Airflow定期查询数据库中状态为`pending`的任务
2. **任务执行**: 根据任务类型执行相应的命令
3. **状态更新**: 通过API更新任务状态和进度
4. **结果记录**: 将执行结果记录到TaskExecution表

### Airflow DAG示例

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def update_task_status(task_id, status, **context):
    # 调用API更新任务状态
    import requests
    response = requests.put(f'/api/tasks/{task_id}/status', 
                          json={'status': status})
    return response.json()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'crawler_content_generation',
    default_args=default_args,
    description='爬虫和内容生成任务调度',
    schedule_interval=timedelta(minutes=5),
    catchup=False
)

# 爬虫任务
crawler_task = BashOperator(
    task_id='run_crawler',
    bash_command='uv run python -m crawler.crawler --url "{{ params.url }}" --rule-ids "{{ params.rule_ids }}" --data-dir ./crawler_data',
    dag=dag
)

# 内容生成任务
content_gen_task = BashOperator(
    task_id='run_content_generation',
    bash_command='python example.py {{ params.crawler_task_id }}',
    dag=dag
)

# 状态更新任务
status_update = PythonOperator(
    task_id='update_status',
    python_callable=update_task_status,
    op_kwargs={'task_id': '{{ params.task_id }}', 'status': 'completed'},
    dag=dag
)

crawler_task >> content_gen_task >> status_update
```

## 最佳实践

1. **任务命名**: 使用描述性的任务名称，包含目标网站和用途
2. **优先级设置**: 重要任务设置高优先级（8-10），常规任务使用默认优先级（5）
3. **配置管理**: 创建任务前确保相关配置已正确设置并测试
4. **错误处理**: 合理设置重试次数，避免无限重试
5. **资源管理**: 监控任务执行情况，避免资源过度占用
6. **依赖关系**: 内容生成任务确保源爬虫任务已完成
7. **状态监控**: 定期检查任务状态，及时处理失败任务

## 错误处理

常见错误代码：
- `INVALID_TASK_TYPE`: 无效的任务类型
- `CONFIG_NOT_FOUND`: 配置不存在
- `SOURCE_TASK_NOT_FOUND`: 源任务不存在
- `SOURCE_TASK_NOT_COMPLETED`: 源任务未完成
- `INVALID_STATUS_TRANSITION`: 无效的状态转换
- `TASK_IN_PROGRESS`: 任务正在执行中
- `INVALID_URL`: URL格式不正确
- `XPATH_SYNC_FAILED`: XPath同步失败

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本
  - 支持三种任务类型：crawler、content_generation、combined
  - 完整的任务生命周期管理
  - Airflow集成支持
  - 任务执行历史记录
  - 状态转换和进度跟踪