from fastmcp import FastMCP
from .plan_manager import PlanManager

mcp = FastMCP("MCPlanManager")

plan_manager = PlanManager()

@mcp.tool()
def initializePlan(goal: str, tasks: list) -> dict:
    """Initializes a new task plan."""
    return plan_manager.initializePlan(goal, tasks)

@mcp.tool()
def getCurrentTask() -> dict:
    """Gets the currently executing task."""
    return plan_manager.getCurrentTask()

@mcp.tool()
def startNextTask() -> dict:
    """Starts the next executable task."""
    return plan_manager.startNextTask()

@mcp.tool()
def completeTask(task_id: int, result: str) -> dict:
    """Marks a task as complete."""
    return plan_manager.completeTask(task_id, result)

@mcp.tool()
def failTask(task_id: int, error_message: str, should_retry: bool = True) -> dict:
    """Marks a task as failed."""
    return plan_manager.failTask(task_id, error_message, should_retry)

@mcp.tool()
def addTask(name: str, dependencies: list, reasoning: str, after_task_id: int = None) -> dict:
    """Adds a new task to the plan."""
    return plan_manager.addTask(name, dependencies, reasoning, after_task_id)

@mcp.tool()
def skipTask(task_id: int, reason: str) -> dict:
    """Skips a specified task."""
    return plan_manager.skipTask(task_id, reason)

@mcp.tool()
def getPlanStatus() -> dict:
    """Gets the status of the entire plan."""
    return plan_manager.getPlanStatus()

@mcp.tool()
def getTaskList(status_filter: str = None) -> dict:
    """Gets a list of tasks, with an optional status filter."""
    return plan_manager.getTaskList(status_filter)

@mcp.tool()
def getExecutableTaskList() -> dict:
    """Gets a list of tasks that are ready to be executed."""
    return plan_manager.getExecutableTaskList()

@mcp.tool()
def visualizeDependencies(format: str = "ascii") -> dict:
    """Generates a visualization of the task dependencies."""
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
    return {"success": True, "data": {"visualization": visualization}}

@mcp.tool()
def generateContextPrompt() -> dict:
    """Generates a context-aware prompt for execution."""
    from .dependency_tools import DependencyPromptGenerator
    generator = DependencyPromptGenerator(plan_manager)
    prompt = generator.generate_context_prompt()
    return {"success": True, "data": {"prompt": prompt}}

def main():
    mcp.run()

if __name__ == "__main__":
    main()