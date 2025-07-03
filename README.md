# MCPlanManager - AI Agent 任务管理系统

一个简洁高效的任务管理器，专为 AI Agent 的长程任务执行而设计，支持MCP (Model Context Protocol) 标准。

## 🎯 核心特性

- **简洁的JSON结构**: 最小化复杂度，使用简单的依赖ID数组
- **完整的工具函数集**: 涵盖任务生命周期的所有操作
- **循环依赖检测**: 自动防止无效的依赖关系
- **可视化支持**: 提供多种依赖关系可视化方式
- **智能Prompt生成**: 自动生成上下文感知的执行指导
- **MCP标准支持**: 兼容各种支持MCP的AI客户端

## 📁 项目结构

```
MCPlanManager/
├── mcplanmanager/           # 核心Python包
│   ├── __init__.py
│   ├── plan_manager.py      # 核心PlanManager类
│   ├── dependency_tools.py  # 可视化和Prompt工具
│   └── mcp_wrapper.py       # MCP服务包装器
├── docs/                    # 文档
│   ├── design.md
│   ├── plan_manager_design.md
│   └── DEPLOYMENT_GUIDE.md
├── tests/                   # 测试文件
│   ├── test_deployment.py
│   └── example_usage.py
├── examples/                # 示例文件
│   ├── example_plan.json
│   └── mcp_configs/         # MCP客户端配置
│       ├── cursor.json      # Cursor IDE配置
│       ├── claude_desktop.json  # Claude Desktop配置
│       ├── github.json      # GitHub配置
│       └── modelscope.json  # 魔搭平台配置
├── server/                  # HTTP服务器
│   └── api_server.py
├── setup.py
├── requirements.txt
├── LICENSE
└── README.md               # 本文档
```

## 🚀 安装方法

### 从GitHub安装
```bash
# 方法一：直接从GitHub安装
pip install git+https://github.com/donway19/MCPlanManager.git

# 方法二：克隆仓库后安装
git clone https://github.com/donway19/MCPlanManager.git
cd MCPlanManager
pip install -e .
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
pip install git+https://github.com/donway19/MCPlanManager.git
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
      "command": "python",
      "args": ["-m", "mcplanmanager.mcp_wrapper"],
      "env": {}
    }
  }
}
```

3. **重启Claude Desktop**使配置生效。

### Continue.dev

1. **安装依赖**:
```bash
pip install git+https://github.com/donway19/MCPlanManager.git
```

2. **配置Continue**:
   - 编辑 `~/.continue/config.json`
   - 添加MCP服务器配置:

```json
{
  "mcpServers": [
    {
      "name": "mcplanmanager",
      "command": "python",
      "args": ["-m", "mcplanmanager.mcp_wrapper"]
    }
  ]
}
```

### 自定义MCP客户端

对于其他支持MCP的客户端，使用以下通用配置模板：

```json
{
  "name": "mcplanmanager",
  "command": "python",
  "args": ["-m", "mcplanmanager.mcp_wrapper"],
  "env": {},
  "capabilities": {
    "tools": true,
    "resources": false,
    "prompts": false
  }
}
```

## 🔍 可用的MCP工具

安装配置成功后，您可以使用以下工具：

- `initializePlan` - 初始化新的任务计划
- `getCurrentTask` - 获取当前应执行的任务
- `startNextTask` - 开始下一个任务
- `completeTask` - 完成任务
- `failTask` - 标记任务失败
- `addTask` - 添加新任务
- `updateTask` - 更新任务信息
- `skipTask` - 跳过任务
- `getPlanStatus` - 获取计划状态
- `getTaskList` - 获取任务列表
- `visualizePlan` - 可视化依赖关系
- `generatePrompt` - 生成上下文提示词

## 💡 使用示例 (MCP模式)

### AI模型友好的初始化方式

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

[调用initializePlan工具]
参数:
{
  "goal": "完成网上购物流程",
  "tasks": [
    {
      "name": "打开购物网站",
      "reasoning": "开始购物流程的第一步",
      "dependencies": []
    },
    {
      "name": "搜索商品", 
      "reasoning": "查找需要购买的商品",
      "dependencies": ["打开购物网站"]
    },
    {
      "name": "加入购物车",
      "reasoning": "将选中商品加入购物车",
      "dependencies": ["搜索商品"]
    },
    {
      "name": "完成支付",
      "reasoning": "执行支付操作",
      "dependencies": ["加入购物车"]
    }
  ]
}

✅ 计划创建成功！已自动分配任务ID和设置初始状态。

用户: 开始执行第一个任务

AI: 开始执行任务...
[使用startNextTask工具]

用户: 任务1完成了，成功打开了购物网站

AI: 标记任务1为完成状态...
[使用completeTask工具]
```

## 🚀 快速开始

### 1. 基本使用

```python
from mcplanmanager import PlanManager

# 创建PlanManager实例
pm = PlanManager("my_plan.json")

