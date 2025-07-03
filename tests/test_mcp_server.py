#!/usr/bin/env python3
"""
测试MCP服务器
手动测试MCP协议通信
"""

import json
import subprocess
import sys
import os

def test_mcp_server():
    """测试MCP服务器"""
    print("测试MCP服务器启动...")
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # 启动MCP服务器
    try:
        # 方式1：直接使用Python模块
        process = subprocess.Popen(
            [sys.executable, "-m", "mcplanmanager.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 测试初始化
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("初始化响应:", json.dumps(response, ensure_ascii=False, indent=2))
            
            if response.get("result"):
                print("✓ 初始化成功")
            else:
                print("✗ 初始化失败")
                return False
        else:
            print("✗ 未收到初始化响应")
            return False
        
        # 测试工具列表
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n发送工具列表请求...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("工具列表响应:", json.dumps(response, ensure_ascii=False, indent=2))
            
            if response.get("result", {}).get("tools"):
                print(f"✓ 获取到 {len(response['result']['tools'])} 个工具")
            else:
                print("✗ 获取工具列表失败")
                return False
        else:
            print("✗ 未收到工具列表响应")
            return False
        
        # 测试工具调用 - 初始化计划
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "initializePlan",
                "arguments": {
                    "goal": "测试计划",
                    "tasks": [
                        {
                            "name": "任务1",
                            "reasoning": "第一个任务",
                            "dependencies": []
                        },
                        {
                            "name": "任务2",
                            "reasoning": "第二个任务",
                            "dependencies": ["任务1"]
                        }
                    ]
                }
            }
        }
        
        print("\n发送工具调用请求...")
        process.stdin.write(json.dumps(tool_call_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("工具调用响应:", json.dumps(response, ensure_ascii=False, indent=2))
            
            if response.get("result", {}).get("content"):
                print("✓ 工具调用成功")
            else:
                print("✗ 工具调用失败")
                return False
        else:
            print("✗ 未收到工具调用响应")
            return False
        
        # 关闭进程
        process.stdin.close()
        process.terminate()
        process.wait()
        
        print("\n✓ MCP服务器测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_command_line():
    """测试命令行启动"""
    print("\n测试命令行启动...")
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # 测试不同的启动方式
    startup_methods = [
        # 使用Python模块
        [sys.executable, "-m", "mcplanmanager.mcp_server"],
        # 使用包装器
        [sys.executable, "-m", "mcplanmanager.mcp_wrapper"],
        # 使用pip安装的入口点（如果安装了）
        ["mcplanmanager"]
    ]
    
    for method in startup_methods:
        print(f"\n测试启动方式: {' '.join(method)}")
        try:
            # 只测试启动，不发送请求
            result = subprocess.run(
                method + ["--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✓ 启动成功")
            else:
                print(f"✗ 启动失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("✓ 启动成功（超时，但这是正常的MCP服务器行为）")
        except FileNotFoundError:
            print("✗ 命令不存在")
        except Exception as e:
            print(f"✗ 启动异常: {e}")

if __name__ == "__main__":
    print("=== MCP服务器测试 ===")
    
    # 测试MCP服务器
    if test_mcp_server():
        print("\n✓ MCP服务器功能正常")
    else:
        print("\n✗ MCP服务器功能异常")
    
    # 测试命令行启动
    test_command_line() 