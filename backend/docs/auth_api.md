# 用户认证API文档

## 概述

用户认证API提供用户注册、登录、身份验证和用户信息管理功能。所有API都基于JWT（JSON Web Token）进行身份验证。

**基础URL**: `http://localhost:5000/api/auth`

## 认证机制

- 使用JWT Token进行身份验证
- Token在登录成功后返回，有效期为24小时
- 需要认证的接口在请求头中包含：`Authorization: Bearer <token>`

## API接口

### 1. 用户注册

**接口**: `POST /register`

**描述**: 创建新用户账户

**请求参数**:
```json
{
  "username": "string",     // 用户名，3-50字符，唯一
  "email": "string",        // 邮箱地址，必须是有效邮箱格式，唯一
  "password": "string",     // 密码，最少6字符
  "display_name": "string"  // 显示名称，可选，最多100字符
}
```

**请求示例**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "display_name": "测试用户"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "用户注册成功",
  "data": {
    "user_id": "uuid-string",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "测试用户",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "用户名已存在",
  "error_code": "USERNAME_EXISTS"
}
```

**状态码**:
- `201`: 注册成功
- `400`: 请求参数错误
- `409`: 用户名或邮箱已存在
- `500`: 服务器内部错误

---

### 2. 用户登录

**接口**: `POST /login`

**描述**: 用户登录获取访问令牌

**请求参数**:
```json
{
  "username": "string",  // 用户名或邮箱
  "password": "string"   // 密码
}
```

**请求示例**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "user_id": "uuid-string",
      "username": "testuser",
      "email": "test@example.com",
      "display_name": "测试用户",
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "api_calls_today": 0,
      "api_calls_total": 0,
      "last_login": "2024-01-15T10:30:00Z"
    }
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "error_code": "INVALID_CREDENTIALS"
}
```

**状态码**:
- `200`: 登录成功
- `400`: 请求参数错误
- `401`: 用户名或密码错误
- `403`: 账户被禁用
- `500`: 服务器内部错误

---

### 3. 获取当前用户信息

**接口**: `GET /me`

**描述**: 获取当前登录用户的详细信息

**认证**: 需要Bearer Token

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-string",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "测试用户",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "api_calls_today": 15,
    "api_calls_total": 150,
    "last_api_call": "2024-01-15T10:25:00Z",
    "created_at": "2024-01-10T08:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T09:00:00Z"
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未授权（Token无效或过期）
- `500`: 服务器内部错误

---

### 4. 更新用户信息

**接口**: `PUT /me`

**描述**: 更新当前用户的基本信息

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "display_name": "string",  // 可选，显示名称
  "email": "string"          // 可选，邮箱地址
}
```

**请求示例**:
```json
{
  "display_name": "新的显示名称",
  "email": "newemail@example.com"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "用户信息更新成功",
  "data": {
    "user_id": "uuid-string",
    "username": "testuser",
    "email": "newemail@example.com",
    "display_name": "新的显示名称",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误
- `401`: 未授权
- `409`: 邮箱已被其他用户使用
- `500`: 服务器内部错误

---

### 5. 修改密码

**接口**: `PUT /password`

**描述**: 修改当前用户密码

**认证**: 需要Bearer Token

**请求参数**:
```json
{
  "current_password": "string",  // 当前密码
  "new_password": "string"       // 新密码，最少6字符
}
```

**请求示例**:
```json
{
  "current_password": "password123",
  "new_password": "newpassword456"
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "当前密码错误",
  "error_code": "INVALID_CURRENT_PASSWORD"
}
```

**状态码**:
- `200`: 修改成功
- `400`: 请求参数错误
- `401`: 未授权或当前密码错误
- `500`: 服务器内部错误

---

### 6. 刷新Token

**接口**: `POST /refresh`

**描述**: 刷新访问令牌（延长有效期）

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

**状态码**:
- `200`: 刷新成功
- `401`: 未授权（Token无效或过期）
- `500`: 服务器内部错误

---

### 7. 用户登出

**接口**: `POST /logout`

**描述**: 用户登出（使当前Token失效）

**认证**: 需要Bearer Token

**响应格式**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

**状态码**:
- `200`: 登出成功
- `401`: 未授权
- `500`: 服务器内部错误

---

## 错误代码说明

| 错误代码 | 描述 |
|---------|------|
| `VALIDATION_ERROR` | 请求参数验证失败 |
| `USERNAME_EXISTS` | 用户名已存在 |
| `EMAIL_EXISTS` | 邮箱已存在 |
| `INVALID_CREDENTIALS` | 用户名或密码错误 |
| `ACCOUNT_DISABLED` | 账户已被禁用 |
| `ACCOUNT_NOT_VERIFIED` | 账户未验证 |
| `INVALID_CURRENT_PASSWORD` | 当前密码错误 |
| `TOKEN_EXPIRED` | Token已过期 |
| `TOKEN_INVALID` | Token无效 |
| `RATE_LIMIT_EXCEEDED` | 请求频率超限 |
| `INTERNAL_ERROR` | 服务器内部错误 |

## 使用示例

### JavaScript/Fetch示例

```javascript
// 用户注册
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  return await response.json();
};

// 用户登录
const loginUser = async (credentials) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials)
  });
  const result = await response.json();
  
  if (result.success) {
    // 保存Token到localStorage
    localStorage.setItem('access_token', result.data.access_token);
  }
  
  return result;
};

// 获取用户信息
const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### Python/Requests示例

```python
import requests

# 用户登录
def login_user(username, password):
    response = requests.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    return response.json()

# 获取用户信息
def get_current_user(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/api/auth/me', headers=headers)
    return response.json()
```

## 安全注意事项

1. **密码安全**: 密码使用bcrypt进行哈希存储，不会明文保存
2. **Token安全**: JWT Token包含用户信息，请妥善保管，避免在不安全的环境中暴露
3. **HTTPS**: 生产环境中必须使用HTTPS协议
4. **频率限制**: API实施了频率限制，防止暴力破解攻击
5. **输入验证**: 所有输入都经过严格验证和清理

## 更新日志

- **v1.0.0** (2024-01-15): 初始版本，包含基础认证功能
- 支持用户注册、登录、信息管理
- JWT Token认证机制
- 完整的错误处理和状态码