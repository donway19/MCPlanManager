# PlanManager 发布部署指南

本指南将详细介绍如何将PlanManager发布到GitHub并在魔搭平台上托管。

PlanManager 采用纯内存管理，所有任务对象均驻留于内存。工具已通过简单测试，主要功能可用。

## GitHub发布步骤

### 1. 更新配置文件

发布前需要修改以下配置：

**mcp_config_github.json** - 用户从GitHub克隆后使用：
```json
{
  "mcpServers": {
    "plan-manager": {
      "command": "python",
      "args": ["mcp_wrapper.py"],
      "cwd": "~/PlanManager",
      "description": "PlanManager AI Agent任务管理工具",
      "env": {
        "PYTHONPATH": "~/PlanManager"
      }
    }
  }
}
```

**setup.py** - 替换占位符：
- `YOUR_USERNAME` -> 你的GitHub用户名
- `Your Name` -> 你的真实姓名  
- `your.email@example.com` -> 你的邮箱

### 2. 创建GitHub仓库

```bash
# 初始化并推送
git init
git add .
git commit -m "Initial commit: PlanManager MCP服务"
git remote add origin https://github.com/YOUR_USERNAME/PlanManager.git
git push -u origin main

# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

## 魔搭平台部署

### 1. 平台配置

**mcp_config_modelscope.json** 适用于魔搭平台：
```json
{
  "mcpServers": {
    "plan-manager": {
      "command": "python", 
      "args": ["mcp_wrapper.py"],
      "cwd": "/workspace/PlanManager",
      "env": {
        "PYTHONPATH": "/workspace/PlanManager",
        "PLAN_MANAGER_DATA_DIR": "/workspace/data"
      }
    }
  }
}
```

### 2. 用户安装方式

**从GitHub克隆：**
```bash
git clone https://github.com/YOUR_USERNAME/PlanManager.git
cd PlanManager
pip install -r requirements.txt
```

**Python包安装：**
```bash
pip install git+https://github.com/YOUR_USERNAME/PlanManager.git
```

### 3. Claude Desktop配置

配置文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

添加配置：
```json
{
  "mcpServers": {
    "plan-manager": {
      "command": "python",
      "args": ["~/PlanManager/mcp_wrapper.py"], 
      "cwd": "~/PlanManager"
    }
  }
}
```

## 验证安装

```bash
# 测试命令行工具
python mcp_wrapper.py getPlanStatus

# 测试Claude Desktop
# 在对话中输入："请帮我初始化一个购物计划"
```