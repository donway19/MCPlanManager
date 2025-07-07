#!/usr/bin/env python3
"""
MCPlanManager 边界情况测试
测试错误处理和边界条件

使用方法：
python test/test_edge_cases.py [--mode uvx|sse]
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport

class EdgeCaseTestSuite:
    def __init__(self, mode: str = "sse"):
        self.mode = mode
        self.client = None
        self.test_results = []
        self.failed_tests = []
        
    async def setup_client(self):
        """设置客户端连接"""
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
    
    async def test_invalid_task_id(self):
        """测试无效的任务ID"""
        invalid_ids = [999, -1, "invalid", None]
        
        for invalid_id in invalid_ids:
            try:
                response = await self.client.call_tool("completeTask", {
                    "task_id": invalid_id,
                    "result": "测试无效ID"
                })
                data = self.extract_data(response)
                
                # 应该返回错误或失败状态
                if isinstance(data, dict):
                    assert not data.get("success", True), f"无效ID {invalid_id} 应该失败"
                    print(f"  ✅ 无效ID {invalid_id} 正确处理")
                
            except Exception as e:
                print(f"  ✅ 无效ID {invalid_id} 抛出异常: {e}")
    
    async def test_empty_plan_initialization(self):
        """测试空计划初始化"""
        # 测试完全空的计划
        response = await self.client.call_tool("initializePlan", {"goal": "空任务计划", "tasks": []})
        data = self.extract_data(response)
        assert not data.get("success", True), "包含空任务列表的计划应该失败"
        print(f"  ✅ 空任务列表的计划被正确拒绝: {data.get('message')}")

        # 测试 goal 为 None
        try:
            await self.client.call_tool("initializePlan", {"goal": None, "tasks": [{"name": "a", "dependencies": [], "reasoning": "a"}]})
        except Exception as e:
            assert "Input should be a valid string" in str(e), "goal 为 None 应该引发 Pydantic 验证错误"
            print("  ✅ goal 为 None 时引发了正确的验证错误")
    
    async def test_circular_dependencies(self):
        """测试循环依赖"""
        circular_plan = {
            "goal": "循环依赖测试",
            "tasks": [
                {
                    "name": "任务A",
                    "dependencies": [1],  # 依赖任务B
                    "reasoning": "测试循环依赖"
                },
                {
                    "name": "任务B", 
                    "dependencies": [0],  # 依赖任务A
                    "reasoning": "测试循环依赖"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", circular_plan)
        data = self.extract_data(response)
        
        if isinstance(data, dict):
            if data.get("success", False):
                print("  ⚠️ 循环依赖计划被接受 - 需要检查依赖验证")
            else:
                print(f"  ✅ 循环依赖正确拒绝: {data.get('message', 'Unknown')}")
    
    async def test_invalid_dependencies(self):
        """测试无效依赖"""
        invalid_plan = {
            "goal": "无效依赖测试",
            "tasks": [
                {
                    "name": "任务1",
                    "dependencies": [999],  # 不存在的依赖
                    "reasoning": "测试无效依赖"
                },
                {
                    "name": "任务2",
                    "dependencies": [-1],  # 负数依赖
                    "reasoning": "测试无效依赖"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", invalid_plan)
        data = self.extract_data(response)
        
        if isinstance(data, dict):
            if data.get("success", False):
                print("  ⚠️ 无效依赖计划被接受 - 需要检查依赖验证")
            else:
                print(f"  ✅ 无效依赖正确拒绝: {data.get('message', 'Unknown')}")
    
    async def test_large_task_name(self):
        """测试超长任务名称"""
        long_name = "超长任务名称" * 100  # 创建很长的名称
        
        plan = {
            "goal": "超长名称测试",
            "tasks": [
                {
                    "name": long_name,
                    "dependencies": [],
                    "reasoning": "测试超长名称处理"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", plan)
        data = self.extract_data(response)
        
        if isinstance(data, dict):
            if data.get("success", False):
                print(f"  ✅ 超长名称任务创建成功 (长度: {len(long_name)})")
            else:
                print(f"  ℹ️ 超长名称被拒绝: {data.get('message', 'Unknown')}")
    
    async def test_special_characters(self):
        """测试特殊字符处理"""
        special_chars_plan = {
            "goal": "特殊字符测试 🚀 #@$%^&*()[]{}",
            "tasks": [
                {
                    "name": "任务 with émojis 🎯 and symbols @#$%",
                    "dependencies": [],
                    "reasoning": "测试特殊字符和emoji处理 ✨"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", special_chars_plan)
        data = self.extract_data(response)
        
        if isinstance(data, dict):
            if data.get("success", False):
                print("  ✅ 特殊字符和emoji处理成功")
            else:
                print(f"  ℹ️ 特殊字符被拒绝: {data.get('message', 'Unknown')}")
    
    async def test_nonexistent_operations(self):
        """测试不存在的操作"""
        # 测试在没有当前任务时完成任务
        response = await self.client.call_tool("getCurrentTask")
        data = self.extract_data(response)
        
        if isinstance(data, dict) and not data.get("success", False):
            # 尝试完成不存在的当前任务
            try:
                complete_response = await self.client.call_tool("completeTask", {
                    "task_id": 999,
                    "result": "尝试完成不存在的任务"
                })
                complete_data = self.extract_data(complete_response)
                
                if isinstance(complete_data, dict):
                    assert not complete_data.get("success", True), "完成不存在的任务应该失败"
                    print("  ✅ 完成不存在任务正确失败")
                
            except Exception as e:
                print(f"  ✅ 完成不存在任务抛出异常: {e}")
    
    async def test_state_consistency(self):
        """测试状态一致性"""
        # 创建一个简单计划
        plan = {
            "goal": "状态一致性测试",
            "tasks": [
                {
                    "name": "测试任务",
                    "dependencies": [],
                    "reasoning": "测试状态一致性"
                }
            ]
        }
        
        response = await self.client.call_tool("initializePlan", plan)
        data = self.extract_data(response)
        
        if isinstance(data, dict) and data.get("success", False):
            # 启动任务
            start_response = await self.client.call_tool("startNextTask")
            start_data = self.extract_data(start_response)
            
            if isinstance(start_data, dict) and start_data.get("success", False):
                task_id = start_data["data"]["id"]
                
                # 尝试重复启动同一个任务
                repeat_response = await self.client.call_tool("startNextTask")
                repeat_data = self.extract_data(repeat_response)
                
                if isinstance(repeat_data, dict):
                    if repeat_data.get("success", False):
                        # 检查是否是不同的任务
                        if repeat_data["data"]["id"] != task_id:
                            print("  ✅ 状态一致性正确 - 启动了不同任务")
                        else:
                            print("  ⚠️ 状态不一致 - 重复启动了同一任务")
                    else:
                        print("  ✅ 状态一致性正确 - 没有重复启动任务")
    
    async def run_all_edge_case_tests(self):
        """运行所有边界情况测试"""
        print("🚀 开始 MCPlanManager 边界情况测试")
        print(f"📋 测试模式: {self.mode.upper()}")
        print("=" * 60)
        
        try:
            async with self.client:
                print("✅ 客户端连接成功")
                
                # 边界情况测试
                await self.run_test("无效任务ID处理", self.test_invalid_task_id)
                await self.run_test("空计划初始化", self.test_empty_plan_initialization)
                await self.run_test("循环依赖检测", self.test_circular_dependencies)
                await self.run_test("无效依赖处理", self.test_invalid_dependencies)
                await self.run_test("超长任务名称", self.test_large_task_name)
                await self.run_test("特殊字符处理", self.test_special_characters)
                await self.run_test("不存在操作处理", self.test_nonexistent_operations)
                await self.run_test("状态一致性", self.test_state_consistency)
                
        except Exception as e:
            print(f"❌ 客户端连接失败: {e}")
            return False
        
        return True
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 边界情况测试结果总结")
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
        
        print("\n🎯 边界情况测试完成!")
        return failed_tests == 0

async def main():
    parser = argparse.ArgumentParser(description="MCPlanManager 边界情况测试")
    parser.add_argument("--mode", choices=["uvx", "sse"], default="sse", 
                       help="测试模式: uvx (本地) 或 sse (Docker)")
    
    args = parser.parse_args()
    
    test_suite = EdgeCaseTestSuite(mode=args.mode)
    await test_suite.setup_client()
    success = await test_suite.run_all_edge_case_tests()
    
    success = test_suite.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 