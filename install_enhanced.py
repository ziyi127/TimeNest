#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 增强版安装程序
包含自动故障处理、多种环境预设和智能错误恢复功能
"""

import sys
import os
import subprocess
import time
import platform
import shutil
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('install.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InstallationError(Exception):
    """安装错误基类"""
    pass


class EnvironmentType(Enum):
    """环境类型枚举"""
    WINDOWS_STANDARD = "windows_standard"
    WINDOWS_CONDA = "windows_conda"
    LINUX_STANDARD = "linux_standard"
    LINUX_CONDA = "linux_conda"
    MACOS_STANDARD = "macos_standard"
    MACOS_CONDA = "macos_conda"
    DOCKER = "docker"
    WSL = "wsl"


@dataclass
class InstallPreset:
    """安装预设配置"""
    name: str
    description: str
    python_min_version: Tuple[int, int]
    pip_args: List[str]
    pre_install_commands: List[str]
    post_install_commands: List[str]
    required_packages: List[str]
    optional_packages: List[str]
    environment_variables: Dict[str, str]
    troubleshooting_steps: List[str]


class EnvironmentDetector:
    """环境检测器"""
    
    @staticmethod
    def detect_environment() -> EnvironmentType:
        """检测当前环境类型"""
        system = platform.system().lower()
        
        # 检查是否在WSL中
        if system == "linux" and "microsoft" in platform.uname().release.lower():
            return EnvironmentType.WSL
        
        # 检查是否在Docker中
        if os.path.exists("/.dockerenv"):
            return EnvironmentType.DOCKER
        
        # 检查是否使用Conda
        conda_env = os.environ.get("CONDA_DEFAULT_ENV")
        if conda_env or shutil.which("conda"):
            if system == "windows":
                return EnvironmentType.WINDOWS_CONDA
            elif system == "linux":
                return EnvironmentType.LINUX_CONDA
            elif system == "darwin":
                return EnvironmentType.MACOS_CONDA
        
        # 标准环境
        if system == "windows":
            return EnvironmentType.WINDOWS_STANDARD
        elif system == "linux":
            return EnvironmentType.LINUX_STANDARD
        elif system == "darwin":
            return EnvironmentType.MACOS_STANDARD
        
        return EnvironmentType.LINUX_STANDARD  # 默认
    
    @staticmethod
    def get_python_info() -> Dict[str, Any]:
        """获取Python环境信息"""
        return {
            "version": sys.version_info,
            "executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "pip_version": EnvironmentDetector._get_pip_version(),
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
        }
    
    @staticmethod
    def _get_pip_version() -> Optional[str]:
        """获取pip版本"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


