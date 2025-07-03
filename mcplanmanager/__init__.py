"""
MCPlanManager - AI Agent 任务管理系统

一个简洁高效的任务管理器，专为 AI Agent 的长程任务执行而设计。
使用纯内存模式，适用于托管环境和无文件系统权限的场景。
"""

__version__ = "1.0.0"
__author__ = "Suhe"
__email__ = "donwaydoom@gmail.com"

from .plan_manager import PlanManager
from .dependency_tools import DependencyVisualizer, DependencyPromptGenerator

__all__ = [
    "PlanManager",
    "DependencyVisualizer", 
    "DependencyPromptGenerator"
] 