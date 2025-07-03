#!/usr/bin/env python3
"""
PlanManager部署测试脚本
验证所有功能是否正常工作
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并检查结果"""
    print(f"\n🧪 测试: {description}")
    print(f"📝 命令: {command}")
    
    try:
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 成功")
            output = result.stdout
            if output:
                try:
                    data = json.loads(output)
                    print(f"📄 结果: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                except:
                    print(f"📄 输出: {output[:200]}...")
            return True, output
        else:
            print("❌ 失败")
            print(f"错误: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print("❌ 超时")
        return False, "命令执行超时"
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, str(e)

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 50)
    print("🚀 开始基本功能测试")
    print("=" * 50)
    
    tests = [
        ("python mcp_wrapper.py", "显示工具列表"),
        ("python mcp_wrapper.py getPlanStatus", "获取计划状态"),
        ("python mcp_wrapper.py getExecutableTaskList", "获取可执行任务"),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, description in tests:
        success, output = run_command(command, description)
        if success:
            passed += 1
    
    print(f"\n📊 基本功能测试结果: {passed}/{total} 通过")
    return passed == total

def main():
    """主测试函数"""
    print("🧪 PlanManager 部署测试")
    
    # 检查当前目录
    if not Path("plan_manager.py").exists():
        print("❌ 错误: 请在PlanManager项目根目录运行此脚本")
        sys.exit(1)
    
    # 运行基本测试
    if test_basic_functionality():
        print("✅ 项目可以发布!")
        return True
    else:
        print("❌ 请修复问题后再发布")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)