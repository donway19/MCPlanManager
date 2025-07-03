#!/usr/bin/env python3
"""
PlanManager工具包装器
为不同环境提供统一的工具接口
"""

import json
import sys
from typing import Dict, Any
from plan_manager import PlanManager
from dependency_tools import DependencyVisualizer, DependencyPromptGenerator

class PlanManagerWrapper:
    """PlanManager工具包装器"""
    
    def __init__(self, plan_file: str = "plan.json"):
        self.plan_file = plan_file
        self.plan_manager = None
    
    def get_plan_manager(self) -> PlanManager:
        """获取PlanManager实例"""
        if self.plan_manager is None:
            self.plan_manager = PlanManager(self.plan_file)
        return self.plan_manager
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        try:
            # 更新plan_file如果提供了
            if 'plan_file' in arguments:
                self.plan_file = arguments['plan_file']
                self.plan_manager = None
            
            pm = self.get_plan_manager()
            
            if tool_name == "getCurrentTask":
                return pm.getCurrentTask()
            elif tool_name == "startNextTask":
                return pm.startNextTask()
            elif tool_name == "completeTask":
                return pm.completeTask(arguments["task_id"], arguments["result"])
            elif tool_name == "failTask":
                return pm.failTask(arguments["task_id"], arguments["error_message"], arguments.get("should_retry", True))
            elif tool_name == "addTask":
                return pm.addTask(arguments["name"], arguments["dependencies"], arguments["reasoning"], arguments.get("after_task_id"))
            elif tool_name == "skipTask":
                return pm.skipTask(arguments["task_id"], arguments["reason"])
            elif tool_name == "getTaskList":
                return pm.getTaskList(arguments.get("status_filter"))
            elif tool_name == "getPlanStatus":
                return pm.getPlanStatus()
            elif tool_name == "getExecutableTaskList":
                return pm.getExecutableTaskList()
            elif tool_name == "initializePlan":
                return pm.initializePlan(arguments["goal"], arguments.get("initial_tasks"))
            elif tool_name == "visualizeDependencies":
                format_type = arguments.get("format", "ascii")
                visualizer = DependencyVisualizer(pm)
                if format_type == "ascii":
                    visualization = visualizer.generate_ascii_graph()
                elif format_type == "tree":
                    visualization = visualizer.generate_tree_view()
                else:
                    visualization = visualizer.generate_ascii_graph()
                return {"success": True, "data": {"visualization": visualization}}
            elif tool_name == "generateContextPrompt":
                generator = DependencyPromptGenerator(pm)
                prompt = generator.generate_context_prompt()
                return {"success": True, "data": {"prompt": prompt}}
            else:
                return {"success": False, "error": {"code": "UNKNOWN_TOOL", "message": f"未知工具: {tool_name}"}}
        
        except Exception as e:
            return {"success": False, "error": {"code": "TOOL_EXECUTION_ERROR", "message": str(e)}}

def get_tool_definitions():
    """获取所有工具定义"""
    return {
        "getCurrentTask": {"description": "获取当前正在执行的任务"},
        "startNextTask": {"description": "自动开始下一个可执行的任务"},
        "completeTask": {"description": "标记任务为完成状态"},
        "failTask": {"description": "标记任务失败"},
        "addTask": {"description": "添加新任务到计划中"},
        "skipTask": {"description": "跳过指定任务"},
        "getTaskList": {"description": "获取任务列表"},
        "getPlanStatus": {"description": "获取整个计划的状态"},
        "getExecutableTaskList": {"description": "获取当前可执行的任务列表"},
        "initializePlan": {"description": "初始化计划"},
        "visualizeDependencies": {"description": "生成依赖关系可视化图表"},
        "generateContextPrompt": {"description": "生成上下文感知的执行提示词"}
    }

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("使用方法: python mcp_wrapper.py <tool_name> [arguments_json]")
        print("\n可用工具:")
        tools = get_tool_definitions()
        for tool_name, tool_def in tools.items():
            print(f"  {tool_name}: {tool_def['description']}")
        return
    
    tool_name = sys.argv[1]
    arguments = {}
    
    if len(sys.argv) > 2:
        try:
            arguments = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(f"参数解析错误: {e}")
            return
    
    wrapper = PlanManagerWrapper()
    result = wrapper.execute_tool(tool_name, arguments)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()