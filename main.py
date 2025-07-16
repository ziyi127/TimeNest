#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 主应用入口 (RinUI版本)
基于RinUI的现代化时间管理工具
"""

import sys
import os
import logging
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils.common_imports import (
    PYSIDE6_AVAILABLE, QApplication, QSystemTrayIcon, QTimer, QIcon,
    Qt, QTranslator, QLocale, qmlRegisterType
)
from utils.shared_utilities import setup_encoding
from utils.config_constants import (
    APP_NAME, APP_VERSION, ORGANIZATION_NAME, ORGANIZATION_DOMAIN,
    LOG_FORMAT, DEFAULT_DIRS
)

if not PYSIDE6_AVAILABLE:
    print("PySide6 not available. Please install it using: pip install PySide6")
    sys.exit(1)

try:
    import RinUI
    from RinUI import RinUIWindow
    from utils.version_manager import version_manager
    from core.rinui_bridge import TimeNestBridge, register_qml_types
    from core.system_tray import SystemTrayManager, TrayNotificationManager
    from core.simple_floating_window import SimpleFloatingWindowManager
except ImportError as e:
    logging.error(f"Critical import error: {e}")
    print(f"Import error: {e}")
    print("Please ensure RinUI and all dependencies are properly installed")
    print("Run: pip install RinUI")
    sys.exit(1)


def setup_logging():
    """设置日志系统"""
    for directory in DEFAULT_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(DEFAULT_DIRS[1] / 'timenest.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    for lib in ['PySide6', 'RinUI']:
        logging.getLogger(lib).setLevel(logging.WARNING if lib == 'PySide6' else logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("TimeNest RinUI版本启动")
    return logger


def setup_application():
    """设置 QApplication"""
    import os  # Ensure os is available in function scope

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(APP_VERSION)
    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)

    # 设置高DPI支持
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    except AttributeError:
        # 如果属性不存在，说明是更新版本的PySide6，可以忽略
        pass

    # 创建应用实例
    app = QApplication(sys.argv)

    # 设置应用图标
    icon_paths = [
        'resources/icons/app_icon.png',
        'resources/icons/tray_icon.png',
        'app_icon.png'
    ]

    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            break

    return app


def check_dependencies():
    """检查依赖项"""
    from utils.common_imports import get_missing_modules

    missing_deps = get_missing_modules()
    critical_deps = ['RinUI']

    missing_critical = [dep for dep in missing_deps if dep in critical_deps]

    if missing_critical:
        print("缺少关键依赖项:")
        for dep in missing_critical:
            print(f"  - {dep}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_critical)}")
        return False

    if missing_deps:
        logging.warning(f"缺少可选依赖项: {', '.join(missing_deps)}")

    return True


def main():
    """
    主函数
    """
    # 设置日志
    logger = setup_logging()

    try:
        # 检查依赖
        if not check_dependencies():
            sys.exit(1)

        # 设置应用
        setup_application()
        app = QApplication.instance()

        # 设置退出策略 - 关闭最后一个窗口时不退出程序（因为有系统托盘）
        app.setQuitOnLastWindowClosed(False)

        logger.info(f"启动 {version_manager.get_app_name()} {version_manager.get_full_version()}")

        # 注册QML类型
        register_qml_types()

        # 创建桥接对象
        bridge = TimeNestBridge()

        # 创建系统托盘管理器
        tray_manager = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            tray_manager = SystemTrayManager()
            tray_notification_manager = TrayNotificationManager(tray_manager)
            logger.info("系统托盘初始化完成")
        else:
            logger.warning("系统托盘不可用")

        # 创建悬浮窗管理器
        floating_manager = SimpleFloatingWindowManager()

        # 设置桥接对象的管理器引用
        bridge.set_floating_manager(floating_manager)
        bridge.set_tray_manager(tray_manager)

        # 创建主窗口
        main_qml = current_dir / "qml" / "main.qml"
        if not main_qml.exists():
            logger.error(f"主QML文件不存在: {main_qml}")
            sys.exit(1)

        # 创建启动加载页面
        splash_qml = current_dir / "qml" / "components" / "SplashScreen.qml"
        if not splash_qml.exists():
            logger.error(f"启动加载页面QML文件不存在: {splash_qml}")
            sys.exit(1)

        # 创建启动加载窗口
        splash_window = RinUIWindow()
        splash_window.load(str(splash_qml))

        # 创建启动状态管理器
        class SplashManager:
            def __init__(self, splash_window):
                self.splash_window = splash_window
                self.current_progress = 0.0

            def update_status(self, message, progress):
                self.current_progress = progress
                try:
                    # 通过QML引擎更新状态
                    if hasattr(self.splash_window, 'engine'):
                        engine = self.splash_window.engine
                        if callable(engine):
                            engine = engine()
                        if engine and hasattr(engine, 'rootContext'):
                            context = engine.rootContext()
                            context.setContextProperty("loadingMessage", message)
                            context.setContextProperty("loadingProgress", progress)
                            logger.info(f"启动状态更新: {message} ({progress*100:.0f}%)")
                except Exception as e:
                    logger.error(f"更新启动状态失败: {e}")

            def close_splash(self):
                try:
                    self.splash_window.close()
                    logger.info("启动加载页面已关闭")
                except Exception as e:
                    logger.error(f"关闭启动加载页面失败: {e}")

        splash_manager = SplashManager(splash_window)

        # 将桥接对象和状态管理器暴露给启动加载页面
        try:
            if hasattr(splash_window, 'engine'):
                engine = splash_window.engine
                if callable(engine):
                    engine = engine()
                if engine and hasattr(engine, 'rootContext'):
                    context = engine.rootContext()
                    context.setContextProperty("timeNestBridge", bridge)
                    context.setContextProperty("loadingMessage", "正在初始化...")
                    context.setContextProperty("loadingProgress", 0.0)
                    logger.info("成功设置启动加载页面QML上下文属性")
            else:
                logger.warning("启动加载窗口没有engine属性")
        except Exception as e:
            logger.error(f"设置启动加载页面QML上下文属性失败: {e}")

        # 显示启动加载页面
        splash_window.show()
        logger.info("启动加载页面已显示")

        # 更新启动状态
        splash_manager.update_status("正在创建主窗口...", 0.1)

        # 创建主窗口（但不显示）
        window = RinUIWindow()
        window.load(str(main_qml))

        splash_manager.update_status("正在加载主窗口...", 0.3)

        # 设置窗口属性（加载后）
        try:
            if hasattr(window, 'setTitle'):
                window.setTitle(version_manager.get_app_name())
        except Exception as e:
            logger.warning(f"无法设置窗口标题: {e}")

        # 默认隐藏主窗口，只显示在系统托盘
        window.hide()
        logger.info("主窗口已创建但隐藏，应用将在系统托盘中运行")

        splash_manager.update_status("正在设置QML上下文...", 0.5)

        # 将桥接对象暴露给主窗口QML
        try:
            # RinUIWindow的上下文设置方式
            if hasattr(window, 'engine'):
                engine = window.engine
                if callable(engine):
                    engine = engine()
                if engine and hasattr(engine, 'rootContext'):
                    context = engine.rootContext()
                    context.setContextProperty("timeNestBridge", bridge)
                    logger.info("成功设置主窗口QML上下文属性")
                else:
                    logger.warning("无法获取主窗口QML引擎的根上下文")
            else:
                logger.warning("主窗口RinUIWindow没有engine属性")
        except Exception as e:
            logger.error(f"设置主窗口QML上下文属性失败: {e}")
            # 尝试备用方法
            try:
                from PySide6.QtQml import qmlRegisterSingletonType
                def create_bridge(engine, script_engine):
                    return bridge
                qmlRegisterSingletonType(type(bridge), "TimeNest", 1, 0, "TimeNestBridge", create_bridge)
                logger.info("使用单例模式注册桥接对象")
            except Exception as e2:
                logger.error(f"备用注册方法也失败: {e2}")

        splash_manager.update_status("正在连接系统托盘...", 0.6)

        # 连接系统托盘信号
        if tray_manager:
            # 连接托盘信号到相应的处理函数
            def show_main_window():
                if hasattr(window, 'show'):
                    window.show()
                    window.raise_()
                    window.requestActivate()
                    logger.info("主窗口已显示并激活")
            tray_manager.show_main_window.connect(show_main_window)
            tray_manager.toggle_floating_window.connect(floating_manager.toggle_floating_window)
            def show_settings_page():
                if window:
                    window.show()
                    window.raise_()
                    window.requestActivate()
                    # 切换到设置页面
                    bridge.switchToSettingsView()
                    logger.info("已切换到设置页面")
            tray_manager.show_settings.connect(show_settings_page)
            tray_manager.show_about.connect(lambda: logger.info("打开关于对话框"))
            tray_manager.quit_application.connect(app.quit)

            # 连接悬浮窗状态变化信号
            floating_manager.visibility_changed.connect(tray_manager.update_floating_status)

        splash_manager.update_status("正在初始化悬浮窗...", 0.8)

        # 创建并显示悬浮窗
        if floating_manager.create_floating_window():
            floating_manager.show_floating_window()
            logger.info("悬浮窗启动成功")
        else:
            logger.warning("悬浮窗启动失败")

        splash_manager.update_status("正在完成初始化...", 0.9)

        # 显示托盘通知
        if tray_manager:
            tray_notification_manager.add_notification(
                "TimeNest",
                "应用已启动，正在后台运行",
                QSystemTrayIcon.MessageIcon.Information
            )

        splash_manager.update_status("启动完成！", 1.0)
        logger.info("应用启动成功")

        # 延迟关闭启动页面
        from PySide6.QtCore import QTimer
        def close_splash_delayed():
            splash_manager.close_splash()

        QTimer.singleShot(1000, close_splash_delayed)  # 1秒后关闭启动页面

        # 运行应用
        exit_code = app.exec()

        # 清理资源
        logger.info("正在清理资源...")
        if floating_manager:
            floating_manager.cleanup()
        if tray_manager:
            tray_manager.cleanup()

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
