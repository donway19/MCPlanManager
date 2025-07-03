#!/usr/bin/env python3
"""
PlanManager HTTP API服务器
基于FastAPI提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from mcp_wrapper import PlanManagerWrapper, get_tool_definitions

app = FastAPI(
    title="PlanManager API",
    description="AI Agent任务管理系统API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}

class InitializePlanRequest(BaseModel):
    goal: str
    initial_tasks: Optional[List[Dict[str, Any]]] = None
    plan_file: Optional[str] = "plan.json"

class TaskRequest(BaseModel):
    task_id: int
    plan_file: Optional[str] = "plan.json"

class CompleteTaskRequest(BaseModel):
    task_id: int
    result: str
    plan_file: Optional[str] = "plan.json"

class FailTaskRequest(BaseModel):
    task_id: int
    error_message: str
    should_retry: bool = True
    plan_file: Optional[str] = "plan.json"

class AddTaskRequest(BaseModel):
    name: str
    dependencies: List[int]
    reasoning: str
    after_task_id: Optional[int] = None
    plan_file: Optional[str] = "plan.json"

class SkipTaskRequest(BaseModel):
    task_id: int
    reason: str
    plan_file: Optional[str] = "plan.json"

# 全局包装器实例
wrapper = PlanManagerWrapper()

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "PlanManager API",
        "version": "1.0.0",
        "description": "AI Agent任务管理系统"
    }

@app.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    return get_tool_definitions()

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """执行工具调用"""
    try:
        result = wrapper.execute_tool(request.tool_name, request.arguments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 核心流程API
@app.get("/current-task")
async def get_current_task(plan_file: str = "plan.json"):
    """获取当前任务"""
    result = wrapper.execute_tool("getCurrentTask", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/start-next-task")
async def start_next_task(plan_file: str = "plan.json"):
    """开始下一个任务"""
    result = wrapper.execute_tool("startNextTask", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/complete-task")
async def complete_task(request: CompleteTaskRequest):
    """完成任务"""
    result = wrapper.execute_tool("completeTask", request.dict())
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/fail-task")
async def fail_task(request: FailTaskRequest):
    """任务失败"""
    result = wrapper.execute_tool("failTask", request.dict())
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

# 任务管理API
@app.post("/add-task")
async def add_task(request: AddTaskRequest):
    """添加任务"""
    result = wrapper.execute_tool("addTask", request.dict())
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/skip-task")
async def skip_task(request: SkipTaskRequest):
    """跳过任务"""
    result = wrapper.execute_tool("skipTask", request.dict())
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

# 查询API
@app.get("/tasks")
async def get_tasks(plan_file: str = "plan.json", status_filter: Optional[str] = None):
    """获取任务列表"""
    args = {"plan_file": plan_file}
    if status_filter:
        args["status_filter"] = status_filter
    
    result = wrapper.execute_tool("getTaskList", args)
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/status")
async def get_plan_status(plan_file: str = "plan.json"):
    """获取计划状态"""
    result = wrapper.execute_tool("getPlanStatus", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/executable-tasks")
async def get_executable_tasks(plan_file: str = "plan.json"):
    """获取可执行任务"""
    result = wrapper.execute_tool("getExecutableTaskList", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

# 工具API
@app.post("/initialize")
async def initialize_plan(request: InitializePlanRequest):
    """初始化计划"""
    result = wrapper.execute_tool("initializePlan", request.dict())
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/visualize")
async def visualize_dependencies(
    plan_file: str = "plan.json", 
    format: str = "ascii"
):
    """可视化依赖关系"""
    result = wrapper.execute_tool("visualizeDependencies", {
        "plan_file": plan_file,
        "format": format
    })
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/context-prompt")
async def generate_context_prompt(plan_file: str = "plan.json"):
    """生成上下文提示词"""
    result = wrapper.execute_tool("generateContextPrompt", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/next-action-prompt")
async def generate_next_action_prompt(plan_file: str = "plan.json"):
    """生成下一步行动提示词"""
    result = wrapper.execute_tool("generateNextActionPrompt", {"plan_file": plan_file})
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)