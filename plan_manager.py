import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from copy import deepcopy


class PlanManager:
    """
    PlanManager - 简洁高效的任务管理器
    专为 AI Agent 的长程任务执行而设计
    """
    
    def __init__(self, plan_file: str = "plan.json"):
        """
        初始化PlanManager
        
        Args:
            plan_file: 计划文件路径
        """
        self.plan_file = plan_file
        self.plan_data = self._load_or_create_plan()
    
    def _load_or_create_plan(self) -> Dict:
        """加载或创建计划文件"""
        if os.path.exists(self.plan_file):
            try:
                with open(self.plan_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 创建默认计划结构
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
    
    def _save_plan(self) -> None:
        """保存计划到文件"""
        self.plan_data["meta"]["updated_at"] = datetime.now().isoformat()
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            json.dump(self.plan_data, f, ensure_ascii=False, indent=2)
    
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
    
    def _detect_circular_dependency(self, task_id: int, dependencies: List[int]) -> bool:
        """检测循环依赖"""
        def has_path(from_id: int, to_id: int, visited: set) -> bool:
            if from_id == to_id:
                return True
            if from_id in visited:
                return False
            
            visited.add(from_id)
            task = self._find_task_by_id(from_id)
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        
        self._save_plan()
        
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
        """获取整个计划的状态"""
        tasks = self.plan_data["tasks"]
        total_tasks = len(tasks)
        
        status_counts = {}
        for task in tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return self._success_response({
            "status": self.plan_data["state"]["status"],
            "current_task_id": self.plan_data["state"]["current_task_id"],
            "total_tasks": total_tasks,
            "completed_tasks": status_counts.get("completed", 0),
            "failed_tasks": status_counts.get("failed", 0),
            "pending_tasks": status_counts.get("pending", 0),
            "in_progress_tasks": status_counts.get("in_progress", 0),
            "skipped_tasks": status_counts.get("skipped", 0)
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
        self._save_plan()
        
        return self._success_response({
            "message": "Plan paused successfully"
        })
    
    def resumePlan(self) -> Dict:
        """恢复计划执行"""
        if self.plan_data["state"]["status"] == "paused":
            self.plan_data["state"]["status"] = "running"
            self._save_plan()
            
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
        
        self._save_plan()
        
        return self._success_response({
            "message": "Plan reset successfully",
            "reset_tasks": reset_count
        })
    
    # 工具函数
    
    def initializePlan(self, goal: str, initial_tasks: List[Dict] = None) -> Dict:
        """初始化计划"""
        self.plan_data["meta"]["goal"] = goal
        self.plan_data["meta"]["created_at"] = datetime.now().isoformat()
        self.plan_data["tasks"] = initial_tasks or []
        self.plan_data["state"]["status"] = "idle"
        self.plan_data["state"]["current_task_id"] = None
        
        self._save_plan()
        
        return self._success_response({
            "message": "Plan initialized successfully",
            "goal": goal,
            "task_count": len(self.plan_data["tasks"])
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