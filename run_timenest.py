#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 启动脚本
简化的启动入口，避免相对导入问题
"""

import sys
import os
from pathlib import Path

# 设置环境变量
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # 使用 X11 后端

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    
    print("🚀 启动 TimeNest...")
    print("=" * 50)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("TimeNest")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("TimeNest Team")
    
    # 设置应用图标
    icon_path = current_dir / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    print("✓ PyQt6 应用创建成功")
    
    # 尝试导入核心组件
    try:
        from core.config_manager import ConfigManager
        print("✓ 配置管理器导入成功")
        
        from core.notification_manager import NotificationManager
        print("✓ 通知管理器导入成功")
        
        from core.floating_manager import FloatingManager
        print("✓ 浮窗管理器导入成功")
        
        from ui.system_tray import SystemTrayManager
        print("✓ 系统托盘管理器导入成功")
        
    except ImportError as e:
        print(f"✗ 核心组件导入失败: {e}")
        QMessageBox.critical(None, "启动失败", f"核心组件导入失败:\n{e}")
        sys.exit(1)
    
    # 创建核心组件
    try:
        print("\n🔧 初始化核心组件...")
        
        # 配置管理器
        config_manager = ConfigManager()
        print("✓ 配置管理器初始化完成")
        
        # 通知管理器
        notification_manager = NotificationManager(config_manager)
        print("✓ 通知管理器初始化完成")
        
        # 浮窗管理器
        floating_manager = FloatingManager()
        print("✓ 浮窗管理器初始化完成")
        
        # 系统托盘
        system_tray = SystemTrayManager(floating_manager)
        print("✓ 系统托盘管理器初始化完成")
        
    except Exception as e:
        print(f"✗ 组件初始化失败: {e}")
        QMessageBox.critical(None, "初始化失败", f"组件初始化失败:\n{e}")
        sys.exit(1)
    
    # 显示系统托盘
    try:
        if system_tray.is_available():
            system_tray.show()
            print("✓ 系统托盘已显示")
        else:
            print("⚠️ 系统托盘不可用")
    except Exception as e:
        print(f"⚠️ 系统托盘显示失败: {e}")
    
    # 创建并显示浮窗
    try:
        floating_manager.create_widget()
        floating_manager.show_widget()
        print("✓ 浮窗已创建并显示")
    except Exception as e:
        print(f"⚠️ 浮窗创建失败: {e}")
    
    # 测试通知系统
    try:
        notification_id = notification_manager.test_notification()
        if notification_id:
            print(f"✓ 通知系统测试成功: {notification_id}")
        else:
            print("⚠️ 通知系统测试失败")
    except Exception as e:
        print(f"⚠️ 通知系统测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TimeNest 启动成功!")
    print("=" * 50)
    print("💡 提示:")
    print("- 右键点击系统托盘图标查看菜单")
    print("- 双击托盘图标显示主窗口")
    print("- 中键点击托盘图标切换浮窗")
    print("- 按 Ctrl+C 退出程序")
    print("=" * 50)
    
    # 运行应用
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        # 清理资源
        try:
            notification_manager.cleanup()
            floating_manager.cleanup()
            system_tray.cleanup()
        except:
            pass
        sys.exit(0)
    
except ImportError as e:
    print(f"✗ PyQt6 导入失败: {e}")
    print("请确保已安装 PyQt6:")
    print("pip install PyQt6")
    sys.exit(1)
except Exception as e:
    print(f"✗ 启动失败: {e}")
    sys.exit(1)
