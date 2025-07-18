# 后门API文档

后门API提供无需认证的爬虫功能，主要用于快速集成和测试。

## 配置

后门API的启用状态由配置文件控制：

```json
{
  "backdoor": {
    "enabled": true,
    "rate_limit": {
      "enabled": true,
      "requests_per_minute": 10,
      "requests_per_hour": 100
    },
    "allowed_ips": [],
    "log_requests": true
  }
}
```

## API端点

### 1. 提交爬取任务

**POST** `/api/backdoor/submit`

提交一个异步爬取任务。

#### 请求参数

```json
{
  "url": "https://example.com/article",
  "xpath_rule_id": "general_article",
  "output_format": "json",
  "include_images": true
}
```

#### 响应

```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "任务已提交，请使用task_id查询状态"
}
```

### 2. 快速爬取

**POST** `/api/backdoor/crawl`

同步执行爬取任务，立即返回结果。

#### 请求参数

```json
{
  "url": "https://example.com/article",
  "xpath_rule_id": "general_article",
  "include_images": true
}
```

#### 响应

```json
{
  "success": true,
  "data": {
    "title": "文章标题",
    "content": "文章内容",
    "images": ["image1.jpg", "image2.jpg"],
    "metadata": {
      "url": "https://example.com/article",
      "crawl_time": "2024-01-01T12:00:00Z"
    }
  },
  "message": "爬取完成"
}
```

### 3. 查询任务状态

**GET** `/api/backdoor/status/{task_id}`

查询异步任务的执行状态。

#### 响应

```json
{
  "success": true,
  "task_info": {
    "task_id": "uuid-string",
    "url": "https://example.com/article",
    "status": "completed",
    "created_at": "2024-01-01T12:00:00Z",
    "result": {
      "title": "文章标题",
      "content": "文章内容"
    },
    "error": null
  }
}
```

### 4. 健康检查

**GET** `/api/backdoor/health`

检查后门API的运行状态。

#### 响应

```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "backdoor_enabled": true
}
```

## 使用示例

### curl 示例

```bash
# 快速爬取
curl -X POST http://localhost:8000/api/backdoor/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "xpath_rule_id": "general_article",
    "include_images": true
  }'

# 提交异步任务
curl -X POST http://localhost:8000/api/backdoor/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "xpath_rule_id": "general_article"
  }'

# 查询任务状态
curl http://localhost:8000/api/backdoor/status/your-task-id

# 健康检查
curl http://localhost:8000/api/backdoor/health
```

### Python 示例

```python
import requests
import json

# 快速爬取
response = requests.post('http://localhost:8000/api/backdoor/crawl', 
                        json={
                            'url': 'https://example.com/article',
                            'xpath_rule_id': 'general_article',
                            'include_images': True
                        })

if response.status_code == 200:
    data = response.json()
    print(f"爬取成功: {data['data']['title']}")
else:
    print(f"爬取失败: {response.text}")
```

## 注意事项

1. **安全性**: 后门API绕过了认证机制，请谨慎启用
2. **限流**: 建议启用限流功能防止滥用
3. **日志**: 启用请求日志以便监控和调试
4. **IP限制**: 可配置允许访问的IP地址列表
5. **生产环境**: 生产环境中建议禁用后门API