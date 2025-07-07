from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional, TypeVar, Generic

T = TypeVar('T')

class ToolResponse(BaseModel, Generic[T]):
    """
    一个通用的工具响应模型，用于标准化所有工具的返回结构。
    """
    success: bool = Field(True, description="操作是否成功。")
    message: Optional[str] = Field(None, description="关于操作结果的可读消息。")
    data: Optional[T] = Field(None, description="操作返回的主要数据负载。")

class TaskInput(BaseModel):
    """
    用于初始化计划时，定义单个任务输入的Pydantic模型。
    这为Agent提供了一个清晰、可验证的数据结构。
    """
    name: str
    dependencies: List[Union[str, int]]
    reasoning: str

class DependencyEdit(BaseModel):
    """
    用于editDependencies工具，定义单个依赖编辑操作的模型。
    """
    task_id: int = Field(..., description="要修改的任务ID。")
    action: Literal["set", "update"] = Field(..., description="要执行的操作：'set' 或 'update'。")
    dependencies: Optional[List[int]] = Field(default=None, description="当action为'set'时，提供新的完整依赖ID列表。")
    add: Optional[List[int]] = Field(default=None, description="当action为'update'时，提供要添加的依赖ID列表。")
    remove: Optional[List[int]] = Field(default=None, description="当action为'update'时，提供要移除的依赖ID列表。")

class TaskOutput(BaseModel):
    """
    用于工具函数返回任务信息时，定义单个任务输出的Pydantic模型。
    """
    id: int
    name: str
    status: str
    dependencies: List[int]
    reasoning: str
    result: Optional[str] = None

class PlanStatusMeta(BaseModel):
    goal: str
    created_at: str
    updated_at: str

class PlanStatusState(BaseModel):
    current_task_id: Optional[int]
    status: str

class PlanProgress(BaseModel):
    completed_tasks: int
    total_tasks: int
    progress_percentage: float

class PlanTaskCounts(BaseModel):
    pending: int
    in_progress: int
    completed: int
    failed: int
    skipped: int
    total: int

class PlanStatusData(BaseModel):
    """
    用于getPlanStatus工具，定义其返回数据的详细模型。
    """
    meta: PlanStatusMeta
    state: PlanStatusState
    progress: PlanProgress
    task_counts: PlanTaskCounts 