class PresetManager:
    """预设管理器"""
    
    def __init__(self):
        self.presets = self._create_presets()
    
    def _create_presets(self) -> Dict[EnvironmentType, InstallPreset]:
        """创建预设配置"""
        return {
            EnvironmentType.WINDOWS_STANDARD: InstallPreset(
                name="Windows 标准环境",
                description="适用于标准Windows环境的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade", "--user"],
                pre_install_commands=[
                    "python -m pip install --upgrade pip setuptools wheel"
                ],
                post_install_commands=[],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule", "plyer"],
                environment_variables={},
                troubleshooting_steps=[
                    "检查Python是否正确安装",
                    "确保pip可用",
                    "尝试使用管理员权限运行",
                    "检查防火墙设置"
                ]
            ),
            
            EnvironmentType.WINDOWS_CONDA: InstallPreset(
                name="Windows Conda环境",
                description="适用于Windows Conda环境的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade"],
                pre_install_commands=[
                    "conda update -n base -c defaults conda",
                    "conda install pip"
                ],
                post_install_commands=[],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule", "plyer"],
                environment_variables={},
                troubleshooting_steps=[
                    "激活正确的conda环境",
                    "更新conda到最新版本",
                    "检查conda channels配置"
                ]
            ),
            
            EnvironmentType.LINUX_STANDARD: InstallPreset(
                name="Linux 标准环境",
                description="适用于标准Linux环境的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade", "--user"],
                pre_install_commands=[
                    "python3 -m pip install --upgrade pip setuptools wheel"
                ],
                post_install_commands=[],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule", "plyer"],
                environment_variables={
                    "QT_QPA_PLATFORM": "xcb"
                },
                troubleshooting_steps=[
                    "安装系统依赖: sudo apt-get install python3-pip python3-venv",
                    "安装Qt依赖: sudo apt-get install qt6-base-dev",
                    "检查X11转发设置",
                    "确保有足够的磁盘空间"
                ]
            ),
            
            EnvironmentType.WSL: InstallPreset(
                name="WSL环境",
                description="适用于Windows Subsystem for Linux的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade", "--user"],
                pre_install_commands=[
                    "sudo apt-get update",
                    "sudo apt-get install -y python3-pip python3-venv",
                    "python3 -m pip install --upgrade pip"
                ],
                post_install_commands=[],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule", "plyer"],
                environment_variables={
                    "DISPLAY": ":0",
                    "QT_QPA_PLATFORM": "xcb"
                },
                troubleshooting_steps=[
                    "安装X11服务器 (如VcXsrv)",
                    "配置DISPLAY环境变量",
                    "安装Qt依赖包",
                    "检查WSL版本兼容性"
                ]
            ),
            
            EnvironmentType.MACOS_STANDARD: InstallPreset(
                name="macOS 标准环境",
                description="适用于标准macOS环境的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade", "--user"],
                pre_install_commands=[
                    "python3 -m pip install --upgrade pip setuptools wheel"
                ],
                post_install_commands=[],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule", "plyer"],
                environment_variables={},
                troubleshooting_steps=[
                    "安装Xcode命令行工具",
                    "使用Homebrew安装Python",
                    "检查macOS版本兼容性",
                    "确保有开发者权限"
                ]
            ),
            
            EnvironmentType.DOCKER: InstallPreset(
                name="Docker环境",
                description="适用于Docker容器的安装配置",
                python_min_version=(3, 8),
                pip_args=["--upgrade", "--no-cache-dir"],
                pre_install_commands=[
                    "apt-get update",
                    "apt-get install -y python3-pip"
                ],
                post_install_commands=[
                    "apt-get clean",
                    "rm -rf /var/lib/apt/lists/*"
                ],
                required_packages=["PyQt6", "requests", "psutil"],
                optional_packages=["schedule"],
                environment_variables={
                    "QT_QPA_PLATFORM": "offscreen"
                },
                troubleshooting_steps=[
                    "使用无头模式运行",
                    "配置虚拟显示",
                    "检查容器权限设置"
                ]
            )
        }
    
    def get_preset(self, env_type: EnvironmentType) -> InstallPreset:
        """获取指定环境的预设"""
        return self.presets.get(env_type, self.presets[EnvironmentType.LINUX_STANDARD])


class AutoRecovery:
    """自动恢复系统"""
    
    def __init__(self):
        self.recovery_strategies = {
            "pip_install_failed": self._recover_pip_install,
            "venv_creation_failed": self._recover_venv_creation,
            "permission_denied": self._recover_permission_denied,
            "network_error": self._recover_network_error,
            "dependency_conflict": self._recover_dependency_conflict,
        }
    
    def attempt_recovery(self, error_type: str, context: Dict[str, Any]) -> bool:
        """尝试自动恢复"""
        strategy = self.recovery_strategies.get(error_type)
        if strategy:
            try:
                return strategy(context)
            except Exception as e:
                logger.error(f"恢复策略失败: {e}")
        return False

    def _recover_pip_install(self, context: Dict[str, Any]) -> bool:
        """恢复pip安装失败"""
        package = context.get("package", "")
        logger.info(f"尝试恢复pip安装失败: {package}")

        # 策略1: 升级pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                         check=True, timeout=60)
            logger.info("pip升级成功")
        except Exception:
            pass

        # 策略2: 清除缓存
        try:
            subprocess.run([sys.executable, "-m", "pip", "cache", "purge"],
                         check=True, timeout=30)
            logger.info("pip缓存清除成功")
        except Exception:
            pass

        # 策略3: 使用不同的索引
        alternative_indexes = [
            "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "https://pypi.douban.com/simple/",
            "https://mirrors.aliyun.com/pypi/simple/"
        ]

        for index in alternative_indexes:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "-i", index, package
                ], check=True, timeout=120)
                logger.info(f"使用镜像源 {index} 安装成功")
                return True
            except Exception:
                continue

        return False

    def _recover_venv_creation(self, context: Dict[str, Any]) -> bool:
        """恢复虚拟环境创建失败"""
        venv_path = context.get("venv_path", "venv")
        logger.info(f"尝试恢复虚拟环境创建失败: {venv_path}")

        # 策略1: 删除现有目录重新创建
        try:
            if os.path.exists(venv_path):
                shutil.rmtree(venv_path)
            subprocess.run([sys.executable, "-m", "venv", venv_path],
                         check=True, timeout=60)
            return True
        except Exception:
            pass

        # 策略2: 使用virtualenv
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv"],
                         check=True, timeout=60)
            subprocess.run([sys.executable, "-m", "virtualenv", venv_path],
                         check=True, timeout=60)
            return True
        except Exception:
            pass

        return False

    def _recover_permission_denied(self, context: Dict[str, Any]) -> bool:
        """恢复权限拒绝错误"""
        logger.info("尝试恢复权限拒绝错误")

        # 在Windows上建议使用--user参数
        if platform.system() == "Windows":
            return True  # 让调用者使用--user参数重试

        return False

    def _recover_network_error(self, context: Dict[str, Any]) -> bool:
        """恢复网络错误"""
        logger.info("尝试恢复网络错误")

        # 等待网络恢复
        time.sleep(5)

        # 测试网络连接
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            return True
        except Exception:
            pass

        return False

    def _recover_dependency_conflict(self, context: Dict[str, Any]) -> bool:
        """恢复依赖冲突"""
        logger.info("尝试恢复依赖冲突")

        # 策略1: 强制重新安装
        package = context.get("package", "")
        if package:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "--force-reinstall", "--no-deps", package
                ], check=True, timeout=120)
                return True
            except Exception:
                pass

        return False


