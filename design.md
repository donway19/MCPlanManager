好的，这是一个非常棒的系统设计问题。为了确保长程任务的鲁棒性和灵活性，设计一个强大的 `PlanManager` 是核心。让模型通过工具函数来间接操作计划，而不是直接修改JSON，是保证数据一致性和防止意外错误的关键。

下面我为你设计一套完整的 `planManager` 方案，包括：

1.  **JSON 数据结构定义**
2.  **配套的工具函数 (Tools)**
3.  **一个完整的工作流示例**

---

### 1. PlanManager 的 JSON 数据结构

这个结构的核心是任务列表，其中每个任务都是一个对象，包含了执行所需的所有元数据。

```json
{
  "overallGoal": "在京东网站上搜索‘机械键盘’，并将价格低于500元的第一款产品加入购物车。",
  "currentTaskID": 1,
  "tasks": [
    {
      "id": 1,
      "name": "Navigate to JD.com homepage",
      "status": "in_progress",
      "dependencies": [],
      "reasoning": "The first step is to open the target website.",
      "result": null
    },
    {
      "id": 2,
      "name": "Input 'mechanical keyboard' into search bar",
      "status": "pending",
      "dependencies": [1],
      "reasoning": "Need to be on the homepage before I can use the search bar.",
      "result": null
    },
    {
      "id": 3,
      "name": "Click the search button",
      "status": "pending",
      "dependencies": [2],
      "reasoning": "After typing the search term, I must click the button to get results.",
      "result": null
    },
    {
      "id": 4,
      "name": "Filter results by price (under 500)",
      "status": "pending",
      "dependencies": [3],
      "reasoning": "The goal requires filtering by price, which can only be done on the search results page.",
      "result": null
    },
    {
      "id": 5,
      "name": "Add the first item to the shopping cart",
      "status": "pending",
      "dependencies": [4],
      "reasoning": "The final step after filtering is to add the item to the cart.",
      "result": null
    }
  ]
}
```

#### 结构字段说明：

*   `overallGoal`: (string) 用户最终的、最高级别的目标。这为 Agent 提供了最终的上下文，在调整计划时至关重要。
*   `currentTaskID`: (integer) 指向当前正在执行的任务的 `id`。这是 Agent 的“光标”。
*   `tasks`: (array) 任务对象列表。
    *   `id`: (integer) 任务的唯一标识符。
    *   `name`: (string) 对任务的简短描述，Agent 以此来理解要做什么。
    *   `status`: (string) 任务的当前状态。
        *   `pending`: 待处理，尚未开始。
        *   `in_progress`: 正在执行中。
        *   `completed`: 已成功完成。
        *   `failed`: 执行失败。
        *   `skipped`: 被跳过。
    *   `dependencies`: (array of integers) 依赖的任务 `id` 列表。一个任务只有在它所有依赖的任务状态都为 `completed` 时才能开始。
    *   `reasoning`: (string) 为什么需要这个任务？这为 Agent 提供了制定和修改计划的逻辑依据。
    *   `result`: (string, optional) 任务完成后的输出或简短总结，例如“成功登录”或“页面未找到”。

---

### 2. 配套的工具函数 (Tool Functions)

这些是 Agent 可以调用的函数。Agent 不会看到这些函数的内部实现，只能调用它们并获取返回值。

#### **核心流程工具 (Core Workflow Tools)**

1.  **`startNextTask()`**
    *   **描述**: 自动查找并开始下一个可执行的任务。它会检查依赖关系，找到第一个状态为 `pending` 且其所有依赖项都已 `completed` 的任务。
    *   **参数**: 无。
    *   **动作**:
        1.  在 `tasks` 列表中查找第一个满足条件的任务。
        2.  如果找到，将其 `status` 更新为 `in_progress`，并更新顶层的 `currentTaskID`。
        3.  返回该任务对象。
        4.  如果找不到（例如，所有任务都完成或卡住了），则返回一个消息，如 "All tasks are completed or blocked."。
    *   **返回值**: (JSON) 新的当前任务对象或一条状态消息。

2.  **`completeCurrentTask(result_message)`**
    *   **描述**: 将当前正在执行的任务标记为已完成。
    *   **参数**:
        *   `result_message`: (string) 一条描述任务成果的消息，将被记录在任务的 `result` 字段。
    *   **动作**:
        1.  找到 `currentTaskID` 对应的任务。
        2.  将其 `status` 更新为 `completed`。
        3.  将 `result_message` 存入 `result` 字段。
        4.  将 `currentTaskID` 设为 `null`，因为当前没有活动任务了。
    *   **返回值**: (JSON) `{"success": true, "message": "Task [id] marked as completed."}`

#### **计划修订工具 (Plan Revision Tools)**

3.  **`addTask(name, dependencies, reasoning, after_task_id)`**
    *   **描述**: 在计划中插入一个新任务。这对于处理意外情况（如弹窗、验证码）至关重要。
    *   **参数**:
        *   `name`: (string) 新任务的名称。
        *   `dependencies`: (array of integers) 新任务的依赖项。
        *   `reasoning`: (string) 为什么要添加这个任务。
        *   `after_task_id`: (integer) 将新任务插入到此任务ID之后。
    *   **动作**:
        1.  创建一个新的任务对象，分配一个新的唯一 `id`。
        2.  将其插入到 `tasks` 数组中 `after_task_id` 的位置。
        3.  **智能依赖更新**: 检查计划中是否有任何任务依赖于 `after_task_id`。如果有，自动将这些任务的依赖关系从 `after_task_id` 更新为这个新任务的 `id`，以保持计划的连续性。
    *   **返回值**: (JSON) `{"success": true, "newTask": <新任务对象>}`

