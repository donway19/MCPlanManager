#!/usr/bin/env python3
"""
MCPlanManager 测试运行器
运行所有测试套件

使用方法：
python test/run_all_tests.py [--mode uvx|sse]
"""

import asyncio
import argparse
import sys
import subprocess
import os
from pathlib import Path

class TestRunner:
    def __init__(self, mode: str = "sse"):
        self.mode = mode
        self.test_dir = Path(__file__).parent
        self.results = {}
        
    def run_test_suite(self, test_file: str, description: str):
        """运行单个测试套件"""
        print(f"\n{'='*60}")
        print(f"🧪 运行 {description}")
        print(f"{'='*60}")
        
        test_path = self.test_dir / test_file
        
        try:
            # 运行测试
            result = subprocess.run([
                sys.executable, str(test_path), "--mode", self.mode
            ], capture_output=True, text=True, cwd=self.test_dir.parent)
            
            # 打印输出
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # 记录结果
            self.results[description] = {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {description} - 通过")
            else:
                print(f"❌ {description} - 失败 (返回码: {result.returncode})")
                
        except Exception as e:
            print(f"❌ 运行 {description} 时出错: {e}")
            self.results[description] = {
                "success": False,
                "error": str(e)
            }
    
    def check_docker_service(self):
        """检查Docker服务是否运行"""
        if self.mode == "sse":
            print("🔍 检查Docker服务状态...")
            try:
                result = subprocess.run([
                    "docker", "ps", "--filter", "name=mcplanmanager", "--format", "table {{.Names}}\t{{.Status}}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and "mcplanmanager" in result.stdout:
                    print("✅ Docker服务正在运行")
                    return True
                else:
                    print("⚠️ Docker服务未运行，尝试启动...")
                    # 尝试启动Docker服务
                    start_result = subprocess.run([
                        "docker-compose", "up", "-d"
                    ], capture_output=True, text=True, cwd=self.test_dir.parent)
                    
                    if start_result.returncode == 0:
                        print("✅ Docker服务启动成功")
                        # 等待服务启动
                        import time
                        time.sleep(5)
                        return True
                    else:
                        print(f"❌ Docker服务启动失败: {start_result.stderr}")
                        return False
                        
            except Exception as e:
                print(f"❌ 检查Docker服务时出错: {e}")
                return False
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行 MCPlanManager 完整测试套件")
        print(f"📋 测试模式: {self.mode.upper()}")
        
        # 检查服务状态
        if not self.check_docker_service():
            print("❌ 服务检查失败，退出测试")
            return False
        
        # 定义测试套件
        test_suites = [
            ("test_complete_suite.py", "完整功能测试"),
            ("test_edge_cases.py", "边界情况测试"),
        ]
        
        # 运行每个测试套件
        for test_file, description in test_suites:
            test_path = self.test_dir / test_file
            if test_path.exists():
                self.run_test_suite(test_file, description)
            else:
                print(f"⚠️ 测试文件不存在: {test_file}")
                self.results[description] = {
                    "success": False,
                    "error": f"Test file not found: {test_file}"
                }
        
        # 打印总结
        self.print_summary()
        
        # 返回是否所有测试都成功
        return all(result.get("success", False) for result in self.results.values())
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 测试总结报告")
        print("="*60)
        
        total_suites = len(self.results)
        passed_suites = sum(1 for result in self.results.values() if result.get("success", False))
        failed_suites = total_suites - passed_suites
        
        print(f"总测试套件数: {total_suites}")
        print(f"通过套件数: {passed_suites} ✅")
        print(f"失败套件数: {failed_suites} ❌")
        print(f"成功率: {(passed_suites/total_suites*100):.1f}%")
        
        if failed_suites > 0:
            print(f"\n❌ 失败的测试套件:")
            for suite_name, result in self.results.items():
                if not result.get("success", False):
                    print(f"  - {suite_name}")
                    if "error" in result:
                        print(f"    错误: {result['error']}")
                    elif result.get("returncode"):
                        print(f"    返回码: {result['returncode']}")
        
        print(f"\n🎯 所有测试套件运行完成!")
        print(f"📋 测试模式: {self.mode.upper()}")
        
        if passed_suites == total_suites:
            print("🎉 所有测试都通过了!")
        else:
            print("⚠️ 部分测试失败，请检查详细输出")

def main():
    parser = argparse.ArgumentParser(description="MCPlanManager 测试运行器")
    parser.add_argument("--mode", choices=["uvx", "sse"], default="sse", 
                       help="测试模式: uvx (本地) 或 sse (Docker)")
    
    args = parser.parse_args()
    
    runner = TestRunner(mode=args.mode)
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 