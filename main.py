#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 主应用入口
一个功能强大的跨平台课程表管理工具
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from core.app_manager import AppManager
    from ui.system_tray import SystemTray
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖已正确安装")
    sys.exit(1)


def setup_logging():
    """
    设置日志系统
    """
    # 创建日志目录
    log_dir = Path.home() / '.timenest' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置日志处理器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / 'timenest.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger('TimeNest')


def setup_application():
    """
    设置 QApplication
    """
    # 设置应用属性
    QApplication.setApplicationName('TimeNest')
    QApplication.setApplicationVersion('1.0.0')
    QApplication.setOrganizationName('TimeNest Team')
    QApplication.setOrganizationDomain('timenest.org')
    
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = Path(__file__).parent / 'resources' / 'icons' / 'app.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 设置高DPI支持 (PyQt6 中高DPI缩放默认启用)
    try:
        # PyQt6 中只需要设置高DPI像素图
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # 如果属性不存在，说明是更新版本的PyQt6，可以忽略
        pass
    
    # 设置样式
    app.setStyle('Fusion')  # 使用 Fusion 样式以获得更好的跨平台一致性
    
    return app


def check_dependencies():
    """
    检查必要的依赖
    """
    missing_deps = []
    
    # 检查核心依赖
    try:
        import PyQt6
    except ImportError:
        missing_deps.append('PyQt6')
    
    try:
        import yaml
    except ImportError:
        missing_deps.append('PyYAML')
    
    try:
        import pandas
    except ImportError:
        missing_deps.append('pandas')
    
    if missing_deps:
        error_msg = f"缺少必要的依赖包:\n\n{', '.join(missing_deps)}\n\n请运行以下命令安装:\npip install {' '.join(missing_deps)}"
        print(error_msg)
        
        # 尝试显示图形化错误消息
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "TimeNest - 依赖错误",
                error_msg
            )
        except:
            pass
        
        return False
    
    return True


def create_directories():
    """
    创建必要的目录结构
    """
    base_dir = Path.home() / '.timenest'
    directories = [
        base_dir,
        base_dir / 'config',
        base_dir / 'schedules',
        base_dir / 'logs',
        base_dir / 'cache',
        base_dir / 'backups',
        base_dir / 'themes',
        base_dir / 'sounds',
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def _show_message(title: str, message: str):
    """显示信息对话框"""
    try:
        QMessageBox.information(None, f"TimeNest - {title}", message)
    except Exception as e:
        print(f"{title}: {message} (错误: {e})")

def main():
    """
    主函数
    """
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建必要目录
    create_directories()
    
    # 设置日志
    logger = setup_logging()
    logger.info("TimeNest 启动中...")
    
    try:
        # 创建应用
        app = setup_application()
        
        # 创建应用管理器
        app_manager = AppManager()
        
        # 初始化应用管理器
        if not app_manager.initialize():
            logger.error("应用管理器初始化失败")
            QMessageBox.critical(
                None,
                "TimeNest - 初始化错误",
                "应用初始化失败，请检查配置文件和权限设置。"
            )
            sys.exit(1)
        
        # 创建系统托盘（纯托盘模式）
        system_tray = SystemTray()

        # 连接托盘信号到模块管理器
        if hasattr(app_manager, 'module_manager') and app_manager.module_manager:
            system_tray.schedule_module_requested.connect(app_manager.module_manager.open_schedule_module)
            system_tray.settings_module_requested.connect(app_manager.module_manager.open_settings_module)
            system_tray.plugins_module_requested.connect(app_manager.module_manager.open_plugins_module)
            system_tray.floating_settings_requested.connect(app_manager.module_manager.open_floating_settings)
            system_tray.time_calibration_requested.connect(app_manager.module_manager.open_time_calibration)
            logger.info("托盘信号已连接到模块管理器")
        else:
            logger.warning("模块管理器不可用，使用备用处理方法")
            # 备用处理方法
            system_tray.schedule_module_requested.connect(lambda: _show_message("课程表管理", "课程表管理功能正在开发中..."))
            system_tray.settings_module_requested.connect(lambda: _show_message("应用设置", "应用设置功能正在开发中..."))
            system_tray.plugins_module_requested.connect(lambda: _show_message("插件市场", "插件市场功能正在开发中..."))
            system_tray.floating_settings_requested.connect(lambda: _show_message("浮窗设置", "浮窗设置功能正在开发中..."))
            system_tray.time_calibration_requested.connect(lambda: _show_message("时间校准", "时间校准功能正在开发中..."))

        # 连接浮窗控制信号
        if app_manager.floating_manager:
            system_tray.toggle_floating_widget_requested.connect(app_manager.floating_manager.toggle_widget)
            logger.info("浮窗控制信号已连接")
        else:
            logger.warning("浮窗管理器不可用")
            system_tray.toggle_floating_widget_requested.connect(lambda: _show_message("浮窗控制", "浮窗功能不可用"))

        # 连接退出信号 - 只有托盘退出按钮能退出程序
        system_tray.quit_requested.connect(app.quit)
        logger.info("退出信号已连接")

        # 设置应用退出策略 - 关闭最后一个窗口时不退出程序
        app.setQuitOnLastWindowClosed(False)

        # 启动智能浮窗系统
        if app_manager.floating_manager:
            # 自动创建并显示智能浮窗
            if app_manager.floating_manager.create_widget():
                app_manager.floating_manager.show_widget()
                logger.info("智能浮窗启动成功")
            else:
                logger.warning("智能浮窗启动失败")

        logger.info("系统托盘图标显示成功")

        logger.info("TimeNest 静默启动完成")
        
        # 运行应用
        exit_code = app.exec()
        
        # 清理资源
        logger.info("TimeNest 正在关闭...")
        app_manager.cleanup()
        logger.info("TimeNest 已关闭")
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"启动失败: {e}", exc_info=True)
        
        try:
            QMessageBox.critical(
                None,
                "TimeNest - 启动错误",
                f"应用启动失败:\n\n{str(e)}\n\n请查看日志文件获取详细信息。"
            )
        except:
            print(f"启动失败: {e}")
        
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())