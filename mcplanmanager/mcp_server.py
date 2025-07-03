#!/usr/bin/env python3
"""
MCPlanManager的标准MCP服务器实现
符合Model Context Protocol标准，通过stdin/stdout通信
"""

import json
import sys
import os
import asyncio
from typing import Dict, List, Any, Optional
from .plan_manager import PlanManager
from .dependency_tools import DependencyVisualizer, DependencyPromptGenerator

class MCPlanManagerServer:
    """MCPlanManager MCP服务器"""
    
    def __init__(self):
        self.plan_manager = None
        self.plan_file = "plan.json"
    
    def get_plan_manager(self) -> PlanManager:
        """获取PlanManager实例"""
        if self.plan_manager is None:
            self.plan_manager = PlanManager(self.plan_file)
        return self.plan_manager
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "mcplanmanager",
                "version": "1.0.0"
            }
        }
    
    async def handle_list_tools(self, params: Dict) -> Dict:
        """返回所有可用工具"""
        tools = [
            {
                "name": "initializePlan",
                "description": "初始化新的任务计划",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "计划的总体目标"
                        },
                        "tasks": {
                            "type": "array",
                            "description": "任务列表",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "任务名称"},
                                    "reasoning": {"type": "string", "description": "执行理由"},
                                    "dependencies": {
                                        "type": "array",
                                        "description": "依赖的任务（名称或索引）",
                                        "items": {"oneOf": [{"type": "string"}, {"type": "integer"}]}
                                    }
                                },
                                "required": ["name"]
                            }
                        }
                    },
                    "required": ["goal", "tasks"]
                }
            },
            {
                "name": "getCurrentTask",
                "description": "获取当前正在执行的任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "description": "Dummy参数（可选）",
                            "default": ""
                        }
                    }
                }
            },
            {
                "name": "startNextTask",
                "description": "开始下一个可执行的任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "description": "Dummy参数（可选）",
                            "default": ""
                        }
                    }
                }
            },
            {
                "name": "completeTask",
                "description": "标记任务为完成状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "任务ID"},
                        "result": {"type": "string", "description": "任务结果"}
                    },
                    "required": ["task_id", "result"]
                }
            },
            {
                "name": "failTask",
                "description": "标记任务失败",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "任务ID"},
                        "error_message": {"type": "string", "description": "错误信息"},
                        "should_retry": {"type": "boolean", "description": "是否重试", "default": True}
                    },
                    "required": ["task_id", "error_message"]
                }
            },
            {
                "name": "addTask",
                "description": "添加新任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "任务名称"},
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "依赖的任务ID"
                        },
                        "reasoning": {"type": "string", "description": "执行理由"},
                        "after_task_id": {"type": "integer", "description": "插入位置", "optional": True}
                    },
                    "required": ["name", "dependencies", "reasoning"]
                }
            },
            {
                "name": "skipTask",
                "description": "跳过指定任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "任务ID"},
                        "reason": {"type": "string", "description": "跳过原因"}
                    },
                    "required": ["task_id", "reason"]
                }
            },
            {
                "name": "getPlanStatus",
                "description": "获取计划状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "description": "Dummy参数（可选）",
                            "default": ""
                        }
                    }
                }
            },
            {
                "name": "getTaskList",
                "description": "获取任务列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status_filter": {
                            "type": "string",
                            "description": "状态过滤器",
                            "enum": ["pending", "in_progress", "completed", "failed", "skipped"],
                            "optional": True
                        }
                    }
                }
            },
            {
                "name": "getExecutableTaskList",
                "description": "获取可执行任务列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "description": "Dummy参数（可选）",
                            "default": ""
                        }
                    }
                }
            },
            {
                "name": "visualizeDependencies",
                "description": "生成依赖关系可视化",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "可视化格式",
                            "enum": ["ascii", "tree", "mermaid"],
                            "default": "ascii"
                        }
                    }
                }
            },
            {
                "name": "generateContextPrompt",
                "description": "生成上下文提示词",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "description": "Dummy参数（可选）",
                            "default": ""
                        }
                    }
                }
            }
        ]
        
        return {"tools": tools}
    
    async def handle_call_tool(self, params: Dict) -> Dict:
        """处理工具调用"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            # 更新plan_file如果提供了
            if 'plan_file' in arguments:
                self.plan_file = arguments['plan_file']
                self.plan_manager = None
            
            # 处理initializePlan工具
            if tool_name == "initializePlan":
                pm = self.get_plan_manager()
                result = pm.initializePlan(arguments["goal"], arguments["tasks"])
            else:
                # 对于其他工具，检查是否有有效的计划文件
                if not os.path.exists(self.plan_file):
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "错误: 计划文件不存在。请先使用initializePlan工具创建计划。"
                            }
                        ],
                        "isError": True
                    }
                
                try:
                    pm = self.get_plan_manager()
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"错误: 无法加载计划文件。请先使用initializePlan工具创建计划。详细错误: {str(e)}"
                            }
                        ],
                        "isError": True
                    }
                
                # 处理其他工具调用
                if tool_name == "getCurrentTask":
                    result = pm.getCurrentTask()
                elif tool_name == "startNextTask":
                    result = pm.startNextTask()
                elif tool_name == "completeTask":
                    result = pm.completeTask(arguments["task_id"], arguments["result"])
                elif tool_name == "failTask":
                    result = pm.failTask(arguments["task_id"], arguments["error_message"], arguments.get("should_retry", True))
                elif tool_name == "addTask":
                    result = pm.addTask(arguments["name"], arguments["dependencies"], arguments["reasoning"], arguments.get("after_task_id"))
                elif tool_name == "skipTask":
                    result = pm.skipTask(arguments["task_id"], arguments["reason"])
                elif tool_name == "getTaskList":
                    result = pm.getTaskList(arguments.get("status_filter"))
                elif tool_name == "getPlanStatus":
                    result = pm.getPlanStatus()
                elif tool_name == "getExecutableTaskList":
                    result = pm.getExecutableTaskList()
                elif tool_name == "visualizeDependencies":
                    format_type = arguments.get("format", "ascii")
                    visualizer = DependencyVisualizer(pm)
                    if format_type == "ascii":
                        visualization = visualizer.generate_ascii_graph()
                    elif format_type == "tree":
                        visualization = visualizer.generate_tree_view()
                    elif format_type == "mermaid":
                        visualization = visualizer.generate_mermaid_graph()
                    else:
                        visualization = visualizer.generate_ascii_graph()
                    result = {"success": True, "data": {"visualization": visualization}}
                elif tool_name == "generateContextPrompt":
                    generator = DependencyPromptGenerator(pm)
                    prompt = generator.generate_context_prompt()
                    result = {"success": True, "data": {"prompt": prompt}}
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"未知工具: {tool_name}"
                            }
                        ],
                        "isError": True
                    }
            
            # 格式化返回结果
            if result.get("success"):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result["data"], ensure_ascii=False, indent=2)
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"错误: {result.get('error', {}).get('message', '未知错误')}"
                        }
                    ],
                    "isError": True
                }
            
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"工具执行异常: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def handle_request(self, request: Dict) -> Dict:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_list_tools(params)
            elif method == "tools/call":
                result = await self.handle_call_tool(params)
            else:
                raise Exception(f"未知方法: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """运行MCP服务器"""
        try:
            while True:
                # 从stdin读取请求
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # 向stdout写入响应
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"JSON解析错误: {e}"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            pass

def main():
    """主函数"""
    server = MCPlanManagerServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main() 