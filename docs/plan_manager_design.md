# PlanManager 设计文档

## 1. 概述

PlanManager 是一个轻量级的任务管理器，专门为 AI Agent 的长程任务执行而设计。采用纯内存管理模式，所有任务对象和计划数据均驻留于内存，不依赖任何文件存储。

### 设计原则
- **简洁性**: 最小化数据结构和 API 复杂度
- **高效性**: 快速查找和更新任务状态
- **可用性**: 提供清晰的错误处理和状态管理
- **可扩展性**: 支持动态添加和修改任务

## 2. 数据结构定义

### 2.1 核心数据结构

```json
{
  "meta": {
    "goal": "在京东网站上搜索'机械键盘'，并将价格低于500元的第一款产品加入购物车",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "state": {
    "current_task_id": 1,
    "status": "running"
  },
  "tasks": [
    {
      "id": 1,
      "name": "Navigate to JD homepage",
      "status": "in_progress",
      "dependencies": [],
      "reasoning": "Need to open the target website first",
      "result": null
    },
    {
      "id": 2,
      "name": "Search for mechanical keyboard", 
      "status": "pending",
      "dependencies": [1],
      "reasoning": "Can only search after homepage is loaded",
      "result": null
    },
    {
      "id": 3,
      "name": "Filter results by price under 500",
      "status": "pending", 
      "dependencies": [2],
      "reasoning": "Need search results before applying filters",
      "result": null
    },
    {
      "id": 4,
      "name": "Add first item to cart",
      "status": "pending",
      "dependencies": [3], 
      "reasoning": "Need filtered results to select the first item",
      "result": null
    }
  ]
}
```

### 2.2 枚举类型定义

```typescript
// 任务状态
enum TaskStatus {
  PENDING = "pending",      // 待执行
  IN_PROGRESS = "in_progress", // 执行中
  COMPLETED = "completed",   // 已完成
  FAILED = "failed",        // 失败
  SKIPPED = "skipped",      // 跳过
  BLOCKED = "blocked"       // 阻塞（依赖未满足）
}

// 计划状态
enum PlanStatus {
  IDLE = "idle",           // 空闲
  RUNNING = "running",     // 运行中
  COMPLETED = "completed", // 全部完成
  FAILED = "failed",       // 失败
  PAUSED = "paused"        // 暂停
}
```

### 2.3 数据字段说明

**meta字段**:
- `goal`: 整体目标描述
- `created_at`: 创建时间
- `updated_at`: 最后更新时间

**state字段**:
- `current_task_id`: 当前执行的任务ID
- `status`: 计划状态 (idle/running/completed/failed/paused)

**task字段**:
- `id`: 任务唯一标识符
- `name`: 任务名称
- `status`: 任务状态 (pending/in_progress/completed/failed/skipped)
- `dependencies`: 依赖的任务ID列表 (简洁的数组结构)
- `reasoning`: 任务执行理由
- `result`: 任务执行结果 (完成后填充)

## 3. 工具函数接口定义

### 3.1 核心流程函数

#### `getCurrentTask()`
**功能**: 获取当前正在执行的任务

**输入参数**: 无

**输出**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Navigate to JD homepage",
    "status": "in_progress",
    "dependencies": [],
    "reasoning": "Need to open the target website first"
  }
}
```

#### `startNextTask()`
**功能**: 自动开始下一个可执行的任务

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "task": { /* 任务对象 */ },
    "message": "Started task 2: Search for mechanical keyboard"
  }
}
```

#### `completeTask(task_id, result)`
**功能**: 标记任务为完成状态

**输入参数**:
- `task_id` (number): 任务ID
- `result` (string): 执行结果描述

**输出**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "message": "Task completed successfully"
  }
}
```

#### `failTask(task_id, error_message, should_retry)`
**功能**: 标记任务失败

**输入参数**:
- `task_id` (number): 任务ID
- `error_message` (string): 错误信息
- `should_retry` (boolean, 可选): 是否应该重试，默认为 true

**输出**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "will_retry": true,
    "retry_count": 1,
    "message": "Task failed, will retry"
  }
}
```

### 3.2 任务管理函数

#### `addTask(name, dependencies, reasoning, after_task_id)`
**功能**: 添加新任务到计划中

**输入参数**:
- `name` (string): 任务名称
- `dependencies` (list[int]): 依赖的任务ID列表
- `reasoning` (string): 添加理由
- `after_task_id` (int, 可选): 插入到指定任务之后

**输出**:
```json
{
  "success": true,
  "data": {
    "new_task": { /* 新任务对象 */ },
    "message": "Task added successfully"
  }
}
```

#### `updateTask(task_id, updates)`
**功能**: 更新任务信息

**输入参数**:
- `task_id` (int): 任务ID
- `updates` (dict): 更新的字段
  - `name` (string, 可选): 新名称
  - `dependencies` (list[int], 可选): 新依赖ID列表
  - `reasoning` (string, 可选): 新理由

**输出**:
```json
{
  "success": true,
  "data": {
    "updated_task": { /* 更新后的任务对象 */ },
    "message": "Task updated successfully"
  }
}
```

#### `skipTask(task_id, reason)`
**功能**: 跳过指定任务

