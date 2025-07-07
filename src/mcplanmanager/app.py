from fastmcp import FastMCP
from typing import List, Optional
from .plan_manager import PlanManager
from .models import TaskInput, DependencyEdit, TaskOutput, ToolResponse, PlanStatusData
import os

mcp = FastMCP("MCPlanManager")

plan_manager = PlanManager()

@mcp.tool()
def initializePlan(goal: str, tasks: List[TaskInput]) -> ToolResponse[dict]:
    """
    初始化或完全替换一个新的任务计划。

    Args:
        goal (str): 描述计划总体目标的字符串。
        tasks (List[TaskInput]): 任务对象的列表。每个任务都应符合TaskInput模型定义的结构。
    """
    task_dicts = [task.model_dump() for task in tasks]
    return plan_manager.initializePlan(goal, task_dicts)

@mcp.tool()
def visualizeDependencies(format: str = "ascii") -> str:
    """
    生成当前任务依赖关系的可视化图。

    Args:
        format (str, optional): 输出的格式。可接受的值为 'mermaid' (生成流程图代码), 
                              'tree' (生成树状图), 或 'ascii' (生成纯文本格式的列表)。
                              默认为 'ascii'。
    
    Returns:
        str: 包含所选格式可视化内容的字符串。
    """
    from .dependency_tools import DependencyVisualizer
    visualizer = DependencyVisualizer(plan_manager)
    if format == "ascii":
        visualization = visualizer.generate_ascii_graph()
    elif format == "tree":
        visualization = visualizer.generate_tree_view()
    elif format == "mermaid":
        visualization = visualizer.generate_mermaid_graph()
    else:
        visualization = visualizer.generate_ascii_graph()
    return visualization

@mcp.tool()
def getCurrentTask() -> ToolResponse[TaskOutput]:
    """
    获取当前标记为 'in_progress' (正在进行中) 的任务详情。
    
    Returns:
        ToolResponse[TaskOutput]: 包含当前任务详情的响应对象。
    """
    return plan_manager.getCurrentTask()

@mcp.tool()
def startNextTask() -> ToolResponse[TaskOutput]:
    """
    自动查找下一个可执行的任务（所有依赖均已完成）并开始执行。
    这会将任务状态更新为 'in_progress'。这是推进计划的核心方法。
    
    Returns:
        ToolResponse[TaskOutput]: 包含已启动任务的响应对象。
    """
    return plan_manager.startNextTask()

@mcp.tool()
def completeTask(task_id: int, result: str) -> ToolResponse[TaskOutput]:
    """
    将指定ID的任务标记为 'completed' (已完成)。
    这是解锁后续依赖任务的关键步骤。

    Args:
        task_id (int): 需要标记为完成的任务的ID (从0开始)。
        result (str): 描述任务完成结果或产出的字符串。
    """
    return plan_manager.completeTask(task_id, result)

@mcp.tool()
def failTask(task_id: int, error_message: str, should_retry: bool = True) -> ToolResponse[TaskOutput]:
    """
    将指定ID的任务标记为 'failed' (失败)。

    Args:
        task_id (int): 需要标记为失败的任务的ID (从0开始)。
        error_message (str): 描述任务失败原因的字符串。
        should_retry (bool, optional): 是否应该重试该任务的标志。默认为 True。
    """
    return plan_manager.failTask(task_id, error_message, should_retry)

@mcp.tool()
def addTask(name: str, dependencies: List[int], reasoning: str, after_task_id: Optional[int] = None) -> ToolResponse[TaskOutput]:
    """
    向当前计划中动态添加一个新任务。

    Args:
        name (str): 新任务的名称，应确保唯一性。
        dependencies (List[int]): 新任务所依赖的任务ID的整数列表 (从0开始)。
        reasoning (str): 解释为何要添加此任务的字符串。
        after_task_id (int, optional): 一个任务ID，新任务将被插入到该任务之后。如果省略，则添加到列表末尾。
        
    Returns:
        ToolResponse[TaskOutput]: 包含新创建任务的响应对象。
    """
    return plan_manager.addTask(name, dependencies, reasoning, after_task_id)

@mcp.tool()
def skipTask(task_id: int, reason: str) -> ToolResponse[TaskOutput]:
    """
    将指定ID的任务标记为 'skipped' (已跳过)。
    被跳过的任务在依赖解析中被视为“已完成”，允许后续任务继续。

    Args:
        task_id (int): 需要跳过的任务的ID (从0开始)。
        reason (str): 解释为何跳过此任务的字符串。
    """
    return plan_manager.skipTask(task_id, reason)

@mcp.tool()
def editDependencies(edits: List[DependencyEdit]) -> ToolResponse[dict]:
    """
    以批量、事务性的方式编辑一个或多个任务的依赖关系。

    此工具允许 'set' 或 'update' 操作，所有编辑将在应用前进行全面验证。
    如果任何指令失败，整个操作将回滚。

    Args:
        edits (List[DependencyEdit]): 一个包含编辑指令对象的列表，每个对象都应符合 DependencyEdit 模型。
    """
    edit_dicts = [edit.model_dump(exclude_none=True) for edit in edits]
    return plan_manager.edit_dependencies_in_batch(edit_dicts)

@mcp.tool()
def getPlanStatus() -> ToolResponse[PlanStatusData]:
    """获取整个计划的全面概览，包括元数据、进度、任务状态统计等。"""
    return plan_manager.getPlanStatus()

@mcp.tool()
def getTaskList(status_filter: Optional[str] = None) -> ToolResponse[List[TaskOutput]]:
    """
    获取计划中所有任务的列表，可按状态进行过滤。

    Args:
        status_filter (str, optional): 用于过滤任务的状态字符串。
                                     可接受的值: 'pending', 'in_progress', 'completed', 'failed', 'skipped'。
    
    Returns:
          ToolResponse[List[TaskOutput]]: 包含任务列表的响应对象。
    """
    return plan_manager.getTaskList(status_filter)

@mcp.tool()
def getExecutableTaskList() -> ToolResponse[List[TaskOutput]]:
    """
    获取当前所有依赖已满足且状态为 'pending' 的可执行任务列表。

    Returns:
        ToolResponse[List[TaskOutput]]: 包含可执行任务列表的响应对象。
    """
    return plan_manager.getExecutableTaskList()

@mcp.tool()
def generateContextPrompt() -> str:
    """
    生成一个详细的文本提示，总结计划的当前状态。
    这个提示可以作为上下文提供给AI模型，以帮助其决定下一步行动。
    内容包括：总体目标、当前任务、可执行任务列表等。
    """
    from .dependency_tools import DependencyPromptGenerator
    generator = DependencyPromptGenerator(plan_manager)
    prompt = generator.generate_context_prompt()
    return prompt


def main():
    """
    The main entry point for running the server via the 'mcplanmanager' script.
    """
    # 检查环境变量来决定运行模式
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8080"))
    
    if transport == "sse":
        print(f"Starting MCP server in SSE mode on {host}:{port}")
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "http":
        print(f"Starting MCP server in HTTP mode on {host}:{port}")
        mcp.run(transport="http", host=host, port=port)
    else:
        print("Starting MCP server in STDIO mode")
        mcp.run()

if __name__ == "__main__":
    main()