class EnhancedInstaller:
    """增强版安装器"""

    def __init__(self):
        self.env_detector = EnvironmentDetector()
        self.preset_manager = PresetManager()
        self.auto_recovery = AutoRecovery()
        self.env_type = self.env_detector.detect_environment()
        self.preset = self.preset_manager.get_preset(self.env_type)
        self.project_dir = Path.cwd()
        self.venv_dir = self.project_dir / "venv"
        self.install_log = []

    def install(self, options: Dict[str, Any] = None) -> Tuple[bool, str]:
        """执行安装"""
        options = options or {}

        try:
            logger.info(f"开始安装 TimeNest - 环境类型: {self.env_type.value}")
            logger.info(f"使用预设: {self.preset.name}")

            # 步骤1: 环境检查
            if not self._check_environment():
                return False, "环境检查失败"

            # 步骤2: 预安装命令
            if not self._run_pre_install_commands():
                return False, "预安装命令执行失败"

            # 步骤3: 创建虚拟环境
            if options.get("create_venv", True):
                if not self._create_virtual_environment():
                    return False, "虚拟环境创建失败"

            # 步骤4: 安装依赖
            if not self._install_dependencies(options):
                return False, "依赖安装失败"

            # 步骤5: 后安装命令
            if not self._run_post_install_commands():
                return False, "后安装命令执行失败"

            # 步骤6: 验证安装
            if not self._verify_installation():
                return False, "安装验证失败"

            logger.info("安装成功完成")
            return True, "安装成功"

        except Exception as e:
            error_msg = f"安装过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def _check_environment(self) -> bool:
        """检查环境"""
        try:
            python_info = self.env_detector.get_python_info()
            logger.info(f"Python信息: {python_info}")

            # 检查Python版本
            min_version = self.preset.python_min_version
            current_version = python_info["version"][:2]

            if current_version < min_version:
                logger.error(f"Python版本过低: {current_version} < {min_version}")
                return False

            # 检查必要工具
            if not shutil.which("pip") and not self._check_pip_module():
                logger.error("pip不可用")
                return False

            # 设置环境变量
            for key, value in self.preset.environment_variables.items():
                os.environ[key] = value
                logger.info(f"设置环境变量: {key}={value}")

            return True

        except Exception as e:
            logger.error(f"环境检查失败: {e}")
            return False

    def _check_pip_module(self) -> bool:
        """检查pip模块是否可用"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"],
                         check=True, capture_output=True, timeout=10)
            return True
        except Exception:
            return False

    def _run_pre_install_commands(self) -> bool:
        """运行预安装命令"""
        for cmd in self.preset.pre_install_commands:
            if not self._run_command_with_recovery(cmd, "pre_install"):
                return False
        return True

    def _create_virtual_environment(self) -> bool:
        """创建虚拟环境"""
        try:
            if self.venv_dir.exists():
                logger.info("虚拟环境已存在，跳过创建")
                return True

            logger.info(f"创建虚拟环境: {self.venv_dir}")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_dir)],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode != 0:
                logger.error(f"虚拟环境创建失败: {result.stderr}")
                # 尝试自动恢复
                if self.auto_recovery.attempt_recovery("venv_creation_failed",
                                                     {"venv_path": str(self.venv_dir)}):
                    logger.info("虚拟环境创建恢复成功")
                    return True
                return False

            logger.info("虚拟环境创建成功")
            return True

        except Exception as e:
            logger.error(f"创建虚拟环境时发生错误: {e}")
            return False

    def _install_dependencies(self, options: Dict[str, Any]) -> bool:
        """安装依赖"""
        try:
            # 获取pip路径
            pip_cmd = self._get_pip_command()

            # 升级pip
            if not self._upgrade_pip(pip_cmd):
                logger.warning("pip升级失败，继续安装")

            # 安装必需包
            for package in self.preset.required_packages:
                if not self._install_package(pip_cmd, package, required=True):
                    return False

            # 安装可选包
            for package in self.preset.optional_packages:
                self._install_package(pip_cmd, package, required=False)

            # 安装requirements文件
            req_files = ["requirements.txt", "requirements-prod.txt"]
            for req_file in req_files:
                req_path = self.project_dir / req_file
                if req_path.exists() and options.get(f"install_{req_file.replace('-', '_').replace('.txt', '')}", True):
                    if not self._install_requirements(pip_cmd, req_path):
                        logger.warning(f"安装 {req_file} 失败，继续安装")

            return True

        except Exception as e:
            logger.error(f"依赖安装失败: {e}")
            return False

    def _get_pip_command(self) -> List[str]:
        """获取pip命令"""
        if self.venv_dir.exists():
            if platform.system() == "Windows":
                pip_path = self.venv_dir / "Scripts" / "pip.exe"
                if pip_path.exists():
                    return [str(pip_path)]
                else:
                    python_path = self.venv_dir / "Scripts" / "python.exe"
                    return [str(python_path), "-m", "pip"]
            else:
                pip_path = self.venv_dir / "bin" / "pip"
                if pip_path.exists():
                    return [str(pip_path)]
                else:
                    python_path = self.venv_dir / "bin" / "python"
                    return [str(python_path), "-m", "pip"]

        return [sys.executable, "-m", "pip"]

    def _upgrade_pip(self, pip_cmd: List[str]) -> bool:
        """升级pip"""
        try:
            cmd = pip_cmd + ["install", "--upgrade", "pip"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info("pip升级成功")
                return True
            else:
                logger.warning(f"pip升级失败: {result.stderr}")
                return False

        except Exception as e:
            logger.warning(f"pip升级时发生错误: {e}")
            return False

    def _install_package(self, pip_cmd: List[str], package: str, required: bool = True) -> bool:
        """安装单个包"""
        try:
            logger.info(f"安装包: {package}")
            cmd = pip_cmd + ["install"] + self.preset.pip_args + [package]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"包 {package} 安装成功")
                return True
            else:
                logger.error(f"包 {package} 安装失败: {result.stderr}")

                if required:
                    # 尝试自动恢复
                    if self.auto_recovery.attempt_recovery("pip_install_failed",
                                                         {"package": package}):
                        logger.info(f"包 {package} 恢复安装成功")
                        return True

                    # 尝试权限恢复
                    if "permission denied" in result.stderr.lower():
                        if self.auto_recovery.attempt_recovery("permission_denied", {}):
                            # 使用--user参数重试
                            cmd_user = pip_cmd + ["install", "--user", package]
                            result_user = subprocess.run(cmd_user, capture_output=True,
                                                       text=True, timeout=300)
                            if result_user.returncode == 0:
                                logger.info(f"包 {package} 使用--user安装成功")
                                return True

                return not required  # 可选包失败不影响整体安装

        except Exception as e:
            logger.error(f"安装包 {package} 时发生错误: {e}")
            return not required

    def _install_requirements(self, pip_cmd: List[str], req_path: Path) -> bool:
        """安装requirements文件"""
        try:
            logger.info(f"安装requirements文件: {req_path}")
            cmd = pip_cmd + ["install", "-r", str(req_path)] + self.preset.pip_args

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                logger.info(f"Requirements文件 {req_path} 安装成功")
                return True
            else:
                logger.error(f"Requirements文件 {req_path} 安装失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"安装requirements文件时发生错误: {e}")
            return False

    def _run_post_install_commands(self) -> bool:
        """运行后安装命令"""
        for cmd in self.preset.post_install_commands:
            if not self._run_command_with_recovery(cmd, "post_install"):
                logger.warning(f"后安装命令失败: {cmd}")
        return True

    def _run_command_with_recovery(self, cmd: str, context: str) -> bool:
        """运行命令并支持恢复"""
        try:
            logger.info(f"执行命令: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True, timeout=120)

            if result.returncode == 0:
                logger.info(f"命令执行成功: {cmd}")
                return True
            else:
                logger.error(f"命令执行失败: {cmd}, 错误: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"执行命令时发生错误: {cmd}, 错误: {e}")
            return False

    def _verify_installation(self) -> bool:
        """验证安装"""
        try:
            logger.info("开始验证安装")

            # 获取Python命令
            python_cmd = self._get_python_command()

            # 验证必需包
            for package in self.preset.required_packages:
                if not self._verify_package(python_cmd, package):
                    logger.error(f"包验证失败: {package}")
                    return False

            # 验证可选包
            for package in self.preset.optional_packages:
                self._verify_package(python_cmd, package, required=False)

            logger.info("安装验证成功")
            return True

        except Exception as e:
            logger.error(f"验证安装时发生错误: {e}")
            return False

    def _get_python_command(self) -> List[str]:
        """获取Python命令"""
        if self.venv_dir.exists():
            if platform.system() == "Windows":
                python_path = self.venv_dir / "Scripts" / "python.exe"
            else:
                python_path = self.venv_dir / "bin" / "python"

            if python_path.exists():
                return [str(python_path)]

        return [sys.executable]

    def _verify_package(self, python_cmd: List[str], package: str, required: bool = True) -> bool:
        """验证单个包"""
        try:
            # 简化包名（去除版本号等）
            package_name = package.split("==")[0].split(">=")[0].split("<=")[0]

            cmd = python_cmd + ["-c", f"import {package_name}; print(f'{package_name} 导入成功')"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"✓ {package_name} 验证通过")
                return True
            else:
                if required:
                    logger.error(f"✗ {package_name} 验证失败")
                else:
                    logger.warning(f"⚠ {package_name} 验证失败（可选包）")
                return not required

        except Exception as e:
            logger.error(f"验证包 {package} 时发生错误: {e}")
            return not required

    def get_troubleshooting_info(self) -> str:
        """获取故障排除信息"""
        info = [
            f"环境类型: {self.env_type.value}",
            f"预设名称: {self.preset.name}",
            "",
            "故障排除步骤:",
        ]

        for i, step in enumerate(self.preset.troubleshooting_steps, 1):
            info.append(f"{i}. {step}")

        return "\n".join(info)


# 尝试导入PyQt6，如果失败则自动安装
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
        QWidget, QLabel, QProgressBar, QPushButton, QTextEdit,
        QMessageBox, QFrame, QCheckBox, QComboBox, QTabWidget,
        QGroupBox, QGridLayout, QSpacerItem, QSizePolicy
    )
    from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
    from PyQt6.QtGui import QFont, QPixmap, QIcon
    PYQT6_AVAILABLE = True
except ImportError:
    print("PyQt6未安装，正在自动安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
            QWidget, QLabel, QProgressBar, QPushButton, QTextEdit,
            QMessageBox, QFrame, QCheckBox, QComboBox, QTabWidget,
            QGroupBox, QGridLayout, QSpacerItem, QSizePolicy
        )
        from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
        from PyQt6.QtGui import QFont, QPixmap, QIcon
        PYQT6_AVAILABLE = True
    except Exception as e:
        print(f"PyQt6安装失败: {e}")
        PYQT6_AVAILABLE = False


class EnhancedInstallWorker(QThread):
    """增强版安装工作线程"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, install_options):
        super().__init__()
        self.install_options = install_options
        self.installer = EnhancedInstaller()

    def run(self):
        """执行安装过程"""
        try:
            self.progress_updated.emit(0)
            self.status_updated.emit("初始化安装程序...")
            self.log_updated.emit(f"检测到环境类型: {self.installer.env_type.value}")
            self.log_updated.emit(f"使用预设: {self.installer.preset.name}")

            # 模拟进度更新
            steps = [
                (10, "检查环境..."),
                (30, "创建虚拟环境..."),
                (50, "安装依赖包..."),
                (80, "验证安装..."),
                (100, "安装完成")
            ]

            success, message = self.installer.install(self.install_options)

            for progress, status in steps:
                self.progress_updated.emit(progress)
                self.status_updated.emit(status)
                self.log_updated.emit(f"步骤完成: {status}")
                time.sleep(0.5)  # 模拟处理时间

            self.finished.emit(success, message)

        except Exception as e:
            error_msg = f"安装过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.finished.emit(False, error_msg)


