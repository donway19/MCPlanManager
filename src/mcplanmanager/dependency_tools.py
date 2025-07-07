#!/usr/bin/env python3
"""
依赖关系工具集
包括可视化和Prompt转换功能
"""

from .plan_manager import PlanManager
from typing import Dict, List, Any
import json


class DependencyVisualizer:
    """依赖关系可视化工具"""
    
    def __init__(self, plan_manager: PlanManager):
        self.pm = plan_manager
    
    def generate_mermaid_graph(self) -> str:
        """生成Mermaid流程图代码"""
        graph_data = self.pm.getDependencyGraph()
        if not graph_data["success"]:
            return "Error: Could not get dependency graph"
        
        nodes = graph_data["data"]["nodes"]
        edges = graph_data["data"]["edges"]
        
        # 状态颜色映射
        status_colors = {
            "pending": "fill:#e1f5fe",
            "in_progress": "fill:#fff3e0", 
            "completed": "fill:#e8f5e8",
            "failed": "fill:#ffebee",
            "skipped": "fill:#f3e5f5"
        }
        
        mermaid_code = ["flowchart TD"]
        
        # 添加节点
        for node in nodes:
            node_id = f"T{node['id']}"
            node_name = node['name'].replace('"', "'")
            status = node['status']
            
            # 根据状态选择节点形状
            if status == "completed":
                shape = f'{node_id}["{node_name}"]'
            elif status == "in_progress":
                shape = f'{node_id}(("{node_name}"))'
            elif status == "failed":
                shape = f'{node_id}["{node_name}"]'
            else:
                shape = f'{node_id}["{node_name}"]'
            
            mermaid_code.append(f"    {shape}")
            
            # 添加样式
            if status in status_colors:
                mermaid_code.append(f"    style {node_id} {status_colors[status]}")
        
        # 添加边
        for edge in edges:
            from_node = f"T{edge['from']}"
            to_node = f"T{edge['to']}"
            mermaid_code.append(f"    {from_node} --> {to_node}")
        
        return "\n".join(mermaid_code)
    
    def generate_ascii_graph(self) -> str:
        """生成ASCII文本图"""
        graph_data = self.pm.getDependencyGraph()
        if not graph_data["success"]:
            return "Error: Could not get dependency graph"
        
        nodes = {node["id"]: node for node in graph_data["data"]["nodes"]}
        edges = graph_data["data"]["edges"]
        
        # 构建邻接表
        dependencies = {}
        for edge in edges:
            to_id = edge["to"]
            from_id = edge["from"]
            if to_id not in dependencies:
                dependencies[to_id] = []
            dependencies[to_id].append(from_id)
        
        # 状态符号
        status_symbols = {
            "pending": "⏳",
            "in_progress": "🔄", 
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }
        
        ascii_lines = ["📋 任务依赖关系图", "=" * 50]
        
        # 按ID排序显示任务
        for task_id in sorted(nodes.keys()):
            node = nodes[task_id]
            symbol = status_symbols.get(node["status"], "❓")
            
            line = f"{symbol} [{task_id}] {node['name']}"
            
            # 显示依赖关系
            if task_id in dependencies:
                deps = dependencies[task_id]
                dep_names = [f"[{dep_id}]" for dep_id in sorted(deps)]
                line += f" (依赖: {', '.join(dep_names)})"
            
            ascii_lines.append(line)
        
        # 添加图例
        ascii_lines.extend([
            "",
            "📝 状态图例:",
            "⏳ 待处理  🔄 进行中  ✅ 已完成  ❌ 失败  ⏭️ 跳过"
        ])
        
        return "\n".join(ascii_lines)
    
    def generate_tree_view(self) -> str:
        """生成树状视图"""
        graph_data = self.pm.getDependencyGraph()
        if not graph_data["success"]:
            return "Error: Could not get dependency graph"
        
        nodes = {node["id"]: node for node in graph_data["data"]["nodes"]}
        edges = graph_data["data"]["edges"]
        
        # 构建父子关系
        children = {}
        parents = {}
        
        for edge in edges:
            parent_id = edge["from"]
            child_id = edge["to"]
            
            if parent_id not in children:
                children[parent_id] = []
            children[parent_id].append(child_id)
            
            if child_id not in parents:
                parents[child_id] = []
            parents[child_id].append(parent_id)
        
        # 找到根节点（没有父节点的节点）
        all_nodes = set(nodes.keys())
        root_nodes = all_nodes - set(parents.keys())
        
        def build_tree(node_id: int, prefix: str = "", is_last: bool = True) -> List[str]:
            node = nodes[node_id]
            symbol = "✅" if node["status"] == "completed" else "⏳" if node["status"] == "pending" else "🔄"
            
            connector = "└── " if is_last else "├── "
            lines = [f"{prefix}{connector}{symbol} [{node_id}] {node['name']}"]
            
            if node_id in children:
                child_nodes = sorted(children[node_id])
                for i, child_id in enumerate(child_nodes):
                    is_last_child = (i == len(child_nodes) - 1)
                    extension = "    " if is_last else "│   "
                    lines.extend(build_tree(child_id, prefix + extension, is_last_child))
            
            return lines
        
        tree_lines = ["🌳 任务依赖树状图", "=" * 30]
        
        for root_id in sorted(root_nodes):
            tree_lines.extend(build_tree(root_id))
            tree_lines.append("")
        
        return "\n".join(tree_lines)


