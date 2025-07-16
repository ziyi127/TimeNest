#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 2.0.0 Preview 自动安装程序
自动创建虚拟环境并安装依赖 - RinUI版本
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
        QWidget, QLabel, QProgressBar, QPushButton, QTextEdit,
        QMessageBox, QFrame, QCheckBox, QComboBox
    )
    from PySide6.QtCore import QThread, Signal, Qt, QTimer
    from PySide6.QtGui import QFont, QPixmap, QIcon
except ImportError:
    print("正在安装PySide6...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
        QWidget, QLabel, QProgressBar, QPushButton, QTextEdit,
        QMessageBox, QFrame, QCheckBox, QComboBox
    )
    from PySide6.QtCore import QThread, Signal, Qt, QTimer
    from PySide6.QtGui import QFont, QPixmap, QIcon


class InstallWorker(QThread):
    """安装工作线程"""
    progress_updated = Signal(int)
    status_updated = Signal(str)
    log_updated = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, install_options):
        super().__init__()
        self.install_options = install_options
        self.project_dir = Path.cwd()
        self.venv_dir = self.project_dir / "venv"
        
    def run(self):
        """执行安装过程"""
        try:
            self.progress_updated.emit(0)
            
            # 步骤1: 检查Python环境
            self.status_updated.emit("检查Python环境...")
            self.log_updated.emit(f"Python版本: {sys.version}")
            self.log_updated.emit(f"Python路径: {sys.executable}")
            time.sleep(1)
            self.progress_updated.emit(10)
            
            # 步骤2: 创建虚拟环境
            if self.install_options['create_venv']:
                self.status_updated.emit("创建虚拟环境...")
                if self.venv_dir.exists():
                    self.log_updated.emit("虚拟环境已存在，跳过创建")
                else:
                    self._run_command([sys.executable, "-m", "venv", str(self.venv_dir)])
                    self.log_updated.emit(f"虚拟环境创建完成: {self.venv_dir}")
            self.progress_updated.emit(30)
            
            # 步骤3: 激活虚拟环境并获取pip路径
            if self.install_options['create_venv']:
                if sys.platform == "win32":
                    pip_path = self.venv_dir / "Scripts" / "pip.exe"
                    python_path = self.venv_dir / "Scripts" / "python.exe"
                else:
                    pip_path = self.venv_dir / "bin" / "pip"
                    python_path = self.venv_dir / "bin" / "python"
            else:
                pip_path = "pip"
                python_path = sys.executable
                
            # 步骤4: 升级pip
            if self.install_options['upgrade_pip']:
                self.status_updated.emit("升级pip...")
                self._run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
                self.log_updated.emit("pip升级完成")
            self.progress_updated.emit(50)
            
            # 步骤5: 安装依赖
            if self.install_options['install_deps']:
                self.status_updated.emit("安装项目依赖...")
                
                # 检查requirements文件
                req_files = [
                    "requirements.txt",
                    "requirements-prod.txt", 
                    "requirements-dev.txt"
                ]
                
                for req_file in req_files:
                    req_path = self.project_dir / req_file
                    if req_path.exists() and self.install_options.get(f'install_{req_file.replace("-", "_").replace(".txt", "")}', True):
                        self.log_updated.emit(f"安装 {req_file}...")
                        self._run_command([str(pip_path), "install", "-r", str(req_path)])
                        self.log_updated.emit(f"{req_file} 安装完成")
                        
            self.progress_updated.emit(80)
            
            # 步骤6: 验证安装
            self.status_updated.emit("验证安装...")
            self._verify_installation(python_path)
            self.progress_updated.emit(100)
            
            self.status_updated.emit("安装完成！")
            self.finished.emit(True, "安装成功完成！")
            
        except Exception as e:
            self.log_updated.emit(f"安装失败: {str(e)}")
            self.finished.emit(False, f"安装失败: {str(e)}")
    
    def _run_command(self, cmd):
        """运行命令"""
        try:
            self.log_updated.emit(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True,
                                  cwd=self.project_dir, timeout=300)

            if result.stdout:
                self.log_updated.emit(result.stdout)
            if result.stderr:
                self.log_updated.emit(f"警告: {result.stderr}")

            if result.returncode != 0:
                error_msg = f"命令执行失败: {' '.join(cmd)}"
                if result.stderr:
                    error_msg += f"\n错误详情: {result.stderr}"
                raise Exception(error_msg)

        except subprocess.TimeoutExpired:
            raise Exception(f"命令执行超时 (300秒): {' '.join(cmd)}")
        except FileNotFoundError:
            raise Exception(f"命令不存在: {cmd[0]}")
        except Exception as e:
            if "命令执行失败" in str(e) or "命令执行超时" in str(e) or "命令不存在" in str(e):
                raise e
            else:
                raise Exception(f"命令执行错误: {str(e)}")
    
    def _verify_installation(self, python_path):
        """验证安装"""
        try:
            test_imports = ["PySide6", "requests", "psutil", "schedule"]

            for module in test_imports:
                try:
                    result = subprocess.run(
                        [str(python_path), "-c", f"import {module}; print(f'{module} 导入成功')"],
                        capture_output=True, text=True, timeout=10
                    )
                    status = "✓ 验证通过" if result.returncode == 0 else "⚠ 验证失败"
                    self.log_updated.emit(f"{status} {module}")
                except subprocess.TimeoutExpired:
                    self.log_updated.emit(f"⚠ {module} 验证超时")

        except Exception as e:
            self.log_updated.emit(f"验证过程出错: {e}")


