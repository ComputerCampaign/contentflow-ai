# uv 依赖管理指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为Python包管理工具。uv是一个快速的Python包安装器和解析器，由Rust编写，可以替代传统的pip和virtualenv工具。

## 安装uv

如果您尚未安装uv，可以按照以下步骤安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 一步式环境设置（推荐）

使用uv sync可以一步完成虚拟环境创建和依赖安装：

```bash
uv sync
```

这个命令会：
1. 自动创建.venv虚拟环境（如果不存在）
2. 从pyproject.toml安装所有依赖
3. 同步依赖状态，确保环境与配置文件一致

## 激活虚拟环境

```bash
source .venv/bin/activate
```

## 其他常用命令

### 安装开发依赖

```bash
uv pip install -e ".[dev]"
```

### 添加新依赖

```bash
uv pip install package_name
```

### 更新依赖

```bash
uv pip install --upgrade .
```

### 查看已安装的包

```bash
uv pip list
```

### 卸载包

```bash
uv pip uninstall package_name
```

### 导出当前环境的依赖

```bash
uv pip freeze > requirements.txt
```

## uv与pip的区别

- uv比pip快10-100倍
- uv内置了虚拟环境管理功能
- uv使用Rust编写，内存安全且高效
- uv可以直接从pyproject.toml安装依赖
- uv支持并行下载和安装
- uv提供sync命令，一步完成环境设置

## 更多资源

- [uv官方文档](https://github.com/astral-sh/uv)
- [uv与pip比较](https://astral.sh/blog/uv)