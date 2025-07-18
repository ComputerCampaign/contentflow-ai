# 认证API文档

认证API提供用户注册、登录和获取当前用户信息的功能。

## API端点

### 1. 用户注册

**POST** `/api/auth/register`

创建新用户账户。

#### 请求参数

```json
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码",
  "group_id": 用户组ID (可选，默认为普通用户组)
}
```

#### 响应

**成功** (201 Created)
```json
{
  "message": "用户注册成功"
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
- 400: 用户名已存在
- 400: 邮箱已存在

### 2. 用户登录

**POST** `/api/auth/login`

用户登录并获取访问令牌。

#### 请求参数

```json
{
  "username": "用户名",
  "password": "密码"
}
```

#### 响应

**成功** (200 OK)
```json
{
  "access_token": "JWT令牌",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱",
    "group": "用户组名称"
  }
}
```

**错误**
```json
{
  "error": "错误描述"
}
```

可能的错误：
- 400: 缺少用户名或密码
- 401: 用户名或密码错误

### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的详细信息。

#### 请求头

```
Authorization: Bearer <access_token>
```

#### 响应

**成功** (200 OK)
```json
{
  "id": 1,
  "username": "用户名",
  "email": "邮箱",
  "group": {
    "id": 1,
    "name": "用户组名称",
    "max_xpath_rules": 10,
    "allowed_templates": ["模板1", "模板2"]
  },
  "xpath_rules_count": 3
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

## 认证流程

1. 用户通过 `/api/auth/register` 注册新账户
2. 用户通过 `/api/auth/login` 登录并获取访问令牌
3. 在后续请求中，将访问令牌添加到请求头中：`Authorization: Bearer <access_token>`
4. 访问令牌有效期内，用户可以访问需要认证的API

## 使用示例

### curl 示例

```bash
# 注册新用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 用户登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 获取当前用户信息
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Python 示例

```python
import requests

# 注册新用户
response = requests.post('http://localhost:8000/api/auth/register',
                        json={
                            'username': 'testuser',
                            'email': 'test@example.com',
                            'password': 'password123'
                        })
print(response.json())

# 用户登录
response = requests.post('http://localhost:8000/api/auth/login',
                        json={
                            'username': 'testuser',
                            'password': 'password123'
                        })
data = response.json()
token = data['access_token']

# 获取当前用户信息
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/auth/me', headers=headers)
user_info = response.json()
print(user_info)
```

## 注意事项

1. 访问令牌有效期默认为24小时
2. 请妥善保管访问令牌，不要泄露给第三方
3. 如需注销，客户端可以删除本地存储的访问令牌
4. 密码在服务器端使用哈希算法加密存储，无法恢复明文密码