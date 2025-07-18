# 用户管理API文档

用户管理API提供用户信息查询、修改以及用户组管理功能。这些API大部分需要管理员权限。

## API端点

### 1. 获取所有用户列表

**GET** `/api/user/users`

获取系统中所有用户的列表（仅管理员可访问）。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_active": true,
      "group": "admin",
      "created_at": "2024-01-01T12:00:00Z",
      "last_login": "2024-01-02T10:30:00Z"
    },
    {
      "id": 2,
      "username": "user1",
      "email": "user1@example.com",
      "is_active": true,
      "group": "regular",
      "created_at": "2024-01-01T14:20:00Z",
      "last_login": "2024-01-02T09:15:00Z"
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
- 403: 权限不足（非管理员用户）

### 2. 获取指定用户信息

**GET** `/api/user/users/<user_id>`

获取指定用户的详细信息（仅管理员可访问）。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "group": {
    "id": 1,
    "name": "admin"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-02T10:30:00Z",
  "xpath_rules_count": 5
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
- 403: 权限不足（非管理员用户）
- 404: 用户不存在

### 3. 更新用户信息

**PUT** `/api/user/users/<user_id>`

更新指定用户的信息（仅管理员可访问）。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 请求参数

```json
{
  "email": "新邮箱", (可选)
  "is_active": true/false, (可选)
  "group_id": 用户组ID, (可选)
  "password": "新密码" (可选)
}
```

#### 响应

**成功** (200 OK)
```json
{
  "message": "用户信息更新成功"
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 邮箱已被其他用户使用
- 400: 用户组不存在
- 401: 未认证或令牌无效
- 403: 权限不足（非管理员用户）
- 404: 用户不存在

### 4. 获取所有用户组列表

**GET** `/api/user/groups`

获取系统中所有用户组的列表。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "groups": [
    {
      "id": 1,
      "name": "admin",
      "description": "管理员组",
      "max_xpath_rules": 100,
      "allowed_templates": ["template1", "template2", "template3"]
    },
    {
      "id": 2,
      "name": "regular",
      "description": "普通用户组",
      "max_xpath_rules": 10,
      "allowed_templates": ["template1"]
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

### 5. 创建新用户组

**POST** `/api/user/groups`

创建新的用户组（仅管理员可访问）。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 请求参数

```json
{
  "name": "用户组名称",
  "description": "用户组描述",
  "max_xpath_rules": 最大XPath规则数量,
  "allowed_templates": ["允许的模板列表"]
}
```

#### 响应

**成功** (201 Created)
```json
{
  "id": 3,
  "name": "premium",
  "message": "用户组创建成功"
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 缺少必要字段
- 400: 用户组名称已存在
- 401: 未认证或令牌无效
- 403: 权限不足（非管理员用户）

## 使用示例

### curl 示例

```bash
# 获取所有用户列表（管理员）
curl -X GET http://localhost:8000/api/user/users \
  -H "Authorization: Bearer <access_token>"

# 获取指定用户信息（管理员）
curl -X GET http://localhost:8000/api/user/users/1 \
  -H "Authorization: Bearer <access_token>"

# 更新用户信息（管理员）
curl -X PUT http://localhost:8000/api/user/users/2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "email": "newemail@example.com",
    "is_active": true,
    "group_id": 2
  }'

# 获取所有用户组
curl -X GET http://localhost:8000/api/user/groups \
  -H "Authorization: Bearer <access_token>"

# 创建新用户组（管理员）
curl -X POST http://localhost:8000/api/user/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "premium",
    "description": "高级用户组",
    "max_xpath_rules": 50,
    "allowed_templates": ["template1", "template2"]
  }'
```

### Python 示例

```python
import requests

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 获取所有用户列表（管理员）
response = requests.get('http://localhost:8000/api/user/users', headers=headers)
users = response.json()['users']
print(f"系统中共有 {len(users)} 个用户")

# 更新用户信息（管理员）
response = requests.put('http://localhost:8000/api/user/users/2',
                       headers=headers,
                       json={
                           'email': 'newemail@example.com',
                           'is_active': True,
                           'group_id': 2
                       })
print(response.json())

# 获取所有用户组
response = requests.get('http://localhost:8000/api/user/groups', headers=headers)
groups = response.json()['groups']
for group in groups:
    print(f"用户组: {group['name']}, 最大XPath规则数: {group['max_xpath_rules']}")
```

## 注意事项

1. 大部分用户管理API需要管理员权限
2. 更新用户信息时，只需提供要修改的字段
3. 创建用户组时，`max_xpath_rules` 和 `allowed_templates` 字段是必需的
4. 用户组一旦创建，目前没有提供删除或修改的API
5. 用户密码在更新时会重新进行哈希处理