**输入参数**:
- `task_id` (number): 任务ID
- `reason` (string): 跳过原因

**输出**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "message": "Task skipped: reason"
  }
}
```

#### `removeTask(task_id)`
**功能**: 删除任务（仅限 pending 状态的任务）

**输入参数**:
- `task_id` (number): 任务ID

**输出**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "message": "Task removed successfully"
  }
}
```

### 3.3 查询函数

#### `getTaskList(status_filter)`
**功能**: 获取任务列表

**输入参数**:
- `status_filter` (string, 可选): 状态过滤器，如 "pending", "completed" 等

**输出**:
```json
{
  "success": true,
  "data": {
    "tasks": [ /* 任务列表 */ ],
    "total": 5,
    "filtered": 3
  }
}
```

#### `getPlanStatus()`
**功能**: 获取整个计划的状态

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "status": "running",
    "progress": 0.4,
    "current_task_id": 2,
    "total_tasks": 5,
    "completed_tasks": 2,
    "failed_tasks": 0,
    "pending_tasks": 3
  }
}
```

#### `getTaskById(task_id)`
**功能**: 根据ID获取任务详情

**输入参数**:
- `task_id` (number): 任务ID

**输出**:
```json
{
  "success": true,
  "data": {
    "task": { /* 任务对象 */ }
  }
}
```

#### `getExecutableTaskList()`
**功能**: 获取当前可执行的任务列表（依赖已满足的 pending 任务）

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "executable_tasks": [ /* 可执行任务列表 */ ],
    "count": 2
  }
}
```

### 3.4 控制函数

#### `pausePlan()`
**功能**: 暂停整个计划

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "message": "Plan paused successfully"
  }
}
```

#### `resumePlan()`
**功能**: 恢复计划执行

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "message": "Plan resumed successfully"
  }
}
```

#### `resetPlan()`
**功能**: 重置计划（将所有任务状态重置为 pending）

**输入参数**: 无

**输出**:
```json
{
  "success": true,
  "data": {
    "message": "Plan reset successfully",
    "reset_tasks": 5
  }
}
```

## 4. 错误处理

所有函数在出错时返回统一的错误格式：

```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 1 not found",
    "details": {}
  }
}
```

### 常见错误代码
- `TASK_NOT_FOUND`: 任务不存在
- `INVALID_DEPENDENCY`: 无效的依赖关系
- `TASK_NOT_EDITABLE`: 任务不可编辑（已完成或进行中）
- `CIRCULAR_DEPENDENCY`: 循环依赖
- `INVALID_STATUS`: 无效的状态转换
- `PLAN_NOT_ACTIVE`: 计划未激活

## 5. 使用示例 (Python)

```python
# 1. 获取当前任务
current_task = plan_manager.getCurrentTask()
# 输出: {"success": True, "data": {"id": 1, "name": "Navigate to JD homepage", ...}}

# 2. 完成当前任务
plan_manager.completeTask(current_task["data"]["id"], "Successfully navigated to homepage")

# 3. 开始下一个任务
next_task = plan_manager.startNextTask()
# 输出: {"success": True, "data": {"task": {"id": 2, "name": "Search for mechanical keyboard", ...}}}

# 4. 处理意外情况，添加新任务
plan_manager.addTask(
    "Close popup dialog",
    [1],  # 依赖任务1
    "Unexpected popup appeared blocking the search",
    after_task_id=1  # 插入到任务1之后
)

# 5. 添加复杂依赖的任务
plan_manager.addTask(
    "Add item to cart",
    [2, 3],  # 需要任务2和任务3都完成
    "Final step to complete the purchase goal"
)

# 6. 查看计划状态
status = plan_manager.getPlanStatus()
# 输出: {"success": True, "data": {"status": "running", "current_task_id": 2, ...}}

# 7. 查看所有可执行的任务
executable_tasks = plan_manager.getExecutableTaskList()
# 输出: {"success": True, "data": {"executable_tasks": [...], "count": 2}}
```

## 6. Agent 工具调用格式 (Python)

Agent 调用这些函数时，使用标准的Python函数调用格式：

```python
# 获取当前任务
plan_manager.getCurrentTask()

# 完成任务
plan_manager.completeTask(1, "Successfully loaded JD homepage")

# 添加新任务
plan_manager.addTask(
    "Handle login verification", 
    [1],  # 依赖任务1
    "Phone verification popup appeared during login"
)

# 更新任务依赖
plan_manager.updateTask(3, {
    "dependencies": [1, 5]  # 依赖任务1和5
})

# 跳过不必要的任务
plan_manager.skipTask(4, "Price filter not needed, items already in range")
```

  ## 7. 性能考虑

- 任务数量建议控制在 100 个以内
- 依赖关系深度建议不超过 10 层
- 使用简洁的JSON结构减少存储开销
- 依赖关系检查采用高效算法

## 8. 扩展性

- 依赖关系可视化工具 (单独实现)
- 依赖关系转Prompt工具 (单独实现)
- 支持任务的并行执行检测
- 支持循环依赖检测和报告

PlanManager 工具已通过简单测试，主要功能可用。

*后台*: 内存中的任务对象状态变为 `completed`，`currentTaskID` 变为 `null`。

*后台*: 内存中的计划数据结构现在看起来像这样（简化版）： 