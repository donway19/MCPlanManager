#!/usr/bin/env python3
"""
MCPlanManager 持久化测试套件
测试 dumpPlan 和 loadPlan 工具的功能

使用方法：
python test/test_persistence.py [--mode uvx|sse]
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any, List
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport
import copy

class MCPPersistenceTestSuite:
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
            self.test_results.append({"name": test_name, "status": "PASS", "result": result})
            print(f"✅ {test_name} - 通过")
            return result
        except Exception as e:
            self.test_results.append({"name": test_name, "status": "FAIL", "error": str(e)})
            self.failed_tests.append(test_name)
            print(f"❌ {test_name} - 失败: {e}")
            # 在调试时，可以取消下面的注释来重新抛出异常
            # raise
            return None

    def extract_data(self, response):
        """从响应中提取数据"""
        if isinstance(response, list) and len(response) > 0:
            content = response[0]
            if hasattr(content, 'text'):
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    return content.text
        return response

    async def test_dump_and_load(self):
        """测试 dumpPlan 和 loadPlan 工具"""
        # 1. 初始化一个复杂的计划
        initial_plan = {
            "goal": "持久化测试计划",
            "tasks": [
                {"name": "Task A", "dependencies": [], "reasoning": "First task"},
                {"name": "Task B", "dependencies": ["Task A"], "reasoning": "Depends on A"},
                {"name": "Task C", "dependencies": ["Task A"], "reasoning": "Depends on A"},
                {"name": "Task D", "dependencies": ["Task B", "Task C"], "reasoning": "Depends on B and C"}
            ]
        }
        init_response = await self.client.call_tool("initializePlan", initial_plan)
        init_data = self.extract_data(init_response)
        assert init_data.get("success"), "初始化计划失败"
        print("📝 初始计划已创建")

        # 2. 修改一些状态
        start_response = await self.client.call_tool("startNextTask") # Start Task A
        start_data = self.extract_data(start_response)
        assert start_data.get("success"), "启动任务A失败"
        task_a_id = start_data["data"]["id"]
        
        comp_response = await self.client.call_tool("completeTask", {"task_id": task_a_id, "result": "A finished"})
        comp_data = self.extract_data(comp_response)
        assert comp_data.get("success"), "完成任务A失败"
        print("🔄 任务A已完成，计划状态已改变")

        # 3. 调用 dumpPlan 导出当前状态
        dump_response_1 = await self.client.call_tool("dumpPlan")
        dump_data_1 = self.extract_data(dump_response_1)
        assert dump_data_1.get("success"), "第一次 dumpPlan 失败"
        plan_to_load = dump_data_1.get("data")
        assert plan_to_load is not None, "导出的计划数据为空"
        print("📤 计划已成功导出")

        # 4. (可选) 重置或创建一个新状态来确保 loadPlan 的有效性
        await self.client.call_tool("initializePlan", {"goal": "临时计划", "tasks": []})
        print("🗑️  当前计划已重置为空白状态")

        # 5. 调用 loadPlan 加载导出的数据
        load_response = await self.client.call_tool("loadPlan", {"plan_data": plan_to_load})
        load_data = self.extract_data(load_response)
        assert load_data.get("success"), "loadPlan 失败"
        print("📥 计划已成功加载")

        # 6. 再次调用 dumpPlan
        dump_response_2 = await self.client.call_tool("dumpPlan")
        dump_data_2 = self.extract_data(dump_response_2)
        assert dump_data_2.get("success"), "第二次 dumpPlan 失败"
        reloaded_plan = dump_data_2.get("data")
        print("📤 第二次导出完成，准备比对")
        
        # 7. 比对两次导出的数据
        # 忽略时间戳的差异，因为它们在操作中会更新
        original_plan_no_ts = copy.deepcopy(plan_to_load)
        reloaded_plan_no_ts = copy.deepcopy(reloaded_plan)
        original_plan_no_ts["meta"].pop("created_at", None)
        original_plan_no_ts["meta"].pop("updated_at", None)
        reloaded_plan_no_ts["meta"].pop("created_at", None)
        reloaded_plan_no_ts["meta"].pop("updated_at", None)
        
        assert original_plan_no_ts == reloaded_plan_no_ts, "导入前后的计划数据不一致"
        print("🔍 数据一致性比对通过！")

        return {"dump_load_consistent": True}

    async def run_all_tests(self):
        """按顺序运行所有持久化相关的测试"""
        await self.setup_client()
        
        async with self.client:
            await self.run_test("测试导出和导入 (dumpPlan & loadPlan)", self.test_dump_and_load)

        self.print_summary()
        
        # 如果有任何测试失败，则以非零状态码退出
        if self.failed_tests:
            sys.exit(1)

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 持久化测试总结报告")
        print("="*60)
        passed = len(self.test_results) - len(self.failed_tests)
        print(f"总计测试: {len(self.test_results)}, 通过: {passed}, 失败: {len(self.failed_tests)}")
        if self.failed_tests:
            print("❌ 失败的测试项:")
            for test_name in self.failed_tests:
                print(f"  - {test_name}")
        else:
            print("🎉 所有持久化测试都通过了!")

async def main():
    parser = argparse.ArgumentParser(description="MCPlanManager 持久化测试")
    parser.add_argument("--mode", choices=["uvx", "sse"], default="sse", 
                       help="测试模式: uvx (本地) 或 sse (Docker)")
    
    args = parser.parse_args()
    
    suite = MCPPersistenceTestSuite(mode=args.mode)
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 