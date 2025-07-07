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
        """获取下一个任务ID（从0开始）"""
        if not self.plan_data["tasks"]:
            return 0
        return max(task["id"] for task in self.plan_data["tasks"]) + 1
    
    def _find_task_by_id(self, task_id: int) -> Optional[Dict]:
        """根据ID查找任务"""
        for task in self.plan_data["tasks"]:
            if task["id"] == task_id:
                return task
        return None
    
    def _check_dependencies_satisfied(self, task: Dict) -> bool:
        """检查任务的依赖是否已满足（已完成或已跳过）"""
        for dep_id in task["dependencies"]:
            dep_task = self._find_task_by_id(dep_id)
            if not dep_task or dep_task["status"] not in ["completed", "skipped"]:
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
    
    
    
    # 核心流程函数
    
    def getCurrentTask(self) -> Dict:
        """获取当前正在执行的任务"""
        current_id = self.plan_data["state"]["current_task_id"]
        if current_id is None:
            return {"success": False, "message": "No task is currently active"}
        
        task = self._find_task_by_id(current_id)
        if not task:
            return {"success": False, "message": f"Current task {current_id} not found"}
        
        return {"success": True, "data": task}
    
    def startNextTask(self) -> Dict:
        """自动开始下一个可执行的任务"""
        # 查找可执行的任务
        executable_tasks = []
        for task in self.plan_data["tasks"]:
            if (task["status"] == "pending" and 
                self._check_dependencies_satisfied(task)):
                executable_tasks.append(task)
        
        if not executable_tasks:
            return {"success": False, "message": "No executable tasks available", "data": None}
        
        # 选择第一个可执行的任务
        next_task = executable_tasks[0]
        next_task["status"] = "in_progress"
        self.plan_data["state"]["current_task_id"] = next_task["id"]
        self.plan_data["state"]["status"] = "running"
        
        self._update_timestamp()
        
        return {
            "success": True,
            "data": next_task,
            "message": f"Started task {next_task['id']}: {next_task['name']}"
        }
    
    def completeTask(self, task_id: int, result: str) -> Dict:
        """标记任务为完成状态"""
        task = self._find_task_by_id(task_id)
        if not task:
            return {"success": False, "message": f"Task {task_id} not found", "data": None}
        
        if task["status"] != "in_progress":
            return {"success": False, "message": f"Task {task_id} is not in progress", "data": None}
        
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
        
        return {
            "success": True,
            "data": task,
            "message": "Task completed successfully"
        }
    
    def failTask(self, task_id: int, error_message: str, should_retry: bool = True) -> Dict:
        """标记任务失败"""
        task = self._find_task_by_id(task_id)
        if not task:
            return {"success": False, "message": f"Task {task_id} not found", "data": None}
        
        task["status"] = "failed"
        task["result"] = error_message
        
        # 如果这是当前任务，清除当前任务ID
        if self.plan_data["state"]["current_task_id"] == task_id:
            self.plan_data["state"]["current_task_id"] = None
        
        self._update_timestamp()
        
        return {
            "success": True,
            "data": task,
            "message": f"Task failed: {error_message}"
        }
    
    # 任务管理函数
    
    def addTask(self, name: str, dependencies: List[int], reasoning: str, 
                after_task_id: Optional[int] = None) -> Dict:
        """添加新任务到计划中"""
        # 验证依赖任务存在
        for dep_id in dependencies:
            if not self._find_task_by_id(dep_id):
                return {"success": False, "message": f"Dependency task {dep_id} not found"}
        
        new_id = self._get_next_task_id()
        
        # 检测循环依赖
        if self._detect_circular_dependency(new_id, dependencies):
            return {"success": False, "message": "Circular dependency detected"}
            
        new_task = {
            "id": new_id,
            "name": name,
            "status": "pending",
            "dependencies": dependencies,
            "reasoning": reasoning,
            "result": None
        }
        
        # 插入任务
        if after_task_id is not None:
            try:
                # 寻找插入位置
                insert_index = next(i for i, task in enumerate(self.plan_data["tasks"]) if task["id"] == after_task_id) + 1
                self.plan_data["tasks"].insert(insert_index, new_task)
            except StopIteration:
                return {"success": False, "message": f"Task with id {after_task_id} not found"}
        else:
            self.plan_data["tasks"].append(new_task)
            
        self._update_timestamp()
        
        return {
            "success": True,
            "data": new_task,
            "message": "Task added successfully"
        }
    
    def updateTask(self, task_id: int, updates: Dict) -> Dict:
        """更新任务信息"""
        task = self = self._find_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task["status"] not in ["pending"]:
            raise ValueError(f"Task {task_id} cannot be edited in {task['status']} status")
        
        # 更新字段
        for key, value in updates.items():
            if key in ["name", "reasoning"]:
                task[key] = value
            elif key == "dependencies":
                # 验证新依赖
                for dep_id in value:
                    if not self._find_task_by_id(dep_id):
                        raise ValueError(f"Dependency task {dep_id} not found")
                
                # 检测循环依赖
                if self._detect_circular_dependency(task_id, value):
                    raise ValueError("Update would create circular dependency")
                
                task["dependencies"] = value
        
        self._update_timestamp()
        
        return {
            "updated_task": task,
            "message": "Task updated successfully"
        }
    
    def skipTask(self, task_id: int, reason: str) -> Dict:
        """跳过任务"""
        task = self._find_task_by_id(task_id)
        if not task:
            return {"success": False, "message": f"Task {task_id} not found"}
        
        if task["status"] not in ["pending", "failed"]:
             return {"success": False, "message": f"Only pending or failed tasks can be skipped. Task {task_id} has status '{task['status']}'"}
        
        task["status"] = "skipped"
        task["result"] = f"Skipped: {reason}"
        
        self._update_timestamp()
        
        return {
            "success": True,
            "data": task,
            "message": f"Task {task_id} skipped. Reason: {reason}"
        }
    
    def removeTask(self, task_id: int) -> Dict:
        """删除任务（仅限pending状态）"""
        task = self._find_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task["status"] != "pending":
            raise ValueError(f"Only pending tasks can be removed")
        
        # 检查是否有其他任务依赖此任务
        dependent_tasks = []
        for t in self.plan_data["tasks"]:
            if task_id in t["dependencies"]:
                dependent_tasks.append(t["id"])
        
        if dependent_tasks:
            raise ValueError(f"Task {task_id} has dependent tasks: {dependent_tasks}")
        
        # 移除任务
        self.plan_data["tasks"] = [t for t in self.plan_data["tasks"] if t["id"] != task_id]
        
        self._update_timestamp()
        
        return {
            "task_id": task_id,
            "message": "Task removed successfully"
        }
    
    # 查询函数
    
    def getTaskList(self, status_filter: Optional[str] = None) -> Dict:
        """获取任务列表，可按状态过滤"""
        if status_filter:
            tasks_to_return = [
                task for task in self.plan_data["tasks"] 
                if task["status"] == status_filter
            ]
        else:
            tasks_to_return = self.plan_data["tasks"]
        
        return {"success": True, "data": tasks_to_return}
    
    def getPlanStatus(self) -> Dict:
        """获取计划状态"""
        total_tasks = len(self.plan_data["tasks"])
        if total_tasks == 0:
            return {
                "success": True, 
                "data": {
                    "meta": self.plan_data["meta"],
                    "state": self.plan_data["state"],
                    "progress": {"completed_tasks": 0, "total_tasks": 0, "progress_percentage": 0.0},
                    "task_counts": {"pending": 0, "in_progress": 0, "completed": 0, "failed": 0, "skipped": 0, "total": 0}
                }
            }

        completed_count = sum(1 for task in self.plan_data["tasks"] if task["status"] in ["completed", "skipped"])
        progress_percentage = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        task_counts = {}
        for task in self.plan_data["tasks"]:
            status = task["status"]
            task_counts[status] = task_counts.get(status, 0) + 1

        status_data = {
            "meta": self.plan_data["meta"],
            "state": self.plan_data["state"],
            "progress": {
                "completed_tasks": completed_count,
                "total_tasks": total_tasks,
                "progress_percentage": round(progress_percentage, 2)
            },
            "task_counts": {
                "pending": task_counts.get("pending", 0),
                "in_progress": task_counts.get("in_progress", 0),
                "completed": task_counts.get("completed", 0),
                "failed": task_counts.get("failed", 0),
                "skipped": task_counts.get("skipped", 0),
                "total": total_tasks
            }
        }
        return {"success": True, "data": status_data}
        
    def getTaskById(self, task_id: int) -> Dict:
        """根据ID获取单个任务"""
        task = self._find_task_by_id(task_id)
        if task:
            return {"success": True, "data": task}
        else:
            return {"success": False, "message": f"Task with id {task_id} not found", "data": None}

    def getExecutableTaskList(self) -> Dict:
        """获取所有可执行的任务列表"""
        executable_tasks = []
        for task in self.plan_data["tasks"]:
            if task["status"] == "pending" and self._check_dependencies_satisfied(task):
                executable_tasks.append(task)
        
        return {"success": True, "data": executable_tasks}
    
    # 控制函数
    
    def pausePlan(self) -> Dict:
        """暂停整个计划"""
        self.plan_data["state"]["status"] = "paused"
        self._update_timestamp()
        
        return {"message": "Plan paused successfully"}
    
    def resumePlan(self) -> Dict:
        """恢复计划执行"""
        if self.plan_data["state"]["status"] == "paused":
            self.plan_data["state"]["status"] = "running"
            self._update_timestamp()
            
            return {"message": "Plan resumed successfully"}
        else:
            raise ValueError("Plan is not in paused status")
    
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
        
        return {
            "message": "Plan reset successfully",
            "reset_tasks": reset_count
        }
    

    def edit_dependencies_in_batch(self, edits: List[Dict]) -> Dict:
        """
        以批量方式编辑多个任务的依赖关系
        该操作是事务性的：所有编辑指令在应用前都会被验证。
        """
        try:
            # --- 验证阶段 ---
            original_tasks_copy = deepcopy(self.plan_data["tasks"])
            temp_tasks_map = {task['id']: task for task in original_tasks_copy}
            
            for edit in edits:
                task_id = edit.get("task_id")
                action = edit.get("action")

                if task_id is None or action is None:
                    raise ValueError("Each edit must contain 'task_id' and 'action'")

                task_to_edit = temp_tasks_map.get(task_id)
                if not task_to_edit:
                    raise ValueError(f"Task {task_id} not found in plan")

                if action == "set":
                    new_deps = edit.get("dependencies", [])
                    for dep_id in new_deps:
                        if dep_id not in temp_tasks_map:
                            raise ValueError(f"Dependency task {dep_id} not found")
                    task_to_edit["dependencies"] = new_deps

                elif action == "update":
                    add_deps = edit.get("add", [])
                    remove_deps = edit.get("remove", [])
                    
                    current_deps_set = set(task_to_edit["dependencies"])
                    
                    for dep_id in add_deps:
                        if dep_id not in temp_tasks_map:
                            raise ValueError(f"Dependency task to add ({dep_id}) not found")
                        current_deps_set.add(dep_id)
                    
                    current_deps_set.difference_update(remove_deps)
                    task_to_edit["dependencies"] = list(current_deps_set)
                    
                else:
                    raise ValueError(f"Invalid action '{action}' for task {task_id}")

            # --- 循环依赖检测阶段 ---
            temp_tasks_list = list(temp_tasks_map.values())
            for task in temp_tasks_list:
                if self._detect_circular_dependency(task["id"], task["dependencies"], tasks_list=temp_tasks_list):
                    raise ValueError(f"Circular dependency detected for task {task['id']} after applying edits.")

            # --- 应用阶段 ---
            self.plan_data["tasks"] = temp_tasks_list
            self._update_timestamp()
            
            results = [{"task_id": edit["task_id"], "new_dependencies": temp_tasks_map[edit["task_id"]]["dependencies"]} for edit in edits]

            return {
                "success": True,
                "message": "Tasks dependencies updated successfully.",
                "data": results
            }
        except ValueError as e:
            return {"success": False, "message": str(e), "data": None}
    
    # 工具函数
    
    def initializePlan(self, goal: str, tasks: List[Dict]) -> Dict:
        """
        初始化计划
        """
        if not tasks:
            return {"success": False, "message": "At least one task is required"}
        
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
        try:
            # First pass: create tasks and map names to IDs
            processed_tasks, task_name_to_id = self._process_tasks_pass_one(tasks)
            # Second pass: resolve dependencies
            self._process_tasks_pass_two(tasks, processed_tasks, task_name_to_id)
            # Third pass: detect circular dependencies
            self._check_all_circular_dependencies(processed_tasks)
        except ValueError as e:
            return {"success": False, "message": str(e)}

        self.plan_data["tasks"] = processed_tasks
        self._update_timestamp()
        
        return {
            "success": True,
            "message": "Plan initialized successfully",
            "data": self.plan_data
        }

    def _process_tasks_pass_one(self, tasks: List[Dict]) -> tuple[List[Dict], Dict[str, int]]:
        processed_tasks = []
        task_name_to_id = {}
        for i, task_input in enumerate(tasks):
            if not isinstance(task_input, dict):
                raise ValueError(f"Task at index {i} must be a dictionary")
            if "name" not in task_input:
                raise ValueError(f"Task at index {i} is missing required field 'name'")
            
            task_id = i
            task_name = task_input["name"]
            if task_name in task_name_to_id:
                raise ValueError(f"Duplicate task name '{task_name}' found.")
            task_name_to_id[task_name] = task_id
            
            processed_task = {
                "id": task_id,
                "name": task_name,
                "status": "pending",
                "dependencies": [],
                "reasoning": task_input.get("reasoning", f"Execute task: {task_name}"),
                "result": None
            }
            processed_tasks.append(processed_task)
        return processed_tasks, task_name_to_id

    def _process_tasks_pass_two(self, tasks: List[Dict], processed_tasks: List[Dict], task_name_to_id: Dict[str, int]):
        for i, task_input in enumerate(tasks):
            dependencies = task_input.get("dependencies", [])
            processed_dependencies = []
            for dep in dependencies:
                if isinstance(dep, str):
                    if dep not in task_name_to_id:
                        raise ValueError(f"Task '{processed_tasks[i]['name']}' depends on unknown task '{dep}'")
                    processed_dependencies.append(task_name_to_id[dep])
                elif isinstance(dep, int):
                    if not (0 <= dep < len(tasks)):
                        raise ValueError(f"Task {i} has invalid dependency index {dep}")
                    processed_dependencies.append(dep)
                else:
                    raise ValueError("Dependencies must be task names (strings) or 0-based indices (integers)")
            processed_tasks[i]["dependencies"] = sorted(list(set(processed_dependencies)))

    def _check_all_circular_dependencies(self, processed_tasks: List[Dict]):
        for task in processed_tasks:
            if self._detect_circular_dependency(task["id"], task["dependencies"], processed_tasks):
                raise ValueError(f"Circular dependency detected involving task '{task['name']}'")
    
    def exportPlan(self) -> Dict:
        """导出计划数据"""
        return deepcopy(self.plan_data)
    
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
        
        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "edges": edges
            }
        } 