# 使用新的AI友好初始化方式
goal = "完成网站自动化任务"
tasks = [
    {
        "name": "打开网站",
        "reasoning": "第一步需要访问目标网站",
        "dependencies": []  # 无依赖
    },
    {
        "name": "登录账户",
        "reasoning": "需要先打开网站才能登录",
        "dependencies": ["打开网站"]  # 依赖任务名称
    }
]

# 工具会自动分配ID、设置状态等技术字段
result = pm.initializePlan(goal, tasks)
print(result)

# 开始执行任务
response = pm.startNextTask()
print(response)
```

### 2. Agent工具函数调用

```python
# 获取当前任务
current_task = pm.getCurrentTask()

# 完成任务
pm.completeTask(1, "成功打开网站")

# 添加新任务处理意外情况
pm.addTask(
    "关闭弹窗", 
    [1],  # 依赖任务1
    "登录时出现广告弹窗"
)

# 更新任务依赖
pm.updateTask(2, {
    "dependencies": [1, 3]  # 现在依赖任务1和3
})

# 跳过任务
pm.skipTask(4, "此步骤不再需要")
```

### 3. 查看依赖关系

```python
from mcplanmanager import DependencyVisualizer, DependencyPromptGenerator

# 可视化依赖关系
pm = PlanManager("my_plan.json")
visualizer = DependencyVisualizer(pm)
print(visualizer.generate_ascii_graph())

# 生成上下文提示词
generator = DependencyPromptGenerator(pm)
prompt = generator.generate_context_prompt()
print(prompt)
```

## 📊 数据结构说明

### initializePlan 参数结构

AI模型在调用`initializePlan`工具时，只需要提供以下简化的参数：

```json
{
  "goal": "任务总目标描述",
  "tasks": [
    {
      "name": "任务名称",
      "reasoning": "执行这个任务的理由和目的", 
      "dependencies": ["依赖的任务名称"] // 或者 [1, 2] 任务索引
    }
  ]
}
```

**依赖关系表达方式：**
- **任务名称**: `["打开网站", "登录账户"]` - 使用任务名称表达依赖
- **任务索引**: `[1, 2]` - 使用1-based索引表达依赖  
- **混合方式**: `["打开网站", 2]` - 可以混合使用

### 内部JSON数据结构

工具会自动生成完整的内部数据结构：

```json
{
  "meta": {
    "goal": "任务总目标",
    "created_at": "2024-01-01T00:00:00Z", 
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "state": {
    "current_task_id": 1,
    "status": "running"
  },
  "tasks": [
    {
      "id": 1,                    // 工具自动分配
      "name": "任务名称",          // 模型提供
      "status": "in_progress",    // 工具自动维护
      "dependencies": [2, 3],     // 工具自动转换为ID
      "reasoning": "执行理由",     // 模型提供
      "result": null              // 工具自动初始化
    }
  ]
}
```

### 状态枚举
- **任务状态**: `pending`, `in_progress`, `completed`, `failed`, `skipped`
- **计划状态**: `idle`, `running`, `completed`, `failed`, `paused`

## 🔧 API 参考

### 核心流程函数

| 函数 | 功能 | 参数 | 返回 |
|------|------|------|------|
| `getCurrentTask()` | 获取当前任务 | 无 | 任务对象 |
| `startNextTask()` | 开始下一个任务 | 无 | 启动的任务 |
| `completeTask(task_id, result)` | 完成任务 | task_id, result | 成功消息 |
| `failTask(task_id, error, retry)` | 标记失败 | task_id, error_msg, should_retry | 失败信息 |

### 任务管理函数

| 函数 | 功能 | 参数 | 返回 |
|------|------|------|------|
| `addTask(name, deps, reason, after)` | 添加任务 | name, dependencies, reasoning, after_task_id | 新任务 |
| `updateTask(task_id, updates)` | 更新任务 | task_id, updates_dict | 更新结果 |
| `skipTask(task_id, reason)` | 跳过任务 | task_id, reason | 跳过确认 |
| `removeTask(task_id)` | 删除任务 | task_id | 删除确认 |

### 查询函数

| 函数 | 功能 | 參數 | 返回 |
|------|------|------|------|
| `getTaskList(filter)` | 获取任务列表 | status_filter | 任务列表 |
| `getPlanStatus()` | 计划状态 | 无 | 状态统计 |
| `getExecutableTaskList()` | 可执行任务 | 无 | 可执行列表 |
| `getDependencyGraph()` | 依赖图数据 | 无 | 图形数据 |

## 🎨 可视化工具

### ASCII图形
```python
from mcplanmanager import PlanManager, DependencyVisualizer

pm = PlanManager("plan.json")
viz = DependencyVisualizer(pm)

# ASCII文本图
print(viz.generate_ascii_graph())

# 树状视图
print(viz.generate_tree_view())

# Mermaid图形代码
print(viz.generate_mermaid_graph())
```

### 输出示例
```
📋 任务依赖关系图
==================================================
✅ [1] Navigate to JD homepage
🔄 [2] Search for mechanical keyboard (依赖: [1])
⏳ [3] Filter results by price under 500 (依赖: [2])
⏳ [4] Add first item to cart (依赖: [3])

📝 状态图例:
⏳ 待处理  🔄 进行中  ✅ 已完成  ❌ 失败  ⏭️ 跳过
```

## 🤖 Prompt生成工具

### 上下文提示词
```python
from mcplanmanager import PlanManager, DependencyPromptGenerator

pm = PlanManager("plan.json")
generator = DependencyPromptGenerator(pm)

# 生成上下文提示词
context_prompt = generator.generate_context_prompt()

# 生成下一步行动指导
action_prompt = generator.generate_next_action_prompt()

# 生成错误处理指导
error_prompt = generator.generate_error_handling_prompt("登录失败")
```

### 提示词示例
```markdown
# 任务执行上下文

## 总体目标
在京东网站上搜索'机械键盘'，并将价格低于500元的第一款产品加入购物车

## 当前状态
- 当前执行任务: [2] Search for mechanical keyboard
- 任务状态: in_progress
- 执行理由: 在首页搜索机械键盘

## 可执行任务
- [3] Filter results by price under 500

## 执行建议
- 当前进度: 25.0% (1/4)
- 剩余 2 个任务待执行
- 继续执行当前任务
```

## 🔍 错误处理

所有函数返回统一格式：

### 成功响应
```json
{
  "success": true,
  "data": { /* 响应数据 */ }
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 1 not found",
    "details": {}
  }
}
```

### 常见错误代码
- `TASK_NOT_FOUND`: 任务不存在
- `INVALID_DEPENDENCY`: 无效依赖
- `CIRCULAR_DEPENDENCY`: 循环依赖
- `TASK_NOT_EDITABLE`: 任务不可编辑
- `NO_EXECUTABLE_TASK`: 无可执行任务

## 📝 使用示例

### 完整工作流程
```python
#!/usr/bin/env python3
from plan_manager import PlanManager

