#!/usr/bin/env python3
"""
MCPlanManager新初始化方式测试

演示AI模型如何使用简化的参数创建任务计划
只需要提供业务内容，技术字段由工具自动维护
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcplanmanager import PlanManager, DependencyVisualizer

def test_model_friendly_initialization():
    """测试模型友好的初始化方式"""
    print("=== MCPlanManager 新初始化方式测试 ===\n")
    
    # 创建PlanManager实例
    pm = PlanManager("test_new_plan.json")
    
    # AI模型只需要提供这些简单的业务内容
    goal = "完成网上购物流程"
    
    # 任务列表 - AI模型只需要专注于业务逻辑
    tasks = [
        {
            "name": "打开购物网站",
            "reasoning": "开始购物流程的第一步，需要访问电商网站",
            "dependencies": []  # 无依赖，第一个任务
        },
        {
            "name": "搜索商品",
            "reasoning": "在网站上搜索需要购买的商品",
            "dependencies": ["打开购物网站"]  # 依赖任务名称
        },
        {
            "name": "筛选商品",
            "reasoning": "根据价格、评价等条件筛选合适的商品",
            "dependencies": [2]  # 也可以用索引（1-based）
        },
        {
            "name": "加入购物车",
            "reasoning": "将选中的商品加入购物车",
            "dependencies": ["筛选商品"]
        },
        {
            "name": "填写收货信息",
            "reasoning": "输入收货地址和联系方式",
            "dependencies": []  # 可以独立进行
        },
        {
            "name": "确认订单",
            "reasoning": "检查商品信息和收货信息无误后确认订单",
            "dependencies": ["加入购物车", "填写收货信息"]  # 多重依赖
        },
        {
            "name": "选择支付方式",
            "reasoning": "选择合适的支付方式进行付款",
            "dependencies": ["确认订单"]
        },
        {
            "name": "完成支付",
            "reasoning": "执行支付操作，完成整个购物流程",
            "dependencies": ["选择支付方式"]
        }
    ]
    
    # 初始化计划
    print("1. 初始化计划...")
    result = pm.initializePlan(goal, tasks)
    
    if result["success"]:
        print("✅ 计划初始化成功！")
        print(f"目标: {result['data']['goal']}")
        print(f"任务数量: {result['data']['task_count']}")
        
        # 显示自动生成的完整任务信息
        print("\n自动生成的任务详情:")
        for task in result['data']['tasks']:
            deps_str = ", ".join(map(str, task['dependencies'])) if task['dependencies'] else "无"
            print(f"  [{task['id']}] {task['name']} (依赖: {deps_str})")
            print(f"      状态: {task['status']}")
            print(f"      理由: {task['reasoning']}")
            print()
    else:
        print(f"❌ 初始化失败: {result['error']['message']}")
        return
    
    # 测试依赖关系可视化
    print("2. 依赖关系可视化...")
    visualizer = DependencyVisualizer(pm)
    print(visualizer.generate_ascii_graph())
    
    # 测试任务执行流程
    print("3. 开始任务执行...")
    
    # 开始第一个任务
    result = pm.startNextTask()
    if result["success"]:
        current_task = result["data"]["task"]
        print(f"✅ 开始任务: [{current_task['id']}] {current_task['name']}")
        
        # 完成第一个任务
        pm.completeTask(current_task['id'], "成功打开了购物网站主页")
        print(f"✅ 完成任务: [{current_task['id']}] {current_task['name']}")
    
    # 继续下一个任务
    result = pm.startNextTask()
    if result["success"]:
        current_task = result["data"]["task"]
        print(f"✅ 开始任务: [{current_task['id']}] {current_task['name']}")
    
    # 查看当前计划状态
    print("\n4. 当前计划状态:")
    status = pm.getPlanStatus()
    if status["success"]:
        data = status["data"]
        print(f"整体状态: {data['status']}")
        print(f"当前任务ID: {data['current_task_id']}")
        print(f"总任务数: {data['total_tasks']}")
        print(f"已完成: {data['completed_tasks']}")
        print(f"进行中: {data['in_progress_tasks']}")
        print(f"待处理: {data['pending_tasks']}")
    
    print("\n=== 测试完成 ===")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===\n")
    
    pm = PlanManager("test_error_plan.json")
    
    # 测试循环依赖检测
    print("1. 测试循环依赖检测...")
    tasks_with_cycle = [
        {
            "name": "任务A",
            "reasoning": "第一个任务",
            "dependencies": ["任务B"]  # A依赖B
        },
        {
            "name": "任务B", 
            "reasoning": "第二个任务",
            "dependencies": ["任务A"]  # B依赖A，形成循环
        }
    ]
    
    result = pm.initializePlan("测试循环依赖", tasks_with_cycle)
    if not result["success"]:
        print(f"✅ 正确检测到循环依赖: {result['error']['message']}")
    else:
        print("❌ 未能检测到循环依赖")
    
    # 测试无效依赖
    print("\n2. 测试无效依赖...")
    tasks_with_invalid_dep = [
        {
            "name": "任务A",
            "reasoning": "第一个任务", 
            "dependencies": ["不存在的任务"]
        }
    ]
    
    result = pm.initializePlan("测试无效依赖", tasks_with_invalid_dep)
    if not result["success"]:
        print(f"✅ 正确检测到无效依赖: {result['error']['message']}")
    else:
        print("❌ 未能检测到无效依赖")
    
    print("\n=== 错误处理测试完成 ===")

if __name__ == "__main__":
    test_model_friendly_initialization()
    test_error_handling() 