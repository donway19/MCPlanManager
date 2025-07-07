# MCPlanManager - AI Agent 任务管理系统

[![PyPI version](https://img.shields.io/pypi/v/mcplanmanager.svg)](https://pypi.org/project/mcplanmanager/)
[![Docker Image Version](https://img.shields.io/docker/v/donway19/mcplanmanager/latest?label=docker)](https://hub.docker.com/r/donway19/mcplanmanager)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个简洁高效的任务管理器，专为 AI Agent 的长程任务执行而设计，支持MCP (Model Context Protocol) 标准，并同时支持 `uvx` 和 `Docker` 两种部署方式。

**版本 1.1.0 更新亮点:**
- 采用 `src` 目录结构，项目结构更清晰。
- **全面转向 SSE 传输模式**，优化了 Docker 部署的性能和实时性。
- **增加了完整的测试套件** (`test/`)，覆盖所有工具的功能和边界情况。
- 修复了 `editDependencies` 工具的参数 Bug 和 `generateContextPrompt` 的数据结构错误。
- 优化了所有工具的 Prompt 说明，提供了更清晰的用法和示例。

## 🚀 部署与使用

我们提供两种推荐的部署方式，请根据您的需求选择。

### 方式一：使用 `uvx` (轻量级 & 快速启动)

`uvx` 允许您以**一行命令**轻松启动 MCP 服务，它会自动处理依赖管理和环境设置。

1.  **先决条件：安装 uv**
    如果您的系统中还没有 `uv`，请先执行以下命令安装：
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **配置您的AI客户端**
    在 Cursor、Continue.dev 等客户端中，使用以下配置即可自动下载并运行服务（通过标准输入输出进行通信）：
    ```json
    {
      "mcpServers": {
        "mcplanmanager": {
          "command": "uvx",
          "args": ["mcplanmanager"]
        }
      }
    }
    ```

### 方式二：使用 `Docker` (生产环境 & 隔离部署)

Docker 提供了最佳的环境一致性和隔离性，是生产环境部署的首选方案。服务将以 **SSE (Server-Sent Events)** 模式运行。

1.  **拉取或构建镜像**
    从 Docker Hub 拉取最新镜像：
    ```bash
    docker pull donway19/mcplanmanager:latest
    ```
    或者在项目根目录本地构建：
    ```bash
    docker-compose build
    ```

2.  **运行容器**
    您可以通过 `docker run` 或 `docker-compose` 来启动服务。

    **使用 `docker run`:**
    ```bash
    docker run -d --name mcplanmanager_service -p 8080:8080 donway19/mcplanmanager:latest
    ```

    **使用 `docker-compose` (推荐):**
    项目根目录下的 `docker-compose.yml` 文件已为您配置好：
    ```yaml
    services:
      mcplanmanager:
        build: .
        container_name: mcplanmanager_service
        ports:
          - "8080:8080"
        restart: unless-stopped
    ```
    然后运行 `docker-compose up -d`。

3.  **配置您的AI客户端**
    使用以下配置通过 SSE 连接到 Docker 容器中运行的服务：
    ```json
    {
      "mcpServers": {
        "mcplanmanager-docker": {
          "transport": "sse",
          "url": "http://localhost:8080/sse"
        }
      }
    }
    ```
    **注意**：如果部署在云服务器上，请将 `localhost` 替换为服务器的公网 IP 或域名。

## 🧪 运行测试

我们提供了一套完整的测试套件来保证代码质量。

1.  **启动服务**
    确保您的 MCP 服务正在运行（通过 `uvx` 或 `Docker`）。

2.  **运行所有测试**
    在项目根目录执行以下命令：
    ```bash
    # 推荐使用 SSE 模式测试 Docker 部署
    python test/run_all_tests.py --mode sse

    # 或者使用 uvx 模式测试本地服务
    # python test/run_all_tests.py --mode uvx
    ```
    该脚本会自动运行所有功能测试和边界情况测试，并输出详细报告。

## 🛠️ MCP 工具列表

本项目提供以下13个工具：

*   **`initializePlan`**: 初始化新的任务计划
*   **`getCurrentTask`**: 获取当前正在执行的任务
*   **`startNextTask`**: 开始下一个可执行的任务
*   **`completeTask`**: 标记任务为完成状态
*   **`failTask`**: 标记任务失败
*   **`skipTask`**: 跳过指定任务
*   **`addTask`**: 添加新任务到计划中
*   **`getTaskList`**: 获取任务列表（支持状态过滤）
*   **`getExecutableTaskList`**: 获取当前可执行的任务列表
*   **`getPlanStatus`**: 获取整个计划的状态
*   **`editDependencies`**: 修改任务间的依赖关系
*   **`visualizeDependencies`**: 生成依赖关系可视化（支持`ascii`, `tree`, `mermaid`格式）
*   **`generateContextPrompt`**: 生成上下文提示词

## 🧑‍💻 本地开发

如果您希望贡献代码或进行二次开发，请遵循以下步骤：

1.  **克隆仓库并设置环境**
    ```bash
    git clone https://github.com/donway19/MCPlanManager.git
    cd MCPlanManager
    uv venv
    source .venv/bin/activate
    uv pip install -e .
    ```

2.  **在 Cursor 中进行本地调试**
    为了实现修改代码后实时生效的热重载调试，请在 Cursor 的 `mcp.server.configFiles` 设置中指向项目中的 `examples/mcp_configs/local_development.json` 文件。该文件已为您配置好了本地开发所需的环境变量。

    启动 Cursor 后，您就可以在聊天窗口中使用 `@mcplanmanager-local-dev` 来调用和测试您本地的最新代码了。

## 📄 许可证

本项目基于 MIT License - 详见 [LICENSE](LICENSE) 文件。