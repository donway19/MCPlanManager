# MCPlanManager - AI Agent 任务管理系统

一个简洁高效的任务管理器，专为 AI Agent 的长程任务执行而设计，支持MCP (Model Context Protocol) 标准。

## 🚀 快速开始 (推荐方式)

我们强烈推荐使用 `uvx` 来运行 MCPlanManager。`uvx` 允许您以**一行命令**轻松启动 MCP 服务，它会自动处理依赖管理和环境设置，确保您始终使用最新版本且避免复杂的依赖冲突。这种模式也为**无缝部署到各种托管平台**提供了基础。

### 1. 先决条件：安装 uv

如果您的系统中还没有 `uv`，请先执行以下命令安装（这只需要做一次）：

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
安装完成后，请重启您的终端或打开一个新的终端窗口。

### 2. 配置您的AI客户端

在Cursor、Continue.dev等支持MCP的客户端设置中，添加一个新的MCP服务器，并使用以下配置：

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
重启客户端后，`MCPlanManager` 的工具即可使用。**无需手动安装依赖或配置Python环境！** `uvx` 会智能地从PyPI下载并运行服务。对于支持 `uvx` 的托管平台，只需配置其启动命令为 `uvx mcplanmanager`，即可实现**自动化部署和弹性伸缩**。

## 📚 备用方案：使用虚拟环境和pip

如果您不想安装 `uv`，也可以使用传统的Python虚拟环境。

1.  **创建并激活虚拟环境**
    ```bash
    python3 -m venv ~/.mcplanmanager-env
    source ~/.mcplanmanager-env/bin/activate  # macOS / Linux
    # .\mcplanmanager-env\Scripts\activate # Windows
    ```
2.  **安装包**
    ```bash
    pip install mcplanmanager
    ```
3.  **配置AI客户端**
    您需要告诉客户端 `mcplanmanager` 命令的具体路径。
    ```json
    {
      "mcpServers": {
        "mcplanmanager": {
          // 注意：这里的路径需要是您虚拟环境中的绝对路径
          // 例如: "/Users/yourname/.mcplanmanager-env/bin/mcplanmanager"
          "command": "<path_to_your_env>/bin/mcplanmanager"
        }
      }
    }
    ```

## 🛠️ 可用的MCP工具

安装配置成功后，您可以使用以下12个工具：

### 基础任务管理
- **`initializePlan`** - 初始化新的任务计划
- **`getCurrentTask`** - 获取当前正在执行的任务
- **`startNextTask`** - 开始下一个可执行的任务
- **`completeTask`** - 标记任务为完成状态
- **`failTask`** - 标记任务失败
- **`skipTask`** - 跳过指定任务

### 任务操作
- **`addTask`** - 添加新任务到计划中
- **`getTaskList`** - 获取任务列表（支持状态过滤）
- **`getExecutableTaskList`** - 获取当前可执行的任务列表
- **`getPlanStatus`** - 获取整个计划的状态

### 可视化和辅助
- **`visualizeDependencies`** - 生成依赖关系可视化（ASCII、树形、Mermaid格式）
- **`generateContextPrompt`** - 生成上下文提示词

## 📝 开发和贡献

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/donway19/MCPlanManager.git
cd MCPlanManager

# 创建虚拟环境并安装开发依赖
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件