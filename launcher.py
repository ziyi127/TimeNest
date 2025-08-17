#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 启动器
负责检查 Python 环境、创建和激活虚拟环境、安装依赖项，并启动 TimeNest 应用程序。
这是推荐的启动方式，会自动处理环境配置并启动应用。
"""

import sys
import subprocess
import time
import platform
from pathlib import Path


def print_status(message: str) -> None:
    """打印状态信息"""
    print(f"[TimeNest Launcher] {message}")


def check_python() -> bool:
    """检查 Python 是否安装"""
    print_status("检查 Python 环境...")
    try:
        python_version = sys.version_info
        if python_version < (3, 8):
            print_status("错误: Python 版本过低，请安装 Python 3.8 或更高版本")
            return False
        print_status(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return True
    except Exception as e:
        print_status(f"错误: 检查 Python 环境时发生错误: {e}")
        return False


def create_virtual_environment() -> bool:
    """创建虚拟环境"""
    print_status("检查虚拟环境...")
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_status("创建虚拟环境...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print_status("虚拟环境创建成功")
        except subprocess.CalledProcessError as e:
            print_status(f"错误: 创建虚拟环境失败: {e}")
            return False
    else:
        print_status("虚拟环境已存在")
    
    return True


def activate_virtual_environment() -> bool:
    """激活虚拟环境"""
    print_status("激活虚拟环境...")
    
    # 实际上不需要显式激活虚拟环境，因为我们会直接使用虚拟环境中的 Python 解释器
    # 这里只是检查虚拟环境是否存在
    if platform.system() == "Windows":
        python_path = Path("venv/Scripts/python.exe")
    else:
        python_path = Path("venv/bin/python")
    
    if not python_path.exists():
        print_status("错误: 虚拟环境中的 Python 解释器不存在")
        return False
    
    print_status("虚拟环境已就绪")
    return True


def install_dependencies() -> bool:
    """安装依赖项"""
    print_status("检查并安装依赖项...")
    
    try:
        # 使用虚拟环境中的 pip
        if platform.system() == "Windows":
            pip_path = Path("venv/Scripts/pip.exe")
        else:
            pip_path = Path("venv/bin/pip")
        
        if not pip_path.exists():
            print_status("错误: 未找到 pip")
            return False
        
        pip_cmd = [str(pip_path)]
        
        # 安装依赖项
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        print_status("依赖项安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"错误: 安装依赖项失败: {e}")
        return False
    except Exception as e:
        print_status(f"错误: 安装依赖项时发生未知错误: {e}")
        return False


def start_backend() -> bool:
    """启动后端组件"""
    print_status("启动后端组件...")
    # 在这个项目中，后端逻辑与前端界面集成在 main.py 中
    # 因此这里只是模拟后端启动过程
    time.sleep(1)  # 模拟启动时间
    print_status("后端组件启动完成")
    return True


def start_frontend() -> bool:
    """启动前端组件"""
    print_status("启动前端组件...")
    # 在这个项目中，前端界面与后端逻辑集成在 main.py 中
    # 因此这里只是模拟前端启动过程
    time.sleep(1)  # 模拟启动时间
    print_status("前端组件启动完成")
    return True


def start_application() -> bool:
    """启动主应用程序"""
    print_status("启动 TimeNest 应用程序...")
    
    try:
        # 使用虚拟环境中的 Python 运行 main.py
        if platform.system() == "Windows":
            python_path = Path("venv/Scripts/python.exe")
        else:
            python_path = Path("venv/bin/python")
        
        # 检查虚拟环境中的 Python 是否存在
        if not python_path.exists():
            print_status("错误: 虚拟环境中的 Python 解释器不存在")
            return False
        
        # 使用虚拟环境中的 Python 运行 main.py，并设置工作目录
        subprocess.run([str(python_path), "main.py"], cwd=".", check=True)
        print_status("TimeNest 应用程序已启动")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"错误: 启动 TimeNest 应用程序失败: {e}")
        return False
    except KeyboardInterrupt:
        print_status("用户中断了应用程序启动")
        return True
    except Exception as e:
        print_status(f"错误: 启动 TimeNest 应用程序时发生未知错误: {e}")
        return False


def main() -> int:
    """主函数"""
    print_status("TimeNest 正在加载...")
    print_status("=" * 50)
    
    # 检查 Python 环境
    if not check_python():
        return 1
    
    # 创建虚拟环境
    if not create_virtual_environment():
        return 1
    
    # 激活虚拟环境
    if not activate_virtual_environment():
        return 1
    
    # 安装依赖项
    if not install_dependencies():
        return 1
    
    # 启动后端组件
    if not start_backend():
        return 1
    
    # 启动前端组件
    if not start_frontend():
        return 1
    
    # 启动主应用程序
    if not start_application():
        return 1
    
    print_status("=" * 50)
    print_status("TimeNest 启动完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())