4.  **`modifyTask(task_id, new_name, new_dependencies)`**
    *   **描述**: 修改一个尚未开始的任务。
    *   **参数**:
        *   `task_id`: (integer) 要修改的任务的ID。
        *   `new_name`: (string, optional) 新的任务名称。
        *   `new_dependencies`: (array, optional) 新的依赖列表。
    *   **动作**:
        1.  找到指定的 `task_id`。
        2.  如果其状态为 `pending`，则更新相应字段。
        3.  如果任务已在进行或已完成，则返回错误。
    *   **返回值**: (JSON) `{"success": true, "updatedTask": <更新后的任务对象>}` 或错误信息。

#### **状态管理工具 (State Management Tools)**

5.  **`skipTask(task_id, reason)`**
    *   **描述**: 跳过一个任务。
    *   **参数**:
        *   `task_id`: (integer) 要跳过的任务ID。
        *   `reason`: (string) 跳过该任务的原因。
    *   **动作**:
        1.  找到指定的 `task_id`，将其 `status` 更新为 `skipped`。
        2.  将 `reason` 记录在 `result` 字段。
    *   **返回值**: (JSON) `{"success": true, "message": "Task [id] skipped."}`

6.  **`failCurrentTask(error_message)`**
    *   **描述**: 将当前任务标记为失败。
    *   **参数**:
        *   `error_message`: (string) 描述失败原因。
    *   **动作**:
        1.  找到 `currentTaskID` 对应的任务，将其 `status` 更新为 `failed`。
        2.  将 `error_message` 记录在 `result` 字段。
    *   **返回值**: (JSON) `{"success": true, "message": "Task [id] marked as failed."}`

---

### 3. 工作流示例 (Workflow Example)

假设 Agent 正在执行上述京东购物计划。

1.  **开始**:
    *   Agent 启动，它的计划中 `currentTaskID` 是 `1`。
    *   **Agent思考**: "我的当前任务是#1: 'Navigate to JD.com homepage'。我将执行浏览器导航操作。"
    *   **Agent行动**: `browser.navigate("https://www.jd.com")`

2.  **完成第一步**:
    *   导航成功。
    *   **Agent思考**: "任务#1已完成。我需要调用工具来更新计划。"
    *   **Agent行动 (调用工具)**: `planManager.completeCurrentTask(result_message="Successfully navigated to JD.com")`
    *   *后台*: `plan.json` 中任务1的状态变为 `completed`。`currentTaskID` 变为 `null`。

3.  **获取下一步**:
    *   **Agent思考**: "我已完成上一个任务，现在需要知道下一步做什么。"
    *   **Agent行动 (调用工具)**: `planManager.startNextTask()`
    *   *后台*: `planManager` 检查到任务1已 `completed`，任务2 `status` 是 `pending` 且其依赖 `[1]` 已满足。于是将任务2的 `status` 设为 `in_progress`，并将 `currentTaskID` 设为 `2`。
    *   *返回值*: `{ "id": 2, "name": "Input 'mechanical keyboard' into search bar", ... }`

4.  **处理意外情况（计划修订）**:
    *   Agent 执行任务2，输入了“机械键盘”。正准备执行任务3（点击搜索）时，网站弹出了一个“新人红包”弹窗，覆盖了搜索按钮。
    *   **Agent观察**: "我无法点击搜索按钮，因为有一个ID为 'new-user-coupon-popup' 的弹窗挡住了它。原始计划没有这一步。"
    *   **Agent思考**: "我必须先关闭这个弹窗，才能继续。我需要在计划中任务2和任务3之间，插入一个新任务。"
    *   **Agent行动 (调用工具)**:
        ```python
        planManager.addTask(
            name="Close the new user coupon popup",
            dependencies=[2], # 它依赖于任务2（输入文本），因为弹窗是在那之后出现的
            reasoning="An unexpected popup is blocking the search button.",
            after_task_id=2
        )
        ```
    *   *后台*:
        *   一个新的任务（比如 `id: 6`）被创建。
        *   它被插入到任务2之后。
        *   原任务3的依赖从 `[2]` 自动更新为 `[6]`。
        *   `plan.json` 现在看起来像这样（简化版）：
            ```
            ...
            { "id": 2, "name": "Input...", "status": "completed", ... },
            { "id": 6, "name": "Close the new user coupon popup", "status": "pending", "dependencies": [2], ... },
            { "id": 3, "name": "Click the search button", "status": "pending", "dependencies": [6], ... }
            ...
            ```

5.  **继续执行新计划**:
    *   **Agent思考**: "计划已更新。我现在需要获取我的新任务。"
    *   **Agent行动 (调用工具)**: `planManager.startNextTask()`
    *   *后台*: `planManager` 找到并启动了新添加的任务#6。
    *   Agent 现在会去执行关闭弹窗的操作，整个任务流程因此变得更加鲁棒和智能。