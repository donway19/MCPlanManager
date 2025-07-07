import asyncio
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport

async def main():
    """
    一个简单的 MCP 客户端，用于测试本地服务是否正常运行。
    """
    try:
        # 1. 创建 UvxStdioTransport 实例
        print("🚀 正在创建 UvxStdioTransport...")
        transport = UvxStdioTransport(tool_name="mcplanmanager")
        
        # 2. 创建 Client 实例
        client = Client(transport)
        
        # 3. 使用 async with 启动并连接
        print("🔌 正在连接到服务...")
        async with client:
            print("✅ 连接成功！")
            
            # 4. 调用一个工具进行测试
            print("\n🔎 正在调用 `getPlanStatus` 工具...")
            status = await client.call_tool("getPlanStatus")
            
            # 5. 打印结果
            print("\n🎉 成功接收到服务响应:")
            print(status)
        
        print("\n👋 连接已关闭。")
        
    except Exception as e:
        print(f"\n🔥 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 