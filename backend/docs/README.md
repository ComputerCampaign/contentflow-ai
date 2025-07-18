# API 文档

本目录包含了爬虫系统的完整API文档。

## 文档结构

- `auth.md` - 认证相关API
- `user.md` - 用户管理API
- `crawler.md` - 爬虫功能API
- `xpath.md` - XPath规则管理API
- `backdoor.md` - 后门API（无认证）
- `examples/` - API使用示例
- `schemas/` - 数据模型定义

## 快速开始

1. 查看 [认证文档](auth.md) 了解如何获取访问令牌
2. 查看 [爬虫API文档](crawler.md) 了解如何提交爬取任务
3. 查看 [后门API文档](backdoor.md) 了解无认证API的使用方法

## API基础信息

- **基础URL**: `http://localhost:8000/api`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 错误处理

所有API都遵循统一的错误响应格式：

```json
{
  "error": "错误描述",
  "code": "错误代码",
  "details": "详细错误信息（可选）"
}
```

## 状态码说明

- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误