class InstallWindow(QMainWindow):
    """安装程序主窗口"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("TimeNest 安装程序")
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
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
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                border: 1px solid #555;
            }
            QCheckBox {
                font-size: 11px;
                color: #333;
            }
        """)
        
        # 中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("TimeNest 2.0.0 Preview 自动安装程序")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 安装选项
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        
        options_label = QLabel("安装选项:")
        options_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        options_layout.addWidget(options_label)
        
        self.create_venv_cb = QCheckBox("创建虚拟环境 (推荐)")
        self.create_venv_cb.setChecked(True)
        options_layout.addWidget(self.create_venv_cb)
        
        self.upgrade_pip_cb = QCheckBox("升级pip到最新版本")
        self.upgrade_pip_cb.setChecked(True)
        options_layout.addWidget(self.upgrade_pip_cb)
        
        self.install_deps_cb = QCheckBox("安装项目依赖")
        self.install_deps_cb.setChecked(True)
        options_layout.addWidget(self.install_deps_cb)
        
        # 依赖文件选择
        deps_frame = QFrame()
        deps_layout = QVBoxLayout(deps_frame)
        deps_layout.setContentsMargins(20, 0, 0, 0)
        
        self.req_main_cb = QCheckBox("requirements.txt (主要依赖)")
        self.req_main_cb.setChecked(True)
        deps_layout.addWidget(self.req_main_cb)
        
        self.req_prod_cb = QCheckBox("requirements-prod.txt (生产环境)")
        self.req_prod_cb.setChecked(False)
        deps_layout.addWidget(self.req_prod_cb)
        
        self.req_dev_cb = QCheckBox("requirements-dev.txt (开发环境)")
        self.req_dev_cb.setChecked(False)
        deps_layout.addWidget(self.req_dev_cb)
        
        options_layout.addWidget(deps_frame)
        layout.addWidget(options_frame)
        
        # 进度显示
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        self.status_label = QLabel("准备安装...")
        self.status_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
        
        # 日志显示
        log_label = QLabel("安装日志:")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.install_btn = QPushButton("开始安装")
        self.install_btn.clicked.connect(self.start_install)
        button_layout.addWidget(self.install_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setEnabled(False)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 检查环境
        self.check_environment()
    
    def check_environment(self):
        """检查环境"""
        self.log_text.append("=== 环境检查 ===")
        self.log_text.append(f"Python版本: {sys.version}")
        self.log_text.append(f"工作目录: {Path.cwd()}")
        
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
        # 获取安装选项
        install_options = {
            'create_venv': self.create_venv_cb.isChecked(),
            'upgrade_pip': self.upgrade_pip_cb.isChecked(),
            'install_deps': self.install_deps_cb.isChecked(),
            'install_requirements': self.req_main_cb.isChecked(),
            'install_requirements_prod': self.req_prod_cb.isChecked(),
            'install_requirements_dev': self.req_dev_cb.isChecked()
        }
        
        # 禁用按钮
        self.install_btn.setEnabled(False)
        
        # 清空日志
        self.log_text.clear()
        self.log_text.append("=== 开始安装 ===")
        
        # 创建并启动工作线程
        self.worker = InstallWorker(install_options)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.log_updated.connect(self.log_text.append)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()
    
    def on_install_finished(self, success, message):
        """安装完成"""
        if success:
            self.status_label.setText("安装成功！")
            self.log_text.append("\n=== 安装成功 ===")
            self.log_text.append("\n使用说明:")
            if self.create_venv_cb.isChecked():
                if sys.platform == "win32":
                    self.log_text.append("激活虚拟环境: venv\\Scripts\\activate")
                    self.log_text.append("运行程序: venv\\Scripts\\python main.py")
                else:
                    self.log_text.append("激活虚拟环境: source venv/bin/activate")
                    self.log_text.append("运行程序: venv/bin/python main.py")
            else:
                self.log_text.append("运行程序: python main.py")
            
            QMessageBox.information(self, "安装完成", "TimeNest安装成功！\n\n请查看日志了解如何运行程序。")
        else:
            self.status_label.setText("安装失败")
            self.log_text.append(f"\n=== 安装失败 ===")
            self.log_text.append(f"错误信息: {message}")
            QMessageBox.critical(self, "安装失败", f"安装过程中出现错误:\n{message}")
        
        self.install_btn.setEnabled(True)
        self.close_btn.setEnabled(True)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("TimeNest Installer")
    
    # 设置应用图标（如果存在）
    icon_path = Path("resources/icons/tray_icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = InstallWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()