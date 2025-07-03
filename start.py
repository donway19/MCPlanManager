#!/usr/bin/env python3
import sys
import os
import subprocess

MIN_PYTHON = (3, 8)

# 检查Python版本
if sys.version_info < MIN_PYTHON:
    sys.stderr.write(f"[ERROR] 需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 及以上版本，当前为 {sys.version_info.major}.{sys.version_info.minor}\n")
    sys.exit(1)

# 检查并安装依赖
try:
    import mcplanmanager
except ImportError:
    # 检查pyproject.toml是否存在
    if not os.path.exists("pyproject.toml"):
        sys.stderr.write("[ERROR] 未找到 pyproject.toml，无法自动安装依赖。\n")
        sys.exit(1)
    print("[INFO] 未检测到 mcplanmanager，正在自动安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "."])
    except subprocess.CalledProcessError:
        sys.stderr.write("[ERROR] pip 安装依赖失败，请检查网络或权限。\n")
        sys.exit(1)

# 再次检查依赖
try:
    import mcplanmanager
except ImportError:
    sys.stderr.write("[ERROR] 依赖安装后仍无法导入 mcplanmanager，请检查依赖配置。\n")
    sys.exit(1)

# 启动 MCP 服务
os.execvp(sys.executable, [sys.executable, "-m", "mcplanmanager.mcp_server"] + sys.argv[1:]) 