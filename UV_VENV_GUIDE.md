# uv 虚拟环境简明指南

本指南简要介绍如何使用 uv 创建和管理 Python 虚拟环境。uv 是一个由 Rust 编写的快速 Python 包管理工具，可以替代传统的 virtualenv 和 pip。

## 基础知识

### 什么是虚拟环境？

虚拟环境是一个独立的 Python 环境，它允许您为不同的项目安装不同版本的包，而不会相互干扰。这对于管理项目依赖非常重要，特别是当不同项目需要不同版本的同一个包时。

### uv 虚拟环境的优势

- **速度快**：uv 创建虚拟环境比传统工具快 10-100 倍
- **简单**：单一命令即可创建和管理虚拟环境
- **兼容性**：与现有的 virtualenv 和 venv 格式兼容
- **轻量级**：最小化依赖，减少出错可能

## 安装 uv

在使用 uv 创建虚拟环境前，您需要先安装 uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 一步式环境设置（推荐）

使用 uv sync 可以一步完成虚拟环境创建和依赖安装：

```bash
uv sync
```

这个命令会：
1. 自动创建 .venv 虚拟环境（如果不存在）
2. 从 pyproject.toml 安装所有依赖
3. 同步依赖状态，确保环境与配置文件一致

## 基本虚拟环境操作

### 手动创建虚拟环境

```bash
uv venv
```

### 激活虚拟环境

```bash
source .venv/bin/activate
```

### 退出虚拟环境

```bash
deactivate
```

### 删除虚拟环境

```bash
rm -rf .venv
```

## 在虚拟环境中安装包

激活虚拟环境后，您可以使用 uv 安装包：

```bash
uv pip install package_name
```

## 最佳实践

1. **为每个项目创建单独的虚拟环境**：避免依赖冲突
2. **使用版本控制忽略虚拟环境目录**：在 .gitignore 中添加 `.venv/`
3. **记录项目依赖**：使用 pyproject.toml 或 requirements.txt
4. **使用 uv sync 简化环境设置**：一步完成环境创建和依赖安装
5. **定期更新依赖**：使用 `uv pip install --upgrade`

## 更多资源

- [uv 官方文档](https://github.com/astral-sh/uv)
- [uv 虚拟环境命令参考](https://github.com/astral-sh/uv/blob/main/docs/venv.md)
- [Python 虚拟环境最佳实践](https://docs.python.org/3/tutorial/venv.html)