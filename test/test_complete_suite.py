#!/usr/bin/env python3
"""
MCPlanManager 完整测试套件
测试所有 MCP 工具的功能

使用方法：
python test/test_complete_suite.py [--mode uvx|sse]
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any, List
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport

class MCPTestSuite:
    def __init__(self, mode: str = "sse"):
        self.mode = mode
        self.client = None
        self.test_results = []
        self.failed_tests = []
        
    async def setup_client(self):
        """根据模式设置客户端连接"""
        print(f"🔧 设置 {self.mode.upper()} 模式客户端...")
        
        if self.mode == "uvx":
            transport = UvxStdioTransport(tool_name="mcplanmanager")
            self.client = Client(transport)
        elif self.mode == "sse":
            sse_url = "http://localhost:8080/sse"
            self.client = Client(sse_url)
        else:
            raise ValueError(f"不支持的模式: {self.mode}")
    
    async def run_test(self, test_name: str, test_func, *args, **kwargs):
        """运行单个测试并记录结果"""
        print(f"\n🧪 测试: {test_name}")
        try:
            result = await test_func(*args, **kwargs)
            self.test_results.append({
                "name": test_name,
                "status": "PASS",
                "result": result
            })
            print(f"✅ {test_name} - 通过")
            return result
        except Exception as e:
            self.test_results.append({
                "name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
            self.failed_tests.append(test_name)
            print(f"❌ {test_name} - 失败: {e}")
            return None
    
    def extract_data(self, response):
        """从响应中提取数据"""
        if isinstance(response, list) and len(response) > 0:
            content = response[0]
            if hasattr(content, 'text'):
                try:
                    return json.loads(content.text)
                except:
                    return content.text
        return response
    
    async def test_get_plan_status(self):
        """测试获取计划状态"""
        response = await self.client.call_tool("getPlanStatus")
        data = self.extract_data(response)
        
        assert "success" in data or "meta" in data, "响应格式不正确"
        print(f"📊 当前状态: {data}")
        return data
    
    async def test_initialize_plan(self):
        """测试初始化计划"""
        test_plan = {
            "goal": "完整功能测试计划",
            "tasks": [
                {
                    "name": "基础功能验证",
                    "dependencies": [],
                    "reasoning": "验证所有基础工具功能"
                },
                {
                    "name": "依赖关系测试",
                    "dependencies": [0],
                    "reasoning": "测试任务依赖关系处理"
                },
                {
                    "name": "状态管理测试",
                    "dependencies": [0],
                    "reasoning": "测试任务状态转换"
                },
                {
                    "name": "批量操作测试",
                    "dependencies": [1, 2],
                    "reasoning": "测试批量依赖编辑功能"
                },
                {
                    "name": "可视化测试",
                    "dependencies": [3],
                    "reasoning": "测试依赖关系可视化"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", test_plan)
        data = self.extract_data(response)
        
        assert data.get("success", False), f"初始化失败: {data}"
        assert len(data.get("data", {}).get("tasks", [])) == 5, "任务数量不正确"
        print(f"📝 计划初始化成功，包含 {len(data['data']['tasks'])} 个任务")
        return data
    
    async def test_get_task_list(self):
        """测试获取任务列表"""
        # 测试无过滤器
        response = await self.client.call_tool("getTaskList")
        data = self.extract_data(response)
        
        assert data.get("success", False), "获取任务列表失败"
        tasks = data.get("data", [])
        assert len(tasks) > 0, "任务列表为空"
        print(f"📋 获取到 {len(tasks)} 个任务")
        
        # 测试状态过滤器
        for status in ["pending", "in_progress", "completed", "failed", "skipped"]:
            response = await self.client.call_tool("getTaskList", {"status_filter": status})
            filtered_data = self.extract_data(response)
            print(f"🔍 状态 '{status}' 的任务数量: {len(filtered_data.get('data', []))}")
        
        return data
    
    async def test_get_executable_task_list(self):
        """测试获取可执行任务列表"""
        response = await self.client.call_tool("getExecutableTaskList")
        data = self.extract_data(response)
        
        assert data.get("success", False), "获取可执行任务列表失败"
        executable_tasks = data.get("data", [])
        print(f"🚀 可执行任务数量: {len(executable_tasks)}")
        return data
    
    async def test_start_next_task(self):
        """测试启动下一个任务"""
        response = await self.client.call_tool("startNextTask")
        data = self.extract_data(response)
        
        if data.get("success", False):
            task = data.get("data", {})
            print(f"▶️ 启动任务: {task.get('name', 'Unknown')} (ID: {task.get('id', 'N/A')})")
            return data
        else:
            print(f"ℹ️ 无可启动任务: {data.get('message', 'Unknown reason')}")
            return data
    
    async def test_get_current_task(self):
        """测试获取当前任务"""
        response = await self.client.call_tool("getCurrentTask")
        data = self.extract_data(response)
        
        if data.get("success", False):
            task = data.get("data", {})
            print(f"📍 当前任务: {task.get('name', 'None')} (ID: {task.get('id', 'N/A')})")
        else:
            print(f"ℹ️ 无当前任务: {data.get('message', 'No active task')}")
        
        return data
    
    async def test_complete_task(self):
        """测试完成任务"""
        # 先获取当前任务
        current_response = await self.client.call_tool("getCurrentTask")
        current_data = self.extract_data(current_response)
        
        if current_data.get("success", False):
            task_id = current_data["data"]["id"]
            task_name = current_data["data"]["name"]
            
            response = await self.client.call_tool("completeTask", {
                "task_id": task_id,
                "result": f"任务 '{task_name}' 已成功完成测试"
            })
            data = self.extract_data(response)
            
            assert data.get("success", False), f"完成任务失败: {data}"
            print(f"✅ 任务 {task_id} 已完成")
            return data
        else:
            print("ℹ️ 无当前任务可完成")
            return {"success": False, "message": "No current task to complete"}
    
    async def test_add_task(self):
        """测试添加新任务"""
        new_task = {
            "name": "动态添加的测试任务",
            "dependencies": [0],  # 依赖第一个任务
            "reasoning": "测试动态添加任务功能"
        }
        
        response = await self.client.call_tool("addTask", new_task)
        data = self.extract_data(response)
        
        assert data.get("success", False), f"添加任务失败: {data}"
        task = data.get("data", {})
        print(f"➕ 添加任务: {task.get('name', 'Unknown')} (ID: {task.get('id', 'N/A')})")
        return data
    
    async def test_skip_task(self):
        """测试跳过任务"""
        # 获取一个待处理的任务
        task_list_response = await self.client.call_tool("getTaskList", {"status_filter": "pending"})
        task_list_data = self.extract_data(task_list_response)
        
        pending_tasks = task_list_data.get("data", [])
        if pending_tasks:
            task_to_skip = pending_tasks[0]
            task_id = task_to_skip["id"]
            
            response = await self.client.call_tool("skipTask", {
                "task_id": task_id,
                "reason": "测试跳过功能"
            })
            data = self.extract_data(response)
            
            assert data.get("success", False), f"跳过任务失败: {data}"
            print(f"⏭️ 跳过任务: {task_to_skip.get('name', 'Unknown')} (ID: {task_id})")
            return data
        else:
            print("ℹ️ 无待处理任务可跳过")
            return {"success": False, "message": "No pending tasks to skip"}
    
    async def test_fail_task(self):
        """测试任务失败"""
        # 启动一个新任务然后标记为失败
        start_response = await self.client.call_tool("startNextTask")
        start_data = self.extract_data(start_response)
        
        if start_data.get("success", False):
            task_id = start_data["data"]["id"]
            
            response = await self.client.call_tool("failTask", {
                "task_id": task_id,
                "error_message": "测试失败场景",
                "should_retry": True
            })
            data = self.extract_data(response)
            
            assert data.get("success", False), f"标记任务失败失败: {data}"
            print(f"❌ 任务 {task_id} 已标记为失败")
            return data
        else:
            print("ℹ️ 无任务可标记为失败")
            return {"success": False, "message": "No task to fail"}
    
    async def test_edit_dependencies(self):
        """测试编辑依赖关系"""
        # 获取任务列表以找到可编辑的任务
        task_list_response = await self.client.call_tool("getTaskList")
        task_list_data = self.extract_data(task_list_response)
        
        tasks = task_list_data.get("data", [])
        if len(tasks) >= 2:
            # 修改第二个任务的依赖关系
            edits = [
                {
                    "task_id": tasks[1]["id"],
                    "action": "set",  # 正确的字段名是 action，不是 operation
                    "dependencies": [tasks[0]["id"]]  # 设置依赖第一个任务
                }
            ]
            
            response = await self.client.call_tool("editDependencies", {"edits": edits})
            data = self.extract_data(response)
            
            assert data.get("success", False), f"编辑依赖关系失败: {data}"
            print(f"🔗 成功编辑任务 {tasks[1]['id']} 的依赖关系")
            return data
        else:
            print("ℹ️ 任务数量不足，无法测试依赖编辑")
            return {"success": False, "message": "Insufficient tasks for dependency editing"}
    
    async def test_visualize_dependencies(self):
        """测试依赖关系可视化"""
        formats = ["ascii", "tree", "mermaid"]
        results = {}
        
        for format_type in formats:
            response = await self.client.call_tool("visualizeDependencies", {"format": format_type})
            
            if isinstance(response, list) and len(response) > 0:
                content = response[0]
                if hasattr(content, 'text'):
                    visualization = content.text
                else:
                    visualization = str(response)
            else:
                visualization = str(response)
            
            results[format_type] = visualization
            print(f"📊 {format_type.upper()} 格式可视化生成成功 (长度: {len(visualization)})")
        
        return results
    
    async def test_generate_context_prompt(self):
        """测试生成上下文提示"""
        response = await self.client.call_tool("generateContextPrompt")
        
        # generateContextPrompt 直接返回字符串，不是 ToolResponse 格式
        if isinstance(response, list) and len(response) > 0:
            content = response[0]
            if hasattr(content, 'text'):
                prompt = content.text
            else:
                prompt = str(content)
        else:
            prompt = str(response)
        
        assert len(prompt) > 0, "生成的提示为空"
        print(f"💬 上下文提示生成成功 (长度: {len(prompt)})")
        return prompt
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 MCPlanManager 完整功能测试")
        print(f"📋 测试模式: {self.mode.upper()}")
        print("=" * 60)
        
        try:
            async with self.client:
                print("✅ 客户端连接成功")
                
                # 基础状态测试
                await self.run_test("获取计划状态", self.test_get_plan_status)
                
                # 计划管理测试
                await self.run_test("初始化计划", self.test_initialize_plan)
                await self.run_test("获取任务列表", self.test_get_task_list)
                await self.run_test("获取可执行任务", self.test_get_executable_task_list)
                
                # 任务执行测试
                await self.run_test("启动下一个任务", self.test_start_next_task)
                await self.run_test("获取当前任务", self.test_get_current_task)
                await self.run_test("完成任务", self.test_complete_task)
                
                # 任务管理测试
                await self.run_test("添加新任务", self.test_add_task)
                await self.run_test("跳过任务", self.test_skip_task)
                await self.run_test("任务失败", self.test_fail_task)
                
                # 高级功能测试
                await self.run_test("编辑依赖关系", self.test_edit_dependencies)
                await self.run_test("可视化依赖关系", self.test_visualize_dependencies)
                await self.run_test("生成上下文提示", self.test_generate_context_prompt)
                
        except Exception as e:
            print(f"❌ 客户端连接失败: {e}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len(self.failed_tests)
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ 失败的测试:")
            for test_name in self.failed_tests:
                print(f"  - {test_name}")
        
        print("\n🎯 所有功能测试完成!")
        return failed_tests == 0

async def main():
    parser = argparse.ArgumentParser(description="MCPlanManager 完整测试套件")
    parser.add_argument("--mode", choices=["uvx", "sse"], default="sse", 
                       help="测试模式: uvx (本地) 或 sse (Docker)")
    
    args = parser.parse_args()
    
    test_suite = MCPTestSuite(mode=args.mode)
    await test_suite.setup_client()
    await test_suite.run_all_tests()
    
    success = test_suite.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 