import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from copy import deepcopy


class PlanManager:
    """
    PlanManager - 简洁高效的任务管理器
    专为 AI Agent 的长程任务执行而设计
    
    使用纯内存模式，适用于托管环境和无文件系统权限的场景
    """
    
    def __init__(self, initial_plan_data: Optional[Dict] = None):
        """
        初始化PlanManager（纯内存模式）
        
        Args:
            initial_plan_data: 初始计划数据（可选）
        """
        # 使用提供的数据或创建默认数据
        self.plan_data = initial_plan_data if initial_plan_data else self._create_empty_plan()
    
    def _create_empty_plan(self) -> Dict:
        """创建空的计划数据结构"""
        return {
            "meta": {
                "goal": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "state": {
                "current_task_id": None,
                "status": "idle"
            },
            "tasks": []
        }
    
    def _update_timestamp(self) -> None:
        """更新时间戳"""
        self.plan_data["meta"]["updated_at"] = datetime.now().isoformat()
    
    def _get_next_task_id(self) -> int:
        """获取下一个任务ID"""
        if not self.plan_data["tasks"]:
            return 1
        return max(task["id"] for task in self.plan_data["tasks"]) + 1
    
    def _find_task_by_id(self, task_id: int) -> Optional[Dict]:
        """根据ID查找任务"""
        for task in self.plan_data["tasks"]:
            if task["id"] == task_id:
                return task
        return None
    
    def _check_dependencies_satisfied(self, task: Dict) -> bool:
        """检查任务的依赖是否已满足"""
        for dep_id in task["dependencies"]:
            dep_task = self._find_task_by_id(dep_id)
            if not dep_task or dep_task["status"] != "completed":
                return False
        return True
    
    def _detect_circular_dependency(self, task_id: int, dependencies: List[int], tasks_list: List[Dict] = None) -> bool:
        """检测循环依赖"""
        # 使用提供的任务列表或者当前计划的任务列表
        tasks_to_check = tasks_list if tasks_list is not None else self.plan_data["tasks"]
        
        def find_task_in_list(tid: int) -> Optional[Dict]:
            for task in tasks_to_check:
                if task["id"] == tid:
                    return task
            return None
        
        def has_path(from_id: int, to_id: int, visited: set) -> bool:
            if from_id == to_id:
                return True
            if from_id in visited:
                return False
            
            visited.add(from_id)
            task = find_task_in_list(from_id)
            if task:
                for dep_id in task["dependencies"]:
                    if has_path(dep_id, to_id, visited.copy()):
                        return True
            return False
        
        for dep_id in dependencies:
            if has_path(dep_id, task_id, set()):
                return True
        return False
    
    def _success_response(self, data: Any, message: str = "") -> Dict:
        """构造成功响应"""
        return {
            "success": True,
            "data": data
        }
    
    def _error_response(self, code: str, message: str, details: Any = None) -> Dict:
        """构造错误响应"""
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }
    
    # 核心流程函数
    
    def getCurrentTask(self) -> Dict:
        """获取当前正在执行的任务"""
        current_id = self.plan_data["state"]["current_task_id"]
        if current_id is None:
            return self._error_response("NO_CURRENT_TASK", "No task is currently active")
        
        task = self._find_task_by_id(current_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Current task {current_id} not found")
        
        return self._success_response(task)
    
    def startNextTask(self) -> Dict:
        """自动开始下一个可执行的任务"""
        # 查找可执行的任务
        executable_tasks = []
        for task in self.plan_data["tasks"]:
            if (task["status"] == "pending" and 
                self._check_dependencies_satisfied(task)):
                executable_tasks.append(task)
        
        if not executable_tasks:
            return self._error_response("NO_EXECUTABLE_TASK", "No executable tasks available")
        
        # 选择第一个可执行的任务
        next_task = executable_tasks[0]
        next_task["status"] = "in_progress"
        self.plan_data["state"]["current_task_id"] = next_task["id"]
        self.plan_data["state"]["status"] = "running"
        
        self._update_timestamp()
        
        return self._success_response({
            "task": next_task,
            "message": f"Started task {next_task['id']}: {next_task['name']}"
        })
    
    def completeTask(self, task_id: int, result: str) -> Dict:
        """标记任务为完成状态"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        if task["status"] != "in_progress":
            return self._error_response("INVALID_STATUS", f"Task {task_id} is not in progress")
        
        task["status"] = "completed"
        task["result"] = result
        
        # 如果这是当前任务，清除当前任务ID
        if self.plan_data["state"]["current_task_id"] == task_id:
            self.plan_data["state"]["current_task_id"] = None
            
            # 检查是否所有任务都完成了
            all_completed = all(
                task["status"] in ["completed", "skipped"] 
                for task in self.plan_data["tasks"]
            )
            if all_completed:
                self.plan_data["state"]["status"] = "completed"
        
        self._update_timestamp()
        
        return self._success_response({
            "task_id": task_id,
            "message": "Task completed successfully"
        })
    
    def failTask(self, task_id: int, error_message: str, should_retry: bool = True) -> Dict:
        """标记任务失败"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        task["status"] = "failed"
        task["result"] = error_message
        
        # 如果这是当前任务，清除当前任务ID
        if self.plan_data["state"]["current_task_id"] == task_id:
            self.plan_data["state"]["current_task_id"] = None
        
        self._update_timestamp()
        
        return self._success_response({
            "task_id": task_id,
            "will_retry": should_retry,
            "message": f"Task failed: {error_message}"
        })
    
    # 任务管理函数
    
    def addTask(self, name: str, dependencies: List[int], reasoning: str, 
                after_task_id: Optional[int] = None) -> Dict:
        """添加新任务到计划中"""
        # 验证依赖任务存在
        for dep_id in dependencies:
            if not self._find_task_by_id(dep_id):
                return self._error_response("INVALID_DEPENDENCY", 
                                          f"Dependency task {dep_id} not found")
        
        new_id = self._get_next_task_id()
        
        # 检测循环依赖
        if self._detect_circular_dependency(new_id, dependencies):
            return self._error_response("CIRCULAR_DEPENDENCY", 
                                      "Adding this task would create circular dependency")
        
        new_task = {
            "id": new_id,
            "name": name,
            "status": "pending",
            "dependencies": dependencies,
            "reasoning": reasoning,
            "result": None
        }
        
        # 插入任务
        if after_task_id is None:
            self.plan_data["tasks"].append(new_task)
        else:
            # 找到插入位置
            insert_index = len(self.plan_data["tasks"])
            for i, task in enumerate(self.plan_data["tasks"]):
                if task["id"] == after_task_id:
                    insert_index = i + 1
                    break
            
            self.plan_data["tasks"].insert(insert_index, new_task)
            
            # 更新后续任务的依赖关系
            for task in self.plan_data["tasks"][insert_index + 1:]:
                if after_task_id in task["dependencies"]:
                    task["dependencies"] = [
                        new_id if dep_id == after_task_id else dep_id 
                        for dep_id in task["dependencies"]
                    ]
                    task["dependencies"].append(after_task_id)
        
        self._update_timestamp()
        
        return self._success_response({
            "new_task": new_task,
            "message": "Task added successfully"
        })
    
    def updateTask(self, task_id: int, updates: Dict) -> Dict:
        """更新任务信息"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        if task["status"] not in ["pending"]:
            return self._error_response("TASK_NOT_EDITABLE", 
                                      f"Task {task_id} cannot be edited in {task['status']} status")
        
        # 更新字段
        for key, value in updates.items():
            if key in ["name", "reasoning"]:
                task[key] = value
            elif key == "dependencies":
                # 验证新依赖
                for dep_id in value:
                    if not self._find_task_by_id(dep_id):
                        return self._error_response("INVALID_DEPENDENCY", 
                                                  f"Dependency task {dep_id} not found")
                
                # 检测循环依赖
                if self._detect_circular_dependency(task_id, value):
                    return self._error_response("CIRCULAR_DEPENDENCY", 
                                              "Update would create circular dependency")
                
                task["dependencies"] = value
        
        self._update_timestamp()
        
        return self._success_response({
            "updated_task": task,
            "message": "Task updated successfully"
        })
    
    def skipTask(self, task_id: int, reason: str) -> Dict:
        """跳过指定任务"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        task["status"] = "skipped"
        task["result"] = reason
        
        # 如果这是当前任务，清除当前任务ID
        if self.plan_data["state"]["current_task_id"] == task_id:
            self.plan_data["state"]["current_task_id"] = None
        
        self._update_timestamp()
        
        return self._success_response({
            "task_id": task_id,
            "message": f"Task skipped: {reason}"
        })
    
    def removeTask(self, task_id: int) -> Dict:
        """删除任务（仅限pending状态）"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        if task["status"] != "pending":
            return self._error_response("TASK_NOT_REMOVABLE", 
                                      f"Only pending tasks can be removed")
        
        # 检查是否有其他任务依赖此任务
        dependent_tasks = []
        for t in self.plan_data["tasks"]:
            if task_id in t["dependencies"]:
                dependent_tasks.append(t["id"])
        
        if dependent_tasks:
            return self._error_response("TASK_HAS_DEPENDENTS", 
                                      f"Task {task_id} has dependent tasks: {dependent_tasks}")
        
        # 移除任务
        self.plan_data["tasks"] = [t for t in self.plan_data["tasks"] if t["id"] != task_id]
        
        self._update_timestamp()
        
        return self._success_response({
            "task_id": task_id,
            "message": "Task removed successfully"
        })
    
    # 查询函数
    
    def getTaskList(self, status_filter: Optional[str] = None) -> Dict:
        """获取任务列表"""
        tasks = self.plan_data["tasks"]
        
        if status_filter:
            filtered_tasks = [t for t in tasks if t["status"] == status_filter]
        else:
            filtered_tasks = tasks
        
        return self._success_response({
            "tasks": filtered_tasks,
            "total": len(tasks),
            "filtered": len(filtered_tasks)
        })
    
    def getPlanStatus(self) -> Dict:
        """获取完整的计划状态和数据"""
        tasks = self.plan_data["tasks"]
        total_tasks = len(tasks)
        
        # 统计任务状态
        status_counts = {}
        for task in tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 计算进度
        completed_count = status_counts.get("completed", 0) + status_counts.get("skipped", 0)
        progress = completed_count / total_tasks if total_tasks > 0 else 0.0
        
        # 返回完整的计划信息
        return self._success_response({
            # 基本信息
            "goal": self.plan_data["meta"]["goal"],
            "created_at": self.plan_data["meta"]["created_at"],
            "updated_at": self.plan_data["meta"]["updated_at"],
            
            # 状态信息
            "status": self.plan_data["state"]["status"],
            "current_task_id": self.plan_data["state"]["current_task_id"],
            
            # 统计信息
            "total_tasks": total_tasks,
            "completed_tasks": status_counts.get("completed", 0),
            "failed_tasks": status_counts.get("failed", 0),
            "pending_tasks": status_counts.get("pending", 0),
            "in_progress_tasks": status_counts.get("in_progress", 0),
            "skipped_tasks": status_counts.get("skipped", 0),
            
            # 进度信息
            "progress": progress,
            "is_completed": self.plan_data["state"]["status"] == "completed",
            "has_failures": status_counts.get("failed", 0) > 0,
            
            # 完整的计划数据（供高级用户使用）
            "plan_data": deepcopy(self.plan_data)
        })
    
    def getTaskById(self, task_id: int) -> Dict:
        """根据ID获取任务详情"""
        task = self._find_task_by_id(task_id)
        if not task:
            return self._error_response("TASK_NOT_FOUND", f"Task {task_id} not found")
        
        return self._success_response({"task": task})
    
    def getExecutableTaskList(self) -> Dict:
        """获取当前可执行的任务列表"""
        executable_tasks = []
        for task in self.plan_data["tasks"]:
            if (task["status"] == "pending" and 
                self._check_dependencies_satisfied(task)):
                executable_tasks.append(task)
        
        return self._success_response({
            "executable_tasks": executable_tasks,
            "count": len(executable_tasks)
        })
    
    # 控制函数
    
    def pausePlan(self) -> Dict:
        """暂停整个计划"""
        self.plan_data["state"]["status"] = "paused"
        self._update_timestamp()
        
        return self._success_response({
            "message": "Plan paused successfully"
        })
    
    def resumePlan(self) -> Dict:
        """恢复计划执行"""
        if self.plan_data["state"]["status"] == "paused":
            self.plan_data["state"]["status"] = "running"
            self._update_timestamp()
            
            return self._success_response({
                "message": "Plan resumed successfully"
            })
        else:
            return self._error_response("INVALID_STATUS", 
                                      "Plan is not in paused status")
    
    def resetPlan(self) -> Dict:
        """重置计划（将所有任务状态重置为pending）"""
        reset_count = 0
        for task in self.plan_data["tasks"]:
            if task["status"] != "pending":
                task["status"] = "pending"
                task["result"] = None
                reset_count += 1
        
        self.plan_data["state"]["current_task_id"] = None
        self.plan_data["state"]["status"] = "idle"
        
        self._update_timestamp()
        
        return self._success_response({
            "message": "Plan reset successfully",
            "reset_tasks": reset_count
        })
    
    # 工具函数
    
    def initializePlan(self, goal: str, tasks: List[Dict]) -> Dict:
        """
        初始化计划
        
        AI模型只需要提供业务内容：
        - goal: 计划目标
        - tasks: 任务列表，每个任务包含：
          - name: 任务名称
          - reasoning: 执行理由
          - dependencies: 依赖的任务（可以是任务名称列表或索引列表）
        
        工具自动维护：
        - id: 从1开始自动分配
        - status: 初始为"pending"
        - result: 初始为None
        - created_at/updated_at: 自动设置时间戳
        """
        if not tasks:
            return self._error_response("INVALID_INPUT", "At least one task is required")
        
        current_time = datetime.now().isoformat()
        
        # 重置计划数据
        self.plan_data = {
            "meta": {
                "goal": goal,
                "created_at": current_time,
                "updated_at": current_time
            },
            "state": {
                "current_task_id": None,
                "status": "idle"
            },
            "tasks": []
        }
        
        # 处理任务列表
        processed_tasks = []
        task_name_to_id = {}  # 用于处理名称依赖
        
        # 第一遍：创建任务并建立名称映射
        for i, task_input in enumerate(tasks):
            if not isinstance(task_input, dict):
                return self._error_response("INVALID_TASK_FORMAT", 
                                          f"Task {i+1} must be a dictionary")
            
            if "name" not in task_input:
                return self._error_response("MISSING_FIELD", 
                                          f"Task {i+1} is missing required field 'name'")
            
            task_id = i + 1
            task_name = task_input["name"]
            task_name_to_id[task_name] = task_id
            
            processed_task = {
                "id": task_id,
                "name": task_name,
                "status": "pending",
                "dependencies": [],  # 先设为空，第二遍处理
                "reasoning": task_input.get("reasoning", f"Execute task: {task_name}"),
                "result": None
            }
            
            processed_tasks.append(processed_task)
        
        # 第二遍：处理依赖关系
        for i, task_input in enumerate(tasks):
            dependencies = task_input.get("dependencies", [])
            processed_dependencies = []
            
            for dep in dependencies:
                if isinstance(dep, str):
                    # 依赖是任务名称
                    if dep in task_name_to_id:
                        processed_dependencies.append(task_name_to_id[dep])
                    else:
                        return self._error_response("INVALID_DEPENDENCY", 
                                                  f"Task '{processed_tasks[i]['name']}' depends on unknown task '{dep}'")
                elif isinstance(dep, int):
                    # 依赖是任务索引（1-based）
                    if 1 <= dep <= len(tasks):
                        processed_dependencies.append(dep)
                    else:
                        return self._error_response("INVALID_DEPENDENCY", 
                                                  f"Task {i+1} has invalid dependency index {dep}")
                else:
                    return self._error_response("INVALID_DEPENDENCY_TYPE", 
                                              f"Dependencies must be task names (strings) or indices (integers)")
            
            processed_tasks[i]["dependencies"] = processed_dependencies
        
        # 检测循环依赖
        for task in processed_tasks:
            if self._detect_circular_dependency(task["id"], task["dependencies"], processed_tasks):
                return self._error_response("CIRCULAR_DEPENDENCY", 
                                          f"Circular dependency detected involving task '{task['name']}'")
        
        self.plan_data["tasks"] = processed_tasks
        self._update_timestamp()
        
        return self._success_response({
            "message": "Plan initialized successfully",
            "goal": goal,
            "task_count": len(processed_tasks),
            "tasks": processed_tasks
        })
    
    def exportPlan(self) -> Dict:
        """导出计划数据"""
        return self._success_response(deepcopy(self.plan_data))
    
    def getDependencyGraph(self) -> Dict:
        """获取依赖关系图数据"""
        nodes = []
        edges = []
        
        for task in self.plan_data["tasks"]:
            nodes.append({
                "id": task["id"],
                "name": task["name"],
                "status": task["status"]
            })
            
            for dep_id in task["dependencies"]:
                edges.append({
                    "from": dep_id,
                    "to": task["id"]
                })
        
        return self._success_response({
            "nodes": nodes,
            "edges": edges
        }) 