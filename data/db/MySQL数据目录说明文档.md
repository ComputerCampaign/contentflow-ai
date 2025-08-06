# MySQL 数据目录文件详解

本文档详细说明了 MySQL 容器挂载目录 `/data/db/mysql` 中各个文件和目录的含义与作用。

## 📋 目录概览

```
data/db/mysql/
├── 业务数据库目录/
├── 系统数据库目录/
├── InnoDB存储引擎文件/
├── 事务日志文件/
├── 二进制日志文件/
├── SSL证书文件/
└── 配置和状态文件/
```

## 🗂️ 核心数据库目录

### 业务数据库

| 目录名 | 说明 | 重要性 |
|--------|------|--------|
| `crawler_airflow_db/` | Airflow业务数据库目录 | 🔴 关键 |
| `crawler_db/` | 主要业务数据库目录 | 🔴 关键 |

### 系统数据库

| 目录名 | 说明 | 重要性 |
|--------|------|--------|
| `mysql/` | MySQL系统数据库，存储用户账户、权限、日志配置等 | 🔴 关键 |
| `performance_schema/` | 性能监控数据库，包含各种性能统计信息 | 🟢 可重建 |
| `sys/` | 系统视图数据库，提供易于理解的性能数据视图 | 🟢 可重建 |

## 📁 InnoDB 存储引擎文件

### 数据文件

| 文件名 | 说明 | 重要性 |
|--------|------|--------|
| `ibdata1` | InnoDB共享表空间文件，存储数据字典、undo日志等 | 🔴 关键 |
| `mysql.ibd` | mysql系统数据库的独立表空间文件 | 🔴 关键 |
| `ibtmp1` | InnoDB临时表空间文件 | 🟢 可重建 |

### 事务日志

#### 重做日志 (Redo Log)
- **目录**: `#innodb_redo/`
- **文件**: `#ib_redo9` 到 `#ib_redo40_tmp`
- **作用**: 用于崩溃恢复，确保事务的持久性
- **重要性**: 🔴 关键

#### 撤销日志 (Undo Log)
- **文件**: `undo_001`, `undo_002`
- **作用**: 支持事务回滚和MVCC（多版本并发控制）
- **重要性**: 🔴 关键

### 临时文件

- **目录**: `#innodb_temp/`
- **文件**: `temp_1.ibt` 到 `temp_10.ibt`
- **作用**: 临时表空间文件，用于临时表和排序操作
- **重要性**: 🟢 可重建

### 双写缓冲 (Doublewrite Buffer)

- **文件**: `#ib_16384_0.dblwr`, `#ib_16384_1.dblwr`
- **作用**: 防止页面损坏，提供数据完整性保护
- **重要性**: 🟡 重要

## 📝 二进制日志 (Binary Log)

| 文件名 | 说明 | 重要性 |
|--------|------|--------|
| `binlog.000001`, `binlog.000002` | 二进制日志文件，记录数据变更 | 🟡 重要 |
| `binlog.index` | 二进制日志索引文件 | 🟡 重要 |

**作用**:
- 主从复制
- 数据恢复
- 增量备份

## 🔐 SSL证书文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `ca.pem`, `ca-key.pem` | 证书颁发机构证书和私钥 | SSL连接验证 |
| `server-cert.pem`, `server-key.pem` | 服务器证书和私钥 | 服务器身份验证 |
| `client-cert.pem`, `client-key.pem` | 客户端证书和私钥 | 客户端身份验证 |
| `private_key.pem`, `public_key.pem` | RSA私钥和公钥 | 加密通信 |

## ⚙️ 配置和状态文件

| 文件名 | 说明 | 重要性 |
|--------|------|--------|
| `auto.cnf` | 自动生成的配置文件，包含server-uuid | 🟡 重要 |
| `ib_buffer_pool` | InnoDB缓冲池转储文件，用于快速预热 | 🟢 可重建 |

## 📊 性能监控文件

`performance_schema/` 目录中的 `.sdi` 文件是序列化字典信息文件，包含：

### 事件统计
- `events_stages_*` - 阶段事件统计
- `events_statement_*` - 语句事件统计
- `events_transacti_*` - 事务事件统计
- `events_waits_*` - 等待事件统计

### 资源统计
- `memory_summary_*` - 内存使用统计
- `file_summary_*` - 文件I/O统计
- `socket_summary_*` - 网络连接统计
- `table_io_waits_*` - 表I/O等待统计

### 连接和用户统计
- `hosts_*` - 主机连接统计
- `users_*` - 用户连接统计
- `accounts_*` - 账户统计
- `session_*` - 会话统计

### 复制统计
- `replication_*` - 主从复制相关统计

## 🔍 文件重要性分级

### 🔴 关键文件（丢失会导致数据库无法启动）
- `ibdata1` - 共享表空间
- `mysql.ibd` - 系统数据库表空间
- `undo_001`, `undo_002` - 撤销日志
- 业务数据库目录 `crawler_airflow_db/`, `crawler_db/`
- `#innodb_redo/` 目录 - 重做日志
- `mysql/` 目录 - 系统数据库

### 🟡 重要文件（丢失会影响功能）
- `binlog.*` - 影响主从复制和数据恢复
- SSL证书文件 - 影响安全连接
- `auto.cnf` - 服务器配置
- `#ib_16384_*.dblwr` - 双写缓冲

### 🟢 可重建文件（可以重新生成）
- `#innodb_temp/`, `ibtmp1` - 临时文件
- `ib_buffer_pool` - 缓冲池转储
- `performance_schema/` - 性能统计数据
- `sys/` - 系统视图数据

## 💡 维护建议

### 备份策略
1. **完整备份**: 定期备份整个 `mysql/` 目录
2. **增量备份**: 备份二进制日志文件
3. **关键文件**: 重点保护 🔴 关键文件

### 监控要点
1. **磁盘空间**: 监控数据目录磁盘使用情况
2. **日志文件**: 定期清理过期的二进制日志
3. **临时文件**: 监控临时文件大小，防止磁盘空间耗尽

### 故障恢复
1. **数据损坏**: 利用重做日志和撤销日志进行恢复
2. **主从同步**: 使用二进制日志重建从库
3. **性能问题**: 分析 `performance_schema` 中的统计数据

## 📚 相关配置

### Docker Compose 配置
```yaml
volumes:
  - ../../data/dev/mysql:/var/lib/mysql  # 数据持久化
  - ./mysql-init:/docker-entrypoint-initdb.d  # 初始化脚本
```

### 环境变量配置
```bash
MYSQL_ROOT_PASSWORD=root_password_123!
MYSQL_DATABASE=crawler_platform
MYSQL_USER=crawler_user
MYSQL_PASSWORD=crawler_user_Pwd123!
```

---

**文档版本**: v1.0  
**创建时间**: 2025年  
**适用版本**: MySQL 8.0+  
**维护者**: 爬虫平台开发团队  

> 💡 **提示**: 本文档基于实际运行的MySQL容器数据目录结构生成，如有疑问请参考MySQL官方文档或联系开发团队。