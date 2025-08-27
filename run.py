#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest-TkTT 跨平台启动脚本
兼容 Windows, macOS, Linux
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入自定义日志配置
from ui.logger_config import setup_logger

# 设置启动日志
logger = setup_logger("TimeNest-Launcher", level="INFO")

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        logger.error("需要 Python 3.6 或更高版本")
        return False
    logger.info(f"Python 版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'tkinter',
        'PIL',
        'pystray'  # 如果有托盘功能
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'PIL':
                from PIL import Image
            elif package == 'pystray':
                import pystray
            logger.info(f"✓ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} 未安装")
    
    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        return False
    
    return True

def install_requirements():
    """安装依赖"""
    try:
        requirements_file = project_root / "requirements.txt"
        if requirements_file.exists():
            logger.info("正在安装依赖包...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            logger.info("依赖包安装完成")
            return True
        else:
            logger.warning("未找到 requirements.txt 文件")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"安装依赖失败: {e}")
        return False
    except Exception as e:
        logger.error(f"安装依赖时出错: {e}")
        return False

def get_python_command():
    """获取正确的Python命令"""
    system = platform.system().lower()
    
    # 尝试常用命令
    commands = [sys.executable]
    
    if system == "windows":
        commands.extend(["python", "python3", "py"])
    else:
        commands.extend(["python3", "python"])
    
    for cmd in commands:
        try:
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                logger.info(f"使用Python命令: {cmd}")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return sys.executable  # 使用当前解释器

def main():
    """主启动函数"""
    logger.info("=" * 50)
    logger.info("启动 TimeNest-TkTT 应用")
    logger.info(f"平台: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.executable}")
    logger.info(f"工作目录: {project_root}")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        logger.info("尝试安装缺失的依赖包...")
        if not install_requirements():
            logger.error("无法安装依赖包，请手动安装")
            sys.exit(1)
        
        # 再次检查依赖
        if not check_dependencies():
            logger.error("依赖检查仍然失败")
            sys.exit(1)
    
    # 获取Python命令
    python_cmd = get_python_command()
    
    # 启动主程序
    try:
        logger.info("启动主程序...")
        main_script = project_root / "main.py"
        
        if not main_script.exists():
            logger.error(f"主程序文件不存在: {main_script}")
            sys.exit(1)
        
        # 运行主程序
        result = subprocess.run([python_cmd, str(main_script)], 
                              cwd=str(project_root))
        
        if result.returncode == 0:
            logger.info("程序正常退出")
        else:
            logger.error(f"程序异常退出，返回码: {result.returncode}")
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"启动程序失败: {e}")
        logger.exception("详细错误信息:")
        sys.exit(1)

if __name__ == "__main__":
    main()