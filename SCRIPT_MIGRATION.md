# 启动脚本迁移说明

## 概述

原项目中有两个独立的脚本：
- `start.sh` - 用于启动Web应用
- `setup_and_run.sh` - 用于环境设置和测试

现在已合并为一个统一的脚本：`run.sh`

## 新脚本功能对比

### 原 start.sh 功能
```bash
# 原来的用法
./start.sh
```

### 原 setup_and_run.sh 功能
```bash
# 原来的用法
source ./setup_and_run.sh
source ./setup_and_run.sh --test
```

### 新 run.sh 统一功能
```bash
# 新的用法 - 替代原start.sh
./run.sh                    # 完整设置并启动应用

# 新的用法 - 替代原setup_and_run.sh
./run.sh --setup           # 仅设置环境
./run.sh --test             # 运行测试
```

## 功能特性

### 🚀 启动应用
```bash
./run.sh                    # 默认端口8001启动
./run.sh --port 9000        # 指定端口启动
./run.sh --dev              # 开发模式启动
```

### 🔧 环境设置
```bash
./run.sh --setup           # 仅设置环境，不启动应用
./run.sh --no-frontend      # 跳过前端构建
```

### 🧪 测试功能
```bash
./run.sh --test             # 运行所有测试
./run.sh --test tests/specific_test.py  # 运行特定测试
```

### 📋 帮助信息
```bash
./run.sh --help            # 显示帮助信息
```

## 迁移建议

### 立即迁移
1. 使用新的 `run.sh` 脚本替代原有脚本
2. 更新文档和CI/CD配置中的脚本调用
3. 团队成员更新本地开发流程

### 保留原脚本（可选）
如果需要保持向后兼容，可以将原脚本改为调用新脚本：

```bash
# start.sh 内容可改为：
#!/bin/bash
echo "注意：start.sh已弃用，请使用 ./run.sh"
./run.sh "$@"

# setup_and_run.sh 内容可改为：
#!/bin/bash
echo "注意：setup_and_run.sh已弃用，请使用 ./run.sh --setup"
./run.sh --setup "$@"
```

## 优势

1. **统一入口** - 一个脚本处理所有启动需求
2. **更好的参数支持** - 支持端口配置、开发模式等
3. **清晰的功能分离** - 通过参数明确指定操作类型
4. **更好的错误处理** - 统一的错误检查和提示
5. **简化维护** - 只需维护一个脚本文件

## 常见用法示例

```bash
# 开发环境快速启动
./run.sh --dev

# 生产环境启动（指定端口）
./run.sh --port 80

# CI/CD环境（仅测试）
./run.sh --test

# 容器环境（跳过前端构建）
./run.sh --no-frontend

# 首次设置环境
./run.sh --setup
```

## 注意事项

1. 新脚本不需要使用 `source` 命令运行
2. 虚拟环境管理已集成到脚本中
3. 前端构建会自动检测和执行
4. 所有依赖安装都通过 `uv` 管理