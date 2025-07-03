#!/usr/bin/env python3
"""
PlanManager 使用示例
演示如何使用 PlanManager 管理 Agent 任务
"""

from plan_manager import PlanManager
import json

def print_response(response):
    """格式化打印响应"""
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("-" * 50)

def main():
    # 创建 PlanManager 实例
    pm = PlanManager("example_plan.json")
    
    print("🚀 PlanManager 使用示例")
    print("=" * 50)
    
    # 1. 初始化计划
    print("1. 初始化计划")
    goal = "在京东网站上搜索'机械键盘'，并将价格低于500元的第一款产品加入购物车"
    
    initial_tasks = [
        {
            "id": 1,
            "name": "Navigate to JD homepage",
            "status": "pending",
            "dependencies": [],
            "reasoning": "需要先打开京东网站",
            "result": None
        },
        {
            "id": 2,
            "name": "Search for mechanical keyboard",
            "status": "pending", 
            "dependencies": [1],
            "reasoning": "在首页搜索机械键盘",
            "result": None
        },
        {
            "id": 3,
            "name": "Filter results by price under 500",
            "status": "pending",
            "dependencies": [2],
            "reasoning": "筛选价格低于500元的商品",
            "result": None
        },
        {
            "id": 4,
            "name": "Add first item to cart",
            "status": "pending",
            "dependencies": [3],
            "reasoning": "将第一个符合条件的商品加入购物车",
            "result": None
        }
    ]
    
    response = pm.initializePlan(goal, initial_tasks)
    print_response(response)
    
    # 2. 查看计划状态
    print("2. 查看计划状态")
    response = pm.getPlanStatus()
    print_response(response)
    
    # 3. 开始执行第一个任务
    print("3. 开始执行第一个任务")
    response = pm.startNextTask()
    print_response(response)
    
    # 4. 查看当前任务
    print("4. 查看当前任务")
    response = pm.getCurrentTask()
    print_response(response)
    
    # 5. 完成当前任务
    print("5. 完成当前任务")
    current_task = pm.getCurrentTask()
    if current_task["success"]:
        task_id = current_task["data"]["id"]
        response = pm.completeTask(task_id, "Successfully navigated to JD.com homepage")
        print_response(response)
    
    # 6. 处理意外情况 - 添加新任务
    print("6. 添加新任务处理弹窗")
    response = pm.addTask(
        "Close login popup",
        [1],  # 依赖任务1
        "Unexpected login popup appeared after homepage loaded",
        after_task_id=1  # 插入到任务1之后
    )
    print_response(response)
    
    # 7. 查看所有可执行的任务
    print("7. 查看可执行任务列表")
    response = pm.getExecutableTaskList()
    print_response(response)
    
    # 8. 开始下一个任务
    print("8. 开始下一个任务")
    response = pm.startNextTask()
    print_response(response)
    
    # 9. 模拟任务失败
    print("9. 模拟任务失败")
    current_task = pm.getCurrentTask()
    if current_task["success"]:
        task_id = current_task["data"]["id"]
        response = pm.failTask(task_id, "Unable to close popup - element not found")
        print_response(response)
    
    # 10. 查看所有任务列表
    print("10. 查看所有任务列表")
    response = pm.getTaskList()
    print_response(response)
    
    # 11. 更新任务依赖关系
    print("11. 更新任务2的依赖关系")
    response = pm.updateTask(2, {
        "dependencies": [1, 5],  # 现在依赖任务1和新添加的任务5
        "reasoning": "需要关闭弹窗后才能搜索"
    })
    print_response(response)
    
    # 12. 获取依赖关系图数据
    print("12. 获取依赖关系图数据")
    response = pm.getDependencyGraph()
    print_response(response)
    
    # 13. 跳过失败的任务
    print("13. 跳过失败的任务")
    failed_tasks = pm.getTaskList("failed")
    if failed_tasks["success"] and failed_tasks["data"]["tasks"]:
        failed_task_id = failed_tasks["data"]["tasks"][0]["id"]
        response = pm.skipTask(failed_task_id, "Will handle popup manually")
        print_response(response)
    
    # 14. 最终状态
    print("14. 查看最终计划状态")
    response = pm.getPlanStatus()
    print_response(response)
    
    print("✅ 示例完成！")
    print(f"计划数据已保存到: {pm.plan_file}")

if __name__ == "__main__":
    main() 