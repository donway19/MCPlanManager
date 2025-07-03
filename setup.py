#!/usr/bin/env python3
"""
MCPlanManager安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcplanmanager",
    version="1.0.0",
    author="Suhe",
    author_email="donwaydoom@gmail.com",
    description="AI Agent任务管理系统 - MCP服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/donway19/MCPlanManager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "api": ["fastapi>=0.104.0", "uvicorn>=0.24.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "mypy>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "mcplanmanager=mcplanmanager.mcp_wrapper:main",
            "mcplanmanager-api=server.api_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
        "mcplanmanager": ["*.md"],
    },
)