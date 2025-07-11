#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统托盘功能
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def test_system_tray():
    """测试系统托盘"""
    logger = setup_logging()
    logger.info("开始测试系统托盘...")
    
    try:
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName('TimeNest Test')
        app.setQuitOnLastWindowClosed(False)
        
        # 导入系统托盘
        from ui.system_tray import SystemTray
        logger.info("✓ 系统托盘类导入成功")
        
        # 创建系统托盘
        system_tray = SystemTray()
        logger.info("✓ 系统托盘创建成功")
        
        # 测试信号连接
        def test_signal(signal_name):
            logger.info(f"✓ {signal_name} 信号触发")
            QMessageBox.information(None, "信号测试", f"{signal_name} 信号工作正常！")
        
        # 连接测试信号
        system_tray.schedule_module_requested.connect(lambda: test_signal("课程表管理"))
        system_tray.settings_module_requested.connect(lambda: test_signal("应用设置"))
        system_tray.plugins_module_requested.connect(lambda: test_signal("插件市场"))
        system_tray.floating_settings_requested.connect(lambda: test_signal("浮窗设置"))
        system_tray.time_calibration_requested.connect(lambda: test_signal("时间校准"))
        system_tray.toggle_floating_widget_requested.connect(lambda: test_signal("浮窗切换"))
        system_tray.quit_requested.connect(lambda: test_signal("退出应用"))
        
        logger.info("✓ 所有信号连接成功")
        
        # 显示测试信息
        QMessageBox.information(
            None, 
            "系统托盘测试", 
            "系统托盘测试启动成功！\n\n"
            "请右键点击系统托盘图标测试各项功能。\n"
            "点击确定开始测试..."
        )
        
        logger.info("系统托盘测试运行中，请右键点击托盘图标测试功能...")
        
        # 运行应用
        return app.exec()
        
    except Exception as e:
        logger.error(f"系统托盘测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            QMessageBox.critical(
                None,
                "测试失败",
                f"系统托盘测试失败:\n\n{str(e)}"
            )
        except:
            print(f"测试失败: {e}")
        
        return 1

if __name__ == '__main__':
    sys.exit(test_system_tray())