def agent_workflow():
    pm = PlanManager("agent_plan.json")
    
    # 1. 初始化任务
    goal = "自动化数据采集任务"
    tasks = [
        {"id": 1, "name": "打开目标网站", "status": "pending", 
         "dependencies": [], "reasoning": "开始数据采集", "result": None},
        {"id": 2, "name": "登录账户", "status": "pending",
         "dependencies": [1], "reasoning": "获取访问权限", "result": None},
        {"id": 3, "name": "采集数据", "status": "pending", 
         "dependencies": [2], "reasoning": "执行主要任务", "result": None}
    ]
    pm.initializePlan(goal, tasks)
    
    # 2. 执行循环
    while True:
        # 获取当前状态
        status = pm.getPlanStatus()
        if not status["success"]:
            break
            
        plan_status = status["data"]["status"]
        
        if plan_status == "completed":
            print("✅ 所有任务已完成!")
            break
        elif plan_status == "failed":
            print("❌ 任务执行失败!")
            break
        
        # 开始下一个任务
        next_task = pm.startNextTask()
        if not next_task["success"]:
            print("⏸️ 没有可执行的任务")
            break
            
        task = next_task["data"]["task"]
        print(f"🔄 执行任务: [{task['id']}] {task['name']}")
        
        # 模拟任务执行
        try:
            # 这里是实际的任务执行逻辑
            result = execute_actual_task(task)
            pm.completeTask(task["id"], result)
            print(f"✅ 任务完成: {result}")
        except Exception as e:
            # 处理异常情况
            if "popup" in str(e):
                # 添加处理弹窗的任务
                pm.addTask(
                    "关闭弹窗",
                    [task["id"]], 
                    f"处理意外弹窗: {str(e)}",
                    after_task_id=task["id"]
                )
                pm.failTask(task["id"], str(e))
            else:
                pm.failTask(task["id"], str(e))
            print(f"❌ 任务失败: {str(e)}")

def execute_actual_task(task):
    # 这里实现具体的任务执行逻辑
    # 如浏览器操作、API调用等
    if task["name"] == "打开目标网站":
        return "成功打开网站"
    elif task["name"] == "登录账户":
        return "登录成功"
    elif task["name"] == "采集数据":
        return "采集完成100条记录"
    return "任务执行完成"

if __name__ == "__main__":
    agent_workflow()
```

## ⚡ 性能建议

- 任务数量建议控制在 100 个以内
- 依赖关系深度建议不超过 10 层
- 定期清理已完成的计划文件
- 使用简洁的任务名称和描述

## 🔧 扩展性

本系统设计为高度可扩展：

1. **自定义状态**: 可以扩展任务状态类型
2. **插件系统**: 可以添加自定义工具函数
3. **存储后端**: 可以替换JSON文件存储
4. **通知系统**: 可以添加任务状态变更通知

## 🤝 贡献

欢迎提交Issues和Pull Requests来改进这个项目！

## 📄 许可证

MIT License - 详见LICENSE文件

---

💡 **提示**: 运行 `python example_usage.py` 查看完整的使用示例！ 