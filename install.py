#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 自动安装脚本
简化安装过程，自动检测环境并安装依赖
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ████████╗██╗███╗   ███╗███████╗███╗   ██╗███████╗███████╗████████╗  ║
║  ╚══██╔══╝██║████╗ ████║██╔════╝████╗  ██║██╔════╝██╔════╝╚══██╔══╝  ║
║     ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║█████╗  ███████╗   ██║     ║
║     ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║██╔══╝  ╚════██║   ██║     ║
║     ██║   ██║██║ ╚═╝ ██║███████╗██║ ╚████║███████╗███████║   ██║     ║
║     ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝     ║
║                                                              ║
║                    TimeNest 自动安装程序                      ║
║                  让时间管理更简单，让学习更高效                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   TimeNest 需要 Python 3.8 或更高版本")
        print("   请访问 https://www.python.org/downloads/ 下载最新版本")
        return False
    
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_system_info():
    """检查系统信息"""
    print("\n📋 系统信息:")
    print(f"   操作系统: {platform.system()} {platform.release()}")
    print(f"   架构: {platform.machine()}")
    print(f"   Python 路径: {sys.executable}")


def run_command(cmd, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_venv():
    """检查是否在虚拟环境中"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ 检测到虚拟环境")
        return True
    else:
        print("⚠️  未检测到虚拟环境")
        return False


def create_venv():
    """创建虚拟环境"""
    print("\n🔧 创建虚拟环境...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("   虚拟环境已存在，跳过创建")
        return True
    
    success, output = run_command(f"{sys.executable} -m venv venv")
    if success:
        print("✅ 虚拟环境创建成功")
        return True
    else:
        print(f"❌ 虚拟环境创建失败: {output}")
        return False


def get_activation_command():
    """获取虚拟环境激活命令"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies(install_type="standard"):
    """安装依赖"""
    requirements_files = {
        "minimal": "requirements-minimal.txt",
        "standard": "requirements.txt", 
        "dev": "requirements-dev.txt",
        "prod": "requirements-prod.txt"
    }
    
    req_file = requirements_files.get(install_type, "requirements.txt")
    
    if not Path(req_file).exists():
        print(f"❌ 依赖文件不存在: {req_file}")
        return False
    
    print(f"\n📦 安装依赖 ({install_type})...")
    
    # 升级 pip
    success, _ = run_command(f"{sys.executable} -m pip install --upgrade pip")
    if not success:
        print("⚠️  pip 升级失败，继续安装...")
    
    # 安装依赖
    success, output = run_command(
        f"{sys.executable} -m pip install -r {req_file}",
        f"安装 {req_file} 中的依赖"
    )
    
    if success:
        print("✅ 依赖安装成功")
        return True
    else:
        print(f"❌ 依赖安装失败: {output}")
        return False


def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")
    
    # 检查核心依赖
    core_modules = ["PyQt6", "yaml", "requests"]
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            return False
    
    # 运行依赖检查脚本
    if Path("check_dependencies.py").exists():
        success, _ = run_command(f"{sys.executable} check_dependencies.py")
        if success:
            print("✅ 依赖检查通过")
        else:
            print("⚠️  依赖检查发现问题，但核心功能应该可用")
    
    return True


def show_next_steps():
    """显示后续步骤"""
    activation_cmd = get_activation_command()
    
    print("\n🎉 安装完成！")
    print("\n📝 后续步骤:")
    print("   1. 激活虚拟环境:")
    print(f"      {activation_cmd}")
    print("   2. 运行 TimeNest:")
    print("      python main.py")
    print("   3. 查看帮助文档:")
    print("      https://ziyi127.github.io/TimeNest-Website")
    print("\n💡 提示:")
    print("   - 首次运行会创建配置文件")
    print("   - 可以通过系统托盘访问应用")
    print("   - 遇到问题请查看 INSTALL.md")


def main():
    """主安装流程"""
    print_banner()
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 显示系统信息
    check_system_info()
    
    # 选择安装类型
    print("\n📦 选择安装类型:")
    print("   1. 标准安装 (推荐)")
    print("   2. 最小安装 (仅核心功能)")
    print("   3. 开发环境安装")
    print("   4. 生产环境安装")
    
    while True:
        choice = input("\n请选择 (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            break
        print("❌ 无效选择，请输入 1-4")
    
    install_types = {
        "1": "standard",
        "2": "minimal", 
        "3": "dev",
        "4": "prod"
    }
    install_type = install_types[choice]
    
    # 检查虚拟环境
    if not check_venv():
        create_venv_choice = input("\n是否创建虚拟环境? (推荐) [Y/n]: ").strip().lower()
        if create_venv_choice in ["", "y", "yes"]:
            if not create_venv():
                print("❌ 虚拟环境创建失败，继续在全局环境安装...")
            else:
                print(f"\n⚠️  请手动激活虚拟环境后重新运行安装脚本:")
                print(f"   {get_activation_command()}")
                print(f"   python install.py")
                sys.exit(0)
    
    # 安装依赖
    if not install_dependencies(install_type):
        print("\n❌ 安装失败！")
        print("💡 可能的解决方案:")
        print("   1. 检查网络连接")
        print("   2. 升级 pip: python -m pip install --upgrade pip")
        print("   3. 使用国内镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt")
        sys.exit(1)
    
    # 验证安装
    if not verify_installation():
        print("\n⚠️  安装验证失败，但可能仍然可用")
    
    # 显示后续步骤
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生错误: {e}")
        print("请查看 INSTALL.md 获取详细安装说明")
        sys.exit(1)
