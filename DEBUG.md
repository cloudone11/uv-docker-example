# Docker 调试指南

本文档介绍如何在 Docker 容器中调试 FastAPI 应用程序，包括远程调试和热重载功能。

## 概述

项目已配置支持：
- **远程调试**：使用 debugpy 在端口 5678 上监听调试连接
- **热重载**：FastAPI 开发模式自动检测代码变化并重新加载
- **VSCode 集成**：配置了远程调试启动配置

## 快速开始

### 1. 启动调试模式

```bash
./run.sh
```

或者 `ctrl + shift + b` 快速启动默认任务 

这将：
- 构建 Docker 镜像
- 启动容器并运行 FastAPI 应用
- 启动 debugpy 调试服务器（等待客户端连接）
- 启用 FastAPI 热重载功能

### 2. 连接调试器

在 VSCode 中：
1. 打开项目文件夹
2. 按 `F5` 或选择"运行 > 开始调试"
3. 选择"Python 调试程序: 远程附加"配置
4. 调试器将连接到容器中的 debugpy 服务器

### 3. 访问应用

- **应用地址**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **调试端口**：5678（用于调试器连接）

## 详细配置

### run.sh 脚本

```bash
docker run \
    --rm \
    --volume .:/app \
    --volume /app/.venv \
    --publish 8000:8000 \
    --publish 5678:5678 \
    --env DEBUGPY_ALLOW_UNSAFE=true \
    $INTERACTIVE \
    $(docker build -q .) \
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m fastapi dev --host 0.0.0.0 src/uv_docker_example \
    "$@"
```

**关键参数说明**：
- `--publish 8000:8000`：映射 FastAPI 应用端口
- `--publish 5678:5678`：映射调试器端口
- `--env DEBUGPY_ALLOW_UNSAFE=true`：允许调试器在容器中运行
- `python -m debugpy --listen 0.0.0.0:5678 --wait-for-client`：启动调试服务器并等待连接
- `-m fastapi dev --host 0.0.0.0`：启动 FastAPI 开发模式

### VSCode 调试配置

`.vscode/launch.json`：
```json
{
  "configurations": [
    {
      "name": "Python 调试程序: 远程附加",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "."
        }
      ]
    }
  ]
}
```

## 调试功能

### 设置断点

1. 在 VSCode 中打开 Python 文件
2. 在代码行号左侧点击设置断点（红点）
3. 连接调试器后，执行到断点时会暂停

### 变量检查

- 在断点处暂停时，可以在"变量"面板查看局部和全局变量
- 可以在"调试控制台"中执行 Python 代码检查变量状态

### 热重载

修改代码后：
1. 保存文件（Ctrl+S）
2. FastAPI 会自动检测变化并重新加载
3. 调试器会重新连接到新的进程
4. 断点会保留（可能需要重新触发）

## 常见问题

### 1. 调试器连接失败

**症状**：VSCode 显示"无法连接到调试器"

**解决方案**：
- 确保容器正在运行：`docker ps`
- 检查端口映射：`docker ps` 应显示 `0.0.0.0:5678->5678/tcp`
- 确认 VSCode 调试配置中的端口是 5678

### 2. 断点不触发

**症状**：设置了断点但程序没有暂停

**解决方案**：
- 确保调试器已连接（VSCode 状态栏显示调试图标）
- 检查代码是否确实被执行到
- 尝试在入口点设置断点测试连接

### 3. 热重载后调试器断开

**症状**：修改代码后调试器连接丢失

**解决方案**：
- 这是正常现象，重新连接调试器即可
- 或者停止容器重新启动：`Ctrl+C` 然后 `./run.sh`

### 4. 冻结模块警告

**症状**：控制台显示关于冻结模块的警告

**解决方案**：
- 这是警告信息，不影响调试功能
- 如需消除，可以在启动命令中添加 `-Xfrozen_modules=off` 参数

## 高级用法

### 自定义启动参数

可以通过传递参数覆盖默认命令：

```bash
# 仅启动 FastAPI（无调试）
./run.sh fastapi dev --host 0.0.0.0 src/uv_docker_example

# 启动 Python 交互式 shell
./run.sh python

# 运行测试
./run.sh python -m pytest
```

### 调试多进程应用

如果应用使用多进程，需要在调试器启动时添加相应参数（当前配置已优化）。

### 生产环境调试

生产环境建议：
- 使用 `fastapi run` 而不是 `fastapi dev`
- 禁用调试器或仅在需要时启用
- 使用适当的日志级别

## 项目依赖

确保 `pyproject.toml` 包含必要依赖：

```toml
dependencies = [
    "debugpy>=1.8.17",
    "fastapi[standard]>=0.112.2",
]
```

## 总结

通过以上配置，您可以：
- 在 Docker 容器中运行 FastAPI 应用
- 使用 VSCode 进行远程调试
- 享受热重载带来的开发便利
- 保持代码和容器环境的同步

如有问题，请检查容器日志：`docker logs <container_id>`