class DependencyPromptGenerator:
    """依赖关系Prompt生成器"""
    
    def __init__(self, plan_manager: PlanManager):
        self.pm = plan_manager
    
    def generate_context_prompt(self) -> str:
        """生成上下文感知的提示词"""
        plan_status = self.pm.getPlanStatus()
        if not plan_status["success"]:
            return "Error: Could not get plan status"
        
        plan_data = self.pm.exportPlan()  # exportPlan() 直接返回计划数据，不需要["data"]
        goal = plan_data["meta"]["goal"]
        tasks = plan_data["tasks"]
        state = plan_data["state"]
        
        prompt_parts = [
            "# 任务执行上下文",
            f"## 总体目标\n{goal}",
            "",
            "## 当前状态"
        ]
        
        # 当前任务信息
        current_task_response = self.pm.getCurrentTask()
        if current_task_response["success"]:
            task = current_task_response["data"]
            prompt_parts.extend([
                f"- 当前执行任务: [{task['id']}] {task['name']}",
                f"- 任务状态: {task['status']}",
                f"- 执行理由: {task['reasoning']}"
            ])
        else:
            prompt_parts.append("- 当前没有活动任务")
        
        # 可执行任务
        executable = self.pm.getExecutableTaskList()
        if executable["success"] and len(executable["data"]) > 0:
            prompt_parts.append("\n## 可执行任务")
            for task in executable["data"]:
                prompt_parts.append(f"- [{task['id']}] {task['name']}")
        
        # 任务依赖关系
        prompt_parts.extend([
            "",
            "## 任务依赖关系",
            self._generate_dependency_text(tasks)
        ])
        
        # 执行建议
        prompt_parts.extend([
            "",
            "## 执行建议",
            self._generate_execution_suggestions(tasks, state)
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_next_action_prompt(self) -> str:
        """生成下一步行动的提示词"""
        current_task = self.pm.getCurrentTask()
        executable = self.pm.getExecutableTaskList()
        
        if current_task["success"]:
            task = current_task["data"]
            return f"""
# 当前任务执行指导

您正在执行任务: **[{task['id']}] {task['name']}**

## 任务详情
- 执行理由: {task['reasoning']}
- 当前状态: {task['status']}

## 执行指南
1. 专注于完成当前任务
2. 遇到问题时及时反馈
3. 完成后调用 completeTask() 函数
4. 如遇无法解决的问题，调用 failTask() 函数

## 下一步行动
请继续执行当前任务，并在完成或遇到问题时及时更新任务状态。
"""
        
        elif executable["success"] and len(executable["data"]) > 0:
            next_tasks = executable["data"][:3]  # 显示前3个
            task_list = "\n".join([f"- [{t['id']}] {t['name']}" for t in next_tasks])
            
            return f"""
# 准备执行下一个任务

## 可执行任务列表
{task_list}

## 建议行动
调用 startNextTask() 函数开始执行下一个任务。

## 注意事项
- 确保依赖任务已完成
- 按照任务优先级执行
- 遇到意外情况及时调用 addTask() 添加处理任务
"""
        
        else:
            return """
# 等待中

当前没有可执行的任务。可能的原因：
1. 所有任务都已完成
2. 存在阻塞的依赖关系
3. 需要处理失败的任务

## 建议行动
1. 检查计划状态: getPlanStatus()
2. 查看失败任务: getTaskList("failed")
3. 必要时跳过或重置任务
"""
    
    def generate_error_handling_prompt(self, error_context: str = "") -> str:
        """生成错误处理提示词"""
        failed_tasks = self.pm.getTaskList("failed")
        
        prompt_parts = [
            "# 错误处理指导",
            "",
            f"## 错误上下文\n{error_context}" if error_context else "## 检测到任务执行问题",
            ""
        ]
        
        if failed_tasks["success"] and failed_tasks["data"]["tasks"]:
            prompt_parts.extend([
                "## 失败任务列表",
                ""
            ])
            
            for task in failed_tasks["data"]["tasks"]:
                prompt_parts.extend([
                    f"### [{task['id']}] {task['name']}",
                    f"- 失败原因: {task.get('result', '未知')}",
                    f"- 理由: {task['reasoning']}",
                    ""
                ])
            
            prompt_parts.extend([
                "## 处理建议",
                "1. 分析失败原因",
                "2. 选择适当的处理方式:",
                "   - 跳过任务: skipTask(task_id, reason)",
                "   - 添加修复任务: addTask(name, dependencies, reasoning)",
                "   - 更新任务依赖: updateTask(task_id, updates)",
                "3. 继续执行计划"
            ])
        else:
            prompt_parts.extend([
                "## 当前状态",
                "没有失败的任务需要处理。请检查其他可能的问题：",
                "- 依赖关系是否正确",
                "- 是否需要添加新的处理任务",
                "- 任务定义是否需要调整"
            ])
        
        return "\n".join(prompt_parts)
    
    def _generate_dependency_text(self, tasks: List[Dict]) -> str:
        """生成依赖关系文本描述"""
        lines = []
        
        for task in tasks:
            deps = task.get("dependencies", [])
            if deps:
                dep_names = []
                for dep_id in deps:
                    dep_task = next((t for t in tasks if t["id"] == dep_id), None)
                    if dep_task:
                        dep_names.append(f"[{dep_id}] {dep_task['name']}")
                
                lines.append(f"- [{task['id']}] {task['name']} 依赖于: {', '.join(dep_names)}")
            else:
                lines.append(f"- [{task['id']}] {task['name']} (无依赖)")
        
        return "\n".join(lines) if lines else "没有任务依赖关系"
    
    def _generate_execution_suggestions(self, tasks: List[Dict], state: Dict) -> str:
        """生成执行建议"""
        suggestions = []
        
        # 分析任务状态
        status_counts = {}
        for task in tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_tasks = len(tasks)
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        pending = status_counts.get("pending", 0)
        
        # 进度建议
        if completed > 0:
            progress = completed / total_tasks * 100
            suggestions.append(f"当前进度: {progress:.1f}% ({completed}/{total_tasks})")
        
        # 状态建议
        if failed > 0:
            suggestions.append(f"注意: 有 {failed} 个任务失败，需要处理")
        
        if pending > 0:
            suggestions.append(f"剩余 {pending} 个任务待执行")
        
        # 执行建议
        if state.get("current_task_id"):
            suggestions.append("继续执行当前任务")
        elif pending > 0:
            suggestions.append("调用 startNextTask() 开始下一个任务")
        else:
            suggestions.append("所有任务已处理完成")
        
        return "\n".join(f"- {s}" for s in suggestions)


# 便捷函数
def visualize_plan(plan_file: str = "plan.json") -> None:
    """可视化计划的便捷函数"""
    pm = PlanManager(plan_file)
    visualizer = DependencyVisualizer(pm)
    
    print("🎨 依赖关系可视化")
    print("=" * 50)
    
    print("\n📊 ASCII图形:")
    print(visualizer.generate_ascii_graph())
    
    print("\n🌳 树状视图:")
    print(visualizer.generate_tree_view())
    
    print("\n🔗 Mermaid图形代码:")
    print("```mermaid")
    print(visualizer.generate_mermaid_graph())
    print("```")


def generate_context_prompt(plan_file: str = "plan.json") -> str:
    """生成上下文提示词的便捷函数"""
    pm = PlanManager(plan_file)
    generator = DependencyPromptGenerator(pm)
    return generator.generate_context_prompt()


if __name__ == "__main__":
    # 测试可视化工具
    visualize_plan("example_plan.json") 