class EnhancedInstallWindow(QMainWindow):
    """增强版安装程序主窗口"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.installer = EnhancedInstaller()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("TimeNest 增强版安装程序")
        self.setFixedSize(800, 700)
        self.setStyleSheet(self._get_stylesheet())

        # 中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题和环境信息
        self._create_header(layout)

        # 选项卡
        self._create_tabs(layout)

        # 进度区域
        self._create_progress_area(layout)

        # 按钮区域
        self._create_buttons(layout)

        # 初始化检查
        self.check_environment()

    def _get_stylesheet(self) -> str:
        """获取样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton#danger {
                background-color: #f44336;
            }
            QPushButton#danger:hover {
                background-color: #da190b;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #fafafa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """

    def _create_header(self, layout: QVBoxLayout):
        """创建头部"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)

        # 标题
        title_label = QLabel("TimeNest 增强版安装程序")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title_label)

        # 环境信息
        env_info = QLabel(f"检测到环境: {self.installer.env_type.value}")
        env_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        env_info.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        header_layout.addWidget(env_info)

        preset_info = QLabel(f"使用预设: {self.installer.preset.name}")
        preset_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preset_info.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        header_layout.addWidget(preset_info)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        header_layout.addWidget(line)

        layout.addWidget(header_frame)

    def _create_tabs(self, layout: QVBoxLayout):
        """创建选项卡"""
        self.tab_widget = QTabWidget()

        # 基本选项标签页
        basic_tab = self._create_basic_options_tab()
        self.tab_widget.addTab(basic_tab, "基本选项")

        # 高级选项标签页
        advanced_tab = self._create_advanced_options_tab()
        self.tab_widget.addTab(advanced_tab, "高级选项")

        # 故障排除标签页
        troubleshoot_tab = self._create_troubleshoot_tab()
        self.tab_widget.addTab(troubleshoot_tab, "故障排除")

        layout.addWidget(self.tab_widget)

    def _create_basic_options_tab(self) -> QWidget:
        """创建基本选项标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 安装选项组
        install_group = QGroupBox("安装选项")
        install_layout = QVBoxLayout(install_group)

        self.create_venv_cb = QCheckBox("创建虚拟环境 (强烈推荐)")
        self.create_venv_cb.setChecked(True)
        self.create_venv_cb.setToolTip("在项目目录中创建独立的Python虚拟环境")
        install_layout.addWidget(self.create_venv_cb)

        self.upgrade_pip_cb = QCheckBox("升级pip到最新版本")
        self.upgrade_pip_cb.setChecked(True)
        self.upgrade_pip_cb.setToolTip("确保使用最新版本的pip包管理器")
        install_layout.addWidget(self.upgrade_pip_cb)

        self.install_deps_cb = QCheckBox("安装项目依赖")
        self.install_deps_cb.setChecked(True)
        self.install_deps_cb.setToolTip("自动安装TimeNest运行所需的所有依赖包")
        install_layout.addWidget(self.install_deps_cb)

        layout.addWidget(install_group)

        # 依赖选择组
        deps_group = QGroupBox("依赖文件选择")
        deps_layout = QVBoxLayout(deps_group)

        self.req_main_cb = QCheckBox("requirements.txt (核心依赖)")
        self.req_main_cb.setChecked(True)
        deps_layout.addWidget(self.req_main_cb)

        self.req_prod_cb = QCheckBox("requirements-prod.txt (生产环境)")
        self.req_prod_cb.setChecked(False)
        deps_layout.addWidget(self.req_prod_cb)

        self.req_dev_cb = QCheckBox("requirements-dev.txt (开发环境)")
        self.req_dev_cb.setChecked(False)
        deps_layout.addWidget(self.req_dev_cb)

        layout.addWidget(deps_group)

        # 添加弹性空间
        layout.addStretch()

        return tab

    def _create_advanced_options_tab(self) -> QWidget:
        """创建高级选项标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 环境配置组
        env_group = QGroupBox("环境配置")
        env_layout = QGridLayout(env_group)

        env_layout.addWidget(QLabel("Python版本:"), 0, 0)
        python_info = self.installer.env_detector.get_python_info()
        version_text = f"{python_info['version'].major}.{python_info['version'].minor}.{python_info['version'].micro}"
        env_layout.addWidget(QLabel(version_text), 0, 1)

        env_layout.addWidget(QLabel("平台:"), 1, 0)
        env_layout.addWidget(QLabel(platform.platform()), 1, 1)

        env_layout.addWidget(QLabel("架构:"), 2, 0)
        env_layout.addWidget(QLabel(platform.architecture()[0]), 2, 1)

        layout.addWidget(env_group)

        # 安装策略组
        strategy_group = QGroupBox("安装策略")
        strategy_layout = QVBoxLayout(strategy_group)

        self.auto_recovery_cb = QCheckBox("启用自动故障恢复")
        self.auto_recovery_cb.setChecked(True)
        self.auto_recovery_cb.setToolTip("当安装失败时自动尝试恢复策略")
        strategy_layout.addWidget(self.auto_recovery_cb)

        self.use_mirrors_cb = QCheckBox("使用国内镜像源")
        self.use_mirrors_cb.setChecked(True)
        self.use_mirrors_cb.setToolTip("使用国内PyPI镜像源加速下载")
        strategy_layout.addWidget(self.use_mirrors_cb)

        self.force_reinstall_cb = QCheckBox("强制重新安装")
        self.force_reinstall_cb.setChecked(False)
        self.force_reinstall_cb.setToolTip("强制重新安装所有包，即使已经安装")
        strategy_layout.addWidget(self.force_reinstall_cb)

        layout.addWidget(strategy_group)

        # 添加弹性空间
        layout.addStretch()

        return tab

    def _create_troubleshoot_tab(self) -> QWidget:
        """创建故障排除标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 故障排除信息
        info_group = QGroupBox("故障排除指南")
        info_layout = QVBoxLayout(info_group)

        troubleshoot_text = QTextEdit()
        troubleshoot_text.setReadOnly(True)
        troubleshoot_text.setMaximumHeight(200)
        troubleshoot_text.setPlainText(self.installer.get_troubleshooting_info())
        info_layout.addWidget(troubleshoot_text)

        layout.addWidget(info_group)

        # 诊断工具组
        diag_group = QGroupBox("诊断工具")
        diag_layout = QVBoxLayout(diag_group)

        self.check_env_btn = QPushButton("检查环境")
        self.check_env_btn.clicked.connect(self.run_environment_check)
        diag_layout.addWidget(self.check_env_btn)

        self.clean_cache_btn = QPushButton("清理缓存")
        self.clean_cache_btn.clicked.connect(self.clean_pip_cache)
        diag_layout.addWidget(self.clean_cache_btn)

        self.test_network_btn = QPushButton("测试网络连接")
        self.test_network_btn.clicked.connect(self.test_network)
        diag_layout.addWidget(self.test_network_btn)

        layout.addWidget(diag_group)

        # 添加弹性空间
        layout.addStretch()

        return tab

    def _create_progress_area(self, layout: QVBoxLayout):
        """创建进度区域"""
        progress_group = QGroupBox("安装进度")
        progress_layout = QVBoxLayout(progress_group)

        # 状态标签
        self.status_label = QLabel("准备安装...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        # 日志显示
        log_label = QLabel("安装日志:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        progress_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        progress_layout.addWidget(self.log_text)

        layout.addWidget(progress_group)

    def _create_buttons(self, layout: QVBoxLayout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.install_btn = QPushButton("开始安装")
        self.install_btn.clicked.connect(self.start_install)
        button_layout.addWidget(self.install_btn)

        self.stop_btn = QPushButton("停止安装")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self.stop_install)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setEnabled(False)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def check_environment(self):
        """检查环境"""
        self.log_text.append("=== 环境检查 ===")

        python_info = self.installer.env_detector.get_python_info()
        self.log_text.append(f"Python版本: {python_info['version']}")
        self.log_text.append(f"Python路径: {python_info['executable']}")
        self.log_text.append(f"平台信息: {python_info['platform']}")

        if python_info['virtual_env']:
            self.log_text.append(f"虚拟环境: {python_info['virtual_env']}")

        if python_info['conda_env']:
            self.log_text.append(f"Conda环境: {python_info['conda_env']}")

        # 检查requirements文件
        req_files = {
            "requirements.txt": self.req_main_cb,
            "requirements-prod.txt": self.req_prod_cb,
            "requirements-dev.txt": self.req_dev_cb
        }

        for req_file, checkbox in req_files.items():
            if Path(req_file).exists():
                self.log_text.append(f"✓ 找到 {req_file}")
                checkbox.setEnabled(True)
            else:
                self.log_text.append(f"✗ 未找到 {req_file}")
                checkbox.setEnabled(False)
                checkbox.setChecked(False)

        self.log_text.append("环境检查完成\n")

    def start_install(self):
        """开始安装"""
        # 收集安装选项
        install_options = {
            "create_venv": self.create_venv_cb.isChecked(),
            "upgrade_pip": self.upgrade_pip_cb.isChecked(),
            "install_deps": self.install_deps_cb.isChecked(),
            "install_requirements": self.req_main_cb.isChecked(),
            "install_requirements_prod": self.req_prod_cb.isChecked(),
            "install_requirements_dev": self.req_dev_cb.isChecked(),
            "auto_recovery": self.auto_recovery_cb.isChecked(),
            "use_mirrors": self.use_mirrors_cb.isChecked(),
            "force_reinstall": self.force_reinstall_cb.isChecked(),
        }

        # 禁用按钮
        self.install_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 清空日志
        self.log_text.clear()
        self.log_text.append("=== 开始安装 ===")

        # 创建并启动工作线程
        self.worker = EnhancedInstallWorker(install_options)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.log_updated.connect(self.log_text.append)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()

    def stop_install(self):
        """停止安装"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.status_label.setText("安装已停止")
            self.log_text.append("\n=== 安装已停止 ===")

        self.install_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def on_install_finished(self, success: bool, message: str):
        """安装完成"""
        if success:
            self.status_label.setText("安装成功！")
            self.log_text.append("\n=== 安装成功 ===")
            self.log_text.append("\n使用说明:")

            if self.create_venv_cb.isChecked():
                if platform.system() == "Windows":
                    self.log_text.append("激活虚拟环境: venv\\Scripts\\activate")
                    self.log_text.append("运行程序: venv\\Scripts\\python main.py")
                else:
                    self.log_text.append("激活虚拟环境: source venv/bin/activate")
                    self.log_text.append("运行程序: venv/bin/python main.py")
            else:
                self.log_text.append("运行程序: python main.py")

            QMessageBox.information(self, "安装完成",
                                  "TimeNest安装成功！\n\n请查看日志了解如何运行程序。")
        else:
            self.status_label.setText("安装失败")
            self.log_text.append(f"\n=== 安装失败 ===")
            self.log_text.append(f"错误信息: {message}")
            self.log_text.append(f"\n故障排除建议:")
            self.log_text.append(self.installer.get_troubleshooting_info())

            QMessageBox.critical(self, "安装失败",
                                f"安装过程中出现错误:\n{message}\n\n请查看故障排除标签页获取帮助。")

        self.install_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def run_environment_check(self):
        """运行环境检查"""
        self.log_text.append("\n=== 详细环境检查 ===")

        # 检查Python
        try:
            result = subprocess.run([sys.executable, "--version"],
                                  capture_output=True, text=True, timeout=10)
            self.log_text.append(f"Python: {result.stdout.strip()}")
        except Exception as e:
            self.log_text.append(f"Python检查失败: {e}")

        # 检查pip
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                                  capture_output=True, text=True, timeout=10)
            self.log_text.append(f"pip: {result.stdout.strip()}")
        except Exception as e:
            self.log_text.append(f"pip检查失败: {e}")

        # 检查网络
        self.test_network()

    def clean_pip_cache(self):
        """清理pip缓存"""
        try:
            self.log_text.append("\n清理pip缓存...")
            result = subprocess.run([sys.executable, "-m", "pip", "cache", "purge"],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_text.append("pip缓存清理成功")
            else:
                self.log_text.append(f"pip缓存清理失败: {result.stderr}")
        except Exception as e:
            self.log_text.append(f"清理缓存时发生错误: {e}")

    def test_network(self):
        """测试网络连接"""
        self.log_text.append("\n测试网络连接...")

        test_urls = [
            "https://pypi.tuna.tsinghua.edu.cn",
            "https://pypi.org",
            "https://pypi.douban.com",
            "https://mirrors.aliyun.com"
        ]

        for url in test_urls:
            try:
                import urllib.request
                urllib.request.urlopen(url, timeout=5)
                self.log_text.append(f"✓ {url} 连接成功")
            except Exception as e:
                self.log_text.append(f"✗ {url} 连接失败: {e}")


def main():
    """主函数"""
    if not PYQT6_AVAILABLE:
        # 如果PyQt6不可用，使用命令行模式
        print("PyQt6不可用，使用命令行模式安装...")
        installer = EnhancedInstaller()
        success, message = installer.install()

        if success:
            print("✓ 安装成功！")
            print("\n使用说明:")
            if Path("venv").exists():
                if platform.system() == "Windows":
                    print("激活虚拟环境: venv\\Scripts\\activate")
                    print("运行程序: venv\\Scripts\\python main.py")
                else:
                    print("激活虚拟环境: source venv/bin/activate")
                    print("运行程序: venv/bin/python main.py")
            else:
                print("运行程序: python main.py")
        else:
            print(f"✗ 安装失败: {message}")
            print("\n故障排除信息:")
            print(installer.get_troubleshooting_info())

        return 0 if success else 1

    # GUI模式
    app = QApplication(sys.argv)
    app.setApplicationName("TimeNest Enhanced Installer")

    # 设置应用图标（如果存在）
    icon_path = Path("resources/icons/app_icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = EnhancedInstallWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
