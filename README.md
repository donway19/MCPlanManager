# MCPlanManager - AI Agent 任务管理系统
[![smithery badge](https://smithery.ai/badge/@donway19/mcplanmanager)](https://smithery.ai/server/@donway19/mcplanmanager)

一个简洁高效的任务管理器，专为 AI Agent 的长程任务执行而设计，支持MCP (Model Context Protocol) 标准。

## 🎯 核心特性

- **简洁的JSON结构**: 最小化复杂度，使用简单的依赖ID数组
- **完整的工具函数集**: 涵盖任务生命周期的所有操作
- **循环依赖检测**: 自动防止无效的依赖关系
- **可视化支持**: 提供多种依赖关系可视化方式（ASCII、树形、Mermaid）
- **智能Prompt生成**: 自动生成上下文感知的执行指导
- **MCP标准支持**: 兼容各种支持MCP的AI客户端
- **灵活的部署方式**: 支持多种安装和配置方式

## 📁 项目结构

```
MCPlanManager-FastMCP/
├── mcplanmanager/           # 核心Python包
│   ├── __init__.py
│   ├── plan_manager.py      # 核心PlanManager类
│   ├── dependency_tools.py  # 可视化和Prompt工具
│   └── app.py               # FastMCP服务器实现
├── docs/                    # 文档
│   ├── design.md
│   ├── plan_manager_design.md
│   └── DEPLOYMENT_GUIDE.md
├── tests/                   # 测试文件
│   ├── test_deployment.py
│   ├── test_new_initialization.py
│   └── example_usage.py
├── examples/                # 示例文件
│   ├── example_plan.json
│   └── mcp_configs/         # MCP客户端配置
│       ├── cursor.json      # Cursor IDE配置
│       ├── claude_desktop.json  # Claude Desktop配置
│       ├── github_deployment.json      # GitHub配置
│       ├── local_development.json      # 本地开发配置
│       └── modelscope_deployment.json  # 魔搭平台配置
├── server/                  # HTTP服务器
│   └── api_server.py
├── pyproject.toml           # 项目配置和依赖
├── LICENSE                  # MIT许可证
└── README.md               # 本文档
```

## 🚀 安装方法

### 推荐方式：使用 uv 安装

### 安装 via Smithery

要在 Claude Desktop 上安装 MCPlanManager，请使用 [Smithery](https://smithery.ai/server/@donway19/mcplanmanager):

```bash
npx -y @smithery/cli install @donway19/mcplanmanager --client claude
```

```bash
# 确保已安装 uv (如果未安装，请参考 uv 官方文档)
# curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆仓库
git clone https://github.com/donway19/MCPlanManager.git
cd MCPlanManager-FastMCP

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装项目
uv pip install .
```

### 直接从GitHub安装 (不推荐，uv 方式更优)
```bash
pip install git+https://github.com/donway19/MCPlanManager.git
```

## 🔧 MCP客户端配置

### Cursor IDE

1. **安装依赖**:
```bash
# 使用uv包管理器（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv ~/.mcpenv
uv pip install --directory ~/.mcpenv git+https://github.com/donway19/MCPlanManager.git
```

2. **配置Cursor**:
   - 打开Cursor设置 → Extensions → MCP
   - 添加以下配置到 `mcp_servers.json`:

```json
{
  "mcpServers": {
    "mcplanmanager": {
      "command": "uv",
      "args": ["--directory", "~/.mcpenv", "run", "mcplanmanager"],
      "env": {
        "UV_PROJECT_ENVIRONMENT": "~/.mcpenv"
      }
    }
  }
}
```

3. **验证安装**: 重启Cursor，在Chat中应该能看到MCPlanManager工具可用。

### Claude Desktop

1. **安装依赖**:
```bash
uv pip install git+https://github.com/donway19/MCPlanManager.git
```

2. **配置Claude Desktop**:
   - 找到Claude Desktop配置文件:
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
     - **Linux**: `~/.config/claude/claude_desktop_config.json`
   - 添加以下配置:

```json
{
  "mcpServers": {
    "mcplanmanager": {
      "command": "uv",
      "args": ["run", "mcplanmanager"],
      "env": {}
    }
  }
}
```

3. **重启Claude Desktop**使配置生效。

### Continue.dev

1. **安装依赖**:
```bash
uv pip install git+https://github.com/donway19/MCPlanManager.git
```

2. **配置Continue**:
   - 编辑 `~/.continue/config.json`
   - 添加MCP服务器配置:

```json
{
  "mcpServers": [
    {
      "name": "mcplanmanager",
      "command": "uv",
      "args": ["run", "mcplanmanager"]
    }
  ]
}
```

### 自定义MCP客户端

对于其他支持MCP的客户端，使用以下通用配置模板：

```json
{
  "name": "mcplanmanager",
  "command": "uv",
  "args": ["run", "mcplanmanager"],
  "env": {},
  "capabilities": {
    "tools": true,
    "resources": false,
    "prompts": false
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

## 💡 使用示例

### 基本用法 (MCP模式)

MCPlanManager专为AI模型设计，模型只需要提供业务内容，技术字段由工具自动维护：

**AI模型只需要提供：**
- `goal`: 计划目标
- `tasks`: 任务列表，每个任务包含：
  - `name`: 任务名称  
  - `reasoning`: 执行理由
  - `dependencies`: 依赖的任务（任务名称列表或索引列表）

**工具自动维护：**
- `id`: 从1开始自动分配
- `status`: 初始为"pending"
- `result`: 初始为None
- `created_at/updated_at`: 自动设置时间戳

### MCP客户端中的对话示例

```
用户: 帮我创建一个网上购物的任务计划

AI: 我来为您创建一个网上购物任务计划。

> 使用工具: initializePlan
> 参数: {
>   "goal": "完成网上购物流程",
>   "tasks": [
>     {
>       "name": "浏览商品",
>       "reasoning": "查看可用商品和价格",
>       "dependencies": []
>     },
>     {
>       "name": "选择商品",
>       "reasoning": "确定要购买的商品",
>       "dependencies": ["浏览商品"]
>     },
>     {
>       "name": "添加到购物车",
>       "reasoning": "将选中的商品加入购物车",
>       "dependencies": ["选择商品"]
>     },
>     {
>       "name": "填写收货信息",
>       "reasoning": "提供配送地址和联系方式",
>       "dependencies": ["添加到购物车"]
>     },
>     {
>       "name": "选择支付方式",
>       "reasoning": "选择合适的支付方式",
>       "dependencies": ["填写收货信息"]
>     },
>     {
>       "name": "确认订单",
>       "reasoning": "最终确认购买",
>       "dependencies": ["选择支付方式"]
>     }
>   ]
> }

计划已创建！包含6个任务，任务间有明确的依赖关系。

用户: 开始执行第一个任务

AI: 好的，我来开始执行第一个任务。

> 使用工具: startNextTask

已开始执行任务1：浏览商品
理由：查看可用商品和价格
```

### 编程使用示例

```python
from mcplanmanager import PlanManager

# 初始化计划管理器
pm = PlanManager() # 移除文件路径参数

# 创建任务计划
tasks = [
    {
        "name": "数据收集",
        "reasoning": "收集分析所需的数据",
        "dependencies": []
    },
    {
        "name": "数据清洗",
        "reasoning": "清理和预处理数据",
        "dependencies": ["数据收集"]
    },
    {
        "name": "数据分析",
        "reasoning": "执行数据分析",
        "dependencies": ["数据清洗"]
    }
]

# 初始化计划
result = pm.initializePlan("数据分析项目", tasks)

# 开始执行任务
current_task = pm.startNextTask()
print(f"当前任务: {current_task['name']}")

# 完成任务
pm.completeTask(current_task['id'], "数据收集完成")

# 查看计划状态
status = pm.getPlanStatus()
print(f"计划进度: {status['progress']:.1%}")
```

## 🔍 依赖关系可视化

MCPlanManager支持多种可视化格式：

```python
# ASCII格式
# pm.visualizeDependencies("ascii") # 移除直接调用，通过MCP工具调用

# 树形格式
# pm.visualizeDependencies("tree") # 移除直接调用，通过MCP工具调用

# Mermaid格式（可在支持的工具中渲染）
# pm.visualizeDependencies("mermaid") # 移除直接调用，通过MCP工具调用
```

## 📊 任务状态管理

支持的任务状态：
- **pending**: 等待执行
- **in_progress**: 正在执行
- **completed**: 已完成
- **failed**: 执行失败
- **skipped**: 已跳过

## 🛡️ 错误处理

MCPlanManager具有完整的错误处理机制：
- 自动检测循环依赖
- 验证任务依赖关系
- 提供详细的错误信息
- 支持任务重试机制

## 📝 开发和贡献

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/donway19/MCPlanManager.git
cd MCPlanManager-FastMCP

# 创建虚拟环境并安装开发依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
uv pip install -e ".[dev]"

# 运行测试
pytest tests/
```

### 测试MCP服务器

```bash
# 运行MCP服务器
uv run mcplanmanager
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系和支持

- **作者**: Donwaydoom
- **邮箱**: Donwaydoom@gmail.com
- **GitHub**: [https://github.com/donway19/MCPlanManager](https://github.com/donway19/MCPlanManager)
- **Issues**: [https://github.com/donway19/MCPlanManager/issues](https://github.com/donway19/MCPlanManager/issues)

## 🎯 版本历史

- **v1.0.0**: 初始版本
  - 完整的MCP支持
  - 12个核心工具函数
  - 多种可视化格式
  - 完善的错误处理

---

**MCPlanManager** - 让AI Agent的任务管理变得简单高效！ 