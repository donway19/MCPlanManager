import asyncio
from fastmcp import Client

async def main():
    """
    测试 Docker 容器中运行的 SSE 模式 MCP 服务
    """
    try:
        print("🚀 正在连接到 Docker 容器中的 SSE MCP 服务...")
        
        # 连接到 SSE 端点
        sse_url = "http://localhost:8080/sse"
        print(f"🔌 连接地址: {sse_url}")
        
        client = Client(sse_url)
        
        async with client:
            print("✅ 连接成功！")
            
            # 测试基本功能
            print("\n🔎 正在调用 `getPlanStatus` 工具...")
            status = await client.call_tool("getPlanStatus")
            
            print("\n🎉 成功接收到服务响应:")
            print(status)
            
            # 测试初始化计划
            print("\n🔎 正在测试 `initializePlan` 工具...")
            init_result = await client.call_tool("initializePlan", {
                "goal": "测试 Docker SSE 部署",
                "tasks": [
                    {
                        "name": "验证 SSE 连接",
                        "dependencies": [],
                        "reasoning": "确保 SSE 模式正常工作"
                    },
                    {
                        "name": "测试工具调用",
                        "dependencies": [0],
                        "reasoning": "验证 MCP 工具能够通过 SSE 正常响应"
                    },
                    {
                        "name": "验证持久化",
                        "dependencies": [1],
                        "reasoning": "测试数据是否正确保存"
                    }
                ]
            })
            
            print("\n📝 计划初始化结果:")
            print(init_result)
            
            # 测试任务列表
            print("\n🔎 正在获取任务列表...")
            task_list = await client.call_tool("getTaskList")
            
            print("\n📋 任务列表:")
            print(task_list)
            
            # 测试启动任务
            print("\n🔎 正在启动下一个任务...")
            next_task = await client.call_tool("startNextTask")
            
            print("\n🚀 启动的任务:")
            print(next_task)
            
            # 测试依赖关系可视化
            print("\n🔎 正在生成依赖关系图...")
            deps = await client.call_tool("visualizeDependencies", {"format": "ascii"})
            
            print("\n📊 依赖关系图:")
            print(deps)
        
        print("\n👋 测试完成，连接已关闭。")
        
    except Exception as e:
        print(f"\n🔥 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 